import streamlit as st
from utils import util
from streamlit_gsheets import GSheetsConnection
import pandas as pd
import login as login
from datetime import date
import time

st.set_page_config(
    page_title="Test Físicos",
    page_icon=":material/directions_run:",
    layout="wide",
    initial_sidebar_state="expanded"
)

# 🔐 Verificación de sesión
login.generarLogin()
if "usuario" not in st.session_state:
    st.stop()

st.header(":blue[Tests Físicos] :material/directions_run:", divider=True)

conn = st.connection("gsheets", type=GSheetsConnection)

fecha_actual = date.today()

columnas_usadas = ["ID", "JUGADOR", "CATEGORIA", "EQUIPO"]

#player_data = util.get_player_data(conn)
#test_data = util.get_test_data(conn)

df_estructura_test = util.get_test(conn)
nombres_tests = df_estructura_test.columns.tolist()
#st.dataframe(nombres_tests)

player_data, test_data = util.getData(conn)

player_data_filtered = util.get_filters(player_data)

col1, col2, col3 = st.columns([1,2,2])
with col1:
	fecha_seleccionada = st.date_input(
		"FECHA:",
		value=fecha_actual,
		max_value=fecha_actual
	)
with col2:
	default_option = "Todos"
	# Mostrar en multiselect de Streamlit
	tests_seleccionados = st.multiselect(
		"TEST FISICOS:",
		placeholder="Seleccione una opción",
		options=nombres_tests #+ [default_option],
		#default=default_option  # o [] si quieres vacío por defecto
	)

# Obtener métricas dinámicamente
metricas = util.get_metricas_por_test(df_estructura_test, tests_seleccionados)
#st.dataframe(metricas)

fecha_formateada = fecha_seleccionada.strftime("%d/%m/%Y")
test_data_filtered = test_data[test_data["FECHA REGISTRO"] == fecha_formateada]
test_data_filtered = test_data_filtered[test_data_filtered["ID"].isin(player_data_filtered["ID"])]
datatest_columns = util.get_dataframe_columns(test_data)

df_nuevo = util.get_new(player_data_filtered, test_data_filtered, columnas_usadas, fecha_formateada)

columnas = ['FECHA REGISTRO', 'ID', 'JUGADOR', 'CATEGORIA', 'EQUIPO']
if len(metricas) > 0:
	df_nuevo = df_nuevo[columnas + metricas]

on = st.toggle("Solo Jugadores con Datos")

st.divider()

# Lista de columnas que quieres excluir de la validación
columnas_excluidas = ['FECHA REGISTRO', 'ID', 'CATEGORIA', 'EQUIPO']

if on:
	datatest_columns = util.get_dataframe_columns(df_nuevo)
	# Lista de columnas que sí quieres validar
	columnas_a_validar = [col for col in datatest_columns if col not in columnas]
	#st.text(columnas_a_validar)
	# 2. Elimina las filas donde TODAS las columnas a validar son NaN o None
	df_nuevo = df_nuevo.dropna(subset=columnas_a_validar, how="all")
     
	edited_df = util.get_data_editor(df_nuevo)
else:
    edited_df = util.get_data_editor(df_nuevo)


# 💾 Diálogo para guardar cambios (manual o auto)
@st.dialog("💾 Guardando datos en Google Sheets...", width="small")
def guardar_datos():
	with st.status("⌛ Actualizando datos en Google Sheets...", expanded=True) as status:
		try:
			edited_df.drop(columns=columnas_usadas[1], inplace=True)

			columnas_a_verificar = [col for col in edited_df.columns if col not in columnas_excluidas]

			df_edited = edited_df.dropna(subset=columnas_a_verificar, how="all")
			df_nuevotest_data = test_data.dropna(subset=columnas_a_verificar, how="all")

			df_combinado = pd.concat([df_nuevotest_data, df_edited], ignore_index=True)
			df_actualizado = df_combinado.drop_duplicates(subset=["FECHA REGISTRO", "ID"], keep="last")

			# Separar DataFrame actualizado en hojas
			dfs_separados = util.separar_dataframe_por_estructura(df_actualizado, df_estructura_test, columnas_excluidas)

			# Guardar cada hoja
			for nombre_hoja, df_hoja in dfs_separados.items():
				if not util.columnas_sin_datos_utiles(df_hoja, columnas_excluidas):
					conn.update(worksheet=nombre_hoja, data=df_hoja)
					#time.sleep(0.5)  # Opcional para evitar problemas de límite API

			status.update(label="✅ Datos actualizados correctamente.", state="complete", expanded=False)
			st.session_state["reload_data"] = True  # Activar recarga manual
			st.rerun()

		except Exception as e:
			status.update(label=f"❌ Error al actualizar: {e}", state="error", expanded=True)

# 🔘 Botón que activa el diálogo manual
if st.button("💾 Guardar Cambios"):
    guardar_datos()
	