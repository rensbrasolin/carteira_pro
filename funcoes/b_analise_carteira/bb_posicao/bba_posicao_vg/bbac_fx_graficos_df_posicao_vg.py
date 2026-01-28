import plotly.graph_objects as go
import plotly.express as px


def _criar_grafico_distrib_cm_tipo_df_posicao(df_posicao):
    # Ordenar valores decrescentes para consistência visual
    df = df_posicao.copy()
    df = df.sort_values(by='Custo Médio', ascending=False)

    # Criar gráfico Sunburst com hierarquia: Tipo > Ativo
    fig = px.sunburst(
        df,
        path=['Tipo', 'Ticker'],  # Hierarquia: primeiro o Tipo, depois o Ativo
        values='Custo Médio',
        color='Tipo',  # Cores por Tipo (você pode personalizar mais abaixo)  ["#022b3a","#1f7a8c","#bfdbf7"]
        color_discrete_sequence=["#00798c","#30638e","#003d5b","#edae49","#d1495b"]
        # ["#e63946", "#ec9a9a", "#f1faee"]
    )

    # Atualizar o layout do gráfico
    fig.update_layout(
        plot_bgcolor='#0a0908',     # Fundo da área do gráfico
        paper_bgcolor='#0a0908',    # Fundo geral
        margin={"l": 40, "r": 40, "t": 5, "b": 5},  # Margens internas

        title={
            'text': 'Composição do Custo Médio por Tipo de Ativo',
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

# -------------------------------------------------------------------------------------------------------------------------------------- 

def _criar_grafico_distrib_pa_tipo_df_posicao(df_posicao):
    # Ordenar valores decrescentes para consistência visual
    df = df_posicao.copy()
    df = df.sort_values(by='Patrimônio Atual', ascending=False)

    # Criar gráfico Sunburst com hierarquia: Tipo > Ativo
    fig = px.sunburst(
        df,
        path=['Tipo', 'Ticker'],  # Hierarquia: primeiro o Tipo, depois o Ativo
        values='Patrimônio Atual',
        color='Tipo',  # Cores por Tipo (você pode personalizar mais abaixo)
        color_discrete_sequence=["#00798c","#30638e","#003d5b","#edae49","#d1495b"]

        # ["#457b9d", "#a8dadc", "#1d3557"]  # Mesmo esquema da pizza
    )

    # Atualizar o layout do gráfico
    fig.update_layout(
        plot_bgcolor='#0a0908',     # Fundo da área do gráfico
        paper_bgcolor='#0a0908',    # Fundo geral
        margin={"l": 40, "r": 40, "t": 5, "b": 5},  # Margens internas

        title={
            'text': 'Composição do Patrimônio Atual por Tipo de Ativo',
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

    #     font={
    #         'family':'Segoe UI',
    #         'color':'#adb5bd',
    #         'size':12
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



# -------------------------------------------------------------------------------------------------------------------------------------- 
def _criar_grafico_rank_variacao_df_posicao(df_posicao):

    df = df_posicao.copy()

    # Excluindo posições zeradas do df, pois para variação % não faz sentido.
    df = df[df['Qtd'] != 0]

    # Ordenar os ativos por Variação %
    df = df.sort_values(by='Variação %', ascending=True)

    # Criar gráfico de barras horizontal com cores por valor
    fig = go.Figure(go.Bar(
        x=df['Variação %']/100,  # Valores no eixo X
        y=df['Ticker'],       # Ativos no eixo Y
        orientation='h',               # Barras horizontais
        # text=df_pos_atual['Variação %'].apply(lambda x: f'{x:.2f}%'),  # Texto formatado em %
        textposition='outside',        # Texto fora da barra
        marker={  # Estilo das barras
            'color': df['Variação %'],  # Cor com base no valor
            'colorscale': 'Burg',  # Escala de cores divergente PuBu
            'line': {'width': 0}  # Remove contorno
        }
    ))

    # Layout no estilo escuro com tipografia clara
    fig.update_layout(
        plot_bgcolor='#0a0908',  # Cor de fundo do gráfico
        paper_bgcolor='#0a0908',  # Cor de fundo do papel
        # font={
        #     'family': 'Segoe UI',  # Fonte consistente
        #     'size': 12,
        #     'color': '#adb5bd'  # Cor do texto clara
        # },
        margin={'l': 60, 'r': 40, 't': 60, 'b': 40},  # Margens internas

        title={  # Título centralizado com estilo
            'text': 'Ranking de Ativos pela Variação de Preço',
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

        xaxis_title='',  # Eixos sem título
        yaxis_title='',
        showlegend=False,  # Sem legenda

        yaxis={  # Estilo do eixo Y (Ativos)
            'showgrid': True,
            'gridcolor': 'rgba(200, 200, 200, 0.075)',  # Linhas discretas
            'gridwidth': 0.5,
            # "tickfont": {  # Cor dos rótulos no eixo X
            #     "color": "#adb5bd",
            #     "size": 10,
            # },
        },

        xaxis={  # Estilo do eixo X (valores %)
            'zeroline': True,
            'zerolinecolor': 'rgba(255, 255, 255, 0.15)',  # Linha no zero
            'showgrid': False,
            'tickformat': '.0%',
            # "tickfont": {  # Cor dos rótulos no eixo X
            #     "color": "#adb5bd",
            #     "size": 10,
            # },
        }
    )

    return fig


# --------------------------------------------------------------------------------------------------------------------------------------
def _criar_grafico_rank_tir_df_posicao(df_posicao):

    df = df_posicao.copy()

    # Ordenar os ativos por Variação %
    df = df.sort_values(by='TIR', ascending=True)

    # Criar gráfico de barras horizontal com cores por valor
    fig = go.Figure(go.Bar(
        x=df['TIR']/100,  # Valores no eixo X
        y=df['Ticker'],       # Ativos no eixo Y
        orientation='h',               # Barras horizontais
        # text=df_pos_atual['TIR %'].apply(lambda x: f'{x:.2f}%'),  # Texto formatado em %
        textposition='outside',        # Texto fora da barra
        marker={  # Estilo das barras
            'color': df['TIR'],  # Cor com base no valor
            'colorscale': 'deep',  # Escala de cores divergente PuRd
            'line': {'width': 0}  # Remove contorno
        }
    ))

    # Layout no estilo escuro com tipografia clara
    fig.update_layout(
        plot_bgcolor='#0a0908',  # Cor de fundo do gráfico
        paper_bgcolor='#0a0908',  # Cor de fundo do papel
        # font={
        #     'family': 'Segoe UI',  # Fonte consistente
        #     'size': 12,
        #     'color': '#adb5bd'  # Cor do texto clara
        # },
        margin={'l': 60, 'r': 40, 't': 60, 'b': 40},  # Margens internas

        title={  # Título centralizado com estilo
            'text': 'Ranking de Ativos pela Taxa Interna de Retorno (a.a.)',
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

        xaxis_title='',  # Eixos sem título
        yaxis_title='',
        showlegend=False,  # Sem legenda

        yaxis={  # Estilo do eixo Y (Ativos)
            'showgrid': True,
            'gridcolor': 'rgba(200, 200, 200, 0.075)',  # Linhas discretas
            'gridwidth': 0.5,
            # "tickfont": {  # Cor dos rótulos no eixo X
            #     "color": "#adb5bd",
            #     "size": 10,
            # },
        },

        xaxis={  # Estilo do eixo X (valores %)
            'zeroline': True,
            'zerolinecolor': 'rgba(255, 255, 255, 0.15)',  # Linha no zero
            'showgrid': False,
            'tickformat': '.0%',
            # "tickfont": {  # Cor dos rótulos no eixo X
            #     "color": "#adb5bd",
            #     "size": 10,
            # },
        }
    )

    return fig