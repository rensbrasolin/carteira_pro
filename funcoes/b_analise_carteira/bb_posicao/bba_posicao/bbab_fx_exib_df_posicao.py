import streamlit as st
import pandas as pd
from datetime import date, timedelta
import numpy as np

from icones import TITULO_DADOS, TITULO_POSICAO, TITULO_VISAO_GERAL, ICONE_DADOS


# ---------------------------------------------------------------------------------------------------------- Fxs Indicadores
# Cálculos são tão simples que poderia fazer a maioria em uma só fx. Mas vou manter o padrão de deixar separado.
# Na hora de realmente exibir lá na página, eu crio as cols e ponho os indicadores onde eu quiser.
# Diferente do df_ext_mov onde as fxs de indicadores são chamadas no mesmo arquivo na fx principal que exibe o df,
# aqui no df_posicao vou chamar as fxs direto lá na página. Isso pq o indicador TIR precisa receber o df_ext_mov
# para obter o fluxo. Eu até tentei criar o df_ext_mov dentro da fx TIR, mas para criá-lo tbm precisa da var 'arquivos'.
def _calc_indicador_qtd_ativos_df_posicao(df_posicao):
    indicador_qtd_ativos_df_posicao = df_posicao['Qtd'].count()
    return indicador_qtd_ativos_df_posicao


def _calc_indicador_qtd_tipos_ativos_df_posicao(df_posicao):
    indicador_qtd_tipos_ativos_df_posicao = df_posicao['Tipo'].nunique()
    return indicador_qtd_tipos_ativos_df_posicao


def _calc_indicador_custo_medio_df_posicao(df_posicao):
    indicador_custo_medio_df_posicao = df_posicao['Custo Médio'].sum()
    return indicador_custo_medio_df_posicao


def _calc_indicador_remuneracoes_df_posicao(df_posicao):
    indicador_remuneracoes_df_posicao = df_posicao['Remunerações'].sum()
    return indicador_remuneracoes_df_posicao


def _calc_indicador_res_vendas_df_posicao(df_posicao):
    indicador_res_vendas_df_posicao = df_posicao['Resultado de Vendas'].sum()
    return indicador_res_vendas_df_posicao

    
def _calc_indicador_patrimonio_atual_df_posicao(df_posicao):
    indicador_patrimonio_atual_df_posicao = df_posicao['Patrimônio Atual'].sum()
    return indicador_patrimonio_atual_df_posicao


def _calc_indicador_variacao_absoluta_df_posicao(df_posicao):
    indicador_variacao_absoluta_df_posicao = df_posicao['Variação $'].sum()
    return indicador_variacao_absoluta_df_posicao


def _calc_indicador_variacao_percentual_df_posicao(indicador_patrimonio_atual_df_posicao, indicador_custo_medio_df_posicao):
    indicador_variacao_percentual_df_posicao = (indicador_patrimonio_atual_df_posicao / indicador_custo_medio_df_posicao - 1) * 100
    return indicador_variacao_percentual_df_posicao


def _calc_indicador_performance_absoluta_df_posicao(df_posicao):
    indicador_performance_absoluta_df_posicao = df_posicao['Performance $'].sum()
    return indicador_performance_absoluta_df_posicao

def _calc_indicador_tir_df_posicao(df_ext_mov, indicador_patrimonio_atual_df_posicao):

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

    # ------------------------------------------------------------------------- Criando o df_fluxo_caixa
    # Parte do df_ext_mov, passa pelo df_ext_mov_fin e se chega no df_fluxo_caixa
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

    df_fluxo_caixa = df_ext_mov_fin.copy()

    # ------------------------------------------------- Tratando     df_fluxo_caixa = df_ext_mov_fin.copy()
    # Compras estão (+), Vendas estão (-). Preciso inverter estes sinais antes de passar o df pra fx.
    # Não atribuir variavel a essa linha, se não ele só manterá a coluna 'Valor da Operação'
    # Por isso usei '=', para atribuir o valor. se não ele multiplica mas não preenche.
    df_fluxo_caixa.loc[(df_fluxo_caixa[
                            'Movimentação'] == 'Transferência - Liquidação'), 'Valor da Operação'] *= -1

    df_fluxo_caixa = df_fluxo_caixa[['Data', 'Valor da Operação']]

    # Ordenando para data decrescente
    df_fluxo_caixa = df_fluxo_caixa.sort_values(by='Data', ascending=True).reset_index(drop=True)

    # ------------------------------------------------------ Criando data para usar na última mov
    data_hoje = date.today()  # data hj será sempre a data de hj.
    data_util = data_hoje  # Data útil inicialmente é hj, mas se hj naõ for dia útil, vira o dia útil anterior.

    if data_hoje.weekday() == 6:  # Domingo é o dia 6
        data_util = data_hoje - timedelta(days=2)

    # Se hoje for sábado, subtraia 1 dia (para obter a cotação de sexta-feira)
    elif data_hoje.weekday() == 5:  # Sábado é o dia 5
        data_util = data_hoje - timedelta(days=1)

    # ---------------------------------------------- Pegando patrimonio atual e inserindo a ultima linha
    # Criando um dict para inserir como ultima linha. Tive que formatar o valor com float.
    # Usei iloc mesmo não sendo em df. Pois só com float daria warning, gpt que sugeriu e funcionou
    dic_venda_simulada = {'Data': data_util, 'Valor da Operação': indicador_patrimonio_atual_df_posicao}

    # Achando a ultima linha e inserindo dados nela
    tam = len(df_fluxo_caixa)
    df_fluxo_caixa.loc[tam] = [dic_venda_simulada['Data'], dic_venda_simulada['Valor da Operação']]

    # Converter a coluna "Data" para datetime, pois mesmo já sendo (<class 'datetime.date'>), no df dava ruim.
    # Essa conversão precisa ser feita aqui, logo após inserir o dic na última linha.
    df_fluxo_caixa['Data'] = pd.to_datetime(df_fluxo_caixa['Data'])

    # ------------------------------------------------------ Finalmente aplicando a fx Xirr
    indicador_tir_df_posicao = _xirr(df_fluxo_caixa, guess=0.05, date_column='Data', amount_column='Valor da Operação') * 100


    return indicador_tir_df_posicao



# # Não faz mais sentido. Deixar um pouco e depois excluir
# yieldoncost_total_df_pos_atual = remuneracoes_total_df_pos_atual / custo_medio_total_df_pos_atual * 100

# # Não faz mais sentido. Deixar um pouco e depois excluir
# # No cálculo da coluna, essa medida ficará zerada se a posição for zerada. Já que compara o desempenho com o 'Custo Médio', que estará zerado.
# # Já aqui no total, não, pois só utiliza valores absolutos. E sim, as posições zeradas terão tbm a coluna 'Variação $' zeradas,
# # porém, nesse cálculo não há problema, pois quando a posição é zerada, o que era 'Variação $' vira 'Resultado com Vendas'. acho
# performance_percentual_total_df_pos_atual = ((remuneracoes_total_df_pos_atual + res_vendas_total_df_pos_atual + variacao_absoluta_total_df_pos_atual)
#                                              / custo_medio_total_df_pos_atual * 100)



# ---------------------------------------------------------------------------------------------------- Exibição do df principal
# Diferente do df_ext_mov, aqui se exibe só o df. Devido a ter mais complexidade nos cálculos dos indicadores. Não há filtros.
def _exibir_df_posicao(df_posicao):

    df_posicao_exib = df_posicao.copy()

    # ______________________________________________________________________________________DF
    # Defina EXATAMENTE como cada coluna deve ser formatada
    COLUMN_CONFIG = {
        # # DATAS
        # 'Data': st.column_config.DateColumn("Data", format="DD/MM/YYYY"),
        
        # VALORES MONETÁRIOS 
        'Custo Médio': st.column_config.NumberColumn("Custo Médio", format="dollar"), # R$     %.2f
        'Cotação': st.column_config.NumberColumn("Cotação", format="dollar"), #localized
        'Remunerações': st.column_config.NumberColumn("Remunerações", format="dollar"),
        'Resultado de Vendas': st.column_config.NumberColumn("Resultado de Vendas", format="dollar"),
        'Preço Médio': st.column_config.NumberColumn("Preço Médio", format="dollar"),
        'Patrimônio Atual': st.column_config.NumberColumn("Patrimônio Atual", format="dollar"),
        'Variação $': st.column_config.NumberColumn("Variação $", format="dollar"),
        'Performance $': st.column_config.NumberColumn("Performance $", format="dollar"),
        
        # QUANTIDADES INTEIRAS
        'Qtd': st.column_config.NumberColumn("Qtd", format="%d"),
        
        # PERCENTUAIS
        'Variação %': st.column_config.NumberColumn("Variação %", format="%.2f%%"),
        'TIR': st.column_config.NumberColumn("TIR", format="%.2f%%"),
    }

    # Mostrar
    lista_ordem_cols = ['Ticker', 'Tipo', 'Qtd', 'Preço Médio', 'Custo Médio', 'Cotação', 'Patrimônio Atual',
                         'Variação %', 'Variação $', 'Remunerações', 'Resultado de Vendas', 'Performance $', 'TIR']  

    with st.expander(f'{TITULO_DADOS} *{TITULO_POSICAO} > {TITULO_VISAO_GERAL}*', expanded=False, icon=f'{ICONE_DADOS}'):
        st.dataframe(
            df_posicao_exib,
            column_order=lista_ordem_cols,
            column_config=COLUMN_CONFIG, # É por aqui que vou conseguir criar cols com imagem e gráfico. Ver na doc do st.
            use_container_width=True,
            hide_index=True
        )