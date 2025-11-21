import streamlit as st
import pandas as pd
from dohvat_podataka import ucitaj_podatke

SHEET_URL = st.secrets["sheet_url"]
SHEET_NAME = "filmovi"
df, worksheet = ucitaj_podatke(SHEET_URL, SHEET_NAME)

df["Godina"] = pd.to_numeric(df["Godina"])
df["Ocjena"] = pd.to_numeric(df["Ocjena"])

st.title("Omiljeni filmovi")

st.subheader("Trenutni popis filmova")
st.dataframe(df)
#poglavlje za dodavanje filmova
st.subheader("Dodaj novi film")
naslov = st.text_input("Naslov")
godina = st.number_input("Godina", step=1, format="%d")
zanr = st.text_input("Žanr")
ocjena = st.slider("Ocjena", 1, 10)

if st.button("Dodaj film"):
    novi_red = [naslov, int(godina), zanr, ocjena]
    worksheet.append_row(novi_red)
    st.success("Film je uspješno dodan!")
    st.rerun()
#poglavlje za pretragu filmova
st.subheader("Pretrazi filmove")
filtrirani = df.copy()

zanr_filter = st.text_input("Pretraži po žanru")
godina_filter = st.number_input("Pretraži po godini", step=1, format="%d")

if zanr_filter:
    filtrirani = filtrirani[filtrirani["Žanr"].str.contains(zanr_filter, case=False, na=False)]

if godina_filter:
    filtrirani = filtrirani[filtrirani["Godina"] == int(godina_filter)]

st.dataframe(filtrirani)
#poglavlje za brisanje filmova
st.subheader("Obriši film")

filmovi_opcije = df.apply(lambda row: f"{row['Naslov']} ({row['Godina']})", axis=1).tolist()
film_za_brisanje = st.selectbox("Odaberi film za brisanje", options=filmovi_opcije)

if st.button("Obriši film"):
    for idx, row in df.iterrows():
        if f"{row['Naslov']} ({row['Godina']})" == film_za_brisanje:
            worksheet.delete_rows(idx + 2)  # +2 zbog zaglavlja i 0-indeksiranja
            st.success("Film je uspješno obrisan!")
            st.rerun()

#poglavlje za prikaz top 3 filmova
st.subheader("TOP 3 FILMOVA")

top3= df.sort_values(by="Ocjena", ascending=False).head(3)
st.table(top3)


            
        
