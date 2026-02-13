import pandas as pd

# 1) Ler o arquivo Excel
arquivo = "consolidada.xlsx"
df = pd.read_excel(arquivo, engine="openpyxl")

# 2) Garantir que a coluna de tensão é numérica
df["tensao"] = pd.to_numeric(df["tensao"], errors="coerce")

# 3) Para cada ID, pegar a linha onde a tensão é MÁXIMA
df_pico_por_id = (
    df.loc[df.groupby("id")["tensao"].idxmax()]
    .reset_index(drop=True)
)

# 4) Estatística sobre a tensão de pico por ID
estatistica = pd.DataFrame({
    "SOMA": [df_pico_por_id["tensao"].count()],   # nº de IDs (≈ 30)
    "MÉDIA": [df_pico_por_id["tensao"].mean()],
    "MEDIANA": [df_pico_por_id["tensao"].median()],
    "DESVPAD": [df_pico_por_id["tensao"].std(ddof=1)],  # amostral
    "MÍNIMO": [df_pico_por_id["tensao"].min()],
    "MÁXIMO": [df_pico_por_id["tensao"].max()]
})

# 5) (Opcional) Salvar resultados
df_pico_por_id.to_excel("tensao_pico_por_id.xlsx", index=False)
estatistica.to_excel("estatistica_tensao_pico.xlsx", index=False)

# 6) Mostrar no console
print("Tensão de pico por ID:")
print(df_pico_por_id[["id", "rocha", "tensao"]])

print("\nEstatística da tensão de pico:")
print(estatistica)
