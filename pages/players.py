import streamlit as st
from utils import util
from streamlit_gsheets import GSheetsConnection
import pandas as pd
import login

# 🛠 Configuración general
st.set_page_config(
    page_title="Jugadores",
    page_icon=":material/account_circle:",
    layout="wide",
    initial_sidebar_state="expanded"
)

# 📡 Conexión con Google Sheets
conn = st.connection("gsheets", type=GSheetsConnection)

# 🔐 Verificación de sesión
login.generarLogin(conn)
if "usuario" not in st.session_state:
    st.stop()

# 🧠 Inicializar control de diálogo
if "mostrar_dialogo_guardado" not in st.session_state:
    st.session_state.mostrar_dialogo_guardado = False

# 📋 Encabezado
st.header(":blue[Jugadores] :material/account_circle:", divider=True)

# 📥 Cargar datos y eliminar columna innecesaria
df_jugadores = util.get_player_data(conn)
df_jugadores.drop(columns=["EDAD"], inplace=True, errors="ignore")

# 🔎 Aplicar filtros definidos
df_filtrado = util.get_filters(df_jugadores)

# ✏️ Editor de datos filtrados
st.divider()
df_editado = util.get_data_editor(df_filtrado, num_rows_user="dynamic")

# 💾 Diálogo para guardar cambios
@st.dialog("💾 Guardando datos en Google Sheets...", width="small")
def guardar_datos():
    with st.status("⌛ Procesando y actualizando hoja...", state="running", expanded=True) as status:
        try:
            # 1. Eliminar registros existentes con mismo ID
            df_sin_duplicados = df_jugadores[~df_jugadores["ID"].isin(df_filtrado["ID"])]

            # 2. Unir datos nuevos + existentes
            df_combinado = pd.concat([df_sin_duplicados, df_editado], ignore_index=True)

            # 3. Formatear y ordenar por fecha
            df_combinado["FECHA REGISTRO"] = pd.to_datetime(
                df_combinado["FECHA REGISTRO"], format="%d/%m/%Y", errors="coerce"
            )
            df_combinado = df_combinado.sort_values(by="FECHA REGISTRO", ascending=False).reset_index(drop=True)
            df_combinado["FECHA REGISTRO"] = df_combinado["FECHA REGISTRO"].dt.strftime('%d/%m/%Y')

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
