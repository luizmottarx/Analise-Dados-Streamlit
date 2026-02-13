import streamlit as st
import pandas as pd
import plotly.express as px

st.set_page_config(layout='wide')

df = pd.read_excel('consolidada.xlsx')

st.title("Gráficos Interativos – Ensaios de Rochas")

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

escala_x = st.radio("Escala do eixo X:", ["linear", "log"])
escala_y = st.radio("Escala do eixo Y:", ["linear", "log"])

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

fig.update_layout(
    xaxis=dict(type=escala_x, range=[min_x, max_x]),
    yaxis=dict(type=escala_y, range=[min_y, max_y])
)

st.plotly_chart(fig, use_container_width=True)