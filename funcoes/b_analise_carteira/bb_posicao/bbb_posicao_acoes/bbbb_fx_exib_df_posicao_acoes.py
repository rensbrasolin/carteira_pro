import streamlit as st

from icones import TITULO_DADOS, TITULO_POSICAO, TITULO_ACOES, ICONE_DADOS


# --------------------------------------------------------------------------------------------------- Fxs Indicadores
# Aqui nos indicadores do df_posicao_acoes vou reaproveitar a maioria das fxs do df_posicao,
#  mudando apenas o df que passo para elas.

def _calc_indicador_qtd_setores_df_posicao_acoes(df_posicao_acoes):

    # Excluindo posições zeradas do df
    df_posicao_acoes_sem_pos_liquidada = df_posicao_acoes[df_posicao_acoes['Qtd'] != 0]

    indicador_qtd_setores_df_posicao_acoes = df_posicao_acoes_sem_pos_liquidada['Setor'].nunique()

    return indicador_qtd_setores_df_posicao_acoes






# ---------------------------------------------------------------------------------------------------- Exibição do df principal
# Diferente do df_ext_mov, aqui se exibe só o df. Devido a ter mais complexidade nos cálculos dos indicadores. Não há filtros.
def _exibir_df_posicao_acoes(df_posicao_acoes):

    df_posicao_acoes_exib = df_posicao_acoes.copy()

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
                         'Variação %', 'Variação $', 'Remunerações', 'Resultado de Vendas', 'Performance $', 'TIR',
                         'Setor', 'Controle Acionário',
                         ]  

    with st.expander(f'{TITULO_DADOS} *{TITULO_POSICAO} > {TITULO_ACOES}*', expanded=False, icon=f'{ICONE_DADOS}'):
        st.dataframe(
            df_posicao_acoes_exib,
            column_order=lista_ordem_cols,
            column_config=COLUMN_CONFIG, # É por aqui que vou conseguir criar cols com imagem e gráfico. Ver na doc do st.
            use_container_width=True,
            hide_index=True
        )