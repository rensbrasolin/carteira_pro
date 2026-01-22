import streamlit as st
import pandas as pd

# ---------------------------------------------------------------------------------------------------- Filtros
# Fxs criam o widget para obter o input e depois aplicam o filtro no df.

def g_filtro_col_data(df, coluna_data, posicao, nome_df):

    # Encontrar datas mínima e máxima
    data_min = df[coluna_data].min().date()
    data_max = df[coluna_data].max().date()
    

    if posicao == 'vertical':
            data_inicio = st.date_input(
                "Data inicial",
                value=None, # data_min
                min_value=data_min,
                max_value=data_max,
                format="DD/MM/YYYY",
                key=f"filtro_{nome_df}_{coluna_data}_inicio"
            )
            data_fim = st.date_input(
                "Data final",
                value=None, # data_max
                min_value=data_min if data_inicio else data_min,
                max_value=data_max,
                format="DD/MM/YYYY",
                key=f"filtro_{nome_df}_{coluna_data}_fim"
            )

    elif posicao == 'horizontal':
        # Criar filtros side-by-side
        col1, col2 = st.columns(2)
        with col1:
            data_inicio = st.date_input(
                "Data inicial",
                value=None, # data_min
                min_value=data_min,
                max_value=data_max,
                format="DD/MM/YYYY",
                key=f"filtro_{nome_df}_{coluna_data}_inicio"
            )
            
        with col2:
            data_fim = st.date_input(
                "Data final",
                value=None, # data_max
                min_value=data_min if data_inicio else data_min,
                max_value=data_max,
                format="DD/MM/YYYY",
                key=f"filtro_{nome_df}_{coluna_data}_fim"
            )


    if data_inicio and data_fim:
        # Aplicar filtro
        filtro = (
            (pd.to_datetime(df["Data"]) >= pd.to_datetime(data_inicio)) &
            (pd.to_datetime(df["Data"]) <= pd.to_datetime(data_fim))
        )
        return df[filtro]
    else: # Se os 2 campos estiverem vazios, mostra df sem filtros.
        return df

# Filtros hierárquicos: Defina os filtros em sequência. Nunca defina um filtro anterior a algum filtro já definido.
def g_filtro_col_string(df, coluna_string, nome_df):

    # Obter valores únicos da coluna, ordenados
    valores_unicos = sorted(df[coluna_string].dropna().unique())
    
    # Adicionar opção 'Todos'
    opcoes = ['Todos'] + valores_unicos
    
    # Criar multiselect para filtro
    valores_selecionados = st.multiselect(
        f"{coluna_string}",
        options=opcoes,
        default=None,  # Acho mais bonito começar vazio do que com ['Todos']
        key=f"filtro_{nome_df}_{coluna_string}"
    )
    
    # Aplicar filtro
    if 'Todos' in valores_selecionados or not valores_selecionados:
        # Se 'Todos' estiver selecionado OU se nenhum item estiver selecionado
        # Retornar DataFrame completo (sem filtro)
        return df
    else:
        # Filtrar pelos valores específicos selecionados
        filtro = df[coluna_string].isin(valores_selecionados)
        return df[filtro]







# Fiz pensando em ter botões para aplicar/limpar filtros. No caso não poderiam ser fxs globais como as acima.
# Teria que ser fx específica para o caso. Mas teria muita lógica para muito botão e precisaria salbar em session_st.
# Preferi simplificar e desisti de fazer dessa forma.
# Se fx for ser usada, tem que tirar daqui, pois ela é específica e não global.
def SEMUSO_form_filtro(df):
    """
    Filtro com formulário que inicia com campos vazios.
    Se campos estiverem vazios, mostra DataFrame original.
    """
    
    with st.form("form_filtro", clear_on_submit=True):
        data_min = df['Data'].min().date()
        data_max = df['Data'].max().date()
        
        # Campos iniciam vazios (None)
        data_inicio = st.date_input(
            "Data inicial",
            value=None,  # Vazio inicialmente
            min_value=data_min,
            max_value=data_max,
            format="DD/MM/YYYY",
            key="filtro_inicio_vazio"
        )
        
        data_fim = st.date_input(
            "Data final",
            value=None,  # Vazio inicialmente
            min_value=data_min if data_inicio else data_min,
            max_value=data_max,
            format="DD/MM/YYYY",
            key="filtro_fim_vazio"
        )
        
        # Botão para aplicar filtro
        aplicado = st.form_submit_button("Aplicar Filtro")
        
        # Se o botão foi clicado OU já temos datas preenchidas
        if aplicado or data_inicio or data_fim:
            # Se AMBOS estiverem preenchidos, aplica filtro
            if data_inicio and data_fim:
                filtro = (
                    (pd.to_datetime(df["Data"]) >= pd.to_datetime(data_inicio)) &
                    (pd.to_datetime(df["Data"]) <= pd.to_datetime(data_fim))
                )
                return df[filtro]
            # Se APENAS UM estiver preenchido, mostra mensagem e retorna original
            elif data_inicio or data_fim:
                st.warning("⚠️ Preencha ambas as datas para aplicar o filtro.")
                return df
    
    # Se chegou aqui (campos vazios e botão não clicado), retorna original
    return df