import streamlit as st
import gspread
from google.oauth2.service_account import Credentials
from gspread_dataframe import get_as_dataframe, set_with_dataframe

@st.cache_resource(show_spinner=True)
def get_spreadsheet():
    scopes = [
          "https://www.googleapis.com/auth/spreadsheets",
          "https://www.googleapis.com/auth/drive"
    ]
    creds = Credentials.from_service_account_info(st.secrets["connections"]["gsheets"], scopes=scopes)
    client = gspread.authorize(creds)
    return client.open("marcet_database")

def set_spreadsheet(ws, sheet, df):
    worksheet = ws.worksheet(sheet)
    set_with_dataframe(worksheet, df, include_index=False)

def get_data(conn, sheet):
    ws = conn.worksheet(sheet)
    df = get_as_dataframe(ws, evaluate_formulas=True)
    return df