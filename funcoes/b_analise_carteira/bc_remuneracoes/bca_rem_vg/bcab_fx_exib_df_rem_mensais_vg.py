import streamlit as st
# import pandas as pd
# from datetime import date, timedelta
# import numpy as np

from icones import TITULO_DADOS, TITULO_REMUNERACOES, TITULO_VISAO_GERAL, ICONE_DADOS


# ---------------------------------------------------------------------------------------------------------- Fxs Indicadores
# Provavelmente não terão indicadores gerais para Remunerações. Terão indicadores em cada gráfico.

# ---------------------------------------------------------------------------------------------------- Exibição do df principal
# Diferente do df_ext_mov, aqui se exibe só o df. Devido a ter mais complexidade nos cálculos dos indicadores. Não há filtros.
def _exibir_df_rem_mensais(df_rem_mensais):

    df_rem_mensais_exib = df_rem_mensais.copy()

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

    with st.expander(f'{TITULO_DADOS} *{TITULO_REMUNERACOES} > {TITULO_VISAO_GERAL}*', expanded=False, icon=f'{ICONE_DADOS}'):
        st.dataframe(
            df_rem_mensais_exib,
            # column_order=lista_ordem_cols,
            column_config=COLUMN_CONFIG, # É por aqui que vou conseguir criar cols com imagem e gráfico. Ver na doc do st.
            use_container_width=True,
            hide_index=True
        )