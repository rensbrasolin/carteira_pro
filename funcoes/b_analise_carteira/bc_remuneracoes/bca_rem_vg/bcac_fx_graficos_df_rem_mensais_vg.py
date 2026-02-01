import pandas as pd
import plotly.graph_objects as go
import plotly.express as px

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
def _desmembrar_df_rem_mensais(df_rem_mensais): # Talvez fazer com 'for' depois

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
    # df_rem_mensais_total = _criar_cols_meses_faltantes(df_rem_mensais_total)
    df_rem_mensais_yonc = _criar_cols_meses_faltantes(df_rem_mensais_yonc)


    return df_rem_mensais_unitario, df_rem_mensais_total, df_rem_mensais_yonc

# _______________________________________________________________________________________________ Fx 3
# O df principal (df_rem_mensais) mostra as 3 medidas para cada mês, só que separado por ativo.
# O que preciso agora é do YonC mensal da carteira como um todo. Lembrando que quando calcula
# YonC por ativo, compara a Rem. Recebida daquele ativo com o CM dele. Já no calculo do YonC da
# Carteira, se compara a Rem. Recebida de cada ativo da Carteira com o CM total ds Carteira.

# Será criado no arq render...
# NO CONTEXTO DA CARTEIRA, NÃO É POSSÍVEL DAR MATCH PELA QTDE COMO FEITO NO CONTEXTO SEPARADO POR TICKER, PELO FATO DE QUE
# SE ANALISARMOS O DF_REM VEREMOS QUE ACUMULAR SUAS QTDES SEM SEPARAR POR TICKER, NÃO FAZ SENTIDO POIS ELA NÃO ACOMPANHA NO
# MESMO PASSO DO DF DE COMPRAS/VNDAS. OU SEJA, ACUMULAR A COL 'QTD' DO DF_REM COMO UM TODU NÃO REFLETE AS VERDADEIRAS QTDES
# QUE A CARTEIRA VAI TENDO CONFORME COMPRAS/VENDAS. ENTÃO, O MATCH SERÁ DADO PELA DATA APROXIMADA (merge_asof).
def _criar_df_rem_mensais_yonc_carteira(df_ext_pm_apos_compra, df_ext_remuneracoes):

    # ----------------------------------------------------- A df_ext_cm_acumulado_carteira

    # Chega-se no 'CM Acumulado (Carteira)' somando a col 'CM Acumulado (Ticker)', que
    # foi criada no df_ext_pm_apos_compra. A col 'CM Acumulado (Ticker)' é criada com o
    # df separado por ativo e ordenado por data. Além disso, qdo há venda ele diminui
    # PM*QtdVendida. Então, para se chegar no 'CM Acumulado (Carteira)' basta ordenar o
    # df por data (semseparar por ticker) e somar a col 'CM Acumulado (Ticker)'. Não 
    # consegui entender como a lógica da venda funciona aqui nesse df de forma perfeita,
    # mas funciona. Deve ter a ver com algo que foi no df anterior na col 'CM Acumulado (Ticker)'.

    df_ext_cm_acumulado_carteira = df_ext_pm_apos_compra.copy()

    # Ordenar por data para garantir a cronologia (caso não esteja)
    df_ext_cm_acumulado_carteira = df_ext_cm_acumulado_carteira.sort_values('Data')

    # Dicionário para armazenar o último estado de cada ativo
    ultimo_custo_por_ativo = {}   # Último custo acumulado por ativo

    # Lista para armazenar os resultados de cada linha
    custo_total_carteira_lista = []

    # Iterar sobre cada linha (já ordenada por data)
    for idx, row in df_ext_cm_acumulado_carteira.iterrows():
        ticker = row['Ticker']
        
        # Atualizar os dicionári com os valores atuais desta linha
        ultimo_custo_por_ativo[ticker] = row['CM Acumulado (Ticker)']

        # Custo total da carteira: soma de todos os custos acumulados
        custo_total = sum(ultimo_custo_por_ativo.values())
        
        # Armazenar nos resultados
        custo_total_carteira_lista.append(custo_total)

    # Adicionar a nova coluna ao DataFrame
    df_ext_cm_acumulado_carteira['CM Acumulado (Carteira)'] = custo_total_carteira_lista

    df_ext_cm_acumulado_carteira = df_ext_cm_acumulado_carteira[['Data', 'CM Acumulado (Carteira)']]

    # Datas ainda podem aparecer + de 1 vez, pois aparecem uma vez para cada compra efetuada. Então vou excluir
    # datas duplicadas, mantendo semprea ultima aparição. O que realmenet reflete a ultima atualização do dia.
    df_ext_cm_acumulado_carteira = df_ext_cm_acumulado_carteira.drop_duplicates(subset='Data', keep='last')


    # ----------------------------------------------------- B df_ext_remuneracoes_carteira
    df_ext_remuneracoes_carteira = df_ext_remuneracoes.copy()

    df_ext_remuneracoes_carteira = df_ext_remuneracoes_carteira.drop(
        columns=['Quantidade', 'Tipo de Ativo', 'Entrada/Saída', 'Preço unitário', 'Rem. Unit. Liq.',
                'PM Correspondente', 'CM Acumulado', 'Yield on Cost'])
    
    df_ext_remuneracoes_carteira.rename(columns={
    'Valor da Operação': 'Rem. Total',
    }, inplace=True)
    
    # Ordenar por data para garantir a cronologia (caso não esteja)
    df_ext_remuneracoes_carteira = df_ext_remuneracoes_carteira.sort_values('Data')

    # Agrupar 'Data' e somar 'Rem'
    df_ext_remuneracoes_carteira = df_ext_remuneracoes_carteira.groupby(['Data'])[
        ['Rem. Total']].sum().reset_index()


    # ----------------------------------------------------- C df_rem_mensais_yonc_carteira

    # Fazer o merge: para cada data de remuneração, pega o CM da data mais recente anterior
    df_rem_mensais_yonc_carteira = pd.merge_asof(
        df_ext_remuneracoes_carteira,        # DataFrame da esquerda (remunerações)
        df_ext_cm_acumulado_carteira[['Data', 'CM Acumulado (Carteira)']],  # Colunas da direita
        on='Data',                           # Coluna para fazer o match
        direction='backward'                 # Pega a data anterior mais próxima
    )

    df_rem_mensais_yonc_carteira['YonC Carteira'] = df_rem_mensais_yonc_carteira[
        'Rem. Total'] / df_rem_mensais_yonc_carteira['CM Acumulado (Carteira)'] *100
    
    # Criar coluna ano-mes
    df_rem_mensais_yonc_carteira['Ano-Mês'] = df_rem_mensais_yonc_carteira['Data'].dt.to_period('M').astype(str)

    # Agrupar 'Data' e somar 'YonC Carteira'
    df_rem_mensais_yonc_carteira = df_rem_mensais_yonc_carteira.groupby(['Ano-Mês'])[
        ['YonC Carteira']].sum().reset_index()
    
    # Df já está pronto de forma vertical, mas vou pivotar para ficar horizontal como os outros,
    # para poder aplicar fx _criar_cols_meses_faltantes
    df_rem_mensais_yonc_carteira = df_rem_mensais_yonc_carteira.set_index('Ano-Mês')['YonC Carteira'].to_frame().T
    df_rem_mensais_yonc_carteira = df_rem_mensais_yonc_carteira.reset_index(drop=True)

    df_rem_mensais_yonc_carteira =_criar_cols_meses_faltantes(df_meses_faltantes=df_rem_mensais_yonc_carteira)
    

    return df_rem_mensais_yonc_carteira



def _criar_df_rem_mensais_yonc_carteira_ANTIGA(df_ext_remuneracoes):
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
    # Se agrupasse por Tipo e Mes como no projeto antigo, cada mes poderia aparecer 1x para cada tipo de ativo.
    # Mas agora, como não uso filtros, vou agrupar geral, de modo que no df apareça o mês uma única vez.
    # Quando for criar esse df para cada tipo de ativo, o df origem (df_ext_remuneracoes) já estará filtrado e poderá ser usado normalmente.
    df_rem_mensais_yonc_carteira = df_rem_mensais_yonc_carteira.groupby(['Ano-Mês'])[
        ['Remunerações', 'CM Acumulado']].sum().reset_index() #  Nesse 2o agrupamento faz sentido somar as 2 cols.
    

    df_rem_mensais_yonc_carteira['YonC'] = df_rem_mensais_yonc_carteira[
        'Remunerações'] / df_rem_mensais_yonc_carteira['CM Acumulado'] * 100
    
    df_rem_mensais_yonc_carteira = df_rem_mensais_yonc_carteira[['Ano-Mês', 'YonC']]

    # Df já está pronto de forma vertical, mas vou pivotar para ficar horizontal como os outros,
    # para poder aplicar fx _criar_cols_meses_faltantes
    df_rem_mensais_yonc_carteira = df_rem_mensais_yonc_carteira.set_index('Ano-Mês')['YonC'].to_frame().T
    df_rem_mensais_yonc_carteira = df_rem_mensais_yonc_carteira.reset_index(drop=True)

    df_rem_mensais_yonc_carteira =_criar_cols_meses_faltantes(df_meses_faltantes=df_rem_mensais_yonc_carteira)

    return df_rem_mensais_yonc_carteira




# -------------------------------------------------------------------------------------------------------------------------------------- Gráficos
# _______________________________________________________________________________________________ Gráfico 1
def _calc_media_mensal_ult_12_meses_df_rem_mensais_total(df_rem_mensais):
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


def _calc_soma_ult_12_meses_df_rem_mensais_total(df_rem_mensais):
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


def _calc_soma_df_rem_mensais_total(df_rem_mensais):
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

        margin={"l": 40, "r": 40, "t": 70, "b": 40},  # Margens internas

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
def _calc_media_mensal_df_rem_mensais_yonc_carteira(df_rem_mensais_yonc_carteira):
    """
    Calcula a média do YonC para todo o período.
    """

    # Converter para numérico
    valores = pd.to_numeric(df_rem_mensais_yonc_carteira.iloc[0], errors='coerce')
    
    # Calcular média
    return valores.mean()


def _calc_media_mensal_ult_12_meses_df_rem_mensais_yonc_carteira(df_rem_mensais_yonc_carteira):
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


def _calc_soma_mensal_ult_12_meses_df_rem_mensais_yonc_carteira(df_rem_mensais_yonc_carteira):
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
    colunas_meses = df_rem_mensais_yonc_carteira.columns.tolist()

    # Converter valores para numérico e dividir por 100
    valores = pd.to_numeric(df_rem_mensais_yonc_carteira.iloc[0], errors='coerce').values / 100

    cor_linha = px.colors.qualitative.Prism[8]


    fig.add_trace(go.Scatter( # Carteira
        x=colunas_meses,
        y=valores,
        mode='lines+markers+text',
        name='Yield on Cost da Carteira',
        # text=[f"{v:.2%}" for v in (valores)],
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
        margin={"l": 80, "r": 40, "t": 75, "b": 40},  # Margens internas

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
            categoryarray=colunas_meses,
            tickangle=-45,
            # Definir o intervalo inicial (últimos 24 meses). Usado -/+0.5 para barras não ficarem pela metade.
            range=[max(0, len(colunas_meses)-36) - 0.5, len(colunas_meses)-1 + 0.5] if len(colunas_meses) > 36 else None,
            # Configurar para permitir arrastar e zoom
            fixedrange=False,  # Permite zoom e pan
        ),
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
        ),
        dragmode='pan',  # Permite arrastar
    )

    return fig


# _______________________________________________________________________________________________ Gráfico 3
# Será criado aqui pq pode ser reaproveitado. Mas não será usado aqui em VG.
def _criar_grafico_rem_mensais_yonc_por_ticker(df_rem_mensais): #g3

    # Obtendo o df que preciso
    _, _, df_rem_mensais_yonc = _desmembrar_df_rem_mensais(df_rem_mensais)

    # Identificar dinamicamente as colunas de meses
    colunas_meses = [col for col in df_rem_mensais_yonc.columns if col[:4].isdigit() and col[4] == "-"]

    # Usar uma paleta de cores pronta do Plotly Express
    paleta_cores = px.colors.qualitative.Dark24  # Paleta tem que ter muita cores

    # Garantir que há cores suficientes para todos os ativos
    cores = paleta_cores * (len(df_rem_mensais_yonc) // len(paleta_cores) + 1)

    # Criar a figura
    fig = go.Figure()

    # Adicionar uma linha para cada ativo
    for i, ticker in enumerate(df_rem_mensais_yonc['Ticker']):
        valores_yonc = df_rem_mensais_yonc.loc[df_rem_mensais_yonc['Ticker'] == ticker, colunas_meses].values.flatten()

        # 🔥 Regra para iniciar com o 1o ticker visível, outros ocultos.
        visible = True if i == 0 else 'legendonly'

        fig.add_trace(go.Scatter(
            x=colunas_meses,  # Eixo X: meses
            y=valores_yonc/100,  # /100 para que valores do eixo x apareçam corretos
            mode='lines+markers',  # Linha com pontos
            name=ticker,  # Nome do ativo para a legenda
            line=dict(color=cores[i], width=0.8),  # Cor da linha, espessura.
            marker={'size':3.7},
            visible=visible,
        ))

    # Configurar o layout do gráfico
    fig.update_layout(
        plot_bgcolor='#0a0908',     # Fundo da área do gráfico
        paper_bgcolor='#0a0908',    # Fundo geral
        margin={"l": 80, "r": 40, "t": 75, "b": 40},  # Margens internas

        title={
            'text': 'Yield on Cost Mensal por Ativo',  # Título
            'x': 0.5,  # Centralizado
            'y': 0.9,
            'xanchor': 'center',
            'yanchor': 'top',
        },
        xaxis_title="Meses",
        # yaxis_title="Dividend Yield",
        legend_title="Ativos",
        template="plotly_white",
        xaxis=dict(
            title="",
            type="category",  # Tratar os meses como categorias
            categoryorder="array",  # Ordenar pela ordem em que aparecem
            categoryarray=colunas_meses,  # Definir a ordem
            tickangle=-45,  # Inclinar os rótulos para melhor visualização
            # Definir o intervalo inicial (últimos 24 meses). Usado -/+0.5 para barras das extremidades não ficarem pela metade.
            range=[max(0, len(colunas_meses)-36) - 0.5, len(colunas_meses)-1 + 0.5] if len(colunas_meses) > 36 else None,
            # Configurar para permitir arrastar e zoom
            fixedrange=False,  # Permite zoom e pan
        ),
        yaxis=dict(
            tickformat=".2%"  # Formatar como porcentagem com duas casas decimais
        ),
        dragmode='pan',  # Permite arrastar

    )

    return fig


# _______________________________________________________________________________________________ Gráfico 4
# Será criado aqui pq pode ser reaproveitado. Mas não será usado aqui em VG.
def _criar_grafico_rem_mensais_yonc_por_ticker_soma_ult_12_meses(df_rem_mensais):
    """
    Cria gráfico de barras horizontais com ranking por ticker
    mostrando a soma do YonC dos últimos 12 meses.
    """
    
    # Obtendo o df que preciso
    _, _, df_rem_mensais_yonc = _desmembrar_df_rem_mensais(df_rem_mensais)


    # Identificar dinamicamente as colunas de meses
    colunas_meses = [col for col in df_rem_mensais_yonc.columns 
                     if col[:4].isdigit() and col[4] == "-"]
    
    # Ordenar as colunas de meses (do mais antigo para o mais recente)
    colunas_meses_ordenadas = sorted(colunas_meses)
    
    # Pegar apenas os últimos 12 meses (ou todos se tiver menos)
    ultimos_12_meses = colunas_meses_ordenadas[-12:] if len(colunas_meses_ordenadas) >= 12 else colunas_meses_ordenadas
    
    # Calcular a soma dos últimos 12 meses para cada ticker
    # axis=1 soma as linhas horizontalmente (por ticker)
    df_rem_mensais_yonc['Soma_Ult_12_Meses'] = df_rem_mensais_yonc[ultimos_12_meses].sum(axis=1)
    
    # Ordenar por soma (maior para menor) para o ranking
    df_ranking = df_rem_mensais_yonc.sort_values('Soma_Ult_12_Meses', ascending=True)

    # >>> ADICIONE AQUI <<<
    # Filtrar apenas tickers com valor maior que 0 nos últimos 12 meses
    df_ranking = df_ranking[df_ranking['Soma_Ult_12_Meses'] > 0]
    
    # Usar paleta sequencial do Plotly (escolhi 'Viridis' - pode trocar)
    # Outras opções: 'Plasma', 'Magma', 'Inferno', 'Cividis', 'Blues', 'Greens', etc.
    cor_sequencial = px.colors.sequential.Tealgrn
    
    # Criar figura
    fig = go.Figure()
    
    # Adicionar barras horizontais
    fig.add_trace(go.Bar(
        y=df_ranking['Ticker'],                   # Tickers no eixo Y
        x=df_ranking['Soma_Ult_12_Meses'] / 100,  # Soma convertida para decimal (/100)
        orientation='h',                           # Barras horizontais
        marker=dict(
            color=df_ranking['Soma_Ult_12_Meses'],  # Cor baseada no valor (gradiente)
            colorscale=cor_sequencial,              # Escala de cores sequencial
            showscale=False,                        # Não mostrar escala de cores ao lado
            line=dict(width=0)                      # Sem borda nas barras
        ),
        text=df_ranking['Soma_Ult_12_Meses'].round(2).astype(str) + '%',  # Texto dentro da barra
        textposition='inside',                     # Texto dentro da barra  
    ))
    
    # Configurar layout
    fig.update_layout(
        plot_bgcolor='#0a0908',     # Fundo da área do gráfico
        paper_bgcolor='#0a0908',    # Fundo geral
        margin={"l": 80, "r": 40, "t": 75, "b": 40},  # Margens internas
        title={
            'text': 'Yield on Cost (últ. 12 Meses)',
            'x': 0.5,
            'y': 0.95,
            'xanchor': 'center',
            'yanchor': 'top',
            'font': dict(size=16)
        },
        xaxis_title="",
        yaxis_title="",
        template="plotly_white",
        height=500 + len(df_ranking) * 25,  # Altura dinâmica baseada no número de tickers
        showlegend=False,                    # Não precisa de legenda
        xaxis=dict(
            tickformat=".2%",                # Formato percentual com 2 casas
            # title="Soma YonC (%)",
            # gridcolor='lightgray',
            gridwidth=0.5,
            showgrid=True,  # Força grade vertical          
        ),
        yaxis=dict(
            categoryorder='total ascending',  # Ordenar pelo valor (já ordenamos, mas mantém)
            autorange=True,                   # Ordem automática (do maior para menor na vertical)
            # tickfont=dict(size=11)
        ),
        bargap=0.15,                         # Espaço entre barras
    )
    
    return fig