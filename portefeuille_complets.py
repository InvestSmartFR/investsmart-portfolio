# -*- coding: utf-8 -*-
"""Portefeuille complets - Simulation avec gestion des fichiers"""

import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt

st.title("Simulateur de portefeuilles InvestSmart 🚀")

# Menu pour choisir le portefeuille
portefeuille = st.sidebar.selectbox(
    "Choisissez un portefeuille à simuler :",
    ["Offensif", "Pondéré", "Prudent"]
)

# Fichiers associés aux portefeuilles
file_paths = {
    "Asia": "Amundi MSCI Em Asia LU1681044563 (1).xlsx",
    "NASDAQ": "AMUNDI NASDAQ (2).xlsx",
    "Euro STOXX": "HistoricalData EuroStoxx 50 (1).xlsx",
    "Euro Gov Bond": "Historique VL Euro Gov Bond (1).xlsx",
    "S&P 500": "IShares Core SP500 (2).xlsx",
    "PIMCO": "PIMCO Euro Short-Term High Yield Corporate Bond Index UCITS ETF.xlsx",
}

# Prétraitement des fichiers Excel
def preprocess_data(df, column_name):
    """Nettoie et prépare les données Excel pour la fusion"""
    if 'Date' not in df.columns or 'NAV' not in df.columns:
        st.error(f"Le fichier chargé pour {column_name} doit contenir les colonnes 'Date' et 'NAV'.")
        return None
    
    # Conversion de la colonne Date
    df['Date'] = pd.to_datetime(df['Date'], errors='coerce')
    df = df.dropna(subset=['Date', 'NAV']).sort_values(by='Date').reset_index(drop=True)
    df.rename(columns={'NAV': column_name}, inplace=True)
    return df

# Chargement des fichiers avec Streamlit
uploaded_files = {}
dfs = {}

st.header(f"Chargez les fichiers Excel pour le portefeuille {portefeuille}")
for key, path in file_paths.items():
    uploaded_files[key] = st.file_uploader(f"Téléchargez {key} :", type=["xlsx"])

if all(uploaded_files.values()):
    for key, file in uploaded_files.items():
        try:
            df = pd.read_excel(file)
            dfs[key] = preprocess_data(df, key)
            if dfs[key] is None:
                st.stop()  # Arrête si un fichier est incorrect
        except Exception as e:
            st.error(f"Erreur lors du chargement du fichier {key} : {e}")
            st.stop()

    # Fusion des fichiers
    df_combined = None
    for key, df in dfs.items():
        if df_combined is None:
            df_combined = df
        else:
            df_combined = pd.merge(df_combined, df[['Date', key]], on='Date', how='outer')

    # Afficher le DataFrame fusionné
    st.success("Fusion réussie !")
    st.write("Aperçu des données combinées :")
    st.dataframe(df_combined.head())

    # Simulation d'investissement
    st.header("Simulation d'investissement 💰")
    montant_initial = st.number_input("Montant initial (€)", value=10000)
    duree = st.slider("Durée (années)", 1, 40, 10)
    rendement_annuel = st.slider("Rendement annuel (%)", 1.0, 10.0, 5.0)

    # Calcul de la projection
    df_combined['Portfolio_Value'] = montant_initial * (1 + rendement_annuel / 100) ** range(len(df_combined))

    # Visualisation
    st.header("Évolution de votre portefeuille 📊")
    fig, ax = plt.subplots()
    ax.plot(df_combined['Date'], df_combined['Portfolio_Value'], label="Valeur du portefeuille")
    ax.set_title(f"Évolution du portefeuille {portefeuille}")
    ax.set_xlabel("Date")
    ax.set_ylabel("Valeur (€)")
    st.pyplot(fig)
else:
    st.warning("Veuillez télécharger tous les fichiers requis pour continuer.")

