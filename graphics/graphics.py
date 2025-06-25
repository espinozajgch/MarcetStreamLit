
import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import matplotlib.pyplot as plt
from utils import util

# Define rangos y colores semáforo por género
SEMAFORO_GRASA = {
    "H": [
        (3, "#FF0000"),   # Rojo
        (6, "#FFA500"),   # Naranja
        (7, "#FFFF00"),   # Amarillo
        (8, "#006400"),   # Verde oscuro
        (10, "#7CFC00"),  # Verde claro
        (14, "#006400"),
        (15, "#FFFF00"),
        (18, "#FFA500"),
        (20, "#FF0000"),
        (25, "#FF0000")
    ],
    "M": [
        (3, "#FF0000"),
        (6, "#FFA500"),
        (7, "#FFFF00"),
        (8, "#006400"),
        (10, "#7CFC00"),
        (14, "#006400"),
        (15, "#FFFF00"),
        (18, "#FFA500"),
        (20, "#FF0000"),
        (25, "#FF0000")
    ]
}

def get_range(gender):
    return SEMAFORO_GRASA.get(gender.upper(), SEMAFORO_GRASA["H"])

def get_color_scale(cmin, cmax, rango_color):
    def norm(valor):
        return round((valor - cmin) / (cmax - cmin), 4)
    
    scale = []
    for valor, color in rango_color:
        escala_norm = norm(valor)
        if 0 <= escala_norm <= 1:
            scale.append([escala_norm, color])
        elif escala_norm < 0:
            scale.append([0, color])
        elif escala_norm > 1:
            scale.append([1, color])
    
    # Asegura el 100% del rango para evitar barras incompletas
    if scale[-1][0] < 1:
        scale.append([1, scale[-1][1]])
    return scale

def calcular_rango_visual(df_grasa, rango_color, margen=1, rango_minimo=5):
    """
    Calcula cmin y cmax ajustados automáticamente según los valores reales y el semáforo.
    
    Args:
        df_grasa: Serie de datos de grasa (%)
        rango_color: Lista de tuplas [(valor, color)]
        margen: Margen extra para cubrir valores extremos.
        rango_minimo: Diferencia mínima entre cmin y cmax para visualización correcta.
    Returns:
        cmin, cmax
    """
    grasa_min = df_grasa.min()
    grasa_max = df_grasa.max()

    semaforo_min = min(valor for valor, _ in rango_color)
    semaforo_max = max(valor for valor, _ in rango_color)

    # Ajustar con margen si los datos reales superan los rangos definidos
    cmin = min(grasa_min - margen, semaforo_min)
    cmax = max(grasa_max + margen, semaforo_max)

    # Asegurar un rango mínimo visible
    if cmax - cmin < rango_minimo:
        delta = (rango_minimo - (cmax - cmin)) / 2
        cmin -= delta
        cmax += delta

    return round(cmin, 2), round(cmax, 2)

def asignar_color_grasa(valor, rango_color):
    if pd.isna(valor):
        return "gray"
    
    for i in range(len(rango_color) - 1):
        v_min, color = rango_color[i]
        v_max, _ = rango_color[i + 1]
        if v_min <= valor < v_max:
            return color
    # Si supera el último rango
    return rango_color[-1][1]

def get_anthropometrics_graph(df_antropometria, categoria, zona_optima_min, zona_optima_max, idioma="es", barras=False):
    df = pd.DataFrame(df_antropometria)
    df["FECHA REGISTRO"] = pd.to_datetime(df["FECHA REGISTRO"], format="%d/%m/%Y")
    df = df.sort_values(by="FECHA REGISTRO")

    metricas = ["PESO (KG)", "GRASA (%)"]
    df = df[["FECHA REGISTRO"] + metricas]

    df_fechas_unicas = df["FECHA REGISTRO"].drop_duplicates().sort_values()
    años_unicos = df_fechas_unicas.dt.year.unique()

    if len(años_unicos) == 1:
        tickvals = df_fechas_unicas
        ticktext = df_fechas_unicas.dt.strftime("%b")
    else:
        tickvals = df_fechas_unicas
        ticktext = df_fechas_unicas.dt.strftime("%b-%Y")

    gender = "H"
    rango_color = get_range(gender)
    cmin, cmax = calcular_rango_visual(df["GRASA (%)"], rango_color)
    colorscale = get_color_scale(cmin, cmax, rango_color)

    #st.text(min(1,(28 - cmin)/(cmax - cmin)))
    color_lineas = {
        "PESO (KG)": "#2989d2",
        "GRASA (%)": "#12527c"
    }

    fig = go.Figure()

    if len(df) == 1:
        new_row = {
            "FECHA REGISTRO": df["FECHA REGISTRO"].iloc[0] + pd.Timedelta(days=5),
            "PESO (KG)": None,
            "GRASA (%)": None
        }
        df = pd.concat([df, pd.DataFrame([new_row])], ignore_index=True)

    # PESO (always as bar)
    if "PESO (KG)" in df.columns:
        size = 20 if len(df) <= 2 else 14

        fig.add_trace(go.Bar(
            x=df["FECHA REGISTRO"],
            y=df["PESO (KG)"],
            name=util.traducir("PESO (KG)", idioma),
            marker_color=color_lineas["PESO (KG)"],
            offsetgroup="peso",
            text=df["PESO (KG)"].apply(lambda x: f"{x:.2f} kg"),
            textposition="inside",
            textfont=dict(size=size),
            yaxis="y1",
            hovertemplate="<b>Fecha:</b> %{x|%d-%m-%Y}<br><b>PESO (KG):</b> %{y:.1f} kg<extra></extra>"
        ))

    # GRASA
    if "GRASA (%)" in df.columns:
        x_vals = df["FECHA REGISTRO"]
        y_vals = df["GRASA (%)"]
        colores_puntos = y_vals.apply(lambda x: asignar_color_grasa(x, rango_color))

        if barras or len(y_vals) == 1:
            #st.text(x_vals)
            size = 20 if len(x_vals) <= 2 else 14
            fig.add_trace(go.Bar(
                x=x_vals,
                y=y_vals,
                name=util.traducir("GRASA (%)", idioma),
                marker_color=colores_puntos,
                offsetgroup="grasa",
                yaxis="y2",
                text=y_vals.apply(lambda x: f"{x:.2f} %"),
                textposition="inside",
                textfont=dict(size=size),
                hovertemplate="<b>Fecha:</b> %{x|%d-%m-%Y}<br><b>GRASA (%):</b> %{y:.1f} %<extra></extra>"
            ))
        else:
            fig.add_trace(go.Scatter(
                x=x_vals,
                y=y_vals,
                mode="lines+markers",
                name=util.traducir("GRASA (%)", idioma),
                line=dict(color="gray", width=3),
                marker=dict(color=colores_puntos, size=10),
                yaxis="y2",
                hovertemplate="<b>Fecha:</b> %{x|%d-%m-%Y}<br><b>GRASA (%):</b> %{y:.2f} %<extra></extra>"
            ))

        df_filtro = df[["FECHA REGISTRO", "GRASA (%)"]].dropna()
        if not df_filtro.empty:
            max_valor = df_filtro["GRASA (%)"].max()
            fila_max = df_filtro[df_filtro["GRASA (%)"] == max_valor].sort_values(by="FECHA REGISTRO", ascending=False).iloc[0]
            text = f"{util.traducir('Max', idioma)}: {fila_max['GRASA (%)']:.2f} %" if not barras else f"{fila_max['GRASA (%)']:.2f} %"

            if not barras:
                fig.add_annotation(
                    x=fila_max["FECHA REGISTRO"],
                    y=fila_max["GRASA (%)"],
                    yref="y2",
                    text=text,
                    showarrow=True,
                    arrowhead=2,
                    ax=0,
                    ay=30,
                    bgcolor="gray",
                    font=dict(size=18, color="white")
                )

            x_min = df["FECHA REGISTRO"].min() - pd.Timedelta(days=20)
            x_max = df["FECHA REGISTRO"].max() + pd.Timedelta(days=15)

            for y_linea, yanchor in [(zona_optima_max, "bottom"), (zona_optima_min, "top")]:
                fig.add_trace(go.Scatter(
                    x=[x_min, x_max],
                    y=[y_linea, y_linea],
                    mode="lines",
                    line=dict(color="green", dash="dash"),
                    yaxis="y2",
                    showlegend=False
                ))
                fig.add_annotation(
                    x=x_max,
                    y=y_linea,
                    yref="y2",
                    text=f"{y_linea} %",
                    showarrow=False,
                    font=dict(size=14, color="black"),
                    xanchor="right",
                    yanchor=yanchor
                )

            fig.add_trace(go.Scatter(
                x=[None], y=[None],
                mode="lines",
                name=f"{util.traducir('ZONA OPTIMA %', idioma)} ({util.traducir('PROMEDIO', idioma)} {util.traducir(categoria.upper(), idioma)} A)".upper(),
                line=dict(color="green", dash="dash"),
                yaxis="y2"
            ))

    # Colorbar lateral
    if "GRASA (%)" in df.columns and not df["GRASA (%)"].isnull().all():
        fig.add_trace(go.Heatmap(
            z=[[0]],
            x=[df["FECHA REGISTRO"].min()],
            y=[(cmin + cmax) / 2],
            zmin=cmin,
            zmax=cmax,
            colorscale=colorscale,
            showscale=True,
            colorbar=dict(
                orientation="v",
                y=-0.02,
                yanchor="bottom",
                len=1.05,
                lenmode="fraction",
                x=1.08,
                xanchor="left",
                thickness=20,
                tickfont=dict(color="white"),
            ),
            hoverinfo="skip"
        ))

    title_layout = "PESO Y % GRASA" if barras else "Evolución del Peso y % Grasa"

    fig.update_layout(
        title=util.traducir(title_layout, idioma).upper(),
        xaxis=dict(
            tickformat="%b",
            dtick="M1",
            tickmode="array",
            tickvals=tickvals,
            ticktext=ticktext,
            showticklabels=not barras
        ),
        yaxis=dict(
            title=util.traducir("PESO (KG)", idioma),
            side="left"
        ),
        yaxis2=dict(
            title=util.traducir("GRASA (%)", idioma),
            overlaying="y",
            side="right",
            showgrid=False,
            dtick=2,
            range=[cmin, cmax],
        ),
        template="plotly_white",
        barmode="group",
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=-0.3,
            xanchor="center",
            x=0.5
        )
    )

    st.plotly_chart(fig, use_container_width=True)
    return fig

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

def get_height_graph(df_altura, idioma="es", barras=False):
    df = pd.DataFrame(df_altura)
    df["FECHA REGISTRO"] = pd.to_datetime(df["FECHA REGISTRO"], format="%d/%m/%Y")
    df = df.sort_values(by="FECHA REGISTRO")

    if "ALTURA (CM)" not in df.columns:
        st.warning("No se encontró la columna 'ALTURA (CM)' en los datos.")
        return None

    fig = go.Figure()

    # Traza principal de altura con burbujas
    fig.add_trace(go.Scatter(
        x=df["FECHA REGISTRO"],
        y=df["ALTURA (CM)"],
        mode="markers+lines",
        name="Altura (cm)",
        marker=dict(
            size=14,
            color="lightblue",
            line=dict(width=2, color="#12527c")
        ),
        line=dict(color="#12527c", width=2),
        hovertemplate="<b>Fecha:</b> %{x|%d-%m-%Y}<br><b>Altura:</b> %{y:.1f} cm<extra></extra>"
    ))

    # Etiquetas personalizadas del eje X
    df_fechas_unicas = df["FECHA REGISTRO"].drop_duplicates().sort_values()
    años_unicos = df_fechas_unicas.dt.year.unique()

    if len(años_unicos) == 1:
        tickvals = df_fechas_unicas
        ticktext = df_fechas_unicas.dt.strftime("%b")
    else:
        tickvals = df_fechas_unicas
        ticktext = df_fechas_unicas.dt.strftime("%b-%Y")

    # Anotación de máximo más reciente
    if not df.empty:
        max_valor = df["ALTURA (CM)"].max()
        fila_max = df[df["ALTURA (CM)"] == max_valor].sort_values(by="FECHA REGISTRO", ascending=False).iloc[0]
        maxl = util.traducir("Max",idioma)
        fig.add_annotation(
            x=fila_max["FECHA REGISTRO"],
            y=fila_max["ALTURA (CM)"],
            text=f"{maxl}: {fila_max['ALTURA (CM)']:.1f} cm",
            showarrow=True,
            arrowhead=2,
            ax=0,
            ay=-30,
            bgcolor="gray",
            font=dict(color="white")
        )

    title_layout = "ALTURA (CM)" if barras else "Evolución de la Altura (cm)"
    fig.update_layout(
        title=util.traducir(title_layout, idioma).upper(),
        xaxis_title=None,
        yaxis_title=util.traducir("ALTURA (CM)", idioma),
        template="plotly_white",
        xaxis=dict(
            tickmode="array",
            tickvals=tickvals,
            ticktext=ticktext,
            showticklabels=not barras
        ),
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=-0.3,
            xanchor="center",
            x=0.5
        )
    )

    st.plotly_chart(fig, use_container_width=True)

    return fig
