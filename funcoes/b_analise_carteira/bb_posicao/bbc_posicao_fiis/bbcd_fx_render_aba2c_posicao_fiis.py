import streamlit as st

from icones import *
from funcoes._global.fxg_tratamento import g_formatar_valor_grande_indicadores
# 2. Posição
from funcoes.b_analise_carteira.bb_posicao.bba_posicao.bbab_fx_exib_df_posicao import (
    _calc_indicador_qtd_ativos_df_posicao,
    _calc_indicador_custo_medio_df_posicao, _calc_indicador_patrimonio_atual_df_posicao,
    _calc_indicador_variacao_percentual_df_posicao, _calc_indicador_variacao_absoluta_df_posicao,
    _calc_indicador_remuneracoes_df_posicao, _calc_indicador_res_vendas_df_posicao,
    _calc_indicador_performance_absoluta_df_posicao, _calc_indicador_tir_df_posicao,
)
from funcoes.b_analise_carteira.bb_posicao.bba_posicao.bbac_fx_graficos_df_posicao import (
    _criar_grafico_rank_variacao_df_posicao, _criar_grafico_rank_tir_df_posicao
)
# 2a. Posição FIIs
from funcoes.b_analise_carteira.bb_posicao.bbc_posicao_fiis.bbcb_fx_exib_df_posicao_fiis import(
    _exibir_df_posicao_fiis,
    _calc_indicador_qtd_segmentos_df_posicao_fiis
)
from funcoes.b_analise_carteira.bb_posicao.bbc_posicao_fiis.bbcc_fx_graficos_df_posicao_fiis import (
    _criar_grafico_cm_pa_rem_df_posicao_fiis, _criar_grafico_cm_pa_rem_total_df_posicao_fiis,
    _criar_grafico_distrib_cm_tipo_df_posicao_fiis, _criar_grafico_distrib_pa_tipo_df_posicao_fiis,
    _criar_grafico_distrib_cm_segmento_df_posicao_fiis, _criar_grafico_distrib_pa_segmento_df_posicao_fiis
)








def render_aba2c_posicao_fiis(df_ext_mov, df_posicao_fiis):
    st.markdown(f'#### {ICONE_FIIS} {TITULO_FIIS}', text_alignment='center', help='FIIs + FIAgros + FIInfras')
    st.caption(f'*{ICONE_ANALISE_CARTEIRA} {TITULO_ANALISE_CARTEIRA} > {ICONE_POSICAO} {TITULO_POSICAO} > {ICONE_FIIS} {TITULO_FIIS}*',
                text_alignment='center')
    

    # ------------------------------------------------------------------------------------------------------------- Exibindo indicadores do df_posicao_fiis
    # Reutilização das fxs de indicadores do df_posicao. Só crio fx para ações, se for mostrar indicador diferente do df_posicao.
    with st.expander(f'{TITULO_INDICADORES} *{TITULO_POSICAO} > {TITULO_FIIS}*', expanded=False, icon=f'{ICONE_INDICADORES}'):
        col1, col2, col3, col4, col5 = st.columns([0.75, 1, 1, 1, 1])
        with col1:
            indicador_qtd_ativos_df_posicao_fiis = _calc_indicador_qtd_ativos_df_posicao(df_posicao=df_posicao_fiis)
            st.metric(f'{ICONE_INDICADOR_QTD_ATIVOS} {TITULO_INDICADOR_QTD_ATIVOS}',
                        f' {indicador_qtd_ativos_df_posicao_fiis:,.0f}', border=True)

            indicador_qtd_setores_df_posicao_fiis = _calc_indicador_qtd_segmentos_df_posicao_fiis(df_posicao_fiis=df_posicao_fiis)
            st.metric(f'{ICONE_INDICADOR_QTD_SEGMENTOS_FIIS} {TITULO_INDICADOR_QTD_SEGMENTOS_FIIS}',
                        f'{indicador_qtd_setores_df_posicao_fiis:,.0f}', border=True)

        with col2:
            indicador_custo_medio_df_posicao_fiis = _calc_indicador_custo_medio_df_posicao(df_posicao=df_posicao_fiis)
            indicador_custo_medio_df_posicao_fiis_fmt = g_formatar_valor_grande_indicadores(indicador_custo_medio_df_posicao_fiis)
            st.metric(f'{ICONE_INDICADOR_CM} {TITULO_INDICADOR_CM}',
                        indicador_custo_medio_df_posicao_fiis_fmt,
                        border=True,
                        help=f"""
                        R$ {indicador_custo_medio_df_posicao_fiis:,.2f}
                        - Soma do valor de todas as compras
                        - Quando há venda, subtrai-se o valor de 'Preço Médio * Qtd Vendida'
                        """
                        )
            
            indicador_patrimonio_atual_df_posicao_fiis = _calc_indicador_patrimonio_atual_df_posicao(df_posicao=df_posicao_fiis)
            indicador_patrimonio_atual_df_posicao_fiis_fmt = g_formatar_valor_grande_indicadores(indicador_patrimonio_atual_df_posicao_fiis)
            st.metric(f'{ICONE_INDICADOR_PA} {TITULO_INDICADOR_PA}',
                    indicador_patrimonio_atual_df_posicao_fiis_fmt,
                    border=True,
                    help = f"""
                    R$ {indicador_patrimonio_atual_df_posicao_fiis:,.2f}\n
                    'Quantidade de Ativos * Cotação Atual'
                    """
                    )
            
        with col3:
            # Fx não usa o df no seu cálculo, mas sim indicadores.
            indicador_variacao_percentual_df_posicao_fiis =_calc_indicador_variacao_percentual_df_posicao(
                indicador_patrimonio_atual_df_posicao=indicador_patrimonio_atual_df_posicao_fiis,
                indicador_custo_medio_df_posicao=indicador_custo_medio_df_posicao_fiis
                )
            st.metric(f'{ICONE_INDICADOR_VAR_PERCENTUAL} {TITULO_INDICADOR_VAR_PERCENTUAL}',
                        f'{indicador_variacao_percentual_df_posicao_fiis:,.2f}%', border=True,
                        help='Diferença entre Cotação Atual e Preço Médio'
                        )
            
            indicador_variacao_absoluta_df_posicao_fiis = _calc_indicador_variacao_absoluta_df_posicao(df_posicao=df_posicao_fiis)
            indicador_variacao_absoluta_df_posicao_fiis_fmt = g_formatar_valor_grande_indicadores(indicador_variacao_absoluta_df_posicao_fiis)
            st.metric(f'{ICONE_INDICADOR_VAR_ABSOLUTA} {TITULO_INDICADOR_VAR_ABSOLUTA}',
                        indicador_variacao_absoluta_df_posicao_fiis_fmt,
                        border=True,
                        help=f"""
                        R$ {indicador_variacao_absoluta_df_posicao_fiis:,.2f}\n
                        Diferença absoluta entre Patrimônio Atual e Custo Médio
                        """
                        )
            
        with col4:
            indicador_remuneracoes_df_posicao_fiis =_calc_indicador_remuneracoes_df_posicao(df_posicao=df_posicao_fiis)
            indicador_remuneracoes_df_posicao_fiis_fmt = g_formatar_valor_grande_indicadores(indicador_remuneracoes_df_posicao_fiis)
            st.metric(f'{ICONE_INDICADOR_REMUNERACOES} {TITULO_INDICADOR_REMUNERACOES}',
                        indicador_remuneracoes_df_posicao_fiis_fmt,
                        border=True,
                        help=f"""
                        R$ {indicador_remuneracoes_df_posicao_fiis:,.2f}\n
                        Soma dos recebimentos de:
                        - Dividendo
                        - Juros Sobre Capital Próprio
                        - Rendimento"""
                        )
            
            indicador_res_vendas_df_posicao_fiis = _calc_indicador_res_vendas_df_posicao(df_posicao=df_posicao_fiis)
            indicador_res_vendas_df_posicao_fiis_fmt = g_formatar_valor_grande_indicadores(indicador_res_vendas_df_posicao_fiis)
            st.metric(f'{ICONE_INDICADOR_RES_VENDAS} {TITULO_INDICADOR_RES_VENAS}',
                        indicador_res_vendas_df_posicao_fiis_fmt,
                        border=True,
                        help=f"""
                        R$ {indicador_res_vendas_df_posicao_fiis:,.2f}\n
                        Saldo dos resultados (lucro ou prejuízo) de todas as operações de vendas
                        """
                        )

        with col5:
            indicador_performance_absoluta_df_posicao_fiis = _calc_indicador_performance_absoluta_df_posicao(df_posicao=df_posicao_fiis)
            indicador_performance_absoluta_df_posicao_fiis_fmt = g_formatar_valor_grande_indicadores(indicador_performance_absoluta_df_posicao_fiis)
            st.metric(f'{ICONE_INDICADOR_PERF_ABSOLUTA} {TITULO_INDICADOR_PERF_ABSOLUTA}',
                        indicador_performance_absoluta_df_posicao_fiis_fmt,
                        border=True,
                        help=f'''
                        R$ {indicador_performance_absoluta_df_posicao_fiis:,.2f}\n
                        Saldo dos resultados de:
                        - Variação Absoluta
                        - Remunerações
                        - Resultado de Vendas
                        '''
                        )
            
            # Filtrando df_ext_mov para entregá-lo a fx
            df_ext_mov_fiis = df_ext_mov.loc[df_ext_mov['Tipo de Ativo'].isin(['FII', 'FIAgro', 'FIInfra'])].copy()
            indicador_tir_df_posicao_fiis = _calc_indicador_tir_df_posicao(
                df_ext_mov=df_ext_mov_fiis, indicador_patrimonio_atual_df_posicao=indicador_patrimonio_atual_df_posicao_fiis)
            st.metric(f'{ICONE_INDICADOR_TIR} {TITULO_INDICADOR_TIR}',
                        f'{indicador_tir_df_posicao_fiis:,.2f}% a.a.', border=True,
                        help='''
                        Calcula a taxa de retorno anual, considerando todas as movimentações do fluxo de caixa da carteira:
                        - Compras [ - ]
                        - Vendas [ + ]
                        - Remunerações [ + ]
                        '''
                        )
    # ------------------------------------------------------------------------------------------------------------- Exibindo df_posicao_acoes
    _exibir_df_posicao_fiis(df_posicao_fiis=df_posicao_fiis)
    # ------------------------------------------------------------------------------------------------------------- Exibindo gráficos do df_posicao_acoes
    with st.expander(f'{TITULO_GRAFICOS} *{TITULO_POSICAO} > {TITULO_FIIS}*', expanded=False, icon=f'{ICONE_GRAFICOS}'):

        col1, col2 = st.columns([1.65, 0.35])
        # Gráfico 1a
        with col1:
            grafico_cm_pa_rem_df_posicao_fiis = _criar_grafico_cm_pa_rem_df_posicao_fiis(df_posicao_fiis=df_posicao_fiis)
            with st.container(border=True):
                st.plotly_chart(grafico_cm_pa_rem_df_posicao_fiis, use_container_width=True)
        # Gráfico 1b
        with col2:
            grafico_cm_pa_rem_total_df_posicao_fiis = _criar_grafico_cm_pa_rem_total_df_posicao_fiis(
            indicador_custo_medio_df_posicao_fiis=indicador_custo_medio_df_posicao_fiis,
            indicador_patrimonio_atual_df_posicao_fiis=indicador_patrimonio_atual_df_posicao_fiis,
            indicador_remuneracoes_df_posicao_fiis=indicador_remuneracoes_df_posicao_fiis,
            indicador_variacao_percentual_df_posicao_fiis=indicador_variacao_percentual_df_posicao_fiis
            )
            with st.container(border=True):
                st.plotly_chart(grafico_cm_pa_rem_total_df_posicao_fiis, use_container_width=True)                
                        
        col1, col2 = st.columns(2)
        # Gráfico 2
        with col1:
            grafico_distrib_cm_tipo_df_posicao_fiis = _criar_grafico_distrib_cm_tipo_df_posicao_fiis(df_posicao_fiis=df_posicao_fiis)
            with st.container(border=True):
                st.plotly_chart(grafico_distrib_cm_tipo_df_posicao_fiis, use_container_width=True)
        # Gráfico 3
        with col2:
            grafico_distrib_pa_tipo_df_posicao_fiis = _criar_grafico_distrib_pa_tipo_df_posicao_fiis(df_posicao_fiis=df_posicao_fiis)
            with st.container(border=True):
                st.plotly_chart(grafico_distrib_pa_tipo_df_posicao_fiis, use_container_width=True)

        col1, col2 = st.columns(2)
        # Gráfico 4
        with col1:
            grafico_distrib_cm_segmento_df_posicao_fiis = _criar_grafico_distrib_cm_segmento_df_posicao_fiis(df_posicao_fiis=df_posicao_fiis)
            with st.container(border=True):
                st.plotly_chart(grafico_distrib_cm_segmento_df_posicao_fiis, use_container_width=True)
        # Gráfico 5
        with col2:
            grafico_distrib_pa_segmento_df_posicao_fiis = _criar_grafico_distrib_pa_segmento_df_posicao_fiis(df_posicao_fiis=df_posicao_fiis)
            with st.container(border=True):
                st.plotly_chart(grafico_distrib_pa_segmento_df_posicao_fiis, use_container_width=True)

        # Reaproveitando fxs de gráfico do df_posicao
        col1, col2 = st.columns(2)
        # Gráfico 6
        with col1:
            grafico_rank_variacao_df_posicao_fiis = _criar_grafico_rank_variacao_df_posicao(df_posicao=df_posicao_fiis)
            with st.container(border=True):
                st.plotly_chart(grafico_rank_variacao_df_posicao_fiis, use_container_width=True)
        # Gráfico 7
        with col2:
            grafico_rank_tir_df_posicao_fiis = _criar_grafico_rank_tir_df_posicao(df_posicao=df_posicao_fiis)
            with st.container(border=True):
                st.plotly_chart(grafico_rank_tir_df_posicao_fiis, use_container_width=True)