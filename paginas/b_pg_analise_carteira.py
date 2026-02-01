import streamlit as st

from icones import *
# 1. Extrato
from funcoes.b_analise_carteira.ba_extrato_movimentacoes.baa_fx_cria_df_ext_mov import carregar_arquivos, criar_df_ext_mov
from funcoes.b_analise_carteira.ba_extrato_movimentacoes.bab_fx_exib_df_ext_mov import exibir_df_ext_mov
from funcoes.b_analise_carteira.ba_extrato_movimentacoes.bac_fx_graficos_df_ext_mov import (
    criar_grafico_compras_vendas_12m_df_ext_mov, criar_grafico_preco_compras_df_ext_mov
)
# 2a. Posição VG
from funcoes.b_analise_carteira.bb_posicao.bba_posicao_vg.bbaa_fx_cria_df_posicao_vg import criar_df_posicao
from funcoes.b_analise_carteira.bb_posicao.bba_posicao_vg.bbad_fx_render_aba2a_posicao_vg import render_aba2a_posicao_vg
# 2b. Posição Ações
from funcoes.b_analise_carteira.bb_posicao.bbb_posicao_acoes.bbba_fx_cria_df_posicao_acoes import criar_df_posicao_acoes
from funcoes.b_analise_carteira.bb_posicao.bbb_posicao_acoes.bbbd_fx_render_aba2b_posicao_acoes import render_aba2b_posicao_acoes
# 2c. Posição FIIs
from funcoes.b_analise_carteira.bb_posicao.bbc_posicao_fiis.bbca_fx_cria_df_posicao_fiis import criar_df_posicao_fiis
from funcoes.b_analise_carteira.bb_posicao.bbc_posicao_fiis.bbcd_fx_render_aba2c_posicao_fiis import render_aba2c_posicao_fiis
# 2d. Posição ETFs
from funcoes.b_analise_carteira.bb_posicao.bbd_posicao_etfs.bbda_fx_cria_df_posicao_etfs import criar_df_posicao_etfs
from funcoes.b_analise_carteira.bb_posicao.bbd_posicao_etfs.bbdd_fx_render_aba2d_posicao_etfs import render_aba2d_posicao_etfs
# 3a. Remunerações VG
from funcoes.b_analise_carteira.bc_remuneracoes.bca_rem_vg.bcaa_fx_cria_df_rem_mensais_vg import (
    criar_df_ext_pm_apos_compra, criar_df_ext_remuneracoes, criar_df_rem_mensais
)
from funcoes.b_analise_carteira.bc_remuneracoes.bca_rem_vg.bcad_fx_render_aba3a_rem_mensais_vg import render_aba3a_remuneracoes_vg
# 3b. Remunerações Ações
from funcoes.b_analise_carteira.bc_remuneracoes.bcb_rem_acoes.bcba_fx_cria_df_rem_mensais_acoes import criar_df_rem_mensais_acoes
from funcoes.b_analise_carteira.bc_remuneracoes.bcb_rem_acoes.bcbd_fx_render_aba3b_rem_mensais_acoes import render_aba3b_remuneracoes_acoes




st.header(f'{ICONE_ANALISE_CARTEIRA} {TITULO_ANALISE_CARTEIRA}', text_alignment='left')
st.markdown("---")
# ------------------------------------------------------------------------------------------------------------ Obtendo dados
# col1, col2 = st.columns([1, 1])
# with col1:
arquivos = carregar_arquivos() # TRATAR ERRO SE CARREGAR ARQUIVO QUE NAO TEM ESTRUTURA DO EXTRATO.

# st.markdown("---")
# If para só carregar toda a análise se tiver subido extrato.
# Todu o resto do cód tem que estar dentro desse if, obrigatoriamente. Sem df_mov não há Análise da carteira.
if arquivos:

    aba1_ext_mov, aba2_posicao, aba3_remuneracoes, = st.tabs([
        f'{ICONE_EXTRATO} {TITULO_EXTRATO}',
        f'{ICONE_POSICAO} {TITULO_POSICAO}',
        f'{ICONE_REMUNERACOES} {TITULO_REMUNERACOES}'
        ])

    # ******************************************************************************************************************************************** aba_ext_mov
    with aba1_ext_mov:
        st.subheader(f'{ICONE_EXTRATO} {TITULO_EXTRATO}', text_alignment='center')
        st.caption(f'*{ICONE_ANALISE_CARTEIRA} {TITULO_ANALISE_CARTEIRA} > {ICONE_EXTRATO} {TITULO_EXTRATO}*', text_alignment='center')
        # st.markdown("---")

        # ------------------------------------------------------------------------------------------------------------ Criando df_ext_mov
        df_ext_mov = criar_df_ext_mov(arquivos)

        # ------------------------------------------------------------------------------------------------------------- Exibindo métricas e df_ext_mov
        # Recebe df_ext_mov e retornaa df_ext_mov_exib
        exibir_df_ext_mov(df_ext_mov=df_ext_mov)

        # ------------------------------------------------------------------------------------------------------------- Exibindo gráficos do df_ext_mov
        with st.expander(f'{TITULO_GRAFICOS} *{TITULO_EXTRATO}*', expanded=False, icon=f'{ICONE_GRAFICOS}'):
            # Criar o gráfico
            grafico_distrib_cm_df_posicao = criar_grafico_preco_compras_df_ext_mov(df_ext_mov=df_ext_mov)
            with st.container(border=True):
                # Exibir o gráfico no Streamlit
                st.plotly_chart(grafico_distrib_cm_df_posicao, use_container_width=True)

            with st.container(border=True):
                grafico_compras_vendas_12m_df_ext_mov = criar_grafico_compras_vendas_12m_df_ext_mov(df_ext_mov=df_ext_mov)
                st.plotly_chart(grafico_compras_vendas_12m_df_ext_mov, use_container_width=True)


    # ******************************************************************************************************************************************** aba_posicao
    with aba2_posicao:
        st.subheader(f'{ICONE_POSICAO} {TITULO_POSICAO}', text_alignment='center')
        st.caption(f'*{ICONE_ANALISE_CARTEIRA} {TITULO_ANALISE_CARTEIRA} > {ICONE_POSICAO} {TITULO_POSICAO}*', text_alignment='center')

        aba2a_posicao_vg, aba2b_posicao_acoes, aba2c_posicao_fiis, aba2d_posicao_etfs = st.tabs([
            f"{ICONE_VISAO_GERAL} {TITULO_VISAO_GERAL}",
            f"{ICONE_ACOES} {TITULO_ACOES}",
            f"{ICONE_FIIS} {TITULO_FIIS}",
            f"{ICONE_ETFS} {TITULO_ETFS}"
            ])


        with aba2a_posicao_vg:
            # ------------------------------------------------------------------------------------------------------------ Criando df_posicao
            # Crio o df direto aqui na pag e não dentro da fx render pq ele precisa ser entregue para as próximas abas
            # A regra da fx render é: Se criar variáveis dentro dela, usá-las la dentro. Pois ela não deve retornar nada
            df_ext_pm_apos_compra = criar_df_posicao(df_ext_mov=df_ext_mov)

            # ------------------------------------------------------------------------------------- Exibindo indicadores, df_posicao e gráficos
            # A regra da fx render é: Se criar variáveis dentro dela, usá-las la dentro. Pois ela não deve retornar nada
            render_aba2a_posicao_vg(df_ext_mov=df_ext_mov, df_posicao=df_ext_pm_apos_compra)


        with aba2b_posicao_acoes:
            # ------------------------------------------------------------------------------------------------------------ Criando df_posicao_acoes
            df_posicao_acoes = criar_df_posicao_acoes(df_posicao=df_ext_pm_apos_compra)
            
            # ------------------------------------------------------------------------------------- Exibindo indicadores, df_posicao_acoes e gráficos
            render_aba2b_posicao_acoes(df_ext_mov=df_ext_mov, df_posicao_acoes=df_posicao_acoes)


        with aba2c_posicao_fiis:
            # ------------------------------------------------------------------------------------------------------------ Criando df_posicao_fiis
            df_posicao_fiis = criar_df_posicao_fiis(df_posicao=df_ext_pm_apos_compra)

            # ------------------------------------------------------------------------------------- Exibindo indicadores, df_posicao_fiis e gráficos
            render_aba2c_posicao_fiis(df_ext_mov=df_ext_mov, df_posicao_fiis=df_posicao_fiis)


        with aba2d_posicao_etfs:
            # ------------------------------------------------------------------------------------------------------------ Criando df_posicao_fiis
            df_posicao_etfs = criar_df_posicao_etfs(df_posicao=df_ext_pm_apos_compra)

            # ------------------------------------------------------------------------------------- Exibindo indicadores, df_posicao_fiis e gráficos
            render_aba2d_posicao_etfs(df_ext_mov=df_ext_mov, df_posicao_etfs=df_posicao_etfs)











    # ******************************************************************************************************************************************** aba_remuneracoes
    with aba3_remuneracoes:
        st.subheader(f'{ICONE_REMUNERACOES} {TITULO_REMUNERACOES}', text_alignment='center')
        st.caption(f'*{ICONE_ANALISE_CARTEIRA} {TITULO_ANALISE_CARTEIRA} > {ICONE_REMUNERACOES} {TITULO_REMUNERACOES}*', text_alignment='center')

        aba3a_remuneracoes_vg, aba3b_remuneracoes_acoes, aba3c_remuneracoes_fiis, aba3d_remuneracoes_etfs = st.tabs([
            f"{ICONE_VISAO_GERAL} {TITULO_VISAO_GERAL}",
            f"{ICONE_ACOES} {TITULO_ACOES}",
            f"{ICONE_FIIS} {TITULO_FIIS}",
            f"{ICONE_ETFS} {TITULO_ETFS}"
            ])


        with aba3a_remuneracoes_vg:
            # ------------------------------------------------------------------------------------------------ 1. Criando dfs para se chegar no df final
            df_ext_pm_apos_compra = criar_df_ext_pm_apos_compra(df_ext_mov=df_ext_mov)
            df_ext_remuneracoes = criar_df_ext_remuneracoes(df_ext_mov=df_ext_mov, df_ext_pm_apos_compra=df_ext_pm_apos_compra)
            df_rem_mensais = criar_df_rem_mensais(df_ext_remuneracoes=df_ext_remuneracoes)

            # ------------------------------------------------------------------------------------- Exibindo indicadores, df_posicao_fiis e gráficos
            # Também entrega o df_ext_remuneracoes e df_ext_pm_apos_compra p/ poder criar o df_rem_mensais_yonc_carteira que será entregue a fx de grafico
            render_aba3a_remuneracoes_vg(df_ext_pm_apos_compra=df_ext_pm_apos_compra,
                                         df_ext_remuneracoes=df_ext_remuneracoes,
                                         df_rem_mensais=df_rem_mensais)


        with aba3b_remuneracoes_acoes:
            # ------------------------------------------------------------------------------------------------ 1. Criando df_rem_mensais_acoes
            df_rem_mensais_acoes = criar_df_rem_mensais_acoes(df_rem_mensais=df_rem_mensais)


            # ------------------------------------------------------------------------------------- Exibindo indicadores, df_posicao_fiis e gráficos
            # Recebe o df_posicao_acoes para trazer cols categóricas
            render_aba3b_remuneracoes_acoes(df_ext_pm_apos_compra=df_ext_pm_apos_compra, df_ext_remuneracoes=df_ext_remuneracoes, 
                                            df_rem_mensais_acoes=df_rem_mensais_acoes, df_posicao_acoes=df_posicao_acoes)
            





        # # Teste:
        # from funcoes.b_analise_carteira.bc_remuneracoes.bca_rem_vg.bcac_fx_graficos_df_rem_mensais_vg import _desmembrar_df_rem_mensais
        # # Obtendo o df que preciso
        # _, _, df_rem_mensais_yonc = _desmembrar_df_rem_mensais(df_rem_mensais)
        # st.dataframe(df_rem_mensais_yonc)