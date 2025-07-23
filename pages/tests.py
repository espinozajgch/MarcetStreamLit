import streamlit as st
import pandas as pd
from datetime import date

from utils import login_util
from utils import util
from utils import data_util
from utils import connector_sgs
from utils import constants

st.set_page_config(
    page_title="Test Físicos",
    page_icon=":material/directions_run:",
    layout="wide",
    initial_sidebar_state="expanded"
)

conn = connector_sgs.get_connector()

# 🔐 Verificación de sesión
login_util.generarLogin(conn)

if "usuario" not in st.session_state:
    st.stop()

st.header(":blue[Tests Físicos] :material/directions_run:", divider=True)

fecha_actual = date.today()

df_estructura_test, _, nombres_tests = data_util.get_diccionario_test_categorias(conn, connector_sgs.get_data)

player_data, test_data, df_checkin = data_util.load_player_and_physical_data(conn, connector_sgs.get_data)
df_joined = util.join_player_and_physical_data(player_data, test_data)
test_data, df_datos_final = util.actualizar_datos_con_checkin(player_data, df_checkin, df_joined)

player_data_filtered = util.get_filters(player_data)

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

	test_data_filtered = util.filtrar_por_rango_fechas(test_data, constants.FECHA_REGISTRO_LABEL, fecha_inicio, fecha_fin)
	test_data_filtered = test_data_filtered.reset_index(drop=True)
	
	test_data_filtered = test_data_filtered.merge(
    player_data_filtered[constants.COLUMNAS_COMUNES_JCE],on=constants.COLUMNAS_COMUNES_JCE,how="inner")

	if not test_data_filtered.empty:
		df_nuevo = util.get_new(player_data_filtered, test_data_filtered, constants.COLUMNAS_USADAS)
		df_nuevo.drop(columns=constants.COLUMNAS_EXCLUIDAS_DROP, inplace=True, errors="ignore")
	else:
		st.warning("⚠️ No existen datos de pruebas fisicas para el periodo seleccionado.")
		st.stop()

elif fecha_inicio == fecha_fin:
	fecha_formateada = fecha_inicio.strftime("%d/%m/%Y")
	test_data_filtered = test_data[test_data[constants.FECHA_REGISTRO_LABEL] == fecha_formateada]

	test_data_filtered = test_data_filtered.merge(
    player_data_filtered[constants.COLUMNAS_COMUNES_JCE],on=constants.COLUMNAS_COMUNES_JCE,how="inner")

	df_nuevo = util.get_new(player_data_filtered, test_data_filtered, constants.COLUMNAS_USADAS, fecha_formateada)
	df_nuevo.drop(columns=constants.COLUMNAS_EXCLUIDAS_DROP, inplace=True, errors="ignore")
	
columnas = constants.COLUMNAS
if len(metricas) > 0:
	df_nuevo = df_nuevo[columnas + metricas]

# Lista de columnas que quieres excluir de la validación
columnas_excluidas = constants.COLUMNAS_COMUNES
datatest_columns = util.get_dataframe_columns(test_data)

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

#st.divider()

# 💾 Diálogo para guardar cambios (manual o auto)
@st.dialog("💾 Guardando datos en Google Sheets...", width="small")
def guardar_datos():
	with st.status("⌛ Actualizando datos en Google Sheets...", expanded=True) as status:
		try:
			edited_df.drop(columns=constants.ID_LABEL, inplace=True, errors="ignore")

			columnas_a_verificar = [col for col in edited_df.columns if col not in columnas_excluidas]

			df_edited = edited_df.dropna(subset=columnas_a_verificar, how="all")
			df_nuevotest_data = test_data.dropna(subset=columnas_a_verificar, how="all")

			df_combinado = pd.concat([df_nuevotest_data, df_edited], ignore_index=True)
			df_actualizado = df_combinado.drop_duplicates(subset=[constants.FECHA_REGISTRO_LABEL, constants.ID_LABEL], keep="last")

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
