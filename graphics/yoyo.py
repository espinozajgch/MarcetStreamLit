import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import matplotlib.pyplot as plt
from utils import util
from utils import traslator

def get_yoyo_graph(df_yoyo, df_promedios_yoyo, categoria, equipo, metrica, columna_fecha_registro, idioma="es", barras=False, cat_label="U19"):
    df = pd.DataFrame(df_yoyo)
    df[columna_fecha_registro] = pd.to_datetime(df[columna_fecha_registro], format="%d/%m/%Y", errors='coerce')
    df = df[[columna_fecha_registro, metrica]].dropna().sort_values(columna_fecha_registro)

    if df.empty or metrica not in df.columns:
        st.warning("No hay datos válidos para mostrar.")
        return

    df["FECHA TEXTO"] = df[columna_fecha_registro].dt.strftime("%b-%Y")
    columna_x = "FECHA TEXTO"

    promedio_row = df_promedios_yoyo[
        (df_promedios_yoyo["CATEGORIA"] == categoria) &
        (df_promedios_yoyo["EQUIPO"] == equipo)
    ]
    valor_prom = promedio_row[metrica].values[0] if not promedio_row.empty and metrica in promedio_row.columns else None

    # === Rangos de semáforo ===
    semaforo_dict = {
        "Juvenil": [
            (3000, "lightgreen"), (2700, "lightgreen"), (2600, "lightgreen"), (2500, "lightgreen"),
            (2400, "lightgreen"), (2300, "lightgreen"), (2200, "lightgreen"), (2100, "lightgreen"),
            (2000, "darkgreen"), (1900, "darkgreen"),
            (1800, "yellow"), (1700, "yellow"),
            (1600, "orange"), (1500, "orange"), (1400, "orange"),
            (1300, "red"), (1200, "red"), (1100, "red"), (1000, "red"), (600, "red")
        ],
        "Cadete": [
            (2500, "lightgreen"), (2400, "lightgreen"), (2300, "lightgreen"), (2200, "lightgreen"),
            (2100, "lightgreen"), (2000, "lightgreen"), (1900, "lightgreen"), (1800, "lightgreen"),
            (1700, "darkgreen"), (1600, "darkgreen"), (1500, "darkgreen"), (1400, "darkgreen"),
            (1300, "yellow"), (1200, "yellow"),
            (1100, "orange"), (1000, "orange"),
            (900, "red"), (800, "red"), (700, "red"), (600, "red")
        ]
    }

    semaforo = semaforo_dict.get(categoria.capitalize(), semaforo_dict["Juvenil"])

    def obtener_color(valor):
        for limite, color in semaforo:
            if valor >= limite:
                return color
        return "red"

    colores = [obtener_color(v) for v in df[metrica]]

    # Rango Y con márgenes dinámicos
    base_min = min([r[0] for r in semaforo])
    base_max = max([r[0] for r in semaforo])
    valores_usuario = df[metrica].tolist() + ([valor_prom] if valor_prom is not None else [])

    margen = 100
    ymin = min(base_min, min(valores_usuario)) - margen
    ymax = max(base_max, max(valores_usuario)) + margen

    # === GRÁFICO ===
    fig = go.Figure()

    if barras:
        ancho_barra = 0.2 if len(df) == 1 else 0.3
        size = 20 if df[metrica].notna().sum() == 1 else 14
        fig.add_trace(go.Bar(
            x=df[columna_x],
            y=df[metrica],
            name=traslator.traducir(metrica, idioma),
            marker_color=colores,
            text=[f"{v:.0f} m" for v in df[metrica]],
            textposition="inside",
            width=ancho_barra,
            textfont=dict(size=size),
            hovertemplate="<b>Fecha:</b> %{x}<br><b>Valor:</b> %{y:.0f} m<extra></extra>"
        ))
    else:
        fig.add_trace(go.Scatter(
            x=df[columna_x],
            y=df[metrica],
            mode="lines+markers",
            name=traslator.traducir(metrica, idioma),
            marker=dict(size=10, color=colores),
            line=dict(color="#1f77b4", width=3),
            hovertemplate="<b>Fecha:</b> %{x}<br><b>Valor:</b> %{y:.0f} m<extra></extra>"
        ))

    if valor_prom is not None:
        fig.add_hline(
            y=valor_prom,
            line=dict(color="green", dash="dash"),
            annotation_text=f"{valor_prom:.0f} m",
            annotation_position="top left",
            annotation=dict(font=dict(color="black", size=14, family="Arial"))
        )
        fig.add_trace(go.Scatter(
            x=[None], y=[None],
            mode="lines",
            name=f"{traslator.traducir('DISTANCIA OPTIMA', idioma)} ({traslator.traducir('PROMEDIO', idioma)} {cat_label})".upper(),
            line=dict(color="green", dash="dash")
        ))

    if len(df) > 1 or not barras:
        fila_max = df.loc[df[metrica].idxmax()]
        fig.add_annotation(
            x=fila_max[columna_x],
            y=fila_max[metrica],
            text=f"Max: {fila_max[metrica]:.0f} m",
            showarrow=True,
            arrowhead=2,
            ax=0,
            ay=-30,
            bgcolor="gray",
            font=dict(color="white")
        )

    # === BARRA LATERAL ===
    valores = sorted(set([v[0] for v in semaforo]))  # sin reverse
    colores_barra = []
    for val in valores:
        for r, color in semaforo:
            if val == r:
                colores_barra.append(color)
                break


    escala_barra = [[i / (len(valores) - 1), colores_barra[i]] for i in range(len(valores))] if len(valores) > 1 else [[0.0, colores_barra[0]], [1.0, colores_barra[0]]]

    fig.add_trace(go.Scatter(
        x=[None], y=[None],
        mode="markers",
        marker=dict(
            size=0,
            color=[(ymin + ymax) / 2],
            colorscale=escala_barra,
            cmin=ymin,
            cmax=ymax,
            colorbar=dict(
                ticks="",
                tickfont=dict(color="white"),
                thickness=20,
                len=1,
                lenmode="fraction",
                y=0,
                yanchor="bottom",
                x=1.05,
                title=None
            ),
            showscale=True
        ),
        showlegend=False,
        hoverinfo="skip"
    ))

    fig.update_layout(
        title=traslator.traducir("Evolución de la Distancia Acumulada", idioma),
        xaxis=dict(
            tickmode="array",
            tickvals=df[columna_x].tolist(),
            ticktext=df[columna_x].tolist(),
            type="category",
            showticklabels=not barras
        ),
        yaxis=dict(
            title=traslator.traducir(metrica, idioma),
            range=[ymin, ymax]
        ),
        template="plotly_white",
        legend=dict(
            orientation="h",
            yanchor="top",
            y=-0.2,
            xanchor="center",
            x=0.5,
            title=""
        )
    )

    st.plotly_chart(fig, use_container_width=True)
    return fig
