# dohvat_podataka.py
import gspread
import pandas as pd
import streamlit as st

def dohvat_podataka(sheet_url: str, sheet_name: str):
    """
    Dohvaća podatke iz Google Sheetsa koristeći gspread i Service Account.
    
    Args:
        sheet_url (str): URL Google Sheeta.
        sheet_name (str): Naziv worksheet-a unutar Sheeta.

    Returns:
        df (pd.DataFrame): Podaci iz Sheeta.
        worksheet (gspread.models.Worksheet): Worksheet objekt za upis.
    """
    try:
        # Učitavanje Service Account credentialsa iz Streamlit secrets
        sa_info = st.secrets["gcp_service_account"]
        gc = gspread.service_account_from_dict(sa_info)

        # Otvaranje Google Sheeta preko URL-a
        sh = gc.open_by_url(sheet_url)

        # Odabir worksheet-a po imenu
        worksheet = sh.worksheet(sheet_name)

        # Dohvat svih podataka i pretvaranje u DataFrame
        data = worksheet.get_all_records()
        df = pd.DataFrame(data)

        # Ako je prazno, kreiraj prazan DataFrame sa standardnim stupcima
        if df.empty:
            df = pd.DataFrame(columns=["Naslov", "Godina", "Žanr", "Ocjena"])

        return df, worksheet

    except Exception as e:
        st.error(f"Greška prilikom dohvaćanja podataka: {e}")
        return pd.DataFrame(columns=["Naslov", "Godina", "Žanr", "Ocjena"]), None
