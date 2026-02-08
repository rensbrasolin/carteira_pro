import streamlit as st

from icones import *
from funcoes._global.fxg_tratamento import g_formatar_valor_grande_indicadores
from funcoes.b_analise_carteira.bc_remuneracoes.bcc_rem_fiis.bccb_fx_exib_df_rem_mensais_fiis import _exibir_df_rem_mensais_fiis
from funcoes.b_analise_carteira.bc_remuneracoes.bca_rem_vg.bcac_fx_graficos_df_rem_mensais_vg import (
    # Reaproveitnado fxs do VG
    # Gráfico 1
    _calc_media_mensal_ult_12_meses_df_rem_mensais_total, _calc_soma_ult_12_meses_df_rem_mensais_total,
    _calc_soma_df_rem_mensais_total,
    # Gráfico 2
    _criar_df_rem_mensais_yonc_carteira,
    _calc_media_mensal_df_rem_mensais_yonc_carteira, _calc_media_mensal_ult_12_meses_df_rem_mensais_yonc_carteira,
    _calc_soma_mensal_ult_12_meses_df_rem_mensais_yonc_carteira, 
    _criar_grafico_rem_mensais_yonc_carteira,
    # Gráfico 3
    _criar_grafico_rem_mensais_yonc_por_ticker,
    # Gráfico 4
    _criar_grafico_rem_mensais_yonc_por_ticker_soma_ult_12_meses
)
from funcoes.b_analise_carteira.bc_remuneracoes.bcc_rem_fiis.bccc_fx_graficos_df_rem_mensais_fiis import (
    # Gráfico 1
    _criar_grafico_rem_mensais_total_fiis_por_segmento,
)

# Recebe o df_posicao_acoes para trazer cols categóricas
def render_aba3c_remuneracoes_fiis(df_ext_pm_apos_compra, df_ext_remuneracoes, df_rem_mensais_fiis, df_posicao_fiis):
    st.markdown(f'#### {ICONE_FIIS} {TITULO_FIIS}', text_alignment='center')
    st.caption(f'*{ICONE_ANALISE_CARTEIRA} {TITULO_ANALISE_CARTEIRA} > {ICONE_REMUNERACOES} {TITULO_REMUNERACOES} > {ICONE_FIIS} {TITULO_FIIS}*',
                text_alignment='center')


    _exibir_df_rem_mensais_fiis(df_rem_mensais_fiis=df_rem_mensais_fiis)

    # ------------------------------------------------------------------------------------------------------------- Exibindo gráficos do df_posicao
    with st.expander(f'{TITULO_GRAFICOS} *{TITULO_REMUNERACOES} > {TITULO_FIIS}*', expanded=False, icon=f'{ICONE_GRAFICOS}'):


        # ------------------------------------------------------------------------------------------------------------- Gráfico 1
        with st.container(border=True):
            # Reaproveitando fxs dos indicadores do VG
            col1, col2, col3 = st.columns([1, 1, 1])
            with col1:
                media_mensal_ult_12_meses_df_rem_mensais_total_fiis = _calc_media_mensal_ult_12_meses_df_rem_mensais_total(df_rem_mensais=df_rem_mensais_fiis)
                media_mensal_rem_mensais_yonc_carteira_acoes_fmt = g_formatar_valor_grande_indicadores(media_mensal_ult_12_meses_df_rem_mensais_total_fiis)
                st.metric('Média Mensal da Carteira (últ. 12 meses)', f'{media_mensal_rem_mensais_yonc_carteira_acoes_fmt}',
                          border=True, help=f'R$ {media_mensal_ult_12_meses_df_rem_mensais_total_fiis:,.2f}')

            with col2:
                soma_ult_12_meses_df_rem_mensais_total_fiis = _calc_soma_ult_12_meses_df_rem_mensais_total(df_rem_mensais=df_rem_mensais_fiis)
                soma_ult_12_meses_df_rem_mensais_total_fiis_fmt = g_formatar_valor_grande_indicadores(
                    soma_ult_12_meses_df_rem_mensais_total_fiis)
                st.metric('Total da Carteira (últ. 12 meses)', f'{soma_ult_12_meses_df_rem_mensais_total_fiis_fmt}',
                         border=True, help=f'R$ {soma_ult_12_meses_df_rem_mensais_total_fiis:,.2f}')

            with col3:
                soma_df_rem_mensais_total_fiis = _calc_soma_df_rem_mensais_total(df_rem_mensais=df_rem_mensais_fiis)
                soma_df_rem_mensais_total_fiis_fmt = g_formatar_valor_grande_indicadores(
                    soma_df_rem_mensais_total_fiis)
                st.metric('Total da Carteira', f'{soma_df_rem_mensais_total_fiis_fmt}',
                         border=True, help=f'R$ {soma_df_rem_mensais_total_fiis:,.2f}')

            grafico_rem_mensais_total_fiis_por_segmento = _criar_grafico_rem_mensais_total_fiis_por_segmento(
                  df_rem_mensais_fiis=df_rem_mensais_fiis, df_posicao_fiis=df_posicao_fiis)
            st.plotly_chart(grafico_rem_mensais_total_fiis_por_segmento, use_container_width=True)


        # ------------------------------------------------------------------------------------------------------------- Gráfico 2 
        # Reaproveitando fxs dos indicadores e gráfico do VG
        with st.container(border=True):
            # Criando df_ext_pm_apos_compra_fiis para entregar apenas ações para a fx de YonC.
            df_ext_pm_apos_compra_fiis = df_ext_pm_apos_compra.loc[df_ext_pm_apos_compra['Tipo de Ativo'].isin(['FII', 'FIAgro', 'FIInfra'])].copy()
            # Criando df_ext_remuneracoes_fiis para entregar apenas ações para a fx de YonC.
            df_ext_remuneracoes_fiis = df_ext_remuneracoes.loc[df_ext_remuneracoes['Tipo de Ativo'].isin(['FII', 'FIAgro', 'FIInfra'])].copy()
            # Reaproveitando fx auxiliar criada no arq de gráficos VG.
            df_rem_mensais_yonc_carteira_fiis = _criar_df_rem_mensais_yonc_carteira(df_ext_pm_apos_compra=df_ext_pm_apos_compra_fiis,
                                                                                     df_ext_remuneracoes=df_ext_remuneracoes_fiis)
            # st.table(df_rem_mensais_yonc_carteira_acoes)
            
            col1, col2, col3 = st.columns([1, 1, 1])
            with col1:
                media_mensal_rem_mensais_yonc_carteira_fiis = _calc_media_mensal_df_rem_mensais_yonc_carteira(
                    df_rem_mensais_yonc_carteira=df_rem_mensais_yonc_carteira_fiis)
                st.metric('Média Mensal (Total)',
                          f'R$ {media_mensal_rem_mensais_yonc_carteira_fiis:,.2f}%',
                            border=True)

            with col2:
                media_mensal_ult_12_meses_df_rem_mensais_yonc_carteira_fiis = _calc_media_mensal_ult_12_meses_df_rem_mensais_yonc_carteira(
                    df_rem_mensais_yonc_carteira=df_rem_mensais_yonc_carteira_fiis)
                st.metric('Média Mensal (últ. 12 meses)',
                          f'R$ {media_mensal_ult_12_meses_df_rem_mensais_yonc_carteira_fiis:,.2f}%', border=True)

            with col3:
                soma_mensal_ult_12_meses_df_rem_mensais_yonc_carteira_fiis = _calc_soma_mensal_ult_12_meses_df_rem_mensais_yonc_carteira(
                    df_rem_mensais_yonc_carteira=df_rem_mensais_yonc_carteira_fiis)
                st.metric('Soma (últ. 12 meses)',
                          f'R$ {soma_mensal_ult_12_meses_df_rem_mensais_yonc_carteira_fiis:,.2f}%', border=True)

            # Para FIIs também vou usar a fx nova de YonC carteira (Realista), que compara o Yield recebido c/ o CM total da
            # carteira, e não com o CM total só dos ativos que pagaram Yield naquele mês, como era na fx antiga (Otimista demais).
            # Apesar que, no caso de FIIs, eles pagam yield todos os meses. Ou seja, de um jeito ou de outro o CM será sempre o total mesmo.
            # Obs.: Nessa fx nova, se eu comprar FIIs após a datacom, não receberei DY no mês seguinte. Mas mesmo não recebendo,
            # a fx irá comparar o DY recebido c/ o CM desses FIIs que comprei e naõ recebi.
            # I.A. me convenceu a usar a nova: Ver analogia no comentário acima da criação da fx.
            grafico_rem_mensais_yonc_carteira_fiis = _criar_grafico_rem_mensais_yonc_carteira(
                df_rem_mensais_yonc_carteira=df_rem_mensais_yonc_carteira_fiis, df_rem_mensais=df_rem_mensais_fiis)
            st.plotly_chart(grafico_rem_mensais_yonc_carteira_fiis, use_container_width=True)


        # ------------------------------------------------------------------------------------------------------------- Gráfico 3
        with st.container(border=True):
            grafico_rem_mensais_yonc_por_ticker_fiis = _criar_grafico_rem_mensais_yonc_por_ticker(df_rem_mensais=df_rem_mensais_fiis)
            st.plotly_chart(grafico_rem_mensais_yonc_por_ticker_fiis, use_container_width=True)

        # ------------------------------------------------------------------------------------------------------------- Gráfico 3
        with st.container(border=True):
            grafico_rem_mensais_yonc_por_ticker_soma_ult_12_meses_fiis = _criar_grafico_rem_mensais_yonc_por_ticker_soma_ult_12_meses(
                df_rem_mensais=df_rem_mensais_fiis)
            st.plotly_chart(grafico_rem_mensais_yonc_por_ticker_soma_ult_12_meses_fiis, use_container_width=True)
