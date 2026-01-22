# - Inicialmente, raspando apenas dados cadastrais de Ações e FIIs.
# - Base da CVM não tem coluna de ticker. Então, depois de obtê-la, dar merge dela com base manual através do CNPJ para obter setor/segmento dos ativos da base da CVM.
# - Base manual de ações até já tem setor/segmento, mas vou puxar da CVM também por 2 motivos: 
    # Manter o padrão e também porque base da CVM tem várias outras informações que podem ser úteis no futuro.
# Tratamento das bases oriundas de webscraping: Se for óbvio, tratar aqui mesmo. Se não, tratar fora. Como se fossem classes e subclasses.

import pandas as pd
import zipfile
from io import BytesIO
import requests

from funcoes._global.fxg_tratamento import g_aplicar_datetime_cols


# -------------------------------------------------------------------------------------------------------- AÇÕES
# Só tratei cols de data.
def g_criar_df_cvm_cad_cia_aberta():
    """
    Acessa site da CVM e cria df com dados de cadastro das companhias.

    """

    # URL do CSV
    url = "https://dados.cvm.gov.br/dados/CIA_ABERTA/CAD/DADOS/cad_cia_aberta.csv"

    # Lê diretamente
    df_cvm_cad_cia_aberta = pd.read_csv(url, encoding='ISO-8859-1', sep=';')

    # Filtra as colunas que começam com 'DT_'
    lista_cols_data = [col for col in df_cvm_cad_cia_aberta.columns if col.startswith('DT_')]
    # Trata cols de data
    df_cvm_cad_cia_aberta = g_aplicar_datetime_cols(df=df_cvm_cad_cia_aberta, lista_colunas_data=lista_cols_data)

    return df_cvm_cad_cia_aberta


# -------------------------------------------------------------------------------------------------------- FIIS
# Pelo que vi, base da CVM tem 4 links para FIIs (3 Informes Mes/Tri/Ano + 1 DemoFinanceiras).
# Cada link pode ter 1 ou mais arquivos.
# 3 tipos de período para Informes: (Mensal: 3 arqs / Tri e Anual: Vários arquivos)
    # Cada período terá as linhas assim:
        # Mês: Ticker se repete 12x, 1 para cada mês
        # Tri: Ticker se repete 4x, 1 para cada trimestre
        # Ano: Ticker não se repete
    # Seja Mês/Tri/Ano, todos os informes têm dados cadastrais. Vou usar o mensal (atualizado mensalmente).
    # Mas para outras infos, os informes tri e anual podem ter infos relevantes q o mensal nao tem.
# Demonstrações Financeiras: (1 arquivo)
    # De relevante só tem o link para aquela página que acessa os rels gerenciais.

# Para dados cadastrais posso ir atualizando o ano do link uma vez por ano.
# Para série históricas terei que pegar 1 link para cada ano. Fazer em outra fx.
# Motivo de não usar para segmento:
# Eu precisava separar papel de tijolo e essa base não tinha isso. Eu até ia tentar conseguir essa info por fora,
# mas para piorar, ela classificava MXRF11 como logística, RECR11 como multiestratégia... Vou usar base manual do Inv10.
def SEMUSOPARADADOSCADASTRAISg_criar_dfs_inf_mensal_fii():
    """
    Carrega os 3 arquivos CSV do ZIP da CVM e retorna DataFrames separados.
    """
    
    # Link:
    url_zip = "https://dados.cvm.gov.br/dados/FII/DOC/INF_MENSAL/DADOS/inf_mensal_fii_2025.zip"

    # Baixa o arquivo ZIP
    response = requests.get(url_zip)
    zip_bytes = BytesIO(response.content)
    
    # Lista para armazenar os DataFrames
    dataframes = []
    
    with zipfile.ZipFile(zip_bytes) as z:
        # Pega a lista de todos os arquivos no ZIP
        arquivos = z.namelist()
        
        # Verifica se há pelo menos 3 arquivos
        if len(arquivos) < 3:
            raise ValueError(f"Esperados 3 arquivos no ZIP, encontrados {len(arquivos)}")
        
        # Itera sobre os 3 primeiros arquivos
        for arquivo_csv in arquivos[:3]:
            # Lê cada arquivo CSV com configurações específicas para CVM
            df = pd.read_csv(
                z.open(arquivo_csv),
                encoding='ISO-8859-1',
                sep=';',               # Separador correto para dados CVM
                on_bad_lines='skip',   # Ignora linhas problemáticas
            )

            # Pega todas que começam com 'Data_'
            lista_cols_data = [col for col in df.columns if col.startswith('Data_')]
            # Trata cols de data
            df = g_aplicar_datetime_cols(df=df, lista_colunas_data=lista_cols_data)
            
            dataframes.append(df)
    
    # Atribui os DataFrames aos nomes específicos
    df_inf_mensal_fii_ativo_passivo = dataframes[0]  # Índice 0
    df_inf_mensal_fii_complemento = dataframes[1]    # Índice 1  
    df_inf_mensal_fii_geral = dataframes[2]          # Índice 2
    
    # Retorna os 3 DataFrames como tupla
    return (
        df_inf_mensal_fii_ativo_passivo,
        df_inf_mensal_fii_complemento, 
        df_inf_mensal_fii_geral
    )
# # Chama a função e recebe os 3 DataFrames
# (df_inf_mensal_fii_ativo_passivo, df_inf_mensal_fii_complemento, df_inf_mensal_fii_geral) = g_criar_dfs_inf_mensal_fii()
