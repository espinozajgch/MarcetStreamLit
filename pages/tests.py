import streamlit as st
from utils import util
from streamlit_gsheets import GSheetsConnection
import pandas as pd
import login as login
from datetime import date

st.set_page_config(
    page_title="Test Fisicos",
    page_icon=":material/directions_run:",
    layout="wide",
    initial_sidebar_state="expanded"
)

# 🔐 Verificación de sesión
login.generarLogin()
if "usuario" not in st.session_state:
    st.stop()

st.header(":blue[Tests Físicos] :material/directions_run:", divider=True)
#st.subheader("Métricas Grupales y alertas")

conn = st.connection("gsheets", type=GSheetsConnection)

fecha_actual = date.today()

col1, col2 = st.columns([1,3])
with col1:
	# Mostrar el filtro con date_input
	fecha_seleccionada = st.date_input(
		"FECHA:",
		value=fecha_actual,
		max_value=fecha_actual
	)

columnas_usadas = ["ID", "JUGADOR", "CATEGORIA", "EQUIPO"]

player_data = util.get_player_data(conn)
test_data = util.get_test_data(conn)
player_data_filtered = util.get_filters(player_data)

fecha_formateada = fecha_seleccionada.strftime("%d/%m/%Y")
test_data_filtered = test_data[test_data["FECHA REGISTRO"] == fecha_formateada]
test_data_filtered = test_data_filtered[test_data_filtered["ID"].isin(player_data_filtered["ID"])]

datatest_columns = util.get_dataframe_columns(test_data)

df_nuevo = util.get_new(player_data_filtered, test_data_filtered, columnas_usadas, fecha_formateada)

st.divider()

edited_df = util.get_data_editor(df_nuevo)
# 💾 Diálogo para guardar cambios
@st.dialog("💾 Guardando datos en Google Sheets...", width="small")
def guardar_datos():
	with st.status("⌛ Actualizando datos en Google Sheets...", expanded=True) as status:
		try:
			# Eliminamos solo el nombre completo (ya está separado en columnas relevantes)
			edited_df.drop(columns=columnas_usadas[1], inplace=True)

			# Eliminar registros con campos clave vacíos
			columnas_excluidas = ['FECHA REGISTRO', 'ID', 'CATEGORIA', 'EQUIPO']
			columnas_a_verificar = [col for col in edited_df.columns if col not in columnas_excluidas]

			df_edited = edited_df.dropna(subset=columnas_a_verificar, how="all")

			# 2. Concatenar y eliminar duplicados por clave compuesta (FECHA + ID)
			df_combinado = pd.concat([test_data, df_edited], ignore_index=True)

			# 3. Eliminar duplicados → mantener SOLO la última aparición
			df_actualizado = df_combinado.drop_duplicates(subset=["FECHA REGISTRO", "ID"], keep="last")

			conn.update(worksheet="DATATEST", data=df_actualizado)
			st.session_state["reload_data"] = True  # Activar recarga manual
			status.update(label="✅ Datos actualizados correctamente.", state="complete", expanded=False)

			#st.cache_data.clear()
			#st.rerun()
		except Exception as e:
			status.update(label=f"❌ Error al actualizar: {e}", state="error", expanded=True)

# 🔘 Botón que activa el diálogo
if st.button("💾 Guardar Cambios"):
    guardar_datos()