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
        combined_df = pd.concat(dfs).groupby(0, as_index=False).mean()
    elif average_type == "Massimo":
        combined_df = pd.concat(dfs).groupby(0, as_index=False).max()
    
    combined_df.columns = ['Frequenza (MHz)', f'{average_type} dB']

    # Filtri per frequenza e dB
    st.sidebar.header("Filtra Dati")
    min_freq, max_freq = st.sidebar.slider(
        "Intervallo di Frequenza (MHz)", float(combined_df['Frequenza (MHz)'].min()), float(combined_df['Frequenza (MHz)'].max()), 
        (float(combined_df['Frequenza (MHz)'].min()), float(combined_df['Frequenza (MHz)'].max()))
    )

    min_db, max_db = st.sidebar.slider(
        "Intervallo dB", float(combined_df[f'{average_type} dB'].min()), float(combined_df[f'{average_type} dB'].max()), 
        (float(combined_df[f'{average_type} dB'].min()), float(combined_df[f'{average_type} dB'].max()))
    )

    # Filtraggio dei dati in base ai selettori
    filtered_dfs = []
    for df in dfs:
        filtered_df = df[(df[0] >= min_freq) & (df[0] <= max_freq) & (df[1] >= min_db) & (df[1] <= max_db)]
        filtered_dfs.append(filtered_df)

    # Filtraggio della media o del massimo
    filtered_combined_df = combined_df[(combined_df['Frequenza (MHz)'] >= min_freq) &
                                       (combined_df['Frequenza (MHz)'] <= max_freq) &
                                       (combined_df[f'{average_type} dB'] >= min_db) &
                                       (combined_df[f'{average_type} dB'] <= max_db)]

    # Visualizzazione della tabella filtrata
    st.write(f"### Tabella dei Dati Filtrati ({average_type})", filtered_combined_df)

    # Creazione del grafico
    fig = go.Figure()

    # Aggiungi una linea per ogni CSV filtrato
    for i, df in enumerate(filtered_dfs):
        fig.add_trace(go.Scatter(x=df[0], y=df[1], mode='lines', name=f"Dataset {nomi_file[i]}"))

    # Aggiungi la linea della media o del massimo filtrato
    fig.add_trace(go.Scatter(x=filtered_combined_df['Frequenza (MHz)'], y=filtered_combined_df[f'{average_type} dB'],
                             mode='lines', name=f'{average_type}', line=dict(color='lime')))

    # Aggiorna layout
    fig.update_layout(title='Frequenza vs dB',
                      xaxis_title='Frequenza (MHz)',
                      yaxis_title='dB',
                      legend_title='Dataset')

    st.plotly_chart(fig)

    # Ordinamento delle frequenze per livello di disturbo
    combined_df.sort_values(by=f'{average_type} dB', inplace=True)

    # Selezione delle migliori frequenze
    selected_frequencies = []
    for _, row in combined_df.iterrows():
        freq = row['Frequenza (MHz)']
        if all(abs(freq - selected) > 0.1 for selected in selected_frequencies):  # Evita frequenze vicine
            selected_frequencies.append(freq)
        if len(selected_frequencies) == num_mics:
            break

    st.write(f"Frequenze selezionate per {num_mics} radiomicrofoni:")
    st.write(selected_frequencies)
    
    # Assicurati che il DataFrame sia ordinato per la frequenza
    combined_df.sort_values(by='Frequenza (MHz)', inplace=True)
    
    # Visualizzazione dei risultati con un grafico migliorato
    fig = go.Figure()

    # Linea principale che rappresenta il livello di disturbo su tutte le frequenze
    fig.add_trace(go.Scatter(
        x=combined_df['Frequenza (MHz)'], 
        y=combined_df[f'{average_type} dB'], 
        mode='lines', 
        name='Disturbo',
        line=dict(color='royalblue')
    ))
    
    # Aggiunta di marker per le frequenze selezionate
    for freq in selected_frequencies:
        fig.add_trace(go.Scatter(
            x=[freq], 
            y=[combined_df.loc[combined_df['Frequenza (MHz)'] == freq, f'{average_type} dB'].values[0]],
            mode='markers', 
            marker=dict(color='red', size=12, symbol='circle'),
            name=f'Frequenza {freq:.2f} MHz'
        ))
        
    # Aggiunta di aree ombreggiate per le frequenze selezionate
    for freq in selected_frequencies:
        fig.add_vrect(
            x0=freq - 0.05, x1=freq + 0.05, 
            fillcolor="LightSalmon", opacity=1, 
            layer="below", line_width=0.1
        )

    # Miglioramenti del layout
    fig.update_layout(
        title='Frequenza vs dB con Frequenze Selezionate',
        xaxis_title='Frequenza (MHz)',
        yaxis_title='dB',
        legend_title='Dataset',
        template='plotly_white'
    )

    # Mostra il grafico su Streamlit
    st.plotly_chart(fig)


    # Download delle frequenze selezionate
    download_df = pd.DataFrame(selected_frequencies, columns=["Frequenza (MHz)"])
    st.download_button(
        label="Scarica Frequenze Selezionate",
        data=download_df.to_csv(index=False).encode('utf-8'),
        file_name='frequenze_selezionate.csv',
        mime='text/csv',
    )
