
import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

def get_anthropometrics_graph(df_anthropometrics):
    # Crear DataFrame y convertir la fecha
    df = pd.DataFrame(df_anthropometrics)
    #df["FECHA REGISTRO"] = pd.to_datetime(df["FECHA REGISTRO"], format="%d/%m/%Y")
    #df = df.sort_values(by="FECHA REGISTRO")  # Ordenar cronológicamente

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
                    "MG [KG]: %{customdata[2]} <br>" +
                    "Grasa: %{customdata[3]} %",
        customdata=df[["ALTURA", "PESO", "MG [KG]" ,"GRASA (%)"]].values,
        text=df[df.columns[1:]].round(2)  # Asegura que los valores del tooltip estén redondeados a 2 decimales
    )

    # Mostrar en Streamlit
    st.plotly_chart(fig)

def get_agilty_graph(df_agilty):
    # Crear DataFrame con los datos proporcionados (aquí debes usar tu propio df_agility)
    df = pd.DataFrame(df_agilty)
    df["FECHA REGISTRO"] = pd.to_datetime(df["FECHA REGISTRO"], format="%d/%m/%Y")

    # Convertir la fecha a formato de mes y año y convertirlo a cadena
    df["Mes-Año"] = df["FECHA REGISTRO"].dt.strftime('%Y-%m')

    # Agrupar los datos por mes (promediar valores por mes)
    df_monthly = df.groupby('Mes-Año').agg({
        '505-DOM [SEG]': 'mean',
        '505-ND [SEG]': 'mean'
    }).reset_index()

    # Transformar el DataFrame a formato largo
    df_melted = df_monthly.melt(id_vars=["Mes-Año"], var_name="MÉTRICA", value_name="VALOR")

    # Crear gráfico de barras comparativas por mes
    fig = px.bar(df_melted, 
                x="Mes-Año", 
                y="VALOR", 
                color="MÉTRICA", 
                title="📈 Comparación de Medidas de Agilidad (Promedio) por Mes",
                barmode="group")

    # Personalizar el tooltip
    fig.update_traces(hovertemplate=
                    '<b>Mes:</b> %{x}<br>'
                    '<b>Métrica:</b> %{customdata[0]}<br>'
                    '<b>Valor:</b> %{y:.2f}<extra></extra>',
                    customdata=df_melted[['MÉTRICA']].values)

    # Mostrar el gráfico en Streamlit
    st.plotly_chart(fig)

def get_cmj_graph(df_cmj):
    # Convertir la columna de fecha a formato datetime
    df = pd.DataFrame(df_cmj)
    df["FECHA REGISTRO"] = pd.to_datetime(df["FECHA REGISTRO"], format="%d/%m/%Y")

    # Ordenar las fechas en orden ascendente
    #df = df.sort_values("FECHA REGISTRO")

    # Convertir el DataFrame a formato largo para Plotly
    df_melted = df.melt(id_vars=["FECHA REGISTRO"], var_name="MÉTRICA", value_name="VALOR")

    # Formatear la fecha para mejor visualización en el gráfico
    df_melted["FECHA REGISTRO"] = df_melted["FECHA REGISTRO"].dt.strftime("%b-%Y")  # Ejemplo: "Sep-2025"

    # Título en Streamlit
    #st.title("📊 Evolución del CMJ en el Tiempo")

    # Crear gráfico interactivo con Plotly
    fig = px.line(df_melted, 
                x="FECHA REGISTRO", 
                y="VALOR", 
                color="MÉTRICA", 
                markers=True, 
                title="📈 Evolución de CMJ (cm) y CMJ (W) a lo largo del tiempo",
                labels={"VALOR": "VALOR", "MÉTRICA": "MÉTRICA", "FECHA REGISTRO": "FECHA REGISTRO"},
                template="plotly_white")

    # Personalizar el tooltip
    fig.update_traces(hovertemplate='<b>Fecha:</b> %{x}<br><b>Métrica:</b> %{customdata[0]}<br><b>Valor:</b> %{y:.2f}',
                    customdata=df_melted[['MÉTRICA']].values)

    # Mostrar el gráfico en Streamlit
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
                title=f"📈 COMPARACIÓN DE SPEED [km/h] y ACCUMULATED SHUTTLE DISTANCE [m] - {selected_test}",
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
