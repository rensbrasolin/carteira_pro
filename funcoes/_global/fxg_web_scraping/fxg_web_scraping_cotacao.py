import streamlit as st
import pandas as pd
import requests
import json
from time import sleep


# Retorna df ticker-preço. Poderia retornar um dict pra deixar mais leve. Mas não acho que seja pra tanto. 
# De início vou trabalhar com as fxs separadas. No futuro, se precisar, posso fazer uma só fx que busca em várias fontes.
# Vou deixar os códigos das outras fxs de cotação em um NB. Assim, caso precise delas, posso testar lá antes de trazer.

@st.cache_data
def g_criar_df_cotacao_tvb3(df_ext_mov_fin):

    # Obtendo os valores únicos da coluna 'ATIVO' e convertendo em uma lista
    lista_tickers_validos = df_ext_mov_fin['Ticker'].unique().tolist()

    url = "https://scanner.tradingview.com/brazil/scan"

    headers = {
        "User-Agent": "Mozilla/5.0",
        "Content-Type": "application/json",
        "Referer": "https://br.tradingview.com/"
    }

    # Lista para armazenar os dados de todos os tickers
    dados = []

    for ticker in lista_tickers_validos:
        payload = {
            "symbols": {
                "tickers": [f"BMFBOVESPA:{ticker}"],  # Pode colocar BBAS3, PETR4, etc
                "query": {"types": []}
            },
            "columns": ["close", "name"]  # Aqui consigo pegar mais dados, preenchendo o nome dele aqui conforme doc API
        }

        response = requests.post(url, headers=headers, data=json.dumps(payload))
        data = response.json()

        try:
            # Atribuindo os dados pegos a variáveis
            resultados = data['data'][0]['d']
            preco_atual = resultados[0]
            # nome = resultados[1] # Se quiser usar depois
        except (IndexError, KeyError, TypeError):
            # Se não encontrar o ativo ou algo der errado, preenche com None
            preco_atual = None
            # nome = None

        # Adicionando à lista de dados para o DataFrame
        dados.append({
            "Ticker": ticker,
            "Cotação": preco_atual
            # "Nome": nome  # Caso queira incluir, é só descomentar
        })

        sleep(0.75) # Talvez usar 1.0 ****

    return pd.DataFrame(dados)

