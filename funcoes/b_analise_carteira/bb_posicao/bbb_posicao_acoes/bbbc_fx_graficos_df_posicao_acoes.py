import plotly.graph_objects as go
import plotly.express as px


# -------------------------------------------------------------------------------------------------------------------- Gráfico 1a
def _criar_grafico_cm_pa_rem_df_posicao_acoes(df_posicao_acoes):

    df = df_posicao_acoes.copy()

    # Excluindo posições zeradas do df, pois para variação % não faz sentido.
    df = df[df['Qtd'] != 0]

    # Ordenar os ativos
    df = df.sort_values(by='Custo Médio', ascending=False)

    fig = go.Figure()

    # Adicionar a barra de 'Custo Médio' (barra individual)
    fig.add_trace(go.Bar(
        x=df['Ticker'],
        y=df['Custo Médio'],
        name='Custo Médio',
        offsetgroup=1,  # Grupo de barras composto
        marker={"color": "#ef476f"} #d1495b 219ebc
    ))

    # Adicionar a barra de 'Patrimônio Atual' (base da barra composta)
    fig.add_trace(go.Bar(
        x=df['Ticker'],
        y=df['Patrimônio Atual'],
        name='Patrimônio Atual',
        offsetgroup=2,
        marker={"color": "#26547c"}, # 00798c 023047
        # Rótulo
        text=df['Variação %'].apply(lambda x: f'{x:.0f}%'),
        textposition='inside',  # Dentro da barra
        insidetextanchor='end',  # start middle end
        textangle=0,  # Mantém o texto na horizontal
        textfont={
            "family": "Segoe UI",  # Acrescentar 'Black' na 'Segoe UI' caso queira negrito
            "size": 9,
            "color": df['Variação %'].apply(lambda x: "#ffb3c1" if x < 0 else "#b7e4c7").tolist()
            # 52b788
        }
    ))

    # Adicionar a barra de 'Remunerações' (empilhada sobre 'Patrimônio Atual')
    fig.add_trace(go.Bar(
        x=df['Ticker'],
        y=df['Remunerações'],
        name='Remunerações',
        base=df['Patrimônio Atual'],  # Começa no topo de 'Patrimônio Atual'
        offsetgroup=2,  # Mesmo grupo que 'Patrimônio Atual'
        marker={"color": "#ffd166"}, # edae49 ffb703
        visible='legendonly'  # Começa oculta no gráfico, mas visível na legenda
    ))

    # Ajustar layout
    fig.update_layout(
        barmode='group',  # Barras lado a lado
        plot_bgcolor='#0a0908',  # Fundo da área do gráfico #202020 #1d1e18 0a0908
        paper_bgcolor='#0a0908',  # Fundo geral (inclusive margens)
        margin={"l": 40, "r": 40, "t": 40, "b": 40},

        yaxis={  # Eixo Y (valores)
            "showgrid": True,
            "gridcolor": '#161a1d',
            "gridwidth": 1,
            "zeroline": False,
            'tickprefix': 'R$ ',
            'tickformat': ',.0f',  # separador de milhar e duas casas decimais
            'separatethousands': True,
            # "tickfont": {  # Cor dos valores do eixo Y
            #     "color": "#adb5bd"
            # }
        },
        xaxis={  # Eixo X (ativos)
            # "tickfont": {  # Cor dos rótulos no eixo X
            #     "color": "#adb5bd",
            #     "size": 11,
            # },
            "tickangle": 0 # <- ROTACAO DO LABEL DO EIXO X (ajuste aqui: positivo ou negativo em graus)
        },

        title={  # Título do gráfico
            "text": 'Investimento x Retorno',
            "x": 0.5,
            "y": 0.97,
            "xanchor": 'center',
            "yanchor": 'top',
            # "font": {  # Cor e estilo do título
            #     "color": "#adb5bd",
            #     "size": 16,
            #     "family": "Segoe UI"
            # }
        },
        xaxis_title='',  # Remove o título do eixo X
        yaxis_title='',  # Remove o título do eixo Y

        showlegend=True,  # Exibe a legenda
        legend={  # Estilo da legenda
            "orientation": "h",
            "yanchor": "bottom",
            "y": -0.2,
            "xanchor": "center",
            "x": 0.5,
            # "font": {
            #     "color": "#adb5bd",  # Cor da legenda
            #     "size": 12,
            #     "family": "Segoe UI"
            # }
        }
    )

    # Texto com quebras de linha manuais para o hover
    hover_msg = (
        'Clicando em "Remunerações" na legenda abaixo, é possível incluí-la na análise de retorno. <br>'
        'No entanto, ao vender parte ou a totalidade de um ativo, a análise das remunerações neste <br>'
        'gráfico pode se tornar imprecisa. Isso ocorre porque os valores de “Custo Médio” e        <br>'
        '“Patrimônio Atual” são reduzidos conforme as vendas, enquanto as “Remunerações” continuam <br>'
        'acumuladas. Assim, o rendimento visual parecerá maior do que foi de fato.'
    )

    # Inserir uma anotação no gráfico
    fig.add_annotation(
        text="⚠️",  # Texto que será exibido (ícone de ajuda)
        xref="paper",
        yref="paper",
        x=0.60,
        y=1.09,
        showarrow=False,
        # font={"size": 14, "color": "#f6fff8"},  # Cor do ícone/emoji
        align="center",
        hovertext=hover_msg,
        hoverlabel={  # Estilo do tooltip (ajuda)
            "bgcolor": "#333",  # Cor de fundo do tooltip
            "bordercolor": "#555",  # Cor da borda
            # "font": {
            #     "family": "Segoe UI",
            #     "size": 13,
            #     "color": "#ffffff"
            # }
        }
    )

    return fig

# -------------------------------------------------------------------------------------------------------------------- Gráfico 1b
def _criar_grafico_cm_pa_rem_total_df_posicao_acoes(
    indicador_custo_medio_df_posicao_acoes,
    indicador_patrimonio_atual_df_posicao_acoes,
    indicador_remuneracoes_df_posicao_acoes,
    indicador_variacao_percentual_df_posicao_acoes
):
    fig = go.Figure()

    # Adicionar a barra de 'Custo Médio' (barra individual)
    fig.add_trace(go.Bar(
        x=['TOTAL'],
        y=[indicador_custo_medio_df_posicao_acoes],
        name='CM',
        offsetgroup=1,
        marker={"color": "#ef476f"},
        showlegend=False
    ))

    # Adicionar a barra de 'Patrimônio Atual'
    fig.add_trace(go.Bar(
        x=['TOTAL'],
        y=[indicador_patrimonio_atual_df_posicao_acoes],
        name='PA',
        offsetgroup=2,
        marker={"color": "#26547c"},
        showlegend=False,
        text=[f'{indicador_variacao_percentual_df_posicao_acoes:.0f}%'],
        textposition='inside',
        insidetextanchor='end',
        textangle=0,
        textfont={
            "family": "Segoe UI",
            "size": 9,
            "color": "#ffb3c1" if indicador_variacao_percentual_df_posicao_acoes < 0 else "#b7e4c7"
        }
    ))

    # Adicionar a barra de 'Remunerações'
    fig.add_trace(go.Bar(
        x=['TOTAL'],
        y=[indicador_remuneracoes_df_posicao_acoes],
        name='Rem',
        base=[indicador_patrimonio_atual_df_posicao_acoes],
        offsetgroup=2,
        marker={"color": "#ffd166"},
        visible='legendonly'
    ))

    # Layout igual ao gráfico por ativo
    fig.update_layout(
        barmode='group',
        plot_bgcolor='#0a0908',
        paper_bgcolor='#0a0908',
        margin={"l": 40, "r": 40, "t": 40, "b": 40},
        yaxis={
            "showgrid": True,
            "gridcolor": '#161a1d',
            "gridwidth": 1,
            "zeroline": False,
            "tickfont": {
                # "color": "#adb5bd"
            }
        },
        xaxis={
            # "tickfont": {
            #     "color": "#adb5bd",
            #     "size": 11
            # },
            "tickangle": 0
        },
        title={
            "text": '',
            "x": 0.5,
            "y": 0.97,
            "xanchor": 'center',
            "yanchor": 'top',
            # "font": {
            #     "color": "#adb5bd",
            #     "size": 14,
            #     "family": "Segoe UI"
            # }
        },
        xaxis_title='',
        yaxis_title='',
        legend={
            "orientation": "h",
            "yanchor": "top",
            "y": -0.1,
            "xanchor": "center",
            "x": 0.5,
            # "font": {
            #     "color": "#adb5bd",
            #     "size": 12,
            #     "family": "Segoe UI"
            # }
        }
    )

    return fig
# -------------------------------------------------------------------------------------------------------------------- Gráfico 2
def _criar_grafico_distrib_cm_setor_df_posicao_acoes(df_posicao_acoes):
    # Ordenar valores decrescentes para consistência visual
    df = df_posicao_acoes.copy()
    df = df.sort_values(by='Custo Médio', ascending=False)

    # Criar gráfico Sunburst com hierarquia: Tipo > Ativo
    fig = px.sunburst(
        df,
        path=['Setor', 'Ticker'],  # Hierarquia: primeiro o Tipo, depois o Ativo
        values='Custo Médio',
        color='Setor',  # Cores por Tipo (você pode personalizar mais abaixo)
        # Paleta de 10 cores pois podem existir muitos setores
        color_discrete_sequence=["#0c285e","#174e86","#2d92d1","#74c9e8","#97e4f4","#5e0c27","#87153b","#d12e64","#e8749a","#f497b6"]
    )

    # Atualizar o layout do gráfico
    fig.update_layout(
        plot_bgcolor='#0a0908',     # Fundo da área do gráfico
        paper_bgcolor='#0a0908',    # Fundo geral
        margin={"l": 40, "r": 40, "t": 5, "b": 5},  # Margens internas

        title={
            'text': 'Composição do Custo Médio por Setor',
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

        # font={
        #     'family': 'Segoe UI',
        #     'color': '#adb5bd',
        #     'size': 12
        # }
    )

    # Exibir valores em formato brasileiro no hover
    fig.update_traces(
        textinfo='label+percent entry',  # 'entry' mostra o rótulo do nó, mesmo nos níveis superiores
        hovertemplate='<b>%{label}</b><br>Custo Médio: R$ %{value:,.0f}<br>Porcentagem: %{percentRoot:.1%}',
        maxdepth=2,  # Limita o número de níveis visíveis (0 = raiz, 1 = 1º nível, 2 = até o 2º nível)
        insidetextorientation="radial",  # Orientação do texto dentro das fatias (melhor visual em círculos)
        domain={
        "x": [0.1, 0.9],  # Ocupa de 10% a 90% da largura disponível (horizontal)
        "y": [0.05, 0.875]  # Ocupa de 10% a 90% da altura disponível (vertical)
    }
    )

    return fig

# -------------------------------------------------------------------------------------------------------------------- Gráfico 3

def _criar_grafico_distrib_pa_setor_df_posicao_acoes(df_posicao_acoes):
    # Ordenar valores decrescentes para consistência visual
    df = df_posicao_acoes.copy()
    df = df.sort_values(by='Patrimônio Atual', ascending=False)

    # Criar gráfico Sunburst com hierarquia: Tipo > Ativo
    fig = px.sunburst(
        df,
        path=['Setor', 'Ticker'],  # Hierarquia: primeiro o Tipo, depois o Ativo
        values='Patrimônio Atual',
        color='Setor',  # Cores por Tipo (você pode personalizar mais abaixo)
        # Paleta de 10 cores pois podem existir muitos setores
        # ["#00193a","#002b53","#023f73","#034780","#7a0213","#a10220","#bf0a26","#cd0c2b","#131313","#262626"]
        color_discrete_sequence=["#0c285e","#174e86","#2d92d1","#74c9e8","#97e4f4","#5e0c27","#87153b","#d12e64","#e8749a","#f497b6"]
    )

    # Atualizar o layout do gráfico
    fig.update_layout(
        plot_bgcolor='#0a0908',     # Fundo da área do gráfico
        paper_bgcolor='#0a0908',    # Fundo geral
        margin={"l": 40, "r": 40, "t": 5, "b": 5},  # Margens internas

        title={
            'text': 'Composição do Patrimônio Atual por Setor',
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

        # font={
        #     'family':'Segoe UI',
        #     'color':'#adb5bd',
        #     'size':12
        # }
    )

    # Exibir valores em formato brasileiro no hover
    fig.update_traces(
        textinfo='label+percent entry',  # 'entry' mostra o rótulo do nó, mesmo nos níveis superiores
        hovertemplate='<b>%{label}</b><br>Patrimônio Atual: R$ %{value:,.0f}<br>Porcentagem: %{percentRoot:.1%}',
        maxdepth=2,  # Limita o número de níveis visíveis (0 = raiz, 1 = 1º nível, 2 = até o 2º nível)
        insidetextorientation="radial",  # Orientação do texto dentro das fatias (melhor visual em círculos)
        domain={
        "x": [0.1, 0.9],  # Ocupa de 10% a 90% da largura disponível (horizontal)
        "y": [0.05, 0.875]  # Ocupa de 10% a 90% da altura disponível (vertical)
    }
    )

    return fig

# -------------------------------------------------------------------------------------------------------------------- Gráfico 4
def _criar_grafico_distrib_cm_controleac_df_posicao_acoes(df_posicao_acoes):

    df = df_posicao_acoes.copy()
    
    # Modificando df:
    # Remover o sufixo ' Holding' da coluna 'Controle Acionário'
    df['Controle Acionário'] = df['Controle Acionário'].str.replace(
        ' Holding',    # String a ser removida (com espaço antes)
        '',           # Substituir por string vazia (remover)
        regex=False   # Remover literalmente, não como regex
    )
    # Remover espaços extras que possam ter ficado
    df['Controle Acionário'] = df['Controle Acionário'].str.strip()

    # Ordenar valores decrescentes para consistência visual
    df = df.sort_values(by='Custo Médio', ascending=False)

    # Criar gráfico Sunburst com hierarquia: Tipo > Ativo
    fig = px.sunburst(
        df,
        path=['Controle Acionário', 'Ticker'],  # Hierarquia: primeiro o Tipo, depois o Ativo
        values='Custo Médio',
        color='Controle Acionário',  # Cores por Tipo (você pode personalizar mais abaixo)
        color_discrete_sequence=["#283044","#bfdbf7"]
    )

    # Atualizar o layout do gráfico
    fig.update_layout(
        plot_bgcolor='#0a0908',     # Fundo da área do gráfico
        paper_bgcolor='#0a0908',    # Fundo geral
        margin={"l": 40, "r": 40, "t": 5, "b": 5},  # Margens internas

        title={
            'text': 'Composição do Custo Médio por Controle Acionário',
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

        # font={
        #     'family': 'Segoe UI',
        #     'color': '#adb5bd',
        #     'size': 12
        # }
    )

    # Exibir valores em formato brasileiro no hover
    fig.update_traces(
        textinfo='label+percent entry',  # 'entry' mostra o rótulo do nó, mesmo nos níveis superiores
        hovertemplate='<b>%{label}</b><br>Custo Médio: R$ %{value:,.0f}<br>Porcentagem: %{percentRoot:.1%}',
        maxdepth=2,  # Limita o número de níveis visíveis (0 = raiz, 1 = 1º nível, 2 = até o 2º nível)
        insidetextorientation="radial",  # Orientação do texto dentro das fatias (melhor visual em círculos)
        domain={
        "x": [0.1, 0.9],  # Ocupa de 10% a 90% da largura disponível (horizontal)
        "y": [0.05, 0.875]  # Ocupa de 10% a 90% da altura disponível (vertical)
    }
    )

    return fig

# -------------------------------------------------------------------------------------------------------------------- Gráfico 5

def _criar_grafico_distrib_pa_controleac_df_posicao_acoes(df_posicao_acoes):

    df = df_posicao_acoes.copy()

    # Modificando df:
    # Remover o sufixo ' Holding' da coluna 'Controle Acionário'
    df['Controle Acionário'] = df['Controle Acionário'].str.replace(
        ' Holding',    # String a ser removida (com espaço antes)
        '',           # Substituir por string vazia (remover)
        regex=False   # Remover literalmente, não como regex
    )
    # Remover espaços extras que possam ter ficado
    df['Controle Acionário'] = df['Controle Acionário'].str.strip()

    # Ordenar valores decrescentes para consistência visual
    df = df.sort_values(by='Patrimônio Atual', ascending=False)

    # Criar gráfico Sunburst com hierarquia: Tipo > Ativo
    fig = px.sunburst(
        df,
        path=['Controle Acionário', 'Ticker'],  # Hierarquia: primeiro o Tipo, depois o Ativo
        values='Patrimônio Atual',
        color='Controle Acionário',  # Cores por Tipo (você pode personalizar mais abaixo)
        color_discrete_sequence=["#283044","#bfdbf7"]
    )

    # Atualizar o layout do gráfico
    fig.update_layout(
        plot_bgcolor='#0a0908',     # Fundo da área do gráfico
        paper_bgcolor='#0a0908',    # Fundo geral
        margin={"l": 40, "r": 40, "t": 5, "b": 5},  # Margens internas

        title={
            'text': 'Composição do Patrimônio Atual por Controle Acionário',
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

        # font={
        #     'family':'Segoe UI',
        #     'color':'#adb5bd',
        #     'size':12
        # }
    )

    # Exibir valores em formato brasileiro no hover
    fig.update_traces(
        textinfo='label+percent entry',  # 'entry' mostra o rótulo do nó, mesmo nos níveis superiores
        hovertemplate='<b>%{label}</b><br>Patrimônio Atual: R$ %{value:,.0f}<br>Porcentagem: %{percentRoot:.1%}',
        maxdepth=2,  # Limita o número de níveis visíveis (0 = raiz, 1 = 1º nível, 2 = até o 2º nível)
        insidetextorientation="radial",  # Orientação do texto dentro das fatias (melhor visual em círculos)
        domain={
        "x": [0.1, 0.9],  # Ocupa de 10% a 90% da largura disponível (horizontal)
        "y": [0.05, 0.875]  # Ocupa de 10% a 90% da altura disponível (vertical)
    }
    )

    return fig

# --------------------------------------------------------------------------------------------------------------------
