
import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import matplotlib.pyplot as plt
from utils import util

def get_anthropometrics_graph(df_anthropometrics):
    # Crear DataFrame y convertir la fecha
    df = pd.DataFrame(df_anthropometrics)
    df["FECHA REGISTRO"] = pd.to_datetime(df["FECHA REGISTRO"], format="%d/%m/%Y")
    df = df.sort_values(by="FECHA REGISTRO")  # Ordenar cronológicamente
    df["FECHA REGISTRO"] = df["FECHA REGISTRO"].dt.strftime('%d/%m/%Y').astype(str)
    
    # Crear gráfico interactivo
    fig = px.line(df, x="FECHA REGISTRO", y=df.columns[1:], 
                    title="📈 Evolución de las Medidas Antropometricas", markers=True)

    fig.update_layout(
        yaxis_title="VALOR"  # Cambia el nombre aquí
    )

    fig.update_traces(
        hovertemplate="<b>Fecha: %{x}</b><br>" +
                    "Altura: %{customdata[0]} cm<br>" + 
                    "Peso: %{customdata[1]} kg<br>" +
                    "Grasa: %{customdata[3]} %",
        customdata=df[["ALTURA (CM)", "PESO (KG)" ,"GRASA (%)"]].values,
        text=df[df.columns[1:]].round(2)  # Asegura que los valores del tooltip estén redondeados a 2 decimales
    )

    # Mostrar en Streamlit
    st.plotly_chart(fig)

import streamlit as st
import pandas as pd
import plotly.express as px

def get_agilty_graph(df_agilty):
    df = pd.DataFrame(df_agilty)
    
    # Asegurar formato datetime
    df["FECHA REGISTRO"] = pd.to_datetime(df["FECHA REGISTRO"], format="%d/%m/%Y", errors='coerce')

    # Crear columna 'Mes-Año' como string legible
    df["Mes-Año"] = df["FECHA REGISTRO"].dt.strftime('%B %Y')  # Ej: 'abril 2025'
    
    # Para asegurar orden cronológico, guardamos también un índice auxiliar de fecha
    df["MesIndex"] = df["FECHA REGISTRO"].dt.to_period("M")

    # Agrupar por MesIndex (periodo) para ordenar bien, luego recuperar 'Mes-Año'
    df_monthly = df.groupby("MesIndex").agg({
        '505-DOM (SEG)': 'mean',
        '505-ND (SEG)': 'mean',
        'Mes-Año': 'first'  # para conservar el nombre legible
    }).reset_index(drop=True)

    # Transformar a formato largo
    df_melted = df_monthly.melt(id_vars=["Mes-Año"], var_name="MÉTRICA", value_name="VALOR")
    
    # Crear gráfico de barras
    fig = px.bar(df_melted, 
                x="Mes-Año", 
                y="VALOR", 
                color="MÉTRICA", 
                title="📈 Comparación de Medidas de Agilidad (Promedio) por Mes",
                barmode="group")
    
    # Tooltips personalizados
    fig.update_traces(hovertemplate=
        '<b>Mes:</b> %{x}<br>'
        '<b>Métrica:</b> %{customdata[0]}<br>'
        '<b>Valor:</b> %{y:.2f}<extra></extra>',
        customdata=df_melted[['MÉTRICA']].values)

    # Eje X como categorías (evita orden alfabético)
    fig.update_xaxes(type='category')

    # Mostrar en Streamlit
    st.plotly_chart(fig)


def get_cmj_graph(df_cmj):
    df = pd.DataFrame(df_cmj)
    df["FECHA REGISTRO"] = pd.to_datetime(df["FECHA REGISTRO"], format="%d/%m/%Y")
    df = df.sort_values(by="FECHA REGISTRO", ascending=True)
    
    # Filtrar columnas numéricas
    metricas = df.select_dtypes(include=["number"]).columns.tolist()

    # Convertir a formato largo para Plotly
    df_melted = df.melt(id_vars=["FECHA REGISTRO"], value_vars=metricas,
                        var_name="MÉTRICA", value_name="VALOR")

    # Eliminar filas vacías
    df_melted = df_melted.dropna(subset=["VALOR"])

    # Formatear la fecha
    df_melted["FECHA REGISTRO"] = df_melted["FECHA REGISTRO"].dt.strftime("%d-%m-%Y")
    #df["FECHA REGISTRO"] = df["FECHA REGISTRO"].dt.strftime('%d/%m/%Y').astype(str)
    # Crear gráfico
    fig = px.line(df_melted,
                  x="FECHA REGISTRO",
                  y="VALOR",
                  color="MÉTRICA",
                  markers=True,
                  title="📈 Evolución de CMJ a lo largo del tiempo",
                  labels={"VALOR": "VALOR", "MÉTRICA": "MÉTRICA", "FECHA REGISTRO": "FECHA"},
                  template="plotly_white")

    fig.update_traces(
        hovertemplate='<b>Fecha:</b> %{x}<br><b>Métrica:</b> %{customdata[0]}<br><b>Valor:</b> %{y:.2f}',
        customdata=df_melted[['MÉTRICA']].values
    )

    # Mostrar en Streamlit
    st.subheader("📊 Evolución del CMJ")
    st.plotly_chart(fig, use_container_width=True)


def get_rsa_graph(df_rsa):

    df = pd.DataFrame(df_rsa)
    #df['FECHA REGISTRO'] = pd.to_datetime(df['FECHA REGISTRO'])

    # Crear el gráfico de líneas con dos ejes Y
    fig = go.Figure()

    # Añadir la primera línea para "MEDIDA EN TIEMPO (SEG)"
    fig.add_trace(go.Scatter(x=df['FECHA REGISTRO'], 
                            y=df['MEDIDA EN TIEMPO (SEG)'], 
                            mode='lines+markers', 
                            name='Medida en Tiempo (seg)',
                            line=dict(color='blue'),
                            hovertemplate="<b>Fecha:</b> %{x|%d-%m-%Y}<br>"
                      "<b>Tiempo:</b> %{y:.2f} seg"))

    # Añadir la segunda línea para "VELOCIDAD (M*SEG)"
    fig.add_trace(go.Scatter(x=df['FECHA REGISTRO'], 
                            y=df['VELOCIDAD (M*SEG)'], 
                            mode='lines+markers', 
                            name='Velocidad (m*seg)',
                            line=dict(color='red'),
                            yaxis='y2',
                            hovertemplate="<b>Fecha:</b> %{x|%d-%m-%Y}<br>"
                      "<b>Velocidad:</b> %{y:.2f} m/s"))

    # Crear el segundo eje Y
    fig.update_layout(
        title="📈 RSA: Medida en Tiempo y Velocidad por Fecha",
        xaxis_title="FECHA REGISTRO",
        yaxis_title="MEDIDA EN TIEMPO (SEG)",
        yaxis2=dict(
            title="Velocidad (m*seg)",
            overlaying="y",
            side="right"
        ),
        legend_title="Métricas",
        template="plotly_white"
    )

    # Mostrar el gráfico en Streamlit
    st.plotly_chart(fig)

def get_yoyo_graph(df_yoyo):
    col1, col2 = st.columns([1,3])

    with col1:
        # Selector de Tipo de Test
        test_type_list = df_yoyo["TEST"].unique()
        test_type_list.sort()
        selected_test = st.selectbox("Selecciona el tipo de test:", test_type_list)

    # Convertir FECHA REGISTRO a tipo fecha
    df = pd.DataFrame(df_yoyo)
    #df["FECHA REGISTRO"] = pd.to_datetime(df["FECHA REGISTRO"], format="%d/%m/%Y")

    # Transformar el DataFrame a formato largo para graficar ambas métricas
    df_melted = df.melt(id_vars=["FECHA REGISTRO", "TEST"], var_name="MÉTRICA", value_name="VALOR")

    # Título en Streamlit
    #st.title("📊 Evolución de Velocidad y Distancia en el Test Yo-Yo")

    # Filtrar por tipo de test seleccionado
    df_filtered = df_melted[df_melted["TEST"] == selected_test]

    # Gráfico de líneas con ambas métricas filtradas por test
    fig = px.line(df_filtered, x="FECHA REGISTRO", y="VALOR", color="MÉTRICA",
                title=f"📈 COMPARACIÓN DE SPEED (KM/H) y ACCUMULATED SHUTTLE DISTANCE (M) - {selected_test}",
                markers=True, template="plotly_white",
                labels={"FECHA REGISTRO": "FECHA REGISTRO", "VALOR": "VALOR", "MÉTRICA": "MÉTRICA"})

    # Ajustar la leyenda en la parte superior
    fig.update_layout(
        legend=dict(
            orientation="h",  # Leyenda horizontal
            yanchor="top",  # Anclaje en la parte inferior de la leyenda
            y=-0.2,  # Posiciona la leyenda arriba del gráfico
            xanchor="center",  # Anclaje al centro horizontal
            x=0.5  # Centra la leyenda horizontalmente
        )
    )

    # Personalizar el tooltip
    fig.update_traces(hovertemplate='<b>Fecha:</b> %{x}<br><b>Métrica:</b> %{customdata[0]}<br><b>Valor:</b> %{y:.2f}',
                    customdata=df_melted[['MÉTRICA']].values)

    # Mostrar gráfico en Streamlit
    st.plotly_chart(fig, use_container_width=True)

def generar_tabla_imc_personalizada(categoria_jugador, path="tabla_imc_personalizada.png"):
    rangos = ["MENOR A 18.49", "18.50 A 24.99", "25 A 29.99", "30 A 34.99", "35 A 39.99", "MAYOR A 40"]
    clasificaciones = ["PESO BAJO", "PESO NORMAL", "SOBREPESO", "OBESIDAD LEVE", "OBESIDAD MEDIA", "OBESIDAD MÓRBIDA"]
    colores = ["#f28e2b", "#4db6ac", "#bc5090", "#ef553b", "#00cc96", "#f4a261"]

    fig, ax = plt.subplots(figsize=(6, 4))
    ax.axis('off')
    table_data = list(zip(rangos, clasificaciones))

    tabla = ax.table(cellText=table_data,
                     colLabels=["ÍNDICE DE MASA CORPORAL (IMC)", "CLASIFICACIÓN"],
                     cellLoc='center',
                     colLoc='center',
                     loc='center')

    tabla.auto_set_font_size(False)
    tabla.set_fontsize(10)
    tabla.scale(1.2, 1.5)

    for i, clasificacion in enumerate(clasificaciones):
        tabla[(i+1, 0)].set_facecolor(colores[i])
        tabla[(i+1, 0)].set_text_props(color='white', weight='bold')
        tabla[(i+1, 1)].set_text_props(weight='bold')

        # Marcar la fila correspondiente al jugador
        if categoria_jugador.upper() in clasificacion.upper():
            tabla[(i+1, 1)].set_facecolor('#34eb3a')  # Amarillo claro
            tabla[(i+1, 1)].set_text_props(color='black')

    # Encabezado
    tabla[(0, 0)].set_facecolor('#263238')
    tabla[(0, 1)].set_facecolor('#263238')
    tabla[(0, 0)].set_text_props(color='white', weight='bold')
    tabla[(0, 1)].set_text_props(color='white', weight='bold')

    #fig.text(0.5, 0.01, "Clasificación oficial del IMC según la OMS", ha='center', fontsize=9, style='italic')

    #plt.tight_layout()
    #plt.savefig(path, dpi=300, bbox_inches='tight')
    #plt.close()
    st.pyplot(fig, use_container_width=True)

import matplotlib.pyplot as plt

def mostrar_grafico_percentiles(percentiles):
    fig, ax = plt.subplots()
    labels = list(percentiles.keys())
    valores = list(percentiles.values())

    ax.barh(labels, valores, color="skyblue")
    ax.set_xlim(0, 100)
    ax.axvline(50, color="gray", linestyle="--", label="Percentil 50 (Promedio)")
    ax.set_xlabel("Percentil")
    ax.set_title("Comparativa por Percentil del Jugador")
    ax.legend()
    st.pyplot(fig)


def mostrar_percentiles_coloreados(jugador: dict, percentiles: dict):
    data = []
    for metrica, p in percentiles.items():
        valor = jugador.get(metrica, "-")
        interpretacion = util.interpretar_percentil(p)  # tu función para texto amigable
        data.append({
            "MÉTRICA": metrica,
            "VALOR": valor,
            "PERCENTIL": round(p, 1),
            "INTERPRETACIÓN": interpretacion
        })

    df = pd.DataFrame(data)

    # Aplicar estilos visuales
    #styled_df = df.style.apply(color_fila, axis=1)

    st.dataframe(df)
