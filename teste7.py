import streamlit as st
import pandas as pd
import plotly.graph_objects as go


st.set_page_config(page_title="Boxplot UCS - Vale x Geocontrole", layout="wide")

st.title("📦 Boxplots UCS (Tensão de Pico) — Vale x Geocontrole")
st.caption(
    "Lê os arquivos da pasta, calcula pico por ID (Geocontrole) e plota boxplots interativos por cenário."
)


@st.cache_data(show_spinner=True)
def load_vale(path: str) -> pd.DataFrame:
    df = pd.read_excel(path, engine="openpyxl")
    if "Litologia" not in df.columns or "Tensão de Pico" not in df.columns:
        raise ValueError("Arquivo do Vale precisa ter colunas: 'Litologia' e 'Tensão de Pico'.")
    df["Tensão de Pico"] = pd.to_numeric(df["Tensão de Pico"], errors="coerce")
    return df


@st.cache_data(show_spinner=True)
def load_geo_and_peak(path: str):
    df = pd.read_excel(path, engine="openpyxl")
    if "id" not in df.columns or "tensao" not in df.columns:
        raise ValueError("Arquivo da Geocontrole precisa ter colunas: 'id' e 'tensao'.")
    df["tensao"] = pd.to_numeric(df["tensao"], errors="coerce")
    df_peak = df.loc[df.groupby("id")["tensao"].idxmax()].copy().reset_index(drop=True)
    return df, df_peak


def stats_series(s: pd.Series) -> pd.Series:
    s = pd.Series(s).dropna().astype(float)
    return pd.Series(
        {
            "SOMA": int(s.count()),
            "MÉDIA": s.mean(),
            "MEDIANA": s.median(),
            "DESVPAD": s.std(ddof=1),
            "MÍNIMO": s.min(),
            "MÁXIMO": s.max(),
        }
    )


def fmt_pt(x):
    if pd.isna(x):
        return ""
    return f"{x:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")


st.sidebar.header("⚙️ Configurações")

vale_path = st.sidebar.text_input("Arquivo Vale", "testeinacio estatisca.xlsx")
geo_path = st.sidebar.text_input("Arquivo Geocontrole", "consolidada.xlsx")

show_points = st.sidebar.checkbox("Mostrar pontos (jitter) sobre o boxplot", value=True)
jitter = st.sidebar.slider("Jitter (dispersão dos pontos)", 0.0, 0.6, 0.25, 0.05)
point_size = st.sidebar.slider("Tamanho dos pontos", 2, 10, 5, 1)

st.sidebar.markdown("---")
st.sidebar.subheader("🎨 Cores")

COLOR_GR = "#FFDCB4"
COLOR_HD = "#C8F0C8"
COLOR_HDA = "#FF4D4D"

st.sidebar.write(f"Graníticas: {COLOR_GR}")
st.sidebar.write(f"Hidrotermalizadas: {COLOR_HD}")
st.sidebar.write(f"Minério HDA: {COLOR_HDA}")

try:
    df_vale = load_vale(vale_path)
except Exception as e:
    st.error(f"Erro ao ler arquivo do Vale ({vale_path}): {e}")
    st.stop()

try:
    df_geo_raw, df_geo_peak = load_geo_and_peak(geo_path)
except Exception as e:
    st.error(f"Erro ao ler arquivo da Geocontrole ({geo_path}): {e}")
    st.stop()

st.success(
    f"Vale carregado: {len(df_vale)} linhas | "
    f"Geocontrole carregado: {len(df_geo_raw)} linhas | "
    f"Pico por ID: {len(df_geo_peak)} IDs"
)

GR = [
    "Granito Isotrópico (GRA)",
    "Granito Albítico (GRB)",
    "Granito Albítico Pegmatítico (GRBp)",
    "Granitoide (GRN)",
]

HD_ALL_VALE = [
    "Anfibolito (ANF)",
    "Biotita Xisto (HDB)",
    "Hidrotermalito (HQM)",
    "Hidrotermalito a Anfibólio (HDA)",
    "Hidrotermalito a Granada (HDG)",
]

HD_SEM_HDA = [
    "Anfibolito (ANF)",
    "Biotita Xisto (HDB)",
    "Hidrotermalito (HQM)",
    "Hidrotermalito a Granada (HDG)",
]

HDA_VALE = ["Hidrotermalito a Anfibólio (HDA)"]

vale_gr = df_vale[df_vale["Litologia"].isin(GR)]["Tensão de Pico"].dropna()
vale_hd_all = df_vale[df_vale["Litologia"].isin(HD_ALL_VALE)]["Tensão de Pico"].dropna()
vale_hd_sem_hda = df_vale[df_vale["Litologia"].isin(HD_SEM_HDA)]["Tensão de Pico"].dropna()
vale_hda = df_vale[df_vale["Litologia"].isin(HDA_VALE)]["Tensão de Pico"].dropna()

geo_peak = df_geo_peak["tensao"].dropna()

c1 = {
    "Rochas graníticas": vale_gr,
    "Rochas graníticas hidrotermalizadas": vale_hd_all,
}

c2 = {
    "Rochas graníticas": vale_gr,
    "Rochas graníticas hidrotermalizadas": pd.concat(
        [vale_hd_all.reset_index(drop=True), geo_peak.reset_index(drop=True)],
        ignore_index=True,
    ),
}

c3 = {
    "Rochas graníticas": vale_gr,
    "Rochas graníticas hidrotermalizadas": vale_hd_sem_hda,
    "Minério HDA": pd.concat(
        [vale_hda.reset_index(drop=True), geo_peak.reset_index(drop=True)],
        ignore_index=True,
    ),
}

cenarios = {
    "1": c1,
    "2": c2,
    "3": c3,
}

scenario = st.selectbox("Selecione o cenário:", list(cenarios.keys()), index=0)
data_groups = cenarios[scenario]

colors = {
    "Rochas graníticas": COLOR_GR,
    "Rochas graníticas hidrotermalizadas": COLOR_HD,
    "Minério HDA": COLOR_HDA,
}

fig = go.Figure()

for name, values in data_groups.items():
    values = pd.Series(values).dropna().astype(float)
    c = colors.get(name, "#CCCCCC")

    fig.add_trace(
        go.Box(
            y=values,
            name=f"<b>{name}</b>",
            boxmean="sd",
            boxpoints="all" if show_points else "outliers",
            jitter=jitter if show_points else 0,
            pointpos=0,
            marker=dict(size=point_size, color=c, opacity=0.60),
            line=dict(color=c, width=2),
            fillcolor=c,
            opacity=0.90,
            hovertemplate=(
                f"<b>{name}</b><br>"
                "Tensão: %{y:.2f} MPa<br>"
                "<extra></extra>"
            ),
        )
    )

fig.update_layout(
    title=dict(
        text=f"<b>Resistência Compressão UCS — {scenario}</b>",
        x=0.02,
        font=dict(size=24, family="Arial Black", color="black"),
    ),
    yaxis=dict(
        title=dict(
            text="<b>Resistência à Compressão (MPa)</b>",
            font=dict(size=20, family="Arial Black", color="black"),
        ),
        tickfont=dict(size=16, family="Arial Black", color="black"),
        gridcolor="rgba(0,0,0,0.08)",
    ),
    xaxis=dict(
        title=dict(
            text="<b>Litotipo</b>",
            font=dict(size=20, family="Arial Black", color="black"),
        ),
        tickfont=dict(size=16, family="Arial Black", color="black"),
    ),
    legend=dict(
        title=dict(
            text="<b>Grupo</b>",
            font=dict(size=20, family="Arial Black", color="black"),
        ),
        font=dict(size=18, family="Arial Black", color="black"),
    ),
    height=650,
    plot_bgcolor="white",
    margin=dict(l=70, r=30, t=90, b=90),
)

st.plotly_chart(fig, use_container_width=True)

st.subheader("📊 Estatística calculada a partir dos dados brutos (exata)")

tab = pd.DataFrame({k: stats_series(v) for k, v in data_groups.items()}).T
tab_disp = tab.copy()

for col in ["MÉDIA", "MEDIANA", "DESVPAD", "MÍNIMO", "MÁXIMO"]:
    tab_disp[col] = tab_disp[col].apply(fmt_pt)

tab_disp["SOMA"] = tab_disp["SOMA"].astype(int)
st.dataframe(tab_disp, use_container_width=True)

with st.expander("🔎 Ver Tensão de Pico por ID (Geocontrole)"):
    cols = [c for c in ["id", "rocha", "tensao"] if c in df_geo_peak.columns]
    st.dataframe(df_geo_peak[cols].sort_values("id"), use_container_width=True)

with st.expander("🧪 Checagens rápidas"):
    st.write(f"IDs Geocontrole (picos): {len(df_geo_peak)}")
    st.write(
        f"Vale - GR: {len(vale_gr)} | "
        f"HD (com HDA): {len(vale_hd_all)} | "
        f"HD (sem HDA): {len(vale_hd_sem_hda)} | "
        f"HDA Vale: {len(vale_hda)}"
    )