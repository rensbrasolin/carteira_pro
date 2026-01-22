import streamlit as st
import pandas as pd

from icones import (
    # Abas principais
    TITULO_EXTRATO,
    # Expanders das abas e sub-abas
    TITULO_FILTROS, ICONE_FILTROS, TITULO_INDICADORES, ICONE_INDICADORES, TITULO_DADOS, ICONE_DADOS,
    # Indicadores Extrato
    TITULO_INDICADOR_COMPRAS, ICONE_INDICADOR_COMPRAS,
    TITULO_INDICADOR_VENDAS, ICONE_INDICADOR_VENDAS,
    TITULO_INDICADOR_REMUNERACOES, ICONE_INDICADOR_REMUNERACOES,
)
from funcoes._global.fxg_filtro import g_filtro_col_data, g_filtro_col_string
from funcoes._global.fxg_tratamento import g_formatar_valor_grande_indicadores


# ---------------------------------------------------------------------------------------------------------- Fxs Indicadores
# Apenas calculá-los. Serão exibidos na fx de exibir
def calc_indicador_compras_df_ext_mov_exib(df_ext_mov_exib):
    filtro = ((df_ext_mov_exib['Entrada/Saída'] == 'Credito') &
              (df_ext_mov_exib['Movimentação'] == 'Transferência - Liquidação'))

    total_compras = df_ext_mov_exib.loc[filtro, 'Valor da Operação'].sum()

    return total_compras
    

def calc_indicador_vendas_df_ext_mov_exib(df_ext_mov_exib):
    filtro = ((df_ext_mov_exib['Entrada/Saída'] == 'Debito') &
              (df_ext_mov_exib['Movimentação'] == 'Transferência - Liquidação'))

    total_vendas = df_ext_mov_exib.loc[filtro, 'Valor da Operação'].sum() *-1 #*-1 pra não ficar (-)

    return total_vendas


def calc_indicador_remuneracoes_df_ext_mov_exib(df_ext_mov_exib):
    filtro = ((df_ext_mov_exib['Movimentação'] == 'Dividendo') |
             (df_ext_mov_exib['Movimentação'] == 'Juros Sobre Capital Próprio') |
             (df_ext_mov_exib['Movimentação'] == 'Rendimento')
              ) # Se tiver mais, acrescentar conforme for descobrindo

    total_remuneracoes = df_ext_mov_exib.loc[filtro, 'Valor da Operação'].sum()

    return total_remuneracoes
# ---------------------------------------------------------------------------------------------------- Exibição com st.dataframe
# Aqui no df_ext_mov, como é mais simples, tudo (filtro,indicadores e df) é exibido dentro da mesma fx.
def exibir_df_ext_mov(df_ext_mov):
    """
    Exibe filtros, métricas e df.
    """

    df_ext_mov_exib = df_ext_mov.copy()

    # ______________________________________________________________________________________FILTROS
    with st.expander(f'{TITULO_FILTROS} *{TITULO_EXTRATO}*', expanded=False, icon=f'{ICONE_FILTROS}'):
        st.markdown('', help="Apenas os gráficos não sofrem influência dos filtros")

        # Data
        col1, col2 = st.columns(2)
        with col1:
            df_ext_mov_exib = g_filtro_col_data(
                df=df_ext_mov_exib, coluna_data='Data', posicao='horizontal', nome_df='df_ext_mov_exib')
            
        # Strings (Poderia perorrer, mas prefiro ter controle de onde pôr o campo no layout)    
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            df_ext_mov_exib = g_filtro_col_string(df_ext_mov_exib, 'Tipo de Ativo', nome_df='df_ext_mov_exib')
        with col2:
            df_ext_mov_exib = g_filtro_col_string(df_ext_mov_exib, 'Ticker', nome_df='df_ext_mov_exib')
        with col3:
            df_ext_mov_exib = g_filtro_col_string(df_ext_mov_exib, 'Entrada/Saída', nome_df='df_ext_mov_exib')
        with col4:
            df_ext_mov_exib = g_filtro_col_string(df_ext_mov_exib, 'Movimentação', nome_df='df_ext_mov_exib')


        # ______________________________________________________________________________________MÉTRICAS
    with st.expander(f'{TITULO_INDICADORES} *{TITULO_EXTRATO}*', expanded=False, icon=f'{ICONE_INDICADORES}'):
        col1, col2, col3 = st.columns(3)
        with col1:
            indicador_compras_df_ext_mov_exib =calc_indicador_compras_df_ext_mov_exib(df_ext_mov_exib=df_ext_mov_exib)
            indicador_compras_df_ext_mov_exib_fmt = g_formatar_valor_grande_indicadores(indicador_compras_df_ext_mov_exib)  # "R$ 1.3M"
            st.metric(f'{ICONE_INDICADOR_COMPRAS} {TITULO_INDICADOR_COMPRAS}', indicador_compras_df_ext_mov_exib_fmt,
                      help=f'R$ {indicador_compras_df_ext_mov_exib:,.2f}', border=True,
            #   width=400,
            #   height=50
            )

        with col2:
            indicador_vendas_df_ext_mov_exib = calc_indicador_vendas_df_ext_mov_exib(df_ext_mov_exib=df_ext_mov_exib)
            indicador_vendas_df_ext_mov_exib_fmt = g_formatar_valor_grande_indicadores(indicador_vendas_df_ext_mov_exib)
            st.metric(f'{ICONE_INDICADOR_VENDAS} {TITULO_INDICADOR_VENDAS}', indicador_vendas_df_ext_mov_exib_fmt,
                      help=f'R$ {indicador_vendas_df_ext_mov_exib:,.2f}', border=True,
                      )
        with col3:
            indicador_remuneracoes_df_ext_mov_exib =calc_indicador_remuneracoes_df_ext_mov_exib(df_ext_mov_exib=df_ext_mov_exib)
            indicador_remuneracoes_df_ext_mov_exib_fmt = g_formatar_valor_grande_indicadores(indicador_remuneracoes_df_ext_mov_exib)
            st.metric(f'{ICONE_INDICADOR_REMUNERACOES} {TITULO_INDICADOR_REMUNERACOES}', indicador_remuneracoes_df_ext_mov_exib_fmt,
                      border=True,
                      help=f"""
                      R$ {indicador_remuneracoes_df_ext_mov_exib:,.2f}\n
                      Soma dos recebimentos de:
                    - Dividendo
                    - Juros Sobre Capital Próprio
                    - Rendimento"""
              )

    # ______________________________________________________________________________________DF

    # Defina EXATAMENTE como cada coluna deve ser formatada
    COLUMN_CONFIG = {
        # DATAS
        'Data': st.column_config.DateColumn("Data", format="DD/MM/YYYY"),
        
        # VALORES MONETÁRIOS 
        'Preço unitário': st.column_config.NumberColumn("Preço unitário", format="dollar"), # R$     %.2f
        'Valor da Operação': st.column_config.NumberColumn("Valor da Operação", format="dollar"), #localized
        
        # # QUANTIDADES INTEIRAS
        # 'Quantidade': st.column_config.NumberColumn("Quantidade", format="%d"),
        
        # # PERCENTUAIS
        # 'Taxa': st.column_config.NumberColumn("Taxa", format="%.2f%%"),
    }

    # Mostrar
    lista_ordem_cols = ['Data', 'Tipo de Ativo', 'Ticker', 'Entrada/Saída', 'Movimentação',
            'Preço unitário', 'Quantidade', 'Valor da Operação', 'Instituição', 'Produto']  

    with st.expander(f'{TITULO_DADOS} *{TITULO_EXTRATO}*', expanded=False, icon=f'{ICONE_DADOS}'):
        st.dataframe(
            df_ext_mov_exib,
            column_order=lista_ordem_cols,
            column_config=COLUMN_CONFIG, # É por aqui que vou conseguir criar cols com imagem e gráfico. Ver na doc do st.
            use_container_width=True,
            hide_index=True
        )



# --------------------------------------------------------------------------------------------------------- Exibição com AgGrid
# Até funciona mas não me sinto 100% no controle com grid.
# Decidi não usá-lo pq filtro na col de data tem que preencher hora também. Não adiantou mudar type para Date.
# Aí então eu desabilitei o filtro só na col de data e criei um filtro manual para data. Mas filtro manual e grid[data] não
# se comunicavam bem e as vezes a atualização acontecia no grid mas nao nos dados do grid. Então não dá pra usar pois metricas tem que 
# sofrer influencia dos dados filtrados no df.
def SEMUSO_renderizar_grid_df_ext_mov(df_ext_mov):

    from st_aggrid import AgGrid, GridOptionsBuilder


    df_ext_mov_grid = df_ext_mov.copy()
 
    # Filtro de Data
    df_ext_mov_grid = g_filtro_col_data(df=df_ext_mov_grid, coluna_data='Data', posicao='horizontal')

    # Usando grid é melhor ordenar o próprio df do que o objeto grid.
    lista_ordem_cols = ['Data', 'Ticker','Tipo de Ativo', 'Entrada/Saída', 'Movimentação',
    'Preço unitário', 'Quantidade', 'Valor da Operação', 'Instituição', 'Produto']

    df_ext_mov_grid = df_ext_mov_grid[lista_ordem_cols]

    # Configurar a tabela.
    gb = GridOptionsBuilder.from_dataframe(df_ext_mov_grid)

    # CONFIGURAÇÕES PADRÃO PARA TODAS AS COLUNAS
    # configure_default_column() aplica configurações globais a todas as colunas
    gb.configure_default_column(
        filterable=True,      # Ativa filtros em todas as colunas, menos string
        filter=True,          # Ativa filtros em todas as colunas, inclusive string
        sortable=True,        # Permite ordenação clicando no cabeçalho
        resizable=True,       # Permite redimensionar largura das colunas
        editable=False,       # Desativa edição direta nas células (apenas visualização)     
        minWidth=75,          # Largura mínima das colunas
        # wrapHeaderText=True,    # Quebra texto do cabeçalho se for longo
        autoHeaderHeight=True     # Ajusta altura do cabeçalho automaticamente
    )

    # Identificar cols float
    colunas_num_float = df_ext_mov_grid.select_dtypes(include=['float64', 'float32']).columns
    # Aplicar valueFormatter para cols numéricas. Formato brasileiro.
    for coluna in colunas_num_float:
        gb.configure_column(
            coluna,
            valueFormatter="value.toLocaleString('pt-BR', {minimumFractionDigits: 2, maximumFractionDigits: 2})")
        
    # Identificar cols int
    colunas_num_int = df_ext_mov_grid.select_dtypes(include=['int64', 'int32']).columns
    # Aplicar valueFormatter para cols numéricas. Formato brasileiro.
    for coluna in colunas_num_int:
        gb.configure_column(
            coluna,
            valueFormatter="value.toLocaleString('pt-BR');")


    # FORMATAÇÃO DE DATAS (verifica se a coluna existe)
    if "Data" in df_ext_mov_grid.columns:
        # Verifica se é realmente uma coluna de data
        if pd.api.types.is_datetime64_any_dtype(df_ext_mov_grid["Data"]):
            gb.configure_column(
                "Data",
                filter=False,
                valueFormatter="new Date(value).toLocaleDateString('pt-BR')"
            )
        else:
            # Se não for datetime, converte
            try:
                df_ext_mov_grid["Data"] = pd.to_datetime(df_ext_mov_grid["Data"])
                gb.configure_column(
                    "Data", 
                    valueFormatter="new Date(value).toLocaleDateString('pt-BR')"
                )
            except:
                # Se não puder converter, deixa como texto
                pass


    # CONFIGURAÇÕES ADICIONAIS DO GRID
    # configure_grid_options() define opções gerais do grid (não específicas por coluna)
    gb.configure_grid_options(
        # Ativa paginação (divide dados em páginas)
        pagination=True,
        # Número de linhas por página
        paginationPageSize=50,
        )

    grid_options = gb.build()


    # EXIBIR O GRID NO STREAMLIT
    # AgGrid() renderiza o grid com as configurações geradas
    grid_response = AgGrid(
        df_ext_mov_grid,           # DataFrame com os dados
        gridOptions=grid_options,  # Configurações geradas
        height=500,           # Altura fixa do grid em pixels
        width='100%',         # Largura total do container
        theme='alpine',    # Tema visual (opções: 'streamlit', 'alpine', 'balham', 'material')
        fit_columns_on_grid_load=True,  # Ajusta colunas para caber na largura
        allow_unsafe_javascript=True,    # Permite JavaScript customizado (necessário para formatação)
        reload_data=True, # =True: A cada rerun, o grid descarta tudo e recarrega do zero. =False: Mantém estado atual (ordenação, filtros, paginação) entre reruns
        enable_enterprise_modules=True, # Ativa os módulos enterprise do ag-Grid (versão paga original), que o st_aggrid disponibiliza gratuitamente.
        # update_on=['cellValueChanged', 'selectionChanged', 'filterChanged', 'sortChanged'],
        allow_dom_layout=True,        # Layout responsivo
        key="df_ext_mov_grid"  # Chave única para cache
    )

    # grid_response é um objeto, por isso retorna dados, para poder acessar dados do grid como se fosse um df
    # e criar metricas que sofram influêcia dos filtros do frid.
    return grid_response['data']
