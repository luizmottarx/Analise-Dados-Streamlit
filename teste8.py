import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import random

st.set_page_config(page_title="Tensão x Deslocamento Axial", layout="wide")

st.title("Tensão x Deslocamento Axial")

df = pd.read_excel("consolidada.xlsx", engine="openpyxl")

required_cols = {"id", "rocha", "def", "tensao"}
if not required_cols.issubset(df.columns):
    st.error("Colunas obrigatórias ausentes no arquivo")
else:
    df = df.copy()
    df = df[df["def"] > 0]

    st.subheader("Gráfico individual (δ – deslocamento axial)")

    col1, col2 = st.columns(2)
    with col1:
        rocha_sel = st.selectbox(
            "Rocha",
            sorted(df["rocha"].astype(str).unique())
        )
    with col2:
        ids_disp = sorted(
            df[df["rocha"].astype(str) == rocha_sel]["id"].unique()
        )
        id_sel = st.selectbox("ID", ids_disp)

    df_ind = df[
        (df["rocha"].astype(str) == rocha_sel) &
        (df["id"] == id_sel)
    ]

    fig1 = go.Figure()
    fig1.add_trace(
        go.Scatter(
            x=df_ind["def"],
            y=df_ind["tensao"],
            mode="markers",
            marker=dict(size=6),
            name=f"ID {id_sel}"
        )
    )

    fig1.update_layout(
        xaxis_title="δ (deslocamento axial)",
        yaxis_title="Tensão (MPa)",
        title=f"Rocha: {rocha_sel} | Ensaio ID: {id_sel}",
        hovermode="closest"
    )

    st.plotly_chart(fig1, use_container_width=True)

    st.subheader("Gráfico geral – todos os ensaios (δ)")

    fig2 = go.Figure()
    random.seed(42)

    for ensaio_id in sorted(df["id"].unique()):
        df_id = df[df["id"] == ensaio_id]
        if len(df_id) > 1:
            cor = f"rgb({random.randint(0,255)},{random.randint(0,255)},{random.randint(0,255)})"
            fig2.add_trace(
                go.Scatter(
                    x=df_id["def"],
                    y=df_id["tensao"],
                    mode="markers",
                    marker=dict(size=5, color=cor),
                    name=f"ID {ensaio_id}",
                    opacity=0.85
                )
            )

    fig2.update_layout(
        xaxis_title="δ (deslocamento axial)",
        yaxis_title="Tensão (MPa)",
        title="Tensão x Deslocamento Axial – Laboratório Comercial - Total 30 Ensaios",
        hovermode="closest",
        legend=dict(itemsizing="constant")
    )

    st.plotly_chart(fig2, use_container_width=True)
