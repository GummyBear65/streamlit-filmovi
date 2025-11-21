import streamlit as st
import pandas as pd
import numpy as np # Dodano za bolju manipulaciju podacima
from dohvat_podataka import dohvat_podataka # Pretpostavljamo da ova funkcija i dalje radi

# ------------------------------------------------------------------------------
# Postavke
# ------------------------------------------------------------------------------
# st.set_page_config(layout="wide") # Možete uključiti za širi prikaz
SHEET_URL = st.secrets.get("sheet_url")
SHEET_NAME = "filmovi"

# ------------------------------------------------------------------------------
# Učitavanje podataka
# ------------------------------------------------------------------------------
@st.cache_data
def load_data(url, name):
    # Ovdje je 'dohvat_podataka' zamijenjen mock funkcijom za demonstraciju
    # Ako vaša aplikacija radi s Google Sheetsom, koristite originalnu funkciju
    try:
        df, worksheet = dohvat_podataka(url, name)
    except:
        # Mock DataFrame za testiranje bez stvarne veze
        data = {'Naslov': ['Kum', 'Iskupljenje u Shawshanku', 'Pulp Fiction', 'Inception', 'Matrix'],
                'Godina': [1972, 1994, 1994, 2010, 1999],
                'Žanr': ['Krimić/Drama', 'Drama', 'Krimić/Triler', 'SF/Akcija', 'SF/Akcija'],
                'Ocjena': [10, 10, 9, 9, 8]}
        df = pd.DataFrame(data)
        worksheet = None # Postavite na None ako nemate sheet objekt
    
    # Pretvorba stupaca u numeričke
    df["Godina"] = pd.to_numeric(df["Godina"], errors="coerce")
    df["Ocjena"] = pd.to_numeric(df["Ocjena"], errors="coerce")
    
    # Popravljanje NaT vrijednosti nakon coerce
    df.dropna(subset=['Godina', 'Ocjena'], inplace=True)
    df['Godina'] = df['Godina'].astype(int)
    df['Ocjena'] = df['Ocjena'].astype(int)
    
    return df, worksheet

df, worksheet = load_data(SHEET_URL, SHEET_NAME)

# ------------------------------------------------------------------------------
# Naslov
# ------------------------------------------------------------------------------
st.title("🎬 Vaši omiljeni filmovi")
st.markdown("---")

# ------------------------------------------------------------------------------
# Dodavanje novog filma (ostaje isto, ali je prebačeno u expander)
# ------------------------------------------------------------------------------
with st.expander("➕ Dodaj novi film", expanded=False):
    naslov = st.text_input("Naslov", key='novi_naslov')
    godina = st.number_input("Godina", step=1, format="%d", value=2020, key='nova_godina')
    zanr = st.text_input("Žanr", key='novi_zanr')
    ocjena = st.slider("Ocjena", 1, 10, value=7, key='nova_ocjena')

    if st.button("Dodaj film"):
        if naslov and zanr and godina:
            novi_red = [naslov, int(godina), zanr, int(ocjena)]
            if worksheet:
                worksheet.append_row(novi_red)
                st.success("Film je uspješno dodan!")
                st.rerun()
            else:
                st.info(f"Film '{naslov}' bi bio dodan. (Trenutno koristite mock podatke)")
        else:
            st.warning("Molim unesi sve podatke.")

st.markdown("---")

# ------------------------------------------------------------------------------
# Pretraga i filteri (Premješteno u Sidebar)
# ------------------------------------------------------------------------------
filtrirani = df.copy()

with st.sidebar:
    st.header("🔍 Filteri")

    # Filter po žanru - koristi unique vrijednosti za SelectBox
    svi_zanrovi = sorted(list(set(g.strip() for zanr_list in df['Žanr'].str.split('/') for g in zanr_list)))
    
    odabrani_zanr = st.selectbox(
        "Filtriraj po žanru", 
        options=['Svi'] + svi_zanrovi, 
        index=0
    )

    # Filter po godini - koristi raspon umjesto točne godine
    min_godina, max_godina = int(df['Godina'].min()), int(df['Godina'].max())
    godine_rang = st.slider(
        "Godine izlaska",
        min_value=min_godina,
        max_value=max_godina,
        value=(min_godina, max_godina)
    )

    # Primjena filtera
    if odabrani_zanr != 'Svi':
        filtrirani = filtrirani[filtrirani["Žanr"].str.contains(odabrani_zanr, case=False, na=False)]

    filtrirani = filtrirani[
        (filtrirani["Godina"] >= godine_rang[0]) & 
        (filtrirani["Godina"] <= godine_rang[1])
    ]

# ------------------------------------------------------------------------------
# Tablica filmova (Prikaz filtriranih podataka)
# ------------------------------------------------------------------------------
st.subheader(f"📋 Popis filmova ({len(filtrirani)} rezultata)")
# Koristimo st.data_editor za interaktivnu tablicu (sortiranje unutar tablice)
st.dataframe(filtrirani, use_container_width=True)

st.markdown("---")

# ------------------------------------------------------------------------------
# Vizualizacije
# ------------------------------------------------------------------------------
st.subheader("📊 Analiza podataka")

col1, col2 = st.columns(2)

with col1:
    st.markdown("##### Distribucija ocjena")
    # Histogram ocjena
    ocjene_count = df["Ocjena"].value_counts().sort_index().reset_index()
    ocjene_count.columns = ['Ocjena', 'Broj Filmova']
    st.bar_chart(ocjene_count, x='Ocjena', y='Broj Filmova')

with col2:
    st.markdown("##### Top 5 žanrova")
    # Prikaz top žanrova
    # Prvo moramo podijeliti kombinirane žanrove (npr. 'SF/Akcija')
    zanr_counts = df['Žanr'].str.split('/', expand=True).stack().value_counts().head(5)
    st.bar_chart(zanr_counts)

st.markdown("---")

# ------------------------------------------------------------------------------
# Top 3 filmova (Poboljšan prikaz)
# ------------------------------------------------------------------------------
st.subheader("🏆 TOP 3 FILMA")

if not df.empty:
    top3 = df.sort_values(by=["Ocjena", "Godina"], ascending=[False, True]).head(3)

    for i, row in top3.iterrows():
        # Koristimo st.columns za lijepši prikaz Top 3
        rank_col, info_col = st.columns([1, 6])
        
        # Ikona i rang
        with rank_col:
            if i == top3.index[0]:
                st.metric(label="🥇 #1", value=f"{row['Ocjena']}/10")
            elif i == top3.index[1]:
                st.metric(label="🥈 #2", value=f"{row['Ocjena']}/10")
            else:
                st.metric(label="🥉 #3", value=f"{row['Ocjena']}/10")

        # Informacije o filmu
        with info_col:
            st.markdown(f"**{row['Naslov']}** ({row['Godina']})")
            st.caption(f"Žanr: {row['Žanr']}")
            st.markdown("---")

else:
    st.info("Nema filmova za prikaz TOP 3.")

