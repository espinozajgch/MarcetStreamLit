#from streamlit_gsheets import GSheetsConnection

import streamlit as st
import pandas as pd
import warnings

from utils import util
from utils import login
from utils import connector_sgs
from utils import data_util
from utils.constants import COLUMNAS_EXCLUIDAS

warnings.filterwarnings("ignore", message="When grouping with a length-1 list-like")

st.set_page_config(
    page_title="Marcet - Cargas Fisicas",
    page_icon=":material/home:",
    layout="wide",
    initial_sidebar_state="expanded"
)

conn = connector_sgs.get_connector() 

# 🔐 Verificación de sesión
login.generarLogin(conn)

if "usuario" not in st.session_state:
    st.stop()

st.header('Bienvenido a :orange[Marcet]')

df_datos, df_data_test, df_checkin = data_util.load_player_and_physical_data(conn, connector_sgs.get_data)
total_jugadores = len(df_datos)

df_joined = util.join_player_and_physical_data(df_datos, df_data_test)
df_joined = util.limpiar_filas_sin_datos_validos(df_joined, COLUMNAS_EXCLUIDAS)
df_sesiones = util.resumen_sesiones(df_joined, total_jugadores)

#########################################################

col1, col2, col3, col4, col5 = st.columns(5)

with col1:
    st.metric("Total de Jugadores", total_jugadores)

with col2:
    act = df_sesiones["TSUM"].iloc[0]
    ant = df_sesiones["TSUM"].iloc[1]
    variacion = act - ant
    st.metric("Total Asistencia (Mes)",f'{act}', f'{variacion:,.2f}')

with col3:
    act = df_sesiones["APUS"].iloc[0]
    ant = df_sesiones["APUS"].iloc[1]
    variacion = act - ant
    st.metric("% Asistencia (Mes)",f'{act:,.3f}', f'{variacion:,.2f}')

with col4:
    act = df_sesiones["JUS"].iloc[0]
    ant = df_sesiones["JUS"].iloc[1]
    variacion = act - ant
    st.metric("Asistencia Ultima Sesion",f'{act}', f'{variacion:,.2f}')

with col5:
    # Mostrar la fecha si es válida
    if not df_joined.empty: 
        ultima_fecha = df_joined['FECHA REGISTRO'].iloc[0]
        if isinstance(ultima_fecha, pd.Timestamp):
            ultima_fecha_str = ultima_fecha.strftime('%d/%m/%Y')
        elif isinstance(ultima_fecha, str):
            ultima_fecha_str = ultima_fecha  # Ya es string, no necesita conversión
        else:
            ultima_fecha_str = str(ultima_fecha)  # Convertir otros tipos a string
        st.metric("Última Sesión", ultima_fecha_str)

    else:
        st.metric("Última Sesión", "####")

st.divider()

if not df_joined.empty: 
    st.markdown("📆 **Cantidad de Sesiones por jugador**")
    _, test_cat, _ = data_util.get_diccionario_test_categorias(conn, connector_sgs.get_data)
    st.dataframe(util.sesiones_por_test(df_joined, test_cat))
