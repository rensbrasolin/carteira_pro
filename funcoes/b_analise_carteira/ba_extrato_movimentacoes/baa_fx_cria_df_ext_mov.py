import streamlit as st
import pandas as pd

from icones import TITULO_CARREGAMENTO_EXTRATO, ICONE_CARREGAMENTO_EXTRATO
from funcoes._global.fxg_tratamento import g_aplicar_datetime_cols, g_aplicar_to_numeric_cols


# ------------------------------------------------------------------------------------------------------------ Obter dados antes
def carregar_arquivos():
    """
    Recebe 1 ou mais arquivos e armazena na variável 'arquivos'.
    """
    with st.expander(f'{ICONE_CARREGAMENTO_EXTRATO} {TITULO_CARREGAMENTO_EXTRATO}', expanded=False):
        with st.container(border=True):
            arquivos = st.file_uploader("Formato esperado: Excel     (.xlsx ou .xls)",
                                        type=["xlsx", "xls"], accept_multiple_files=True)
    return arquivos

# ------------------------------------------------------------------------------------------------------  Definindo fxs internas
@st.cache_data
def _unificar_extratos_em_df(arquivos):
    # Lê cada arquivo Excel e armazena os DataFrames numa lista com list comprehension.
    lista_dfs = [pd.read_excel(arquivo) for arquivo in arquivos]

    # Concatena todos os DataFrames em um único DataFrame. A ordem do carregamento não importa agora.
    df_ext_mov = pd.concat(lista_dfs, ignore_index=True)

    return df_ext_mov

# _____________________________________________________________________________

def _negativar_valores_debito(df_ext_mov, lista_colunas_numericas):
    # Transforma números positivos em negativos quando for débito
    df_ext_mov.loc[df_ext_mov['Entrada/Saída'] == 'Debito', lista_colunas_numericas] *= -1

    return df_ext_mov

# _____________________________________________________________________________
def _criar_col_ticker(df_ext_mov):
    # Extrair o código do ativo da coluna 'Produto' e criar uma nova coluna 'Ativo'
    df_ext_mov['Ticker'] = df_ext_mov['Produto'].str.split(' ').str[0]

    # Reorganizar df para que 'Ativo' seja a primeira col
    df_ext_mov = df_ext_mov[['Ticker'] + list(df_ext_mov.columns.difference(['Ticker']))]

    return df_ext_mov


# _____________________________________________________________________________
def _criar_col_tipo_ativo(df_ext_mov):
    """
    Classifica Ações, FIIs, FIAgros e FIInfras conforme aba da base manual.
    Se não achar na base, clasifica com N/A.
    Reclassifica ETFs pelos termos de sua denominação.
    """
    
    # Carregar DataFrames
    df_acoes = pd.read_excel('bases_dados/ativos_dados_cadastrais.xlsx', sheet_name='Ações')
    df_fiis = pd.read_excel('bases_dados/ativos_dados_cadastrais.xlsx', sheet_name='FIIs')
    df_fiagros = pd.read_excel('bases_dados/ativos_dados_cadastrais.xlsx', sheet_name='FIAgros')
    df_fiinfras = pd.read_excel('bases_dados/ativos_dados_cadastrais.xlsx', sheet_name='FIInfras')
    
    # Criar dicionário de mapeamento: prefixo → tipo
    prefixo_para_tipo = {}
    
    # Popular dicionário (último vence em caso de duplicata)
    # Ordem de prioridade: FIIs > FIAgros > FIInfras > Ações
    for ticker in df_fiis['Ticker']:
        if pd.notna(ticker) and len(str(ticker)) >= 4:
            prefixo = str(ticker)[:4]
            prefixo_para_tipo[prefixo] = 'FII'
    
    for ticker in df_fiagros['Ticker']:
        if pd.notna(ticker) and len(str(ticker)) >= 4:
            prefixo = str(ticker)[:4]
            prefixo_para_tipo[prefixo] = 'FIAgro'
    
    for ticker in df_fiinfras['Ticker']:
        if pd.notna(ticker) and len(str(ticker)) >= 4:
            prefixo = str(ticker)[:4]
            prefixo_para_tipo[prefixo] = 'FIInfra'
    
    for ticker in df_acoes['Ticker']:
        if pd.notna(ticker) and len(str(ticker)) >= 4:
            prefixo = str(ticker)[:4]
            prefixo_para_tipo[prefixo] = 'Ação'
    
    # Função de classificação usando dicionário (O(1) lookup)
    def _classificar_ativos_pela_base(ticker):
        if pd.isna(ticker):
            return 'N/A'
        
        ticker_str = str(ticker).strip()
        if len(ticker_str) < 4:
            return 'N/A'
        
        prefixo = ticker_str[:4]
        return prefixo_para_tipo.get(prefixo, 'N/A')
    
    # Aplicar
    df_ext_mov['Tipo de Ativo'] = df_ext_mov['Ticker'].apply(_classificar_ativos_pela_base)

    # ============================================
    # RECLASSIFICAÇÃO DE ETFs (SIMPLES)
    # ============================================
    
    # Lista de termos ETF (já em maiúsculas como você mencionou)
    lista_termos_etfs = [
        'FUNDO DE INDICE', 'FUNDO DE ÍNDICE', 'ETF', 'INDEX', 'ÍNDICE',
        'FDO IND', 'FDO. IND.', 'FDO DE INDI', 'FDO DE IND', 'DE IND',
        'IBOV', 'F. DE Í.'
    ]
    
    # Função para classificar ETFs
    def _reclassificar_etfs(row):
        """Reclassifica como ETF se for N/A e produto contiver termo ETF"""
        if row['Tipo de Ativo'] == 'N/A' and pd.notna(row.get('Produto')):
            produto = str(row['Produto'])
            # Verifica se algum termo ETF está contido no produto
            if any(termo in produto for termo in lista_termos_etfs):
                return 'ETF'
        return row['Tipo de Ativo']
    
    # Aplicar reclassificação de ETFs
    df_ext_mov['Tipo de Ativo'] = df_ext_mov.apply(_reclassificar_etfs, axis=1)

    
    return df_ext_mov
    

# _____________________________________________________________________________
def _atualizar_ticker(df_ext_mov):
    """
    Usa o nome completo da empresa da coluna 'Produto' para alterar apenas as
    cols 'Ticker' anteriores a data de atualização.
    """

    # Filtrar linhas onde a "Movimentação" é "Atualização"
    atualizacoes = df_ext_mov[df_ext_mov["Movimentação"] == "Atualização"]

    # Iterar sobre cada linha de atualização
    for index, row in atualizacoes.iterrows():
        # Extrair o nome completo do ativo da coluna "Produto"
        nome_completo = row["Produto"].split(" - ")[1]
        novo_ticker = row["Ticker"]
        data_atualizacao = row["Data"]

        # Filtrar linhas anteriores à data da atualização e que contenham o mesmo nome completo no "Produto"
        linhas_para_atualizar = (df_ext_mov["Produto"].str.contains(nome_completo)) & \
                                (df_ext_mov["Data"] < data_atualizacao)

        # Atualizar a coluna "Ticker" nas linhas filtradas
        df_ext_mov.loc[linhas_para_atualizar, "Ticker"] = novo_ticker

    return df_ext_mov


# _____________________________________________________________________________
# Assim que acontecer o primeiro agrupamento da carteira, tenho que aplicar aqui da mesma forma. 
# Acredito que seja só pegar esse código, aplicar o mesmo filtro e inverter os sinais do cálculo.
def _aplicar_desdobro(df_ext_mov):
    """
    O desdobramento é apenas a correção (ajuste) de quantidade (*2) e preço unitário (/2).
    Ele é aplicado partindo da data do desdobro e voltando até o início. Em todas as movimentações daquele ticker.
    Se tiver mais de 1 desdobro do mesmo ticker, o código vai "ajustar 2x" as movimentações anteriores ao primeiro desdobro.
    Mas na minha lógica, acredito ser isso mesmo o correto.
    """

    
    # Itera sobre as linhas onde a coluna 'Movimentação' tem 'Desdobro', para ter em mãos o ativo e a data do desdobro.
    for index, row in df_ext_mov[df_ext_mov['Movimentação'] == 'Desdobro'].iterrows():
        ticker = row['Ticker']
        data_desdobro = row['Data']

        # Aplica o filtro para pegar as linhas do mesmo ativo, com data anterior ao desdobro e mantendo só trasnf-liq.
        mask = (
            (df_ext_mov['Ticker'] == ticker) &
            (df_ext_mov['Data'] <= data_desdobro)
        )

        # Aplica o desdobramento
        df_ext_mov.loc[mask, 'Preço unitário'] /= 2
        df_ext_mov.loc[mask, 'Quantidade'] *= 2

    return df_ext_mov

# -------------------------------------------------------------------------------------------------------- FX principal que cria o df_ext_mov
def criar_df_ext_mov(arquivos):
    df_ext_mov = _unificar_extratos_em_df(arquivos=arquivos)

    df_ext_mov = g_aplicar_datetime_cols(df=df_ext_mov, lista_colunas_data=['Data'])

    df_ext_mov = g_aplicar_to_numeric_cols(df=df_ext_mov, lista_colunas_numericas=
                                          ['Preço unitário', 'Quantidade', 'Valor da Operação'])

    df_ext_mov = _negativar_valores_debito(df_ext_mov=df_ext_mov, lista_colunas_numericas=
                                          ['Preço unitário', 'Quantidade', 'Valor da Operação'])

    df_ext_mov = _criar_col_ticker(df_ext_mov=df_ext_mov)

    df_ext_mov = _criar_col_tipo_ativo(df_ext_mov=df_ext_mov)

    df_ext_mov = _atualizar_ticker(df_ext_mov=df_ext_mov)

    df_ext_mov = _aplicar_desdobro(df_ext_mov=df_ext_mov)

    return df_ext_mov
    



