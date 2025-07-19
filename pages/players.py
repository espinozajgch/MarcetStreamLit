import streamlit as st
from utils import util
#from streamlit_gsheets import GSheetsConnection
import pandas as pd
from utils import login
from utils import data_util
from utils import connector_sgs
from utils import constants

# 🛠 Configuración general
st.set_page_config(
    page_title="Jugadores",
    page_icon=":material/account_circle:",
    layout="wide",
    initial_sidebar_state="expanded"
)

# 📡 Conexión con Google Sheets
conn = connector_sgs.get_connector()

# 🔐 Verificación de sesión
login.generarLogin(conn)

if "usuario" not in st.session_state:
    st.stop()

# 🧠 Inicializar control de diálogo
#if "mostrar_dialogo_guardado" not in st.session_state:
#    st.session_state.mostrar_dialogo_guardado = False

# 📋 Encabezado
st.header(":blue[Jugadores] :material/account_circle:", divider=True)

# 📥 Cargar datos y eliminar columna innecesaria
df_jugadores = data_util.get_player_data(conn, connector_sgs.get_data)
df_jugadores.drop(columns=[constants.EDAD_LABEL], inplace=True, errors="ignore")

# 🔎 Aplicar filtros definidos
df_filtrado = util.get_filters(df_jugadores)

# ✏️ Editor de datos filtrados
#st.divider()
df_editado = util.get_data_editor(df_filtrado, num_rows_user="dynamic")

# if "last_saved_df" not in st.session_state:
#     st.session_state.last_saved_df = df_editado.copy()

# # Comparar si el usuario editó algo
# if not df_editado.equals(st.session_state.last_saved_df):
#     st.info("Guardando cambios...")

# 💾 Diálogo para guardar cambios
@st.dialog("💾 Guardando datos en Google Sheets...", width="small")
def guardar_datos():
    with st.status("⌛ Procesando y actualizando hoja...", state="running", expanded=True) as status:
        try:
            # 1. Eliminar registros existentes con mismo ID
            df_sin_duplicados = df_jugadores[~df_jugadores[constants.ID_LABEL].isin(df_filtrado[constants.ID_LABEL])]

            # 2. Unir datos nuevos + existentes
            df_combinado = pd.concat([df_sin_duplicados, df_editado], ignore_index=True)

            # 3. Formatear y ordenar por fecha
            df_combinado[constants.FECHA_REGISTRO_LABEL] = pd.to_datetime(
                df_combinado[constants.FECHA_REGISTRO_LABEL], format="%d/%m/%Y", errors="coerce"
            )
            df_combinado = df_combinado.sort_values(by=constants.FECHA_REGISTRO_LABEL, ascending=False).reset_index(drop=True)
            df_combinado[constants.FECHA_REGISTRO_LABEL] = df_combinado[constants.FECHA_REGISTRO_LABEL].dt.strftime('%d/%m/%Y')

            # 4. Actualizar hoja de cálculo
            conn.update(worksheet="DATOS", data=df_combinado)
            st.session_state["reload_data"] = True  # Activar recarga manual
            status.update(label="✅ Datos actualizados correctamente.", state="complete", expanded=False)
            st.rerun()

        except Exception as e:
            status.update(label="❌ Error al guardar los datos.", state="error", expanded=True)
            st.exception(e)

# 🔘 Botón que activa el diálogo
if st.button("💾 Guardar Cambios"):
    guardar_datos()
