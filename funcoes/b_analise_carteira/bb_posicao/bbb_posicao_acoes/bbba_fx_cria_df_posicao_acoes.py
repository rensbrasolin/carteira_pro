import pandas as pd

from funcoes._global.fxg_web_scraping.fxg_web_scraping_cvm import g_criar_df_cvm_cad_cia_aberta
from funcoes._global.fxg_tratamento import g_excluir_strings_cols


# --------------------------------------------------------------------------------------------------------------------------------  Definindo fxs internas

# df_posicao já existirá na página 'Análise carteira'. Então é só entregá-lo a fx.
def _iniciar_df_posicao_acoes(df_posicao):

    df_posicao_acoes = df_posicao.copy()

    # Mantendo apenas linhas de ações.
    df_posicao_acoes = df_posicao_acoes.loc[df_posicao_acoes['Tipo'] == 'Ação']

    # Excluindo cols desnecessárias
    df_posicao_acoes = df_posicao_acoes.drop(
        columns=['Tipo'])
    

    return df_posicao_acoes

# _______________________________ Parte 2: Criar colunas fora do df_posicao e trazê-las.

def _criar_df_cvm_cad_cia_aberta_final():
    """
    Não dá pra trazer direto o df da cvm pq ele não tem o ticker, só o CNPJ.
    Então, trago antes a base interna de ações (que tem cnpj/ticker) para dar match pelo cnpj.
    É criado um 3º df com ticke + as infos (ticker+categorias) necessárias para mesclar com o df_posicao_acoes.
    """

    # ------------------------------------------------------------------------------ Obtendo df de ações da base interna
    df_base_acoes = pd.read_excel('bases_dados/ativos_dados_cadastrais.xlsx', sheet_name='Ações')

    # Mudando nome mantendo apenas cols necessárias
    df_base_acoes = df_base_acoes[['Ticker', 'CNPJ']].copy()

    # ------------------------------------------------------------------------------------------- # Obtendo df da cvm
    df_cvm_cad_cia_aberta = g_criar_df_cvm_cad_cia_aberta()

    # Excluir CNPJs duplicados. Alguns tickers tem cnpj duplicado, acredito eu, devido a atualizações.
    df_cvm_cad_cia_aberta = df_cvm_cad_cia_aberta.drop_duplicates(
        subset=['CNPJ_CIA'], 
        keep='last'  # Mantém a última ocorrência (que acredito ser a mais atual), remove as demais
    )

    # ----------------------------------------------------------------- # Criando um 3º df que une ticker+categorias
    # Trouxe só essas 2 categorias pois foram as únicas que achei fazerem sentido.
    df_cvm_cad_cia_aberta_final = df_base_acoes.merge(
        df_cvm_cad_cia_aberta[['CNPJ_CIA', 'SETOR_ATIV', 'CONTROLE_ACIONARIO']],
        left_on='CNPJ',
        right_on='CNPJ_CIA',
        how='left'
    )

    # ----------------------------------------------------------------- # Tratando colunas
    # Renomeando cols
    df_cvm_cad_cia_aberta_final.rename(columns={'SETOR_ATIV': 'Setor', 'CONTROLE_ACIONARIO': 'Controle Acionário'}, inplace=True)

    # Tratando nomenclatura da col 'Setor' para retirar termos indesejados
    lista_strings_excluir = ['Emp. Adm. Part. -', ', Serv. Água e Gás']
    df_cvm_cad_cia_aberta_final = g_excluir_strings_cols(lista_strings_excluir=lista_strings_excluir, df=df_cvm_cad_cia_aberta_final, coluna='Setor')

    
    # Existem apenas esses 6 valores na col. Eu poderia excluir a string HOLDING (com a fx g_excluir_strings_cols) e diminuir para só 3 categorias.
    # Controle Acionário: Valores únicos. 
    # PRIVADO                2113
    # PRIVADO HOLDING         289
    # ESTRANGEIRO             111
    # ESTATAL                  88
    # ESTRANGEIRO HOLDING      35
    # ESTATAL HOLDING          12

    # Tratando col 'Controle Acionário' que estava toda em maiuscúla. Aproveitando para tratar preposições
    df_cvm_cad_cia_aberta_final['Controle Acionário'] = (
    df_cvm_cad_cia_aberta_final['Controle Acionário']
    .str.title() # Converte para só 1ª letra maiúscula
    .str.replace(' De ', ' de ')   # Mantém "de" minúsculo
    .str.replace(' Da ', ' da ')   # Mantém "da" minúsculo  
    .str.replace(' Do ', ' do ')   # Mantém "do" minúsculo
    .str.replace(' Das ', ' das ') # Mantém "das" minúsculo
    .str.replace(' Dos ', ' dos ') # Mantém "dos" minúsculo
    .str.replace(' E ', ' e ')     # Mantém "e" minúsculo
    )


    return df_cvm_cad_cia_aberta_final









# --------------------------------------------------------------------------------------------------------------------- FX principal que cria o df_posicao_acoes
def criar_df_posicao_acoes(df_posicao):

    df_posicao_acoes = _iniciar_df_posicao_acoes(df_posicao=df_posicao)

    # ---------------------------------------------------------------------- Cria df fora e tras pro principal
    df_setor_acoes = _criar_df_cvm_cad_cia_aberta_final()

    # Trazendo dados para o df_posicao_acoes
    df_posicao_acoes = df_posicao_acoes.merge(
        df_setor_acoes[['Ticker', 'Setor', 'Controle Acionário']],
        left_on='Ticker',
        right_on='Ticker',
        how='left'
    )

    # A IDÉIA AQUI É DEPOIS, TRAZER MAIS DADOS DE FONTES EXTERNAS COM WEBSCRAPING E CRIAR MAIS GRÁFICOS SEGMENTADOS QUE SEJAM ÚTEIS.
        # Já tenho no projeto Carteira1 alguns exemplos de webscrpaing.
        # Não fazer agora pois o foco agora é refatorar tudo que tem nos projetos Carteira1 e Web1 para que eu possa excluí-los e usar só CarteiraPro.


    return df_posicao_acoes