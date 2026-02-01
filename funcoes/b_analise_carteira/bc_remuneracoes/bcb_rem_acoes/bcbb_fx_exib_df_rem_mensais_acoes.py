import streamlit as st

from icones import *


# ---------------------------------------------------------------------------------------------------------- Fxs Indicadores
# Provavelmente não terão indicadores gerais para Remunerações. Terão indicadores em cada gráfico.

# ---------------------------------------------------------------------------------------------------- Exibição do df principal
# Diferente do df_ext_mov, aqui se exibe só o df. Devido a ter mais complexidade nos cálculos dos indicadores. Não há filtros.
def _exibir_df_rem_mensais_acoes(df_rem_mensais_acoes):

    df_rem_mensais_acoes_exib = df_rem_mensais_acoes.copy()

    # Excluindo cols desnecessárias na hora certa.
    df_rem_mensais_acoes_exib = df_rem_mensais_acoes_exib.drop(
        columns=[('', 'Tipo')])

    # ______________________________________________________________________________________DF
    # Defina EXATAMENTE como cada coluna deve ser formatada
    COLUMN_CONFIG = {  
        # VALORES MONETÁRIOS 
        'Unitário': st.column_config.NumberColumn("Unitário", format="dollar"), # R$     %.2f
        'Total': st.column_config.NumberColumn("Total", format="dollar"), #localized      
        
        # PERCENTUAIS
        'YonC': st.column_config.NumberColumn("YonC", format="%.2f%%"),
    }

    # # Mostrar
    # lista_ordem_cols = []  

    with st.expander(f'{TITULO_DADOS} *{TITULO_REMUNERACOES} > {TITULO_ACOES}*', expanded=False, icon=f'{ICONE_DADOS}'):
        st.dataframe(
            df_rem_mensais_acoes_exib,
            # column_order=lista_ordem_cols,
            column_config=COLUMN_CONFIG, # É por aqui que vou conseguir criar cols com imagem e gráfico. Ver na doc do st.
            use_container_width=True,
            hide_index=True
        )