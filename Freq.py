import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import numpy as np

# Titolo dell'applicazione
st.title("Frequency Monitoring and Analysis with Averaging")

# Caricamento di più file CSV
uploaded_files = st.file_uploader("Choose CSV files", type="csv", accept_multiple_files=True)

if uploaded_files:
    dfs = []
    file_names = []

    # Processamento di ogni file caricato
    for file in uploaded_files:
        df = pd.read_csv(file, header=None, delimiter=';', skipinitialspace=True)
        df[0] = df[0].str.replace(',', '.').astype(float) / 1e6  # Converti in MHz
        df[1] = df[1].str.replace(',', '.').astype(float)  # Valori dB
        dfs.append(df)
        file_names.append(file.name)

    # Assumiamo che tutte le frequenze siano le stesse in ogni file per semplificare la media
    combined_df = pd.concat(dfs).groupby(0).mean().reset_index()
    combined_df.columns = ['Frequency (MHz)', 'Average dB']

    # Filtri per frequenza e dB
    st.sidebar.header("Filter Data")
    min_freq, max_freq = st.sidebar.slider(
        "Frequency Range (MHz)", float(combined_df['Frequency (MHz)'].min()), float(combined_df['Frequency (MHz)'].max()), 
        (float(combined_df['Frequency (MHz)'].min()), float(combined_df['Frequency (MHz)'].max()))
    )

    min_db, max_db = st.sidebar.slider(
        "dB Range", float(combined_df['Average dB'].min()), float(combined_df['Average dB'].max()), 
        (float(combined_df['Average dB'].min()), float(combined_df['Average dB'].max()))
    )

    # Filtraggio dei dati in base ai selettori
    filtered_dfs = []
    for df in dfs:
        filtered_df = df[(df[0] >= min_freq) & (df[0] <= max_freq) & (df[1] >= min_db) & (df[1] <= max_db)]
        filtered_dfs.append(filtered_df)

    # Filtraggio della media
    filtered_combined_df = combined_df[(combined_df['Frequency (MHz)'] >= min_freq) &
                                       (combined_df['Frequency (MHz)'] <= max_freq) &
                                       (combined_df['Average dB'] >= min_db) &
                                       (combined_df['Average dB'] <= max_db)]

    # Visualizzazione della tabella filtrata
    st.write("### Filtered Average Data Table", filtered_combined_df)

    # Creazione del grafico
    fig = go.Figure()

    # Aggiungi una linea per ogni CSV filtrato
    for i, df in enumerate(filtered_dfs):
        fig.add_trace(go.Scatter(x=df[0], y=df[1], mode='lines', name=f"Dataset {file_names[i]}"))

    # Aggiungi la linea della media filtrata
    fig.add_trace(go.Scatter(x=filtered_combined_df['Frequency (MHz)'], y=filtered_combined_df['Average dB'],
                             mode='lines', name='Average', line=dict(color='yellow')))

    # Aggiorna layout
    fig.update_layout(title='Frequency vs dB',
                      xaxis_title='Frequency (MHz)',
                      yaxis_title='dB',
                      legend_title='Datasets')

    st.plotly_chart(fig)

    # Sezione di analisi aggiuntiva (se necessaria)
    # Puoi inserire qui ulteriori funzionalità di analisi dei dati, come analisi statistica o altre visualizzazioni.
