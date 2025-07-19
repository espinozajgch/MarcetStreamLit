import streamlit as st
import pandas as pd

from utils import util
from utils import constants
from datetime import datetime

@st.cache_data(ttl=600)
def get_usuarios(_conn, _get_data):
    return _get_data(_conn, "USUARIOS")

@st.cache_data(ttl=60)  
def get_test(_conn, _get_data):
    return _get_data(_conn, "TEST")

@st.cache_data(ttl=60)
def get_player_data(_conn, _get_data):
    """
    Carga, limpia y transforma los datos de jugadores desde la hoja "DATOS" de Google Sheets.

    Esta función:
    - Elimina espacios en blanco en columnas tipo texto.
    - Elimina la columna "Cantidad" si existe.
    - Elimina duplicados por ID.
    - Convierte y formatea fechas de nacimiento.
    - Calcula la edad del jugador a partir de la fecha de nacimiento.
    - Rellena fechas faltantes o inválidas con la fecha actual.
    - Convierte "FECHA REGISTRO" a datetime para ordenar, y luego la devuelve como string.
    - Limpia y corrige nacionalidades según reglas definidas en `util.limpiar_nacionalidades`.
    - Asegura tipos consistentes para columnas clave.

    Args:
        _conn: Objeto `Spreadsheet` de gspread conectado a Google Sheets.

    Returns:
        pd.DataFrame: DataFrame limpio y ordenado con los datos de jugadores.
    """
    hoy = datetime.today()
    df = _get_data(_conn, "DATOS")

    # Limpieza general de strings
    str_cols = df.select_dtypes(include=["object", "string"]).columns
    df[str_cols] = df[str_cols].apply(lambda col: col.str.strip())

    # Eliminar columna innecesaria si existe
    df.drop(columns="Cantidad", errors="ignore", inplace=True)

    # Eliminar duplicados por ID
    df.drop_duplicates(subset=[constants.ID_LABEL], keep="first", inplace=True)

    # === Limpieza y cálculo de fechas ===
    df[constants.FECHA_NACIMIENTO_LABEL] = df[constants.FECHA_NACIMIENTO_LABEL].apply(util.convertir_fecha_segura)
    df[constants.EDAD_LABEL] = df[constants.FECHA_NACIMIENTO_LABEL].apply(
        lambda x: hoy.year - x.year - ((hoy.month, hoy.day) < (x.month, x.day)) if pd.notnull(x) else None
    )
    df[constants.FECHA_NACIMIENTO_LABEL] = df[constants.FECHA_NACIMIENTO_LABEL].apply(util.formatear_fecha)

    # Asegurar y ordenar por FECHA REGISTRO
    #df = util.rellenar_fechas_invalidas(df, columna=constants.FECHA_REGISTRO_LABEL)
    df[constants.FECHA_REGISTRO_LABEL] = pd.to_datetime(df[constants.FECHA_REGISTRO_LABEL], format="%d/%m/%Y", errors="coerce")
    df.sort_values(by=constants.FECHA_REGISTRO_LABEL, ascending=False, inplace=True)
    df[constants.FECHA_REGISTRO_LABEL] = df[constants.FECHA_REGISTRO_LABEL].dt.strftime("%d/%m/%Y")

    # Tipos seguros
    df = df.astype({constants.ID_LABEL: str, constants.JUGADOR_LABEL: str})

    df = util.limpiar_nacionalidades(df)
    #df = util.rellenar_fechas_invalidas(df, columna="FECHA DE NACIMIENTO")

    df.reset_index(drop=True, inplace=True)

    return df

def get_test_data(conn, hoja, _get_data):
    """
    Carga y limpia los datos de una hoja de test físico.

    Args:
        _spreadsheet: Objeto gspread Spreadsheet.
        hoja (str): Nombre de la hoja a cargar.

    Returns:
        pd.DataFrame: Datos limpios de la hoja de test.
    """
    df = _get_data(conn, hoja).reset_index(drop=True)

    if constants.ID_LABEL in df.columns:
        df = df.astype({constants.ID_LABEL: str})
    else:
        # Si no tiene encabezado estándar, usar la primera fila como header
        df.columns = df.iloc[0]
        df = df[1:].reset_index(drop=True)

        # Filtrar filas con al menos un valor numérico
        mask = df.applymap(util.es_numerico)
        df = df[mask.any(axis=1)]

        df.replace("None", 0, inplace=True)
        df.fillna(0, inplace=True)
        df = df.infer_objects(copy=False)

        df[constants.CATEGORIA_LABEL] = "Check in"
        if constants.JUGADOR_LABEL in df.columns:
            df[constants.JUGADOR_LABEL] = df[constants.JUGADOR_LABEL].astype(str).str.upper()

    return df

@st.cache_data(ttl=60)
def load_player_and_physical_data(_conn, _get_data):
    """
    Carga y consolida los datos de jugadores y sus tests físicos.

    Args:
        _spreadsheet: Objeto gspread Spreadsheet.

    Returns:
        tuple: (df_datos, df_data_test, df_checkin)
    """
    df_datos = get_player_data(_conn, _get_data)

    # Cargar todos los tests por hoja
    _, _, hojas_test = get_diccionario_test_categorias(_conn, _get_data)
    df_tests = [get_test_data(_conn, hoja, _get_data) for hoja in hojas_test]
    df_checkin = get_test_data(_conn, constants.CHECKIN_LABEL, _get_data)

    df_data_test = util.unir_dataframes(df_tests, constants.COLUMNAS_COMUNES)

    # Limpieza básica
    for col in [constants.CATEGORIA_LABEL, constants.EQUIPO_LABEL]:
        if col in df_data_test.columns:
            df_data_test[col] = df_data_test[col].astype(str).str.strip()

    # Preparar columnas numéricas
    columnas_estructura = util.get_dataframe_columns(df_data_test)
    columnas_numericas = [col for col in columnas_estructura if col not in constants.COLUMNAS_EXCLUIDAS]

    # Normalizar datos numéricos
    df_data_test = util.limpiar_columnas_numericas(df_data_test, columnas_numericas)
    df_checkin = util.limpiar_columnas_numericas(df_checkin, columnas_numericas)

    # Validar y limpiar fechas
    for df in [df_data_test, df_checkin]:
        df = util.rellenar_fechas_invalidas(df, columna=constants.FECHA_REGISTRO_LABEL)
        df.reset_index(drop=True, inplace=True)

    return df_datos, df_data_test, df_checkin

@st.cache_data(ttl=600)
def get_diccionario_test_categorias(_conn, _get_data):
    test = get_test(_conn, _get_data)
    test_cat = util.construir_diccionario_test_categorias(test)
    lista_columnas = test.columns.tolist()

    return test, test_cat, lista_columnas