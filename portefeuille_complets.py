# -*- coding: utf-8 -*-
"""Portefeuille complets - Chargement depuis le même dossier"""

import os
import pandas as pd
import streamlit as st
import matplotlib.pyplot as plt

# Titre de l'application
st.title("Simulateur de portefeuilles InvestSmart 🚀")

# Obtenir le répertoire actuel où le script est exécuté
current_dir = os.path.dirname(os.path.abspath(__file__))

# Fichiers stockés localement dans le même dossier
local_files = {
    "Asia": os.path.join(current_dir, "Amundi MSCI Em Asia LU1681044563 (1).xlsx"),
    "NASDAQ": os.path.join(current_dir, "AMUNDI NASDAQ (2).xlsx"),
    "Euro STOXX": os.path.join(current_dir, "HistoricalData EuroStoxx 50 (1).xlsx"),
    "Euro Gov Bond": os.path.join(current_dir, "Historique VL Euro Gov Bond (1).xlsx"),
    "S&P 500": os.path.join(current_dir, "IShares Core SP500 (2).xlsx"),
    "PIMCO": os.path.join(current_dir, "PIMCO Euro Short-Term High Yield Corporate Bond Index UCITS ETF.xlsx"),
}

# Prétraitement des fichiers Excel
def preprocess_data(file_path, column_name):
    """Nettoie et prépare les données Excel pour la fusion"""
    try:
        df = pd.read_excel(file_path)
        if 'Date' not in df.columns or 'NAV' not in df.columns:
            st.error(f"Le fichier {column_name} doit contenir les colonnes 'Date' et 'NAV'.")
            return None

        # Conversion de la colonne Date
        df['Date'] = pd.to_datetime(df['Date'], errors='coerce')
        df = df.dropna(subset=['Date', 'NAV']).sort_values(by='Date').reset_index(drop=True)
        df.rename(columns={'NAV': column_name}, inplace=True)
        return df
    except Exception as e:
        st.error(f"Erreur lors du chargement des données pour {column_name} : {e}")
        return None

# Charger les fichiers depuis le dossier local
dfs = {}
for key, path in local_files.items():
    dfs[key] = preprocess_data(path, key)
    if dfs[key] is None:
        st.stop()

# Fusionner les données
df_combined = None
for key, df in dfs.items():
    if df_combined is None:
        df_combined = df
    else:
        df_combined = pd.merge(df_combined, df[['Date', key]], on='Date', how='outer')

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
ax.set_title(f"Évolution du portefeuille")
ax.set_xlabel("Date")
ax.set_ylabel("Valeur (€)")
st.pyplot(fig)
