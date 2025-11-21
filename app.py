import streamlit as st
import pandas as pd
from gspread import service_account
from gspread.exceptions import APIError

# --------------------------------------------------------------------------
# Postavke
# --------------------------------------------------------------------------
SHEET_URL = st.secrets["sheet_url"]  # URL Google Sheeta
SHEET_NAME = "filmovi"

# --------------------------------------------------------------------------
# Dohvat podataka iz Google Sheets
# --------------------------------------------------------------------------
@st.cache_data
def load_data():
    try:
        # Autentifikacija preko Service Account JSON (Streamlit Secrets)
        sa = service_account(filename=None)  # filename=None → koristi st.secrets["gcp_service_account"]
        sh = sa.open_by_url(SHEET_URL)
        worksheet = sh.worksheet(SHEET_NAME)
        df = pd.DataFrame(worksheet.get_all_records())
        # Pretvorba u numeričke tipove
        df["Godina"] = pd.to_numeric(df["Godina"], errors="coerce").fillna(0).astype(int)
        df["Ocjena"] = pd.to_numeric(df["Ocjena"], errors="coerce").fillna(0).astype(int)
    except Exception:
        # Ako nije moguće spojiti se, vraća mock podatke
        data = {
            "Naslov": ["Kum", "Iskupljenje u Shawshanku", "Pulp Fiction"],
            "Godina": [1972, 1994, 1994],
            "Žanr": ["Krimić/Drama", "Drama", "Krimić/Triler"],
            "Ocjena": [10, 10, 9],
        }
        df = pd.DataFrame(data)
        worksheet = None
    return df, worksheet

df, worksheet = load_data()

# --------------------------------------------------------------------------
# Naslov
# --------------------------------------------------------------------------
st.title("🎬 Vaši omiljeni filmovi")
st.markdown("---")

# --------------------------------------------------------------------------
# Dodavanje novog filma
# --------------------------------------------------------------------------
with st.expander("➕ Dodaj novi film"):
    naslov = st.text_input("Naslov")
    godina = st.number_input("Godina", step=1, format="%d", value=2020)
    zanr = st.text_input("Žanr")
    ocjena = st.slider("Ocjena", 1, 10, value=7)

    if st.button("Dodaj film"):
        if naslov and zanr and godina:
            novi_red = [naslov, int(godina), zanr, int(ocjena)]
            if worksheet:
                try:
                    worksheet.append_row(novi_red, value_input_option="USER_ENTERED")
                    st.success(f"Film '{naslov}' uspješno dodan!")
                except APIError as e:
                    st.error(f"Greška pri dodavanju u Google Sheet: {e}")
            else:
                st.info(f"Film '{naslov}' bi bio dodan. (Trenutno koristite mock podatke)")
        else:
            st.warning("Molim unesi sve podatke.")

# --------------------------------------------------------------------------
# Prikaz tablice
# --------------------------------------------------------------------------
st.subheader(f"📋 Popis filmova ({len(df)})")
st.dataframe(df, width="stretch")

