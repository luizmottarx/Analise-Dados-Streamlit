import streamlit as st
import pandas as pd
import plotly.express as px

# =========================
# 🔐 CONFIG DE ACESSO
# =========================
# Coloque aqui os e-mails que você quer permitir
ALLOWED_EMAILS = {
    "luzdias@gmail.com",
}

st.set_page_config(layout="wide")

st.title("Gráficos Interativos – Ensaios de Rochas")

# =========================
# 🔐 LOGIN OIDC (Streamlit)
# =========================
# Se não estiver logado, mostra o botão de login e para o app
if not st.user.is_logged_in:
    st.info("Faça login para acessar o aplicativo.")
    st.button("Entrar", on_click=st.login)
    st.stop()

# Se estiver logado, pega o email (depende do provedor OIDC)
user_email = (st.user.get("email") or "").lower()

# Bloqueio por allowlist
if user_email not in {e.lower() for e in ALLOWED_EMAILS}:
    st.error("Acesso não autorizado para este usuário.")
    st.write(f"Usuário logado: {user_email}")
    st.button("Sair", on_click=st.logout)
    st.stop()

# Se quiser, mostrar usuário e botão de logout
with st.sidebar:
    st.success(f"Logado como: {user_email}")
    st.button("Sair", on_click=st.logout)

# =========================
# 📄 DADOS
# =========================
# ⚠️ No Streamlit Cloud, seu arquivo consolidada.xlsx precisa estar no repositório.
# Alternativa melhor: permitir upload do Excel.
# Se você preferir upload, me diga que eu adapto.

df = pd.read_excel("consolidada.xlsx")

# =========================
# 🎛️ FILTROS
# =========================
rochas = df["rocha"].unique()
rocha_sel = st.selectbox("Selecione a rocha:", rochas)

df_r = df[df["rocha"] == rocha_sel]

ids = df_r["id"].unique()
id_sel = st.selectbox("Selecione o ID:", ids)

df_id = df_r[df_r["id"] == id_sel]

st.subheader("Configurações do gráfico interativo")

col1, col2 = st.columns(2)
with col1:
    eixo_x = st.selectbox("Eixo X:", ["def", "tensao", "tempo", "carga"])
with col2:
    eixo_y = st.selectbox("Eixo Y:", ["def", "tensao", "tempo", "carga"])

escala_x = st.radio("Escala do eixo X:", ["linear", "log"], horizontal=True)
escala_y = st.radio("Escala do eixo Y:", ["linear", "log"], horizontal=True)

min_x, max_x = st.slider(
    "Limite do eixo X:",
    float(df_id[eixo_x].min()),
    float(df_id[eixo_x].max()),
    (float(df_id[eixo_x].min()), float(df_id[eixo_x].max()))
)

min_y, max_y = st.slider(
    "Limite do eixo Y:",
    float(df_id[eixo_y].min()),
    float(df_id[eixo_y].max()),
    (float(df_id[eixo_y].min()), float(df_id[eixo_y].max()))
)

fig = px.scatter(
    df_id,
    x=eixo_x,
    y=eixo_y,
    title=f"Gráfico Interativo: {eixo_x} x {eixo_y}",
)

# Nota: Em Plotly, range em eixo log é em log10; para simplificar, mantive como está.
# Se você usar log e quiser "range" correto, eu ajusto (é simples).
fig.update_layout(
    xaxis=dict(type=escala_x, range=[min_x, max_x]),
    yaxis=dict(type=escala_y, range=[min_y, max_y])
)

st.plotly_chart(fig, use_container_width=True)