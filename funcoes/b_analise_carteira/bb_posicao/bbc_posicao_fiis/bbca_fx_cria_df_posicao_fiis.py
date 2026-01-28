import pandas as pd


# --------------------------------------------------------------------------------------------------------------------------------  Definindo fxs internas

# df_posicao já existirá na página 'Análise carteira'. Então é só entregá-lo a fx.
def _iniciar_df_posicao_fiis(df_posicao):

    df_posicao_fiis = df_posicao.copy()

    # Mantendo apenas linhas dos 3 tipos.
    # Explicação na fx primária que cria a col 'Tipo de Ativo' no df_ext_mov.
    df_posicao_fiis = df_posicao_fiis.loc[
        df_posicao_fiis['Tipo'].isin(['FII', 'FIAgro', 'FIInfra'])
        ]

    # Excluindo col que não fará mais sentido, uma vez que o df agora é só de 1 tipo
    df_posicao_fiis = df_posicao_fiis.drop('Tipo', axis=1)

    return df_posicao_fiis

# _______________________________ Parte 2: Criar colunas fora do df e trazê-las.
# Motivo de não usar base da CVM para para tipo e segmento:
# Eu precisava separar papel de tijolo  base CVM não tinha isso. Eu até ia tentar conseguir essa info por fora,
# mas para piorar, ela classificava MXRF11 como logística, RECR11 como multiestratégia... Vou usar base manual do Inv10.
def _criar_cols_tipo_segmento(df_posicao_fiis):
    """
    Base obtida do Investidor10 e depois acoplada a base manual interna.
    Cria as 2 cols de categoria: Tipo de Fundo e Segmento.
    """

    # ----------------------------------------------------------- Obtendo dfs de fiis, fiagros, fiinfras da base interna
    # Lê e concatena tudo de uma vez
    df_base_fiis = pd.concat([
        pd.read_excel('bases_dados/ativos_dados_cadastrais.xlsx', sheet_name='FIIs'),
        pd.read_excel('bases_dados/ativos_dados_cadastrais.xlsx', sheet_name='FIAgros'),
        pd.read_excel('bases_dados/ativos_dados_cadastrais.xlsx', sheet_name='FIInfras')
    ], ignore_index=True)

    # ----------------------------------------------------------------- # Criando um 3º df que une ticker+categorias
    # Trouxe só essas 2 categorias pois foram as únicas que achei fazerem sentido.
    df_posicao_fiis = df_posicao_fiis.merge(
        df_base_fiis[['Ticker', 'Tipo de Fundo', 'Segmento']],
        left_on='Ticker',
        right_on='Ticker',
        how='left'
    )

    # ----------------------------------------------------------------- # Tratamentos 
    # Substitui 'Fundo de papel' por 'Fundo de Papel' na coluna 'Tipo de Fundo'
    df_posicao_fiis['Tipo de Fundo'] = df_posicao_fiis['Tipo de Fundo'].replace(
        'Fundo de papel',  # Valor original
        'Fundo de Papel'   # Novo valor
    )

    # Abreviando algumas nomenclaturas de segmento
    df_posicao_fiis['Segmento'] = df_posicao_fiis['Segmento'].replace(
    'Títulos e Valores Mobiliários',  # Valor original
    'Tít. e Val. Mob.'   # Novo valor
    ).replace(
        'Logístico / Indústria / Galpões',
        'Logística'
    ).replace(
        'Shoppings / Varejo',
        'Shoppings'
    )
    

    return df_posicao_fiis









# --------------------------------------------------------------------------------------------------------------------- FX principal que cria o df_posicao_acoes
def criar_df_posicao_fiis(df_posicao):

    df_posicao_fiis = _iniciar_df_posicao_fiis(df_posicao=df_posicao)

    df_posicao_fiis = _criar_cols_tipo_segmento(df_posicao_fiis=df_posicao_fiis)


    # A IDÉIA AQUI É DEPOIS, TRAZER MAIS DADOS DE FONTES EXTERNAS COM WEBSCRAPING E CRIAR MAIS GRÁFICOS SEGMENTADOS QUE SEJAM ÚTEIS.
        # Já tenho no projeto Carteira1 alguns exemplos de webscrpaing.
        # Não fazer agora pois o foco agora é refatorar tudo que tem nos projetos Carteira1 e Web1 para que eu possa excluí-los e usar só CarteiraPro.


    return df_posicao_fiis