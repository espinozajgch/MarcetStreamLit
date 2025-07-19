import streamlit as st
from streamlit_gsheets import GSheetsConnection

@st.cache_resource(show_spinner=True)
def get_connector():
    return st.connection("gsheets", type=GSheetsConnection)

def get_ttl():
    if st.session_state.get("reload_data", False):
        default_reload_time = "0m"  # Forzar recarga
        st.session_state["reload_data"] = False  # Resetear flag después de la recarga
    else:
        default_reload_time = "360m"  # Usar caché normalmente

    return default_reload_time

def get_data(_conn, sheet):
    df = _conn.read(worksheet=sheet, ttl=get_ttl())
    return df