import streamlit as st
from utils import util
from utils import graphics
from datetime import datetime

from streamlit_gsheets import GSheetsConnection

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

# 🔐 Verificación de sesión
login.generarLogin()
if "usuario" not in st.session_state:
    st.stop()

mensaje_no_data = "El Jugador seleccionado no cuenta con datos suficientes para mostrar esta sección"

st.header(" :blue[Player Hub] :material/contacts:", divider=True)
#st.subheader("Datos individuales, historicos y alertas")

# Create a connection object.
conn = st.connection("gsheets", type=GSheetsConnection)

df_datos, df_data_test = util.getData(conn)
df_joined = util.getJoinedDataFrame(conn)

df_datos_filtrado = util.get_filters(df_datos)

columnas_excluidas_promedio = ['FECHA REGISTRO', 'ID', "CATEGORIA", "EQUIPO" ,'TEST']

datatest_columns = util.get_dataframe_columns(df_data_test)
columnas_a_verificar = [col for col in datatest_columns if col not in columnas_excluidas_promedio]

# Agrupar por CATEGORIA y EQUIPO, calcular promedio
df_promedios = df_data_test.groupby(["CATEGORIA", "EQUIPO"])[columnas_a_verificar].mean().reset_index()

# Redondear si lo deseas
df_promedios = df_promedios.round(2)

#st.dataframe(df_promedios)

st.divider()
###################################################

if df_datos_filtrado.empty or len(df_datos_filtrado) > 1:
    st.warning("No se ha encontrado información o aun no ha seleccionado a un jugador.")
else:
    
    # Obtener ID del jugador seleccionado (único y limpio)
    ids_disponibles = df_datos_filtrado["ID"].dropna().astype(str).str.strip().unique().tolist()

    # Validar que exista al menos un ID
    if ids_disponibles:
        jugador_id = ids_disponibles[0]

        columnas_excluidas = ["FECHA REGISTRO"]

        # Filtrar los DataFrames por el ID seleccionado
        df_jugador = df_datos[df_datos["ID"].astype(str).str.strip() == jugador_id]
        df_joined_filtrado = df_joined[df_joined["ID"].astype(str).str.strip() == jugador_id]

        jugador = df_jugador.iloc[0]
        referencia = df_datos[df_datos["EDAD"] == jugador["EDAD"]]
        referencia_test = df_data_test[df_data_test["ID"].isin(referencia["ID"])]
            
        # Mostrar DataFrame principal
        #st.dataframe(df_joined_filtrado)

        response = util.get_photo(df_jugador['FOTO PERFIL'].iloc[0])

        id = df_jugador['ID'].iloc[0]
        nombre = df_jugador['JUGADOR'].iloc[0]
        nacionalidad = df_jugador['NACIONALIDAD'].iloc[0]
        bandera = util.obtener_bandera(nacionalidad.replace(",", "."))


        st.markdown(f"## {nombre} ")
        st.markdown(f"##### **_:blue[ID:]_** _{id}_ | **_:blue[NACIONALIDAD:]_** _{nacionalidad}_ {bandera}")

        col1, col2, col3 = st.columns([1, 2, 2])

        with col1:
            if response:
                st.image(response.content, width=150)
            else:
                st.image("assets/images/profile.png", width=180)
        with col2:
            categoria = df_jugador['CATEGORIA'].iloc[0]
            equipo = df_jugador['EQUIPO'].iloc[0]
            fnacimiento = df_jugador['FECHA DE NACIMIENTO'].iloc[0]

            st.metric(label="Equipo - Categoria", value=f" {categoria} {equipo}", border=True)
            st.metric(label="F. Nacimiento", value=f"{fnacimiento}", border=True)

        with col3:
            edad = df_jugador['EDAD'].iloc[0]
            demarcacion = df_jugador['DEMARCACION'].iloc[0]
            st.metric(label="Posición", value=f"{demarcacion.capitalize()}", border=True)
            st.metric(label="Edad", value=f"{edad:,.0f} años", border=True)
    else:
        st.warning("⚠️ No se encontró ningún ID válido en los datos filtrados.")

###################################################

    if not df_datos_filtrado.empty:
        ##tab1,tab2,tab3 = st.tabs(["👤 Perfil", "📈 Rendimiento", "📆 Historicos" ,"📉 Comparaciones", "🏥 Alertas"])
        antropometria, cmj, sprint, yoyo, agilidad, rsa, reporte = st.tabs(["ANTROPOMETRIA", "CMJ", "SPRINT LINEAL", "YO-YO", "AGILIDAD", "RSA", "REPORTE"])
        
        figan = None
        figcmj = None
        figagd = None
        figagnd = None
        figspt = None
        figspv = None
        figyoyo = None
        figrsat = None
        figrsav = None
        
        with antropometria:
            if len(df_joined_filtrado) > 0:

                ###################################################
                ###################################################
                ## ANTROPOMETRIA
                df_anthropometrics = df_joined_filtrado[["FECHA REGISTRO", "ALTURA (CM)", "PESO (KG)", "GRASA (%)"]]
                df_anthropometrics = df_anthropometrics.reset_index(drop=True)
    
                columnas_estructura = util.get_dataframe_columns(df_anthropometrics)
                # Eliminar columnas excluidas
                columnas_filtradas = [col for col in columnas_estructura if col not in columnas_excluidas]
                #todos_ceros = (df_anthropometrics[columnas_filtradas] == 0).all().all()

                if not util.columnas_sin_datos_utiles(df_anthropometrics, columnas_excluidas):
                    df_anthropometrics = df_anthropometrics[~(df_anthropometrics[columnas_estructura] == 0).any(axis=1)]
                    percentiles_an = util.calcular_percentiles(df_anthropometrics.iloc[0], referencia_test, columnas_filtradas)
                    
                    #st.markdown("### :blue[ANTROPOMETRÍA]")
                    st.markdown("📆 **Ultímas Mediciones**")
                    #st.dataframe(df_anthropometrics.iloc[0])    
                    
                    col1, col2, col3, col4 = st.columns(4)
                    with col1:
                        act = df_anthropometrics['ALTURA (CM)'].iloc[0]
                        ant = df_anthropometrics['ALTURA (CM)'].iloc[1] if len(df_anthropometrics) > 1 else 0
                        variacion = float(act) - float(ant)
                        st.metric(f"Altura (cm)",f'{float(act):,.2f}', f'{float(variacion):,.2f}')

                    with col2:
                        act = df_anthropometrics['PESO (KG)'].iloc[0]
                        ant = df_anthropometrics['PESO (KG)'].iloc[1] if len(df_anthropometrics) > 1 else 0
                        variacion = act - ant
                        st.metric(f"Peso (Kg)",f'{float(act):,.2f}', f'{float(variacion):,.2f}')

                    #with col3:
                    #    act = df_anthropometrics['MG [KG]'].iloc[0]
                    #    ant = df_anthropometrics['MG [KG]'].iloc[1] if len(df_anthropometrics) > 1 else 0
                    #    variacion = act - ant
                    #    st.metric(f"MG (Kg)",f'{float(act):,.2f}', f'{float(variacion):,.2f}')

                    with col3:
                        act = df_anthropometrics['GRASA (%)'].iloc[0]
                        ant = df_anthropometrics['GRASA (%)'].iloc[1] if len(df_anthropometrics) > 1 else 0
                        variacion = act - ant
                        st.metric(f"Grasa (%)",f'{float(act):,.2f}')
                    
                    with col4:
                        act = df_anthropometrics['FECHA REGISTRO'].iloc[0]
                        st.metric(f"Último Registro",act)

                    #st.dataframe(df_anthropometrics)
                    #df_ang = df_anthropometrics[["FECHA REGISTRO", "PESO (KG)", "GRASA (%)"]]
                    figan = graphics.get_anthropometrics_graph(df_anthropometrics, df_promedios, categoria, equipo)
                    
                    st.divider()
                    c1, c2 = st.columns([2,1.5])     
                    with c1:
                        # Cálculo del IMC
                        # Verificar si PESO o ALTURA son 0 o nulos (OR entre condiciones)
                        mask = (df_anthropometrics["PESO (KG)"] == 0) | (df_anthropometrics["ALTURA (CM)"] == 0) | df_anthropometrics["PESO (KG)"].isnull() | df_anthropometrics["ALTURA (CM)"].isnull()

                        # Aplicar el cálculo del IMC y la categorización solo cuando la condición no se cumpla
                        df_anthropometrics["IMC"] = np.where(mask, np.nan, df_anthropometrics["PESO (KG)"] / ((df_anthropometrics["ALTURA (CM)"] / 100) ** 2))

                        # Asegurarse de que la columna "IMC" no contenga "N/A" como string
                        df_anthropometrics["Categoría IMC"] = np.where(df_anthropometrics["IMC"].isna(), "N/A", df_anthropometrics["IMC"].apply(util.categorizar_imc))

                        # Índice de grasa corporal
                        df_anthropometrics["Índice de grasa"] = np.where(mask, np.nan, (df_anthropometrics["GRASA (%)"] * df_anthropometrics["PESO (KG)"]) / 100)
                        df_anthropometrics["Categoría Grasa"] = np.where(df_anthropometrics["IMC"].isna(), "N/A", df_anthropometrics["GRASA (%)"].apply(util.categorizar_grasa))

                        #df_anthropometrics = util.calcular_imc_indice_grasa(df_anthropometrics)
                        df_anthropometrics[["ALTURA (CM)", "PESO (KG)", "IMC", "Índice de grasa"]] = df_anthropometrics[["ALTURA (CM)", "PESO (KG)", "IMC", "Índice de grasa"]].round(2)

                        st.markdown("📊 **Análisis de IMC y Porcentaje de Grasa Corporal**")
                        st.dataframe(df_anthropometrics[["FECHA REGISTRO", "ALTURA (CM)", "PESO (KG)", "IMC", "Categoría IMC", "Índice de grasa", "Categoría Grasa"]]
                        .style
                        .format({"ALTURA (CM)": "{:.2f}", "PESO (KG)": "{:.2f}", "IMC": "{:.2f}", "Índice de grasa": "{:.2f}"})  # Aplica el formato de 2 decimales
                        .map(util.color_categorias, subset=["Categoría IMC", "Categoría Grasa"]))
                    with c2:
                        # Cálculo de estadísticas
                        stats = {
                            "ALTURA (CM)": [df_anthropometrics["ALTURA (CM)"].mean(), df_anthropometrics["ALTURA (CM)"].max(), df_anthropometrics["ALTURA (CM)"].min()],
                            "PESO (KG)": [df_anthropometrics["PESO (KG)"].mean(), df_anthropometrics["PESO (KG)"].max(), df_anthropometrics["PESO (KG)"].min()],
                            "GRASA (%)": [df_anthropometrics["GRASA (%)"].mean(), df_anthropometrics["GRASA (%)"].max(), df_anthropometrics["GRASA (%)"].min()],
                        }

                        stats_df = pd.DataFrame(stats, index=["Promedio", "Máximo", "Mínimo"])

                        st.markdown("📊 **Valores máximos, mínimos y promedio**")
                        st.dataframe(stats_df.round(1))

                    #st.divider()
                    #st.markdown("📊 **Tabla de percentiles: Comparación del jugador con atletas de su misma edad**")
                    #graphics.mostrar_percentiles_coloreados(df_anthropometrics.iloc[0], percentiles_an)
                else:
                    st.text(mensaje_no_data)
                    percentiles_an = None
            else:
                st.text(mensaje_no_data)
                percentiles_an = None
        
        with cmj:
            if len(df_joined_filtrado) > 0:
                df_cmj = df_joined_filtrado[["FECHA REGISTRO", "CMJ (CM)", "CMJ (W)"]]
                df_cmj = df_cmj.reset_index(drop=True)
                
                #columnas_excluidas = ["FECHA REGISTRO", "ID", "CATEGORIA", "EQUIPO", "TEST"]
                columnas_estructura = util.get_dataframe_columns(df_cmj)

                # Eliminar columnas excluidas
                columnas_filtradas = [col for col in columnas_estructura if col not in columnas_excluidas]

                todos_ceros = (df_cmj[columnas_filtradas] == 0).all().all()

                if not todos_ceros:
                    df_cmj = df_cmj[~(df_cmj[columnas_estructura] == 0).all(axis=1)]
                    #st.dataframe(columnas_estructura)    
                    percentiles_cmj = util.calcular_percentiles(df_cmj.iloc[0], referencia_test, columnas_filtradas)
                    
                    st.markdown("📆 **Ultímas Mediciones**")
                    
                    col1, col2, col3 = st.columns(3)

                    with col1:
                        act = df_cmj['CMJ (CM)'].iloc[0]
                        ant = df_cmj['CMJ (CM)'].iloc[1] if len(df_cmj) > 1 else 0
                        variacion = act - ant
                        st.metric(f"CMJ (CM)",f'{act:,.1f}', f'{variacion:,.1f}')

                    with col2:
                        act = df_cmj['CMJ (W)'].iloc[0]
                        ant = df_cmj['CMJ (W)'].iloc[1] if len(df_cmj) > 1 else 0
                        variacion = act - ant
                        st.metric(f"CMJ (W)",f'{act:,.1f}', f'{variacion:,.1f}')

                    with col3:
                        act = df_cmj['FECHA REGISTRO'].iloc[0]
                        st.metric(f"Último Registro",act)

                    #graphics.get_cmj_graph(df_cmj, df_promedios, categoria, equipo)

                    #st.divider()
                    cola, colb = st.columns([2.5,1])

                    with cola:
                        figcmj = graphics.get_cmj_graph(df_cmj, df_promedios, categoria, equipo)

                    with colb:
                        st.markdown("📊 **Históricos**")
                        styled_df = util.aplicar_semaforo(df_cmj)
                        st.dataframe(styled_df)
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
                df_sprint = df_joined_filtrado[["FECHA REGISTRO", "TOTAL 40M (SEG)", "TIEMPO 0-5M (SEG)", "VEL 0-5M (M/S)", 
                                                "TIEMPO 5-20M (SEG)", "VEL 5-20M (M/S)", "TIEMPO 20-40M (SEG)",
                                                "VEL 20-40M (M/S)"]]
                
                df_sprint = df_sprint.reset_index(drop=True)

                #columnas_excluidas = ["FECHA REGISTRO", "ID", "CATEGORIA", "EQUIPO", "TEST"]
                columnas_estructura = util.get_dataframe_columns(df_sprint)

                # Eliminar columnas excluidas
                columnas_filtradas = [col for col in columnas_estructura if col not in columnas_excluidas]

                todos_ceros = (df_sprint[columnas_filtradas] == 0).all().all()
                
                #st.dataframe(df_sprint)
                if not todos_ceros:
                    df_sprint = df_sprint[~(df_sprint[columnas_estructura] == 0).all(axis=1)]
                    percentiles_sp = util.calcular_percentiles(df_sprint.iloc[0], referencia_test, columnas_filtradas)
                    
                    st.markdown("📆 **Ultímas Mediciones**")

                    col1, col2, col3, col4, col5, col6, col7 = st.columns(7)

                    with col1:
                        act = df_sprint['TOTAL 40M (SEG)'].iloc[0]
                        ant = df_sprint['TOTAL 40M (SEG)'].iloc[1] if len(df_sprint) > 1 else 0
                        variacion = act - ant
                        st.metric(f"TOTAL 40M (SEG)",f'{float(act):,.2f}', f'{float(variacion):,.2f}', delta_color="inverse")

                    with col2:
                        act = df_sprint['TIEMPO 0-5M (SEG)'].iloc[0]
                        ant = df_sprint['TIEMPO 0-5M (SEG)'].iloc[1] if len(df_sprint) > 1 else 0
                        variacion = act - ant
                        st.metric(f"TIEMPO 0-5M (SEG)",f'{float(act):,.2f}', f'{float(variacion):,.2f}', delta_color="inverse")

                    with col3:
                        act = df_sprint['VEL 0-5M (M/S)'].iloc[0]
                        ant = df_sprint['VEL 0-5M (M/S)'].iloc[1] if len(df_sprint) > 1 else 0
                        variacion = act - ant
                        st.metric(f"VEL 0-5M (M/S)",f'{float(act):,.2f}', f'{float(variacion):,.2f}')

                    with col4:
                        act = df_sprint['TIEMPO 5-20M (SEG)'].iloc[0]
                        ant = df_sprint['TIEMPO 5-20M (SEG)'].iloc[1] if len(df_sprint) > 1 else 0
                        variacion = act - ant
                        st.metric(f"TIEMPO 5-20M (SEG)",f'{float(act):,.2f}', f'{float(variacion):,.2f}', delta_color="inverse")

                    with col5:
                        act = df_sprint['VEL 5-20M (M/S)'].iloc[0]
                        ant = df_sprint['VEL 5-20M (M/S)'].iloc[1] if len(df_sprint) > 1 else 0
                        variacion = act - ant
                        st.metric(f"VEL 5-20M (M/S)",f'{float(act):,.2f}', f'{float(variacion):,.2f}')

                    with col6:
                        act = df_sprint['TIEMPO 20-40M (SEG)'].iloc[0]
                        ant = df_sprint['TIEMPO 20-40M (SEG)'].iloc[1] if len(df_sprint) > 1 else 0
                        variacion = act - ant
                        st.metric(f"TIEMPO 20-40M (SEG)",f'{float(act):,.2f}', f'{float(variacion):,.2f}', delta_color="inverse")

                    with col7:
                        act = df_sprint['VEL 20-40M (M/S)'].iloc[0]
                        ant = df_sprint['VEL 20-40M (M/S)'].iloc[1] if len(df_sprint) > 1 else 0
                        variacion = act - ant
                        st.metric(f"VEL 20-40M (M/S)",f'{float(act):,.2f}', f'{float(variacion):,.2f}')

                    df_sprint = util.convertir_m_s_a_km_h(df_sprint, ["VEL 0-5M (M/S)", "VEL 5-20M (M/S)", "VEL 20-40M (M/S)"])
                    st.divider()
                    cola ,colb = st.columns([2,1])
                    with cola:
                        figspt = graphics.get_sprint_time_graph(df_sprint, df_promedios, categoria, equipo)
                    with colb:
                        # Mostrar el DataFrame estilizado en Streamlit
                        st.markdown("📊 **Históricos**")
                        styled_df = util.aplicar_semaforo(df_sprint[["FECHA REGISTRO", "TIEMPO 0-5M (SEG)", "TIEMPO 20-40M (SEG)"]], invertir=True)
                        st.dataframe(styled_df)   

                    st.divider()
                    colc ,cold = st.columns([2,1])
                    with colc:
                        figspv = graphics.get_sprint_velocity_graph(df_sprint, df_promedios, categoria, equipo)
                    with cold:
                        # Mostrar el DataFrame estilizado en Streamlit
                        st.markdown("📊 **Históricos**")
                        styled_df = util.aplicar_semaforo(df_sprint[["FECHA REGISTRO", "VEL 0-5M (KM/H)", "VEL 20-40M (KM/H)"]])
                        st.dataframe(styled_df)


                    #st.divider()
                    #st.markdown("📊 **Históricos Generales**")
                    #styled_df = util.aplicar_semaforo(df_sprint)
                    #st.dataframe(df_sprint)   

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
                df_yoyo = df_joined_filtrado[["FECHA REGISTRO", "TEST", "SPEED (KM/H)", "ACCUMULATED SHUTTLE DISTANCE (M)"]]
                df_yoyo = df_yoyo.reset_index(drop=True)

                columnas_excluidas = ["FECHA REGISTRO", "TEST"]
                columnas_estructura = util.get_dataframe_columns(df_yoyo)

                # Eliminar columnas excluidas
                columnas_filtradas = [col for col in columnas_estructura if col not in columnas_excluidas]

                todos_ceros = (df_yoyo[columnas_filtradas] == 0).all().all()

                if not todos_ceros:
                    df_yoyo = df_yoyo[~(df_yoyo[columnas_estructura] == 0).all(axis=1)]
                    percentiles_yoyo = util.calcular_percentiles(df_yoyo.iloc[0], referencia_test, columnas_filtradas)
                    
                    st.markdown("📆 **Ultímas Mediciones**")
                    col1, col2, col3, col4 = st.columns(4)

                    with col1:
                        act = df_yoyo['SPEED (KM/H)'].iloc[0]
                        ant = df_yoyo['SPEED (KM/H)'].iloc[1] if len(df_yoyo) > 1 else 0
                        variacion = 1
                        st.metric(f"505-ND (SEG)",f'{act:,.1f}', f'{variacion:,.1f}')

                    with col2:
                        act = df_yoyo['ACCUMULATED SHUTTLE DISTANCE (M)'].iloc[0]
                        ant = df_yoyo['ACCUMULATED SHUTTLE DISTANCE (M)'].iloc[1] if len(df_yoyo) > 1 else 0
                        variacion = 1
                        st.metric(f"505-ND (SEG)",f'{act:,.1f}', f'{variacion:,.1f}')
                    
                    with col3:
                        act = df_yoyo['TEST'].iloc[0]
                        st.metric(f"TEST",act)

                    with col4:
                        act = df_yoyo['FECHA REGISTRO'].iloc[0]
                        st.metric(f"Último Registro",act)

                    st.divider()
                    #df_yoyo = df_yoyo.fillna(0).replace("None", 0)
                    #st.dataframe(df_yoyo) 
                    

                    #st.divider()
                    cola, colb = st.columns([2.5,1.5])

                    with cola:
                        figyoyo = graphics.get_yoyo_graph(df_yoyo, df_promedios, categoria, equipo)
                        #st.dataframe(df_yoyo)    
                    with colb:   
                        st.markdown("📊 **Históricos**")
                        df_yoyo = df_yoyo.rename(columns={"ACCUMULATED SHUTTLE DISTANCE (M)": "DISTANCE (M)"})

                        styled_df = util.aplicar_semaforo(df_yoyo)
                        st.dataframe(styled_df)    
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
                df_agilty = df_joined_filtrado[["FECHA REGISTRO", "505-DOM (SEG)", "505-ND (SEG)"]]
                df_agilty = df_agilty.reset_index(drop=True)

                #columnas_excluidas = ["FECHA REGISTRO", "ID", "CATEGORIA", "EQUIPO", "TEST"]
                columnas_estructura = util.get_dataframe_columns(df_agilty)

                # Eliminar columnas excluidas
                columnas_filtradas = [col for col in columnas_estructura if col not in columnas_excluidas]

                todos_ceros = (df_agilty[columnas_filtradas] == 0).all().all()

                if not todos_ceros:
                    
                    df_agilty = df_agilty[~(df_agilty[columnas_estructura] == 0).any(axis=1)]
                    percentiles_ag = util.calcular_percentiles(df_agilty.iloc[0], referencia_test, columnas_filtradas)
                    
                    st.markdown("📆 **Ultímas Mediciones**")
                    col1, col2, col3 = st.columns(3)

                    with col1:
                        act = df_agilty['505-DOM (SEG)'].iloc[0]
                        ant = df_agilty['505-DOM (SEG)'].iloc[1] if len(df_agilty) > 1 else 0
                        variacion = act - ant
                        st.metric(f"505-DOM (SEG)",f'{float(act):,.2f}', f'{float(variacion):,.2f}', delta_color="inverse")
                        
                    with col2:
                        act = df_agilty['505-ND (SEG)'].iloc[0]
                        ant = df_agilty['505-ND (SEG)'].iloc[1] if len(df_agilty) > 1 else 0
                        variacion = act - ant
                        st.metric(f"505-ND (SEG)",f'{float(act):,.2f}', f'{float(variacion):,.2f}', delta_color="inverse")

                    with col3:
                        act = df_agilty['FECHA REGISTRO'].iloc[0] if len(df_agilty) > 0 else 0
                        st.metric(f"Último Registro",act)

                    #st.divider()
                    #styled_df = util.aplicar_semaforo(df_agilty[["FECHA REGISTRO","505-DOM (SEG)"]])
                    cola, colb = st.columns([3,1])

                    with cola:
                        figagd = graphics.get_agility_graph_dom(df_agilty, df_promedios, categoria, equipo)
                    with colb:
                        #graphics.get_agility_graph_nd(df_agilty, df_promedios, categoria, equipo)
                        st.markdown("📊 **Históricos**")
                        st.dataframe(util.aplicar_semaforo(df_agilty[["FECHA REGISTRO","505-DOM (SEG)"]], invertir=True))
                    #    st.markdown("📊 **Tabla de percentiles: Comparación del jugador con atletas de su misma edad**")
                    #    graphics.mostrar_percentiles_coloreados(df_agilty.iloc[0], percentiles_ag)

                    #styled_df = util.aplicar_semaforo(df_agilty[["FECHA REGISTRO","505-ND (SEG)"]])
                    colc, cold = st.columns([3,1])

                    with colc:
                        figagnd = graphics.get_agility_graph_nd(df_agilty, df_promedios, categoria, equipo)
                    with cold:
                        #graphics.get_agility_graph_nd(df_agilty, df_promedios, categoria, equipo)
                        st.markdown("📊 **Históricos**")
                        st.dataframe(util.aplicar_semaforo(df_agilty[["FECHA REGISTRO","505-ND (SEG)"]], invertir=True))
                else:
                    st.text(mensaje_no_data)
                    percentiles_ag = None
            else:
                st.text(mensaje_no_data)
                percentiles_ag = None
                            
        with rsa:
            if len(df_joined_filtrado) > 0:
                df_rsa = df_joined_filtrado[["FECHA REGISTRO", "MEDIDA EN TIEMPO (SEG)","VELOCIDAD (M*SEG)" ]]

                df_rsa = df_rsa.reset_index(drop=True)
                
                #columnas_excluidas = ["FECHA REGISTRO", "ID", "CATEGORIA", "EQUIPO", "TEST"]
                columnas_estructura = util.get_dataframe_columns(df_rsa)

                # Eliminar columnas excluidas
                columnas_filtradas = [col for col in columnas_estructura if col not in columnas_excluidas]

                todos_ceros = (df_rsa[columnas_filtradas] == 0).all().all()

                if not todos_ceros:
                    df_rsa = df_rsa[~(df_rsa[columnas_estructura] == 0).all(axis=1)]
                    percentiles_rsa = util.calcular_percentiles(df_rsa.iloc[0], referencia_test, columnas_filtradas)
                    
                    st.markdown("📆 **Ultímas Mediciones**")

                    col1, col2, col3 = st.columns(3)

                    with col1:
                        act = df_rsa['MEDIDA EN TIEMPO (SEG)'].iloc[0]
                        ant = df_rsa['MEDIDA EN TIEMPO (SEG)'].iloc[1] if len(df_rsa) > 1 else 0
                        variacion = act - ant
                        st.metric(f"MEDIDA EN TIEMPO (SEG)",f'{act:,.1f}', f'{variacion:,.1f}', delta_color="inverse")

                    with col2:
                        act = df_rsa['VELOCIDAD (M*SEG)'].iloc[0]
                        ant = df_rsa['VELOCIDAD (M*SEG)'].iloc[1] if len(df_rsa) > 1 else 0
                        variacion = act - ant
                        st.metric(f"VELOCIDAD (M*SEG)",f'{act:,.1f}', f'{variacion:,.1f}')

                    with col3:
                        act = df_agilty['FECHA REGISTRO'].iloc[0]
                        st.metric(f"Último Registro",act)

                    styled_dfa = util.aplicar_semaforo(df_rsa[["FECHA REGISTRO","MEDIDA EN TIEMPO (SEG)"]], invertir=True)
                    #st.divider()
                    cola, colb = st.columns([2.5,1])

                    with cola:
                        figrsat = graphics.get_rsa_graph(df_rsa, df_promedios, categoria, equipo)
                        #st.dataframe(df_rsa)
                    with colb:    
                        st.markdown("📊 **Históricos**")
                        st.dataframe(styled_dfa) 

                    df_rsa = util.convertir_m_s_a_km_h(df_rsa, ["VELOCIDAD (M*SEG)"])
                    styled_dfb = util.aplicar_semaforo(df_rsa[["FECHA REGISTRO","VELOCIDAD (KM/H)"]])
                    colc, cold = st.columns([2.5,1])
                    with colc:
                        figrsav = graphics.get_rsa_velocity_graph(df_rsa, df_promedios, categoria, equipo)
                        #st.dataframe(df_rsa)
                    with cold:    
                        st.markdown("📊 **Históricos**")
                        st.dataframe(styled_dfb) 

                    #    st.markdown("📊 **Tabla de percentiles: Comparación del jugador con atletas de su misma edad**")
                    #    graphics.mostrar_percentiles_coloreados(df_rsa.iloc[0], percentiles_rsa) 

                else:
                    st.text(mensaje_no_data) 
                    percentiles_rsa = None      
            else:
                st.text(mensaje_no_data)
                percentiles_rsa = None
                
        with reporte:
            # # 1. Generar PDF como bytes (puede tardar)
            # pdf_bytes = util.generate_pdf(
            #     df_jugador, df_anthropometrics, df_agilty, df_sprint, 
            #     df_cmj, df_yoyo, df_rsa, figan, figcmj, figspt, figspv, figyoyo, figagd, figagnd, figrsat, figrsav, 
            # )

            # # 2. Codificar y preparar para mostrar
            # b64_pdf = base64.b64encode(pdf_bytes).decode('utf-8')
            # pdf_data = base64.b64decode(b64_pdf)

            # # Enlace de descarga con nombre específico
            # st.markdown(f'''
            #     <a href="data:application/pdf;base64,{b64_pdf}" download="Informe_Fisico_{nombre}.pdf" target="_blank">
            #     📥 Descargar PDF
            #     </a>
            # ''', unsafe_allow_html=True)

            # # 3. Mostrar PDF en Streamlit
            # html_code = f'''
            #     <object data="data:application/pdf;base64,{b64_pdf}" type="application/pdf" width="100%" height="1200px"></object>
            # '''
            # st.write(html_code, unsafe_allow_html=True)

            if len(df_joined_filtrado) > 0:

                if st.button("📄 Generar PDF"):
                    # Mostrar el status inmediatamente
                    status = st.status("🛠 Generando PDF...", state="running", expanded=True)

                    try:
                        # 1. Generar PDF como bytes (puede tardar)
                        pdf_bytes = util.generate_pdf(
                            df_jugador, df_anthropometrics, df_agilty, df_sprint, 
                            df_cmj, df_yoyo, df_rsa, figan, figcmj, figspt, figspv, figyoyo, figagd, figagnd, figrsat, figrsav
                        )

                        # 2. Codificar y preparar para mostrar
                        b64_pdf = base64.b64encode(pdf_bytes).decode('utf-8')
                        pdf_data = base64.b64decode(b64_pdf)

                        # Enlace de descarga con nombre específico
                        st.markdown(f'''
                            <a href="data:application/pdf;base64,{b64_pdf}" download="Informe_Fisico_{nombre}.pdf" target="_blank">
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