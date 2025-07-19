import streamlit as st
from utils import login
from utils.data_util import get_usuarios
from utils import connector_gs
from utils import connector_sgs
from utils import constants

# 🛠 Configuración general
st.set_page_config(
    page_title="Jugadores",
    page_icon=":material/groups:",
    layout="wide",
    initial_sidebar_state="expanded"
)

# 📡 Conexión con Google Sheets
conn = connector_sgs.get_connector()
ws = connector_gs.get_spreadsheet()

# 🔐 Verificación de sesión
login.generarLogin(conn)
if "usuario" not in st.session_state:
    st.stop()

st.header(":blue[Usuarios] :material/groups:", divider=True)

# 📥 Cargar datos y eliminar columna innecesaria
df_usuarios = get_usuarios(conn, connector_sgs.get_data)
df_usuarios = df_usuarios.reset_index(drop=True)
# ✏️ Editor de datos filtrados
df_editado = st.data_editor(df_usuarios, num_rows="fixed", hide_index=True, use_container_width=True)

#connector_gs.set_spreadsheet(ws, constants.USUARIOS_WS, df_editado)
#get_usuarios.clear()

# 💾 Diálogo para guardar cambios
@st.dialog("💾 Guardando datos en Google Sheets...", width="small")
def guardar_datos():
    with st.status("⌛ Procesando y actualizando hoja...", state="running", expanded=True) as status:
        try:
            connector_gs.set_spreadsheet(ws, constants.USUARIOS_WS, df_editado)
            #conn.update(worksheet="USUARIOS", data=df_editado)
            st.session_state["reload_data"] = True  # Activar recarga manual
            status.update(label="✅ Datos actualizados correctamente.", state="complete", expanded=False)
            st.rerun()

        except (ValueError, KeyError, ConnectionError) as e:  # Catch specific exceptions
            status.update(label="❌ Error al guardar los datos.", state="error", expanded=True)
            st.exception(e)

# 🔘 Botón que activa el diálogo
#if st.button("💾 Guardar Cambios"):
#    guardar_datos()
