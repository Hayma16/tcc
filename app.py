"""
app.py — Dashboard de Telemetria Veicular
Compatível com dados do Assetto Corsa via coletor_ac.py

Rodar: streamlit run app.py
"""

import streamlit as st
import pandas as pd
import time
import os

st.set_page_config(
    page_title="Telemetria Veicular",
    page_icon="🏎️",
    layout="wide"
)

ARQUIVO = "dados_ac.csv"

COLUNAS = [
    "timestamp", "volta", "tempo_volta_ms", "posicao_pista",
    "velocidade_kmh", "rpm", "marcha",
    "acelerador", "freio", "embreagem",
    "forca_g_lat", "forca_g_lon",
    "temp_pneu_fl", "temp_pneu_fr", "temp_pneu_rl", "temp_pneu_rr",
    "temp_freio_fl", "temp_freio_fr", "temp_freio_rl", "temp_freio_rr",
    "desgaste_pneu_fl", "desgaste_pneu_fr", "desgaste_pneu_rl", "desgaste_pneu_rr",
    "abs_ativo", "tc_ativo", "turbo_boost", "distancia_total_m",
]

# ── Garante que o CSV existe com cabeçalho ──────────────────────────────────
if not os.path.exists(ARQUIVO) or os.path.getsize(ARQUIVO) == 0:
    pd.DataFrame(columns=COLUNAS).to_csv(ARQUIVO, index=False)

# ── ETL: Extração ───────────────────────────────────────────────────────────
@st.cache_data(ttl=2)
def carregar_dados(arquivo):
    df = pd.read_csv(arquivo)

    if df.empty:
        return df

    if "velocidade_kmh" in df.columns:
        df = df.rename(columns={"velocidade_kmh": "velocidade"})

    # Garante que colunas numéricas estão no tipo correto
    cols_numericas = [
        "velocidade", "rpm", "acelerador", "freio", "embreagem",
        "forca_g_lat", "forca_g_lon",
        "temp_pneu_fl", "temp_pneu_fr", "temp_pneu_rl", "temp_pneu_rr",
        "temp_freio_fl", "temp_freio_fr", "temp_freio_rl", "temp_freio_rr",
        "desgaste_pneu_fl", "desgaste_pneu_fr", "desgaste_pneu_rl", "desgaste_pneu_rr",
        "turbo_boost", "distancia_total_m", "posicao_pista",
    ]
    for col in cols_numericas:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors="coerce").fillna(0)

    df["variacao_velocidade"] = df["velocidade"].diff().fillna(0)
    df["aceleracao_brusca"]   = df["variacao_velocidade"] > 15
    df["freada_forte"]        = df["variacao_velocidade"] < -15

    return df

# ── Interface ───────────────────────────────────────────────────────────────
st.title("🏎️ Dashboard de Telemetria Veicular")
st.caption("Dados coletados via Assetto Corsa — Shared Memory API")

# Sidebar
st.sidebar.header("⚙️ Configurações")
auto_refresh = st.sidebar.toggle("🔄 Atualização automática", value=True)
if auto_refresh:
    st.sidebar.caption("Atualizando a cada 2 segundos")

df = carregar_dados(ARQUIVO)

# ── Aguardando dados ────────────────────────────────────────────────────────
if df.empty:
    st.info("⏳ Aguardando dados do Assetto Corsa... Abra o jogo, entre em uma sessão e rode o **coletor_ac.py**.")
    if auto_refresh:
        time.sleep(2)
        st.rerun()
    st.stop()

# Filtro por volta
if "volta" in df.columns and df["volta"].nunique() > 1:
    voltas = ["Todas"] + sorted(df["volta"].unique().tolist())
    volta_sel = st.sidebar.selectbox("Filtrar por volta", voltas)
    if volta_sel != "Todas":
        df = df[df["volta"] == volta_sel]

# Filtro de velocidade
vel_max_val = df["velocidade"].max()
if pd.isna(vel_max_val):
    vel_max_val = 1
vel_max_dados = max(int(vel_max_val), 1)
vel_min, vel_max = st.sidebar.slider(
    "Faixa de velocidade (km/h)", 0, vel_max_dados + 10, (0, vel_max_dados)
)
df_filtrado = df[(df["velocidade"] >= vel_min) & (df["velocidade"] <= vel_max)]

# ── ETL: Carga / Métricas ───────────────────────────────────────────────────
aceleracao_brusca = df[df["aceleracao_brusca"]]
freada_forte      = df[df["freada_forte"]]
score = max(0, 100 - len(aceleracao_brusca) * 5 - len(freada_forte) * 5)
emoji_score, classe = ("🟢","Boa") if score >= 80 else ("🟡","Regular") if score >= 50 else ("🔴","Ruim")

# ── Métricas principais ─────────────────────────────────────────────────────
st.subheader("📊 Métricas Gerais")
c1, c2, c3, c4, c5 = st.columns(5)
c1.metric("Velocidade Média",  f"{df['velocidade'].mean():.1f} km/h")
c2.metric("Velocidade Máxima", f"{df['velocidade'].max():.1f} km/h")
c3.metric("RPM Médio",         f"{df['rpm'].mean():.0f}")
c4.metric("RPM Máximo",        f"{df['rpm'].max():.0f}")
c5.metric(f"Score {emoji_score}", f"{score}/100", delta=classe)

st.divider()

# ── Gráficos de condução ────────────────────────────────────────────────────
st.subheader("📈 Gráficos de Condução")
cg1, cg2 = st.columns(2)
with cg1:
    st.markdown("**Velocidade (km/h)**")
    st.line_chart(df_filtrado["velocidade"], use_container_width=True)
with cg2:
    st.markdown("**RPM do Motor**")
    st.line_chart(df_filtrado["rpm"], use_container_width=True)

# ── Entradas do piloto ──────────────────────────────────────────────────────
if "acelerador" in df.columns:
    st.subheader("🎮 Entradas do Piloto")
    ce1, ce2, ce3 = st.columns(3)
    with ce1:
        st.markdown("**Acelerador (0-1)**")
        st.line_chart(df_filtrado["acelerador"], use_container_width=True)
    with ce2:
        st.markdown("**Freio (0-1)**")
        st.line_chart(df_filtrado["freio"], use_container_width=True)
    with ce3:
        st.markdown("**Marcha**")
        marcha_num = pd.to_numeric(df_filtrado["marcha"], errors="coerce")
        st.line_chart(marcha_num, use_container_width=True)

# ── Forças G ───────────────────────────────────────────────────────────────
if "forca_g_lat" in df.columns:
    st.subheader("⚡ Forças G")
    cf1, cf2 = st.columns(2)
    with cf1:
        st.markdown("**Força G Lateral**")
        st.line_chart(df_filtrado["forca_g_lat"], use_container_width=True)
    with cf2:
        st.markdown("**Força G Longitudinal**")
        st.line_chart(df_filtrado["forca_g_lon"], use_container_width=True)

# ── Temperatura dos pneus ───────────────────────────────────────────────────
if "temp_pneu_fl" in df.columns and len(df) > 0:
    st.subheader("🌡️ Temperatura dos Pneus — último registro (°C)")
    ct1, ct2, ct3, ct4 = st.columns(4)
    ct1.metric("Diant. Esq.", f"{df['temp_pneu_fl'].iloc[-1]:.0f}°C")
    ct2.metric("Diant. Dir.", f"{df['temp_pneu_fr'].iloc[-1]:.0f}°C")
    ct3.metric("Tras. Esq.",  f"{df['temp_pneu_rl'].iloc[-1]:.0f}°C")
    ct4.metric("Tras. Dir.",  f"{df['temp_pneu_rr'].iloc[-1]:.0f}°C")

st.divider()

# ── Eventos detectados ──────────────────────────────────────────────────────
st.subheader("⚠️ Eventos de Condução Detectados")
cev1, cev2 = st.columns(2)

with cev1:
    st.markdown(f"**🚀 Acelerações Bruscas:** {len(aceleracao_brusca)} eventos")
    if not aceleracao_brusca.empty:
        st.dataframe(
            aceleracao_brusca[["velocidade", "variacao_velocidade"]].reset_index(drop=True),
            use_container_width=True, hide_index=True
        )
    else:
        st.success("Nenhuma aceleração brusca detectada!")

with cev2:
    st.markdown(f"**🛑 Freadas Fortes:** {len(freada_forte)} eventos")
    if not freada_forte.empty:
        st.dataframe(
            freada_forte[["velocidade", "variacao_velocidade"]].reset_index(drop=True),
            use_container_width=True, hide_index=True
        )
    else:
        st.success("Nenhuma freada forte detectada!")

st.divider()

# ── Dados brutos ────────────────────────────────────────────────────────────
with st.expander("🗂️ Ver dados brutos"):
    st.dataframe(df_filtrado, use_container_width=True)
    st.caption(f"Total de registros: {len(df_filtrado)}")

# ── Auto-refresh ────────────────────────────────────────────────────────────
if auto_refresh:
    time.sleep(2)
    st.rerun()