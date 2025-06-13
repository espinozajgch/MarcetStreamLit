from streamlit_gsheets import GSheetsConnection

import streamlit as st
from utils import util
from utils import player
from utils import graphics
from datetime import datetime
import pandas as pd
import plotly.express as px
import numpy as np
import matplotlib.pyplot as plt
import plotly.graph_objects as go
import seaborn as sns
import login as login

import base64
import io

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

unavailable = "No Disponible"
fecha_registro = "FECHA REGISTRO"
mensaje_no_data = "El Jugador seleccionado no cuenta con datos suficientes para mostrar esta sección"
equipo_promedio = "A"
columnas_excluidas_promedio = ['FECHA REGISTRO', 'ID', "CATEGORIA", "EQUIPO"]

st.header(" :blue[Player Hub] :material/contacts:", divider=True)
#st.subheader("Datos individuales, historicos y alertas")

df_datos, df_data_test, df_checkin = util.getData(conn)
df_joined = util.getJoinedDataFrame(df_datos, df_data_test)
test, test_cat, lista_columnas = util.get_diccionario_test_categorias(conn)

#st.text(lista_columnas[0])

# 1. Extraer solo columnas necesarias del check-in
df_nuevos = df_checkin[["JUGADOR", "CATEGORIA"]].drop_duplicates()

# 2. Asegurar que los nuevos registros tengan la misma estructura que df_datos
df_nuevos = df_nuevos.reindex(columns=df_datos.columns)

# 3. Concatenar
df_resultado = pd.concat([df_datos, df_nuevos], ignore_index=True)

# 4. Eliminar duplicados basados en JUGADOR y CATEGORIA
df_resultado = df_resultado.drop_duplicates(subset=["JUGADOR", "CATEGORIA"], keep="first").reset_index(drop=True)

# 5. Eliminar filas donde todas las columnas sean NaN
df_datos = df_resultado.dropna(how="all").reset_index(drop=True)

# 6. Merge df_checkin con df_joined
df_final = util.merge_by_nombre_categoria(df_joined, df_checkin)

idiomas = ["Español", "Inglés", "Francés", "Italiano", "Alemán", "Catalán", "Portugues", "Arabe"]
idioma_map = {
    "Español": "es",
    "Inglés": "en",
    "Francés": "fr",
    "Italiano": "it",
    "Alemán": "de",
    "Catalán": "ca",
    "Portugues": "pt",
    "Arabe": "ar"
}

seleccion = st.radio("Selecciona un idioma:", idiomas, horizontal=True)
idioma = idioma_map[seleccion]

on = st.toggle("Solo Jugadores con Test Realizados")
if on:
    df_sesiones = util.sesiones_por_test(df_final, test_cat)
    df_filtrado = df_datos[df_datos["JUGADOR"].isin(df_sesiones["JUGADOR"])]
    df_datos_filtrado = util.get_filters(df_filtrado)
else:
    df_datos_filtrado = util.get_filters(df_datos)

datatest_columns = util.get_dataframe_columns(df_data_test)
columnas_a_verificar = [col for col in datatest_columns if col not in columnas_excluidas_promedio]

# Agrupar por CATEGORIA y EQUIPO, calcular promedio
#df_promedios = df_data_test.groupby(["CATEGORIA", "EQUIPO"])[columnas_a_verificar].mean().reset_index()
df_promedios =  util.calcular_promedios_filtrados(df_final, columnas_a_verificar)

# Promedio yoyo
# Juvenil 2100m
# Cadete 1700m

# Promedio CMJ
# Juvenil 41cm
# Cadete 36 cm

# Promedio Sprint 0 a 40m
# Juvenil 5.1 seg
# Cadete 5.7 seg

df_promedios.loc[(df_promedios["CATEGORIA"] == "Cadete") & (df_promedios["EQUIPO"] == "A"), "DISTANCIA ACUMULADA (M)"] = float(1700)
df_promedios.loc[(df_promedios["CATEGORIA"] == "Cadete") & (df_promedios["EQUIPO"] == "A"), "ALTURA-(CM)"] = float(36.00)
df_promedios.loc[(df_promedios["CATEGORIA"] == "Cadete") & (df_promedios["EQUIPO"] == "A"), "TIEMPO 0-40M (SEG)"] = float(5.7)

df_promedios.loc[(df_promedios["CATEGORIA"] == "Juvenil") & (df_promedios["EQUIPO"] == "A"), "DISTANCIA ACUMULADA (M)"] = float(2100)
df_promedios.loc[(df_promedios["CATEGORIA"] == "Juvenil") & (df_promedios["EQUIPO"] == "A"), "ALTURA-(CM)"] = float(41.00)
df_promedios.loc[(df_promedios["CATEGORIA"] == "Juvenil") & (df_promedios["EQUIPO"] == "A"), "TIEMPO 0-40M (SEG)"] = float(5.1)

#st.dataframe(df_promedios)

st.divider()
###################################################

if df_datos_filtrado.empty or len(df_datos_filtrado) > 1:
    st.warning("No se ha encontrado información o aun no ha seleccionado a un jugador.")
else:
    df_joined_filtrado, df_jugador, categoria, equipo = player.player_block(df_datos_filtrado, df_datos, df_final, unavailable, idioma)

###################################################
    if not df_datos_filtrado.empty:

        #traducidas = util.traducir_lista(lista_columnas + ["REPORTE"], idioma)
        ##tab1,tab2,tab3 = st.tabs(["👤 Perfil", "📈 Rendimiento", "📆 Historicos" ,"📉 Comparaciones", "🏥 Alertas"])
        antropometria, cmj, sprint, yoyo, agilidad, rsa, reporte = st.tabs(lista_columnas + ["REPORTE"])
        #st.text(lista_columnas)
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


        with antropometria:
            if len(df_joined_filtrado) > 0:

                ###################################################
                ###################################################
                ## ANTROPOMETRIA
                columns = list(test_cat.get(lista_columnas[0], []))
                
                df_anthropometrics = df_joined_filtrado[[fecha_registro] + columns]
                df_anthropometrics = df_anthropometrics.reset_index(drop=True)
    
                if not util.columnas_sin_datos_utiles(df_anthropometrics, [fecha_registro]):
                    
                    # Eliminar las filas donde TODAS las columnas filtradas sean cero o nulas
                    df_anthropometrics = df_anthropometrics[~(df_anthropometrics[columns] == 0).all(axis=1)]
                    #percentiles_an = util.calcular_percentiles(df_anthropometrics.iloc[0], referencia_test, columnas_filtradas)
                   
                    st.markdown("📆 **Ultímas Mediciones**")
                    st.text(categoria)

                    if categoria == "Juvenil":
                        zona_optima_min = 10
                        zona_optima_max = 12.5   
                    elif categoria == "Cadete":
                        zona_optima_min = 11
                        zona_optima_max = 13  
                    
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
                        st.metric(f"Último Registro",act)

                    if(gact < zona_optima_min) or (gact > zona_optima_max):
                        st.warning(f"El porcentaje de grasa corporal ({gact:.2f}%) está fuera de la zona óptima ({zona_optima_min:.2f}% - {zona_optima_max:.2f}%) para su categoria", icon="⚠️")
                    else:
                        st.success(f"El porcentaje de grasa corporal ({gact:.2f}%) está dentro de la zona óptima ({zona_optima_min:.2f}% - {zona_optima_max:.2f}%) para su categoria", icon="✅")
                    
                    figalt = graphics.get_height_graph(df_anthropometrics, idioma)

                    df_anthropometrics_sin_ceros = df_anthropometrics[~(df_anthropometrics[columns] == 0).any(axis=1)]
                    figant = graphics.get_anthropometrics_graph(df_anthropometrics_sin_ceros, categoria, zona_optima_min, zona_optima_max, idioma)
                    
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
                        st.metric(f"Último Registro",act)

                    promedio_cmj = df_promedios.loc[
                    (df_promedios["CATEGORIA"] == categoria) & (df_promedios["EQUIPO"] == equipo_promedio),
                    columns[0]].values[0] if not df_promedios.loc[
                    (df_promedios["CATEGORIA"] == categoria) & (df_promedios["EQUIPO"] == equipo_promedio),
                    columns[0]].empty else None

                    promedio_cmj = float(promedio_cmj)
                    cactc = float(cactc)

                    if promedio_cmj is not None:
                        if(cactc < promedio_cmj):
                            st.warning(f"{metrica_cmj} ({cactc:.2f} cm) está por debajo del promedio de su categoría ({promedio_cmj:.2f} cm)", icon="⚠️")
                        else:
                            st.success(f"{metrica_cmj} ({cactc:.2f} cm) está por encima del promedio de su categoría ({promedio_cmj:.2f} cm)", icon="✅")
                    #graphics.get_cmj_graph(df_cmj, df_promedios, categoria, equipo)

                    #st.divider()
                    cola, colb = st.columns([2.5,1])

                    with cola:
                        figcmj = graphics.get_cmj_graph(df_cmj, df_promedios, categoria, equipo_promedio, [columns[0]], fecha_registro, idioma)
                    with colb:
                        st.markdown("📊 **Históricos**")
                        styled_df = util.aplicar_semaforo(df_cmj)
                        st.dataframe(df_cmj)
                        #st.dataframe(df_cmj)
                    #    st.markdown("📊 **Tabla de percentiles: Comparación del jugador con atletas de su misma edad**")
                    #    graphics.mostrar_percentiles_coloreados(df_cmj.iloc[0], percentiles_cmj)  
                else:
                    st.text(mensaje_no_data) 
                    percentiles_cmj = None      
            else:
                st.text(mensaje_no_data)
                percentiles_cmj = None
          
        with sprint:
            if len(df_joined_filtrado) > 0:

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
                    
                    if(act05t != 0) or (act05v != 0):
                        figsp05 = graphics.get_sprint_graph(df_sprint, df_promedios, categoria, equipo_promedio, columns[0],columns[1], fecha_registro, idioma)

                    if(act040t != 0) or (act040v != 0):
                        figsp040 = graphics.get_sprint_graph(df_sprint, df_promedios, categoria, equipo_promedio, columns[2],columns[3], fecha_registro, idioma)
                
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
                        st.metric(columns[0].capitalize(),f'{act:,.1f}', f'{variacion:,.1f}')

                    with col2:
                        act = df_yoyo[columns[1]].iloc[0]
                        ant = df_yoyo[columns[1]].iloc[1] if len(df_yoyo) > 1 else 0
                        variacion = 1
                        st.metric(columns[1].capitalize(),f'{act:,.1f}', f'{variacion:,.1f}')
                    
                    with col3:
                        act = df_yoyo[fecha_registro].iloc[0]
                        st.metric(f"Último Registro",act)

                    st.divider()

                    cola, colb = st.columns([2.5,1.5])

                    with cola:
                        figyoyo = graphics.get_yoyo_graph(df_yoyo, df_promedios, categoria, equipo_promedio, columns[1], fecha_registro, idioma)
                    with colb:   
                        st.markdown("📊 **Históricos**")
                        styled_df = util.aplicar_semaforo(df_yoyo)
                        st.dataframe(df_yoyo)    
                    #    st.markdown("📊 **Tabla de percentiles: Comparación del jugador con atletas de su misma edad**")
                    #    graphics.mostrar_percentiles_coloreados(df_yoyo.iloc[0], percentiles_yoyo)  
                else:
                    st.text(mensaje_no_data)
                    percentiles_yoyo = None
            else:
                st.text(mensaje_no_data)
                percentiles_yoyo = None

        with agilidad:
            #st.dataframe(df_joined_filtrado)
            if len(df_joined_filtrado) > 0: 
                columns = list(test_cat.get(lista_columnas[4], []))
                df_agilty = df_joined_filtrado[[fecha_registro] + columns]

                df_agilty = df_agilty.loc[~(df_agilty[columns].fillna(0) == 0).all(axis=1)]

                todos_ceros = (df_agilty[columns] == 0).all().all()

                if not todos_ceros:
                    
                    df_agilty = df_agilty[~(df_agilty[columns] == 0).any(axis=1)]
                    #percentiles_ag = util.calcular_percentiles(df_agilty.iloc[0], referencia_test, columnas_filtradas)
                    
                    st.markdown("📆 **Ultímas Mediciones**")
                    col1, col2, col3 = st.columns(3)

                    with col1:
                        act = df_agilty[columns[0]].iloc[0]
                        ant = df_agilty[columns[0]].iloc[1] if len(df_agilty) > 1 else 0
                        variacion = act - ant
                        st.metric(columns[0].capitalize(),f'{float(act):,.2f}', f'{float(variacion):,.2f}', delta_color="inverse")
                        
                    with col2:
                        act = df_agilty[columns[1]].iloc[0]
                        ant = df_agilty[columns[1]].iloc[1] if len(df_agilty) > 1 else 0
                        variacion = act - ant
                        st.metric(columns[1].capitalize(),f'{float(act):,.2f}', f'{float(variacion):,.2f}', delta_color="inverse")

                    with col3:
                        act = df_agilty[fecha_registro].iloc[0] if len(df_agilty) > 0 else 0
                        st.metric(f"Último Registro",act)

                    figag = graphics.get_agility_graph_combined(df_agilty, df_promedios, categoria, equipo, columns, fecha_registro, idioma)
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
                        st.metric(columns[0].capitalize(),f'{act:,.1f}', f'{variacion:,.1f}', delta_color="inverse")

                    with col2:
                        act = df_rsa[columns[1]].iloc[0]
                        ant = df_rsa[columns[1]].iloc[1] if len(df_rsa) > 1 else 0
                        variacion = act - ant
                        st.metric(columns[1].capitalize(),f'{act:,.1f}', f'{variacion:,.1f}')

                    with col3:
                        act = df_rsa[fecha_registro].iloc[0]
                        st.metric(f"Último Registro",act)

                    #styled_dfa = util.aplicar_semaforo(df_rsa[columna_fecha_registro + columns], invertir=True)

                    cola, colb = st.columns([2.5,1])
                    with cola:
                        figrsat = graphics.get_rsa_graph(df_rsa, df_promedios, categoria, equipo_promedio, columns, fecha_registro, idioma)
                    with colb:    
                        st.markdown("📊 **Históricos**")
                        st.dataframe(df_rsa[[fecha_registro] + [columns[0]]]) 

                    styled_dfb = util.aplicar_semaforo(df_rsa[[fecha_registro] + columns])
                    colc, cold = st.columns([2.5,1])
                    with colc:
                        figrsav = graphics.get_rsa_velocity_graph(df_rsa, df_promedios, categoria, equipo_promedio, columns[1], fecha_registro, idioma)
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
                if figalt is not None and figant is not None:
                    graficos_pdf.append("COMPOSICIÓN CORPORAL")

                # CMJ
                if figcmj is not None:
                    graficos_pdf.append("CMJ")

                # SPRINT
                if figsp05 is not None or figsp040 is not None:
                    graficos_pdf.append("SPRINT")

                # YO-YO
                if figyoyo is not None:
                    graficos_pdf.append("YO-YO")

                # AGILIDAD
                if figag is not None:
                    graficos_pdf.append("AGILIDAD")

                # RSA (Tiempo y Velocidad)
                if figrsat is not None and figrsav is not None:
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

                    try:
                        # 1. Generar PDF como bytes (puede tardar)
                        pdf_bytes = util.generate_pdf(
                            df_jugador, df_anthropometrics, df_agilty, df_sprint, 
                            df_cmj, df_yoyo, df_rsa, figs_filtrados, idioma)

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