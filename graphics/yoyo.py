import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import matplotlib.pyplot as plt
from utils import util

def get_yoyo_graph(df_yoyo, df_promedios_yoyo, categoria, equipo, metrica, columna_fecha_registro, idioma="es", barras=False):

    df = pd.DataFrame(df_yoyo)
    df[columna_fecha_registro] = pd.to_datetime(df[columna_fecha_registro], format="%d/%m/%Y", errors='coerce')
    df = df[[columna_fecha_registro, metrica]].dropna().sort_values(columna_fecha_registro)

    if df.empty or metrica not in df.columns:
        st.warning("No hay datos válidos para mostrar.")
        return

    # Determinar formato de fecha dinámico
    fechas_unicas = pd.to_datetime(df[columna_fecha_registro].dropna().unique())
    periodos = pd.Series(fechas_unicas).dt.to_period("M").unique()
    fecha_formato = "%d-%b-%Y" if len(periodos) == 1 else "%b-%Y"

    df["FECHA TEXTO"] = df[columna_fecha_registro].dt.strftime(fecha_formato)
    columna_x = "FECHA TEXTO"

    # Obtener promedio
    promedio_row = df_promedios_yoyo[(df_promedios_yoyo["CATEGORIA"] == categoria) & (df_promedios_yoyo["EQUIPO"] == equipo)]
    valor_prom = promedio_row[metrica].values[0] if not promedio_row.empty and metrica in promedio_row.columns else None

    # Calcular rango del eje Y
    valores = df[metrica].tolist() + ([valor_prom] if valor_prom is not None and not pd.isna(valor_prom) else [])
    ymin = min(valores) - 300
    ymax = max(valores) + (max(valores) - min(valores)) * 0.5

    # Etiquetas eje X
    tickvals = df[columna_x].tolist()
    ticktext = tickvals

    # Colorear puntos/barras
    colores = []
    for valor in df[metrica]:
        if valor_prom is not None and not pd.isna(valor_prom):
            if valor >= valor_prom:
                colores.append("rgba(0, 200, 0, 0.8)")
            elif abs(valor - valor_prom) <= 5:
                colores.append("rgba(255, 215, 0, 0.9)")
            else:
                colores.append("rgba(255, 0, 0, 0.8)")
        else:
            colores.append("gray")

    fig = go.Figure()

    if barras:
        ancho_barra = 0.1 if len(df) == 1 else 0.3
        fig.add_trace(go.Bar(
            x=df[columna_x],
            y=df[metrica],
            name=util.traducir(metrica, idioma),
            marker_color=colores,
            text=[f"{v:.2f}" for v in df[metrica]],
            textposition="inside",
            width=ancho_barra,
            hovertemplate=f"<b>Fecha:</b> %{{x}}<br><b>Valor:</b> %{{y:.2f}}<extra></extra>"
        ))
    else:
        fig.add_trace(go.Scatter(
            x=df[columna_x],
            y=df[metrica],
            mode="lines+markers",
            name=util.traducir(metrica, idioma),
            marker=dict(size=10, color=colores),
            line=dict(color="#1f77b4", width=3),
            hovertemplate=f"<b>Fecha:</b> %{{x}}<br><b>Valor:</b> %{{y:.2f}}<extra></extra>"
        ))

    if valor_prom is not None and not pd.isna(valor_prom):
        fig.add_hline(
            y=valor_prom,
            line=dict(color="green", dash="dash"),
            annotation_text=f"{valor_prom:.2f} m",
            annotation_position="top left",
            annotation=dict(font=dict(color="black", size=12, family="Arial"))
        )
        fig.add_trace(go.Scatter(
            x=[None], y=[None],
            mode="lines",
            name=f"{util.traducir('DISTANCIA ACUMULADA (M)', idioma)} {util.traducir('PROMEDIO', idioma)} ({util.traducir(categoria.upper(), idioma)} {equipo})",
            line=dict(color="green", dash="dash")
        ))

    if len(df) > 1:
        max_val = df[metrica].max()
        fila_max = df[df[metrica] == max_val].sort_values(columna_fecha_registro, ascending=False).iloc[0]
        maxl = util.traducir("Max", idioma)
        fig.add_annotation(
            x=fila_max[columna_x],
            y=fila_max[metrica],
            text=f"{maxl}: {fila_max[metrica]:.0f} (M)",
            showarrow=True,
            arrowhead=2,
            ax=0,
            ay=-30,
            bgcolor="#1f77b4",
            font=dict(color="white")
        )

    rel_prom = (valor_prom - ymin) / (ymax - ymin) if valor_prom is not None else 0.5
    colorscale = [
        [0.0, "red"],
        [max(rel_prom * 0.7, 0.001), "orange"],
        [rel_prom, "green"],
        [1.0, "green"]
    ]

    fig.add_trace(go.Scatter(
        x=[None],
        y=[None],
        mode="markers",
        marker=dict(
            size=0,
            color=[(ymin + ymax) / 2],
            colorscale=colorscale,
            cmin=ymin,
            cmax=ymax,
            colorbar=dict(
                ticks="outside",
                tickfont=dict(color="black"),
                thickness=20,
                len=1,
                lenmode="fraction",
                y=0,
                yanchor="bottom",
                x=1.05
            ),
            showscale=True
        ),
        showlegend=False,
        hoverinfo="skip"
    ))

    fig.update_layout(
        title=util.traducir("Evolución de la Distancia Acumulada", idioma),
        xaxis=dict(
            tickmode="array",
            tickvals=tickvals,
            ticktext=ticktext,
            type="category"
        ),
        yaxis=dict(
            title=util.traducir(metrica, idioma),
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
