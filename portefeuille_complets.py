# -*- coding: utf-8 -*-
"""Portefeuille complets - Simulateur avec gestion des erreurs"""

import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

st.title("Simulateur de portefeuilles InvestSmart 🚀")

# Menu pour choisir le portefeuille
portefeuille = st.sidebar.selectbox(
    "Choisissez un portefeuille à simuler :",
    ["Offensif", "Pondéré", "Prudent"]
)

# Définir les fichiers pour chaque portefeuille
portefeuilles_files = {
    "Offensif": {
        "Euro Gov Bond": "Historique VL Euro Gov Bond.xlsx",
        "NASDAQ": "AMUNDI NASDAQ.xlsx",
        "Core S&P 500": "IShares Core SP500.xlsx",
        "Asia EM": "Amundi MSCI Em Asia LU1681044563.xlsx"
    },
    "Pondéré": {
        "Euro Gov Bond": "Historique VL Euro Gov Bond.xlsx",
        "Euro STOXX 50": "HistoricalData EuroStoxx 50.xlsx",
        "Core S&P 500": "IShares Core SP500.xlsx",
        "PIMCO Euro Short": "PIMCO Euro Short-Term High Yield Corporate Bond Index UCITS ETF.xlsx"
    },
    "Prudent": {
        "Euro Gov Bond": "Historique VL Euro Gov Bond.xlsx",
        "Core S&P 500": "IShares Core SP500.xlsx",
        "PIMCO Euro Short": "PIMCO Euro Short-Term High Yield Corporate Bond Index UCITS ETF.xlsx"
    }
}

# Fonction de prétraitement des fichiers Excel
def preprocess_data(df, column_name):
    """Nettoie et prépare les données Excel pour la fusion"""
    if 'Date' not in df.columns or 'NAV' not in df.columns:
        st.error(f"Le fichier chargé pour {column_name} doit contenir les colonnes 'Date' et 'NAV'.")
        return None

    # Conversion de la colonne Date
    df['Date'] = pd.to_datetime(df['Date'], errors='coerce', dayfirst=True)
    if df['Date'].isnull().any():
        st.warning(f"Certaines dates dans {column_name} sont invalides et seront ignorées.")

    # Nettoyage des valeurs manquantes
    df = df.dropna(subset=['Date', 'NAV']).sort_values(by='Date').reset_index(drop=True)
    
    # Renommage de la colonne NAV
    df.rename(columns={'NAV': column_name}, inplace=True)
    return df

# Charger les fichiers pour le portefeuille sélectionné
files = portefeuilles_files[portefeuille]
uploaded_files = {}
dfs = {}

st.header(f"Chargez les fichiers Excel pour le portefeuille {portefeuille}")
for key in files:
    uploaded_files[key] = st.file_uploader(f"Téléchargez {key} :", type=["xlsx"])

# Prétraiter les fichiers chargés
if all(uploaded_files.values()):
    for key, file in uploaded_files.items():
        df = pd.read_excel(file)
        dfs[key] = preprocess_data(df, key)
        if dfs[key] is None:
            st.stop()  # Arrête l'application si un fichier est incorrect

    # Vérification des colonnes avant la fusion
    for key, df in dfs.items():
        if 'Date' not in df.columns or key not in df.columns:
            st.error(f"Le fichier {key} ne contient pas les colonnes nécessaires pour la fusion.")
            st.stop()

    # Fusion des fichiers
    df_combined = dfs[list(dfs.keys())[0]]
    for key in list(dfs.keys())[1:]:
        df_combined = pd.merge(df_combined, dfs[key][['Date', key]], on='Date', how='outer')

    st.success("Fusion réussie !")
    st.write("Aperçu des données combinées :")
    st.dataframe(df_combined.head())

    # Inputs utilisateur pour la simulation
    st.header("Simulation d'investissement 💰")
    montant_initial = st.number_input("Montant initial (€)", value=10000)
    duree = st.slider("Durée (années)", 1, 40, 10)
    rendement_annuel = st.slider("Rendement annuel (%)", 1.0, 10.0, 5.0)

    # Simulation de la projection
    df_combined['Portfolio_Value'] = montant_initial * (1 + rendement_annuel / 100) ** np.arange(len(df_combined))

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

