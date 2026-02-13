import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go

# -----------------------------
# Config Streamlit
# -----------------------------
st.set_page_config(page_title="Boxplot UCS - Vale x Geocontrole", layout="wide")

st.title("📦 Boxplots UCS (Tensão de Pico) — Vale x Geocontrole")
st.caption("Lê os arquivos da pasta, calcula pico por ID (Geocontrole) e plota boxplots interativos por cenário.")

# -----------------------------
# Leitura dos arquivos (cache)
# -----------------------------
@st.cache_data(show_spinner=True)
def load_vale(path="testeinacio estatisca.xlsx"):
    df = pd.read_excel(path, engine="openpyxl")
    # Garantias de tipo
    df["Tensão de Pico"] = pd.to_numeric(df["Tensão de Pico"], errors="coerce")
    return df

@st.cache_data(show_spinner=True)
def load_geo_and_peak(path="consolidada.xlsx"):
    df = pd.read_excel(path, engine="openpyxl")
    df["tensao"] = pd.to_numeric(df["tensao"], errors="coerce")
    # PICO por ID = máximo da coluna tensao
    df_peak = df.loc[df.groupby("id")["tensao"].idxmax()].copy().reset_index(drop=True)
    return df, df_peak

def stats_series(s: pd.Series) -> pd.Series:
    s = pd.Series(s).dropna().astype(float)
    return pd.Series({
        "SOMA": int(s.count()),
        "MÉDIA": s.mean(),
        "MEDIANA": s.median(),
        "DESVPAD": s.std(ddof=1),   # amostral
        "MÍNIMO": s.min(),
        "MÁXIMO": s.max()
    })

def fmt_pt(x):
    # Formata números com vírgula e 2 casas
    if pd.isna(x):
        return ""
    return f"{x:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")

# -----------------------------
# Sidebar: arquivos e opções
# -----------------------------
st.sidebar.header("⚙️ Configurações")

vale_path = st.sidebar.text_input("Arquivo Vale", "testeinacio estatisca.xlsx")
geo_path  = st.sidebar.text_input("Arquivo Geocontrole", "consolidada.xlsx")

show_points = st.sidebar.checkbox("Mostrar pontos (jitter) sobre o boxplot", value=True)
jitter = st.sidebar.slider("Jitter (dispersão dos pontos)", 0.0, 0.6, 0.25, 0.05)
point_size = st.sidebar.slider("Tamanho dos pontos", 2, 10, 5, 1)

# -----------------------------
# Carregar dados
# -----------------------------
try:
    df_vale = load_vale(vale_path)
except Exception as e:
    st.error(f"Erro ao ler {vale_path}: {e}")
    st.stop()

try:
    df_geo_raw, df_geo_peak = load_geo_and_peak(geo_path)
except Exception as e:
    st.error(f"Erro ao ler {geo_path}: {e}")
    st.stop()

st.success(f"Vale carregado: {len(df_vale)} linhas | Geocontrole carregado: {len(df_geo_raw)} linhas | Pico por ID: {len(df_geo_peak)} IDs")

# -----------------------------
# Definições de grupos (Vale)
# -----------------------------
GR = [
    "Granito Isotrópico (GRA)",
    "Granito Albítico (GRB)",
    "Granito Albítico Pegmatítico (GRBp)",
    "Granitoide (GRN)"
]

HD_ALL_VALE = [
    "Anfibolito (ANF)",
    "Biotita Xisto (HDB)",
    "Hidrotermalito (HQM)",
    "Hidrotermalito a Anfibólio (HDA)",
    "Hidrotermalito a Granada (HDG)"
]

HD_SEM_HDA = [
    "Anfibolito (ANF)",
    "Biotita Xisto (HDB)",
    "Hidrotermalito (HQM)",
    "Hidrotermalito a Granada (HDG)"
]

HDA_VALE = ["Hidrotermalito a Anfibólio (HDA)"]

# -----------------------------
# Montagem dos 3 cenários (dados brutos)
# -----------------------------
vale_gr = df_vale[df_vale["Litologia"].isin(GR)]["Tensão de Pico"].dropna()
vale_hd_all = df_vale[df_vale["Litologia"].isin(HD_ALL_VALE)]["Tensão de Pico"].dropna()
vale_hd_sem_hda = df_vale[df_vale["Litologia"].isin(HD_SEM_HDA)]["Tensão de Pico"].dropna()
vale_hda = df_vale[df_vale["Litologia"].isin(HDA_VALE)]["Tensão de Pico"].dropna()

geo_peak = df_geo_peak["tensao"].dropna()  # 30 picos (ou quantos IDs existirem)

# Cenário 1: Somente Vale 1
c1 = {
    "Rochas graníticas": vale_gr,
    "Rochas graníticas hidrotermalizadas": vale_hd_all
}

# Cenário 2: Vale x Geocontrole 2 (hidrotermalizadas = Vale(hd_all) + Geo(picos))
c2 = {
    "Rochas graníticas": vale_gr,
    "Rochas graníticas hidrotermalizadas": pd.concat([vale_hd_all.reset_index(drop=True), geo_peak.reset_index(drop=True)], ignore_index=True)
}

# Cenário 3: Vale x Geocontrole 3
# hidrotermalizadas = Vale(hd_sem_hda)
# minério HDA = Vale(hda) + Geo(picos)
c3 = {
    "Rochas graníticas": vale_gr,
    "Rochas graníticas hidrotermalizadas": vale_hd_sem_hda,
    "Minério HDA": pd.concat([vale_hda.reset_index(drop=True), geo_peak.reset_index(drop=True)], ignore_index=True)
}

cenarios = {
    "Somente Vale 1": c1,
    "Vale × Geocontrole 2": c2,
    "Vale × Geocontrole 3": c3
}

scenario = st.selectbox("Selecione o cenário:", list(cenarios.keys()), index=0)
data_groups = cenarios[scenario]

# -----------------------------
# Boxplot interativo (Plotly)
# -----------------------------
fig = go.Figure()

for name, values in data_groups.items():
    values = pd.Series(values).dropna().astype(float)

    fig.add_trace(go.Box(
        y=values,
        name=name,
        boxmean="sd",          # mostra média e ±1 desvio padrão
        boxpoints="outliers" if not show_points else "all",
        jitter=jitter if show_points else 0,
        pointpos=0,
        marker=dict(size=point_size),
        hovertemplate=(
            f"<b>{name}</b><br>"
            "Tensão: %{y:.2f} MPa<br>"
            "<extra></extra>"
        )
    ))

fig.update_layout(
    title=f"Boxplot — {scenario}",
    yaxis_title="Tensão de Pico (MPa)",
    xaxis_title="Grupo",
    height=600
)

st.plotly_chart(fig, use_container_width=True)

# -----------------------------
# Tabela de estatística (EXATA com dados brutos)
# -----------------------------
st.subheader("📊 Estatística calculada a partir dos dados brutos (exata)")

tab = pd.DataFrame({k: stats_series(v) for k, v in data_groups.items()}).T
tab_disp = tab.copy()

for col in ["MÉDIA", "MEDIANA", "DESVPAD", "MÍNIMO", "MÁXIMO"]:
    tab_disp[col] = tab_disp[col].apply(fmt_pt)

tab_disp["SOMA"] = tab_disp["SOMA"].astype(int)

st.dataframe(tab_disp, use_container_width=True)

# -----------------------------
# Extras: mostrar pico por ID e validações
# -----------------------------
with st.expander("🔎 Ver Tensão de Pico por ID (Geocontrole)"):
    st.dataframe(df_geo_peak[["id", "rocha", "tensao"]].sort_values("id"), use_container_width=True)

with st.expander("🧪 Checagens rápidas"):
    st.write(f"IDs Geocontrole (picos): {len(df_geo_peak)}")
    st.write(f"Vale - GR: {len(vale_gr)} | HD (com HDA): {len(vale_hd_all)} | HD (sem HDA): {len(vale_hd_sem_hda)} | HDA Vale: {len(vale_hda)}")
