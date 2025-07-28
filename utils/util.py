import streamlit as st
import pandas as pd
import numpy as np
import requests
from datetime import datetime
from scipy.stats import percentileofscore
from functools import reduce
from utils import constants
import unicodedata

#from gspread_dataframe import get_as_dataframe, set_with_dataframe

def formatear_fecha(x):
    try:
        return x.strftime('%d/%m/%Y')
    except Exception:
        return None

def convertir_fecha_segura(valor):
    try:
        valor = str(valor).strip()
        fecha = pd.to_datetime(valor, format="%d/%m/%Y", errors="raise")
        return fecha.date()
    except Exception:
        print(f"❌ Fecha inválida: {valor}")
        return None

def rellenar_fechas_invalidas(df, columna="FECHA REGISTRO", formato="%d/%m/%Y"):
    """
    Reemplaza valores nulos o no válidos en una columna de fecha por la fecha actual (formato: dd/mm/yyyy).

    Args:
        df (pd.DataFrame): El DataFrame a procesar.
        columna (str): El nombre de la columna de fechas.
        formato (str): El formato de salida (por defecto: "%d/%m/%Y").

    Returns:
        pd.DataFrame: El DataFrame con la columna corregida.
    """
    hoy = datetime.today()

    # Convertir a datetime con errores como NaT
    df[columna] = pd.to_datetime(df[columna], errors="coerce", dayfirst=True)

    # Reemplazar valores inválidos con fecha actual
    df[columna] = df[columna].fillna(hoy)

    # Convertir nuevamente a string con el formato deseado
    df[columna] = df[columna].dt.strftime(formato)

    return df

def unir_dataframes(dfs, columnas_comunes, metodo='outer'):
    """
    Une una lista de DataFrames basándose en columnas comunes.

    Args:
        dfs (list): Lista de DataFrames a unir.
        columnas_comunes (list): Columnas comunes para hacer el merge.
        metodo (str): Tipo de unión ('outer' para no perder datos, 'inner' para intersección).

    Returns:
        pd.DataFrame: Un DataFrame combinado con columnas comunes al inicio.
    """
    if not dfs:
        raise ValueError("La lista de DataFrames está vacía.")

    dfs_validos = []

    for idx, df in enumerate(dfs):
        columnas_faltantes = [col for col in columnas_comunes if col not in df.columns]
        if columnas_faltantes:
            mensaje = f"⚠️ El DataFrame #{idx + 1} no contiene las columnas necesarias: {', '.join(columnas_faltantes)}. Será excluido."
            try:
                st.warning(mensaje)
            except:
                print(mensaje)
            continue
        # Limpiar duplicados por columnas comunes
        df = df.drop_duplicates(subset=columnas_comunes)
        df.drop(constants.JUGADOR_LABEL, axis=1, inplace=True, errors='ignore')

        dfs_validos.append(df)

    if not dfs_validos:
        raise ValueError("Ningún DataFrame contenía todas las columnas comunes necesarias.")

    # Merge secuencial
    df_final = reduce(lambda left, right: pd.merge(left, right, on=columnas_comunes, how=metodo), dfs_validos)

    # Eliminar filas donde TODAS las columnas NO comunes son NaN
    columnas_no_comunes = [col for col in df_final.columns if col not in columnas_comunes]
    df_final = df_final.dropna(subset=columnas_no_comunes, how='all')

    # Reordenar columnas
    columnas_ordenadas = columnas_comunes + [col for col in df_final.columns if col not in columnas_comunes]
    return df_final[columnas_ordenadas]

def es_numerico(val):
    try:
        return isinstance(val, (int, float)) and not pd.isna(val)
    except:
        return False
    
def get_dataframe_columns(dataframe):
    dataframe_columns = dataframe.columns.tolist()
    return dataframe_columns

def join_player_and_physical_data(df_datos, df_data_test):

    # Verificar si alguno de los DataFrames está vacío
    if df_datos.empty or df_data_test.empty:
        return pd.DataFrame()  # Retornar DataFrame vacío si alguno de los dos está vacío

    columnas_excluidas = ["FECHA REGISTRO", "ID", "CATEGORIA", "EQUIPO", "GENERO"]
    columnas_estructura = get_dataframe_columns(df_data_test)

    # Eliminar columnas excluidas
    columnas_filtradas = [col for col in columnas_estructura if col not in columnas_excluidas]

    # Asegurarse de insertar el nombre completo en la posición 2 si falta
    columna_nombre = "JUGADOR" 
    columna_genero = "GENERO" 
    
    # Si hay datos ya existentes, mapear nombres desde datos_jugadores
    if not df_data_test.empty:
        # Eliminar registros cuyo ID no está en df_datos
        df_data_test = df_data_test[df_data_test["ID"].isin(df_datos["ID"])]

        # Asegurar que la columna de nombres esté presente
        if columna_nombre not in df_data_test.columns:
            df_data_test.insert(2, columna_nombre, None)

        if columna_genero not in df_data_test.columns:
            df_data_test.insert(3, columna_genero, None)

        # Mapear nombres desde df_datos
        id_a_nombre = df_datos.set_index("ID")["JUGADOR"].to_dict()
        id_a_genero = df_datos.set_index("ID")["GENERO"].to_dict()
        df_data_test[columna_nombre] = df_data_test["ID"].map(id_a_nombre)
        df_data_test[columna_genero] = df_data_test["ID"].map(id_a_genero)

        # Eliminar registros ya existentes según ID
        #datos_jugadores = datos_jugadores[~datos_jugadores["ID"].isin(df_data_test["ID"])]

    #st.dataframe(df_data_test)
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

def limpiar_filas_sin_datos_validos(df, columnas_excluidas=None):
    """
    Elimina filas donde todas las columnas válidas (no excluidas) son NaN o 0.
    Si alguna columna esperada no existe, se muestra una advertencia.

    Args:
        df (pd.DataFrame): DataFrame a procesar.
        columnas_excluidas (list, optional): Columnas que no se validan. Por defecto:
            ['FECHA REGISTRO', 'ID', 'JUGADOR', 'CATEGORIA', 'EQUIPO', 'anio', 'mes']

    Returns:
        pd.DataFrame: DataFrame limpio, sin filas vacías o con ceros en columnas relevantes.
    """
    if columnas_excluidas is None:
        columnas_excluidas = ['FECHA REGISTRO', 'ID', 'JUGADOR', 'CATEGORIA', 'EQUIPO', 'anio', 'mes']

    # Columnas que intentaríamos validar (las que no están excluidas)
    todas_columnas = df.columns.tolist()
    columnas_a_validar = [col for col in todas_columnas if col not in columnas_excluidas]

    # Verificar columnas faltantes
    columnas_faltantes = [col for col in columnas_a_validar if col not in df.columns]
    if columnas_faltantes:
        mensaje = f"⚠️ Columnas no encontradas para validación: {', '.join(columnas_faltantes)}"
        try:
            st.warning(mensaje)
        except:
            print(mensaje)
        # Excluirlas de la validación para evitar errores
        columnas_a_validar = [col for col in columnas_a_validar if col in df.columns]

    if not columnas_a_validar:
        # Nada que validar, retornar sin cambios
        return df

    # Eliminar filas donde todas las columnas a validar son NaN
    df = df.dropna(subset=columnas_a_validar, how="all")

    # Eliminar filas donde todas las columnas a validar son 0
    mask = (df[columnas_a_validar] == 0).all(axis=1)
    df = df[~mask]

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
        faltantes = faltantes[faltantes["_merge"] == "left_only"].drop(columns="_merge", errors="ignore")

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
    df_datos_final = pd.concat([df_datos, df_nuevos], ignore_index=True)

    # 5. Eliminar duplicados por JUGADOR y CATEGORIA, manteniendo solo los que vienen de df_datos
    df_datos_final = df_datos_final.sort_values(by="PRIORIDAD", ascending=False)  # "datos" < "nuevos"
    df_datos_final = df_datos_final.drop_duplicates(subset=["JUGADOR", "CATEGORIA"], keep="first")

    # 6. Eliminar la columna auxiliar
    df_datos_final = df_datos_final.drop(columns="PRIORIDAD", errors="ignore").reset_index(drop=True)

    # 7. Eliminar filas completamente vacías
    df_datos_final = df_datos_final.dropna(how="all").reset_index(drop=True)

    # 8. Realizar merge con df_joined
    df_data_test_final = merge_by_nombre_categoria(df_joined, df_checkin)

    if not df_data_test_final.empty:
        # Mapear nombres desde df_datos
        id_a_genero = df_datos_final.set_index("JUGADOR")["GENERO"].to_dict()
        df_data_test_final["GENERO"] = df_data_test_final["JUGADOR"].map(id_a_genero)

    #st.dataframe(df_datos_final)
    return df_data_test_final, df_datos_final

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
    columnas_excluidas = ["FECHA REGISTRO", "ID", "EQUIPO", "TEST", "JUGADOR", "CATEGORIA", "GENERO"]
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
    df_final = df_final.drop_duplicates(subset=["JUGADOR", "GENERO" ,"CATEGORIA", "FECHA REGISTRO"], keep="last")

    return df_final

def filtrar_por_rango_fechas(df, columna_fecha, fecha_inicio, fecha_fin, formato="%d/%m/%Y"):
    """
    Filtra un DataFrame por un rango de fechas, manteniendo la columna de fechas como string.
    Si la columna no existe, se muestra una advertencia y se retorna el DataFrame original.

    Args:
        df (pd.DataFrame): DataFrame original.
        columna_fecha (str): Nombre de la columna que contiene fechas como string.
        fecha_inicio (datetime.date): Fecha inicial del rango.
        fecha_fin (datetime.date): Fecha final del rango.
        formato (str): Formato de fecha en el DataFrame (por defecto: "%d/%m/%Y").

    Returns:
        pd.DataFrame: DataFrame filtrado (o el original si la columna no existe).
    """
    if columna_fecha not in df.columns:
        mensaje = f"⚠️ La columna de fecha '{columna_fecha}' no existe en el DataFrame. No se aplicará filtro."
        try:
            st.warning(mensaje)
        except:
            print(mensaje)
        return df

    df_temp = df.copy()
    df_temp["FECHA DT"] = pd.to_datetime(df_temp[columna_fecha], format=formato, errors="coerce")

    if fecha_inicio == fecha_fin:
        filtrado = df_temp
    else:
        filtrado = df_temp[
            (df_temp["FECHA DT"].dt.date >= fecha_inicio) &
            (df_temp["FECHA DT"].dt.date <= fecha_fin)
        ]

    return filtrado.drop(columns=["FECHA DT"], errors="ignore")

# Utilidad para obtener lista única ordenada de una columna, con filtros
def get_filtered_list(dataframe, column, filters, default_option="Todos"):
    for col, val in filters.items():
        if val != default_option:
            dataframe = dataframe[dataframe[col] == val]
    valores_unicos = dataframe[column].dropna().astype(str).str.strip().unique().tolist()
    return sorted(limpiar_lista(valores_unicos))

def limpiar_lista(valores):
    """
    Elimina elementos vacíos, nulos o no informativos (NaN, None, '', 'nan', 'none') de una lista.
    """
    return [
        v for v in valores
        if pd.notna(v) and str(v).strip().lower() not in ["", "nan", "none"]
    ]

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
        df_filtrado = df_filtrado.reset_index(drop=True)
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


# Función para eliminar acentos
def quitar_acentos(texto):
    if not isinstance(texto, str):
        return texto
    # Descomposición Unicode
    texto_normalizado = unicodedata.normalize('NFD', texto)
    # Elimina tildes pero deja la ñ
    texto_sin_tildes = ''.join(
        c for c in texto_normalizado
        if unicodedata.category(c) != 'Mn' or c == '̃' and texto_normalizado[texto_normalizado.index(c)-1].lower() == 'n'
    )
    return texto_sin_tildes

def limpiar_nacionalidades(df):
    reemplazos = {
        "ESPANA": "ESPAÑA",
        "FEDERACIÓN RUSSA": "RUSIA",
        "FEDERACION RUSSA": "RUSIA",
        "R. DOMINICANA": "REPUBLICA DOMINICANA",
        "KENYA": "KENIA",
        "MOROCCO": "MARRUECOS"
    }

    # Normalizar texto y aplicar reemplazos
    df["NACIONALIDAD"] = (
        df["NACIONALIDAD"]
        .astype(str)
        .str.upper()
        .str.strip()
        .replace(reemplazos)
    )

    df["NACIONALIDAD"] = df["NACIONALIDAD"].astype(str).str.replace(",", ".", regex=False).str.strip()
    df['NACIONALIDAD'] = df['NACIONALIDAD'].apply(quitar_acentos)


    return df


def obtener_bandera(pais):
    # Diccionario de códigos de país ISO 3166-1 alfa-2
    paises = {
        "AFGANISTAN": "🇦🇫", "ALBANIA": "🇦🇱", "ALEMANIA": "🇩🇪", "ANDORRA": "🇦🇩",
        "ANGOLA": "🇦🇴","ANTIGUA Y BARBUDA": "🇦🇬", "ARABIA SAUDITA": "🇸🇦","ARGELIA": "🇩🇿",
        "ARGENTINA": "🇦🇷","ARMENIA": "🇦🇲", "AUSTRALIA": "🇦🇺","AUSTRIA": "🇦🇹","AZERBAIYAN": "🇦🇿",
        "BAHAMAS": "🇧🇸","BANGLADES": "🇧🇩","BARBADOS": "🇧🇧","BAREIN": "🇧🇭","BELGICA": "🇧🇪","BELICE": "🇧🇿","BENIN": "🇧🇯",
        "BIELORRUSIA": "🇧🇾","BIRMANIA": "🇲🇲","BOLIVIA": "🇧🇴","BOSNIA Y HERZEGOVINA": "🇧🇦","BOTSUANA": "🇧🇼","BRASIL": "🇧🇷",
        "BRUNEI": "🇧🇳","BULGARIA": "🇧🇬","BURKINA FASO": "🇧🇫","BURUNDI": "🇧🇮","BUTAN": "🇧🇹","CABO VERDE": "🇨🇻",
        "CAMBOYA": "🇰🇭","CAMERUN": "🇨🇲","CANADA": "🇨🇦","CATAR": "🇶🇦","CHAD": "🇹🇩","CHILE": "🇨🇱","CHINA": "🇨🇳","CHIPRE": "🇨🇾",
        "COLOMBIA": "🇨🇴","COMORAS": "🇰🇲","COREA DEL NORTE": "🇰🇵","COREA DEL SUR": "🇰🇷","COSTA DE MARFIL": "🇨🇮",
        "COSTA RICA": "🇨🇷","CROACIA": "🇭🇷","CUBA": "🇨🇺","DINAMARCA": "🇩🇰","DOMINICA": "🇩🇲","ECUADOR": "🇪🇨","EGIPTO": "🇪🇬",
        "EL SALVADOR": "🇸🇻","EMIRATOS ARABES UNIDOS": "🇦🇪","ERITREA": "🇪🇷","ESLOVAQUIA": "🇸🇰","ESLOVENIA": "🇸🇮",
        "ESPANA": "🇪🇸","ESTADOS UNIDOS": "🇺🇸","ESTONIA": "🇪🇪","ETIOPIA": "🇪🇹","FIJI": "🇫🇯","FILIPINAS": "🇵🇭",
        "FINLANDIA": "🇫🇮","FRANCIA": "🇫🇷","GABON": "🇬🇦","GAMBIA": "🇬🇲","GEORGIA": "🇬🇪","GHANA": "🇬🇭","GRANADA": "🇬🇩",
        "GRECIA": "🇬🇷","GUATEMALA": "🇬🇹","GUINEA": "🇬🇳","GUINEA BISSAU": "🇬🇼","GUINEA ECUATORIAL": "🇬🇶","GUYANA": "🇬🇾",
        "HAITI": "🇭🇹","HOLANDA": "🇳🇱","HONDURAS": "🇭🇳","HUNGRIA": "🇭🇺","INDIA": "🇮🇳","INDONESIA": "🇮🇩","INGLATERRA": "🇬🇧",
        "IRAK": "🇮🇶","IRAN": "🇮🇷","IRLANDA": "🇮🇪","ISLANDIA": "🇮🇸","ISLAS MARSHALL": "🇲🇭","ISLAS SALOMON": "🇸🇧",
        "ISLAS VIRGENES": "🇻🇬","ISRAEL": "🇮🇱","ITALIA": "🇮🇹","JAMAICA": "🇯🇲","JAPON": "🇯🇵","JORDANIA": "🇯🇴","KAZAJISTAN": "🇰🇿",
        "KENIA": "🇰🇪","KIRGUISTAN": "🇰🇬","KIRIBATI": "🇰🇮","KUWAIT": "🇰🇼","LAOS": "🇱🇦","LESOTO": "🇱🇸","LETONIA": "🇱🇻",
        "LIBANO": "🇱🇧","LIBERIA": "🇱🇷","LIBIA": "🇱🇾","LIECHTENSTEIN": "🇱🇮","LITUANIA": "🇱🇹","LUXEMBURGO": "🇱🇺",
        "MACEDONIA DEL NORTE": "🇲🇰","MADAGASCAR": "🇲🇬","MALASIA": "🇲🇾","MALAUI": "🇲🇼","MALDIVAS": "🇲🇻","MALI": "🇲🇱",
        "MALTA": "🇲🇹","MARRUECOS": "🇲🇦","MAURICIO": "🇲🇺","MAURITANIA": "🇲🇷","MEXICO": "🇲🇽","MICRONESIA": "🇫🇲",
        "MOLDAVIA": "🇲🇩","MONACO": "🇲🇨","MONGOLIA": "🇲🇳","MONTENEGRO": "🇲🇪","MOZAMBIQUE": "🇲🇿","NAMIBIA": "🇳🇦","NAURU": "🇳🇷",
        "NEPAL": "🇳🇵","NICARAGUA": "🇳🇮","NIGER": "🇳🇪","NIGERIA": "🇳🇬","NORUEGA": "🇳🇴","NUEVA ZELANDA": "🇳🇿","OMÁN": "🇴🇲",
        "PAISES BAJOS": "🇳🇱","PAKISTAN": "🇵🇰","PALAOS": "🇵🇼","PALESTINA": "🇵🇸","PANAMA": "🇵🇦","PAPUA NUEVA GUINEA": "🇵🇬",
        "PARAGUAY": "🇵🇾","PERU": "🇵🇪","POLINESIA FRANCESA": "🇵🇫","POLONIA": "🇵🇱","PORTUGAL": "🇵🇹","R. DOMINICANA": "🇩🇴",
        "R.D. DEL CONGO": "🇨🇩","R. DEL CONGO": "🇨🇬","REINO UNIDO": "🇬🇧","REPUBLICA CENTROAFRICANA": "🇨🇫",
        "REPUBLICA CHECA": "🇨🇿","RUANDA": "🇷🇼","RUMANIA": "🇷🇴","RUSIA": "🇷🇺","SAMOA": "🇼🇸","SAN CRISTOBAL Y NIEVES": "🇰🇳",
        "SAN MARINO": "🇸🇲","SAN VICENTE Y LAS GRANADINAS": "🇻🇨","SANTA LUCIA": "🇱🇨","SANTO TOME Y PRINCIPE": "🇸🇹",
        "SENEGAL": "🇸🇳","SERBIA": "🇷🇸","SEYCHELLES": "🇸🇨","SIERRA LEONA": "🇸🇱","SINGAPUR": "🇸🇬","SIRIA": "🇸🇾",
        "SOMALIA": "🇸🇴","SRI LANKA": "🇱🇰","SUAZILANDIA": "🇸🇿","SUDAFRICA": "🇿🇦","SUDAN": "🇸🇩","SUDAN DEL SUR": "🇸🇸",
        "SUECIA": "🇸🇪","SUIZA": "🇨🇭","SURINAM": "🇸🇷","TAILANDIA": "🇹🇭","TANZANIA": "🇹🇿","TAYIKISTAN": "🇹🇯",
        "TIMOR ORIENTAL": "🇹🇱","TOGO": "🇹🇬","TONGA": "🇹🇴","TRINIDAD Y TOBAGO": "🇹🇹","TUNEZ": "🇹🇳","TURKMENISTAN": "🇹🇲",
        "TURQUIA": "🇹🇷","TUVALU": "🇹🇻","UCRANIA": "🇺🇦","UGANDA": "🇺🇬","URUGUAY": "🇺🇾","UZBEKISTAN": "🇺🇿","VANUATU": "🇻🇺",
        "VATICANO": "🇻🇦","VENEZUELA": "🇻🇪","VIETNAM": "🇻🇳","YEMEN": "🇾🇪","YIBUTI": "🇩🇯","ZAMBIA": "🇿🇲","ZIMBABUE": "🇿🇼"
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
    return {
        "PORTERO": "POR",
        "PORTERA": "POR",
        "DEFENSA CENTRAL": "DFC",
        "CENTRAL": "DFC",
        "LATERAL DERECHO": "LD",
        "LATERAL IZQUIERDO": "LI",
        "MEDIOCENTRO DEFENSIVO": "MC",
        "MEDIOCENTRO": "MC",
        "MEDIAPUNTA": "MC",         
        "EXTREMO": "EX", 
        "EXTREMO IZQUIERDO": "EI", 
        "EXTREMO DERECHO": "ED",
        "LATERAL": "LA",             
        "DELANTERO": "DC",
        "DELANTERA": "DC",
        "NO DISPONIBLE": "ND"
    }

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

def calcular_promedios_filtrados(df, columnas_a_verificar, categorial, equipol, equipo_promedio):
    """
    Calcula el promedio por GENERO, CATEGORIA y EQUIPO, ignorando valores 0 y NaN por columna.
    Asigna valores manuales para hombres. Si no existen registros femeninos, los añade.

    Args:
        df (pd.DataFrame): DataFrame con los datos originales.
        columnas_a_verificar (list): Columnas a calcular.
        categorial (str): Nombre de la columna de categoría.
        equipol (str): Nombre de la columna de equipo.
        equipo_promedio (str): Equipo base para valores por defecto.

    Returns:
        pd.DataFrame: DataFrame con los promedios calculados y registros añadidos si es necesario.
    """
    filas_promedio = []

    for (genero, categoria, equipo), grupo in df.groupby(["GENERO", "CATEGORIA", "EQUIPO"]):
        fila = {
            "GENERO": genero,
            "CATEGORIA": categoria,
            "EQUIPO": equipo
        }
        for columna in columnas_a_verificar:
            datos_columna = pd.to_numeric(grupo[columna], errors="coerce")
            datos_validos = datos_columna[(datos_columna != 0) & (~datos_columna.isna())]
            fila[columna] = datos_validos.mean() if not datos_validos.empty else np.nan
        filas_promedio.append(fila)

    df_promedios = pd.DataFrame(filas_promedio).round(2)

    # --- Valores manuales para Hombres ---
    condiciones_h = {
        "Cadete": {"DISTANCIA ACUMULADA (M)": 1400, "ALTURA-(CM)": 35.00, "TIEMPO 0-40M (SEG)": 5.7},
        "Juvenil": {"DISTANCIA ACUMULADA (M)": 1900, "ALTURA-(CM)": 39.00, "TIEMPO 0-40M (SEG)": 5.2},
    }

    for categoria_val, valores in condiciones_h.items():
        df_promedios.loc[
            (df_promedios["GENERO"] == "H") &
            (df_promedios[categorial] == categoria_val) &
            (df_promedios[equipol] == equipo_promedio),
            list(valores.keys())
        ] = list(valores.values())

    # --- Valores manuales para Mujeres (si no existen) ---
    condiciones_m = {
        "Cadete": {"DISTANCIA ACUMULADA (M)": 1400, "ALTURA-(CM)": 23.00, "TIEMPO 0-40M (SEG)": 6.4},
        "Juvenil": {"DISTANCIA ACUMULADA (M)": 1900, "ALTURA-(CM)": 25.00, "TIEMPO 0-40M (SEG)": 6.2},
    }

    for categoria_val, valores in condiciones_m.items():
        existe_femenino = (
            ((df_promedios["GENERO"] == "M") &
             (df_promedios[categorial] == categoria_val) &
             (df_promedios[equipol] == equipo_promedio))
            .any()
        )

        if not existe_femenino:
            nueva_fila = {
                "GENERO": "M",
                "CATEGORIA": categoria_val,
                "EQUIPO": equipo_promedio,
                **{col: np.nan for col in columnas_a_verificar}  # Inicializar todas
            }
            nueva_fila.update(valores)
            df_promedios = pd.concat([df_promedios, pd.DataFrame([nueva_fila])], ignore_index=True)

    return df_promedios

def obtener_promedio_genero(df_promedios, categoria, equipo_promedio, columna, genero):
    """
    Devuelve el promedio filtrado por categoría, equipo y género.

    Args:
        df_promedios (DataFrame): DataFrame de promedios.
        categoria (str): Categoría ("Cadete", "Juvenil", etc.).
        equipo_promedio (str): Nombre del equipo promedio.
        columna (str): Columna métrica a consultar.
        genero (str): "H" o "M".

    Returns:
        float or None: Promedio si existe, de lo contrario None.
    """
    filtro = (
        (df_promedios["GENERO"] == genero) &
        (df_promedios["CATEGORIA"] == categoria) &
        (df_promedios["EQUIPO"] == equipo_promedio)
    )

    valores = df_promedios.loc[filtro, columna]

    if not valores.empty:
        return float(valores.values[0])
    else:
        return None

def obtener_promedios_metricas_genero(df_promedios, categoria, equipo, metricas, genero, tipo="CMJ"):
    """
    Filtra el DataFrame por CATEGORIA, EQUIPO y GENERO, y devuelve un diccionario con los valores promedio
    por cada métrica solicitada.

    Args:
        df_promedios (DataFrame): DataFrame con promedios.
        categoria (str): Categoría del jugador (e.g., 'Juvenil', 'Cadete').
        equipo (str): Nombre del equipo.
        metricas (list): Lista de columnas a evaluar.
        genero (str): 'H' o 'M'.
        tipo (str): Para identificar el contexto del aviso (CMJ, Sprint, etc.)

    Returns:
        dict: Diccionario con métricas y sus valores promedio si existen.
    """
    # Forzar tipos seguros
    for col in ["GENERO", "CATEGORIA", "EQUIPO"]:
        if col in df_promedios.columns:
            df_promedios[col] = df_promedios[col].astype(str)

    filtro = (
        (df_promedios["GENERO"] == genero) &
        (df_promedios["CATEGORIA"] == categoria) &
        (df_promedios["EQUIPO"] == equipo)
    )

    promedio_row = df_promedios.loc[filtro]
    #st.text(metricas)
    promedios = {}
    if not promedio_row.empty:
        for metrica in metricas:
            if metrica in promedio_row.columns:
                valor = promedio_row[metrica].values[0]
                if pd.notna(valor):
                    promedios[metrica] = float(valor)
    else:
        st.warning(f"No se encontraron promedios de {tipo} para la categoría, equipo y género especificados.")

    return promedios

def get_observacion_grasa(grasa, categoria, gender):

    if "juvenil" in categoria:
        if grasa > 15:
            return (
                "Porcentajes > 15% de grasa corporal representa:\n"
                "- Aumento en la incidencia de lesiones músculoesqueléticas.\n"
                "- Acelera la aparición de fatiga.\n"
                "- Disminuye la eficiencia energética y el rendimiento físico.\n"
                "- Afecta parámetros hormonales y metabólicos.\n"
                "- Recomendamos realizar un seguimiento con un nutricionista.")
        elif grasa < 7:
            if gender == "H":
                return (
                    "Porcentajes menores al 7% de grasa corporal representan:\n"
                    "- Aumento en la incidencia de lesiones músculoesqueléticas.\n"
                    "- Aceleración en la aparición de la fatiga.\n"
                    "- Disminución de la eficiencia energética y del rendimiento físico.\n"
                    "- Alteraciones en parámetros hormonales y metabólicos.\n"
                    "- Se recomienda realizar un seguimiento con un nutricionista deportivo."
                )
            else:
                return (
                    "Porcentajes menores al 8% de grasa corporal representan:\n"
                    "- Aumento en la incidencia de lesiones músculoesqueléticas.\n"
                    "- Aceleración en la aparición de la fatiga.\n"
                    "- Disminución de la eficiencia energética y del rendimiento físico.\n"
                    "- Alteraciones en parámetros hormonales y metabólicos.\n"
                    "- Se recomienda realizar un seguimiento con un nutricionista deportivo."
                )
        else:
            return "Tu nivel de grasa corporal está en el rango ideal para un futbolista de alto rendimiento."
    
    elif "cadete" in categoria:
        if grasa > 17:
            return (
                "Porcentajes > 17% de grasa corporal representa:\n"
                "- Aumento en la incidencia de lesiones músculoesqueléticas.\n"
                "- Acelera la aparición de fatiga.\n"
                "- Disminuye la eficiencia energética y el rendimiento físico.\n"
                "- Afecta parámetros hormonales y metabólicos.\n"
                "- Recomendamos realizar un seguimiento con un nutricionista deportivo.")
        elif grasa < 8:
            return (
                "Porcentajes menores al 8% de grasa corporal representan:\n"
                "- Aumento en la incidencia de lesiones músculoesqueléticas.\n"
                "- Aceleración en la aparición de la fatiga.\n"
                "- Disminución de la eficiencia energética y del rendimiento físico.\n"
                "- Alteraciones en parámetros hormonales y metabólicos.\n"
                "- Se recomienda realizar un seguimiento con un nutricionista deportivo."
            )
        else:
            return "Tu nivel de grasa corporal está en el rango ideal para un futbolista de alto rendimiento."
        
    
    return ""

def get_observacion_cmj(valor_cmj, categoria, gender):
    """
    Devuelve una frase interpretativa para el test de CMJ según la categoría ('Juvenil' o 'Cadete')
    y el valor de salto (en cm).
    """

    if valor_cmj is None or pd.isna(valor_cmj):
        return ""

    categoria = categoria.lower()

    if "juvenil" in categoria:
        if gender == "H":
            if valor_cmj > 36:
                return (
                    "Tu nivel en el CMJ está dentro del rango óptimo de rendimiento.\n"
                    "El objetivo es mejorar la eficiencia en la técnica de salto y mantener o incrementar levemente el rendimiento."
                )
            elif 32 < valor_cmj <= 36:
                return (
                    "Mejorar la eficiencia en la técnica de salto.\n"
                    "Necesidad de trabajo de potencia de tren inferior."
                )
            elif valor_cmj <= 32:
                return (
                    "Masa muscular insuficiente.\n"
                    "Necesidad de trabajo de fuerza y potencia de tren inferior.\n"
                    "Mejorar la técnica de salto."
                )
        elif gender == "M":
            if valor_cmj >= 34:
                return (
                    "Excelente estado de potencia de miembro inferior para el fútbol femenino"
                    )
            elif 24 < valor_cmj < 34:
                return (
                    "Tu nivel en el CMJ está dentro del rango óptimo de rendimiento.\n"
                    "El objetivo es mejorar la eficiencia en la técnica de salto y mantener o incrementar levemente el rendimiento."
                )
            elif 23 <= valor_cmj < 24:
                return (
                    "Mejorar la eficiencia en la técnica de salto.\n"
                    "Necesidad de trabajo de potencia de tren inferior."
                )
            elif valor_cmj <= 22:
                return (
                    "Masa muscular insuficiente.\n"
                    "Necesidad de trabajo de fuerza y potencia de tren inferior.\n"
                    "Mejorar la técnica de salto."
                )
    elif "cadete" in categoria:
        if gender == "H":
            if valor_cmj > 30:
                return (
                    "Tu nivel en el CMJ está dentro del rango óptimo de rendimiento."
                )
            elif 26 < valor_cmj <= 30:
                return (
                    "Mejorar la eficiencia en la técnica de salto.\n"
                    "Necesidad de trabajo de potencia de tren inferior."
                )
            elif valor_cmj <= 26:
                return (
                    "Masa muscular insuficiente.\n"
                    "Necesidad de trabajo de fuerza y potencia de tren inferior.\n"
                    "Mejorar la técnica de salto."
                )
        elif gender == "M":
            if valor_cmj >= 31:
                return (
                    "Excelente estado de potencia de miembro inferior para el fútbol femenino"
                    )
            elif 23 <= valor_cmj <= 30:
                return (
                    "Tu nivel en el CMJ está dentro del rango óptimo de rendimiento.\n"
                    "El objetivo es mejorar la eficiencia en la técnica de salto y mantener o incrementar levemente el rendimiento."
                )
            elif 20 <= valor_cmj <= 22:
                return (
                    "Mejorar la eficiencia en la técnica de salto.\n"
                    "Necesidad de trabajo de potencia de tren inferior."
                )
            elif valor_cmj <= 19:
                return (
                    "Masa muscular insuficiente.\n"
                    "Necesidad de trabajo de fuerza y potencia de tren inferior.\n"
                    "Mejorar la técnica de salto."
                )
    return ""

def get_observacion_sprint(valor_sprint, categoria, genero):
    """
    Devuelve una observación interpretativa según el valor del sprint (0-40m en segundos),
    la categoría ('Juvenil' o 'Cadete') y el género ('H' o 'M').
    """

    if valor_sprint is None or pd.isna(valor_sprint):
        return ""

    categoria = categoria.lower()
    genero = genero.upper()

    texto_1 = "Tu nivel de fuerza horizontal para el sprint es excelente para tu edad y categoría."
    texto_2 = (
        "Necesidad de trabajo técnico de zancada y frecuencia de paso.\n"
        "Identificar si el déficit está en la aceleración inicial o en la fase de velocidad máxima.\n"
        "Mejorar tu potencia en tramos cortos."
    )
    texto_3 = (
        "Tienes un margen muy grande de mejora en el trabajo de fuerza de tren inferior.\n"
        "Necesidad de trabajo técnico de zancada y frecuencia de paso.\n"
        "Es fundamental mejorar tu potencia en tramos cortos y largos."
    )

    if genero == "H":
        if "juvenil" in categoria:
            if valor_sprint < 5.2:
                return texto_1
            elif 5.2 <= valor_sprint < 5.8:
                return texto_2
            else:
                return texto_3

        elif "cadete" in categoria:
            if valor_sprint < 5.9:
                return texto_1
            elif 5.9 <= valor_sprint < 6.2:
                return texto_2
            else:
                return texto_3

    elif genero == "M":
        if "juvenil" in categoria:
            if valor_sprint < 6.2:
                return texto_1
            elif 6.3 <= valor_sprint < 6.5:
                return texto_2
            else:
                return texto_3

        elif "cadete" in categoria:
            if valor_sprint < 6.4:
                return texto_1
            elif 6.5 <= valor_sprint < 6.7:
                return texto_2
            else:
                return texto_3

    return ""


def get_observacion_agilidad(valor_asimetria, genero="H", categoria="juvenil"):
    """
    Devuelve una observación interpretativa basada en el porcentaje de asimetría funcional
    entre ambas piernas, considerando género y categoría.
    """
    if valor_asimetria is None or pd.isna(valor_asimetria):
        return ""

    genero = genero.upper()
    categoria = categoria.lower()
    
    if genero == "M":
        if categoria == "cadete":
            
            if valor_asimetria < 4:
                return "La jugadora presenta un nivel de simetría funcional adecuado (< 4%) entre ambas piernas en el cambio de dirección."
            elif valor_asimetria <= 6:
                return (
                    "Ligera asimetría funcional entre ambas piernas en el cambio de dirección.\n"
                    "Es recomendable aplicar estrategias preventivas para evitar que afecte el rendimiento o aumente el riesgo de lesión."
                )
            else:
                return (
                    "Asimetría >7% en el cambio de dirección representa:\n- Déficit de fuerza excéntrica y/o potencia reactiva.\n- Necesidad de mejora de la técnica de frenado.\n- Incremento en el riesgo de lesión musculoesquelética, sobre todo en isquiosurales y LCA.\n- Limitación de la capacidad de realizar acciones explosivas (con giros, fintas, driblings).\n\nRecomendamos un plan específico de entrenamiento unilateral de la pierna deficitaria."
                )

        elif categoria == "juvenil":
            if valor_asimetria < 3:
                return "La jugadora presenta un nivel de simetría funcional adecuado (< 3%) entre ambas piernas en el cambio de dirección."
            elif valor_asimetria < 5.5:
                return (
                    "Ligera asimetría funcional entre ambas piernas en el cambio de dirección.\n"
                    "Es recomendable aplicar estrategias preventivas para evitar que afecte el rendimiento o aumente el riesgo de lesión."
                )
            else:
                return (
                    "Asimetría > 5.5% en el cambio de dirección representa:\n- Déficit de fuerza excéntrica y/o potencia reactiva\n- Necesidad de mejora de la técnica de frenado \n- Incremento en el riesgo de lesión musculoesquelética, sobre todo en isquiosurales y LCA.\n- Limitación de la capacidad de realizar acciones explosivas (con giros, fintas, driblings)\n\nRecomendamos un plan específico de entrenamiento unilateral de la pierna deficitaria."
                )

    # Default masculino
    if valor_asimetria <= 5:
        return (
            "El jugador presenta un nivel de simetría funcional adecuado (<5%) entre ambas piernas en el cambio de dirección."
        )
    elif 5 < valor_asimetria <= 8:
        return (
            "Ligera asimetría funcional entre ambas piernas en el cambio de dirección.\n"
            "Aunque se encuentra dentro de un rango aceptable, es recomendable aplicar estrategias preventivas para evitar que esta diferencia aumente y afecte el rendimiento o aumente el riesgo de lesión."
        )
    else:
        return (
            "Asimetría >10% en el cambio de dirección representa:\n"
            "- Déficit de fuerza excéntrica y/o potencia reactiva.\n"
            "- Necesidad de mejora de la técnica de frenado.\n"
            "- Incremento en el riesgo de lesión musculoesquelética, sobre todo en isquiosurales y LCA.\n"
            "- Limitación de la capacidad de realizar acciones explosivas (con giros, fintas, driblings).\n\n"
            "Recomendamos un plan específico de entrenamiento unilateral de la pierna deficitaria."
        )

