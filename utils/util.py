import streamlit as st
import pandas as pd
from fpdf import FPDF
import numpy as np
import requests
from datetime import datetime
from utils.pdf import PDF
from scipy.stats import percentileofscore
from functools import reduce


def get_ttl():
    if st.session_state.get("reload_data", False):
        default_reload_time = "0m"  # Forzar recarga
        st.session_state["reload_data"] = False  # Resetear flag después de la recarga
    else:
        default_reload_time = "360m"  # Usar caché normalmente

    return default_reload_time

def get_usuarios(conn):
    df = conn.read(worksheet="USUARIOS", ttl=get_ttl())
    return df

def get_test(conn):
    df = conn.read(worksheet="TEST", ttl=get_ttl())
    return df

def get_player_data(conn):
    #st.cache_data.clear()
    df = conn.read(worksheet="DATOS", ttl=get_ttl())
    #st.dataframe(df)
    hoy = datetime.today()

    for col in df.select_dtypes(include=["object", "string"]):
        df[col] = df[col].str.strip()

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

    # Eliminar filas donde ID es NaN, 0 o "nan"
    #df = df[df["ID"].notnull() &
    #(df["ID"].astype(str) != "0") &
    #(df["ID"].astype(str).str.lower() != "nan")]

    return df

def getData(conn):
    df_datos = get_player_data(conn)

    df_an = get_test_data(conn,'ANTROPOMETRIA')
    df_ag = get_test_data(conn,'AGILIDAD')
    df_sp = get_test_data(conn,'SPRINT')
    df_cmj = get_test_data(conn,'CMJ')
    df_yoyo = get_test_data(conn,'YO-YO')
    df_rsa = get_test_data(conn,'RSA')

    df_checkin = get_test_data(conn,'CHECK-IN')

    columnas_comunes = ['FECHA REGISTRO', 'ID', 'CATEGORIA', 'EQUIPO']
    df_data_test = unir_dataframes([df_an, df_ag, df_sp, df_cmj, df_yoyo, df_rsa], columnas_comunes)

    df_data_test["CATEGORIA"] = df_data_test["CATEGORIA"].str.strip()
    df_data_test["EQUIPO"] = df_data_test["EQUIPO"].str.strip()

    columnas_excluidas = ["FECHA REGISTRO", "ID", "JUGADOR" ,"CATEGORIA", "EQUIPO", "TEST"]
    columnas_estructura = get_dataframe_columns(df_data_test)
   
    # Eliminar columnas excluidas
    columnas_filtradas = [col for col in columnas_estructura if col not in columnas_excluidas]

    df_data_test = limpiar_columnas_numericas(df_data_test, columnas_filtradas)
    df_checkin = limpiar_columnas_numericas(df_checkin, columnas_filtradas)

    #st.text("Datos de los tests")
    #st.dataframe(columnas_filtradas)
    return df_datos, df_data_test, df_checkin

def unir_dataframes(dfs, columnas_comunes, metodo='outer'):
    """
    Une una lista de DataFrames basándose en columnas comunes.

    Args:
        dfs (list): Lista de DataFrames a unir.
        columnas_comunes (list): Columnas comunes para hacer el merge.
        metodo (str): Tipo de unión ('outer' para no perder datos, 'inner' para intersección).

    Returns:
        DataFrame: Un DataFrame combinado con columnas comunes al inicio.
    """
    if not dfs:
        raise ValueError("La lista de DataFrames está vacía.")
    
    dfs = [df.drop_duplicates(subset=columnas_comunes) for df in dfs]

    # Verifica que todos los DataFrames contengan las columnas comunes
    for df in dfs:
        for col in columnas_comunes:
            if col not in df.columns:
                raise ValueError(f"La columna '{col}' no existe en uno de los DataFrames.")
    
    # Merge secuencial de todos los DataFrames
    df_final = reduce(lambda left, right: pd.merge(left, right, on=columnas_comunes, how=metodo), dfs)
    
    # Eliminar filas donde TODAS las columnas NO comunes son NaN
    columnas_no_comunes = [col for col in df_final.columns if col not in columnas_comunes]
    df_final = df_final.dropna(subset=columnas_no_comunes, how='all')

    # Reordenar columnas: comunes primero
    columnas_ordenadas = columnas_comunes + [col for col in df_final.columns if col not in columnas_comunes]
    df_final = df_final[columnas_ordenadas]
    
    return df_final

def es_numerico(val):
    try:
        return isinstance(val, (int, float)) and not pd.isna(val)
    except:
        return False
    
def get_test_data(conn, hoja):
    df = conn.read(worksheet=hoja, ttl=get_ttl())
    df = df.reset_index(drop=True)  # Reinicia los índices

    if "ID" in df.columns:
        df = df.astype({"ID": str})  # o ajusta a tus columnas específicas
    else:
        df.columns = df.iloc[0]  # Usa la primera fila como nombres de columna
        df = df[1:]  # Elimina la fila de encabezado original
        df = df.reset_index(drop=True)
        
        mask = df.applymap(es_numerico)
        df = df[mask.any(axis=1)]
        
        # ✅ Reemplazo sin advertencia futura
        df = df.replace("None", 0)
        df = df.fillna(0)
        df = df.infer_objects(copy=False)
       
        df["CATEGORIA"] = "Check in"
        df["JUGADOR"] = df["JUGADOR"].str.upper()

    return df

def get_dataframe_columns(dataframe):
    dataframe_columns = dataframe.columns.tolist()
    return dataframe_columns

def getJoinedDataFrame(df_datos, df_data_test):
    #df_datos, df_data_test = getData(conn)
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
    #df_data_test[columnas_filtradas] = df_data_test[columnas_filtradas].apply(lambda col: col.astype(str).str.replace(r"[,-]", ".", regex=True).astype(float))
    df_data_test = limpiar_columnas_numericas(df_data_test, columnas_filtradas)

    # # Reemplazar valores nulos o 'None' por 0
    df_data_test = df_data_test.fillna(0).replace("None", 0)

    # Eliminar filas donde todos los valores son 0
    #df_data_test = df_data_test.loc[:, (df_data_test != 0).any(axis=0)]
    df_data_test = df_data_test.astype({ "JUGADOR": str })  # o ajusta a tus columnas específicas

    return df_data_test

def merge_by_nombre_categoria(df_unido, df_nuevo):
    """
    Une dos DataFrames con estructura similar usando 'JUGADOR' y 'CATEGORIA' como claves.
    - Conserva el orden y columnas de df_unido.
    - Llena columnas faltantes en df_nuevo con NaN o 0 según tipo.
    - Limpia solo columnas numéricas.
    - Mantiene los valores originales de JUGADOR y CATEGORIA.
    """
    if df_unido.empty or df_nuevo.empty:
        return pd.DataFrame()

    # === Columnas que NO deben tocarse durante limpieza ===
    columnas_excluidas = ["FECHA REGISTRO", "ID", "EQUIPO", "TEST", "JUGADOR", "CATEGORIA"]
    columnas_estructura = get_dataframe_columns(df_nuevo)
    columnas_filtradas = [col for col in columnas_estructura if col not in columnas_excluidas]

    # === Procesamiento de fechas ===
    df_nuevo["FECHA REGISTRO"] = pd.to_datetime(df_nuevo["FECHA REGISTRO"], errors='coerce', dayfirst=True)
    df_nuevo["anio"] = df_nuevo["FECHA REGISTRO"].dt.year.astype(str)
    df_nuevo["mes"] = df_nuevo["FECHA REGISTRO"].dt.month.astype(str)
    df_nuevo = df_nuevo.sort_values(by="FECHA REGISTRO", ascending=False)
    df_nuevo["FECHA REGISTRO"] = df_nuevo["FECHA REGISTRO"].dt.strftime('%d/%m/%Y')

    # === Limpieza SOLO de columnas numéricas ===
    df_nuevo = limpiar_columnas_numericas(df_nuevo, columnas_filtradas)
    df_nuevo[columnas_filtradas] = df_nuevo[columnas_filtradas].fillna(0).replace("None", 0)

    # === Asegurar tipo texto correcto en claves ===
    df_nuevo["JUGADOR"] = df_nuevo["JUGADOR"].astype(str).str.strip()
    df_nuevo["CATEGORIA"] = df_nuevo["CATEGORIA"].astype(str).str.strip()

    # === Asegurar que df_nuevo tenga todas las columnas de df_unido ===
    columnas_faltantes = [col for col in df_unido.columns if col not in df_nuevo.columns]
    for col in columnas_faltantes:
        if df_unido[col].dtype.kind in "iufc":  # numérico
            df_nuevo[col] = 0
        else:
            df_nuevo[col] = None

    # === Reordenar columnas en el orden de df_unido ===
    df_nuevo = df_nuevo[df_unido.columns]

    # === Concatenar ===
    df_final = pd.concat([df_unido, df_nuevo], ignore_index=True)

    # === Eliminar duplicados si corresponde ===
    df_final = df_final.drop_duplicates(subset=["JUGADOR", "CATEGORIA", "FECHA REGISTRO"], keep="last")

    return df_final

def limpiar_columnas_numericas(df, columnas_filtradas):
    for col in columnas_filtradas:
        # Reemplaza comas y guiones por puntos, convierte a numérico (NaN si falla)
        df[col] = (
            df[col]
            .astype(str)
            .str.replace(r"[,-]", ".", regex=True)
            .pipe(pd.to_numeric, errors="coerce")
        )
    
    return df

def columnas_sin_datos_utiles(df, columnas_excluidas=None, mostrar_alerta=False, mensaje="❗ No hay datos útiles en las columnas seleccionadas."):
    """
    Verifica si todas las celdas (excepto columnas excluidas) son NaN, None o 0.

    Args:
        df (pd.DataFrame): DataFrame a validar.
        columnas_excluidas (list): Lista de columnas a ignorar.
        mostrar_alerta (bool): Si True, muestra advertencia en Streamlit.
        mensaje (str): Texto de advertencia a mostrar.

    Returns:
        bool: True si todas las celdas útiles son NaN, None o 0. False en caso contrario.
    """
    if df.empty:
        return True

    columnas_estructura = get_dataframe_columns(df)

    # Si no se pasa una lista, usar lista vacía
    columnas_excluidas = columnas_excluidas or []

    # Eliminar columnas excluidas
    columnas_filtradas = [col for col in columnas_estructura if col not in columnas_excluidas]

    if not columnas_filtradas:
        return True  # Nada que validar

    try:
        todos_vacios_o_ceros = (
            df[columnas_filtradas]
            .map(lambda x: pd.isna(x) or x == 0)
            .all()
            .all()
        )

        if todos_vacios_o_ceros and mostrar_alerta:
            st.warning(mensaje)

        return todos_vacios_o_ceros

    except KeyError as e:
        st.error(f"❌ Columnas no encontradas: {e}")
        return True

def get_metricas_por_test(df_estructura, tests_seleccionados):
    """
    Devuelve una lista única de métricas asociadas a los tests seleccionados,
    según la estructura del DataFrame.

    Args:
        df_estructura (pd.DataFrame): DataFrame con columnas como tipos de test,
                                      y filas como métricas asociadas.
        tests_seleccionados (list): Lista de nombres de tests seleccionados (columnas del DataFrame).

    Returns:
        list: Lista única de métricas (valores no nulos) asociadas a los tests.
    """
    if not tests_seleccionados:
        return []

    metricas = []

    for test in tests_seleccionados:
        if test in df_estructura.columns:
            metricas.extend(df_estructura[test].dropna().tolist())

    # 🔥 Eliminar duplicados respetando el orden de aparición
    metricas_unicas = list(dict.fromkeys(metricas))

    return metricas_unicas

def get_new(datos_jugadores, df_existente, columnas_datos, fecha=None):
    """
    Genera un nuevo DataFrame con la estructura de 'df_existente',
    agregando registros faltantes por combinación (JUGADOR + CATEGORIA + FECHA REGISTRO),
    y asignando correctamente la fecha si se especifica.

    Siempre ordena por FECHA REGISTRO de menor a mayor
    y coloca la columna JUGADOR justo después de ID.

    Args:
        datos_jugadores (pd.DataFrame): Nuevos registros a insertar.
        df_existente (pd.DataFrame): DataFrame original con estructura base.
        columnas_datos (list): Columnas clave a mantener desde los datos de origen.
        fecha (str, opcional): Fecha única para asignar a nuevos registros. Formato: 'dd/mm/yyyy'.

    Returns:
        pd.DataFrame: DataFrame combinado y ordenado por 'FECHA REGISTRO' y 'JUGADOR'.
    """
    
    columnas_estructura = get_dataframe_columns(df_existente)
    if "JUGADOR" not in columnas_estructura:
        columnas_estructura.insert(2, "JUGADOR")

    # === Añadir JUGADOR a df_existente si falta ===
    if "JUGADOR" not in df_existente.columns and "ID" in df_existente.columns:
        if "ID" in datos_jugadores.columns and "JUGADOR" in datos_jugadores.columns:
            id_to_nombre = datos_jugadores.set_index("ID")["JUGADOR"].to_dict()
            df_existente["JUGADOR"] = df_existente["ID"].map(id_to_nombre)

    # === Añadir CATEGORIA a df_existente si falta ===
    if "CATEGORIA" not in df_existente.columns and "ID" in df_existente.columns:
        if "ID" in datos_jugadores.columns and "CATEGORIA" in datos_jugadores.columns:
            id_to_categoria = datos_jugadores.set_index("ID")["CATEGORIA"].to_dict()
            df_existente["CATEGORIA"] = df_existente["ID"].map(id_to_categoria)

    # Asegurar tipos string consistentes
    for col in ["JUGADOR", "CATEGORIA"]:
        if col in datos_jugadores.columns:
            datos_jugadores[col] = datos_jugadores[col].astype(str)
        if col in df_existente.columns:
            df_existente[col] = df_existente[col].astype(str)

    # === MODO 1: Se pasa una única fecha ===
    if fecha:
        #existentes = df_existente[["ID"]].drop_duplicates()
        nuevos = datos_jugadores[~datos_jugadores["ID"].isin(df_existente["ID"])].copy()

        df_nuevo = pd.DataFrame(columns=columnas_estructura)
        for col in columnas_datos:
            if col in df_nuevo.columns and col in nuevos.columns:
                df_nuevo[col] = nuevos[col]

        df_nuevo["JUGADOR"] = nuevos["JUGADOR"]
        df_nuevo["CATEGORIA"] = nuevos["CATEGORIA"]
        df_nuevo["FECHA REGISTRO"] = fecha

    # === MODO 2: Detectar sesiones faltantes ===
    else:
        fechas_existentes = df_existente["FECHA REGISTRO"].dropna().unique().tolist()
        fechas_existentes = [f for f in fechas_existentes if isinstance(f, str)]

        jugadores_categoria = datos_jugadores[["JUGADOR", "CATEGORIA", "ID"]].drop_duplicates()

        combinaciones = pd.MultiIndex.from_product(
            [jugadores_categoria["JUGADOR"], jugadores_categoria["CATEGORIA"], fechas_existentes],
            names=["JUGADOR", "CATEGORIA", "FECHA REGISTRO"]
        ).to_frame(index=False)

        existentes = df_existente[["JUGADOR", "CATEGORIA", "FECHA REGISTRO"]].drop_duplicates()
        faltantes = combinaciones.merge(existentes, on=["JUGADOR", "CATEGORIA", "FECHA REGISTRO"], how="left", indicator=True)
        faltantes = faltantes[faltantes["_merge"] == "left_only"].drop(columns="_merge")

        df_nuevo = faltantes.merge(jugadores_categoria, on=["JUGADOR", "CATEGORIA"], how="left")
        df_nuevo = df_nuevo.merge(datos_jugadores, on=["ID", "JUGADOR", "CATEGORIA"], how="left")

    
    # === Finalizar df_nuevo ===
    if not df_nuevo.empty:
        if "FECHA REGISTRO" not in df_nuevo.columns:
            df_nuevo["FECHA REGISTRO"] = None

        df_nuevo = df_nuevo.drop_duplicates(subset=["JUGADOR", "CATEGORIA", "FECHA REGISTRO"])

        for col in columnas_estructura:
            if col not in df_nuevo.columns:
                df_nuevo[col] = None

        df_nuevo = df_nuevo[columnas_estructura]

        if "ID" in df_nuevo.columns:
            df_nuevo["ID"] = df_nuevo["ID"].astype(str)

        df_nuevo = df_nuevo[df_nuevo["FECHA REGISTRO"].notna()]
    else:
        df_nuevo = pd.DataFrame(columns=columnas_estructura)

    df_existente = df_existente.reset_index(drop=True)
    #st.dataframe(df_existente)
    # === Combinar ===
    df_final = pd.concat([df_existente, df_nuevo], ignore_index=True)
   

    # === Ordenar por fecha y jugador ===
    if "FECHA REGISTRO" in df_final.columns:
        df_final["FECHA REGISTRO"] = pd.to_datetime(df_final["FECHA REGISTRO"], format="%d/%m/%Y", errors="coerce")
        df_final = df_final.sort_values(by=["FECHA REGISTRO", "JUGADOR"]).reset_index(drop=True)
        df_final["FECHA REGISTRO"] = df_final["FECHA REGISTRO"].dt.strftime("%d/%m/%Y")

    # === Reordenar columnas: JUGADOR justo después de ID ===
    if "ID" in df_final.columns and "JUGADOR" in df_final.columns:
        cols = df_final.columns.tolist()
        cols.remove("JUGADOR")
        idx = cols.index("ID") + 1
        cols.insert(idx, "JUGADOR")
        df_final = df_final[cols]

    return df_final


def get_data_editor(df_nuevo, key=None, num_rows_user="fixed"):
    edited_df = st.data_editor(df_nuevo, key=key, column_config={
            "TEST": st.column_config.SelectboxColumn(
                label="TEST",
                options=["ENDURANCE I", "ENDURANCE II", "RECOVERY I", "RECOVERY II"],
                required=True,
                width="medium"
            )
        },num_rows=num_rows_user,
        hide_index=True) # 👈 An editable dataframe
    return edited_df

def separar_dataframe_por_estructura(df_general, df_estructura, columnas_usadas):
    """
    Separa automáticamente un DataFrame grande en múltiples DataFrames,
    añadiendo siempre columnas clave al inicio y eliminando registros
    donde todas las métricas específicas sean NaN, None o 0.

    Args:
        df_general (DataFrame): El DataFrame con todas las métricas.
        df_estructura (DataFrame): El DataFrame que define cómo separar.
        columnas_usadas (list): Columnas clave que siempre deben incluirse.

    Returns:
        dict: {nombre_hoja: DataFrame filtrado con columnas específicas}
    """
    hojas_separadas = {}

    for hoja in df_estructura.columns:
        # 1. Obtener métricas asociadas a esta hoja
        columnas_metrica = df_estructura[hoja].dropna().tolist()

        # 2. Validar columnas existentes en df_general
        columnas_existentes = [col for col in columnas_metrica if col in df_general.columns]

        # 3. Combinar con columnas clave
        columnas_finales = columnas_usadas + columnas_existentes

        # 4. Respetar el orden original de df_general
        columnas_finales = [col for col in df_general.columns if col in columnas_finales]

        if columnas_existentes:
            df_hoja = df_general[columnas_finales].copy()

            # 5. Filtrar registros donde todas las métricas son NaN/None o 0
            metricas_validas = df_hoja[columnas_existentes].applymap(lambda x: pd.isna(x) or x == 0)
            filas_a_mantener = ~metricas_validas.all(axis=1)

            df_hoja_filtrado = df_hoja[filas_a_mantener].copy()

            hojas_separadas[hoja] = df_hoja_filtrado
        else:
            hojas_separadas[hoja] = pd.DataFrame()

    return hojas_separadas



######################

def actualizar_datos_con_checkin(df_datos, df_checkin, df_joined):
    """
    Actualiza el DataFrame df_datos con nuevos registros desde df_checkin,
    manteniendo la estructura original y eliminando duplicados. Luego realiza merge con df_joined.

    Parámetros:
        df_datos (pd.DataFrame): DataFrame original con datos existentes.
        df_checkin (pd.DataFrame): DataFrame de nuevos registros (check-in).
        df_joined (pd.DataFrame): DataFrame a combinar tras limpieza.

    Retorna:
        pd.DataFrame: DataFrame final actualizado y combinado.
    """

    # 1. Extraer columnas necesarias y eliminar duplicados
    df_nuevos = df_checkin[["JUGADOR", "CATEGORIA"]].drop_duplicates()

    # 2. Alinear estructura de columnas
    df_nuevos = df_nuevos.reindex(columns=df_datos.columns)

    # 3. Marcar el origen de cada DataFrame
    df_datos["PRIORIDAD"] = "1"
    df_nuevos["PRIORIDAD"] = "0"

    # 4. Concatenar
    df_resultado = pd.concat([df_datos, df_nuevos], ignore_index=True)

    # 5. Eliminar duplicados por JUGADOR y CATEGORIA, manteniendo solo los que vienen de df_datos
    df_resultado = df_resultado.sort_values(by="PRIORIDAD", ascending=False)  # "datos" < "nuevos"
    df_resultado = df_resultado.drop_duplicates(subset=["JUGADOR", "CATEGORIA"], keep="first")

    # 6. Eliminar la columna auxiliar
    df_resultado = df_resultado.drop(columns="PRIORIDAD").reset_index(drop=True)

    # 7. Eliminar filas completamente vacías
    df_resultado = df_resultado.dropna(how="all").reset_index(drop=True)

    # 8. Realizar merge con df_joined
    df_final = merge_by_nombre_categoria(df_joined, df_checkin)

    return df_final, df_resultado

def filtrar_por_rango_fechas(df, columna_fecha, fecha_inicio, fecha_fin, formato="%d/%m/%Y"):
    """
    Filtra un DataFrame por un rango de fechas, manteniendo la columna de fechas como string.
    Si la fecha de inicio y fin son iguales, no se aplica filtro.

    Parámetros:
        df (pd.DataFrame): DataFrame original.
        columna_fecha (str): Nombre de la columna que contiene fechas como string.
        fecha_inicio (datetime.date): Fecha inicial del rango.
        fecha_fin (datetime.date): Fecha final del rango.
        formato (str): Formato de fecha en el DataFrame (por defecto: "%d/%m/%Y").

    Retorna:
        pd.DataFrame: DataFrame filtrado, con la columna de fecha como string y sin columnas auxiliares.
    """
    df_temp = df.copy()
    df_temp["FECHA DT"] = pd.to_datetime(df_temp[columna_fecha], format=formato, errors="coerce")

    if fecha_inicio == fecha_fin:
        filtrado = df_temp  # No se filtra si ambas fechas son iguales
    else:
        filtrado = df_temp[
            (df_temp["FECHA DT"].dt.date >= fecha_inicio) &
            (df_temp["FECHA DT"].dt.date <= fecha_fin)
        ]

    return filtrado.drop(columns=["FECHA DT"])

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
        filters["CATEGORIA"] = st.selectbox("CATEGORÍA:", options=[default_option] + category_list, index=0, key="categoria")
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
    df = df.reset_index(drop=True)
    return df

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

def aplicar_semaforo(df, exclude_columns=["FECHA REGISTRO"], invertir=False):
    """
    Aplica un formato de color semáforo a un DataFrame.

    - Verde: mejor valor (según invertir).
    - Rojo: peor valor.
    - Amarillo: intermedio.
    - Blanco para columnas excluidas o valores NaN.

    Parámetros:
    df : pd.DataFrame
    exclude_columns : list -> columnas a excluir del formato.
    invertir : bool -> si True, valores bajos son mejores.

    Retorna:
    df.style
    """

    def semaforo(val, column):
        if column in exclude_columns or not np.issubdtype(df[column].dtype, np.number):
            return ''

        if pd.isna(val):
            return 'background-color: rgba(255, 255, 255, 0)'

        col_min = df[column].min()
        col_max = df[column].max()

        # Normalización
        if col_max != col_min:
            normalized = (val - col_min) / (col_max - col_min)
        else:
            normalized = 0.5  # todos iguales

        if invertir:
            normalized = 1 - normalized

        # Interpolar colores
        r = int(255 * (1 - normalized))
        g = int(255 * normalized)
        b = 0
        opacity = 0.4

        return f'background-color: rgba({r}, {g}, {b}, {opacity})'

    styled_df = df.style.apply(lambda x: [semaforo(val, x.name) for val in x], axis=0)

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

def sesiones_por_test(df_joined, test_categorias):
    """
    Cuenta la cantidad de sesiones por jugador y categoría, y por tipo de test.
    También agrega la fecha de la última sesión registrada por cada jugador.

    Parámetros:
        df_joined (pd.DataFrame): DataFrame con los registros de sesiones.
        test_categorias (dict): Diccionario con los tipos de test y sus columnas asociadas.

    Retorna:
        pd.DataFrame: Cantidad de sesiones por jugador/categoría, tipo de test y su última sesión.
    """
    
    if df_joined.empty:
        return pd.DataFrame()
    
    df = pd.DataFrame(df_joined)

    # Verificar columnas esenciales
    columnas_requeridas = {"JUGADOR", "CATEGORIA", "FECHA REGISTRO"}
    if not columnas_requeridas.issubset(df.columns):
        return pd.DataFrame()

    # Convertir fecha
    df["FECHA REGISTRO"] = pd.to_datetime(df["FECHA REGISTRO"], errors='coerce', dayfirst=True)
    df = df.dropna(subset=["FECHA REGISTRO"])

    # Inicializar diccionario de resultados
    sesiones_dict = {"JUGADOR": [], "CATEGORIA": [], "ÚLTIMA SESIÓN": []}
    for test in test_categorias:
        sesiones_dict[test] = []

    # Agrupar por nombre y categoría
    for (jugador_nombre, categoria), datos_jugador in df.groupby(["JUGADOR", "CATEGORIA"]):
        sesiones_dict["JUGADOR"].append(jugador_nombre)
        sesiones_dict["CATEGORIA"].append(categoria)
        sesiones_dict["ÚLTIMA SESIÓN"].append(datos_jugador["FECHA REGISTRO"].max().strftime("%d/%m/%Y"))

        for test, columnas in test_categorias.items():
            columnas_validas = [col for col in columnas if col in datos_jugador.columns]
            if columnas_validas:
                sesiones_validas = datos_jugador[columnas_validas].apply(lambda x: (x != 0).any(), axis=1)
                sesiones_dict[test].append(sesiones_validas.sum())
            else:
                sesiones_dict[test].append(0)

    # Crear DataFrame final y ordenar
    sesiones_df = pd.DataFrame(sesiones_dict)
    sesiones_df["ÚLTIMA SESIÓN"] = pd.to_datetime(sesiones_df["ÚLTIMA SESIÓN"], format="%d/%m/%Y")
    sesiones_df = sesiones_df.sort_values(by="ÚLTIMA SESIÓN", ascending=False).reset_index(drop=True)
    sesiones_df["ÚLTIMA SESIÓN"] = sesiones_df["ÚLTIMA SESIÓN"].dt.strftime('%d/%m/%Y').astype(str)

    return sesiones_df

def obtener_columnas_unidas(test_cat, clave, columnas_fecha_registro):
    """
    Combina la columna 'FECHA REGISTRO' con las columnas de la lista asociada
    a 'clave' dentro del diccionario 'test_cat', evitando duplicados.

    Parámetros:
    - test_cat (dict): Diccionario que contiene listas de columnas por clave.
    - clave (str): Clave de la lista a extraer y unir con 'FECHA REGISTRO'.

    Retorna:
    - list: Lista de columnas con 'FECHA REGISTRO' al principio y sin duplicados.
    """
    lista_test_cat = list(test_cat.get(clave, []))
    columnas_unidas = columnas_fecha_registro + [col for col in lista_test_cat if col != "FECHA REGISTRO"]
    return columnas_unidas


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


def get_diccionario_test_categorias(conn):
    test = get_test(conn)
    test_cat = construir_diccionario_test_categorias(test)
    lista_columnas = test.columns.tolist()

    return test, test_cat, lista_columnas

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
        "CENTRAL": "DFC",
        "LATERAL DERECHO": "LD",
        "LATERAL IZQUIERDO": "LI",
        "MEDIOCENTRO DEFENSIVO": "MC",
        "MEDIOCENTRO": "MC",
        "MEDIAPUNTA": "MC",         
        "EXTREMO": "EX", 
        "EXTREMO IZQUIERDO": "EI", 
        "LATERAL DERECHO": "ED",
        "LATERAL": "LA",             
        "DELANTERO": "DC",
        "NO DISPONIBLE": "ND"
    }

    return MAPA_DEMARCACIONES

def convertir_m_s_a_km_h(df, metricas_m_s):
    """
    Añade columnas nuevas transformadas de m/s a km/h para las columnas indicadas.

    Args:
        df (pd.DataFrame): DataFrame original.
        metricas_m_s (list): Lista de nombres de columnas en m/s a convertir.

    Returns:
        pd.DataFrame: DataFrame con columnas nuevas en km/h.
    """
    df = df.copy()

    for col in metricas_m_s:
        if col in df.columns:
            import re
            nueva_col = re.sub(r"\s*\(M[/*]?S(EG)?\)", " (KM/H)", col, flags=re.IGNORECASE)
            df[nueva_col] = df[col] * 3.6

    return df

def calcular_promedios_filtrados(df, columnas_a_verificar):
    """
    Calcula el promedio por CATEGORIA y EQUIPO, ignorando valores 0 y NaN por columna.

    Args:
        df (pd.DataFrame): DataFrame con los datos originales.
        columnas_a_verificar (list): Lista de columnas sobre las que calcular promedios.

    Returns:
        pd.DataFrame: DataFrame con los promedios filtrados.
    """
    filas_promedio = []

    for (categoria, equipo), grupo in df.groupby(["CATEGORIA", "EQUIPO"]):
        fila = {"CATEGORIA": categoria, "EQUIPO": equipo}
        for columna in columnas_a_verificar:
            # Asegurarse de que sean valores numéricos
            datos_columna = pd.to_numeric(grupo[columna], errors="coerce")
            datos_validos = datos_columna[(datos_columna != 0) & (~datos_columna.isna())]
            fila[columna] = datos_validos.mean() if not datos_validos.empty else np.nan
        filas_promedio.append(fila)

    df_promedios = pd.DataFrame(filas_promedio)
    df_promedios = df_promedios.round(2)

    return df_promedios

TRADUCCIONES = {
    "PESO Y % GRASA": {
        "es": "PESO Y % GRASA",
        "en": "WEIGHT AND % FAT",
        "pt": "PESO E % DE GORDURA",
        "ar": "الوزن و٪ الدهون"
    },
    "Evolución de la Distancia Acumulada": {
        "en": "Evolution of Accumulated Distance",
        "it": "Evoluzione della Distanza Accumulata",
        "de": "Entwicklung der Zurückgelegten Distanz",
        "fr": "Évolution de la Distance Accumulée",
        "ca": "Evolució de la Distància Acumulada",
        "pt": "Evolução da Distância Acumulada",
        "ar": "تطور المسافة التراكمية"
    },
    "DISTANCIA ACUMULADA (M)": {
        "en": "ACCUMULATED DISTANCE (M)",
        "it": "DISTANZA ACCUMULATA (M)",
        "de": "ZURÜCKGELEGTE DISTANZ (M)",
        "fr": "DISTANCE ACCUMULÉE (M)",
        "ca": "DISTÀNCIA ACUMULADA (M)",
        "pt": "DISTÂNCIA ACUMULADA (M)",
        "ar": "المسافة التراكمية (متر)"
    },
    "Evolución de la Potencia Muscular de Salto (CMJ)": {
        "en": "Evolution of Jump Muscle Power (CMJ)",
        "it": "Evoluzione della Potenza Muscolare del Salto (CMJ)",
        "de": "Entwicklung der Sprungkraft (CMJ)",
        "fr": "Évolution de la Puissance Musculaire de Saut (CMJ)",
        "ca": "Evolució de la Potència Muscular del Salt (CMJ)",
        "pt": "Evolução da Potência Muscular do Salto (CMJ)",
        "ar": "تطور القوة العضلية للقفز (CMJ)"
    },
    "POTENCIA MUSCULAR DE SALTO (CMJ)": {
        "es": "POTENCIA MUSCULAR DE SALTO (CMJ)",
        "en": "JUMP MUSCULAR POWER (CMJ)",
        "pt": "POTÊNCIA MUSCULAR DO SALTO (CMJ)",
        "ar": "القوة العضلية للقفز (CMJ)"
    },
    "Evolución del Tiempo Total en Repeticiones de Sprint": {
        "en": "Evolution of Total Time in Sprint Repetitions",
        "it": "Evoluzione del Tempo Totale nelle Ripetizioni di Sprint",
        "de": "Entwicklung der Gesamtzeit bei Sprintwiederholungen",
        "fr": "Évolution du Temps Total lors des Répétitions de Sprint",
        "ca": "Evolució del Temps Total en Repeticions d'Esprint",
        "pt": "Evolução do Tempo Total em Repetições de Sprint",
        "ar": "تطور الوقت الإجمالي في تكرارات العدو"
    },
    "Evolución de la Velocidad en Repeticiones de Sprint": {
        "en": "Evolution of Speed in Sprint Repetitions",
        "it": "Evoluzione della Velocità nelle Ripetizioni di Sprint",
        "de": "Entwicklung der Geschwindigkeit bei Sprintwiederholungen",
        "fr": "Évolution de la Vitesse lors des Répétitions de Sprint",
        "ca": "Evolució de la Velocitat en Repeticions d'Esprint",
        "pt": "Evolução da Velocidade nas Repetições de Sprint",
        "ar": "تطور السرعة في تكرارات العدو السريع"
    },
    "Evolución de la Agilidad (IZQ y DER)": {
        "en": "Agility Evolution (LEFT & RIGHT)",
        "it": "Evoluzione dell'Agilità (SIN & DES)",
        "de": "Agilitätsentwicklung (LI & RE)",
        "fr": "Évolution de l'Agilité (GAUCHE & DROITE)",
        "ca": "Evolució de l'Agilitat (ESQ i DRE)",
        "pt": "Evolução da Agilidade (ESQ e DIR)",
        "ar": "تطور الرشاقة (يسار ويمين)"
    },
    "AGILIDAD (IZQ Y DER)": {
        "es": "AGILIDAD (IZQ Y DER)",
        "en": "AGILITY (LEFT AND RIGHT)",
        "pt": "AGILIDADE (ESQ E DIR)",
        "ar": "الرشاقة (يسار ويمين)"
    },
    "Evolución del Sprint": {
        "en": "Sprint Evolution",
        "it": "Evoluzione dello Sprint",
        "de": "Sprint-Entwicklung",
        "fr": "Évolution du Sprint",
        "ca": "Evolució de l'Sprint",
        "pt": "Evolução do Sprint",
        "ar": "تطور العدو السريع"
    },
    "SPRINT": {
        "en": "SPRINT EVOLUTION",
        "it": "EVOLUZIONE DELLO SPRINT",
        "de": "SPRINT-ENTWICKLUNG",
        "fr": "ÉVOLUTION DU SPRINT",
        "ca": "EVOLUCIÓ DE L'SPRINT",
        "pt": "EVOLUÇÃO DO SPRINT",
        "ar": "تطور العدو السريع"
    },
    "DIFERENCIA %": {
        "en": "DIFFERENCE %",
        "it": "DIFFERENZA %",
        "de": "DIFFERENZ %",
        "fr": "DIFFÉRENCE %",
        "ca": "DIFERÈNCIA %",
        "pt": "DIFERENÇA %",
        "ar": "النسبة المئوية للاختلاف"
    },
    "505-IZQ (SEG)": {
        "en": "505-LEFT (SEC)",
        "it": "505-SIN (SEC)",
        "de": "505-LI (SEK)",
        "fr": "505-GAUCHE (SEC)",
        "ca": "505-ESQ (SEG)",
        "pt": "505-ESQ (SEG)",
        "ar": "505-يسار (ثانية)"
    },
    "505-DER (SEG)": {
        "en": "505-RIGHT (SEC)",
        "it": "505-DES (SEC)",
        "de": "505-RE (SEK)",
        "fr": "505-DROITE (SEC)",
        "ca": "505-DRE (SEG)",
        "pt": "505-DIR (SEG)",
        "ar": "505-يمين (ثانية)"
    },
    "VELOCIDAD (M/S)": {
        "en": "SPEED (M/S)",
        "it": "VELOCITÀ (M/S)",
        "de": "GESCHWINDIGKEIT (M/S)",
        "fr": "VITESSE (M/S)",
        "ca": "VELOCITAT (M/S)",
        "pt": "VELOCIDADE (M/S)",
        "ar": "السرعة (م/ث)"
    },
    "TIEMPO (SEG)": {
        "en": "TIME (SEC)",
        "it": "TEMPO (SEC)",
        "de": "ZEIT (SEK)",
        "fr": "TEMPS (SEC)",
        "ca": "TEMPS (SEG)",
        "pt": "TEMPO (SEG)",
        "ar": "الوقت (ثانية)"
    },
    "TIEMPO 0-5M (SEG)": {
        "en": "TIME 0-5M (SEC)",
        "it": "TEMPO 0-5M (SEC)",
        "de": "ZEIT 0-5M (SEK)",
        "fr": "TEMPS 0-5M (SEC)",
        "ca": "TEMPS 0-5M (SEG)",
        "pt": "TEMPO 0-5M (SEG)",
        "ar": "الوقت 0-5م (ثانية)"
    },
    "TIEMPO 0-40M (SEG)": {
        "en": "TIME 0-40M (SEC)",
        "it": "TEMPO 0-40M (SEC)",
        "de": "ZEIT 0-40M (SEK)",
        "fr": "TEMPS 0-40M (SEC)",
        "ca": "TEMPS 0-40M (SEG)",
        "pt": "TEMPO 0-40M (SEG)",
        "ar": "الوقت 0-40م (ثانية)"
    },
    "VEL 0-5M (M/S)": {
        "en": "SPEED 0-5M (M/S)",
        "it": "VEL 0-5M (M/S)",
        "de": "GESCHW 0-5M (M/S)",
        "fr": "VIT 0-5M (M/S)",
        "ca": "VEL 0-5M (M/S)",
        "pt": "VEL 0-5M (M/S)",
        "ar": "السرعة 0-5م (م/ث)"
    },
    "VEL 0-40M (M/S)": {
        "en": "SPEED 0-40M (M/S)",
        "it": "VEL 0-40M (M/S)",
        "de": "GESCHW 0-40M (M/S)",
        "fr": "VIT 0-40M (M/S)",
        "ca": "VEL 0-40M (M/S)",
        "pt": "VEL 0-40M (M/S)",
        "ar": "السرعة 0-40م (م/ث)"
    },
    "ALTURA DE SALTO (CM)": {
        "en": "JUMP HEIGHT (CM)",
        "it": "ALTEZZA DEL SALTO (CM)",
        "de": "SPRUNGHÖHE (CM)",
        "fr": "HAUTEUR DE SAUT (CM)",
        "ca": "ALÇADA DEL SALT (CM)",
        "pt": "ALTURA DO SALTO (CM)",
        "ar": "ارتفاع القفزة (سم)"
    },
    "PROMEDIO": {
        "en": "AVERAGE",
        "it": "MEDIA",
        "de": "DURCHSCHNITT",
        "fr": "MOYENNE",
        "ca": "MITJANA",
        "pt": "MÉDIA",
        "ar": "المتوسط"
    },
    "Evolución del Peso y % Grasa": {
        "en": "Evolution of Weight and Fat %",
        "it": "Evoluzione del Peso e Grasso %",
        "de": "Entwicklung von Gewicht und Fett %",
        "fr": "Évolution du Poids et de la Graisse %",
        "ca": "Evolució del Pes i del Greix %",
        "pt": "Evolução do Peso e % de Gordura",
        "ar": "تطور الوزن ونسبة الدهون (%)"
    },
    "ZONA OPTIMA %": {
        "en": "OPTIMAL FAT ZONE %",
        "it": "ZONA OTTIMALE DI GRASSO %",
        "de": "OPTIMALE FETTZONE %",
        "fr": "ZONE OPTIMALE DE GRAISSE %",
        "ca": "ZONA ÒPTIMA DE GREIX %",
        "pt": "ZONA ÓTIMA DE GORDURA %",
        "ar": "منطقة الدهون المثلى (%)"
    },
    "Evolución de la Altura (cm)": {
        "en": "Height Evolution (cm)",
        "it": "Evoluzione dell'Altezza (cm)",
        "de": "Größenentwicklung (cm)",
        "fr": "Évolution de la Taille (cm)",
        "ca": "Evolució de l'Alçada (cm)",
        "pt": "Evolução da Altura (cm)",
        "ar": "تطور الطول (سم)"
    },
    "ALTURA OPTIMA": {
        "en": "OPTIMAL HEIGHT",
        "it": "ALTEZZA OTTIMALE",
        "de": "OPTIMALE KÖRPERGRÖSSE",
        "fr": "TAILLE OPTIMALE",
        "ca": "ALÇADA ÒPTIMA",
        "pt": "ALTURA ÓTIMA",
        "ar": "الطُول الأَمْثَل"
    },
    "TIEMPO OPTIMO": {
        "en": "OPTIMAL TIME",
        "it": "TEMPO OTTIMALE",
        "de": "OPTIMALE ZEIT",
        "fr": "TEMPS OPTIMAL",
        "ca": "TEMPS ÒPTIM",
        "pt": "TEMPO ÓTIMO",
        "ar": "الزَّمَن الأَمْثَل"
    },
    "DISTANCIA OPTIMA": {
        "en": "OPTIMAL DISTANCE",
        "it": "DISTANZA OTTIMALE",
        "de": "OPTIMALE DISTANZ",
        "fr": "DISTANCE OPTIMALE",
        "ca": "DISTÀNCIA ÒPTIMA",
        "pt": "DISTÂNCIA ÓTIMA",
        "ar": "المَسَافَة الأَمْثَل"
    },
    "VELOCIDAD OPTIMA": {
        "en": "OPTIMAL SPEED",
        "it": "VELOCITÀ OTTIMALE",
        "de": "OPTIMALE GESCHWINDIGKEIT",
        "fr": "VITESSE OPTIMALE",
        "ca": "VELOCITAT ÒPTIMA",
        "pt": "VELOCIDADE ÓTIMA",
        "ar": "السُّرْعَة الأَمْثَل"
    },

    # Secciones
    "COMPOSICIÓN CORPORAL": {
        "en": "BODY COMPOSITION",
        "it": "COMPOSIZIONE CORPOREA",
        "de": "KÖRPERZUSAMMENSETZUNG",
        "fr": "COMPOSITION CORPORELLE",
        "ca": "COMPOSICIÓ CORPORAL",
        "pt": "COMPOSIÇÃO CORPORAL",
        "ar": "تركيب الجسم"
    },
    "POTENCIA MUSCULAR (SALTO CON CONTRAMOVIMIENTO)": {
        "en": "MUSCULAR POWER (COUNTER MOVEMENT JUMP)",
        "it": "POTENZA MUSCOLARE (SALTO CONTRO MOVIMENTO)",
        "de": "MUSKELKRAFT (GEGENBEWEGUNGSSPRUNG)",
        "fr": "PUISSANCE MUSCULAIRE (SAUT À CONTRE-MOUVEMENT)",
        "ca": "POTÈNCIA MUSCULAR (SALT AMB CONTRAMOVIMENT)",
        "pt": "POTÊNCIA MUSCULAR (SALTO COM CONTRAMOVIMENTO)",
        "ar": "القدرة العضلية (قفزة مع حركة عكسية)"
    },
    "EVOLUCIÓN DEL SPRINT (0-5M)": {
        "en": "SPRINT EVOLUTION (0-5M)",
        "it": "EVOLUZIONE DELLO SPRINT (0-5M)",
        "de": "SPRINT-ENTWICKLUNG (0-5M)",
        "fr": "ÉVOLUTION DU SPRINT (0-5M)",
        "ca": "EVOLUCIÓ DE L'SPRINT (0-5M)",
        "pt": "EVOLUÇÃO DO SPRINT (0-5M)",
        "ar": "تطور السرعة (0-5م)"
    },
    "EVOLUCIÓN DEL SPRINT (0-40M)": {
        "en": "SPRINT EVOLUTION (0-40M)",
        "it": "EVOLUZIONE DELLO SPRINT (0-40M)",
        "de": "SPRINT-ENTWICKLUNG (0-40M)",
        "fr": "ÉVOLUTION DU SPRINT (0-40M)",
        "ca": "EVOLUCIÓ DE L'SPRINT (0-40M)",
        "pt": "EVOLUÇÃO DO SPRINT (0-40M)",
        "ar": "تطور السرعة (0-40م)"
    },
    "VELOCIDAD EN EL CAMBIO DE DIRECCIÓN (AGILIDAD 505)": {
        "en": "CHANGE OF DIRECTION SPEED (AGILITY 505)",
        "it": "VELOCITÀ DI CAMBIO DIREZIONE (AGILITÀ 505)",
        "de": "RICHTUNGSWECHSELGESCHWINDIGKEIT (AGILITÄT 505)",
        "fr": "VITESSE DE CHANGEMENT DE DIRECTION (AGILITÉ 505)",
        "ca": "VELOCITAT EN EL CANVI DE DIRECCIÓ (AGILITAT 505)",
        "pt": "VELOCIDADE NA MUDANÇA DE DIREÇÃO (AGILIDADE 505)",
        "ar": "السرعة في تغيير الاتجاه (رشاقة 505)"
    },
    "RESISTENCIA INTERMITENTE DE ALTA INTENSIDAD (YO-YO TEST)": {
        "en": "HIGH-INTENSITY INTERMITTENT ENDURANCE (YO-YO TEST)",
        "it": "RESISTENZA INTERMITTENTE AD ALTA INTENSITÀ (YO-YO TEST)",
        "de": "HOCHINTENSIVES INTERMITTIERENDES AUSDAUERTRAINING (YO-YO TEST)",
        "fr": "ENDURANCE INTERMITTENTE À HAUTE INTENSITÉ (YO-YO TEST)",
        "ca": "RESISTÈNCIA INTERMITENT D'ALTA INTENSITAT (TEST YO-YO)",
        "pt": "RESISTÊNCIA INTERMITENTE DE ALTA INTENSIDADE (TESTE YO-YO)",
        "ar": "التحمل المتقطع عالي الشدة (اختبار يو-يو)"
    },
    "CAPACIDAD DE REALIZAR SPRINT'S REPETIDOS (RSA)": {
        "en": "REPEATED SPRINT ABILITY (RSA)",
        "it": "CAPACITÀ DI SPRINT RIPETUTI (RSA)",
        "de": "WIEDERHOLTE SPRINTFÄHIGKEIT (RSA)",
        "fr": "CAPACITÉ DE SPRINTS RÉPÉTÉS (RSA)",
        "ca": "CAPACITAT DE REALITZAR ESPRINTS REPETITS (RSA)",
        "pt": "CAPACIDADE DE REALIZAR SPRINTS REPETIDOS (RSA)",
        "ar": "القدرة على تكرار العدو السريع (RSA)"
    },

    # Métricas con unidades
    "ALTURA-(CM)": {
        "en": "JUMP HEIGHT (CM)",
        "it": "ALTEZZA DEL SALTO (CM)",
        "de": "SPRUNGHÖHE (CM)",
        "fr": "HAUTEUR DE SAUT (CM)",
        "ca": "ALÇADA DEL SALT (CM)",
        "pt": "ALTURA (CM)",
        "ar": "الطول (سم)"
    },
    "ALTURA (CM)": {
        "en": "HEIGHT (CM)",
        "it": "ALTEZZA (CM)",
        "de": "KÖRPERGRÖSSE (CM)",
        "fr": "TAILLE (CM)",
        "ca": "ALÇADA (CM)",
        "pt": "ALTURA (CM)",
        "ar": "الطول (سم)"
    },
    "PESO (KG)": {
        "en": "WEIGHT (KG)",
        "it": "PESO (KG)",
        "de": "GEWICHT (KG)",
        "fr": "POIDS (KG)",
        "ca": "PES (KG)",
        "pt": "PESO (KG)",
        "ar": "الوزن (كغ)"
    },
    "GRASA (%)": {
        "en": "FAT (%)",
        "it": "GRASSO (%)",
        "de": "FETT (%)",
        "fr": "GRAISSE (%)",
        "ca": "GREIX (%)",
        "pt": "GORDURA (%)",
        "ar": "الدهون (%)"
    },

    # Datos personales
    "NACIONALIDAD": {
        "en": "NATIONALITY",
        "it": "NAZIONALITÀ",
        "de": "NATIONALITÄT",
        "fr": "NATIONALITÉ",
        "ca": "NACIONALITAT",
        "pt": "NACIONALIDADE",
        "ar": "الجنسية"
    },
    "F. DE NACIMIENTO": {
        "en": "BIRTH DATE",
        "it": "D. DI NASCITA",
        "de": "GEBURTSDATUM",
        "fr": "D. DE NAISSANCE",
        "ca": "D. DE NAIXEMENT",
        "pt": "D. DE NASCIMENTO",
        "ar": "تاريخ الميلاد"
    },
    "EDAD": {
        "en": "AGE",
        "it": "ETÀ",
        "de": "ALTER",
        "fr": "ÂGE",
        "ca": "EDAT",
        "pt": "IDADE",
        "ar": "العمر"
    },
    "DEMARCACIÓN": {
        "en": "POSITION",
        "it": "RUOLO",
        "de": "POSITION",
        "fr": "POSTE",
        "ca": "DEMARCACIÓ",
        "pt": "POSIÇÃO",
        "ar": "المركز"
    },
    "CATEGORIA": {
        "en": "CATEGORY",
        "it": "CATEGORIA",
        "de": "KATEGORIE",
        "fr": "CATÉGORIE",
        "ca": "CATEGORIA",
        "pt": "CATEGORIA",
        "ar": "الفئة"
    },
    "EQUIPO": {
        "en": "TEAM",
        "it": "SQUADRA",
        "de": "MANNSCHAFT",
        "fr": "ÉQUIPE",
        "ca": "EQUIP",
        "pt": "EQUIPE",
        "ar": "الفريق"
    },

    # Escala visual
    "Escala de valoración": {
        "en": "Assessment Scale",
        "it": "Scala di valutazione",
        "de": "Bewertungsskala",
        "fr": "Échelle d'évaluation",
        "ca": "Escala de valoració",
        "pt": "Escala de Avaliação",
        "ar": "مقياس التقييم"
    },
    "Óptimo": {
        "en": "Optimal",
        "it": "Ottimale",
        "de": "Optimal",
        "fr": "Optimal",
        "ca": "Òptim",
        "pt": "Ótimo",
        "ar": "مثالي"
    },
    "Promedio": {
        "en": "Average",
        "it": "Media",
        "de": "Durchschnitt",
        "fr": "Moyenne",
        "ca": "Promig",
        "pt": "Média",
        "ar": "متوسط"
    },
    "Crítico": {
        "en": "Critical",
        "it": "Critico",
        "de": "Kritisch",
        "fr": "Critique",
        "ca": "Crític",
        "pt": "Crítico",
        "ar": "حرج"
    },
    "DEPARTAMENTO DE OPTIMIZACIÓN DEL RENDIMIENTO DEPORTIVO": {
        "en": "DEPARTMENT OF SPORTS PERFORMANCE OPTIMIZATION",
        "it": "DIPARTIMENTO DI OTTIMIZZAZIONE DELLE PRESTAZIONI SPORTIVE",
        "de": "ABTEILUNG FÜR OPTIMIERUNG DER SPORTLICHEN LEISTUNG",
        "fr": "DÉPARTEMENT D'OPTIMISATION DE LA PERFORMANCE SPORTIVE",
        "ca": "DEPARTAMENT D'OPTIMITZACIÓ DEL RENDIMENT ESPORTIU",
        "pt": "DEPARTAMENTO DE OTIMIZAÇÃO DO DESEMPENHO ESPORTIVO",
        "ar": "قسم تحسين الأداء الرياضي"
    },
    "INFORME INDIVIDUAL - INFORME FÍSICO": {
        "en": "INDIVIDUAL REPORT - PHYSICAL REPORT",
        "it": "RAPPORTO INDIVIDUALE - RAPPORTO FISICO",
        "de": "EINZELBERICHT - PHYSISCHER BERICHT",
        "fr": "RAPPORT INDIVIDUEL - RAPPORT PHYSIQUE",
        "ca": "INFORME INDIVIDUAL - INFORME FÍSIC",
        "pt": "RELATÓRIO INDIVIDUAL - RELATÓRIO FÍSICO",
        "ar": "تقرير فردي - تقرير بدني"
    },

    # Demarcaciones
    "PORTERO": {
        "en": "GOALKEEPER", "it": "PORTIERE", "de": "TORWART", "fr": "GARDIEN", "ca": "PORTER",
        "pt": "GOLEIRO", "ar": "حارس مرمى"
    },
    "LATERAL DERECHO": {
        "en": "RIGHT BACK", "it": "TERZINO DESTRO", "de": "RECHTER VERTEIDIGER", "fr": "LATÉRAL DROIT", "ca": "LATERAL DRET",
        "pt": "LATERAL DIREITO", "ar": "ظهير أيمن"
    },
    "LATERAL IZQUIERDO": {
        "en": "LEFT BACK", "it": "TERZINO SINISTRO", "de": "LINKER VERTEIDIGER", "fr": "LATÉRAL GAUCHE", "ca": "LATERAL ESQUERRE",
        "pt": "LATERAL ESQUERDO", "ar": "ظهير أيسر"
    },
    "DEFENSA CENTRAL": {
        "en": "CENTER BACK", "it": "DIFENSORE CENTRALE", "de": "INNENVERTEIDIGER", "fr": "DÉFENSEUR CENTRAL", "ca": "DEFENSA CENTRAL",
        "pt": "ZAGUEIRO CENTRAL", "ar": "قلب دفاع"
    },
    "MEDIOCENTRO DEFENSIVO": {
        "en": "DEFENSIVE MIDFIELDER", "it": "CENTROCAMPISTA DIFENSIVO", "de": "DEFENSIVER MITTELFELDSPIELER", "fr": "MILIEU DÉFENSIF", "ca": "PIVOT DEFENSIU",
        "pt": "VOLANTE DEFENSIVO", "ar": "وسط مدافع"
    },
    "MEDIOCENTRO": {
        "en": "MIDFIELDER", "it": "CENTROCAMPISTA", "de": "MITTELFELDSPIELER", "fr": "MILIEU", "ca": "CENTRECAMPISTA",
        "pt": "MEIO-CAMPISTA", "ar": "وسط"
    },
    "MEDIAPUNTA": {
        "en": "ATTACKING MIDFIELDER", "it": "TREQUARTISTA", "de": "OFFENSIVER MITTELFELDSPIELER", "fr": "MILIEU OFFENSIF", "ca": "MITJAPUNTA",
        "pt": "MEIA ATACANTE", "ar": "وسط هجومي"
    },
    "EXTREMO": {
        "en": "WINGER", "it": "ALA", "de": "FLÜGELSPIELER", "fr": "AILIER", "ca": "EXTREM",
        "pt": "PONTA", "ar": "جناح"
    },
    "DELANTERO": {
        "en": "FORWARD", "it": "ATTACCANTE", "de": "STÜRMER", "fr": "ATTAQUANT", "ca": "DAVANTER",
        "pt": "ATACANTE", "ar": "مهاجم"
    },
    # Categorías
    "CADETE": {
        "en": "CADET", "it": "CADETTO", "de": "KADETTE", "fr": "CADET", "ca": "CADET",
        "pt": "CADETE", "ar": "ناشئ"
    },
    "JUVENIL": {
        "en": "YOUTH", "it": "GIOVANILE", "de": "JUGEND", "fr": "JEUNE", "ca": "JUVENIL",
        "pt": "JUVENIL", "ar": "شباب"
    },
    "CHECK-IN": {
        "en": "CHECK-IN", "it": "CHECK-IN", "de": "CHECK-IN", "fr": "CHECK-IN", "ca": "CHECK-IN",
        "pt": "CHECK-IN", "ar": "تسجيل الدخول"
    },
    "CHECK IN": {
        "en": "CHECK IN", "it": "CHECK IN", "de": "CHECK IN", "fr": "CHECK IN", "ca": "CHECK IN",
        "pt": "CHECK IN", "ar": "تسجيل الدخول"
    },

    "LATERAL": {
        "es": "LATERAL",
        "en": "FULLBACK",
        "fr": "LATÉRAL",
        "it": "TERZINO",
        "de": "AUSSENVERTEIDIGER",
        "ca": "LATERAL",
        "pt": "LATERAL",
        "ar": "الظهير"
    },
    "EXTREMO DERECHO": {
        "es": "EXTREMO DERECHO",
        "en": "RIGHT WINGER",
        "fr": "AILIER DROIT",
        "it": "ALA DESTRA",
        "de": "RECHTSAUSSEN",
        "ca": "EXTREM DRET",
        "pt": "EXTREMO DIREITO",
        "ar": "الجناح الأيمن"
    },
    "EXTREMO IZQUIERDO": {
        "es": "EXTREMO IZQUIERDO",
        "en": "LEFT WINGER",
        "fr": "AILIER GAUCHE",
        "it": "ALA SINISTRA",
        "de": "LINKSAUSSEN",
        "ca": "EXTREM ESQUERRE",
        "pt": "EXTREMO ESQUERDO",
        "ar": "الجناح الأيسر"
    },


    "ANTROPOMETRIA": {
        "en": "ANTHROPOMETRY",
        "it": "ANTROPOMETRIA",
        "de": "ANTHROPOMETRIE",
        "fr": "ANTHROPOMÉTRIE",
        "ca": "ANTROPOMETRIA",
        "pt": "ANTROPOMETRIA",
        "ar": "القياسات الجسمية"
    },
    "AGILIDAD": {
        "en": "AGILITY",
        "it": "AGILITÀ",
        "de": "AGILITÄT",
        "fr": "AGILITÉ",
        "ca": "AGILITAT",
        "pt": "AGILIDADE",
        "ar": "رشاقة"
    },
    "REPORTE": {
        "en": "REPORT",
        "it": "RAPPORTO",
        "de": "BERICHT",
        "fr": "RAPPORT",
        "ca": "INFORME",
        "pt": "RELATÓRIO",
        "ar": "تقرير"
    },
    "años": {
        "en": "years old",
        "it": "anni",
        "de": "Jahre alt",
        "fr": "ans",
        "ca": "anys",
        "pt": "anos",
        "ar": "سنة"
    },
    "Max": {
        "en": "Max",
        "it": "Max",
        "de": "Max",
        "fr": "Max",
        "ca": "Max",
        "pt": "Max",
        "ar": "ماكس"
    },
    "Min:": {
        "en": "Min:",
        "it": "Minimo:",
        "de": "Minimal:",
        "fr": "Min :",
        "ca": "Mínim:",
        "pt": "Mínimo:",
        "ar": "الحد الأدنى:"
    },
    "ID": {
        "en": "ID",
        "it": "ID",
        "de": "ID",
        "fr": "ID",
        "ca": "ID",
        "pt": "ID",
        "ar": "معرّف"
    },
    "No Disponible": {
        "en": "Unavailable",
        "it": "Non disponibile",
        "de": "Nicht verfügbar",
        "fr": "Non disponible",
        "ca": "No disponible",
        "pt": "Indisponível",
        "ar": "غير متوفر"
    },
    "No disponible": {
        "en": "Unavailable",
        "it": "Non disponibile",
        "de": "Nicht verfügbar",
        "fr": "Non disponible",
        "ca": "No disponible",
        "pt": "Indisponível",
        "ar": "غير متوفر"
    },
    "OBSERVACIONES": {
        "es": "OBSERVACIONES",
        "en": "OBSERVATIONS",
        "it": "OSSERVAZIONI",
        "de": "BEOBACHTUNGEN",
        "fr": "OBSERVATIONS",
        "ca": "OBSERVACIONS",
        "pt": "OBSERVAÇÕES",
        "ar": "ملاحظات"
    }


}

def traducir(texto, idioma="es"):
    return TRADUCCIONES.get(texto, {}).get(idioma, texto)

def traducir_lista(palabras, idioma_destino="en"):
    palabras_traducidas = []
    for palabra in palabras:
        traduccion = TRADUCCIONES.get(palabra, {}).get(idioma_destino, palabra)
        palabras_traducidas.append(traduccion)
    return palabras_traducidas

def get_observacion_grasa(grasa):
    if grasa > 15:
        return ("Grasa corporal >15%: mayor riesgo de lesiones, fatiga precoz, menor eficiencia y rendimiento físico. "
                "Recomendamos seguimiento con nutricionista deportivo.")
    elif grasa < 7:
        return ("Grasa <7%: riesgo de lesiones, fatiga y desequilibrio hormonal. "
                "Recomendamos seguimiento con nutricionista deportivo.")
    else:
        return "Tu nivel de grasa corporal está en el rango ideal para un futbolista de alto rendimiento."

def get_observacion_cmj(valor_cmj, categoria):
    """
    Devuelve una frase interpretativa para el test de CMJ según la categoría ('Juvenil' o 'Cadete')
    y el valor de salto (en cm).
    """

    if valor_cmj is None or pd.isna(valor_cmj):
        return ""

    categoria = categoria.lower()

    if "juvenil" in categoria:
        if valor_cmj > 36:
            return (
                "Tu nivel en el CMJ está dentro del rango óptimo de rendimiento. "
                "El objetivo es mejorar la eficiencia en la técnica de salto y mantener o incrementar levemente el rendimiento."
            )
        elif 32 < valor_cmj <= 36:
            return (
                "Mejorar la eficiencia en la técnica de salto. "
                "Necesidad de trabajo de potencia de tren inferior."
            )
        elif valor_cmj <= 32:
            return (
                "Masa muscular insuficiente. "
                "Necesidad de trabajo de fuerza y potencia de tren inferior. "
                "Mejorar la técnica de salto."
            )

    elif "cadete" in categoria:
        if valor_cmj > 30:
            return (
                "Tu nivel en el CMJ está dentro del rango óptimo de rendimiento."
            )
        elif 26 < valor_cmj <= 30:
            return (
                "Mejorar la eficiencia en la técnica de salto. "
                "Necesidad de trabajo de potencia de tren inferior."
            )
        elif valor_cmj <= 26:
            return (
                "Masa muscular insuficiente. "
                "Necesidad de trabajo de fuerza y potencia de tren inferior. "
                "Mejorar la técnica de salto."
            )

    return ""

def get_observacion_sprint(valor_sprint, categoria):
    """
    Devuelve una observación interpretativa según el valor del sprint (0-40m en segundos)
    y la categoría ('Juvenil' o 'Cadete').
    """
    if valor_sprint is None or pd.isna(valor_sprint):
        return ""

    categoria = categoria.lower()

    if "juvenil" in categoria:
        if valor_sprint < 5.2:
            return "Tu nivel de fuerza horizontal para el sprint es excelente para tu edad y categoría."
        elif 5.2 <= valor_sprint < 5.8:
            return (
                "Necesidad de trabajo técnico de zancada y frecuencia de paso. "
                "Identificar si el déficit está en la aceleración inicial o en la fase de velocidad máxima. "
                "Mejorar tu potencia en tramos cortos."
            )
        else:  # valor_sprint >= 5.8
            return (
                "Tienes un margen muy grande de mejora en el trabajo de fuerza de tren inferior. "
                "Necesidad de trabajo técnico de zancada y frecuencia de paso. "
                "Es fundamental mejorar tu potencia en tramos cortos y largos."
            )

    elif "cadete" in categoria:
        if valor_sprint < 5.9:
            return "Tu nivel de fuerza horizontal para el sprint es excelente para tu edad y categoría."
        elif 5.9 <= valor_sprint < 6.2:
            return (
                "Necesidad de trabajo técnico de zancada y frecuencia de paso. "
                "Identificar si el déficit está en la aceleración inicial o en la fase de velocidad máxima. "
                "Mejorar tu potencia en tramos cortos."
            )
        else:  # valor_sprint >= 6.2
            return (
                "Tienes un margen muy grande de mejora en el trabajo de fuerza de tren inferior. "
                "Necesidad de trabajo técnico de zancada y frecuencia de paso. "
                "Es fundamental mejorar tu potencia en tramos cortos y largos."
            )

    return ""

def get_observacion_agilidad(valor_asimetria):
    """
    Devuelve una observación interpretativa basada en el porcentaje de asimetría funcional
    (diferencia entre piernas en el cambio de dirección), sin diferenciar por categoría.
    """
    if valor_asimetria is None or pd.isna(valor_asimetria):
        return ""

    if valor_asimetria <= 5:
        return (
            "El jugador presenta un nivel de simetría funcional adecuado (<5%) entre ambas piernas en el cambio de dirección."
        )
    elif 5 < valor_asimetria <= 8:
        return (
            "Ligera asimetría funcional entre ambas piernas en el cambio de dirección. "
            "Aunque se encuentra dentro de un rango aceptable, es recomendable aplicar estrategias preventivas para evitar que esta diferencia aumente y afecte el rendimiento o aumente el riesgo de lesión."
        )
    else:  # valor_asimetria > 8
        return (
            ". Asimetría >10% en el cambio de dirección representa:\n"
            "- Déficit de fuerza excéntrica y/o potencia reactiva\n"
            "- Necesidad de mejora de la técnica de frenado\n"
            "- Incremento en el riesgo de lesión musculoesquelética, sobre todo en isquiosurales y LCA.\n"
            "- Limitación de la capacidad de realizar acciones explosivas (con giros, fintas, driblings)\n\n"
            ". Recomendamos un plan específico de entrenamiento unilateral de la pierna deficitaria."
        )
