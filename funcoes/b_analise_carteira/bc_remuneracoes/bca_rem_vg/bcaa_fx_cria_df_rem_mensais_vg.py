import numpy as np
import pandas as pd


# Diferente da seção 'Posicão', onde os dfs são inicados pelo df_ext_mov e
# na sequência vão sendo incrementadas colunas no próprio df iniciado, aqui
#  na seção de 'Remunerações' atyé se parte do df_ext_mov, mas é mais direto
#  ao ponto. É um processo c/ 3 dfs: 
    # O df1 auxiliar (PMapósCompra) é criado, depois entregue para a próxima fx 
    # que já calcula o que precisa (YonC) no df2. Por fim, se cria o df final que tem
    #  os mesmos dados do anterior, porém consolidados.

# Df1 (df_ext_pm_apos_compra) serve p/ emprestar sua col 'PM após Compra' para ser usada no df2 (df_ext_remuneracoes).
# Df2 (df_ext_remuneracoes) pega a medida recebida do df1 e a usa para produzir a col 'YonC'. Ele já tem todas as
#  infos necessárias, mas não consolidadas por ticker e mês.
# Df3 (df_rem_mensais) tem os mesmos dados do df2, só que consolidado e c/ multi-índice para cols (Nível1=Meses Nível2=Medidas)
    # Será usado apenas para exibição dos dados, pois cada gráfico o receberá e dele obterá um df mono-índice
    #  com a medida que ele precisar.
# Em vez de criar o df3 multi-índice, poedria criar direto 2 dfs desmembrados. Mas seria ruim para exibir os dados,
    # pois precisaria exibir 2 tabelas.

# ---------------------------------------------------------------------------------------------------------------------------- 1. df_ext_pm_apos_compra
def criar_df_ext_pm_apos_compra(df_ext_mov):
    """
    Df auxiliar. Parte do extrato e mantem só compras e vendas.
    Calcula 'Qtd Acumulada' e 'CM Acumulado' para com eles calcular o PM após cada compra ou venda.
    Vendas não mudam PM, mas mudam a qtde acumulada.
    Será utilizado para dar match pelas cols 'Qtde Acumulada' c/ o df_rem
    """

    df_ext_pm_apos_compra = df_ext_mov.copy()

    # Mantendo apenas linahs de compras e vendas para somas no groupby fazer sentido.
    df_ext_pm_apos_compra = df_ext_pm_apos_compra.loc[df_ext_pm_apos_compra
                                ['Movimentação'] == 'Transferência - Liquidação']
    # Mantendo apenas cols necessárias
    df_ext_pm_apos_compra = df_ext_pm_apos_compra.drop(columns=['Instituição', 'Movimentação', 'Produto'])

    # Ajuda a interpretar o df, mas não é crucial.
    df_ext_pm_apos_compra = df_ext_pm_apos_compra.sort_values('Data')

    # (Atualizada a cada compra/venda)
    df_ext_pm_apos_compra['Qtd Acumulada'] = df_ext_pm_apos_compra.groupby('Ticker')['Quantidade'].cumsum()

    # ----------------------------------------------------------- Criando col custo médio, que é a mais elaborada desse df
    # Agrupa o DataFrame por 'Ativo' para calcular o custo médio separadamente para cada ativo
    for ticker, grupo in df_ext_pm_apos_compra.groupby('Ticker'):
        indices = grupo.index  # Obtém os índices reais do DataFrame original
        custo_medio_acumulado = 0  # Inicializa o custo médio acumulado

        for i, idx in enumerate(indices):
            qtd_acumulada = df_ext_pm_apos_compra.loc[idx, 'Qtd Acumulada']
            entrada_saida = df_ext_pm_apos_compra.loc[idx, 'Entrada/Saída']
            valor_operacao = df_ext_pm_apos_compra.loc[idx, 'Valor da Operação']

            # Primeira linha do ativo: apenas copia o valor da operação
            if i == 0:
                custo_medio_acumulado = valor_operacao

            elif qtd_acumulada == 0:
                custo_medio_acumulado = 0  # Se a quantidade acumulada for 0, o custo médio também deve ser zerado

            elif entrada_saida == 'Credito':
                # Se for uma compra, soma o valor da operação ao custo médio acumulado
                custo_medio_acumulado += valor_operacao

            elif entrada_saida == 'Debito':
                # Se for uma venda, reduz o custo médio proporcionalmente à quantidade vendida.
                # Não reduz o "Preço a venda*qtd vendida" mas sim "PM*qtd vendida"
                qtd_movimentada = abs(df_ext_pm_apos_compra.loc[idx, 'Quantidade']) # Garante que a quantidade seja positiva para o cálculo
                custo_medio_acumulado -= (custo_medio_acumulado / (qtd_acumulada + qtd_movimentada)) * qtd_movimentada

            # Atualiza o DataFrame com o custo médio calculado para a linha atual
            df_ext_pm_apos_compra.loc[idx, 'Custo Médio Acumulado'] = custo_medio_acumulado

    # ----------------------------------------------------------- Fim da col custo médio
    # Criando col 'PM após compra'
    df_ext_pm_apos_compra['PM Após Compra'] = df_ext_pm_apos_compra['Custo Médio Acumulado'] / df_ext_pm_apos_compra['Qtd Acumulada']

    return df_ext_pm_apos_compra

# ---------------------------------------------------------------------------------------------------------------------------- 2. df_ext_remuneracoes

def criar_df_ext_remuneracoes(df_ext_mov, df_ext_pm_apos_compra):

    """
    Também parte do extrato, mas mantém só remunerações.
    Trás do df auxiliar (df_ext_pm_apos_compra) a col PM Após Compra
    para calcular a col Yield on Cost.
    Ao final, terá todas as medidas necessárias para exibição:
    Remunerações (Totais e Unitárias) e YonC.
    Mas df ainda não foi não consolidado um extrato, ou seja,.
    """

    df_ext_remuneracoes = df_ext_mov.copy()

    # Filtrando por movimentações que sejam referentes a remunerações. Se tiver mais, acrescentar.
    df_ext_remuneracoes = df_ext_remuneracoes.loc[(df_ext_remuneracoes['Movimentação'] == 'Rendimento') |
                                                (df_ext_remuneracoes['Movimentação'] == 'Dividendo') |
                                                (df_ext_remuneracoes['Movimentação'] == 'Juros Sobre Capital Próprio')]

    df_ext_remuneracoes = df_ext_remuneracoes.drop(columns=['Instituição', 'Movimentação', 'Produto'])

    # Ajuda a interpretar o df, mas não é crucial.
    df_ext_remuneracoes = df_ext_remuneracoes.sort_values(by='Data')

    # Criando col Preço Liq. Lembrando q col original 'Preço unitário' é valor bruto.
    df_ext_remuneracoes['Rem. Unit. Liq.'] = df_ext_remuneracoes['Valor da Operação'] / df_ext_remuneracoes['Quantidade']

# ----------------------------------------------------------- Criando cols PM e CM que são as mais elaboradas desse df

    # Seria o equivalente a um merge, mas não tão simples pois precisa atender condições.
    # GPT criou lógica:
    # Acho que não usou merge pois para resolver casos de qtd duplicada ao longo do tempo não basta só dar match pela qtd
    # Precisa ser aquela qtde sim, mas se tiver duplicidade, tem que pegar aquela qtd no registro anterior mais próximo.

    # Tenho que buscar no df_pm_apos_compra o PM equivalente a essa qtde de ativos da qual recebi remuneração (cada linha).
    # Mas lá no df_pm_apos_compra a qtd pode se repetir: Tenho qtd x, compro 2, vendo 2, volto a ter x.
    # Se acontecer, terá que puxar a anterior mais recente.

    # Ordena os DataFrames por ativo e data para garantir que a busca funcione corretamente
    df_ext_pm_apos_compra = df_ext_pm_apos_compra.sort_values(by=['Ticker', 'Data'])
    df_ext_remuneracoes = df_ext_remuneracoes.sort_values(by=['Ticker', 'Data'])

    # Criar as colunas 'Preço Médio' e 'Custo Médio' no df_remuneracoes
    df_ext_remuneracoes['PM Correspondente'] = None
    df_ext_remuneracoes['CM Acumulado'] = None

    # Agrupar os DataFrames por ativo
    for ticker, df_rem in df_ext_remuneracoes.groupby('Ticker'):
        df_pm = df_ext_pm_apos_compra[df_ext_pm_apos_compra['Ticker'] == ticker]

        for idx, row in df_rem.iterrows():
            quantidade = row['Quantidade']
            data_remuneracao = row['Data']

            # Filtra os registros do df_pm_apos_compra que possuem a mesma quantidade acumulada
            # e cuja data seja anterior à data do evento em df_remuneracoes
            df_filtrado = df_pm[(df_pm['Qtd Acumulada'] == quantidade) & (df_pm['Data'] < data_remuneracao)]

            if not df_filtrado.empty:
                # Pega o último registro antes da data da remuneração
                preco_medio_correspondente = df_filtrado.iloc[-1]['PM Após Compra']
                custo_medio_acumulado = df_filtrado.iloc[-1]['Custo Médio Acumulado']
            else:
                # Caso não encontre, pode deixar NaN ou outro valor padrão
                preco_medio_correspondente = None
                custo_medio_acumulado = None

            df_ext_remuneracoes.at[idx, 'PM Correspondente'] = preco_medio_correspondente
            df_ext_remuneracoes.at[idx, 'CM Acumulado'] = custo_medio_acumulado

# __________________________________________ Criando col DY %

    df_ext_remuneracoes['Yield on Cost'] = df_ext_remuneracoes['Rem. Unit. Liq.'] / df_ext_remuneracoes['PM Correspondente'] * 100


    return df_ext_remuneracoes

# ------------------------------------------------------------------------------------------------------------------------- 3. df_rem_mensais (Principal)

def criar_df_rem_mensais(df_ext_remuneracoes):
    """
    Df3 (df_rem_mensais) tem os mesmos dados do df2, só que consolidado e
        c/ multi-índice para cols (Nível1=Meses Nível2=Medidas)
    """

    df_rem_mensais = df_ext_remuneracoes.copy()

    # Criar coluna ano-mes
    df_rem_mensais['Ano-Mês'] = df_rem_mensais['Data'].dt.to_period('M').astype(str)

    df_rem_mensais = df_rem_mensais.drop(
        columns=['Data', 'Entrada/Saída', 'Preço unitário', 'Quantidade', 'PM Correspondente'])

    df_rem_mensais.rename(columns={
        'Tipo de Ativo': 'Tipo',
        'Rem. Unit. Liq.': 'Unitário',
        'Valor da Operação': 'Total',
        'Yield on Cost': 'YonC'
    }, inplace=True)

# ------------------- Agrupar cols 'qualitativas' e somar cols 'quantitativas'

    # Resetar para que indices voltem ser colunas e tenham seus titulos de volta.
    df_rem_mensais = df_rem_mensais.groupby(['Ticker', 'Tipo', 'Ano-Mês'])[
        ['Unitário', 'Total', 'YonC']].sum().reset_index()

# ---------------------------------------------------------------- Pivotar df
    # A alternativa para não pivotar, seria criar um df para cada ano-mes. A exibição da tab ficaria parecida, em vez de
    # os meses ficarem colodas num só df, provavelmente ficariam varios df_mes com espaço entre eles.
    # Além do que, meus graficos já estão prontos considerando uma tabela pivotada multi indice.

    # Pivotar o DataFrame para que a col 'Ano-Mês' vire linha (Titulo principal do df)
    df_rem_mensais = df_rem_mensais.pivot(index=['Tipo', 'Ticker'], #'Ticker', 'Tipo'
                                                            columns='Ano-Mês',
                                                            values=['Unitário', 'Total', 'YonC']).reset_index()

    # Coloca os meses no topo, acima dos values.
    df_rem_mensais.columns = df_rem_mensais.columns.swaplevel(0, 1)

    # Ordenando meses para decrescente: * (operador de desempacotamento) é usado para expandir elementos de uma lista dentro de outra.
    df_rem_mensais = df_rem_mensais[
        [
            *df_rem_mensais.columns[:2],  # Mantém as duas primeiras colunas ('Ativo' e 'Tipo de Ativo')
            *sorted(df_rem_mensais.columns[2:], key=lambda x: x[0], reverse=True)
            # Ordena os meses do mais recente ao mais antigo
        ]
    ]

    # Se eu deixar pd.NA, não consigo arredondar. No df aparece tanto pd.NA quanto np.nan como 'None' mas tem diferença
    df_rem_mensais = df_rem_mensais.replace({pd.NA: np.nan})

    # Preencher valores NaN com 0 (ou outro valor de sua preferência)
    df_rem_mensais.fillna(0, inplace=True)


    return df_rem_mensais