import streamlit as st

from icones import *


# -------------------------------------------------------------------------------------------------------------------------
st.title(f'{ICONE_INICIO} {TITULO_INICIO}', text_alignment='center')
st.markdown("---")



# ------------------------------------------------------------------------------------------------------------ Info
col1, _ = st.columns([1.2, 0.8])
with col1:
    with st.expander(f' {ICONE_INFO} Sobre o CarteiraPro'):
        st.markdown(f"""
        ### 🎯 **Objetivos Principais:**
        - ✅ **Consolidar** sua carteira de investimentos ({ICONE_ANALISE_CARTEIRA} {TITULO_ANALISE_CARTEIRA})
        - 📊 **Disponibilizar** dados e análises para auxiliar nas decisões
        
        ### ⚙️ **Premissas Atuais:**
        - 🔓 **Independência:** Sem APIs pagas ou servidores externos
        - 🎨 **Foco:** Back-end priorizado sobre front-end (por enquanto)
        
        ### 🚀 **Implementações Futuras:**
        - 📈 **Mercado:** Indicadores financeiros em tempo real
        - 🏆 **Ranking:** Screening de Ações e FIIs
        - 🧮 **Preços:** Cálculo de preço teto para Ações e FIIs de tijolo
        - 📋 **FIIs:** Visualização customizada do Informe Mensal Estruturado
        - 🏦 **Renda Fixa:** Análise completa
        """)