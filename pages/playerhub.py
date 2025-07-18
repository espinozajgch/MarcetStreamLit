from streamlit_gsheets import GSheetsConnection

import streamlit as st
from utils import util
from utils import player
from utils import reporte as report
from graphics import graphics
from graphics import cmj as cmjg
from graphics import sprint as sprintg
from graphics import yoyo as yoyog
from graphics import rsa as rsag
from graphics import agilidad as agilidadg
import pandas as pd
import numpy as np
import login as login
from datetime import date
import base64
from utils import traslator

st.set_page_config(
    page_title="PlayerHub",
    page_icon=":material/contacts:",
    layout="wide",
    initial_sidebar_state="expanded"
)

# 📡 Conexión con Google Sheets
conn = st.connection("gsheets", type=GSheetsConnection)

# 🔐 Verificación de sesión
login.generarLogin(conn)
if "usuario" not in st.session_state:
    st.stop()

st.header(" :blue[Player Hub] :material/contacts:", divider=True)
#st.subheader("Datos individuales, historicos y alertas")

unavailable = "No Disponible"
fecha_registro = "FECHA REGISTRO"
categorial = "CATEGORIA"
equipol = "EQUIPO"
jugadorl = "JUGADOR"
mensaje_no_data = "El Jugador seleccionado no cuenta con datos suficientes para mostrar esta sección"
equipo_promedio = "A"
columnas_excluidas_promedio = [fecha_registro, 'ID', categorial, equipol]
fecha_actual = date.today()

# Conexion, lectura y limpieza lectura de datos
###################################################
df_datos, df_data_test, df_checkin = util.getData(conn)
df_joined = util.getJoinedDataFrame(df_datos, df_data_test)
#st.dataframe(df_datos )

test, test_cat, lista_columnas = util.get_diccionario_test_categorias(conn)

datatest_columns = util.get_dataframe_columns(df_data_test)
columnas_a_verificar = [col for col in datatest_columns if col not in columnas_excluidas_promedio]

df_data_test_final, df_datos_final = util.actualizar_datos_con_checkin(df_datos, df_checkin, df_joined)
###################################################
#st.dataframe(df_datos_final)

df_datos_filtrado = pd.DataFrame()
# Filtros
###################################################
genero = ["Todos", "Masculino", "Femenino"]
gender_type = st.radio("Genero", genero, horizontal=True)

if gender_type == "Masculino":
    gender_type = "H"
elif gender_type == "Femenino":
    gender_type = "M"
else:
    gender_type = "NA"

if gender_type != "NA":
    df_datos_final = df_datos_final[df_datos_final["GENERO"] == gender_type]

on = st.toggle("Mostrar solo jugadores con registros")
if on:
    df_sesiones = util.sesiones_por_test(df_data_test_final, test_cat)
    df_datos_final = df_datos_final[df_datos_final[jugadorl].isin(df_sesiones[jugadorl])]
    #df_datos_filtrado = util.get_filters(df_filtrado)
#else:

df_datos_filtrado = util.get_filters(df_datos_final)

# @st.fragment
# def filtros_fragment(df):
#     return util.get_filters(df)
#df_datos_filtrado = filtros_fragment(df_datos_final)


with st.expander("Configuración Avanzada"):

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

    if fecha_fin < fecha_inicio:
        st.warning("❌ La fecha final no puede ser anterior a la fecha inicial.")
        st.stop()

    test_data_filtered = util.filtrar_por_rango_fechas(df_data_test_final, fecha_registro, fecha_inicio, fecha_fin)

    #st.divider()
    idiomas = ["Español", "Inglés", "Francés", "Italiano", "Alemán", "Catalán", "Portugues"]
    idioma_map = {
        "Español": "es",
        "Inglés": "en",
        "Francés": "fr",
        "Italiano": "it",
        "Alemán": "de",
        "Catalán": "ca",
        "Portugues": "pt",
        #"Arabe": "ar"
    }

    seleccion = st.radio("Selecciona un idioma:", idiomas, horizontal=True)
    idioma = idioma_map[seleccion]

    #st.divider()
    type_report = ["Simple", "Avanzado"]
    tipo_reporte = st.radio("Tipo Reporte", type_report, horizontal=True)

    if tipo_reporte == "Simple":
        tipo_reporte_bool = True
    else:
        tipo_reporte_bool = False

# Promedios
###################################################
# Agrupar por CATEGORIA y EQUIPO, calcular promedio
#df_promedios = df_data_test.groupby(["CATEGORIA", "EQUIPO"])[columnas_a_verificar].mean().reset_index()
df_promedios =  util.calcular_promedios_filtrados(df_data_test_final, columnas_a_verificar, categorial, equipol, equipo_promedio)
#st.dataframe(df_promedios)

###################################################

if df_datos_filtrado.empty or len(df_datos_filtrado) > 1:
    st.warning("No se ha encontrado información o aun no ha seleccionado a un jugador.")
else:
    df_datos_final["FOTO PERFIL"] = df_datos_final["FOTO PERFIL"].apply(player.convert_drive_url)
    
    #st.dataframe(df_datos_final)

    # Sección datos de usuario
    df_joined_filtrado, df_jugador, categoria, equipo, gender = player.player_block(df_datos_filtrado, df_datos_final, test_data_filtered, unavailable, idioma)
    
   

    cat_label = "U19" if categoria.lower() == "juvenil" else "U15"
   
    if not df_datos_filtrado.empty:
        #traducidas = util.traducir_lista(lista_columnas + ["REPORTE"], idioma)
        ##tab1,tab2,tab3 = st.tabs(["👤 Perfil", "📈 Rendimiento", "📆 Historicos" ,"📉 Comparaciones", "🏥 Alertas"])
        antropometria, cmj, sprint, yoyo, agilidad, rsa, reporte = st.tabs(lista_columnas + ["REPORTE"])

        figalt = None
        figant = None
        figcmj = None
        figag = None
        figagd = None
        figagnd = None
        figsp05 = None
        figsp040 = None
        figspv = None
        figyoyo = None
        figrsat = None
        figrsav = None
        observaciones_dict = {}

        with antropometria:
            if len(df_joined_filtrado) > 0:
                ######################################################################################################
                ## ANTROPOMETRIA
                columns = list(test_cat.get(lista_columnas[0], []))
                
                df_anthropometrics = df_joined_filtrado[[fecha_registro] + columns]
                df_anthropometrics = df_anthropometrics.reset_index(drop=True)
                #st.dataframe(df_anthropometrics)
                if not util.columnas_sin_datos_utiles(df_anthropometrics, [fecha_registro]):
                    
                    # Eliminar las filas donde TODAS las columnas filtradas sean cero o nulas
                    df_anthropometrics = df_anthropometrics[~(df_anthropometrics[columns] == 0).all(axis=1)]
                    #percentiles_an = util.calcular_percentiles(df_anthropometrics.iloc[0], referencia_test, columnas_filtradas)
                    
                    st.markdown("📆 **Ultímas Mediciones**")

                    zona_optima_min = 8
                    zona_optima_max = 16
                    if categoria == "Juvenil":
                        if gender == "H":
                            zona_optima_min = 8
                            zona_optima_max = 14   
                        elif gender == "M":
                            zona_optima_min = 9
                            zona_optima_max = 14
                    elif categoria == "Cadete":
                        if gender == "H":
                            zona_optima_min = 8
                            zona_optima_max = 16  
                        elif gender == "M":
                            zona_optima_min = 8
                            zona_optima_max = 14  
                    
                        

                    col1, col2, col3, col4 = st.columns(4)
                    with col1:
                        act = df_anthropometrics[columns[0]].iloc[0]
                        ant = df_anthropometrics[columns[0]].iloc[1] if len(df_anthropometrics) > 1 else 0
                        variacion = float(act) - float(ant)
                        st.metric(columns[0].capitalize(),f'{float(act):,.2f}', f'{float(variacion):,.2f}')

                    with col2:
                        act = df_anthropometrics[columns[1]].iloc[0]
                        ant = df_anthropometrics[columns[1]].iloc[1] if len(df_anthropometrics) > 1 else 0
                        variacion = act - ant
                        st.metric(columns[1].capitalize(),f'{float(act):,.2f}', f'{float(variacion):,.2f}')

                    with col3:
                        gact = df_anthropometrics[columns[2]].iloc[0]
                        gant = df_anthropometrics[columns[2]].iloc[1] if len(df_anthropometrics) > 1 else 0
                        variacion = gact - gant
                        st.metric(columns[2].capitalize(),f'{float(gact):,.2f}')
                    
                    with col4:
                        act = df_anthropometrics[fecha_registro].iloc[0]
                        st.metric("Último Registro", act)

                    observacion = util.get_observacion_grasa(gact, categoria.lower(), gender)
                    observacion = traslator.traducir(observacion, idioma)
                    
                    if(gact < 7) or (gact > 15):
                        st.warning(f"{observacion}", icon="⚠️")
                    else:
                        st.success(f"{observacion}", icon="✅")
                    
                    observaciones_dict["Peso y % Grasa"] = observacion

                    figalt = graphics.get_height_graph(df_anthropometrics, idioma, tipo_reporte_bool)

                    #df_anthropometrics_sin_ceros = df_anthropometrics[~(df_anthropometrics[columns] == 0).any(axis=1)]
                    figant = graphics.get_anthropometrics_graph(df_anthropometrics, categoria, zona_optima_min, zona_optima_max, idioma, tipo_reporte_bool, gender, cat_label)
                    
                    st.divider()
                    c1, c2 = st.columns([2,1.5])     
                    with c1:
                        # Cálculo del IMC
                        # Verificar si PESO o ALTURA son 0 o nulos (OR entre condiciones)
                        mask = (df_anthropometrics[columns[0]] == 0) | (df_anthropometrics[columns[1]] == 0) | df_anthropometrics[columns[0]].isnull() | df_anthropometrics[columns[1]].isnull()

                        # Aplicar el cálculo del IMC y la categorización solo cuando la condición no se cumpla
                        df_anthropometrics["IMC"] = np.where(mask, np.nan, df_anthropometrics[columns[1]] / ((df_anthropometrics[columns[0]] / 100) ** 2))

                        # Asegurarse de que la columna "IMC" no contenga "N/A" como string
                        df_anthropometrics["Categoría IMC"] = np.where(df_anthropometrics["IMC"].isna(), "N/A", df_anthropometrics["IMC"].apply(util.categorizar_imc))

                        st.markdown("📊 **Análisis de IMC y Porcentaje de Grasa Corporal**")
                        st.dataframe(df_anthropometrics
                            .style
                            .format({"ALTURA (CM)": "{:.2f}", "PESO (KG)": "{:.2f}", "IMC": "{:.2f}", "GRASA (%)": "{:.2f}"})  # Aplica el formato de 2 decimales
                            .map(util.color_categorias, subset=["Categoría IMC"]))
                    with c2:
                        # Cálculo de estadísticas
                        stats = {
                            columns[0]: [df_anthropometrics[columns[0]].mean(), df_anthropometrics[columns[0]].max(), df_anthropometrics[columns[0]].min()],
                            columns[1]: [df_anthropometrics[columns[1]].mean(), df_anthropometrics[columns[1]].max(), df_anthropometrics[columns[1]].min()],
                            columns[2]: [df_anthropometrics[columns[2]].mean(), df_anthropometrics[columns[2]].max(), df_anthropometrics[columns[2]].min()],
                        }
                        stats_df = pd.DataFrame(stats, index=["Promedio", "Máximo", "Mínimo"])

                        st.markdown("📊 **Valores máximos, mínimos y promedio**")
                        st.dataframe(stats_df.round(1))
                else:
                    st.text(mensaje_no_data)
                    percentiles_an = None
            else:
                st.text(mensaje_no_data)
                percentiles_an = None
        
        with cmj:
            if len(df_joined_filtrado) > 0:

                ######################################################################################################
                ## CMJ
                columns = list(test_cat.get(lista_columnas[1], []))
                df_cmj = df_joined_filtrado[[fecha_registro] + columns]
                df_cmj = df_cmj.reset_index(drop=True)

                # Eliminar las filas donde TODAS las columnas filtradas sean cero o nulas
                df_cmj = df_cmj[~(df_cmj[columns] == 0).all(axis=1)]
                todos_ceros = (df_cmj[columns] == 0).all().all()

                if not todos_ceros:
                    df_cmj = df_cmj[~(df_cmj[columns] == 0).all(axis=1)]
                    #st.dataframe(df_cmj)  
                    #percentiles_cmj = util.calcular_percentiles(df_cmj.iloc[0], referencia_test, columnas_filtradas)
                    
                    st.markdown("📆 **Ultímas Mediciones**")
                    
                    col1, col2, col3 = st.columns(3)

                    with col1:
                        cactc = df_cmj[columns[0]].iloc[0]
                        cantc = df_cmj[columns[0]].iloc[1] if len(df_cmj) > 1 else 0
                        variacion = cactc - cantc
                        metrica_cmj = columns[0].replace("-", " ").capitalize()
                        st.metric(metrica_cmj,f'{cactc:,.2f}', f'{variacion:,.2f}')

                    with col2:
                        cactw = df_cmj[columns[1]].iloc[0]
                        cantw = df_cmj[columns[1]].iloc[1] if len(df_cmj) > 1 else 0
                        variacion = cactw - cantw
                        st.metric(columns[1].replace("-", " ").capitalize(),f'{cactw:,.2f}', f'{variacion:,.2f}')

                    with col3:
                        act = df_cmj[fecha_registro].iloc[0]
                        st.metric("Último Registro", act)

                    #st.text(gender)
                    promedio_cmj = util.obtener_promedio_genero(df_promedios, categoria, equipo_promedio, columns[0], gender)
                    cactc = float(cactc)
                    #st.text(cactc)
                    observacion = util.get_observacion_cmj(cactc, categoria, gender)
                    observacion = traslator.traducir(observacion, idioma)
                    observaciones_dict["POTENCIA MUSCULAR (SALTO CON CONTRAMOVIMIENTO)"] = observacion
                    
                    # Mostrar mensaje visual según el rango definido por categoría
                    if cactc is not None and pd.notna(cactc):
                        #categoria = categoria.lower()

                        if gender == "M":
                            if categoria.lower() == "juvenil":
                                if cactc >= 23:
                                    st.success(observacion, icon="✅")
                                else:
                                    st.warning(observacion, icon="⚠️")

                            elif categoria.lower() == "cadete":
                                if cactc >= 22:
                                    st.success(observacion, icon="✅")
                                else:  # cactc < 18
                                    st.warning(observacion, icon="⚠️")
                        elif genero == "H":
                            if categoria.lower() == "juvenil":
                                if cactc > 36:
                                    st.success(observacion, icon="✅")
                                elif 32 < cactc <= 36:
                                    st.warning(observacion, icon="⚠️")
                                else:
                                    st.warning(observacion, icon="⚠️")

                            elif categoria.lower() == "cadete":
                                if cactc > 30:
                                    st.success(observacion, icon="✅")
                                elif 26 < cactc <= 30:
                                    st.warning(observacion, icon="⚠️")
                                else:
                                    st.warning(observacion, icon="⚠️")

                    #graphics.get_cmj_graph(df_cmj, df_promedios, categoria, equipo)

                    #st.divider()
                    cola, colb = st.columns([2.5,1])

                    with cola:
                        promedios = util.obtener_promedios_metricas_genero(
                            df_promedios=df_promedios,
                            categoria=categoria,
                            equipo=equipo,
                            metricas=[columns[0].upper()],
                            genero=gender,
                            tipo="CMJ"
                        )
                        
                        figcmj = cmjg.get_cmj_graph(df_cmj, promedios, categoria, equipo_promedio, [columns[0]], fecha_registro, idioma, tipo_reporte_bool, gender, cat_label)
                    with colb:
                        st.markdown("📊 **Históricos**")
                        styled_df = util.aplicar_semaforo(df_cmj)
                        st.dataframe(df_cmj)

                    #st.markdown("📊 **Tabla de percentiles: Comparación del jugador con atletas de su misma edad**")
                    #graphics.mostrar_percentiles_coloreados(df_cmj.iloc[0], percentiles_cmj)  
                else:
                    st.text(mensaje_no_data) 
                    percentiles_cmj = None      
            else:
                st.text(mensaje_no_data)
                percentiles_cmj = None
          
        with sprint:
            if len(df_joined_filtrado) > 0:

                ######################################################################################################
                ## SPRINT

                columns = list(test_cat.get(lista_columnas[2], []))
                df_sprint = df_joined_filtrado[[fecha_registro] + columns]
                
                df_sprint = df_sprint.reset_index(drop=True)

                # Eliminar las filas donde TODAS las columnas filtradas sean cero o nulas
                df_sprint = df_sprint.loc[~(df_sprint[columns].fillna(0) == 0).all(axis=1)]

                todos_ceros = (df_sprint[columns] == 0).all().all()
                
                #st.dataframe(df_sprint)
                if not todos_ceros:
                    df_sprint = df_sprint[~(df_sprint[columns] == 0).all(axis=1)]
                    #percentiles_sp = util.calcular_percentiles(df_sprint.iloc[0], referencia_test, columnas_filtradas)
                    
                    st.markdown("📆 **Ultímas Mediciones**")

                    col1, col2, col3, col4, col5 = st.columns(5)

                    with col1:
                        act05t = df_sprint[columns[0]].iloc[0]
                        ant05t = df_sprint[columns[0]].iloc[1] if len(df_sprint) > 1 else 0
                        variacion05t = act05t - ant05t
                        st.metric(columns[0].capitalize(),f'{float(act05t):,.2f}', f'{float(variacion05t):,.2f}', delta_color="inverse")

                    with col2:
                        act05v = df_sprint[columns[1]].iloc[0]
                        ant05v = df_sprint[columns[1]].iloc[1] if len(df_sprint) > 1 else 0
                        variacion05v = act05v - ant05v
                        st.metric(columns[1].capitalize(),f'{float(act05v):,.2f}', f'{float(variacion05v):,.2f}', delta_color="inverse")

                    with col3:
                        act040t = df_sprint[columns[2]].iloc[0]
                        ant040t = df_sprint[columns[2]].iloc[1] if len(df_sprint) > 1 else 0
                        variacion040t = act040t - ant040t
                        st.metric(columns[2].capitalize(),f'{float(act040t):,.2f}', f'{float(variacion040t):,.2f}')

                    with col4:
                        act040v = df_sprint[columns[3]].iloc[0]
                        ant040v = df_sprint[columns[3]].iloc[1] if len(df_sprint) > 1 else 0
                        variacion040v = act040v - ant040v
                        st.metric(columns[3].capitalize(),f'{float(act040v):,.2f}', f'{float(variacion040v):,.2f}', delta_color="inverse")

                    with col5:
                        act = df_sprint[fecha_registro].iloc[0]
                        st.metric(f"Último Registro",act)
                        #df_sprint = util.convertir_m_s_a_km_h(df_sprint, ["VEL 0-5M (M/S)", "VEL 5-20M (M/S)", "VEL 20-40M (M/S)"])
                    
                    
                    observacion = util.get_observacion_sprint(valor_sprint=act040t, categoria=categoria, genero=gender)
                    observacion = traslator.traducir(observacion, idioma)
                    observaciones_dict["SPRINT (0-40M)"] = observacion
                    
                    act040t = float(act040t) if pd.notna(act040t) else None

                    if act040t is not None:
                        #categoria = categoria.lower()

                        if gender == "H":
                            umbral_bueno = 5.2 if "juvenil" in categoria.lower() else 5.9
                        elif genero == "M":
                            umbral_bueno = 5.5 if "juvenil" in categoria.lower() else 6.0
                        else:
                            umbral_bueno = 999  # valor de fallback por si hay un error

                        if act040t < umbral_bueno:
                            st.success(observacion, icon="✅")
                        else:
                            st.warning(observacion, icon="⚠️")

                    #st.text(columns[2].upper())
                    promedios_sprint = util.obtener_promedios_metricas_genero(
                            df_promedios=df_promedios,
                            categoria=categoria.capitalize(),
                            equipo=equipo,
                            metricas=[columns[2].upper()],
                            genero=gender,
                            tipo="Sprint 0-40m"
                        )
                    
                    #st.dataframe(df_promedios)

                    if(act05t != 0) or (act05v != 0):
                        figsp05 = sprintg.get_sprint_graph(df_sprint, promedios_sprint, categoria, equipo_promedio, columns[0],columns[1], fecha_registro, idioma, tipo_reporte_bool, cat_label, gender)

                    if(act040t != 0) or (act040v != 0):
                        figsp040 = sprintg.get_sprint_graph(df_sprint, promedios_sprint, categoria, equipo_promedio, columns[2],columns[3], fecha_registro, idioma, tipo_reporte_bool, cat_label, gender)
                
                    st.divider()
                    st.markdown("📊 **Históricos**")
                    st.dataframe(df_sprint)   
                    
                    #st.divider()
                    #st.markdown("📊 **Tabla de percentiles: Comparación del jugador con atletas de su misma edad**")
                    #graphics.mostrar_percentiles_coloreados(df_sprint.iloc[0], percentiles_sp) 
                else:
                    st.text(mensaje_no_data)  
                    percentiles_sp = None 
            else:
                st.text(mensaje_no_data)
                percentiles_sp = None
                
        with yoyo:

            if len(df_joined_filtrado) > 0:

                ######################################################################################################
                ## YO-YO

                columns = list(test_cat.get(lista_columnas[3], []))
                df_yoyo = df_joined_filtrado[[fecha_registro] + columns]
                df_yoyo = df_yoyo.reset_index(drop=True)

                # Eliminar las filas donde TODAS las columnas filtradas sean cero o nulas
                df_yoyo = df_yoyo.loc[~(df_yoyo[columns].fillna(0) == 0).all(axis=1)]

                todos_ceros = (df_yoyo[columns] == 0).all().all()

                if not todos_ceros:
                    df_yoyo = df_yoyo[~(df_yoyo[columns] == 0).all(axis=1)]
                    #percentiles_yoyo = util.calcular_percentiles(df_yoyo.iloc[0], referencia_test, columnas_filtradas)
                    
                    st.markdown("📆 **Ultímas Mediciones**")
                    col1, col2, col3 = st.columns(3)

                    with col1:
                        act = df_yoyo[columns[0]].iloc[0]
                        ant = df_yoyo[columns[0]].iloc[1] if len(df_yoyo) > 1 else 0
                        variacion = 1
                        st.metric(columns[0].capitalize(),f'{act:,.2f}', f'{variacion:,.2f}')

                    with col2:
                        act = df_yoyo[columns[1]].iloc[0]
                        ant = df_yoyo[columns[1]].iloc[1] if len(df_yoyo) > 1 else 0
                        variacion = 1
                        st.metric(columns[1].capitalize(),f'{act:,.2f}', f'{variacion:,.2f}')
                    
                    with col3:
                        act = df_yoyo[fecha_registro].iloc[0]
                        st.metric(f"Último Registro",act)

                    st.divider()

                    cola, colb = st.columns([2.5,1.5])

                    #with cola:
                    figyoyo = yoyog.get_yoyo_graph(df_yoyo, df_promedios, categoria, equipo_promedio, columns[1], fecha_registro, idioma, tipo_reporte_bool, cat_label)
                    #with colb:   
                    st.markdown("📊 **Históricos**")
                    styled_df = util.aplicar_semaforo(df_yoyo)
                    st.dataframe(df_yoyo)    
                    #st.markdown("📊 **Tabla de percentiles: Comparación del jugador con atletas de su misma edad**")
                    #graphics.mostrar_percentiles_coloreados(df_yoyo.iloc[0], percentiles_yoyo)  
                else:
                    st.text(mensaje_no_data)
                    percentiles_yoyo = None
            else:
                st.text(mensaje_no_data)
                percentiles_yoyo = None

        with agilidad:
            #st.dataframe(df_joined_filtrado)
            if len(df_joined_filtrado) > 0: 

                ######################################################################################################
                ## AGILIDAD
                columns = list(test_cat.get(lista_columnas[4], []))
                
                df_agilty = df_joined_filtrado[[fecha_registro] + columns]
                #st.dataframe(df_joined_filtrado)
                df_agilty = df_agilty.loc[~(df_agilty[columns].fillna(0) == 0).all(axis=1)]
                todos_ceros = (df_agilty[columns] == 0).all().all()

                if not todos_ceros:
                    
                    df_agilty = df_agilty[~(df_agilty[columns] == 0).any(axis=1)]
                    diferencias = agilidadg.get_diferencia_agilidad(df_agilty, columns, fecha_registro)
                    ultima_diferencia = diferencias[-1]["diferencia_%"] if diferencias else None
                    #percentiles_ag = util.calcular_percentiles(df_agilty.iloc[0], referencia_test, columnas_filtradas)
                    
                    st.markdown("📆 **Ultímas Mediciones**")
                    col1, col2, col3, col4 = st.columns(4)

                    with col1:
                        if not df_agilty.empty and not df_agilty[columns[0]].dropna().empty:
                            act = df_agilty[columns[0]].iloc[0]
                            antd = df_agilty[columns[0]].iloc[1] if len(df_agilty) > 1 else 0
                            variacion = act - antd
                            st.metric(columns[0].capitalize(),f'{float(act):,.2f}', f'{float(variacion):,.2f}', delta_color="inverse")
                    with col2:
                        if not df_agilty.empty and not df_agilty[columns[1]].dropna().empty:
                            act = df_agilty[columns[1]].iloc[0]
                            antnd = df_agilty[columns[1]].iloc[1] if len(df_agilty) > 1 else 0
                            variacion = act - antnd
                            st.metric(columns[1].capitalize(),f'{float(act):,.2f}', f'{float(variacion):,.2f}', delta_color="inverse")

                    with col3:
                        if not df_agilty.empty and not df_agilty[columns[0]].dropna().empty:
                            diferencia_ant = 0 if pd.isna(antd) or antd == 0 else round((abs(antd - antnd) / antd) * 100, 2)
                            variacion = ultima_diferencia - diferencia_ant
                            st.metric("% Diferencia", f'{float(ultima_diferencia):,.2f} %', f'{float(variacion):,.2f}', delta_color="inverse")

                    with col4:
                        if not df_agilty.empty and not df_agilty[columns[0]].dropna().empty:
                            act = df_agilty[fecha_registro].iloc[0] if len(df_agilty) > 0 else 0
                            st.metric("Último Registro", act)

                    if not df_agilty.empty and not df_agilty[columns[0]].dropna().empty:
                        observacion = util.get_observacion_agilidad(valor_asimetria=ultima_diferencia, genero=gender, categoria=categoria)
                        observacion = traslator.traducir(observacion, idioma)
                        observaciones_dict["VELOCIDAD EN EL CAMBIO DE DIRECCIÓN (AGILIDAD 505)"] = observacion
                        #st.text(diferencia)
                        if ultima_diferencia <= 5:
                            st.success(observacion, icon="✅")
                        else:
                            st.warning(observacion, icon="⚠️")

                        figag = agilidadg.get_agility_graph_combined_simple(df_agilty, df_promedios, categoria, equipo, columns, fecha_registro, idioma, tipo_reporte_bool, cat_label, gender)
                        st.divider()
                        
                    
                        st.markdown("📊 **Históricos**")
                        st.dataframe(df_agilty)
                   
                else:
                    st.text(mensaje_no_data)
                    percentiles_ag = None
            else:
                st.text(mensaje_no_data)
                percentiles_ag = None
                            
        with rsa:
            if len(df_joined_filtrado) > 0:

                ######################################################################################################
                ## RSA
                columns = list(test_cat.get(lista_columnas[5], []))
                df_rsa = df_joined_filtrado[[fecha_registro] + columns]
                df_rsa = df_rsa.reset_index(drop=True)
                
                # Eliminar las filas donde TODAS las columnas filtradas sean cero o nulas
                df_rsa = df_rsa.loc[~(df_rsa[columns].fillna(0) == 0).all(axis=1)]

                todos_ceros = (df_rsa[columns] == 0).all().all()
                #st.dataframe(df_rsa)
                if not todos_ceros:
                    df_rsa = df_rsa[~(df_rsa[columns] == 0).all(axis=1)]
                    #percentiles_rsa = util.calcular_percentiles(df_rsa.iloc[0], referencia_test, columnas_filtradas)
                    
                    st.markdown("📆 **Ultímas Mediciones**")

                    col1, col2, col3 = st.columns(3)

                    with col1:
                        act = df_rsa[columns[0]].iloc[0]
                        ant = df_rsa[columns[0]].iloc[1] if len(df_rsa) > 1 else 0
                        variacion = act - ant
                        st.metric(columns[0].capitalize(),f'{act:,.2f}', f'{variacion:,.2f}', delta_color="inverse")

                    with col2:
                        act = df_rsa[columns[1]].iloc[0]
                        ant = df_rsa[columns[1]].iloc[1] if len(df_rsa) > 1 else 0
                        variacion = act - ant
                        st.metric(columns[1].capitalize(),f'{act:,.2f}', f'{variacion:,.2f}')

                    with col3:
                        act = df_rsa[fecha_registro].iloc[0]
                        st.metric(f"Último Registro",act)

                    #styled_dfa = util.aplicar_semaforo(df_rsa[columna_fecha_registro + columns], invertir=True)

                    cola, colb = st.columns([2.5,1])
                    with cola:
                        figrsat = rsag.get_rsa_graph(df_rsa, df_promedios, categoria, equipo_promedio, columns, fecha_registro, idioma, tipo_reporte_bool, cat_label) 
                    with colb:    
                        st.markdown("📊 **Históricos**")
                        st.dataframe(df_rsa[[fecha_registro] + [columns[0]]]) 

                    styled_dfb = util.aplicar_semaforo(df_rsa[[fecha_registro] + columns])
                    colc, cold = st.columns([2.5,1])
                    with colc:
                        #st.dataframe(df_promedios)
                        figrsav = rsag.get_rsa_velocity_graph(df_rsa, df_promedios, categoria, equipo_promedio, columns[1], fecha_registro, idioma, tipo_reporte_bool, cat_label)
                    with cold:    
                        st.markdown("📊 **Históricos**")
                        st.dataframe(df_rsa[[fecha_registro] + [columns[1]]]) 
                else:
                    st.text(mensaje_no_data) 
                    percentiles_rsa = None      
            else:
                st.text(mensaje_no_data)
                percentiles_rsa = None
                
        with reporte:
            if len(df_joined_filtrado) > 0:
                
                # Diccionario de gráficos disponibles
                graficos_disponibles = {
                    "Altura": figalt,
                    "Peso y Grasa": figant,
                    "CMJ": figcmj,
                    "SPRINT 0-5": figsp05,
                    "SPRINT 0-40": figsp040,
                    "YO-YO": figyoyo,
                    "AGILIDAD": figag,
                    "RSA Tiempo": figrsat,
                    "RSA Velocidad": figrsav
                }
                # Lista de categorías para el PDF (dinámica según gráficos disponibles)
                graficos_pdf = []

                # Composición Corporal requiere Altura y Peso y Grasa
                if figalt is not None or figant is not None:
                    graficos_pdf.append("COMPOSICIÓN CORPORAL")

                # CMJ
                if figcmj is not None:
                    graficos_pdf.append("CMJ")

                # SPRINT
                if figsp05 is not None or figsp040 is not None:
                    graficos_pdf.append("SPRINT")

                # YO-YO
                if figyoyo is not None and not tipo_reporte_bool:
                    graficos_pdf.append("YO-YO")

                # AGILIDAD
                if figag is not None:
                    graficos_pdf.append("AGILIDAD")

                # RSA (Tiempo y Velocidad)
                if figrsat is not None and figrsav is not None and not tipo_reporte_bool:
                    graficos_pdf.append("RSA")

                # Multiselect para tests
                @st.fragment
                def seleccionar_graficos(graficos_pdf):
                    return st.multiselect(
                        "Gráficos:",
                        options=graficos_pdf,
                        default=graficos_pdf,
                        placeholder="Seleccione una opción"
                    )

                tests_seleccionados = seleccionar_graficos(graficos_pdf)

                # Generar figs_filtrados según tests seleccionados
                figs_filtrados = {}
                for test in tests_seleccionados:
                    if test == "COMPOSICIÓN CORPORAL":
                        figs_filtrados["Altura"] = figalt
                        figs_filtrados["Peso y Grasa"] = figant
                    elif test == "RSA":
                        figs_filtrados["RSA Tiempo"] = figrsat
                        figs_filtrados["RSA Velocidad"] = figrsav
                    elif test == "SPRINT":
                        figs_filtrados["SPRINT 0-5"] = figsp05
                        figs_filtrados["SPRINT 0-40"] = figsp040
                    else:
                        # Asumimos que para CMJ, Sprint, Yo-Yo los nombres coinciden con las claves
                        for k in graficos_disponibles.keys():
                            if test in k:
                                figs_filtrados[k] = graficos_disponibles[k]

                if st.button("📄 Generar PDF"):
                    # Mostrar el status inmediatamente
                    status = st.status("🛠 Generando PDF...", state="running", expanded=True)
                    fecha_str = fecha_actual.strftime("%d/%m/%Y")

                    observaciones = {
                        "Peso y % Grasa": "El jugador mantiene un % graso dentro del rango saludable.",
                        "POTENCIA MUSCULAR (SALTO CON CONTRAMOVIMIENTO)": "Mejora significativa respecto al mes anterior.",
                        "SPRINT (0-40M)": "El tiempo total ha disminuido, indicando mayor aceleración.",
                        "VELOCIDAD EN EL CAMBIO DE DIRECCIÓN (AGILIDAD 505)": "Aún se observa una leve asimetría entre piernas."
                    }
                    
                    try:
                        if(tipo_reporte=="Avanzado"):
                            # 1. Generar PDF como bytes (puede tardar)
                            pdf_bytes = report.generate_pdf_avanzado(
                                df_jugador, df_anthropometrics, df_agilty, df_sprint, 
                                df_cmj, df_yoyo, df_rsa, figs_filtrados, fecha_str, idioma, observaciones_dict)
                        else:
                            # 2. Generar PDF como bytes (puede tardar)
                            pdf_bytes = report.generate_pdf_simple(
                                df_jugador, df_anthropometrics, figs_filtrados, fecha_str, idioma, observaciones_dict)
                            
                        # 2. Codificar y preparar para mostrar
                        b64_pdf = base64.b64encode(pdf_bytes).decode('utf-8')
                        pdf_data = base64.b64decode(b64_pdf)

                        # Enlace de descarga con nombre específico
                        st.markdown(f'''
                            <a href="data:application/pdf;base64,{b64_pdf}" download="Informe_Fisico_{df_jugador['JUGADOR'].iloc[0]}.pdf" target="_blank">
                                📥 Descargar PDF
                            </a>
                        ''', unsafe_allow_html=True)

                        # 3. Mostrar PDF en Streamlit
                        html_code = f'''
                            <object data="data:application/pdf;base64,{b64_pdf}" type="application/pdf" width="100%" height="1200px"></object>
                        '''
                        st.write(html_code, unsafe_allow_html=True)

                        # 4. Cerrar el status como completado
                        status.update(label="✅ PDF generado con éxito", state="complete", expanded=False)

                    except Exception as e:
                        # Mostrar error si algo falla
                        status.update(label="❌ Error al generar el PDF", state="error", expanded=True)
                        st.exception(e)
            else:
                st.text(mensaje_no_data)
