# bibliotecas
import streamlit as st
import pandas as pd

# Ler dados
df = pd.read_csv("dados.csv")

# Título
st.title("Dashboard Veicular")

# Métricas
vel_media = df['velocidade'].mean()
rpm_media = df['rpm'].mean()

st.metric("Velocidade Média", f"{vel_media:.2f} km/h")
st.metric("RPM Médio", f"{rpm_media:.0f}")

# Análise
df['variacao_velocidade'] = df['velocidade'].diff()

aceleracao_brusca = df[df['variacao_velocidade'] > 15]
freada_forte = df[df['variacao_velocidade'] < -15]

score = 100
score -= len(aceleracao_brusca) * 5
score -= len(freada_forte) * 5

st.metric("Score de Direção", score)

# Filtro
vel_min = st.slider("Velocidade mínima", 0, 150, 0)
df_filtrado = df[df['velocidade'] >= vel_min]

# Gráfico
st.subheader("Velocidade ao longo do tempo")
st.line_chart(df_filtrado.set_index('tempo')['velocidade'])

# Tabela
st.write(df_filtrado)