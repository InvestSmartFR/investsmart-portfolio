import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

st.title("Simulateur de portefeuille pondéré 📊⚖️")

# Charger les fichiers Excel
files = {
    "Euro Gov Bond": "Historique VL Euro Gov Bond.xlsx",
    "Euro STOXX 50": "HistoricalData EuroStoxx 50.xlsx",
    "Core S&P 500": "IShares Core SP500.xlsx",
    "PIMCO Euro Short": "PIMCO Euro Short-Term High Yield Corporate Bond Index UCITS ETF.xlsx"
}

# Téléchargement des fichiers Excel
st.header("Téléchargez vos fichiers Excel 📂")
uploaded_files = {}
for key in files:
    uploaded_files[key] = st.file_uploader(f"Téléchargez {key} :", type=["xlsx"])

if all(uploaded_files.values()):
    # Lecture des fichiers Excel
    dfs = {}
    for key, file in uploaded_files.items():
        dfs[key] = pd.read_excel(file)

    # Prétraitement des données
    def preprocess_data(df, column_name):
        df['Date'] = pd.to_datetime(df['Date'], errors='coerce', dayfirst=True)
        df = df.dropna(subset=['Date']).sort_values(by='Date').reset_index(drop=True)
        df.rename(columns={'NAV': column_name}, inplace=True)
        return df

    for key, df in dfs.items():
        dfs[key] = preprocess_data(df, key)

    # Fusion des données
    df_combined = dfs[list(dfs.keys())[0]]
    for key in list(dfs.keys())[1:]:
        df_combined = pd.merge(df_combined, dfs[key][['Date', key]], on='Date', how='outer')

    # Simulation d'un investissement
    st.header("Simulation d'investissement 💰")
    montant_initial = st.number_input("Montant initial (€)", value=10000)
    duree = st.slider("Durée (années)", 1, 40, 10)
    rendement_annuel = st.slider("Rendement annuel (%)", 1.0, 10.0, 5.0) / 100

    # Calcul de la projection
    df_combined = df_combined.sort_values(by="Date")
    df_combined['Portfolio_Value'] = montant_initial * (1 + rendement_annuel) ** np.arange(len(df_combined))

    # Visualisation
    st.header("Évolution de votre portefeuille 📊")
    fig, ax = plt.subplots()
    ax.plot(df_combined['Date'], df_combined['Portfolio_Value'], label="Valeur du portefeuille")
    ax.set_title("Évolution de la valeur du portefeuille pondéré")
    ax.set_xlabel("Date")
    ax.set_ylabel("Valeur (€)")
    st.pyplot(fig)

else:
    st.warning("Veuillez télécharger tous les fichiers requis pour continuer.")
