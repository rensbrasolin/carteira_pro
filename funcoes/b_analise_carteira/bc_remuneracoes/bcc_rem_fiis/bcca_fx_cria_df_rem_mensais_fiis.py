




# --------------------------------------------------------------------------------------------------------------------------------  Definindo fxs internas
def _iniciar_df_rem_mensais_fiis(df_rem_mensais):
    
    df_rem_mensais_fiis = df_rem_mensais.copy()

    # Mantendo apenas linhas de Fiis/Fiagros/Fiinfras.
    df_rem_mensais_fiis = df_rem_mensais_fiis.loc[
    df_rem_mensais_fiis[('', 'Tipo')].isin(['FII', 'FIAgro', 'FIInfra'])
    ]

    # Apesar de fazer sentido, não excluir a col 'Tipo' aqui,
    # pois qdo o df_rem_(tipo) for entregue a fx _desmembrar_df_rem_mensais
    # ele precisará estar com a estrutura do df_rem_vg (Cols Tipo e Ativo). 
    # Será excluída só na fx que exibe o df.
    

    return df_rem_mensais_fiis



# _______________________________ Parte 2: Criar colunas fora do df_rem_mensais e trazê-las.
# Diferente de Posições, em Remunerações não vou trazer dados categóricos para o df_rem_mensais_...
# pois não faz muto sentido, já que é um df multi-índice com muitas colunas. 
# Vou trazer dados categóricos apenas para as fxs de gráfico, que usarão dfs mono-índice. 
# Mas não vou trazer de fora, como quando criei os dfs_posicao por tipo de ativo. Aqui em
# Remunerações vou trazer os dados categóricos do df_posicao respectivo.









# --------------------------------------------------------------------------------------------------------------------- FX principal que cria o df_rem_mensais_fiis
def criar_df_rem_mensais_fiis(df_rem_mensais):

    df_rem_mensais_fiis = _iniciar_df_rem_mensais_fiis(df_rem_mensais=df_rem_mensais)






    return df_rem_mensais_fiis