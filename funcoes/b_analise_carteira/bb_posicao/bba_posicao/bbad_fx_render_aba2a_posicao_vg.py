import streamlit as st

from icones import (
    # Cabeçário
    TITULO_ANALISE_CARTEIRA, ICONE_ANALISE_CARTEIRA,
    # Abas principais
    TITULO_POSICAO, ICONE_POSICAO,
    # Sub-abas (1. Extrato não tem)
    TITULO_VISAO_GERAL, ICONE_VISAO_GERAL,
    # Expanders das abas e sub-abas
    TITULO_INDICADORES, ICONE_INDICADORES, TITULO_GRAFICOS, ICONE_GRAFICOS,
    # Indicadores Posição
    TITULO_INDICADOR_QTD_ATIVOS, ICONE_INDICADOR_QTD_ATIVOS, 
    TITULO_INDICADOR_QTD_TIPOS_ATIVOS_VG, ICONE_INDICADOR_QTD_TIPOS_ATIVOS_VG,
    TITULO_INDICADOR_CM, ICONE_INDICADOR_CM, TITULO_INDICADOR_PA, ICONE_INDICADOR_PA,
    TITULO_INDICADOR_VAR_PERCENTUAL, ICONE_INDICADOR_VAR_PERCENTUAL, TITULO_INDICADOR_VAR_ABSOLUTA, ICONE_INDICADOR_VAR_ABSOLUTA,
    TITULO_INDICADOR_REMUNERACOES, ICONE_INDICADOR_REMUNERACOES, TITULO_INDICADOR_RES_VENAS, ICONE_INDICADOR_RES_VENDAS,
    TITULO_INDICADOR_PERF_ABSOLUTA, ICONE_INDICADOR_PERF_ABSOLUTA, TITULO_INDICADOR_TIR, ICONE_INDICADOR_TIR
)
from funcoes._global.fxg_tratamento import g_formatar_valor_grande_indicadores
# 2. Posição
from funcoes.b_analise_carteira.bb_posicao.bba_posicao.bbab_fx_exib_df_posicao import (
    _calc_indicador_qtd_ativos_df_posicao, _calc_indicador_qtd_tipos_ativos_df_posicao,
    _calc_indicador_custo_medio_df_posicao, _calc_indicador_patrimonio_atual_df_posicao,
    _calc_indicador_variacao_percentual_df_posicao, _calc_indicador_variacao_absoluta_df_posicao,
    _calc_indicador_remuneracoes_df_posicao, _calc_indicador_res_vendas_df_posicao,
    _calc_indicador_performance_absoluta_df_posicao, _calc_indicador_tir_df_posicao,
    _exibir_df_posicao
)
from funcoes.b_analise_carteira.bb_posicao.bba_posicao.bbac_fx_graficos_df_posicao import (
    _criar_grafico_distrib_cm_tipo_df_posicao, _criar_grafico_distrib_pa_tipo_df_posicao,
    _criar_grafico_rank_variacao_df_posicao, _criar_grafico_rank_tir_df_posicao
)








def render_aba2a_posicao_vg(df_ext_mov, df_posicao):
    st.markdown(f'#### {ICONE_VISAO_GERAL} {TITULO_VISAO_GERAL}', text_alignment='center')
    st.caption(f'*{ICONE_ANALISE_CARTEIRA} {TITULO_ANALISE_CARTEIRA} > {ICONE_POSICAO} {TITULO_POSICAO} > {ICONE_VISAO_GERAL} {TITULO_VISAO_GERAL}*',
                text_alignment='center')

    # ------------------------------------------------------------------------------------------------------------- Exibindo indicadores do df_posicao
    with st.expander(f'{TITULO_INDICADORES} *{TITULO_POSICAO} > {TITULO_VISAO_GERAL}*',
                        expanded=False, icon=f'{ICONE_INDICADORES}'):
        col1, col2, col3, col4, col5 = st.columns([0.75, 1, 1, 1, 1])
        with col1:
            indicador_qtd_ativos_df_posicao =_calc_indicador_qtd_ativos_df_posicao(df_posicao=df_posicao)
            st.metric(f'{ICONE_INDICADOR_QTD_ATIVOS} {TITULO_INDICADOR_QTD_ATIVOS}',
                        f' {indicador_qtd_ativos_df_posicao:,.0f}', border=True)

            indicador_qtd_tipos_ativos_df_posicao = _calc_indicador_qtd_tipos_ativos_df_posicao(df_posicao=df_posicao)
            st.metric(f'{ICONE_INDICADOR_QTD_TIPOS_ATIVOS_VG} {TITULO_INDICADOR_QTD_TIPOS_ATIVOS_VG}',
                        f'{indicador_qtd_tipos_ativos_df_posicao:,.0f}', border=True)

        with col2:
            indicador_custo_medio_df_posicao =_calc_indicador_custo_medio_df_posicao(df_posicao=df_posicao)
            indicador_custo_medio_df_posicao_fmt = g_formatar_valor_grande_indicadores(indicador_custo_medio_df_posicao)
            st.metric(f'{ICONE_INDICADOR_CM} {TITULO_INDICADOR_CM}',
                        indicador_custo_medio_df_posicao_fmt,
                        border=True,
                        help=f"""
                        R$ {indicador_custo_medio_df_posicao:,.2f}
                        - Soma do valor de todas as compras
                        - Quando há venda, subtrai-se o valor de 'Preço Médio * Qtd Vendida'
                        """
                        )
            
            indicador_patrimonio_atual_df_posicao = _calc_indicador_patrimonio_atual_df_posicao(df_posicao=df_posicao)
            indicador_patrimonio_atual_df_posicao_fmt = g_formatar_valor_grande_indicadores(indicador_patrimonio_atual_df_posicao)
            st.metric(f'{ICONE_INDICADOR_PA} {TITULO_INDICADOR_PA}',
                        indicador_patrimonio_atual_df_posicao_fmt,
                        border=True,
                        help =f"""
                        R$ {indicador_patrimonio_atual_df_posicao:,.2f}\n
                        'Quantidade de Ativos * Cotação Atual'
                        """
                        )
            
        with col3:
            # Fx não usa o df no seu cálculo, mas sim indicadores.
            indicador_variacao_percentual_df_posicao =_calc_indicador_variacao_percentual_df_posicao(
                indicador_patrimonio_atual_df_posicao=indicador_patrimonio_atual_df_posicao,
                indicador_custo_medio_df_posicao=indicador_custo_medio_df_posicao
                )
            st.metric(f'{ICONE_INDICADOR_VAR_PERCENTUAL} {TITULO_INDICADOR_VAR_PERCENTUAL}',
                        f'{indicador_variacao_percentual_df_posicao:,.2f}%', border=True,
                        help="""
                        Diferença entre Cotação Atual e Preço Médio
                        """
                        )
            
            indicador_variacao_absoluta_df_posicao = _calc_indicador_variacao_absoluta_df_posicao(df_posicao=df_posicao)
            indicador_variacao_absoluta_df_posicao_fmt = g_formatar_valor_grande_indicadores(indicador_variacao_absoluta_df_posicao)
            st.metric(f'{ICONE_INDICADOR_VAR_ABSOLUTA} {TITULO_INDICADOR_VAR_ABSOLUTA}',
                        indicador_variacao_absoluta_df_posicao_fmt,
                        border=True,
                        help=f"""
                        R$ {indicador_variacao_absoluta_df_posicao:,.2f}\n
                        Diferença absoluta entre Patrimônio Atual e Custo Médio
                        """
                        )
            
        with col4:
            indicador_remuneracoes_df_posicao =_calc_indicador_remuneracoes_df_posicao(df_posicao=df_posicao)
            indicador_remuneracoes_df_posicao_fmt = g_formatar_valor_grande_indicadores(indicador_remuneracoes_df_posicao)
            st.metric(f'{ICONE_INDICADOR_REMUNERACOES} {TITULO_INDICADOR_REMUNERACOES}',
                        indicador_remuneracoes_df_posicao_fmt,
                        border=True,
                        help=f"""
                        R$ {indicador_remuneracoes_df_posicao:,.2f}\n
                        Soma dos recebimentos de:
                        - Dividendo
                        - Juros Sobre Capital Próprio
                        - Rendimento"""
                        )
            
            indicador_res_vendas_df_posicao = _calc_indicador_res_vendas_df_posicao(df_posicao=df_posicao)
            indicador_res_vendas_df_posicao_fmt = g_formatar_valor_grande_indicadores(indicador_res_vendas_df_posicao)
            st.metric(f'{ICONE_INDICADOR_RES_VENDAS} {TITULO_INDICADOR_RES_VENAS}',
                        indicador_res_vendas_df_posicao_fmt,
                        border=True,
                        help=f"""
                        R$ {indicador_res_vendas_df_posicao:,.2f}\n
                        Saldo dos resultados (lucro ou prejuízo) de todas as operações de vendas
                        """
                        )
    
        with col5:
            indicador_performance_absoluta_df_posicao = _calc_indicador_performance_absoluta_df_posicao(df_posicao=df_posicao)
            indicador_performance_absoluta_df_posicao_fmt = g_formatar_valor_grande_indicadores(indicador_performance_absoluta_df_posicao)
            st.metric(f'{ICONE_INDICADOR_PERF_ABSOLUTA} {TITULO_INDICADOR_PERF_ABSOLUTA}',
                        indicador_performance_absoluta_df_posicao_fmt,
                        border=True,
                        help=f'''
                        R$ {indicador_performance_absoluta_df_posicao:,.2f}\n
                        Saldo dos resultados de:
                        - Variação Absoluta
                        - Remunerações
                        - Resultado de Vendas
                        '''
                        )
            
            indicador_tir_df_posicao = _calc_indicador_tir_df_posicao(
                df_ext_mov=df_ext_mov, indicador_patrimonio_atual_df_posicao=indicador_patrimonio_atual_df_posicao)
            st.metric(f'{ICONE_INDICADOR_TIR} {TITULO_INDICADOR_TIR}',
                        f'{indicador_tir_df_posicao:,.2f}% a.a.', border=True,
                        help='''
                        Calcula a taxa de retorno anual, considerando todas as movimentações do fluxo de caixa da carteira:
                        - Compras [ - ]
                        - Vendas [ + ]
                        - Remunerações [ + ]
                        '''
                        )

    # ------------------------------------------------------------------------------------------------------------- Exibindo df_posicao
    # Recebe df_posicao e retornaa df_posicao_exib
    _exibir_df_posicao(df_posicao=df_posicao)

    # ------------------------------------------------------------------------------------------------------------- Exibindo gráficos do df_posicao
    with st.expander(f'{TITULO_GRAFICOS} *{TITULO_POSICAO} > {TITULO_VISAO_GERAL}*', expanded=False, icon=f'{ICONE_GRAFICOS}'):
        col1, col2 = st.columns(2)
        # Gráfico 1
        with col1:
            grafico_distrib_cm_df_posicao = _criar_grafico_distrib_cm_tipo_df_posicao(df_posicao=df_posicao)
            with st.container(border=True):
                st.plotly_chart(grafico_distrib_cm_df_posicao, use_container_width=True)
        # Gráfico 2
        with col2:
            grafico_distrib_pa_df_posicao = _criar_grafico_distrib_pa_tipo_df_posicao(df_posicao=df_posicao)
            with st.container(border=True):
                st.plotly_chart(grafico_distrib_pa_df_posicao, use_container_width=True)

        col1, col2 = st.columns(2)
        # Gráfico 3
        with col1:
            grafico_rank_variacao_df_posicao = _criar_grafico_rank_variacao_df_posicao(df_posicao=df_posicao)
            with st.container(border=True):
                st.plotly_chart(grafico_rank_variacao_df_posicao, use_container_width=True)
        # Gráfico 4
        with col2:
            grafico_rank_tir_df_posicao = _criar_grafico_rank_tir_df_posicao(df_posicao=df_posicao)
            with st.container(border=True):
                st.plotly_chart(grafico_rank_tir_df_posicao, use_container_width=True)

    return df_posicao