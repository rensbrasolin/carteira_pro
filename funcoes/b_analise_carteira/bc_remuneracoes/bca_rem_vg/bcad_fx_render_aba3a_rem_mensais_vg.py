import streamlit as st

from icones import *
from funcoes._global.fxg_tratamento import g_formatar_valor_grande_indicadores
# from funcoes.b_analise_carteira.bc_remuneracoes.bca_rem_vg.bcaa_fx_cria_df_rem_mensais_vg import (
#     criar_df_ext_pm_apos_compra, criar_df_ext_remuneracoes, criar_df_rem_mensais
#     )
from funcoes.b_analise_carteira.bc_remuneracoes.bca_rem_vg.bcab_fx_exib_df_rem_mensais_vg import _exibir_df_rem_mensais
from funcoes.b_analise_carteira.bc_remuneracoes.bca_rem_vg.bcac_fx_graficos_df_rem_mensais_vg import (
    # Gráfico 1
    _calc_media_mensal_ult_12_meses_df_rem_mensais_total, _calc_soma_ult_12_meses_df_rem_mensais_total,
    _calc_soma_df_rem_mensais_total,
    _criar_grafico_rem_mensais_total_por_tipo,
    # Gráfico 2
    _criar_df_rem_mensais_yonc_carteira,
    _calc_media_mensal_df_rem_mensais_yonc_carteira, _calc_media_mensal_ult_12_meses_df_rem_mensais_yonc_carteira,
    _calc_soma_mensal_ult_12_meses_df_rem_mensais_yonc_carteira, 
    _criar_grafico_rem_mensais_yonc_carteira, 
)


def render_aba3a_remuneracoes_vg(df_ext_pm_apos_compra, df_ext_remuneracoes, df_rem_mensais):
    st.markdown(f'#### {ICONE_VISAO_GERAL} {TITULO_VISAO_GERAL}', text_alignment='center')
    st.caption(f'*{ICONE_ANALISE_CARTEIRA} {TITULO_ANALISE_CARTEIRA} > {ICONE_REMUNERACOES} {TITULO_REMUNERACOES} > {ICONE_VISAO_GERAL} {TITULO_VISAO_GERAL}*',
                text_alignment='center')


    _exibir_df_rem_mensais(df_rem_mensais=df_rem_mensais)

    # ------------------------------------------------------------------------------------------------------------- Exibindo gráficos do df_posicao
    with st.expander(f'{TITULO_GRAFICOS} *{TITULO_REMUNERACOES} > {TITULO_VISAO_GERAL}*', expanded=False, icon=f'{ICONE_GRAFICOS}'):


        # ------------------------------------------------------------------------------------------------------------- Gráfico 1
        with st.container(border=True):
            col1, col2, col3 = st.columns([1, 1, 1])
            with col1:
                media_mensal_rem_mensais_yonc_carteira = _calc_media_mensal_ult_12_meses_df_rem_mensais_total(df_rem_mensais=df_rem_mensais)
                media_mensal_rem_mensais_yonc_carteira_fmt = g_formatar_valor_grande_indicadores(media_mensal_rem_mensais_yonc_carteira)
                st.metric('Média Mensal da Carteira (últ. 12 meses)', f'{media_mensal_rem_mensais_yonc_carteira_fmt}',
                          border=True, help=f'R$ {media_mensal_rem_mensais_yonc_carteira:,.2f}')

            with col2:
                media_mensal_ult_12_meses_df_rem_mensais_yonc_carteira = _calc_soma_ult_12_meses_df_rem_mensais_total(df_rem_mensais=df_rem_mensais)
                media_mensal_ult_12_meses_df_rem_mensais_yonc_carteira_fmt = g_formatar_valor_grande_indicadores(
                    media_mensal_ult_12_meses_df_rem_mensais_yonc_carteira)
                st.metric('Total da Carteira (últ. 12 meses)', f'{media_mensal_ult_12_meses_df_rem_mensais_yonc_carteira_fmt}',
                         border=True, help=f'R$ {media_mensal_ult_12_meses_df_rem_mensais_yonc_carteira:,.2f}')

            with col3:
                soma_mensal_ult_12_meses_df_rem_mensais_yonc_carteira = _calc_soma_df_rem_mensais_total(df_rem_mensais=df_rem_mensais)
                soma_mensal_ult_12_meses_df_rem_mensais_yonc_carteira_fmt = g_formatar_valor_grande_indicadores(
                    soma_mensal_ult_12_meses_df_rem_mensais_yonc_carteira)
                st.metric('Total da Carteira', f'{soma_mensal_ult_12_meses_df_rem_mensais_yonc_carteira_fmt}',
                         border=True, help=f'R$ {soma_mensal_ult_12_meses_df_rem_mensais_yonc_carteira:,.2f}')

            grafico_rem_mensais_total_por_tipo = _criar_grafico_rem_mensais_total_por_tipo(df_rem_mensais)
            st.plotly_chart(grafico_rem_mensais_total_por_tipo, use_container_width=True)



        # ------------------------------------------------------------------------------------------------------------- Gráfico 2
        with st.container(border=True):
            # Fx auxiliar criada no arq de gráficos.
            df_rem_mensais_yonc_carteira = _criar_df_rem_mensais_yonc_carteira(df_ext_pm_apos_compra=df_ext_pm_apos_compra,
                                                                               df_ext_remuneracoes=df_ext_remuneracoes)
            # st.table(df_rem_mensais_yonc_carteira)


            col1, col2, col3 = st.columns([1, 1, 1])
            with col1:
                media_mensal_rem_mensais_yonc_carteira = _calc_media_mensal_df_rem_mensais_yonc_carteira(
                    df_rem_mensais_yonc_carteira=df_rem_mensais_yonc_carteira)
                st.metric('Média Mensal da Carteira (Total)',
                          f'R$ {media_mensal_rem_mensais_yonc_carteira:,.2f}%',
                            border=True)

            with col2:
                media_mensal_ult_12_meses_df_rem_mensais_yonc_carteira = _calc_media_mensal_ult_12_meses_df_rem_mensais_yonc_carteira(
                    df_rem_mensais_yonc_carteira=df_rem_mensais_yonc_carteira)
                st.metric('Média Mensal da Carteira (últ. 12 meses)',
                          f'R$ {media_mensal_ult_12_meses_df_rem_mensais_yonc_carteira:,.2f}%', border=True)

            with col3:
                soma_mensal_ult_12_meses_df_rem_mensais_yonc_carteira = _calc_soma_mensal_ult_12_meses_df_rem_mensais_yonc_carteira(
                    df_rem_mensais_yonc_carteira=df_rem_mensais_yonc_carteira)
                st.metric('Soma da Carteira (últ. 12 meses)',
                          f'R$ {soma_mensal_ult_12_meses_df_rem_mensais_yonc_carteira:,.2f}%', border=True)

            grafico_rem_mensais_yonc_carteira = _criar_grafico_rem_mensais_yonc_carteira(
                df_rem_mensais_yonc_carteira=df_rem_mensais_yonc_carteira, df_rem_mensais=df_rem_mensais)
            st.plotly_chart(grafico_rem_mensais_yonc_carteira, use_container_width=True)