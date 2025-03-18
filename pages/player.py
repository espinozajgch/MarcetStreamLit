import streamlit as st
from utils import util
from utils import graphics

from streamlit_gsheets import GSheetsConnection

import pandas as pd
import plotly.express as px
import numpy as np
import matplotlib.pyplot as plt
import plotly.graph_objects as go
import seaborn as sns
import login as login

st.set_page_config(
    page_title="PlayerHub",
    page_icon="⚽",
    layout="wide",
    initial_sidebar_state="expanded"
)

login.generarLogin()

# 🔹 Bloquear contenido si el usuario no está en session_state
if 'usuario' not in st.session_state:
    #st.warning("Debes iniciar sesión para acceder a esta página.")
    st.stop()  # 🔹 Detiene la ejecución del código si no hay sesión activa
else:
    st.header(" :blue[Player Hub]")
    st.subheader("Datos individuales, historicos y alertas")

    # Create a connection object.
    conn = st.connection("gsheets", type=GSheetsConnection)
    
    df_datos = util.getDatos(conn)
    df_joined = util.getJoinedDataFrame(conn)
    
    df_datos_filtrado = util.generateFilters(df_datos)
    
    #st.dataframe(df_datos_filtrado)

    #st.button("📄 Generar PDF")
        #pdf = util.generar_pdf()
        #pdf.output("reporte.pdf")  # Guardar el archivo
        #with open("reporte.pdf", "rb") as file:
        #    st.download_button("📥 Descargar PDF", file, file_name="reporte.pdf", mime="application/pdf")

    st.divider()
    ###################################################

    if df_datos_filtrado.empty:
        st.text("No se encontró información del jugador seleccionado.")
    else:
        jugador_id = df_datos_filtrado["ID"].dropna().astype(str).str.strip().unique().tolist()        
        df_jugador = df_datos[df_datos["ID"]==jugador_id[0]]
        df_joined_filtrado=df_joined[df_joined["ID"]==jugador_id[0]]
        #datatest= util.getDataTest(conn)
        
        response = util.get_photo(df_jugador['URL'].iloc[0])

        nombre = df_jugador['JUGADOR'].iloc[0]
        nacionalidad = df_jugador['NACIONALIDAD'].iloc[0]
        bandera = util.obtener_bandera(nacionalidad.replace(",", "."))

        st.markdown(f"## {nombre}")
        st.markdown(f"##### **_:blue[NACIONALIDAD:]_** _{nacionalidad}_ {bandera}")

        col1, col2, col3 = st.columns([1, 2, 2])

        with col1:
            if response:
                st.image(response.content, width=150)

        with col2:
            categoria = df_jugador['CATEGORIA'].iloc[0]
            equipo = df_jugador['EQUIPO'].iloc[0]
            fnacimiento = df_jugador['FECHA DE NACIMIENTO'].iloc[0]

            st.metric(label="Equipo - Categoria", value=f" {categoria} {equipo}", border=True)
            st.metric(label="F. Nacimiento", value=f"{fnacimiento}", border=True)

        with col3:
            edad = df_jugador['EDAD'].iloc[0]
            demarcacion = df_jugador['DEMARCACIÓN'].iloc[0]
            st.metric(label="Posición", value=f"{demarcacion.capitalize()}", border=True)
            st.metric(label="Edad", value=f"{edad} años", border=True)

    ###################################################

    if not df_datos_filtrado.empty:
        ##tab1,tab2,tab3 = st.tabs(["👤 Perfil", "📈 Rendimiento", "📆 Historicos" ,"📉 Comparaciones", "🏥 Alertas"])
        antropometria,agilidad,sprint,cmj,yoyo,rsa = st.tabs(["ANTROPOMETRIA", "AGILIDAD" ,"SPRINT LINEAL", "CMJ", "YO-YO", "RSA"])
        with antropometria:
            if len(df_joined_filtrado) > 0:

                ###################################################
                ###################################################
                ## ANTROPOMETRIA

                df_anthropometrics = df_joined_filtrado[["FECHA REGISTRO", "ALTURA", "PESO", "MG [KG]", "GRASA (%)"]]
                df_anthropometrics = df_anthropometrics.reset_index(drop=True)
                
                #st.markdown("### :blue[ANTROPOMETRÍA]")
                st.markdown("📆 **Ultímas Mediciones**")
                #st.dataframe(df_anthropometrics)    
               
                col1, col2, col3, col4, col5 = st.columns(5)
                with col1:
                    act = df_anthropometrics['ALTURA'].iloc[0]
                    ant = df_anthropometrics['ALTURA'].iloc[1] if len(df_anthropometrics) > 1 else 0
                    variacion = float(act) - float(ant)
                    st.metric(f"Altura (cm)",f'{act:,.2f}', f'{variacion:,.2f}')

                with col2:
                    act = df_anthropometrics['PESO'].iloc[0]
                    ant = df_anthropometrics['PESO'].iloc[1] if len(df_anthropometrics) > 1 else 0
                    variacion = act - ant
                    st.metric(f"Peso (Kg)",f'{act:,.2f}', f'{variacion:,.2f}')

                with col3:
                    act = df_anthropometrics['MG [KG]'].iloc[0]
                    ant = df_anthropometrics['MG [KG]'].iloc[1] if len(df_anthropometrics) > 1 else 0
                    variacion = act - ant
                    st.metric(f"MG (Kg)",f'{act:,.2f}', f'{variacion:,.2f}')

                with col4:
                    act = df_anthropometrics['GRASA (%)'].iloc[0]
                    ant = df_anthropometrics['GRASA (%)'].iloc[1] if len(df_anthropometrics) > 1 else 0
                    variacion = act - ant
                    st.metric(f"Grasa (%)",f'{act:,.2f}', f'{variacion:,.2f}')
                
                with col5:
                    act = df_anthropometrics['FECHA REGISTRO'].iloc[0]
                    st.metric(f"Último Registro",act)

                #st.dataframe(df_anthropometrics)
                graphics.get_anthropometrics_graph(df_anthropometrics)
                
                c1, c2 = st.columns([2,1.5])     
                with c1:
                    # Cálculo del IMC
                    # Verificar si PESO o ALTURA son 0 o nulos (OR entre condiciones)
                    mask = (df_anthropometrics["PESO"] == 0) | (df_anthropometrics["ALTURA"] == 0) | df_anthropometrics["PESO"].isnull() | df_anthropometrics["ALTURA"].isnull()

                    # Aplicar el cálculo del IMC y la categorización solo cuando la condición no se cumpla
                    df_anthropometrics["IMC"] = np.where(mask, np.nan, df_anthropometrics["PESO"] / ((df_anthropometrics["ALTURA"] / 100) ** 2))

                    # Asegurarse de que la columna "IMC" no contenga "N/A" como string
                    df_anthropometrics["Categoría IMC"] = np.where(df_anthropometrics["IMC"].isna(), "N/A", df_anthropometrics["IMC"].apply(util.categorizar_imc))

                    # Índice de grasa corporal
                    df_anthropometrics["Índice de grasa"] = np.where(mask, np.nan, (df_anthropometrics["GRASA (%)"] * df_anthropometrics["PESO"]) / 100)
                    df_anthropometrics["Categoría Grasa"] = np.where(df_anthropometrics["IMC"].isna(), "N/A", df_anthropometrics["GRASA (%)"].apply(util.categorizar_grasa))

                    #df_anthropometrics = util.calcular_imc_indice_grasa(df_anthropometrics)
                    df_anthropometrics[["ALTURA", "PESO", "IMC", "Índice de grasa"]] = df_anthropometrics[["ALTURA", "PESO", "IMC", "Índice de grasa"]].round(2)

                    st.markdown("📊 **Análisis de IMC y Porcentaje de Grasa Corporal**")
                    st.dataframe(df_anthropometrics[["FECHA REGISTRO", "ALTURA", "PESO", "IMC", "Categoría IMC", "Índice de grasa", "Categoría Grasa"]]
                    .style
                    .format({"ALTURA": "{:.2f}", "PESO": "{:.2f}", "IMC": "{:.2f}", "Índice de grasa": "{:.2f}"})  # Aplica el formato de 2 decimales
                    .applymap(util.color_categorias, subset=["Categoría IMC", "Categoría Grasa"]))
                with c2:
                    # Cálculo de estadísticas
                    stats = {
                        "ALTURA": [df_anthropometrics["ALTURA"].mean(), df_anthropometrics["ALTURA"].max(), df_anthropometrics["ALTURA"].min()],
                        "PESO": [df_anthropometrics["PESO"].mean(), df_anthropometrics["PESO"].max(), df_anthropometrics["PESO"].min()],
                        "MG [KG]": [df_anthropometrics["MG [KG]"].mean(), df_anthropometrics["MG [KG]"].max(), df_anthropometrics["MG [KG]"].min()],
                        "GRASA (%)": [df_anthropometrics["GRASA (%)"].mean(), df_anthropometrics["GRASA (%)"].max(), df_anthropometrics["GRASA (%)"].min()],
                    }

                    stats_df = pd.DataFrame(stats, index=["Promedio", "Máximo", "Mínimo"])

                    st.markdown("📊 **Valores máximos, mínimos y promedio**")
                    st.dataframe(stats_df)

            else:
                st.text("El Jugador seleccionado no cuenta con datos suficientes")
        with agilidad:
            if len(df_joined_filtrado) > 0: 
                df_agilty = df_joined_filtrado[["FECHA REGISTRO", "505-DOM [SEG]", "505-ND [SEG]"]]
                df_agilty = df_agilty.reset_index(drop=True)

                st.markdown("📆 **Ultímas Mediciones**")
                col1, col2, col3 = st.columns(3)

                with col1:
                    act = df_agilty['505-DOM [SEG]'].iloc[0]
                    ant = df_agilty['505-DOM [SEG]'].iloc[1] if len(df_agilty) > 1 else 0
                    variacion = act - ant
                    st.metric(f"505-DOM [SEG]",f'{act:,.2f}', f'{variacion:,.2f}')
                    
                with col2:
                    act = df_agilty['505-ND [SEG]'].iloc[0]
                    ant = df_agilty['505-ND [SEG]'].iloc[1] if len(df_agilty) > 1 else 0
                    variacion = act - ant
                    st.metric(f"505-ND [SEG]",f'{act:,.2f}', f'{variacion:,.2f}')

                with col3:
                    act = df_agilty['FECHA REGISTRO'].iloc[0] if len(df_agilty) > 1 else 0
                    st.metric(f"Último Registro",act)

                graphics.get_agilty_graph(df_agilty)

                st.markdown("📊 **Históricos**")
                styled_df = util.aplicar_semaforo(df_agilty)
                st.dataframe(styled_df)
                #st.dataframe(df_agilty)
            else:
                st.text("El Jugador seleccionado no cuenta con datos suficientes")
            
        with sprint:
            if len(df_joined_filtrado) > 0:
                df_sprint = df_joined_filtrado[["FECHA REGISTRO", "TOTAL 40M [SEG]", "TIEMPO 0-5M [SEG]", "VEL 0-5M [M/S]", 
                                                "TIEMPO 5-20M [SEG]", "VEL 5-20M [M/S]", "TIEMPO 20-40M [SEG]",
                                                "VEL 20-40M [M/S]"]]
                
                df_sprint = df_sprint.reset_index(drop=True)
    
                st.markdown("📆 **Ultímas Mediciones**")

                col1, col2, col3, col4, col5, col6, col7 = st.columns(7)

                with col1:
                    act = df_sprint['TOTAL 40M [SEG]'].iloc[0]
                    ant = df_sprint['TOTAL 40M [SEG]'].iloc[1] if len(df_sprint) > 1 else 0
                    variacion = act - ant
                    st.metric(f"TOTAL 40M [SEG]",f'{act:,.2f}', f'{variacion:,.2f}')

                with col2:
                    act = df_sprint['TIEMPO 0-5M [SEG]'].iloc[0]
                    ant = df_sprint['TIEMPO 0-5M [SEG]'].iloc[1] if len(df_sprint) > 1 else 0
                    variacion = act - ant
                    st.metric(f"TIEMPO 0-5M [SEG]",f'{act:,.2f}', f'{variacion:,.2f}')

                with col3:
                    act = df_sprint['VEL 0-5M [M/S]'].iloc[0]
                    ant = df_sprint['VEL 0-5M [M/S]'].iloc[1] if len(df_sprint) > 1 else 0
                    variacion = act - ant
                    st.metric(f"VEL 0-5M [M/S]",f'{act:,.2f}', f'{variacion:,.2f}')

                with col4:
                    act = df_sprint['TIEMPO 5-20M [SEG]'].iloc[0]
                    ant = df_sprint['TIEMPO 5-20M [SEG]'].iloc[1] if len(df_sprint) > 1 else 0
                    variacion = act - ant
                    st.metric(f"TIEMPO 5-20M [SEG]",f'{act:,.2f}', f'{variacion:,.2f}')

                with col5:
                    act = df_sprint['VEL 5-20M [M/S]'].iloc[0]
                    ant = df_sprint['VEL 5-20M [M/S]'].iloc[1] if len(df_sprint) > 1 else 0
                    variacion = act - ant
                    st.metric(f"VEL 5-20M [M/S]",f'{act:,.2f}', f'{variacion:,.2f}')

                with col6:
                    act = df_sprint['TIEMPO 20-40M [SEG]'].iloc[0]
                    ant = df_sprint['TIEMPO 20-40M [SEG]'].iloc[1] if len(df_sprint) > 1 else 0
                    variacion = act - ant
                    st.metric(f"TIEMPO 20-40M [SEG]",f'{act:,.2f}', f'{variacion:,.2f}')

                with col7:
                    act = df_sprint['VEL 20-40M [M/S]'].iloc[0]
                    ant = df_sprint['VEL 20-40M [M/S]'].iloc[1] if len(df_sprint) > 1 else 0
                    variacion = act - ant
                    st.metric(f"VEL 20-40M [M/S]",f'{act:,.2f}', f'{variacion:,.2f}')


                # Mostrar el DataFrame estilizado en Streamlit
                st.markdown("📊 **Históricos**")
                styled_df = util.aplicar_semaforo(df_sprint)
                st.dataframe(styled_df)
                #st.dataframe(df_sprint)      
            else:
                st.text("El Jugador seleccionado no cuenta con datos suficientes")
        with cmj:
            if len(df_joined_filtrado) > 0:
                df_cmj = df_joined_filtrado[["FECHA REGISTRO", "CMJ [cm]", "CMJ [W]"]]
                df_cmj = df_cmj.reset_index(drop=True)
                
                st.markdown("📆 **Ultímas Mediciones**")

                col1, col2, col3 = st.columns(3)

                with col1:
                    act = df_cmj['CMJ [cm]'].iloc[0]
                    ant = df_cmj['CMJ [cm]'].iloc[1] if len(df_cmj) > 1 else 0
                    variacion = act - ant
                    st.metric(f"CMJ [cm]",f'{act:,.1f}', f'{variacion:,.1f}')

                with col2:
                    act = df_cmj['CMJ [W]'].iloc[0]
                    ant = df_cmj['CMJ [W]'].iloc[1] if len(df_cmj) > 1 else 0
                    variacion = act - ant
                    st.metric(f"CMJ [W]",f'{act:,.1f}', f'{variacion:,.1f}')

                with col3:
                    act = df_agilty['FECHA REGISTRO'].iloc[0]
                    st.metric(f"Último Registro",act)

                graphics.get_cmj_graph(df_cmj)

                st.markdown("📊 **Históricos**")
                styled_df = util.aplicar_semaforo(df_cmj)
                st.dataframe(styled_df)
                #st.dataframe(df_cmj)
                
            else:
                st.text("El Jugador seleccionado no cuenta con datos suficientes")
                
        with yoyo:

            if len(df_joined_filtrado) > 0:
                df_yoyo = df_joined_filtrado[["FECHA REGISTRO", "TEST", "SPEED [km/h]", "ACCUMULATED SHUTTLE DISTANCE [m]"]]
                df_yoyo = df_yoyo.reset_index(drop=True)
            
                st.markdown("📆 **Ultímas Mediciones**")
                col1, col2, col3, col4 = st.columns(4)

                with col1:
                    act = df_yoyo['SPEED [km/h]'].iloc[0]
                    ant = df_yoyo['SPEED [km/h]'].iloc[1] if len(df_yoyo) > 1 else 0
                    variacion = 1
                    st.metric(f"505-ND [SEG]",f'{act:,.1f}', f'{variacion:,.1f}')

                with col2:
                    act = df_yoyo['ACCUMULATED SHUTTLE DISTANCE [m]'].iloc[0]
                    ant = df_yoyo['ACCUMULATED SHUTTLE DISTANCE [m]'].iloc[1] if len(df_yoyo) > 1 else 0
                    variacion = 1
                    st.metric(f"505-ND [SEG]",f'{act:,.1f}', f'{variacion:,.1f}')
                
                with col3:
                    act = df_yoyo['TEST'].iloc[0]
                    st.metric(f"TEST",act)

                with col4:
                    act = df_agilty['FECHA REGISTRO'].iloc[0]
                    st.metric(f"Último Registro",act)

                st.divider()
                graphics.get_yoyo_graph(df_yoyo)

                st.markdown("📊 **Históricos**")
                styled_df = util.aplicar_semaforo(df_yoyo)
                st.dataframe(styled_df)
                #st.dataframe(df_yoyo)           
            else:
                st.text("El Jugador seleccionado no cuenta con datos suficientes")   
        with rsa:
            if len(df_joined_filtrado) > 0:
                df_rsa = df_joined_filtrado[["FECHA REGISTRO", "MEDIDA EN TIEMPO (SEG)","VELOCIDAD (M*SEG)" ]]

                df_rsa = df_rsa.reset_index(drop=True)
                
                st.markdown("📆 **Ultímas Mediciones**")

                col1, col2, col3 = st.columns(3)

                with col1:
                    act = df_rsa['MEDIDA EN TIEMPO (SEG)'].iloc[0]
                    ant = df_rsa['MEDIDA EN TIEMPO (SEG)'].iloc[1] if len(df_rsa) > 1 else 0
                    variacion = act - ant
                    st.metric(f"MEDIDA EN TIEMPO (SEG)",f'{act:,.1f}', f'{variacion:,.1f}')

                with col2:
                    act = df_rsa['VELOCIDAD (M*SEG)'].iloc[0]
                    ant = df_rsa['VELOCIDAD (M*SEG)'].iloc[1] if len(df_rsa) > 1 else 0
                    variacion = act - ant
                    st.metric(f"VELOCIDAD (M*SEG)",f'{act:,.1f}', f'{variacion:,.1f}')

                with col3:
                    act = df_agilty['FECHA REGISTRO'].iloc[0]
                    st.metric(f"Último Registro",act)

                graphics.get_rsa_graph(df_rsa)

                st.markdown("📊 **Históricos**")
                styled_df = util.aplicar_semaforo(df_rsa)
                st.dataframe(styled_df)
                #st.dataframe(df_rsa)
            else:
                st.text("El Jugador seleccionado no cuenta con datos suficientes")  