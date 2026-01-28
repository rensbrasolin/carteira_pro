import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
import numpy as np

# -------------------------------------------------------------------------------------------------------------------------------------- Fxs auxiliares
# _______________________________________________________________________________________________ Fx 1
# Fx aux, será usada para os 3 dfs criados na fx _desmembrar_df_rem_mensais e também no df_rem_mensais_yonc_carteira,
# para criar colunas zeradas para os meses faltantes.
def _criar_cols_meses_faltantes(df_meses_faltantes):
    # Identificar as colunas de meses (formato YYYY-MM)
    meses_existentes = [col for col in df_meses_faltantes.columns 
                        if isinstance(col, str) and len(col) == 7 
                        and col[4] == '-' and col[:4].isdigit() and col[5:].isdigit()]

    # Converter para objetos de data para manipulação
    datas = []
    for mes in meses_existentes:
        ano, mes_num = map(int, mes.split('-'))
        datas.append((ano, mes_num, mes))

    # Ordenar e encontrar intervalo
    datas.sort()
    primeiro_ano, primeiro_mes, primeiro_str = datas[0]
    ultimo_ano, ultimo_mes, ultimo_str = datas[-1]

    # Gerar todos os meses do intervalo
    todos_meses = []
    ano_atual, mes_atual = primeiro_ano, primeiro_mes

    while (ano_atual < ultimo_ano) or (ano_atual == ultimo_ano and mes_atual <= ultimo_mes):
        mes_str = f"{ano_atual:04d}-{mes_atual:02d}"
        todos_meses.append(mes_str)
        
        # Avançar um mês
        mes_atual += 1
        if mes_atual > 12:
            mes_atual = 1
            ano_atual += 1

    # Identificar meses faltantes
    meses_faltantes = [mes for mes in todos_meses if mes not in meses_existentes]

    # Adicionar colunas zeradas para meses faltantes
    for mes in meses_faltantes:
        df_meses_faltantes[mes] = 0.0

    # Reordenar colunas: 'Tipo', 'Ticker' seguidos dos meses em ordem
    colunas_nao_meses = [col for col in df_meses_faltantes.columns if col not in todos_meses]
    nova_ordem = colunas_nao_meses + sorted([mes for mes in todos_meses if mes in df_meses_faltantes.columns])
    df_meses_faltantes = df_meses_faltantes[nova_ordem]

    return df_meses_faltantes

# _______________________________________________________________________________________________ Fx 2
# Será usada dentro de cada fx de gráfico para facilitar a criação, já que o df rem é multi índice.
def _desmembrar_df_rem_mensais(df_rem_mensais): # gráfico zero, talvez fazer com 'for' depois

    # Primeiro, extraia as colunas fixas (nível 0: vazio, nível 1: "Ativo" e "Tipo de Ativo")
    df_fix = df_rem_mensais.loc[:, [("", "Tipo"), ("", "Ticker")]].copy()
    df_fix.columns = ["Tipo", "Ticker"]

    # Agora, para cada tipo de dado, use xs() com drop_level=True para remover o nível de "rótulo"
    df_rem_mensais_unitario = df_rem_mensais.xs("Unitário", axis=1, level=1, drop_level=True)
    df_rem_mensais_total    = df_rem_mensais.xs("Total", axis=1, level=1, drop_level=True)
    df_rem_mensais_yonc     = df_rem_mensais.xs("YonC", axis=1, level=1, drop_level=True)

    # Por fim, concatene as colunas fixas com os dados extraídos para cada DataFrame
    df_rem_mensais_unitario = pd.concat([df_fix, df_rem_mensais_unitario], axis=1)
    df_rem_mensais_total    = pd.concat([df_fix, df_rem_mensais_total], axis=1)
    df_rem_mensais_yonc     = pd.concat([df_fix, df_rem_mensais_yonc], axis=1)

    # Ordenar os meses em ordem crescente (ignorando as 2 colunas fixas)
    df_rem_mensais_unitario = pd.concat([df_fix, df_rem_mensais_unitario.iloc[:, 2:].reindex(sorted(df_rem_mensais_unitario.columns[2:]), axis=1)], axis=1)
    df_rem_mensais_total    = pd.concat([df_fix, df_rem_mensais_total.iloc[:, 2:].reindex(sorted(df_rem_mensais_total.columns[2:]), axis=1)], axis=1)
    df_rem_mensais_yonc     = pd.concat([df_fix, df_rem_mensais_yonc.iloc[:, 2:].reindex(sorted(df_rem_mensais_yonc.columns[2:]), axis=1)], axis=1)

    # Preencher valores NaN com 0 (ou outro valor de sua preferência)
    df_rem_mensais_unitario.fillna(0, inplace=True)
    df_rem_mensais_total.fillna(0, inplace=True)
    df_rem_mensais_yonc.fillna(0, inplace=True)

    # Aplica fx aux para criar cols zeradas p/ os meses faltantes
    df_rem_mensais_unitario = _criar_cols_meses_faltantes(df_rem_mensais_unitario)
    df_rem_mensais_total = _criar_cols_meses_faltantes(df_rem_mensais_total)
    df_rem_mensais_yonc = _criar_cols_meses_faltantes(df_rem_mensais_yonc)


    return df_rem_mensais_unitario, df_rem_mensais_total, df_rem_mensais_yonc

# _______________________________________________________________________________________________ Fx 3
# O df principal (df_rem_mensais) mostra as 3 medidas para cada mês, só que separado por ativo.
# O que preciso agora é do YonC mensal da carteira como um todo. Então vou eliminar categorias e
# manter apenas uma col de mês e outra c/ o YonC.
# Será criado no arq render...
def _criar_df_rem_mensais_yonc_carteira(df_ext_remuneracoes):
    """
    Parte do df_ext_remuneracoes e o agrupa para obter 'Remunerações' e 'CM Acumulado'
    referente a cada mês. Em seguida, cria a col YonC mensal da carteira.
    """

    df_rem_mensais_yonc_carteira = df_ext_remuneracoes.copy()

    df_rem_mensais_yonc_carteira.rename(columns={'Valor da Operação': 'Remunerações'}, inplace=True)

    # Criar coluna ano-mes
    df_rem_mensais_yonc_carteira['Ano-Mês'] = df_rem_mensais_yonc_carteira['Data'].dt.to_period('M').astype(str)

    # 1a camada de agrupamento: Custo médio aparece se repetindo a cada remuneração dentro do mesmo mês, então devo não somar.
    # Só precisava repetí-lo, então média resolveu.
    df_rem_mensais_yonc_carteira = df_rem_mensais_yonc_carteira.groupby(['Ticker', 'Tipo de Ativo', 'Ano-Mês'],
                                                                    as_index=False).agg({
        'Remunerações': 'sum',
        'CM Acumulado': 'mean'
    })

    # 2a camada: Agora já tenho tanto o 'total recebido de rem' quanto o 'CM naquele momento'.
    # O df até aqui, ainda tem uma linha de Mes para cada ativo, mas como quero o total da carteira, vou eliminar todas colunas de categoria.
    # Se agrupasse por Tipo e Mes como no projeto antigo, cda mes poderia aparecer 1x para cada tipo de ativo.
    # Mas agora, como não uso filtros, vou agrupar geral, de modo que no dfapareça o mês uma única vez.
    # Quando for criar esse df para cada tipo de ativo, o df origem (df_ext_remuneracoes) já estará filtrado e poderá serr usado normalmente.
    df_rem_mensais_yonc_carteira = df_rem_mensais_yonc_carteira.groupby(['Ano-Mês'])[
        ['Remunerações', 'CM Acumulado']].sum().reset_index() #  Nesse 2o agrupamento faz sentido somar as 2 cols.
    

    df_rem_mensais_yonc_carteira['YonC'] = df_rem_mensais_yonc_carteira[
        'Remunerações'] / df_rem_mensais_yonc_carteira['CM Acumulado'] * 100
    
    df_rem_mensais_yonc_carteira = df_rem_mensais_yonc_carteira[['Ano-Mês', 'YonC']]

    # Df já está pronto de forma  vertical, mas vou pivotar para ficar horizontal como os outros,
    # para poder aplicar fx _criar_cols_meses_faltantes
    df_rem_mensais_yonc_carteira = df_rem_mensais_yonc_carteira.set_index('Ano-Mês')['YonC'].to_frame().T
    df_rem_mensais_yonc_carteira = df_rem_mensais_yonc_carteira.reset_index(drop=True)

    df_rem_mensais_yonc_carteira =_criar_cols_meses_faltantes(df_meses_faltantes=df_rem_mensais_yonc_carteira)

    return df_rem_mensais_yonc_carteira




# -------------------------------------------------------------------------------------------------------------------------------------- Gráficos
# _______________________________________________________________________________________________ Gráfico 1
def _calc_media_mensal_ult_12_meses_df_rem_mensais_total(df_rem_mensais): # ind1
    """
    Calcula média mensal dos últimos 12 meses.
    DataFrame já deve ter todos os meses preenchidos.
    """
    
    # Obtendo o df que preciso
    _, df_rem_mensais_total, _ = _desmembrar_df_rem_mensais(df_rem_mensais=df_rem_mensais)

    # Filtrar e ordenar colunas de meses
    meses = sorted([col for col in df_rem_mensais_total.columns 
                    if isinstance(col, str) and len(col)==7 and col[4]=='-'])
    
    # Pegar últimos 12 meses
    meses_recentes = meses[-12:] if len(meses) >= 12 else meses
    
    # Calcular média
    # Primeiro somamos (cols) os valores de cada ativo por mês, depois somamos (df) todos os ativos
    return df_rem_mensais_total[meses_recentes].sum().sum() / 12.0


def _calc_soma_ult_12_meses_df_rem_mensais_total(df_rem_mensais): # ind2
    """
    Calcula soma dos últimos 12 meses.
    DataFrame já deve ter todos os meses preenchidos.
    """
    
    # Obtendo o df que preciso
    _, df_rem_mensais_total, _ = _desmembrar_df_rem_mensais(df_rem_mensais=df_rem_mensais)

    # Filtrar e ordenar colunas de meses
    meses = sorted([col for col in df_rem_mensais_total.columns 
                    if isinstance(col, str) and len(col)==7 and col[4]=='-'])
    
    # Pegar últimos 12 meses
    meses_recentes = meses[-12:] if len(meses) >= 12 else meses
    
    # Calcular soma
    # Primeiro somamos (cols) os valores de cada ativo por mês, depois somamos (df) todos os ativos
    return df_rem_mensais_total[meses_recentes].sum().sum()


def _calc_soma_df_rem_mensais_total(df_rem_mensais): # ind3
    """
    Calcula soma total do df_rem_mensais_total.
    DataFrame já deve ter todos os meses preenchidos.
    """
    
    # Obtendo o df que preciso
    _, df_rem_mensais_total, _ = _desmembrar_df_rem_mensais(df_rem_mensais=df_rem_mensais)

    # Filtrar e ordenar colunas de meses
    meses = sorted([col for col in df_rem_mensais_total.columns 
                    if isinstance(col, str) and len(col)==7 and col[4]=='-'])
    
    # Calcular soma total
    # Primeiro somamos (cols) os valores de cada ativo por mês, depois somamos (df) todos os ativos
    return df_rem_mensais_total[meses].sum().sum()



def _criar_grafico_rem_mensais_total_por_tipo(df_rem_mensais): # g1

    # Obtendo o df que preciso
    _, df_rem_mensais_total, _ = _desmembrar_df_rem_mensais(df_rem_mensais=df_rem_mensais)


    # Identificar dinamicamente as colunas de meses
    colunas_meses = [col for col in df_rem_mensais_total.columns if col[:4].isdigit() and col[4] == "-"]

    df_rem_mensais_total_por_tipo = df_rem_mensais_total.groupby('Tipo')[colunas_meses].sum().reset_index()

    # Calcular os totais por mês
    totais_por_mes = df_rem_mensais_total_por_tipo[colunas_meses].sum()

    # Obter a paleta de cores
    cores = px.colors.qualitative.Prism #Bold
    tipos = df_rem_mensais_total_por_tipo['Tipo'].unique()

    # Criar um mapa de cores fixas para cada ativo
    cor_por_tipo = {tipo: cores[i % len(cores)] for i, tipo in enumerate(tipos)}

    # Criar a figura
    fig = go.Figure()

    # Reorganizar os valores para que os maiores fiquem na base
    valores_por_tipo = {tipo: df_rem_mensais_total_por_tipo.loc[df_rem_mensais_total_por_tipo['Tipo'] == tipo, colunas_meses].values.flatten() for tipo in tipos}

    for mes_idx, mes in enumerate(colunas_meses):
        # Obter valores do mês específico para todos os ativos
        valores_mes = [(tipo, valores[mes_idx]) for tipo, valores in valores_por_tipo.items()]
        # Ordenar em ordem decrescente (maiores na base)
        valores_mes_ordenados = sorted(valores_mes, key=lambda x: x[1], reverse=True)

        # Adicionar ao gráfico na ordem decrescente
        for tipo, valor in valores_mes_ordenados:
            fig.add_trace(go.Bar(
                x=[mes],
                y=[valor],
                name=tipo,
                # text=f"{valor:.2f}" if valor > 0 else "",
                # texttemplate='%{text}',
                # textposition='inside',
                marker_color=cor_por_tipo[tipo],
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

        margin={"l": 40, "r": 40, "t": 40, "b": 40},  # Margens internas

        title={
            'text': 'Remuneração Mensal por Tipo de Ativo',
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
def _calc_media_mensal_df_rem_mensais_yonc_carteira(df_rem_mensais_yonc_carteira):# ind1
    """
    Calcula a média do YonC para todo o período.
    """

    # Converter para numérico
    valores = pd.to_numeric(df_rem_mensais_yonc_carteira.iloc[0], errors='coerce')
    
    # Calcular média
    return valores.mean()


def _calc_media_mensal_ult_12_meses_df_rem_mensais_yonc_carteira(df_rem_mensais_yonc_carteira): # ind 2
    """
    Calcula média do YonC dos últimos 12 meses.
    """
    
    # Filtrar e ordenar colunas de meses
    meses = sorted([col for col in df_rem_mensais_yonc_carteira.columns 
                    if isinstance(col, str) and len(col)==7 and col[4]=='-'])
    
    # Pegar últimos 12 meses
    meses_recentes = meses[-12:] if len(meses) >= 12 else meses
    
    # Calcular média
    valores = pd.to_numeric(df_rem_mensais_yonc_carteira[meses_recentes].iloc[0], errors='coerce')

    return valores.mean()


def _calc_soma_mensal_ult_12_meses_df_rem_mensais_yonc_carteira(df_rem_mensais_yonc_carteira): # ind 2
    """
    Calcula soma simples do YonC dos últimos 12 meses.
    """
    
    # Filtrar e ordenar colunas de meses
    meses = sorted([col for col in df_rem_mensais_yonc_carteira.columns 
                    if isinstance(col, str) and len(col)==7 and col[4]=='-'])
    
    # Pegar últimos 12 meses
    meses_recentes = meses[-12:] if len(meses) >= 12 else meses
    
    # Calcular soma
    valores = pd.to_numeric(df_rem_mensais_yonc_carteira[meses_recentes].iloc[0], errors='coerce')
    return valores.sum()



def _criar_grafico_rem_mensais_yonc_carteira(df_rem_mensais_yonc_carteira, df_rem_mensais): # g2

    # Criar figura
    fig = go.Figure()

    # --------------------------------------------------------------------------- YonC Carteira
    # Extrair meses (nomes das colunas)
    meses = df_rem_mensais_yonc_carteira.columns.tolist()

    # Converter valores para numérico e dividir por 100
    valores = pd.to_numeric(df_rem_mensais_yonc_carteira.iloc[0], errors='coerce').values / 100

    cor_linha = px.colors.qualitative.Prism[8]


    fig.add_trace(go.Scatter( # Carteira
        x=meses,
        y=valores,
        mode='lines+markers+text',
        name='Yield on Cost da Carteira',
        text=[f"{v:.2%}" for v in (valores)],
        textposition="bottom center",
        line=dict(color=cor_linha, width=1.25),
        marker={'size': 4.2}
    ))

    # # ----------------------------------------------------------------------- Média Mensal de YonC
    # ERRO: EM MESES ZERADOS A LINHA NÃO APARECE. DEIXAR COMENTADO CASO QUEIRA CORRIGIR NO FUTURO
    # # Obtendo o df que preciso
    # _, _, df_rem_mensais_yonc = _desmembrar_df_rem_mensais(df_rem_mensais=df_rem_mensais)

    # # Calcular média mensal de YonC ignorando 0. Usa os meses já criados, pois são os mesmos.
    # # Média caso aplicasse o mesmo valor em todos os ativos.
    # media_mensal_yonc = df_rem_mensais_yonc[meses].replace(0, np.nan).mean().values


    # # Adicionar linha de média mensal de DY com rótulos
    # fig.add_trace(go.Scatter( # Média ativos
    #     x=meses,
    #     y=media_mensal_yonc / 100,  # /100 para ajustar valores para porcentagem
    #     mode='lines+markers+text',  # Adicionar rótulos aos marcadores
    #     name='Média Mensal de Yield on Cost',
    #     # text=[f"{v:.2%}" for v in (media_dy_mensal / 100)],  # Rótulos formatados como %
    #     textposition="top left",  # Posição dos rótulos
    #     line=dict(color='#f72585', width=0.4), #34a0a4
    #     marker={'size': 2}
    # ))

    # ----------------------------------------------------------------------- Configurações 

    # Configurar layout do gráfico
    fig.update_layout(
        plot_bgcolor='#0a0908',     # Fundo da área do gráfico
        paper_bgcolor='#0a0908',    # Fundo geral
        margin={"l": 40, "r": 40, "t": 40, "b": 40},  # Margens internas

        title={
            'text': 'Yield on Cost Mensal da Carteira',  # Título
            'x': 0.5,  # Centralizado
            'y': 0.9,
            'xanchor': 'center',
            'yanchor': 'top',
        },
        xaxis_title="",
        # yaxis_title="Dividend Yield",
        # template="plotly_white",
        xaxis=dict(
            type="category",
            categoryorder="array",
            categoryarray=meses,
            tickangle=-45,
            # Definir o intervalo inicial (últimos 24 meses). Usado -/+0.5 para barras não ficarem pela metade.
            range=[max(0, len(meses)-24) - 0.5, len(meses)-1 + 0.5] if len(meses) > 24 else None,
            # Configurar para permitir arrastar e zoom
            fixedrange=False,  # Permite zoom e pan
        ),
        dragmode='pan',  # Permite arrastar
        yaxis=dict(
            tickformat=".2%"  # Formatar como porcentagem com duas casas decimais
        ),
        # Manter legenda, caso eu volte o pôr a 2a linha.
        legend=dict(
            orientation="h",  # Define a legenda como horizontal
            yanchor="bottom",  # Alinha na parte inferior da legenda
            y=1.05,  # Ajusta a posição verticalmente para cima do gráfico
            xanchor="center",  # Centraliza horizontalmente
            x=0.9  # Define o centro como referência
        )
    )

    return fig