
from streamlit_gsheets import GSheetsConnection
import streamlit as st
from utils import util
import pandas as pd
import login as login
from datetime import date

st.set_page_config(
    page_title="Test Físicos",
    page_icon=":material/directions_run:",
    layout="wide",
    initial_sidebar_state="expanded"
)

conn = st.connection("gsheets", type=GSheetsConnection)

# 🔐 Verificación de sesión
login.generarLogin(conn)
if "usuario" not in st.session_state:
    st.stop()

st.header(":blue[Tests Físicos] :material/directions_run:", divider=True)

fecha_actual = date.today()
columnas_usadas = ["ID", "JUGADOR", "CATEGORIA", "EQUIPO"]

#player_data = util.get_player_data(conn)
#test_data = util.get_test_data(conn)

df_estructura_test = util.get_test(conn)
nombres_tests = df_estructura_test.columns.tolist()

player_data, test_data, df_checkin = util.getData(conn)

df_joined = util.getJoinedDataFrame(player_data, test_data)
test_data, df_datos_final = util.actualizar_datos_con_checkin(player_data, df_checkin, df_joined)

player_data_filtered = util.get_filters(player_data)
player_data_filtered = player_data_filtered.reset_index(drop=True)
	
#st.dataframe(player_data_filtered)

col1, col2, col3 = st.columns([1,1,2])
with col1:
	fecha_inicio = st.date_input(
		"FECHA INICIO:",
		value=fecha_actual,
		max_value=fecha_actual
	)
with col2:
	fecha_fin = st.date_input(
		"FECHA FIN:",
		value=fecha_actual,
		max_value=fecha_actual
	)
with col3:
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

if fecha_fin < fecha_inicio:
	st.warning("❌ La fecha final no puede ser anterior a la fecha inicial.")
	st.stop()
elif fecha_fin > fecha_inicio:

	test_data_filtered = util.filtrar_por_rango_fechas(test_data, "FECHA REGISTRO", fecha_inicio, fecha_fin)
	test_data_filtered = test_data_filtered.reset_index(drop=True)
	
	test_data_filtered = test_data_filtered.merge(
    player_data_filtered[["JUGADOR", "CATEGORIA", "EQUIPO"]],on=["JUGADOR", "CATEGORIA", "EQUIPO"],how="inner")

	#test_data_filtered = test_data_filtered[test_data_filtered["JUGADOR"].isin(player_data_filtered["JUGADOR"])]
	#st.dataframe(player_data_filtered)
	
	if not test_data_filtered.empty:
		df_nuevo = util.get_new(player_data_filtered, test_data_filtered, columnas_usadas)
		df_nuevo.drop(columns=["anio", "mes"], inplace=True)
	else:
		st.warning("⚠️ No existen datos de pruebas fisicas para el periodo seleccionado.")
		st.stop()
	
	#st.dataframe(df_nuevo)
	
elif fecha_inicio == fecha_fin:
	fecha_formateada = fecha_inicio.strftime("%d/%m/%Y")
	test_data_filtered = test_data[test_data["FECHA REGISTRO"] == fecha_formateada]

	#st.dataframe(test_data_filtered)

	test_data_filtered = test_data_filtered.merge(
    player_data_filtered[["JUGADOR", "CATEGORIA", "EQUIPO"]],on=["JUGADOR", "CATEGORIA", "EQUIPO"],how="inner")

	#test_data_filtered = test_data_filtered[test_data_filtered["ID"].isin(player_data_filtered["ID"])]
	#test_data_filtered = util.filtrar_por_rango_fechas(test_data, "FECHA REGISTRO", fecha_inicio, fecha_fin)
	
	#if test_data_filtered.empty:
	#	st.text("fechas iguales")
	df_nuevo = util.get_new(player_data_filtered, test_data_filtered, columnas_usadas, fecha_formateada)
	df_nuevo.drop(columns=["anio", "mes"], inplace=True)
	

columnas = ['FECHA REGISTRO', 'ID', 'JUGADOR', 'CATEGORIA', 'EQUIPO']
if len(metricas) > 0:
	df_nuevo = df_nuevo[columnas + metricas]

# Lista de columnas que quieres excluir de la validación
columnas_excluidas = ['FECHA REGISTRO', 'ID', 'CATEGORIA', 'EQUIPO']
datatest_columns = util.get_dataframe_columns(test_data)

# on = st.toggle("Solo Jugadores con Datos")

# if on:
# 	datatest_columns = util.get_dataframe_columns(df_nuevo)
# 	# Lista de columnas que sí quieres validar
# 	columnas_a_validar = [col for col in datatest_columns if col not in columnas]
# 	# 2. Elimina las filas donde TODAS las columnas a validar son NaN o None
# 	df_nuevo = df_nuevo.dropna(subset=columnas_a_validar, how="all")

# 	if df_nuevo.empty:
# 		st.warning("⚠️ No existen datos de pruebas fisicas para el periodo seleccionado.")
# 		st.stop()
	
# 	edited_df = util.get_data_editor(df_nuevo)
# else:
# 	edited_df = util.get_data_editor(df_nuevo)

# Selector horizontal
opcion_datos = st.radio(
    "Selecciona los jugadores a visualizar:",
    ("Jugadores con Datos Físicos", "Jugadores sin Datos Físicos"),
    horizontal=True
)

# Identificar columnas físicas (las que no están en 'columnas')
datatest_columns = util.get_dataframe_columns(df_nuevo)
columnas_a_validar = [col for col in datatest_columns if col not in columnas]

# Crear una copia de trabajo
df_filtrado = df_nuevo.copy()

if opcion_datos == "Jugadores con Datos Físicos":
    # Filtro: al menos una columna relevante no es nula ni cero
    mask_datos = ~(df_filtrado[columnas_a_validar].isna() | (df_filtrado[columnas_a_validar] == 0)).all(axis=1)
    df_filtrado = df_filtrado[mask_datos]

    if df_filtrado.empty:
        st.warning("⚠️ No existen datos de pruebas físicas para el periodo seleccionado.")
        st.stop()

else:  # Jugadores sin datos físicos
    # Filtro: todas las columnas relevantes son NaN, None o 0
	if len(tests_seleccionados)>1:
		mask_sin_datos = (df_filtrado[columnas_a_validar].isna() | (df_filtrado[columnas_a_validar] == 0)).any(axis=1)
	else:
		mask_sin_datos = (df_filtrado[columnas_a_validar].isna() | (df_filtrado[columnas_a_validar] == 0)).all(axis=1)
    
	df_filtrado = df_filtrado[mask_sin_datos]

edited_df = util.get_data_editor(df_filtrado)


st.divider()

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
#if st.button("💾 Guardar Cambios"):
#	guardar_datos()
