import pandas as pd


# --------------------------------------------------------------------------------------------------------------------------------  Definindo fxs internas

# df_posicao já existirá na página 'Análise carteira'. Então é só entregá-lo a fx.
def _iniciar_df_posicao_etfs(df_posicao):

    df_posicao_etfs = df_posicao.copy()

    # Mantendo apenas linhas de ações.
    df_posicao_etfs = df_posicao_etfs.loc[df_posicao_etfs['Tipo'] == 'ETF']

    # Excluindo col que não fará mais sentido, uma vez que o df agora é só de 1 tipo
    df_posicao_etfs = df_posicao_etfs.drop('Tipo', axis=1)

    return df_posicao_etfs

# _______________________________ Parte 2: Criar colunas fora do df e trazê-las.










# --------------------------------------------------------------------------------------------------------------------- FX principal que cria o df_posicao_acoes
def criar_df_posicao_etfs(df_posicao):

    df_posicao_etfs = _iniciar_df_posicao_etfs(df_posicao=df_posicao)


    # A IDÉIA AQUI É DEPOIS, TRAZER MAIS DADOS DE FONTES EXTERNAS COM WEBSCRAPING E CRIAR MAIS GRÁFICOS SEGMENTADOS QUE SEJAM ÚTEIS.
        # Já tenho no projeto Carteira1 alguns exemplos de webscrpaing.
        # Não fazer agora pois o foco agora é refatorar tudo que tem nos projetos Carteira1 e Web1 para que eu possa excluí-los e usar só CarteiraPro.


    return df_posicao_etfs