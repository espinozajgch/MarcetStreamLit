import streamlit as st
import pandas as pd
from fpdf import FPDF
import numpy as np
import requests

def get_ttl():
    if st.session_state.get("reload_data", False):
        default_reload_time = "0m"  # Forzar recarga
        st.session_state["reload_data"] = False  # Resetear flag después de la recarga
    else:
        default_reload_time = "10m"  # Usar caché normalmente

    return default_reload_time

def getData(conn):
    df_datos = getDatos(conn)
    df_data_test = getDataTest(conn)

    return df_datos, df_data_test

def getDatos(conn):
    df = conn.read(worksheet="DATOS", ttl=get_ttl())
    df = df.iloc[:, 2:] ##Elimina las primeras 2 columnas del DataFrame df2, manteniendo el resto.
    df.drop(columns=['BANDERA','FOTO PERFIL'],inplace=True)
    df = df.reset_index(drop=True)  # Reinicia los índices
    df['EDAD'] = df['EDAD'].fillna(0).astype(int).astype(str)
    df["NACIONALIDAD"] = df["NACIONALIDAD"].astype(str).str.replace(",", ".", regex=False).str.strip()
    df.drop_duplicates(subset=["ID"], keep="first")
    df = df.applymap(lambda x: x.strip() if isinstance(x, str) else x)
    return df

def getDataTest(conn):
    df = conn.read(worksheet="DATATEST", ttl=get_ttl())
    df = df.reset_index(drop=True)  # Reinicia los índices
    df.columns = df.iloc[0]  # Usa la primera fila como nombres de columna
    df = df[1:]  # Elimina la fila de encabezado original
    df = df.reset_index(drop=True)  # Reinicia los índices
    return df

def getJoinedDataFrame(conn):
    df_datos, df_data_test = getData(conn)
    ##df_datos = getDatos(conn, default_reload_time)
    ##df_data_test = getDataTest(conn, default_reload_time)

    # Verificar si alguno de los DataFrames está vacío
    if df_datos.empty or df_data_test.empty:
        return pd.DataFrame()  # Retornar DataFrame vacío si alguno de los dos está vacío

    # Realizar el merge asegurando que las claves de unión existen en ambos DataFrames
    common_columns = ['ID', 'JUGADOR', 'CATEGORIA', 'EQUIPO']
    if not all(col in df_datos.columns and col in df_data_test.columns for col in common_columns):
        return pd.DataFrame()  # Si faltan columnas clave, retornar vacío

    df_unido = pd.merge(df_datos, df_data_test, on=common_columns, how="inner")

    # Verificar si el DataFrame unido quedó vacío
    if df_unido.empty:
        return df_unido

    # Convertir la columna de fecha asegurando el formato correcto
    df_unido["FECHA REGISTRO"] = pd.to_datetime(df_unido["FECHA REGISTRO"], errors='coerce', dayfirst=True)

    # Eliminar filas con fechas inválidas
    df_unido = df_unido.dropna(subset=["FECHA REGISTRO"])

    # Extraer año y mes
    df_unido["anio"] = df_unido["FECHA REGISTRO"].dt.year.astype(str)
    df_unido["mes"] = df_unido["FECHA REGISTRO"].dt.month.astype(str)

    # Ordenar por fecha de más reciente a más antigua
    df_unido = df_unido.sort_values(by="FECHA REGISTRO", ascending=False)

    # Convertir la fecha a string en formato dd/mm/yyyy
    df_unido["FECHA REGISTRO"] = df_unido["FECHA REGISTRO"].dt.strftime('%d/%m/%Y').astype(str)

    # Reemplazar valores nulos o 'None' por 0
    df_unido = df_unido.fillna(0).replace("None", 0)

    # Eliminar filas donde todos los valores son 0
    df_unido = df_unido.loc[:, (df_unido != 0).any(axis=0)]

    return df_unido

def generar_pdf():
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", size=12)
    pdf.cell(200, 10, txt="Este es un informe generado en Streamlit", ln=True, align="C")
    return pdf

def generateMenu():
    with st.sidebar:
        st.page_link('app.py', label="Inicio", icon="🏠")
        st.page_link('pages/player.py', label="PlayerHub", icon="⚽")
        #st.page_link('pages/team.py', label="StatsLab", icon="📊")
        #st.page_link('pages/perfil.py', label="Perfil", icon="📊")

def generateFilters(df):

    ##anios = df["anio"].dropna().astype(str).str.strip().unique().tolist()
    df_filtrado = pd.DataFrame() 
    default_option = "Todos";

    category_col, team_col, position_col, nationality_col, player_col = st.columns(5)

    with category_col:
        category_list = df["CATEGORIA"].dropna().astype(str).str.strip().unique().tolist()
        category_list.sort()
        category = st.selectbox("CATEGORIA:", options=[default_option]+category_list, index=0)

    with team_col:

        if category == default_option:
            team_list = df["EQUIPO"]
        else:
            team_list = df[df['CATEGORIA'] == category]["EQUIPO"]
    
        team_list = team_list.dropna().astype(str).str.strip().unique().tolist()
        team_list.sort()
        team = st.selectbox("EQUIPO:", options=[default_option]+team_list)
    
    with position_col:
        position_list = df

        if category != default_option:
            position_list = position_list[position_list['CATEGORIA'] == category]

        if team != default_option:
            position_list = position_list[position_list['EQUIPO'] == team]

        position_list = position_list["DEMARCACIÓN"].dropna().astype(str).str.strip().unique().tolist()
        position_list.sort()
        position = st.selectbox("DEMARCACIÓN", options=[default_option]+position_list, index=0)

    with nationality_col:
        nationality_list = df

        if category != default_option:
            nationality_list = nationality_list[nationality_list['CATEGORIA'] == category]

        if team != default_option:
            nationality_list = nationality_list[nationality_list['EQUIPO'] == team]

        if position != default_option:
            nationality_list = nationality_list[nationality_list['DEMARCACIÓN'] == position]

        nationality_list = nationality_list["NACIONALIDAD"].dropna().astype(str).str.strip().unique().tolist()
        nationality_list.sort()
        nationality = st.selectbox("NACIONALIDAD:", options=[default_option]+nationality_list, index=0)
        
    with player_col:
        player_list = df
        
        if category != default_option:
            player_list = player_list[player_list['CATEGORIA'] == category]

        if team != default_option:
            player_list = player_list[player_list['EQUIPO'] == team]

        if position != default_option:
            player_list = player_list[player_list['DEMARCACIÓN'] == position]
        
        if nationality != default_option:
            player_list = player_list[player_list['NACIONALIDAD'] == nationality]

        player_list = player_list["JUGADOR"].dropna().astype(str).str.strip().unique().tolist()
        player_list.sort()
        player = st.selectbox("JUGADOR:", options=[default_option]+player_list, index=0)

    if player != default_option:
        df_filtrado=df[df["JUGADOR"]==player]

    #if anio:
    #    df_filtrado=df_filtrado[df_filtrado["anio"]==anio]
    #    df_filtrado = df_filtrado.reset_index(drop=True)  # Reinicia los índices

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
    
import pandas as pd

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



import pandas as pd

def sesiones_por_test(df):
    """
    Cuenta la cantidad de sesiones por jugador y por tipo de test.

    Parámetros:
    df : pd.DataFrame -> DataFrame con los registros de sesiones.

    Retorna:
    pd.DataFrame -> Cantidad de sesiones por jugador y tipo de test.
    """

    # Verificar si el DataFrame está vacío
    if df.empty:
        return pd.DataFrame()  # Retornar DataFrame vacío si no hay datos

    # Lista de columnas asociadas a cada test
    test_categorias = {
        "ANTROPOMETRÍA": ["ALTURA", "PESO", "MG [KG]", "GRASA (%)"],
        "AGILIDAD 505": ["505-DOM [SEG]", "505-ND [SEG]"],
        "SPRINT LINEAL": [
            "TOTAL 40M [SEG]", "TIEMPO 0-5M [SEG]", "VEL 0-5M [M/S]",
            "TIEMPO 5-20M [SEG]", "VEL 5-20M [M/S]", "TIEMPO 20-40M [SEG]", "VEL 20-40M [M/S]"
        ],
        "CMJ": ["CMJ [cm]", "CMJ [W]"],
        "YO-YO": ["TEST", "SPEED [km/h]", "ACCUMULATED SHUTTLE DISTANCE [m]"],
        "RSA": ["MEDIDA EN TIEMPO (SEG)", "VELOCIDAD (M*SEG)"]
    }

    # Verificar que las columnas esenciales existen
    required_columns = {"ID", "JUGADOR", "FECHA REGISTRO"}
    if not required_columns.issubset(df.columns):
        return pd.DataFrame()  # Retornar vacío si faltan columnas clave

    # Convertir FECHA REGISTRO a datetime con manejo de errores
    df["FECHA REGISTRO"] = pd.to_datetime(df["FECHA REGISTRO"], errors='coerce', dayfirst=True)

    # Eliminar filas con FECHA REGISTRO inválida
    df = df.dropna(subset=["FECHA REGISTRO"])

    # Crear un diccionario para contar sesiones por test
    sesiones_dict = {"ID": [], "JUGADOR": []}
    
    for test in test_categorias:
        sesiones_dict[test] = []

    # Agrupar por jugador y contar sesiones por test
    for (jugador_id, jugador_nombre), datos in df.groupby(["ID", "JUGADOR"]):
        sesiones_dict["ID"].append(jugador_id)
        sesiones_dict["JUGADOR"].append(jugador_nombre)

        for test, columnas in test_categorias.items():
            # Filtrar solo las columnas que existen en el DataFrame para evitar errores
            columnas_validas = [col for col in columnas if col in df.columns]

            if columnas_validas:
                sesiones_dict[test].append(datos.dropna(subset=columnas_validas)["FECHA REGISTRO"].nunique())
            else:
                sesiones_dict[test].append(0)  # Si no hay columnas válidas, asignar 0

    # Crear DataFrame final
    sesiones_df = pd.DataFrame(sesiones_dict)

    return sesiones_df


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
