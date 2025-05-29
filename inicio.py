import streamlit as st
import pandas as pd
from streamlit_gsheets import GSheetsConnection
import matplotlib.pyplot as plt
import seaborn as sns
from utils import util
import numpy as np
import login as login
import warnings
warnings.filterwarnings("ignore", message="When grouping with a length-1 list-like")

st.set_page_config(
    page_title="Marcet - Cargas Fisicas",
    page_icon=":material/home:",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Create a connection object.
conn = st.connection("gsheets", type=GSheetsConnection)

login.generarLogin(conn)

# 🔹 Bloquear contenido si el usuario no está en session_state
if 'usuario' not in st.session_state:
    #st.warning("Debes iniciar sesión para acceder a esta página.")
    st.stop()  # 🔹 Detiene la ejecución del código si no hay sesión activa
else:
    st.header('Bienvenido a :orange[Marcet]')
    
    # Create a connection object.
    #conn = st.connection("gsheets", type=GSheetsConnection)
    #########################################################

    df_datos, df_data_test = util.getData(conn)
    df_joined = util.getJoinedDataFrame(df_datos, df_data_test)

    test = util.get_test(conn)
    test_cat = util.construir_diccionario_test_categorias(test)
    #st.dataframe(df_data_test)

    # 1. Lista de columnas que quieres excluir de la validación
    columnas_excluidas = ['FECHA REGISTRO', 'ID', 'JUGADOR', 'CATEGORIA', 'EQUIPO','anio','mes']

    # 2. Lista de columnas que sí quieres validar
    columnas_a_validar = [col for col in df_joined.columns if col not in columnas_excluidas]

    # 3. Eliminar filas donde todas las columnas a validar son NaN o None
    df_joined = df_joined.dropna(subset=columnas_a_validar, how="all")

    # 4. Eliminar filas donde todas las columnas a validar son 0
    mask = (df_joined[columnas_a_validar] == 0).all(axis=1)
    df_joined = df_joined[np.logical_not(mask)]


    total_jugadores = len(df_datos)
    df_sesiones = util.resumen_sesiones(df_joined, total_jugadores)
    #st.dataframe(df_joined)
    #########################################################

    ##st.header("Bienvenido")
    
    col1, col2, col3, col4, col5 = st.columns(5)

    with col1:
        st.metric(f"Total de Jugadores",f'{total_jugadores}')

    with col2:
        act = df_sesiones["TSUM"].iloc[0]
        ant = df_sesiones["TSUM"].iloc[1]
        variacion = act - ant
        st.metric(f"Total Asistencia (Mes)",f'{act}', f'{variacion:,.2f}')

    with col3:
        act = df_sesiones["APUS"].iloc[0]
        ant = df_sesiones["APUS"].iloc[1]
        variacion = act - ant
        st.metric(f"% Asistencia (Mes)",f'{act:,.3f}', f'{variacion:,.2f}')

    with col4:
        act = df_sesiones["JUS"].iloc[0]
        ant = df_sesiones["JUS"].iloc[1]
        variacion = act - ant
        st.metric(f"Asistencia Ultima Sesion",f'{act}', f'{variacion:,.2f}')

    with col5:
        # Mostrar la fecha si es válida
        if not df_joined.empty: 
            ultima_fecha = df_joined['FECHA REGISTRO'].iloc[0]
            if isinstance(ultima_fecha, pd.Timestamp):
                ultima_fecha_str = ultima_fecha.strftime('%d/%m/%Y')
            elif isinstance(ultima_fecha, str):
                ultima_fecha_str = ultima_fecha  # Ya es string, no necesita conversión
            else:
                ultima_fecha_str = str(ultima_fecha)  # Convertir otros tipos a string
            st.metric("Última Sesión", ultima_fecha_str)

        else:
            st.metric("Última Sesión", "####")

    st.divider()
    #st.dataframe(util.contar_jugadores_por_categoria(df_datos))
    #st.dataframe(df_sesiones)
    if not df_joined.empty: 
        st.markdown("📆 **Cantidad de Sesiones por jugador**")
        st.dataframe(util.sesiones_por_test(df_joined, test_cat))


    #st.bar_chart(np.random.randn(50,3))

    ########################################

    # import plotly.graph_objects as go

    # velocidad_max = 30.6

    # fig = go.Figure(go.Indicator(
    #     mode="gauge+number",
    #     value=velocidad_max,
    #     title={'text': "Velocidad Máxima (km/h)"},
    #     gauge={
    #         'axis': {'range': [0, 40]},
    #         'bar': {'color': "black"},
    #         'steps': [
    #             {'range': [0, 20], 'color': 'lightgray'},
    #             {'range': [20, 30], 'color': 'green'},
    #             {'range': [30, 40], 'color': '#ddd'}
    #         ],
    #         'threshold': {
    #             'line': {'color': "red", 'width': 4},
    #             'thickness': 0.75,
    #             'value': velocidad_max
    #         }
    #     }
    # ))

    # #fig.show()
    # st.plotly_chart(fig, use_container_width=True)
