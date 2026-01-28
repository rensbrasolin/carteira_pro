import pandas as pd
from datetime import date, timedelta
import numpy as np

from funcoes._global.fxg_web_scraping.fxg_web_scraping_cotacao import g_criar_df_cotacao_tvb3

# --------------------------------------------------------------------------------------------------------------------------------  Definindo fxs internas
# ________________________________________ Parte 1: Pré-consolidação
# Iniciando o df_posicao. Criando cols que usam as linhas nos cálculos. Aqui, df ainda não tem ticker únicos.

# df_ext_mov já existirá na página 'Análise carteira'. Então é só entregá-lo a fx.
def _iniciar_df_posicao(df_ext_mov):

    df_posicao = df_ext_mov.copy()

    # Mantendo apenas linahs de compras e vendas para somas no groupby fazer sentido.
    df_posicao = df_posicao.loc[df_posicao
                                ['Movimentação'] == 'Transferência - Liquidação']
    
    # Mantendo apenas cols necessárias
    df_posicao = df_posicao.drop(columns=['Instituição', 'Movimentação', 'Produto'])

    return df_posicao


def _criar_col_qtd_acumulada(df_posicao):

    # Ordenando antes de agrupar, por segurança
    df_posicao = df_posicao.sort_values(by='Data')

    # (Atualizada a cada compra/venda)
    df_posicao['Qtd Acumulada'] = df_posicao.groupby('Ticker')['Quantidade'].cumsum()

    return df_posicao


# Coluna vai ajustando o 'Valor Aplicado/Total Investido/ PM Total/ Custo Médio' conforme compras e vendas.
# Quando há vendas ele não debita o valor da venda (Preço vendido*qtde vendas), mas sim o PM atual*qtd vendas
def _criar_col_custo_medio(df_posicao):

    # Ordenando antes de agrupar, por segurança
    df_posicao = df_posicao.sort_values(by='Data')

    # Inicializa a coluna 'Custo médio'
    df_posicao['Custo Médio'] = 0.0

    # Agrupa o DataFrame por 'Ativo' para calcular o custo médio separadamente para cada ativo
    for ativo, grupo in df_posicao.groupby('Ticker'):
        indices = grupo.index  # Obtém os índices reais do DataFrame original
        custo_medio_acumulado = 0  # Inicializa o custo médio acumulado

        for i, idx in enumerate(indices):
            qtd_acumulada = df_posicao.loc[idx, 'Qtd Acumulada']
            entrada_saida = df_posicao.loc[idx, 'Entrada/Saída']
            valor_operacao = df_posicao.loc[idx, 'Valor da Operação']

            # Primeira linha do ativo: apenas copia o valor da operação
            if i == 0:
                custo_medio_acumulado = valor_operacao

            # Se a quantidade acumulada for 0, o custo médio também deve ser zerado
            elif qtd_acumulada == 0:
                custo_medio_acumulado = 0

            # Se for uma compra, soma o valor da operação ao custo médio acumulado
            elif entrada_saida == 'Credito':
                custo_medio_acumulado += valor_operacao

            # Se for uma venda, reduz o custo médio proporcionalmente à quantidade vendida
            elif entrada_saida == 'Debito':
                qtd_movimentada = abs(df_posicao.loc[idx, 'Quantidade']) # Garante que a quantidade seja positiva para o cálculo
                custo_medio_acumulado -= (custo_medio_acumulado / (qtd_acumulada + qtd_movimentada)) * qtd_movimentada

            # Atualiza o DataFrame com o custo médio calculado para a linha atual
            df_posicao.loc[idx, 'Custo Médio'] = custo_medio_acumulado

    return df_posicao


# # criar_col_pm - DEIXAR COMENTADA
# # Poderia ser criada aqui, mas para manter a organização, vou criá-la no outro arq, pois coluna não é consolidada, e sim calculada.
# # Caso um dia eu queira verificar evolução de PM e PREÇO PAGO a cada compra, esse df será útil.
# df_pos_atual_col_consolidadas_inicio['Preço Médio'] = df_pos_atual_col_consolidadas_inicio['Custo Médio'] / df_pos_atual_col_consolidadas_inicio['Qtd Acumulada']


def _consolidar_df_posicao(df_posicao):

    # Consolidando df
    # Deixando apenas a linha mais recente de cada ativo. Assim a coluna qtd_acumulada virará a coluna qtd_atual
    # Ordena pela data em ordem decrescente e mantém apenas a primeira ocorrência de cada ativo, sem groupby mesmo.
    df_posicao = df_posicao.sort_values('Data', ascending=False).drop_duplicates(subset='Ticker', keep='first')

    # Deixando apenas as cols necessárias, com nomes menores e/ou melhores.
    df_posicao = df_posicao[['Ticker', 'Tipo de Ativo', 'Qtd Acumulada', 'Custo Médio']]
    df_posicao.rename(columns={'Tipo de Ativo': 'Tipo', 'Qtd Acumulada': 'Qtd'}, inplace=True)

    return df_posicao


# _______________________________ Parte 2: Pós-consolidação - Criar colunas fora do df_posicao e trazê-las.
def _criar_df_remuneracoes(df_ext_mov):

    # Obtendo apenas movimentações de recebimento de remuneração (linhas)
    df_remuneracoes = df_ext_mov.loc[(df_ext_mov['Movimentação'] == 'Rendimento') |
                                            (df_ext_mov['Movimentação'] == 'Dividendo') |
                                            (df_ext_mov['Movimentação'] == 'Juros Sobre Capital Próprio')
                                            ].copy()

    # Mantendo apenas cols necessarias
    df_remuneracoes = df_remuneracoes[['Ticker', 'Valor da Operação']]
    df_remuneracoes.rename(columns={'Valor da Operação': 'Remunerações'}, inplace=True)

    # Agrupando por ativo, somando e resetandpo indice pra ticker voltar a ser coluna
    df_remuneracoes = df_remuneracoes.groupby('Ticker').sum().reset_index()

    # Deixando apenas as cols necessárias
    df_remuneracoes = df_remuneracoes[['Ticker', 'Remunerações']]

    return df_remuneracoes


# fx g_criar_df_cotacao_tvb3 é global, por isso nao está aqui!


# Resultado de vendas. df só cria linha se houver registro, mas o merge acontece normalmente preenchendo c/ 0 se vazio.
# saldo_posicao é como um estoque corrente: soma as compras, subtrai as vendas.
# Se o investidor zerar a posição (saldo 0), reiniciamos o preço médio.
# Assim, novas compras feitas após zerar não misturam o PM com as compras antigas, como você queria.
def _criar_df_res_vendas(df_ext_mov):

    # Obtendo apenas movimentações de compras e vendas
    df_res_vendas = df_ext_mov.loc[
        (df_ext_mov['Movimentação'] == 'Transferência - Liquidação')].copy().reset_index()

    # Deixando apenas as cols necessárias
    df_res_vendas = df_res_vendas[
        ['Ticker', 'Data', 'Quantidade', 'Valor da Operação']]

    # VER EXPLICAÇÃO NAS ANOTAÇÕES

    # Ordena o DataFrame por ativo e data
    df_res_vendas.sort_values(by=['Ticker', 'Data'], inplace=True)

    # Cria a nova coluna com valor zero inicialmente
    df_res_vendas['PM na Venda'] = 0.0

    # Itera sobre cada ativo para calcular o preço médio na venda
    for ticker, grupo in df_res_vendas.groupby('Ticker'):
        # Inicializa acumuladores de quantidade, valor e saldo da posição
        qtde_acumulada = 0
        valor_acumulado = 0.0
        saldo_posicao = 0  # Novo: acompanha posição líquida do ativo

        # Itera pelas linhas do grupo
        for idx in grupo.index:
            row = df_res_vendas.loc[idx]

            if row['Quantidade'] > 0:  # É uma compra
                # Atualiza acumuladores
                qtde_acumulada += row['Quantidade']
                valor_acumulado += row['Valor da Operação']
                saldo_posicao += row['Quantidade']  # Novo
                # Atribui 0 ao preço médio na coluna para compras
                df_res_vendas.loc[idx, 'PM na Venda'] = 0.0

            else:  # É uma venda
                if qtde_acumulada > 0:
                    preco_medio = valor_acumulado / qtde_acumulada
                else:
                    preco_medio = 0.0  # Caso não haja histórico de compras

                # Atribui o preço médio na venda para a linha de venda
                df_res_vendas.loc[idx, 'PM na Venda'] = preco_medio

                # Atualiza saldo da posição
                saldo_posicao += row['Quantidade']  # row['Quantidade'] é negativa

                # Se posição for zerada, zera os acumu  ladores
                if saldo_posicao == 0:
                    qtde_acumulada = 0
                    valor_acumulado = 0.0

    # Agora que não preciso mais das compras, vou fazer alguns ajustes

    # Manter só Vendas
    df_res_vendas = df_res_vendas.loc[
        (df_res_vendas['Quantidade'] < 0)].copy().reset_index(drop=True)

    # Alterar nome da coluna para un nome intuitivo
    df_res_vendas.rename(columns={'Valor da Operação': 'Total Vendido'}, inplace=True)

    # Transpor números negativos
    df_res_vendas[['Quantidade', 'Total Vendido']] *= -1

    # Criando coluna de Preço Médio Total, para poder encontrar a diferença, que se for positiva será lucro e se for negativa será prejuízo na venda
    df_res_vendas['PM Total'] = df_res_vendas['Quantidade'] * df_res_vendas['PM na Venda']

    # Criando coluna de lucro/prej. nas vendas
    df_res_vendas['Resultado de Vendas'] = df_res_vendas['Total Vendido'] - df_res_vendas['PM Total']

    df_res_vendas = df_res_vendas[['Ticker', 'Resultado de Vendas']]

    # Agrupando por ativos
    df_res_vendas = df_res_vendas.groupby('Ticker').sum()

    # Para que índice "Ativo" vire coluna
    df_res_vendas = df_res_vendas.reset_index()

    return df_res_vendas

# _______________________________ Parte 3: Colunas calculadas dentro do df
def _criar_cols_calculadas(df_posicao):

    # Preço Médio
    df_posicao['Preço Médio'] = df_posicao['Custo Médio'] / df_posicao['Qtd']

    # Patrimônio Atual
    df_posicao['Patrimônio Atual'] = df_posicao["Qtd"] * df_posicao["Cotação"]

    # Variação %
    df_posicao['Variação %'] = (( df_posicao['Cotação'] / df_posicao['Preço Médio']) -1) * 100

    # Variação $
    df_posicao['Variação $'] = (df_posicao['Patrimônio Atual'] - df_posicao['Custo Médio'])

    # Performance $ - Não reflete o saldo atual, mas sim o retorno, a diferença.
    df_posicao['Performance $'] = df_posicao['Resultado de Vendas'] + df_posicao['Remunerações'] + df_posicao['Variação $']


    # # Performance % - Deixar um pouco para ver se tem alternativas, se não, depois excluir.
    # # Não será exibido, pois não faz sentido comparar a Performance $ de todu um período com o Custo Médio atual.
    # # A única medida que faz sentido comparar com o Custo Médio Atual é o Patrimônuo Atual, que muda junto com ele.
    # # Imagina que o investidor liquidou toda a posição menos 1. Nesse caso o CM será igual ao PM, e não faria sentido
    # # comparar esse CM/PM com Remunerações $ e Resultado de Vendas de todu um período.
    # # Daria no mesmo usar 'Variação $' ou 'Patimônio Atual'-1.
    # # Posições que foram zeradas terão valor vazio pois custo médio será 0
    # df_pos_atual['Performance %'] = df_pos_atual['Performance $']/ df_pos_atual['Custo Médio'] * 100


    # # Yield on Cost % - Deixar um pouco e depois provavelmente excluir.
    # # Não será exibido, pois não faz sentido comparar todos os dividendos recebidos com o Custo Médio atual.
    # # A única medida que faz sentido comprar com o Custo Médio Atual é o Patrimônuo Atual, que muda junto com ele.
    # # Essa medida faz mais sentido ser calculada a cada recebimento dela, como faço na seção de remunerações
    # df_pos_atual['Yield on Cost %'] = ( df_pos_atual['Remunerações $'] / df_pos_atual['Custo Médio']) * 100

    return df_posicao


# _______________________________ Parte 4: TIR
def _criar_df_tir(df_ext_mov_fin, df_posicao):

    # ------------------------------------------------------------------------- Definindo fx interna
    def _xirr(df, guess=0.05, date_column='date', amount_column='amount'):
        '''Calculates XIRR from a series of cashflows.
           Needs a dataframe with columns date and amount, customisable through parameters.
           Requires Pandas, NumPy libraries'''

        df = df.sort_values(by=date_column).reset_index(drop=True)

        amounts = df[amount_column].values
        dates = df[date_column].values

        years = np.array(dates - dates[0], dtype='timedelta64[D]').astype(int) / 365

        step = 0.05
        epsilon = 0.0001
        limit = 1000
        residual = 1

        # Test for direction of cashflows
        disc_val_1 = np.sum(amounts / ((1 + guess) ** years))
        disc_val_2 = np.sum(amounts / ((1.05 + guess) ** years))
        mul = 1 if disc_val_2 < disc_val_1 else -1

        # Calculate XIRR
        for i in range(limit):
            prev_residual = residual
            residual = np.sum(amounts / ((1 + guess) ** years))
            if abs(residual) > epsilon:
                if np.sign(residual) != np.sign(prev_residual):
                    step /= 2
                guess = guess + step * np.sign(residual) * mul
            else:
                return guess  # Retorna a tir em decimal
    

# ------------------------------------------------------------------------- Criando data

    data_hoje = date.today() # data hj será sempre a data de hj.
    data_util = data_hoje # Data útil inicialmente é hj, mas se hj naõ for dia útil, vira o dia útil anterior.

    if data_hoje.weekday() == 6:  # Domingo é o dia 6
        data_util = data_hoje - timedelta(days=2)

    # Se hoje for sábado, subtraia 1 dia (para obter a cotação de sexta-feira)
    elif data_hoje.weekday() == 5:  # Sábado é o dia 5
        data_util = data_hoje - timedelta(days=1)


    # --------------------------------------------------- Criando 1 df para cada ticker para calular a TIR para cada um

    df_mov_tir = df_ext_mov_fin.copy()

    # Obter valores únicos da coluna 'Ticker'
    lista_fluxo_ativos = df_mov_tir['Ticker'].unique()

    # Dicionário para armazenar os DataFrames separados pot ticker
    dict_dfs_fluxo = {}

    # Loop sobre cada ativo
    for ticker in lista_fluxo_ativos:

        # Criando um df_fluxo para cada ativo, Filtrar o DataFrame original para obter apenas as linhas com o ativo atual
        df_fluxo = df_mov_tir[df_mov_tir['Ticker'] == ticker].reset_index(drop=True)

        # Invertendo sinais: Compras estão +, Vendas estão - Preciso inverter
        df_fluxo.loc[(df_fluxo[
                          'Movimentação'] == 'Transferência - Liquidação'),
                          'Valor da Operação'] *= -1  # Usei '=' aqui para atribuir o valor. se não ele multiplica mas não preenche

        # Filtrando só as coluans necessárias
        df_fluxo = df_fluxo[['Data', 'Valor da Operação']]

        # Ordenando para data decrescente
        df_fluxo = df_fluxo.sort_values(by='Data', ascending=True).reset_index(drop=True)

        ###########     INSERINDO A ÚLTIMA LINHA, QUE É O 'PATRIMÔNIO ATUAL'     ###########

        # Primeiro vou criar uma variável 'patrimonio_atual' puxada lá do df_acoes_patrimonio, que é onde tem o valor que preciso.
        patrimonio_atual_ticker = df_posicao['Patrimônio Atual'].loc[df_posicao['Ticker'] == ticker]


        # Criando um dict para inserir como ultima linha. Tive que formatar o valor com float.
        # Usei iloc mesmo não sendo em df. Pois só com float daria warning, gpt que sugeriu e funcionou
        dic_venda_simulada_ticker = {'Data': data_util, 'Valor da Operação': float(patrimonio_atual_ticker.iloc[0])}

        # Achando a ultima linha e inserindo dados nela
        tam = len(df_fluxo)
        df_fluxo.loc[tam] = [dic_venda_simulada_ticker['Data'], dic_venda_simulada_ticker['Valor da Operação']]

        # Converter a coluna "Data" para datetime, pois mesmo já sendo (<class 'datetime.date'>), no df dava ruim.
        df_fluxo['Data'] = pd.to_datetime(df_fluxo['Data'])

        # Armazenar o DataFrame filtrado no dicionário, usando o nome do ativo como chave
        dict_dfs_fluxo[ticker] = df_fluxo



    # Agora, com todos os fluxos armazenados, vou calcular a TIR para cada ativo e inserir "ativo:TIR" no dic_tirs
    dic_tirs = {}

    for ticker, df_fluxo in dict_dfs_fluxo.items():
        # Aplicando a função em cada ativo
        tir = _xirr(df_fluxo, guess=0.05, date_column='Data', amount_column='Valor da Operação') * 100
        # Iinserindo o item no dicinário (ativo = TIR)
        dic_tirs[ticker] = tir


    # Criando um df com os dados do dic
    df_tir = pd.DataFrame.from_dict(dic_tirs, orient='index', columns=['TIR'])

    # Defenindo um nome para o índice, que estava em branco. Que por sinal tem que ser diferente de 'Ativo'
    df_tir.index.name = 'Ticker'

    # Resetando índice para que vire coluna
    df_tir = df_tir.reset_index()


    return df_tir


# --------------------------------------------------------------------------------------------------------------------- FX principal que cria o criar_df_posicao
def criar_df_posicao(df_ext_mov):

    # ==================================================================================================== Parte 1
    df_posicao = _iniciar_df_posicao(df_ext_mov=df_ext_mov)

    df_posicao = _criar_col_qtd_acumulada(df_posicao=df_posicao)

    df_posicao = _criar_col_custo_medio(df_posicao=df_posicao)

    df_posicao = _consolidar_df_posicao(df_posicao=df_posicao)

    # ==================================================================================================== Parte 2
    # Aqui, partimos do df_ext_mov para se chegar nessas medidas/colunas. É criado um df/fx para cada col que queremos trazer.
    # Depois, cada df_col é trazido pro df_posicao
    # ----------------------------------------------------------------------- Parte 2a: Obter df_ext_mov_fin
    # Começar obtendo os dados (df_ext_mov_fin) que vou precisar usar nas próximas fxs para se chegar nas medidas desejadas.
    # Df criado para eliminar movimentações que não sejam financeiras do df_ext_mov.
    # Poderia filtar não pela movimentação mas sim pelas cols de valores, excluindo valores Nones.
    # Mas quero ter controle dessas outras movimentações mais de perto.
    
    # Df utilizado apenas nas fxs: g_criar_df_cotacao_tvb3 e TIR
    df_ext_mov_fin = df_ext_mov.copy()

    lista_movs_nao_financeiras = [
        "Direitos de Subscrição - Não Exercido",
        "Cessão de Direitos - Solicitada",
        "Cessão de Direitos",
        "Direito de Subscrição",
        "Atualização",
        "Desdobro",
        "Bonificação em Ativos" # Tive bonificação de ITSA4 em 12/2025 mas foi qtd 0,36. Olhei no nubank e qtd não mudou.
        # Tenho lista salva em anotações.
    ]

    # Filtrando o df_ext_mov para eliminar movimentações e tickers indesejados.
    df_ext_mov_fin = df_ext_mov_fin[~df_ext_mov_fin['Movimentação'].isin(lista_movs_nao_financeiras)]

    # ----------------------------------------------------------------------- Parte 2b: Cotação - Fxg     ************* DEIXAR COMENTADO DURANTE TESTES ********
    # Pegando cotação e pondo em um df
    df_cotacao_tvb3 = g_criar_df_cotacao_tvb3(df_ext_mov_fin=df_ext_mov_fin)

    # Trazendo dados para o df_posicao
    df_posicao = df_posicao.merge(
        df_cotacao_tvb3[['Ticker', 'Cotação']],
        left_on='Ticker',
        right_on='Ticker',
        how='left'
    )

    # ----------------------------------------------------------------------- Parte 2c: Remunerações
    # Cria df_col
    df_remuneracoes = _criar_df_remuneracoes(df_ext_mov=df_ext_mov)

    # Trazendo dados para o df_posicao
    df_posicao = df_posicao.merge(
        df_remuneracoes[['Ticker', 'Remunerações']],
        left_on='Ticker',
        right_on='Ticker',
        how='left'
    ).fillna(0)  # Para não ficar None


    # ----------------------------------------------------------------------- Parte 2d: Resultado de Vendas
    df_res_vendas = _criar_df_res_vendas(df_ext_mov=df_ext_mov)

    # Trazendo dados para o df_posicao
    df_posicao = df_posicao.merge(
        df_res_vendas[['Ticker', 'Resultado de Vendas']],
        left_on='Ticker',
        right_on='Ticker',
        how='left'
    ).fillna(0)  # Para não ficar None


    # ==================================================================================================== Parte 3: Colunas calculadas
    df_posicao = _criar_cols_calculadas(df_posicao=df_posicao)


    # ==================================================================================================== Parte 4: TIR
    # Criada por último pq precisa da col Patrimônio Atual do df_posicao

    df_tir = _criar_df_tir(df_ext_mov_fin=df_ext_mov_fin, df_posicao=df_posicao)

    # Trazendo dados para o df_posicao
    df_posicao = df_posicao.merge(
        df_tir[['Ticker', 'TIR']],
        left_on='Ticker',
        right_on='Ticker',
        how='left'
    )



    return df_posicao

