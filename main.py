import streamlit as st

from icones import TITULO_APP, ICONE_APP, TITULO_INICIO, ICONE_INICIO, TITULO_ANALISE_CARTEIRA, ICONE_ANALISE_CARTEIRA


# Configurar o layout da página para ocupar toda a largura
st.set_page_config(layout="wide")

# # -------------------------------------------------------------------------------------------------------------------------
# st.title(f'{ICONE_APP} {TITULO_APP}', text_alignment='left')
# st.markdown("---")

# ------------------------------------------------------------------------------------------------------------------- Menu
# Registrar todas as páginas do app no menu. Depois exibir apenas os links necessários na sidebar.
menu = st.navigation(
    pages=
    {
        '# A. Início': [st.Page('paginas/a_pg_inicial.py', title=f'{ICONE_INICIO} {TITULO_INICIO}')], # 

        '# B. Análise da carteira': [
            st.Page('paginas/b_pg_analise_carteira.py', title=f'{ICONE_ANALISE_CARTEIRA} {TITULO_ANALISE_CARTEIRA}')],


        # '# 1. Extrato de Movimentações B3': [
        #     st.Page('paginas/movimentacoes/pg_mov_completo.py', title='- Extrato Completo (a+b)'),
        #     st.Page('paginas/movimentacoes/pg_mov_financeiras.py', title='- Movimentações Financeiras (a)'),
        #     st.Page('paginas/movimentacoes/pg_mov_eventos.py', title='- Outros Eventos (b)')
        # ],

        # '# 2. Consolidações': [
        #     st.Page('paginas/consolidacoes/pg_consolidacao_carteira.py', title='- Posição Atual'),
        #     st.Page('paginas/consolidacoes/pg_rem.py', title='- Remunerações')
        # ],
    },
        position="hidden"  # ← oculta o menu lateral padrão do Streamlit
)

menu.run()

# Menu do usuário
with st.sidebar:
    st.title(f'{ICONE_APP} {TITULO_APP}', text_alignment='left')
    st.markdown("---")

    # Links diretos para as páginas
    st.page_link("paginas/a_pg_inicial.py", label=f'{ICONE_INICIO} {TITULO_INICIO}',)# icon="")
    st.page_link("paginas/b_pg_analise_carteira.py", label=f'{ICONE_ANALISE_CARTEIRA} {TITULO_ANALISE_CARTEIRA}')


# --------------------------------------------------------------------------------------------------------------- RODAPÉ
# Opção 1: Rodapé fixo no final da janela
st.markdown(
    """
    <style>
    /* 
    RODAPÉ FIXO - ESTILOS CSS
    Este estilo mantém o rodapé sempre visível no final da tela
    */
    .fixed-footer {
        position: fixed;      /* Fixa o elemento na viewport */
        bottom: 0;            /* Cola no fundo da tela */
        right: 0;             /* Alinha à direita */
        left: 0;              /* Ocupa toda a largura */

        /* background-color: white; */  /* Fundo branco para contraste */

        text-align: right;    /* Alinha o texto à direita */
        font-size: 0.6em;     /* Tamanho reduzido da fonte */
        color: #666;          /* Cor cinza médio */
        padding: 10px 20px;   /* Espaçamento interno: 10px top/bottom, 20px left/right */
        
        /* border-top: 1px solid #363636; */  /* Linha divisória no topo */
        /* z-index: 999; */         /* Garante que fique acima de outros elementos */

    }
    </style>
    
    <div class="fixed-footer">
        © 2026 Renato Brasolin | Analista de Dados | renatobrasolin2@gmail.com — Todos os direitos reservados.
    </div>
    """,
    unsafe_allow_html=True
)

