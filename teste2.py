import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

st.set_page_config(layout='wide')

df = pd.read_excel('consolidada.xlsx')

st.title('Análise de Ensaios de Rochas')

rochas = df['rocha'].unique()
rocha_sel = st.selectbox('Selecione a rocha:', rochas)

df_r = df[df['rocha'] == rocha_sel]

ids = df_r['id'].unique()
id_sel = st.selectbox('Selecione o ID:', ids)

df_id = df_r[df_r['id'] == id_sel]

st.subheader('Dispersão: Def x Tensão')
fig, ax = plt.subplots()
sns.scatterplot(data=df_id, x='def', y='tensao', ax=ax)
st.pyplot(fig)

st.subheader('Curva: Tensão x Tempo')
fig2, ax2 = plt.subplots()
sns.lineplot(data=df_id, x='tempo', y='tensao', ax=ax2)
st.pyplot(fig2)

st.subheader('Curva: Tensão x Carga')
fig3, ax3 = plt.subplots()
sns.lineplot(data=df_id, x='carga', y='tensao', ax=ax3)
st.pyplot(fig3)

st.subheader('Curva: Def x Tempo')
fig4, ax4 = plt.subplots()
sns.lineplot(data=df_id, x='tempo', y='def', ax=ax4)
st.pyplot(fig4)

st.subheader('Histograma de Tensão')
fig5, ax5 = plt.subplots()
sns.histplot(df_id['tensao'], kde=True, ax=ax5)
st.pyplot(fig5)

st.subheader('Histograma de Deformação (Def)')
fig6, ax6 = plt.subplots()
sns.histplot(df_id['def'], kde=True, ax=ax6)
st.pyplot(fig6)

st.subheader('Mapa de Correlação')
fig7, ax7 = plt.subplots(figsize=(8,5))
sns.heatmap(df_id[['def','tensao','tempo','carga']].corr(), annot=True, cmap='viridis', ax=ax7)
st.pyplot(fig7)

st.subheader('Resumo Estatístico')
st.write(df_id[['def','tensao','tempo','carga']].describe())