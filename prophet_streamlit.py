import streamlit as st
import yfinance as yf
import pandas as pd
from  plotly import graph_objs as go
from prophet import Prophet
from prophet.plot import plot_plotly,plot_components_plotly
from datetime import date

DATA_INICIO = '2010-01-01'
DATA_FIM = date.today().strftime('%Y-%m-%d')

st.title('Análise de Ações')
#criando a sidebar
st.sidebar.header('Escolha a ação')

n_dias = st.sidebar.slider('Dias de previsão', 30, 365)

def pegar_dados_acoes():
    path = './acoes.csv'
    return pd.read_csv(path,delimiter=';')

df = pegar_dados_acoes()
acao = df['snome']
nome_acao = st.sidebar.selectbox('Escolha uma ação:',acao)

df_acao = df[df['snome'] == nome_acao]
acao_escolhida = df_acao.iloc[0]['sigla_acao'] + '.SA'
acao_escolhida

@st.cache
#função para pegar valores online do yfinance
def pegar_valores_online(sigla_acao):
    df = yf.download(sigla_acao,DATA_INICIO,DATA_FIM)
    df.reset_index(inplace=True)
    return df

df_valores = pegar_valores_online(acao_escolhida)
df_valores

st.subheader('Tabela de valores - '+nome_acao)
st.write(df_valores.tail(10))

#criar graficos de preços
fig = go.Figure()
fig.add_trace(go.Scatter(x=df_valores['Date'],y=df_valores['Open'],name='Abertura',line_color='yellow'))
fig.add_trace(go.Scatter(x=df_valores['Date'],y=df_valores['Close'],name='Fechamento',line_color='blue'))
fig.layout

#fazer a previsão
df_treino = df_valores[['Date','Close']]
df_treino = df_treino.rename(columns={'Date':'ds','Close':'y'})
df_treino

#criar o modelo
modelo = Prophet()
modelo.fit(df_treino)

futuro = modelo.make_future_dataframe(periods=n_dias,freq='b')
previsoes = modelo.predict(futuro)

st.subheader('Previsões')
st.write(previsoes[['ds','yhat','yhat_lower','yhat_upper']].tail(n_dias))

grafico1 = plot_plotly(modelo,previsoes)
st.plotly_chart(grafico1)

grafico2 = plot_components_plotly(modelo,previsoes)
st.plotly_chart(grafico2)