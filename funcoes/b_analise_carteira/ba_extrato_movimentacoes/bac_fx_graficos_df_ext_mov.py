import pandas as pd
import plotly.graph_objects as go

from icones import ICONE_INDICADOR_COMPRAS, ICONE_INDICADOR_VENDAS


def criar_grafico_preco_compras_df_ext_mov(df_ext_mov):
    """
    Cria um gráfico de linha mostrando a evolução do preço unitário por Ticker ao longo do tempo.
    """

    df_ext_mov_compras = df_ext_mov.copy()

    filtro = ((df_ext_mov_compras['Entrada/Saída'] == 'Credito') & (df_ext_mov_compras['Movimentação'] == 'Transferência - Liquidação'))
    df_ext_mov_compras = df_ext_mov_compras.loc[filtro]

    # Verificar se as colunas necessárias existem no DataFrame
    colunas_necessarias = ['Ticker', 'Data', 'Preço unitário']
    for coluna in colunas_necessarias:
        if coluna not in df_ext_mov_compras.columns:
            raise ValueError(f"Coluna '{coluna}' não encontrada no DataFrame")

    # Criar cópia do DataFrame para não modificar o original
    df_plot = df_ext_mov_compras.copy()

    # Converter coluna 'Data' para datetime (caso ainda não esteja)
    df_plot['Data'] = pd.to_datetime(df_plot['Data'])

    # Ordenar os dados por Data para garantir linhas contínuas
    df_plot = df_plot.sort_values('Data')

    # Criar figura do Plotly
    fig = go.Figure()

    # Obter lista única de Tickers e ordenar alfabeticamente
    tickers_unicos = sorted(df_plot['Ticker'].unique())

    # Para cada Ticker, adicionar uma linha no gráfico
    for i, ticker in enumerate(tickers_unicos):        # Filtrar dados apenas para este Ticker
        df_ticker = df_plot[df_plot['Ticker'] == ticker]

        # 🔥 Regra para iniciar com o 1o ticker visível, outros ocultos.
        visible = True if i == 0 else 'legendonly'

        # Adicionar linha ao gráfico
        fig.add_trace(
            go.Scatter(
                x=df_ticker['Data'],          # Eixo X: datas
                y=df_ticker['Preço unitário'], # Eixo Y: preços unitários
                mode='lines+markers',          # Modo: linhas com marcadores nos pontos
                name=ticker,                   # Nome da linha (aparece na legenda)
                visible=visible,               # 🔥 Esta é a chave!
                # Configurações visuais da linha
                line=dict(width=1),            # Espessura da linha
                marker=dict(size=2),           # Tamanho dos marcadores
                # 🔥 E ADICIONE ESTE PARÂMETRO:
                customdata=df_ticker[['Quantidade', 'Valor da Operação']].values
            )
        )

    # Configurar layout do gráfico
    fig.update_layout(
        plot_bgcolor='#0a0908',     # Fundo da área do gráfico
        paper_bgcolor='#0a0908',    # Fundo geral
        title={
            'text': "Compras por Ativo",  # Título com emoji
            'x': 0.5,
            'y': 0.95,
            'xanchor': 'center',
            'yanchor': 'top',
            # 'font': {
            #     'family': 'Segoe UI',
            #     'size': 16,
            #     'color': '#adb5bd'
            # }                                # Tamanho da fonte
        },
        # xaxis_title="📅 Data",                                  # Título do eixo X
        # yaxis_title="💰 Preço Unitário (R$)",                  # Título do eixo Y
        # Configurar hover (informações ao passar mouse)
        hovermode='closest',                                    # Mostra info do ponto mais próximo
        # Configurar legenda
        legend_title_text="Ativos",                          # Título da legenda
        legend=dict(
            yanchor="top",                                      # Âncora no topo
            y=0.99,                                             # Posição vertical
            xanchor="left",                                     # Âncora à esquerda
            x=0.99                                              # Posição horizontal
        ),
        # Configurar margens
        margin={"l": 40, "r": 40, "t": 70, "b": 40},            # Margens: left, right, top, bottom
        # Configurar grid
        # plot_bgcolor='rgba(240, 240, 240, 0.8)',               # Cor de fundo do gráfico
        # Configurar eixo X (datas)
        xaxis=dict(
            showgrid=False,                                      # Mostrar grid vertical
            # gridcolor='rgba(200, 200, 200, 0.5)',              # Cor do grid
            tickformat='%d/%m/%Y'                               # Formato brasileiro das datas
        ),
        # Configurar eixo Y (preços)
        yaxis=dict(
            showgrid=True,                                      # Mostrar grid horizontal
            # gridcolor='rgba(200, 200, 200, 0.5)',              # Cor do grid
            tickprefix='R$ ',                                   # Prefixo real nos valores
            tickformat=',.2f'                                   # Formato com 2 casas decimais
        )
    )


    # Configurar tooltip (informação que aparece ao passar mouse)
    fig.update_traces(
        hovertemplate=(
            '<b>%{fullData.name}</b><br>' +
            '%{x|%d/%m/%Y}<br><br>' +
            'Preço: R$ %{y:.2f}<br>' +
            'Qtd: %{customdata[0]}<br>' +
            'Total: R$ %{customdata[1]:.2f}<extra></extra>'
        )
    )


    return fig


def criar_grafico_compras_vendas_12m_df_ext_mov(df_ext_mov):
    """
    Cria um gráfico de barras verticais mostrando compras e vendas dos últimos 12 meses.

    Parâmetros:
    -----------
    df_ext_mov : pandas.DataFrame
        DataFrame contendo as movimentações financeiras

    Retorna:
    --------
    plotly.graph_objects.Figure
        Gráfico de barras verticais com compras e vendas por mês
    """

    # Criar cópia do DataFrame para não modificar o original
    df = df_ext_mov.copy()

    # -------------------------------------------------------------------------
    # 1. FILTRAR COMPRAS
    # Filtro para compras: Entrada/Saída = 'Credito' E Movimentação = 'Transferência - Liquidação'
    filtro_compras = (
        (df['Entrada/Saída'] == 'Credito') &
        (df['Movimentação'] == 'Transferência - Liquidação')
    )
    df_compras = df.loc[filtro_compras].copy()

    # -------------------------------------------------------------------------
    # 2. FILTRAR VENDAS  
    # Filtro para vendas: Entrada/Saída = 'Debito' E Movimentação = 'Transferência - Liquidação'
    filtro_vendas = (
        (df['Entrada/Saída'] == 'Debito') &
        (df['Movimentação'] == 'Transferência - Liquidação')
    )
    df_vendas = df.loc[filtro_vendas].copy()
    # Para vendas mudar sinal para barra nao e crescer pra baixo.
    df_vendas['Valor da Operação'] = df_vendas['Valor da Operação']*-1

    # -------------------------------------------------------------------------
    # 3. DEFINIR OS ÚLTIMOS 12 MESES
    # Encontrar a data mais recente no DataFrame
    data_maxima = df['Data'].max()

    # Criar lista dos últimos 12 meses (formato: YYYY-MM)
    meses = []
    for i in range(12):
        # Subtrair i meses da data máxima
        data = data_maxima - pd.DateOffset(months=i)
        # Formatar como 'YYYY-MM' para agrupamento
        meses.append(data.strftime('%Y-%m'))

    # Inverter a lista para ter do mais antigo para o mais recente
    meses = meses[::-1]

    # -------------------------------------------------------------------------
    # 4. AGRUPAR DADOS POR MÊS
    # Função auxiliar para agrupar e somar valores por mês
    def agrupar_por_mes(df_movimentacoes):
        if df_movimentacoes.empty:
            # Se não houver dados, retorna zeros para todos os meses
            return {mes: 0 for mes in meses}

        # Criar coluna de mês no formato YYYY-MM
        df_movimentacoes['Mes'] = df_movimentacoes['Data'].dt.strftime('%Y-%m')

        # Filtrar apenas os últimos 12 meses
        df_movimentacoes = df_movimentacoes[df_movimentacoes['Mes'].isin(meses)]

        # Agrupar por mês e somar o valor das operações
        agrupado = df_movimentacoes.groupby('Mes')['Valor da Operação'].sum()

        # Garantir que todos os meses apareçam (meses com valor zero)
        resultado = {mes: agrupado.get(mes, 0) for mes in meses}

        return resultado

    # Agrupar compras e vendas
    compras_por_mes = agrupar_por_mes(df_compras)
    vendas_por_mes = agrupar_por_mes(df_vendas)

    # -------------------------------------------------------------------------
    # 5. PREPARAR DADOS PARA O GRÁFICO
    # Converter meses para formato brasileiro (MM/YYYY)
    meses_formatados = [f"{mes[5:7]}/{mes[0:4]}" for mes in meses]

    # Valores de compras e vendas na ordem dos meses
    valores_compras = [compras_por_mes[mes] for mes in meses]
    valores_vendas = [vendas_por_mes[mes] for mes in meses]

    # -------------------------------------------------------------------------
    # 6. CRIAR GRÁFICO DE BARRAS VERTICAIS
    fig = go.Figure()

    # Barra de COMPRAS (verde)
    fig.add_trace(go.Bar(
        x=meses_formatados,  # Agora no eixo X (meses)
        y=valores_compras,   # Agora no eixo Y (valores)
        name='Compras',
        # Removido orientation='h' para barras verticais (padrão)
        marker_color='#2ecc71',  # Verde
        hovertemplate='<b>Compras</b><br>' +
                     'Mês: %{x}<br>' +
                     'Total: R$ %{y:,.2f}<br>' +
                     '<extra></extra>',
        text=[f'R$ {v:,.2f}' if v > 0 else '' for v in valores_compras],
        textposition='outside'
    ))

    # Barra de VENDAS (vermelho)
    fig.add_trace(go.Bar(
        x=meses_formatados,  # Agora no eixo X (meses)
        y=valores_vendas,    # Agora no eixo Y (valores)
        name='Vendas',
        # Removido orientation='h' para barras verticais (padrão)
        marker_color='#e74c3c',  # Vermelho
        hovertemplate='<b>Vendas</b><br>' +
                     'Mês: %{x}<br>' +
                     'Total: R$ %{y:,.2f}<br>' +
                     '<extra></extra>',
        text=[f'R$ {v:,.2f}' if v > 0 else '' for v in valores_vendas],
        textposition='outside'
    ))

    # -------------------------------------------------------------------------
    # 7. CONFIGURAR LAYOUT DO GRÁFICO
    fig.update_layout(

        plot_bgcolor='#0a0908',     # Fundo da área do gráfico
        paper_bgcolor='#0a0908',    # Fundo geral

        title={
            'text': 'Compras vs Vendas (últ. 12 Meses)',
            'x': 0.5,
            'y': 0.95,
            'xanchor': 'center',
            'yanchor': 'top',
            # 'font': {
            #     'family': 'Segoe UI',
            #     'size': 16,
            #     'color': '#adb5bd'
            # }
        },
        # xaxis_title='📅 Mês',
        # yaxis_title='💰 Valor Total (R$)',
        # Layout de barras agrupadas (grouped bar chart)
        barmode='group',
        # Configurações da legenda
        legend=dict(
            orientation='h',
            yanchor='bottom',
            y=1.02,
            xanchor='right',
            x=1
        ),
        # Margens
        margin={"l": 40, "r": 40, "t": 70, "b": 40},  # Aumentado bottom para rótulos dos meses
        # Cores de fundo
        # plot_bgcolor='rgba(240, 240, 240, 0.1)',
        # Configurar eixo X (meses)
        xaxis=dict(
            showgrid=False,
            # gridcolor='rgba(200, 200, 200, 0.3)',
            # Rotacionar rótulos para melhor legibilidade
            tickangle=-45,
            # Evitar que rótulos sejam cortados
            tickfont=dict(size=10)
        ),
        # Configurar eixo Y (valores)
        yaxis=dict(
            showgrid=True,
            # gridcolor='rgba(200, 200, 200, 0.3)',
            tickprefix='R$ ',
            tickformat=',.2f'
        ),
        # Altura do gráfico
        height=500,
        # Largura responsiva
        autosize=True
    )

    # # -------------------------------------------------------------------------
    # # 8. ADICIONAR INFORMAÇÕES ADICIONAIS (OPCIONAL)
    # # Calcular totais gerais
    # total_compras = sum(valores_compras)
    # total_vendas = sum(valores_vendas)
    # saldo = total_compras - total_vendas

    # # Adicionar anotações com totais
    # fig.add_annotation(
    #     x=0.5,
    #     y=1.12,  # Ajustado para ficar acima do título
    #     xref='paper',
    #     yref='paper',
    #     text=f'<b>Total Compras:</b> R$ {total_compras:,.2f} | ' +
    #          f'<b>Total Vendas:</b> R$ {total_vendas:,.2f} | ' +
    #          f'<b>Saldo:</b> R$ {saldo:,.2f}',
    #     showarrow=False,
    #     font=dict(size=12),
    #     align='center',
    #     bgcolor='rgba(255, 255, 255, 0.8)'
    # )

    return fig