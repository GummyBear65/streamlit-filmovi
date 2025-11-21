import streamlit as st
import pandas as pd
from dohvat_podataka import dohvat_podataka

# ------------------------------------------------------------------------------
# Postavke
# ------------------------------------------------------------------------------
SHEET_URL = st.secrets["sheet_url"]
SHEET_NAME = "filmovi"

# ------------------------------------------------------------------------------
# Učitavanje podataka
# ------------------------------------------------------------------------------
df, worksheet = dohvat_podataka(SHEET_URL, SHEET_NAME)

# Pretvorba stupaca u numeričke
df["Godina"] = pd.to_numeric(df["Godina"], errors="coerce")
df["Ocjena"] = pd.to_numeric(df["Ocjena"], errors="coerce")

# ------------------------------------------------------------------------------
# Naslov
# ------------------------------------------------------------------------------
st.title("🎬 Moji omiljeni filmovi")

# ------------------------------------------------------------------------------
# Tablica filmova
# ------------------------------------------------------------------------------
st.subheader("📋 Trenutni popis filmova")
st.dataframe(df)

# ------------------------------------------------------------------------------
# Dodavanje novog filma
# ------------------------------------------------------------------------------
st.subheader("➕ Dodaj novi film")

naslov = st.text_input("Naslov")
godina = st.number_input("Godina", step=1, format="%d")
zanr = st.text_input("Žanr")
ocjena = st.slider("Ocjena", 1, 10)

if st.button("Dodaj film"):
    if naslov and zanr and godina:
        novi_red = [naslov, int(godina), zanr, int(ocjena)]
        worksheet.append_row(novi_red)
        st.success("Film je uspješno dodan!")
        st.rerun()
    else:
        st.warning("Molim unesi sve podatke.")

# ------------------------------------------------------------------------------
# Pretraga
# ------------------------------------------------------------------------------
st.subheader("🔍 Pretraži filmove")
filtrirani = df.copy()

žanr_filt = st.text_input("Pretraži po žanru")
godina_filt = st.number_input("Pretraži po godini", step=1, format="%d")

if žanr_filt:
    filtrirani = filtrirani[filtrirani["Žanr"].str.contains(žanr_filt, case=False, na=False)]

if godina_filt:
    filtrirani = filtrirani[filtrirani["Godina"] == int(godina_filt)]

st.dataframe(filtrirani)

# ------------------------------------------------------------------------------
# Brisanje filmova
# ------------------------------------------------------------------------------
st.subheader("🗑️ Brisanje filmova")

# Opcije u SelectBox
filmovi_opcije = df.apply(lambda r: f"{r['Naslov']} ({r['Godina']})", axis=1).tolist()
film_za_brisanje = st.selectbox("Odaberi film", options=filmovi_opcije)

if st.button("Izbriši film"):
    for idx, row in df.iterrows():
        if f"{row['Naslov']} ({row['Godina']})" == film_za_brisanje:
            worksheet.delete_rows(idx + 2)  # +2 zbog headera
            st.success("Film je uspješno izbrisan!")
            st.rerun()

# ------------------------------------------------------------------------------
# Top 3 filmova
# ------------------------------------------------------------------------------
st.subheader("🏆 TOP 3 FILMA")
top3 = df.sort_values(by="Ocjena", ascending=False).head(3)
st.table(top3)
