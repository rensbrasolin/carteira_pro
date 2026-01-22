import streamlit as st
import pandas as pd


def g_mostrar_tipos_cols(df):
    # Cria mini-tabela só com tipos
    tipos_df = pd.DataFrame({
        'Coluna': df.columns,
        'Tipo': df.dtypes.values
    })
    st.dataframe(tipos_df, hide_index=True, use_container_width=True)
# # Uso
# from funcoes._global.fxg_tratamento import g_mostrar_tipos_cols
# g_mostrar_tipos_cols(df)


def g_aplicar_datetime_cols(df, lista_colunas_data):
    """
    Recebe um df e uma lista de cols string.
    """
    for coluna in lista_colunas_data: # Retirei dayfirst=True pois gerou troca de mes por dia.
        df[coluna] = pd.to_datetime(df[coluna], errors='coerce')

    return df


# Converter as cols numéricas corretamente para substituir o "-" por 0 ou None.
# Comentei o fillna pois ele transforma NaN em 0. Ir vendo com o tempo se é melhor que fique Nan ou 0.
def g_aplicar_to_numeric_cols(df, lista_colunas_numericas):
    """
    Recebe um df e uma lista de cols string.
    """
    for coluna in lista_colunas_numericas:
        df[coluna] = pd.to_numeric(df[coluna], errors='coerce')#.fillna(0)

    return df



def g_excluir_strings_cols(lista_strings_excluir, df, coluna):
    """
    Remove strings específicas de uma coluna do DataFrame.
    
    Para cada valor na coluna especificada, remove todas as ocorrências
    das strings fornecidas na lista, mantendo o restante do conteúdo.
    
    Parâmetros:
    -----------
    lista_strings_excluir : list
        Lista de strings a serem removidas dos valores da coluna
    df : pandas.DataFrame
        DataFrame contendo os dados
    coluna : str
        Nome da coluna onde as strings serão removidas
        
    Retorna:
    --------
    pandas.DataFrame
        DataFrame com as strings removidas da coluna especificada
        
    Exemplo:
    --------
    >>> df = pd.DataFrame({'Produto': ['BANCO DO BRASIL S.A. - BANCO DO BRASIL S.A.',
    ...                                'ITAÚ UNIBANCO S.A. - ITAÚ UNIBANCO S.A.']})
    >>> g_excluir_strings_cols(['S.A.', '-'], df, 'Produto')
    Retorna DataFrame com:
        'BANCO DO BRASIL  BANCO DO BRASIL'
        'ITAÚ UNIBANCO  ITAÚ UNIBANCO'
    """
    
    # Criar cópia do DataFrame para não modificar o original
    df_modificado = df.copy()
    
    # Para cada string na lista de exclusão
    for string_excluir in lista_strings_excluir:
        # Verificar se é string válida
        if not isinstance(string_excluir, str):
            raise TypeError(f"Item '{string_excluir}' não é uma string")
        
        # Remover a string de todos os valores da coluna
        # Usar str.replace() para substituir por string vazia
        df_modificado[coluna] = df_modificado[coluna].astype(str).str.replace(
            string_excluir,           # String a ser removida
            '',                       # Substituir por vazio
            regex=False               # Não usar regex (remover literalmente)
        )
    
    # Opcional: Remover espaços extras que possam ter ficado
    # Substitui múltiplos espaços por um único espaço
    df_modificado[coluna] = df_modificado[coluna].str.replace(
        r'\s+',          # Regex: um ou mais espaços
        ' ',             # Substituir por um único espaço
        regex=True       # Usar regex para múltiplos espaços
    )
    
    # Remover espaços no início e fim das strings
    df_modificado[coluna] = df_modificado[coluna].str.strip()
    
    return df_modificado



def g_formatar_valor_grande_indicadores(valor):
    """
    Formata valores grandes de forma legível.
    Valores < 10k não mostram decimais.
    A partir de 10k, começa a abreviar.
    """
    if valor >= 1_000_000_000:
        return f"R$ {valor/1_000_000_000:.1f}B"
    elif valor >= 1_000_000:
        return f"R$ {valor/1_000_000:.1f}M"
    elif valor >= 10_000:
        return f"R$ {valor/1_000:.1f}K"
    else:
        return f'R$ {valor:,.0f}'.replace(",", "X").replace(".", ",").replace("X", ".")
# # Uso
# valor_formatado = formatar_valor(1250000.50)  # "R$ 1.3M"
# st.metric(f"**💰 Patrimônio:**", valor_formatado)