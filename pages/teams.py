
import plotly.express as px
import streamlit as st
from utils import util
from streamlit_gsheets import GSheetsConnection
import pandas as pd
from utils import login
from datetime import date

import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np

conn = st.connection("gsheets", type=GSheetsConnection)

# 🔐 Verificación de sesión
login.generarLogin(conn)
if "usuario" not in st.session_state:
    st.stop()

st.header(" :blue[StatsLab] :material/query_stats:", divider=True)

col1, col2 = st.columns([1, 2])

with col1:
    st.image("https://cdn-icons-png.flaticon.com/512/5281/5281619.png", width=200)
    st.markdown("## **Krzysztof Piątek** 🇵🇱")
    st.markdown("### #19 - AC Milan")
    st.metric(label="Edad", value="28 años")
    st.metric(label="Posición", value="Delantero Centro")
    st.metric(label="Valor de Mercado", value="€30M")

with col2:
    # Evolución del valor de mercado
    market_data = pd.DataFrame({"Fecha": ["2018", "2019", "2020"], "Valor (€M)": [5, 30, 22]})
    fig = px.line(market_data, x="Fecha", y="Valor (€M)", markers=True, title="Evolución del Valor de Mercado")
    st.plotly_chart(fig, use_container_width=True)

# Sección de estadísticas
st.markdown("## 📊 Estadísticas de Temporada")

col3, col4 = st.columns(2)
with col3:
    st.markdown("### 🔥 Goles en la Temporada")
    st.metric(label="Total", value="29")
    st.metric(label="Serie A", value="21")
    st.metric(label="Coppa Italia", value="8")

with col4:
    st.markdown("### 🏆 Máximos Goleadores Serie A")
    goleadores = pd.DataFrame({
        "Jugador": ["Fabio Quagliarella", "Krzysztof Piątek", "Duván Zapata", "Cristiano Ronaldo"],
        "Goles": [21, 21, 20, 19]
    })
    st.dataframe(goleadores, hide_index=True)

# Tabla de Partidos
st.markdown("## 📅 Últimos Partidos")
partidos = pd.DataFrame({
    "Fecha": ["10/03", "05/03", "01/03", "25/02"],
    "Rival": ["Lazio", "Juventus", "Udinese", "Inter"],
    "Resultado": ["1-0 ✅", "1-2 ❌", "1-1 ⚖️", "0-1 ❌"],
    "Minuto Gol": ["83'", "90'", "90'", "-"]
})
st.dataframe(partidos, hide_index=True)

# Cargar los datos (ajustar según los datos reales)
data = {
    'AGILIDAD 505-DOM [SEG]': [5.2, 3.8],
    'AGILIDAD 505-ND [SEG]': [1.631, 1.639],
    'TOTAL 40M [SEG]': [6, 6],
    'TIEMPO 0-5M [SEG]': [2, 2],
    'VEL 0-5M [M/S]': [2, 2],
    'TIEMPO 5-20M [SEG]': [3, 3],
    'VEL 5-20M [M/S]': [2, 2],
    'TIEMPO 20-40M [SEG]': [6, 6],
    'VEL 20-40M [M/S]': [4, 4],
    'CMJ [cm]': [40, 40],
    'CMJ [W]': [880.6, 865.3],
    'TEST': ['ENDURANCE II', 'ENDURANCE II'],
    'SPEED [km/h]': [16, 15.9],
    'ACCUMULATED SHUTTLE DISTANCE [m]': [1950, 1700]
}

# Crear un DataFrame con los datos
df = pd.DataFrame(data)

# Título de la app
st.title("Visualización de Rendimiento Deportivo")

# 4.1 Gráficos de Barras
st.header("4.1 Comparación de Tiempos y Potencia en CMJ")

# Comparación de tiempos en tramos de carrera
st.subheader("Comparación de Tiempos en Tramos de Carrera")
# Los tiempos en tramos de carrera
tiempos_carrera = ['TIEMPO 0-5M [SEG]', 'TIEMPO 5-20M [SEG]', 'TIEMPO 20-40M [SEG]']
tiempos = df[tiempos_carrera].mean()

fig, ax = plt.subplots()
tiempos.plot(kind='bar', ax=ax, color='lightblue')
ax.set_title('Comparación de Tiempos en Tramos de Carrera')
ax.set_xlabel('Tramos de Carrera')
ax.set_ylabel('Tiempo [Segundos]')
st.pyplot(fig)

# Comparación de potencia y rendimiento en CMJ
st.subheader("Comparación de Potencia en CMJ")
fig, ax = plt.subplots()
df[['CMJ [cm]', 'CMJ [W]']].mean().plot(kind='bar', ax=ax, color=['skyblue', 'orange'])
ax.set_title('Comparación de Potencia y Altura en CMJ')
ax.set_ylabel('Valor Promedio')
st.pyplot(fig)

# 4.2 Mapas de Calor
st.header("4.2 Mapas de Calor")

# Mapas de calor para la comparación con la media del equipo
# Suponiendo que tienes un DataFrame con datos de varios jugadores
# Crear un ejemplo ficticio para la comparación de velocidad
df_comparativo = pd.DataFrame({
    'Jugador': ['Jugador 1', 'Jugador 2'],
    'Velocidad Media [km/h]': [16, 15.9],
    'Aceleración Media [m/s^2]': [2.5, 2.6],
    'Potencia Media [W]': [880, 865]
})

# Mapa de calor comparativo entre jugadores
fig = px.imshow(df_comparativo.drop(columns='Jugador').corr(), text_auto=True, errors="ignore")
st.plotly_chart(fig)

# 4.3 Radar Charts
st.header("4.3 Radar Charts")

# Radar chart comparando velocidad, aceleración, fuerza y potencia
# Creando datos de ejemplo para el radar chart
labels = ['Velocidad', 'Aceleración', 'Fuerza', 'Potencia']
valores = [16, 2.5, 50, 880]

# Función para crear el gráfico radar
def radar_chart(labels, values):
    angles = np.linspace(0, 2 * np.pi, len(labels), endpoint=False).tolist()
    values += values[:1]
    angles += angles[:1]

    fig = plt.figure(figsize=(6, 6))
    ax = fig.add_subplot(111, polar=True)
    ax.fill(angles, values, color='orange', alpha=0.25)
    ax.plot(angles, values, color='orange', linewidth=2)

    ax.set_yticklabels([])
    ax.set_xticks(angles[:-1])
    ax.set_xticklabels(labels)
    ax.set_title('Comparación de Atributos Físicos')
    st.pyplot(fig)

radar_chart(labels, valores)

# 4.4 Histogramas y Boxplots
st.header("4.4 Histogramas y Boxplots")

# Histograma de los tiempos en los tramos de carrera
st.subheader("Histograma de los Tiempos en Tramos de Carrera")
fig, ax = plt.subplots()
df[tiempos_carrera].plot(kind='hist', bins=10, alpha=0.5, ax=ax)
ax.set_title('Distribución de Tiempos en Tramos de Carrera')
ax.set_xlabel('Tiempo [Segundos]')
st.pyplot(fig)

# Boxplot de los tiempos de carrera
st.subheader("Boxplot de los Tiempos en los Tramos de Carrera")
fig, ax = plt.subplots()
sns.boxplot(data=df[tiempos_carrera], ax=ax)
ax.set_title('Boxplot de Tiempos en Tramos de Carrera')
st.pyplot(fig)

#################

# Simulación de datos (debes reemplazarlos con los tuyos)
data = {
    "FECHA": ["2024-07-01", "2024-08-01", "2024-09-01"],
    "ALTURA": [1.75, 1.75, 1.75],
    "PESO": [70, 72, 71],
    "MG [KG]": [10, 11, 10.5],
    "GRASA (%)": [15, 14.5, 14]
}

df = pd.DataFrame(data)

# Cálculo de métricas
df["IMC"] = df["PESO"] / (df["ALTURA"] ** 2)
df["Relación Masa Muscular"] = (df["PESO"] - df["MG [KG]"]) / df["PESO"]

# Título de la sección
st.title("📊 Análisis de Composición Corporal")

## 1.1 Cálculo de Índices Claves
st.header("📌 Cálculo de Índices Claves")
st.write("Se analizan métricas clave para evaluar la condición física del jugador.")

st.dataframe(df[["FECHA", "IMC", "GRASA (%)", "Relación Masa Muscular"]])

## 1.2 Comparación con Valores de Referencia
st.header("📊 Comparación con Valores de Referencia")
st.write("Comparamos los valores con estándares de atletas de alto rendimiento.")

# Valores de referencia (Ejemplo: debes ajustarlos según el contexto deportivo)
ref_imc = 22.5  # Promedio recomendado para atletas
ref_grasa = 12  # Porcentaje ideal de grasa para un atleta

# Mostrar comparación
df["IMC - Diferencia"] = df["IMC"] - ref_imc
df["GRASA - Diferencia"] = df["GRASA (%)"] - ref_grasa

st.dataframe(df[["FECHA", "IMC - Diferencia", "GRASA - Diferencia"]])

## 1.3 Tendencias Temporales
st.header("📈 Tendencias Temporales")
st.write("Evolución del peso, masa muscular y porcentaje de grasa en el tiempo.")

# Gráficos de evolución
grafico_peso = px.line(df, x="FECHA", y="PESO", title="Evolución del Peso")
grafico_mg = px.line(df, x="FECHA", y="MG [KG]", title="Evolución de la Masa Grasa")
grafico_grasa = px.line(df, x="FECHA", y="GRASA (%)", title="Evolución del Porcentaje de Grasa")

st.plotly_chart(grafico_peso)
st.plotly_chart(grafico_mg)
st.plotly_chart(grafico_grasa)

# Gráfico combinado con todas las métricas
fig = px.line(df, x="FECHA", y=["PESO", "MG [KG]", "GRASA (%)"], 
            title="Evolución de Peso, Masa Grasa y Porcentaje de Grasa",
            labels={"value": "Medida", "variable": "Métrica"})

# Mostrar gráfico en Streamlit
st.plotly_chart(fig)

############################




# Datos proporcionados (ajustar los datos según sea necesario)
data = {
    'ALTURA': [174.4, 174.1],
    'PESO': [61, 60.4],
    'MG [KG]': [8.5, 6.8],
    'GRASA (%)': [None, 6.8],  # Si tienes los porcentajes de grasa, agrégalo aquí
}

# Crear un DataFrame con los datos
df = pd.DataFrame(data)

# Calcular el IMC
df['IMC'] = df['PESO'] / (df['ALTURA'] / 100) ** 2

# Función para categorizar IMC
def categorizar_imc(imc):
    if imc < 18.5:
        return 'Bajo peso'
    elif 18.5 <= imc < 24.9:
        return 'Normal'
    elif 25 <= imc < 29.9:
        return 'Sobrepeso'
    else:
        return 'Obesidad'

# Función para categorizar el porcentaje de grasa
def categorizar_grasa(porcentaje_grasa):
    if porcentaje_grasa is None:
        return 'No disponible'
    elif porcentaje_grasa < 20:
        return 'Saludable'
    else:
        return 'No saludable'

# Aplicar las funciones de categorización
df['Categoria IMC'] = df['IMC'].apply(categorizar_imc)
df['Categoria Grasa'] = df['GRASA (%)'].apply(categorizar_grasa)

# Título del informe
st.title("Informe de Análisis de Salud de Jugadores")

# Mostrar los datos
st.write("Datos de los Jugadores:")
st.dataframe(df)

# Análisis de IMC
st.header("Análisis de IMC")
imc_distribution = df['Categoria IMC'].value_counts()

# Corregir para evitar el error en plot
fig, ax = plt.subplots()
imc_distribution.plot(kind='bar', ax=ax, color='skyblue')
ax.set_title('Distribución de Jugadores según IMC')
ax.set_xlabel('Categoría IMC')
ax.set_ylabel('Número de Jugadores')
st.pyplot(fig)

# Análisis de porcentaje de grasa corporal
st.header("Análisis de Porcentaje de Grasa Corporal")
grasa_distribution = df['Categoria Grasa'].value_counts()

# Corregir para evitar el error en plot
fig, ax = plt.subplots()
grasa_distribution.plot(kind='bar', ax=ax, color='lightgreen')
ax.set_title('Distribución de Jugadores según Porcentaje de Grasa Corporal')
ax.set_xlabel('Categoría Grasa Corporal')
ax.set_ylabel('Número de Jugadores')
st.pyplot(fig)

