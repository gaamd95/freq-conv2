import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import numpy as np

# Titolo dell'applicazione
st.title("Monitoraggio e Analisi delle Frequenze con Opzioni di Media")

# Caricamento di più file CSV
uploaded_files = st.file_uploader("Scegli file CSV", type="csv", accept_multiple_files=True)

# Selettore del tipo di media
average_type = st.sidebar.selectbox(
    "Seleziona Tipo di Media",
    ("Media", "Massimo")
)

# Input per il numero di radiomicrofoni
num_mics = st.sidebar.number_input("Numero di Radiomicrofoni", min_value=1, step=1)

if uploaded_files:
    dfs = []
    nomi_file = []

    # Processamento di ogni file caricato
    for file in uploaded_files:
        df = pd.read_csv(file, header=None, delimiter=';', skipinitialspace=True)
        df[0] = df[0].str.replace(',', '.').astype(float) / 1e6  # Converti in MHz
        df[1] = df[1].str.replace(',', '.').astype(float)  # Valori dB
        dfs.append(df)
        nomi_file.append(file.name)

    # Calcolo della media o del massimo
    if average_type == "Media":
        combined_df = pd.concat(dfs).groupby(0).mean().reset_index()
    else:
        combined_df = pd.concat(dfs).groupby(0).max().reset_index()

    # Ordinamento delle frequenze per livello di disturbo
    combined_df.sort_values(by=1, inplace=True)

    # Selezione delle migliori frequenze
    selected_frequencies = []
    for _, row in combined_df.iterrows():
        freq = row[0]
        if all(abs(freq - selected) > 0.1 for selected in selected_frequencies):  # Evita frequenze vicine
            selected_frequencies.append(freq)
        if len(selected_frequencies) == num_mics:
            break

    st.write(f"Frequenze selezionate per {num_mics} radiomicrofoni:")
    st.write(selected_frequencies)

    # Visualizzazione dei risultati
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=combined_df[0], y=combined_df[1], mode='lines', name='Disturbo'))
    for freq in selected_frequencies:
        fig.add_trace(go.Scatter(x=[freq], y=[combined_df.loc[combined_df[0] == freq, 1].values[0]],
                                 mode='markers', marker=dict(color='red', size=10), name=f'Frequenza {freq} MHz'))

    st.plotly_chart(fig)

    # Download delle frequenze selezionate
    download_df = pd.DataFrame(selected_frequencies, columns=["Frequenza (MHz)"])
    st.download_button(
        label="Scarica Frequenze Selezionate",
        data=download_df.to_csv(index=False).encode('utf-8'),
        file_name='frequenze_selezionate.csv',
        mime='text/csv',
    )
