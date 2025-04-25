import streamlit as st
import pandas as pd
from fpdf import FPDF
import numpy as np
import requests
from datetime import datetime
from utils.pdf import PDF
from scipy.stats import percentileofscore

def get_ttl():
    if st.session_state.get("reload_data", False):
        default_reload_time = "0m"  # Forzar recarga
        st.session_state["reload_data"] = False  # Resetear flag después de la recarga
    else:
        default_reload_time = "360m"  # Usar caché normalmente

    return default_reload_time

def get_test(conn):
    df = conn.read(worksheet="TEST", ttl=get_ttl())
    return df

def get_player_data(conn):
    #st.cache_data.clear()
    df = conn.read(worksheet="DATOS", ttl=get_ttl())

    hoy = datetime.today()

    # Convertir a tipo datetime (asegura formato día/mes/año)
    df["FECHA DE NACIMIENTO"] = pd.to_datetime(df["FECHA DE NACIMIENTO"], format="%d/%m/%Y")
    df["EDAD"] = df["FECHA DE NACIMIENTO"].apply(lambda x: hoy.year - x.year - ((hoy.month, hoy.day) < (x.month, x.day)))    
    df["FECHA DE NACIMIENTO"] = df["FECHA DE NACIMIENTO"].dt.strftime('%d/%m/%Y').astype(str)

    df["NACIONALIDAD"] = df["NACIONALIDAD"].astype(str).str.replace(",", ".", regex=False).str.strip()
    df.drop_duplicates(subset=["ID"], keep="first")
    
    df["FECHA REGISTRO"] = pd.to_datetime(df["FECHA REGISTRO"], format="%d/%m/%Y")
    df = df.sort_values(by=["FECHA REGISTRO"], ascending=False).reset_index(drop=True)
    df["FECHA REGISTRO"] = df["FECHA REGISTRO"].dt.strftime('%d/%m/%Y').astype(str)
    df = df.astype({ "ID": str }) 
    df = df.astype({ "JUGADOR": str }) 
    return df

def getData(conn):
    df_datos = get_player_data(conn)
    df_data_test = get_test_data(conn)

    return df_datos, df_data_test

def get_test_data(conn):
    df = conn.read(worksheet="DATATEST", ttl=get_ttl())
    df = df.reset_index(drop=True)  # Reinicia los índices
    # Asegúrate de que todas las columnas tienen tipos compatibles con Arrow
    df = df.astype({ "ID": str })  # o ajusta a tus columnas específicas
    
    #df.columns = df.iloc[0]  # Usa la primera fila como nombres de columna
    #df = df[1:]  # Elimina la fila de encabezado original
    #df = df.reset_index(drop=True)  # Reinicia los índices
    #df = df.fillna(0).replace("None", 0)
    return df

def get_dataframe_columns(dataframe):
    dataframe_columns = dataframe.columns.tolist()
    return dataframe_columns

def getJoinedDataFrame(conn):
    df_datos, df_data_test = getData(conn)
    ##df_datos = getDatos(conn, default_reload_time)
    ##df_data_test = getDataTest(conn, default_reload_time)

    # Verificar si alguno de los DataFrames está vacío
    if df_datos.empty or df_data_test.empty:
        return pd.DataFrame()  # Retornar DataFrame vacío si alguno de los dos está vacío

    columnas_excluidas = ["FECHA REGISTRO", "ID", "CATEGORIA", "EQUIPO", "TEST"]
    columnas_estructura = get_dataframe_columns(df_data_test)

    # Eliminar columnas excluidas
    columnas_filtradas = [col for col in columnas_estructura if col not in columnas_excluidas]

    # Asegurarse de insertar el nombre completo en la posición 2 si falta
    columna_nombre = "JUGADOR"  # por ejemplo "NOMBRE COMPLETO"
    #if columna_nombre not in columnas_estructura:
    #    columnas_estructura.insert(2, columna_nombre)

    # Si hay datos ya existentes, mapear nombres desde datos_jugadores
    if not df_data_test.empty:
        # Eliminar registros cuyo ID no está en df_datos
        df_data_test = df_data_test[df_data_test["ID"].isin(df_datos["ID"])]

        # Asegurar que la columna de nombres esté presente
        if columna_nombre not in df_data_test.columns:
            df_data_test.insert(2, columna_nombre, None)

        # Mapear nombres desde df_datos
        id_a_nombre = df_datos.set_index("ID")["JUGADOR"].to_dict()
        df_data_test[columna_nombre] = df_data_test["ID"].map(id_a_nombre)

        # Eliminar registros ya existentes según ID
        #datos_jugadores = datos_jugadores[~datos_jugadores["ID"].isin(df_data_test["ID"])]

    # Realizar el merge asegurando que las claves de unión existen en ambos DataFrames
    common_columns = ['ID', 'JUGADOR', 'CATEGORIA', 'EQUIPO']
    if not all(col in df_datos.columns and col in df_data_test.columns for col in common_columns):
        return pd.DataFrame()  # Si faltan columnas clave, retornar vacío

    #df_unido = pd.merge(df_datos, df_data_test, on=common_columns, how="inner")

    # Verificar si el DataFrame unido quedó vacío
    #if df_unido.empty:
    #return df_data_test

    # Convertir la columna de fecha asegurando el formato correcto
    df_data_test["FECHA REGISTRO"] = pd.to_datetime(df_data_test["FECHA REGISTRO"], errors='coerce', dayfirst=True)

    # # Eliminar filas con fechas inválidas
    # df_unido = df_unido.dropna(subset=["FECHA REGISTRO"])

    # # Extraer año y mes
    df_data_test["anio"] = df_data_test["FECHA REGISTRO"].dt.year.astype(str)
    df_data_test["mes"] = df_data_test["FECHA REGISTRO"].dt.month.astype(str)

    # # Ordenar por fecha de más reciente a más antigua
    df_data_test = df_data_test.sort_values(by="FECHA REGISTRO", ascending=False)

    # # Convertir la fecha a string en formato dd/mm/yyyy
    df_data_test["FECHA REGISTRO"] = df_data_test["FECHA REGISTRO"].dt.strftime('%d/%m/%Y').astype(str)

    # # Aplicar transformación solo a esas columnas
    df_data_test[columnas_filtradas] = df_data_test[columnas_filtradas].apply(lambda col: col.astype(str).str.replace(r"[,-]", ".", regex=True).astype(float))
    
    # # Reemplazar valores nulos o 'None' por 0
    df_data_test = df_data_test.fillna(0).replace("None", 0)

    # Eliminar filas donde todos los valores son 0
    #df_data_test = df_data_test.loc[:, (df_data_test != 0).any(axis=0)]
    df_data_test = df_data_test.astype({ "JUGADOR": str })  # o ajusta a tus columnas específicas

    return df_data_test

def get_new(datos_jugadores, df_existente, columnas_datos, fecha):
    """
    Genera un nuevo DataFrame con la estructura de 'df_existente',
    agregando datos nuevos desde 'datos_jugadores' y completando
    la columna de nombre del jugador si el ID coincide.

    Args:
        datos_jugadores (pd.DataFrame): Nuevos registros a insertar.
        df_existente (pd.DataFrame): DataFrame original con estructura base.
        columnas_datos (list): Columnas clave a mantener desde los datos de origen.
        fecha (str): Fecha a insertar en la columna FECHA (formato dd/mm/yyyy).

    Returns:
        pd.DataFrame: DataFrame combinado y ordenado por 'JUGADOR'.
    """
    # Obtener estructura base de columnas desde el DataFrame existente
    columnas_estructura = get_dataframe_columns(df_existente)

    # Asegurarse de insertar el nombre completo en la posición 2 si falta
    columna_nombre = columnas_datos[1]  # por ejemplo "NOMBRE COMPLETO"
    if columna_nombre not in columnas_estructura:
        columnas_estructura.insert(2, columna_nombre)

    # Crear DataFrame base vacío con estructura completa
    df_nuevo = pd.DataFrame(columns=columnas_estructura)

    # Si hay datos ya existentes, mapear nombres desde datos_jugadores
    if not df_existente.empty:
        if columna_nombre not in df_existente.columns:
            df_existente.insert(2, columna_nombre, None)

        id_a_nombre = datos_jugadores.set_index("ID")["JUGADOR"].to_dict()
        df_existente[columna_nombre] = df_existente["ID"].map(id_a_nombre)

        # Eliminar registros ya existentes según ID
        datos_jugadores = datos_jugadores[~datos_jugadores["ID"].isin(df_existente["ID"])]

    # Copiar columnas comunes desde datos_jugadores al nuevo DataFrame
    columnas_comunes = [col for col in columnas_datos if col in df_nuevo.columns]
    for col in columnas_comunes:
        df_nuevo[col] = datos_jugadores[col]

    # Agregar la fecha actual a la columna FECHA
    if "FECHA REGISTRO" in df_nuevo.columns:
        df_nuevo["FECHA REGISTRO"] = fecha

    # Forzar tipos seguros
    df_nuevo["ID"] = df_nuevo["ID"].astype(str)
    df_nuevo.columns = df_nuevo.columns.astype(str)

    # Unir datos existentes con los nuevos si aplica
    if not df_existente.empty:
        df_nuevo = pd.concat([df_existente, df_nuevo], ignore_index=True)

    columnas_orden = ["CATEGORIA", "EQUIPO"]
    columnas_presentes = [col for col in columnas_orden if col in df_nuevo.columns]

    if columnas_presentes:
        df_nuevo = df_nuevo.sort_values(by=columnas_presentes).reset_index(drop=True)

    return df_nuevo

def get_data_editor(df_nuevo, key=None):
    edited_df = st.data_editor(df_nuevo, key=key, column_config={
            "TEST": st.column_config.SelectboxColumn(
                label="TEST",
                options=["ENDURANCE I", "ENDURANCE II", "RECOVERY I", "RECOVERY II"],
                required=True,
                width="medium"
            )
        },num_rows="dynamic") # 👈 An editable dataframe
    return edited_df

def generateMenu():
    with st.sidebar:
        st.page_link('app.py', label="Inicio", icon="🏠")
        st.page_link('pages/player.py', label="PlayerHub", icon="⚽")
        #st.page_link('pages/team.py', label="StatsLab", icon="📊")
        #st.page_link('pages/perfil.py', label="Perfil", icon="📊")

# Utilidad para obtener lista única ordenada de una columna, con filtros
def get_filtered_list(dataframe, column, filters, default_option="Todos"):
    for col, val in filters.items():
        if val != default_option:
            dataframe = dataframe[dataframe[col] == val]
    return sorted(dataframe[column].dropna().astype(str).str.strip().unique().tolist())

def get_filters(df):
    default_option = "Todos"

    # Diccionario con los filtros y sus valores seleccionados
    filters = {
        "CATEGORIA": default_option,
        "EQUIPO": default_option,
        "DEMARCACION": default_option,
        "NACIONALIDAD": default_option,
        "JUGADOR": default_option
    }

    # Layout en 5 columnas
    category_col, team_col, position_col, nationality_col, player_col = st.columns(5)

    with category_col:
        category_list = get_filtered_list(df, "CATEGORIA", {})
        filters["CATEGORIA"] = st.selectbox("CATEGORÍA:", options=[default_option] + category_list)

    with team_col:
        team_list = get_filtered_list(df, "EQUIPO", {"CATEGORIA": filters["CATEGORIA"]})
        filters["EQUIPO"] = st.selectbox("EQUIPO:", options=[default_option] + team_list)

    with position_col:
        position_list = get_filtered_list(df, "DEMARCACION", {
            "CATEGORIA": filters["CATEGORIA"],
            "EQUIPO": filters["EQUIPO"]
        })
        filters["DEMARCACION"] = st.selectbox("DEMARCACION:", options=[default_option] + position_list)

    with nationality_col:
        nationality_list = get_filtered_list(df, "NACIONALIDAD", {
            "CATEGORIA": filters["CATEGORIA"],
            "EQUIPO": filters["EQUIPO"],
            "DEMARCACION": filters["DEMARCACION"]
        })
        filters["NACIONALIDAD"] = st.selectbox("NACIONALIDAD:", options=[default_option] + nationality_list)

    with player_col:
        player_list = get_filtered_list(df, "JUGADOR", {
            "CATEGORIA": filters["CATEGORIA"],
            "EQUIPO": filters["EQUIPO"],
            "DEMARCACION": filters["DEMARCACION"],
            "NACIONALIDAD": filters["NACIONALIDAD"]
        })
        filters["JUGADOR"] = st.selectbox("JUGADOR:", options=[default_option] + player_list)

    # Verificar si se aplicó al menos un filtro (distinto de "Todos")
    if any(value != default_option for value in filters.values()):
        df_filtrado = df.copy()
        for col, val in filters.items():
            if val != default_option:
                df_filtrado = df_filtrado[df_filtrado[col] == val]
        return df_filtrado

    # Si no se seleccionó ningún filtro, retornar el original
    return df

# def generateFilters(df):

#     ##anios = df["anio"].dropna().astype(str).str.strip().unique().tolist()
#     df_filtrado = pd.DataFrame() 
#     default_option = "Todos";

#     category_col, team_col, position_col, nationality_col, player_col = st.columns(5)

#     with category_col:
#         category_list = df["CATEGORIA"].dropna().astype(str).str.strip().unique().tolist()
#         category_list.sort()
#         category = st.selectbox("CATEGORIA:", options=[default_option]+category_list, index=0)

#     with team_col:

#         if category == default_option:
#             team_list = df["EQUIPO"]
#         else:
#             team_list = df[df['CATEGORIA'] == category]["EQUIPO"]
    
#         team_list = team_list.dropna().astype(str).str.strip().unique().tolist()
#         team_list.sort()
#         team = st.selectbox("EQUIPO:", options=[default_option]+team_list)
    
#     with position_col:
#         position_list = df

#         if category != default_option:
#             position_list = position_list[position_list['CATEGORIA'] == category]

#         if team != default_option:
#             position_list = position_list[position_list['EQUIPO'] == team]

#         position_list = position_list["DEMARCACION"].dropna().astype(str).str.strip().unique().tolist()
#         position_list.sort()
#         position = st.selectbox("DEMARCACIÓN", options=[default_option]+position_list, index=0)

#     with nationality_col:
#         nationality_list = df

#         if category != default_option:
#             nationality_list = nationality_list[nationality_list['CATEGORIA'] == category]

#         if team != default_option:
#             nationality_list = nationality_list[nationality_list['EQUIPO'] == team]

#         if position != default_option:
#             nationality_list = nationality_list[nationality_list['DEMARCACIÓN'] == position]

#         nationality_list = nationality_list["NACIONALIDAD"].dropna().astype(str).str.strip().unique().tolist()
#         nationality_list.sort()
#         nationality = st.selectbox("NACIONALIDAD:", options=[default_option]+nationality_list, index=0)
        
#     with player_col:
#         player_list = df
        
#         if category != default_option:
#             player_list = player_list[player_list['CATEGORIA'] == category]

#         if team != default_option:
#             player_list = player_list[player_list['EQUIPO'] == team]

#         if position != default_option:
#             player_list = player_list[player_list['DEMARCACIÓN'] == position]
        
#         if nationality != default_option:
#             player_list = player_list[player_list['NACIONALIDAD'] == nationality]

#         player_list = player_list["JUGADOR"].dropna().astype(str).str.strip().unique().tolist()
#         player_list.sort()
#         player = st.selectbox("JUGADOR:", options=[default_option]+player_list, index=0)

#     if player != default_option:
#         df_filtrado=df[df["JUGADOR"]==player]

#     #if anio:
#     #    df_filtrado=df_filtrado[df_filtrado["anio"]==anio]
#     #    df_filtrado = df_filtrado.reset_index(drop=True)  # Reinicia los índices

#     return df_filtrado

def generateFilters(df):
    default_option = "Todos"
    df_filtrado = pd.DataFrame()

    # Inicializar session_state solo para el filtro de JUGADOR
    if "JUGADOR" not in st.session_state:
        st.session_state["JUGADOR"] = default_option

    # Columnas de layout
    category_col, team_col, position_col, nationality_col, player_col = st.columns(5)

    # Filtro: CATEGORIA
    with category_col:
        category_list = sorted(df["CATEGORIA"].dropna().astype(str).str.strip().unique().tolist())
        category = st.selectbox("CATEGORIA:", [default_option] + category_list)

    # Filtro: EQUIPO
    team_df = df if category == default_option else df[df["CATEGORIA"] == category]
    with team_col:
        team_list = sorted(team_df["EQUIPO"].dropna().astype(str).str.strip().unique().tolist())
        team = st.selectbox("EQUIPO:", [default_option] + team_list)

    # Filtro: DEMARCACION
    pos_df = team_df if team == default_option else team_df[team_df["EQUIPO"] == team]
    with position_col:
        position_list = sorted(pos_df["DEMARCACION"].dropna().astype(str).str.strip().unique().tolist())
        position = st.selectbox("DEMARCACION", [default_option] + position_list)

    # Filtro: NACIONALIDAD
    nat_df = pos_df if position == default_option else pos_df[pos_df["DEMARCACION"] == position]
    with nationality_col:
        nationality_list = sorted(nat_df["NACIONALIDAD"].dropna().astype(str).str.strip().unique().tolist())
        nationality = st.selectbox("NACIONALIDAD:", [default_option] + nationality_list)

    # Filtro: JUGADOR (manteniendo el control con session_state)
    player_df = nat_df if nationality == default_option else nat_df[nat_df["NACIONALIDAD"] == nationality]
    with player_col:
        player_list = sorted(player_df["JUGADOR"].dropna().astype(str).str.strip().unique().tolist())
        player_options = [default_option] + player_list

        # Validar si la opción previa sigue disponible
        if st.session_state["JUGADOR"] not in player_options:
            st.session_state["JUGADOR"] = default_option

        selected_player = st.selectbox(
            "JUGADOR:",
            options=player_options,
            #index=player_options.index(st.session_state["JUGADOR"]),
            key="selected_player"
        )

        if selected_player != st.session_state["JUGADOR"]:
            st.session_state["JUGADOR"] = selected_player

    # Aplicar el filtro final solo si hay un jugador seleccionado
    if st.session_state["JUGADOR"] != default_option:
        df_filtrado = df[df["JUGADOR"].astype(str).str.strip() == st.session_state["JUGADOR"]]

    return df_filtrado


def get_photo(url):
    try:
        response = requests.get(url)
        response.raise_for_status()  # Verifica si hubo un error (por ejemplo, 404 o 500)
    except requests.exceptions.RequestException:
        response = None  # Si hay un error, no asignamos nada a response

    return response

def categorizar_grasa(porcentaje_grasa):
    if porcentaje_grasa is None:
        return "No disponible"
    elif porcentaje_grasa < 20:
        return "Saludable"
    else:
        return "No saludable"
    
def categorizar_imc(valor):
    if valor < 18.5:
        return "Bajo peso"
    elif 18.5 <= valor < 24.9:
        return "Normal"
    elif 25 <= valor < 29.9:
        return "Sobrepeso"
    else:
        return "Obesidad"

def color_categorias(val):
    color_mapping = {
        "Bajo peso": 0.2,  # Más cercano a rojo
        "Normal": 0.8,  # Más cercano a verde
        "Sobrepeso": 0.5,  # Amarillo
        "Obesidad": 0.1,  # Rojo fuerte
        "Saludable": 0.8,  # Verde
        "No saludable": 0.3  # Naranja/rojo
    }
    
    # Si el valor no está en el diccionario, devolver sin formato
    if val not in color_mapping:
        return ""
    
    # Normalizar el color en el rango de 0 (rojo) a 1 (verde)
    normalized = color_mapping[val]
    
    # Interpolar colores
    r = int(255 * (1 - normalized))  # Rojo disminuye con mayor valor
    g = int(255 * normalized)  # Verde aumenta con mayor valor
    b = 0  # Azul en 0 para tonos cálidos
    opacity = 0.4  # Opacidad fija
    
    return f'background-color: rgba({r}, {g}, {b}, {opacity})'

def aplicar_semaforo(df, exclude_columns=["FECHA REGISTRO"]):
    """
    Aplica un formato de color semáforo con opacidad a un DataFrame.

    - Rojo (peor valor de la columna).
    - Verde (mejor valor de la columna).
    - Amarillo (valores intermedios).
    - Blanco/transparente para NaN o columnas excluidas.

    Parámetros:
    df : pd.DataFrame  ->  DataFrame a estilizar.
    exclude_columns : list  ->  Lista de columnas a excluir de la pintura.

    Retorna:
    df.style -> DataFrame estilizado.
    """

    def semaforo(val, column):
        # Excluir columnas no numéricas o especificadas
        if column in exclude_columns or not np.issubdtype(df[column].dtype, np.number):
            return ''

        # Manejar valores NaN
        if pd.isna(val):  
            return 'background-color: rgba(255, 255, 255, 0)'

        # Obtener mínimo y máximo de la columna
        column_min = df[column].min()
        column_max = df[column].max()

        # Normalizar el valor entre 0 (mínimo) y 1 (máximo)
        if column_max != column_min:  
            normalized = (val - column_min) / (column_max - column_min)
        else:  
            normalized = 0.5  # Si todos los valores son iguales, usar amarillo

        # Interpolar colores (rojo -> amarillo -> verde)
        r = int(255 * (1 - normalized))  # Rojo se reduce cuando el valor sube
        g = int(255 * normalized)  # Verde aumenta cuando el valor sube
        b = 0  # Mantener el azul en 0 para tonos cálidos
        opacity = 0.4  # Opacidad fija

        return f'background-color: rgba({r}, {g}, {b}, {opacity})'

    # Aplicar la función a todas las columnas excepto las excluidas
    styled_df =  df.style.apply(lambda x: [semaforo(val, x.name) for val in x], axis=0)

    # Aplicar formato de dos decimales a todas las columnas numéricas no excluidas
    numeric_columns = [col for col in df.select_dtypes(include=[np.number]).columns if col not in exclude_columns]
    styled_df = styled_df.format({col: "{:.2f}" for col in numeric_columns})

    return styled_df            


def contar_jugadores_por_categoria(df):
    """
    Retorna un DataFrame con las categorías como columnas y la cantidad de jugadores únicos en cada una.

    Parámetros:
    df : pd.DataFrame -> DataFrame con la información de los jugadores, debe contener la columna 'CATEGORIA' y 'JUGADOR'.

    Retorna:
    pd.DataFrame -> DataFrame con las categorías como columnas y la cantidad de jugadores por categoría.
    """
    # Contar jugadores únicos por categoría
    jugadores_por_categoria = df.groupby("CATEGORIA")["JUGADOR"].nunique()

    # Convertir a DataFrame con categorías como columnas
    resultado = jugadores_por_categoria.to_frame().T

    return resultado
    
def resumen_sesiones(df, total_jugadores):
    """
    Calcula la cantidad de sesiones en los dos últimos meses, la asistencia promedio en cada mes,
    la cantidad de jugadores en la última sesión de cada mes y la fecha de la última sesión.

    Parámetros:
    df : pd.DataFrame -> DataFrame con los registros de sesiones.
    total_jugadores : int -> Número total de jugadores posibles a asistir.

    Retorna:
    pd.DataFrame -> Resumen de sesiones en el último mes y penúltimo mes.
    """

    # Verificar si el DataFrame está vacío o no tiene las columnas necesarias
    if df.empty or "FECHA REGISTRO" not in df or "ID" not in df:
        return pd.DataFrame({"MES": ["Último", "Penúltimo"], "TSUM": [0, 0], "APUS": [0, 0], "JUS": [0, 0], "FUS": [None, None]})

    # Convertir FECHA REGISTRO a datetime
    df["FECHA REGISTRO"] = pd.to_datetime(df["FECHA REGISTRO"], dayfirst=True, errors='coerce')

    # Verificar si hay fechas válidas
    if df["FECHA REGISTRO"].isna().all():
        return pd.DataFrame({"MES": ["Último", "Penúltimo"], "TSUM": [0, 0], "APUS": [0, 0], "JUS": [0, 0], "FUS": [None, None]})

    # Última fecha de sesión válida
    ultima_fecha = df["FECHA REGISTRO"].max()

    # Definir los rangos de tiempo
    un_mes_atras = ultima_fecha - pd.DateOffset(months=1)
    dos_meses_atras = ultima_fecha - pd.DateOffset(months=2)

    df_ultimo_mes = df[df["FECHA REGISTRO"] >= un_mes_atras]
    df_penultimo_mes = df[(df["FECHA REGISTRO"] >= dos_meses_atras) & (df["FECHA REGISTRO"] < un_mes_atras)]

    def calcular_resumen(df_periodo, nombre_mes):
        if df_periodo.empty:
            return {"MES": nombre_mes, "TSUM": 0, "APUS": 0, "JUS": 0, "FUS": None}
        
        # Contar sesiones únicas
        sesiones_mes = df_periodo.groupby("FECHA REGISTRO")["ID"].nunique().sum()
        
        # Última sesión del periodo
        ultima_fecha_periodo = df_periodo["FECHA REGISTRO"].max()
        jugadores_ultima_sesion = df[df["FECHA REGISTRO"] == ultima_fecha_periodo]["ID"].nunique()

        # Calcular asistencia promedio
        asistencia_promedio = jugadores_ultima_sesion / total_jugadores if total_jugadores > 0 else 0

        return {
            "MES": nombre_mes,
            "TSUM": sesiones_mes,
            "APUS": asistencia_promedio,
            "JUS": jugadores_ultima_sesion,
            "FUS": ultima_fecha_periodo.strftime('%d/%m/%Y') if pd.notna(ultima_fecha_periodo) else None
        }

    # Calcular resumen para ambos meses
    resumen_ultimo_mes = calcular_resumen(df_ultimo_mes, "Último")
    resumen_penultimo_mes = calcular_resumen(df_penultimo_mes, "Penúltimo")

    # Crear DataFrame con los resultados
    resumen_df = pd.DataFrame([resumen_ultimo_mes, resumen_penultimo_mes])

    return resumen_df

def sesiones_por_test(df, test_categorias):
    """
    Cuenta la cantidad de sesiones por jugador y por tipo de test.
    También agrega la fecha de la última sesión registrada por jugador.

    Parámetros:
        df (pd.DataFrame): DataFrame con los registros de sesiones.
        test_categorias (dict): Diccionario con los tipos de test y sus columnas asociadas.

    Retorna:
        pd.DataFrame: Cantidad de sesiones por jugador, tipo de test, y su última sesión.
    """
    
    if df.empty:
        return pd.DataFrame()

    # Verificar columnas esenciales
    columnas_requeridas = {"ID", "JUGADOR", "FECHA REGISTRO"}
    if not columnas_requeridas.issubset(df.columns):
        return pd.DataFrame()

    # Convertir fecha a datetime
    df["FECHA REGISTRO"] = pd.to_datetime(df["FECHA REGISTRO"], errors='coerce', dayfirst=True)
    df = df.dropna(subset=["FECHA REGISTRO"])

    # Inicializar diccionario
    sesiones_dict = {"ID": [], "JUGADOR": [], "ÚLTIMA SESIÓN": []}
    for test in test_categorias:
        sesiones_dict[test] = []

    # Agrupar por jugador
    for (jugador_id, jugador_nombre), datos_jugador in df.groupby(["ID", "JUGADOR"]):
        sesiones_dict["ID"].append(jugador_id)
        sesiones_dict["JUGADOR"].append(jugador_nombre)
        sesiones_dict["ÚLTIMA SESIÓN"].append(datos_jugador["FECHA REGISTRO"].max().strftime("%d/%m/%Y"))

        for test, columnas in test_categorias.items():
            columnas_validas = [col for col in columnas if col in datos_jugador.columns]
            if columnas_validas:
                sesiones_validas = datos_jugador[columnas_validas].apply(lambda x: (x != 0).any(), axis=1)
                sesiones_dict[test].append(sesiones_validas.sum())
            else:
                sesiones_dict[test].append(0)

    # Crear DataFrame final ordenado por jugador
    sesiones_df = pd.DataFrame(sesiones_dict)
    #sesiones_df = sesiones_df.sort_values(by=["JUGADOR"]).reset_index(drop=True)

    sesiones_df["ÚLTIMA SESIÓN"] = pd.to_datetime(sesiones_df["ÚLTIMA SESIÓN"], format="%d/%m/%Y")
    sesiones_df = sesiones_df.sort_values(by=["ÚLTIMA SESIÓN"], ascending=False).reset_index(drop=True)
    sesiones_df["ÚLTIMA SESIÓN"] = sesiones_df["ÚLTIMA SESIÓN"].dt.strftime('%d/%m/%Y').astype(str)
    
    return sesiones_df


def construir_diccionario_test_categorias(df_columnas_raw):
    """
    Convierte un DataFrame con columnas por categoría de test y valores por fila
    en un diccionario con estructura tipo: {"TEST": [métricas]}
    """
    test_categorias = {}

    for col in df_columnas_raw.columns:
        valores = df_columnas_raw[col].dropna().astype(str).str.strip().tolist()
        test_categorias[col.strip()] = valores

    return test_categorias


def obtener_bandera(pais):
    # Diccionario de códigos de país ISO 3166-1 alfa-2
    paises = {
        "ALBANIA": "🇦🇱", "ALEMANIA": "🇩🇪", "ANDORRA": "🇦🇩", "ARGENTINA": "🇦🇷",
        "ARMENIA": "🇦🇲", "AUSTRALIA": "🇦🇺", "AUSTRIA": "🇦🇹", "AZERBAIJAN": "🇦🇿",
        "BARBADOS": "🇧🇧", "BELGIUM": "🇧🇪", "BENIN": "🇧🇯", "BOLIVIA": "🇧🇴",
        "BOSNIA AND HERZEGOVINA": "🇧🇦", "BRASIL": "🇧🇷", "BULGARIA": "🇧🇬", "CAMEROON": "🇨🇲",
        "CANADA": "🇨🇦", "CHILE": "🇨🇱", "CHINA": "🇨🇳", "COLOMBIA": "🇨🇴",
        "COSTA DE MARFIL": "🇨🇮", "DINAMARCA": "🇩🇰", "DOMINICAN REPUBLIC": "🇩🇴", "ECUADOR": "🇪🇨",
        "EGIPTO": "🇪🇬", "EL SALVADOR": "🇸🇻", "ESPAÑA": "🇪🇸", "ETIOPÍA": "🇪🇹", "FILIPINAS": "🇵🇭",
        "FRANCIA": "🇫🇷", "GABON": "🇬🇦", "GAMBIA": "🇬🇲", "GEORGIA": "🇬🇪", "GERMANY": "🇩🇪",
        "GHANA": "🇬🇭", "GUATEMALA": "🇬🇹", "GUINEA": "🇬🇳", "HOLANDA": "🇳🇱", "HONDURAS": "🇭🇳",
        "HUNGRIA": "🇭🇺", "INDIA": "🇮🇳", "INGLATERRA": "🇬🇧", "IRLANDA": "🇮🇪", "ISRAEL": "🇮🇱",
        "ITALIA": "🇮🇹", "JORDANIA": "🇯🇴", "KAZAKHSTAN": "🇰🇿", "LATVIA": "🇱🇻", "LÍBANO": "🇱🇧",
        "LIBERIA": "🇱🇷", "LITUANIA": "🇱🇹", "MADAGASCAR": "🇲🇬", "MALTA": "🇲🇹", "MARRUECOS": "🇲🇦",
        "MÉXICO": "🇲🇽", "MONGOLIA": "🇲🇳", "MOROCCO": "🇲🇦", "MOZAMBIQUE": "🇲🇿", "NIGERIA": "🇳🇬",
        "PAÍS VASCO": "🇪🇸", "PANAMÁ": "🇵🇦", "PERÚ": "🇵🇪", "POLAND": "🇵🇱", "POLINESIA FRANCESA": "🇵🇫",
        "POLONIA": "🇵🇱", "PORTUGAL": "🇵🇹", "R. DOMINICANA": "🇩🇴", "RUMANIA": "🇷🇴", "RUSIA": "🇷🇺",
        "SIRIA": "🇸🇾", "SUECIA": "🇸🇪", "SUIZA": "🇨🇭", "TANZANIA": "🇹🇿", "TUNEZ": "🇹🇳",
        "TURKMENISTAN": "🇹🇲", "UCRANIA": "🇺🇦", "USA": "🇺🇸", "VENEZUELA": "🇻🇪", "VIRGIN ISLANDS": "🇻🇬"
    }

    
    # Normalizar el nombre del país
    pais = pais.strip().upper()

    if pais in paises:
        codigo = paises[pais]
        # Convertir el código de país a su bandera en Unicode
        #bandera_unicode = ''.join(chr(0x1F1E6 + ord(c)) for c in codigo)
        return codigo
    else:
        return ""

def generate_pdf(df_jugador, df_anthropometrics, df_agilty, df_sprint, df_cmj, df_yoyo, df_rsa, percentiles_an, percentiles_ag, percentiles_sp, percentiles_cmj, percentiles_yoyo, percentiles_rsa):
    pdf = PDF()
    pdf.add_page()

    # Datos personales
    #pdf.section_title("DATOS PERSONALES")
    pdf.add_player_block(df_jugador)
    
    # Composición corporal
    pdf.section_title("COMPOSICIÓN CORPORAL")
    
    if percentiles_an:
        pdf.section_subtitle("ANTOPOMETRIA")
        x_start = 10
        y_start = pdf.get_y()
        
        footer_text = "Tabla de percentiles: Comparación del jugador con atletas de su misma edad."
        pdf.add_percentile_semaforo_table(df_anthropometrics.iloc[0], percentiles_an, x=x_start, y=y_start, footer=footer_text)
        pdf.add_indices_table(df_anthropometrics.iloc[0], x_start + 105, y_start)
        pdf.ln(10)

    if percentiles_ag or percentiles_cmj:
    
        # Resultados físicos
        pdf.section_title("RESULTADOS TESTS FÍSICOS")

        if percentiles_ag:
            pdf.section_subtitle("AGILIDAD 505")
            x_start = 10
            y_start = pdf.get_y()
            footer_text = "El objetivo de este test es medir la capacidad de un atleta para cambiar de dirección."
            pdf.add_percentile_semaforo_table(df_agilty.iloc[0], percentiles_ag, x=x_start, y=y_start, footer=footer_text)
            pdf.add_img("assets/images/test/505.jpg",x=130, y=y_start, w=55)
            pdf.ln(3)

        if percentiles_cmj:
            pdf.section_subtitle("CMJ")
            x_start = 10
            y_start = pdf.get_y()
            footer_text = "El objetivo de este test es medir la potencia explosiva del tren inferior."
            pdf.add_percentile_semaforo_table(df_cmj.iloc[0], percentiles_cmj, x=x_start, y=y_start, footer=footer_text)
            pdf.add_img("assets/images/test/cmj.jpg",x=130, y=y_start-5, w=65)
            pdf.ln(3)

    page_height = pdf.get_height()
    margen_inferior = 33
    y_final = page_height - margen_inferior
    pdf.draw_gradient_scale(x=10, y=y_final)

    if percentiles_rsa or percentiles_sp or percentiles_yoyo:

        pdf.add_page()
        pdf.ln(20)
        pdf.section_title("RESULTADOS TESTS FÍSICOS")
        
        if percentiles_rsa:
            pdf.section_subtitle("RSA")
            x_start = 10
            y_start = pdf.get_y()
            footer_text = "El objetivo de este test es medir la resistencia a la fatiga en sprints repetidos."
            pdf.add_percentile_semaforo_table(df_rsa.iloc[0], percentiles_rsa, x=x_start, y=y_start, wm=50, footer=footer_text)
            pdf.add_img("assets/images/test/rsa.jpg",x=135, y=y_start-2, w=65)
            pdf.ln(3)

        if percentiles_sp:
            pdf.section_subtitle("SPRINT LINEAL")
            x_start = 10
            y_start = pdf.get_y()
            footer_text = "El objetivo de este test es medir la capacidad de un atleta para acelerar en línea recta."
            pdf.add_percentile_semaforo_table(df_sprint.iloc[0], percentiles_sp, x=x_start, y=y_start, wm=50, footer=footer_text)
            pdf.add_img("assets/images/test/sprint.jpg",x=135, y=y_start+20, w=65)
            pdf.ln(3)

        if percentiles_yoyo:
            pdf.section_subtitle("YO-YO")
            x_start = 10
            y_start = pdf.get_y()
            footer_text = "El objetivo de este test es medir la capacidad de recuperación en esfuerzos intermitentes."
            pdf.add_percentile_semaforo_table(df_yoyo.iloc[0], percentiles_yoyo, x=x_start, y=y_start, wm=75, footer=footer_text)
            
            y_start = pdf.get_y()
            pdf.add_img("assets/images/test/yo-yo.jpg",x=65, y=y_start+5, w=75)
            pdf.ln(45)

        page_height = pdf.get_height()
        margen_inferior = 35
        y_final = page_height - margen_inferior
        pdf.draw_gradient_scale(x=10, y=y_final)

    return pdf.output(dest='S').encode('latin1')


def calcular_percentiles(jugador, referencia, columnas_estructura):
    percentiles = {}
    #st.dataframe(referencia)
    #columnas_estructura = get_dataframe_columns(jugador)
    for variable in columnas_estructura:
        ref = referencia[variable].dropna().astype(float)
        valor = jugador[variable]
        percentil = percentileofscore(ref, valor, kind='rank')
        percentiles[variable] = round(percentil, 1)
    return percentiles

def obtener_color_percentil(p):
    if p is None or pd.isna(p):
        return (255, 255, 255), "Sin datos suficientes" # ⚪ 
    if p < 25:
        return (255, 69, 58), "Por debajo del promedio"  # 🔴
    elif p < 50:
        return (255, 165, 0), "Ligeramente inferior"     # 🟠
    elif p < 75:
        return (255, 225, 0), "En el promedio o superior" # 🟡
    else:
        return (52, 235, 58), "Muy por encima del promedio"  # 🟢

def interpretar_percentil(p):
    if p is None or pd.isna(p):
        return "⚪ Sin datos suficientes"
    elif p < 25:
        return "🔴 Por debajo del promedio"
    elif p < 50:
        return "🟠 Ligeramente inferior a la media"
    elif p < 75:
        return "🟡 En el promedio o superior"
    else:
        return "🟢 Muy por encima del promedio"

def get_rgb_from_categoria(val):
    color_mapping = {
        "Bajo peso": 0.2,
        "Normal": 0.8,
        "Sobrepeso": 0.5,
        "Obesidad": 0.1,
        "Saludable": 0.8,
        "No saludable": 0.3
    }
    if val not in color_mapping:
        return (255, 255, 255)  # Blanco si no se reconoce
    normalized = color_mapping[val]
    r = int(255 * (1 - normalized))
    g = int(255 * normalized)
    b = 0
    return (r, g, b)

def get_demarcaciones():
    MAPA_DEMARCACIONES = {
        "PORTERO": "POR",
        "DEFENSA CENTRAL": "DFC",
        "LATERAL DERECHO": "LD",
        "LATERAL IZQUIERDO": "LI",
        "MEDIOCENTRO DEFENSIVO": "MC",
        "MEDIOCENTRO": "MC",
        "MEDIAPUNTA": "MC",         
        "EXTREMO": "EX",             
        "DELANTERO": "DC"
    }

    return MAPA_DEMARCACIONES
