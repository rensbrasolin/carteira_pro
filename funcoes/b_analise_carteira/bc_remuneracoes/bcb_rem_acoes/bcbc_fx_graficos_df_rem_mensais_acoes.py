import plotly.graph_objects as go
import plotly.express as px

from funcoes.b_analise_carteira.bc_remuneracoes.bca_rem_vg.bcac_fx_graficos_df_rem_mensais_vg import _desmembrar_df_rem_mensais


# -------------------------------------------------------------------------------------------------------------------------------------- Fxs auxiliares
# _______________________________________________________________________________________________ Fx 1
# Diferente de Posições, em Remunerações não vou trazer dados categóricos para o df_rem_mensais_...
# pois não faz muto sentido, já que é um df multi-índice com muitas colunas. 
# Vou trazer dados categóricos apenas para as fxs de gráfico, que usarão dfs mono-índice. 
# Mas não vou trazer de fora, como quando criei os dfs_posicao por tipo de ativo. Aqui em
# Remunerações vou trazer os dados categóricos do df_posicao respectivo.

def _trazer_cols_df_posicao_acoes(df_principal, df_posicao_acoes):

    # Trazendo dados para o df principal
    df_principal = df_principal.merge(
        df_posicao_acoes[['Ticker', 'Setor', 'Controle Acionário']],
        left_on='Ticker',
        right_on='Ticker',
        how='left'
    )

    return df_principal


# -------------------------------------------------------------------------------------------------------------------------------------- Gráficos
# _______________________________________________________________________________________________ Gráfico 1
# Recebe o df_posicao_acoes para trazer cols categóricas
def _criar_grafico_rem_mensais_total_acoes_por_setor(df_rem_mensais_acoes, df_posicao_acoes): # g1

    # Obtendo o df que preciso
    _, df_rem_mensais_total_acoes, _ = _desmembrar_df_rem_mensais(df_rem_mensais=df_rem_mensais_acoes)

    # Trazendo cols categóricas
    df_rem_mensais_total_acoes = _trazer_cols_df_posicao_acoes(df_principal=df_rem_mensais_total_acoes, df_posicao_acoes=df_posicao_acoes)

    # Identificar dinamicamente as colunas de meses
    colunas_meses = [col for col in df_rem_mensais_total_acoes.columns if col[:4].isdigit() and col[4] == "-"]

    df_rem_mensais_total_acoes_por_setor = df_rem_mensais_total_acoes.groupby('Setor')[colunas_meses].sum().reset_index()

    # Calcular os totais por mês
    totais_por_mes = df_rem_mensais_total_acoes_por_setor[colunas_meses].sum()

    # Obter a paleta de cores
    cores = px.colors.qualitative.Prism #Bold
    setores = df_rem_mensais_total_acoes_por_setor['Setor'].unique()

    # Criar um mapa de cores fixas para cada ativo
    cor_por_setor = {setor: cores[i % len(cores)] for i, setor in enumerate(setores)}

    # Criar a figura
    fig = go.Figure()

    # Reorganizar os valores para que os maiores fiquem na base
    valores_por_setor = {setor: df_rem_mensais_total_acoes_por_setor.loc[
        df_rem_mensais_total_acoes_por_setor['Setor'] == setor, colunas_meses].values.flatten() for setor in setores}

    for mes_idx, mes in enumerate(colunas_meses):
        # Obter valores do mês específico para todos os ativos
        valores_mes = [(setor, valores[mes_idx]) for setor, valores in valores_por_setor.items()]
        # Ordenar em ordem decrescente (maiores na base)
        valores_mes_ordenados = sorted(valores_mes, key=lambda x: x[1], reverse=True)

        # Adicionar ao gráfico na ordem decrescente
        for setor, valor in valores_mes_ordenados:
            fig.add_trace(go.Bar(
                x=[mes],
                y=[valor],
                name=setor,
                # text=f"{valor:.2f}" if valor > 0 else "",
                # texttemplate='%{text}',
                # textposition='inside',
                marker_color=cor_por_setor[setor],
                marker_line_width=0, # borda nas barras
                showlegend=(mes_idx == 0)
            ))

    # Adicionar os valores totais acima das barras
    fig.add_trace(go.Scatter(
        x=colunas_meses,
        y=totais_por_mes,
        mode='text',
        text=totais_por_mes.apply(
            lambda x: f"<span style='color:white; font-size:12px'>{x:.0f}</span>"),  # HTML plotly
        textposition='top center',
        showlegend=False
    ))

    # Configurar o layout do gráfico
    fig.update_layout(
        plot_bgcolor='#0a0908',     # Fundo da área do gráfico
        paper_bgcolor='#0a0908',    # Fundo geral

        margin={"l": 40, "r": 40, "t": 70, "b": 40},  # Margens internas

        title={
            'text': 'Remuneração Mensal por Setor',
            'x': 0.5,
            'y': 0.95,
            'xanchor': 'center',
            'yanchor': 'top',
            # "font": {  # Cor e estilo do título
            #     "color": "#adb5bd",
            #     "size": 16,
            #     "family": "Segoe UI"
            # }
        },
        xaxis_title="",
        yaxis_title="",
        barmode= "stack",
        # template="plotly_white",
        xaxis=dict(
            type="category",
            tickangle=-45,
            # Definir o intervalo inicial (últimos 24 meses). Usado -/+0.5 para barras não ficarem pela metade.
            range=[max(0, len(colunas_meses)-24) - 0.5, len(colunas_meses)-1 + 0.5] if len(colunas_meses) > 24 else None,
            # Configurar para permitir arrastar e zoom
            fixedrange=False,  # Permite zoom e pan
        ),
        yaxis=dict(tickformat=".2f",
                  tickprefix='R$ ',
                  separatethousands=True,
                  ),
        dragmode='pan',  # Permite arrastar
        # Aumentar um pouco o espaçamento entre as barras para melhor visualização
        bargap=0.25,
        bargroupgap=0.02,
        legend=dict(
            orientation="h",
            yanchor='bottom',
            y=-0.3,
            xanchor="center",
            x=0.45
        ),
    )

    return fig


# _______________________________________________________________________________________________ Gráfico 2
# Reaproveitará o gráfico de VG

# _______________________________________________________________________________________________ Gráfico 3
# Reaproveitará o gráfico de VG

# _______________________________________________________________________________________________ Gráfico 4
# Reaproveitará o gráfico de VG