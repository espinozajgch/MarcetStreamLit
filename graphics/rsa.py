import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import matplotlib.pyplot as plt
from utils import util

def get_rsa_graph(df_rsa, df_promedios_rsa, categoria, equipo, metricas, columna_fecha_registro, idioma="es", barras=False):
    df = pd.DataFrame(df_rsa)
    df[columna_fecha_registro] = pd.to_datetime(df[columna_fecha_registro], format="%d/%m/%Y")
    df = df.sort_values(by=columna_fecha_registro)

    fechas_unicas = pd.to_datetime(df[columna_fecha_registro].dropna().unique())
    periodos = pd.Series(fechas_unicas).dt.to_period("M").unique()
    fecha_formato = "%d-%b-%Y" if len(periodos) == 1 else "%b-%Y"
    df["FECHA TEXTO"] = df[columna_fecha_registro].dt.strftime(fecha_formato)
    columna_x = "FECHA TEXTO"

    title = util.traducir("TIEMPO (SEG)", idioma)

    promedio_row = df_promedios_rsa[
        (df_promedios_rsa["CATEGORIA"] == categoria) &
        (df_promedios_rsa["EQUIPO"] == equipo)
    ]

    promedios = {}

    if not promedio_row.empty:
        for metrica in metricas:
            if metrica in promedio_row.columns:
                valor = promedio_row[metrica].values[0]
                # Validación robusta: excluye NaN, None, strings vacíos y valores claramente nulos
                if pd.notna(valor) and valor not in ["", None, "null"]:
                    promedios[metrica] = valor

        if not promedios:
            st.warning("No se encontraron promedios para esta categoría y equipo.")
    else:
        st.warning("No se encontraron promedios para esta categoría y equipo.")


    fig_tiempo = go.Figure()

    y_vals = df[metricas[0]].tolist()
    x_vals = df[columna_x].tolist()

    color_linea = "#1f77b4"
    prom = promedios.get(metricas[0], None)
    tolerancia = 1.5
    colores_puntos = []

    for val in y_vals:
        if prom is not None and not pd.isna(prom):
            if val < (prom - tolerancia):
                colores_puntos.append("rgba(0, 200, 0, 0.8)")
            elif abs(val - prom) <= tolerancia:
                colores_puntos.append("rgba(255, 215, 0, 0.9)")
            else:
                colores_puntos.append("rgba(255, 0, 0, 0.8)")
        else:
            colores_puntos.append(color_linea)

    valores = y_vals.copy()
    if prom is not None and not pd.isna(prom):
        valores.append(prom)

    ymin = min(valores) - 1
    ymax = max(valores) + ((max(valores) - min(valores)) * 1)

    tickvals = df[columna_x].tolist()
    ticktext = tickvals

    if barras:
        ancho_barra = 0.2 if len(df) == 1 else 0.3
        size = 20 if len(x_vals) == 1 else 14
        fig_tiempo.add_trace(go.Bar(
            x=x_vals,
            y=y_vals,
            name=title,
            marker_color=colores_puntos,
            text=[f"{v:.2f} seg" for v in y_vals],
            textposition="inside",
            textfont=dict(size=size),
            width=ancho_barra,
            hovertemplate="<b>Fecha:</b> %{x}<br><b>Tiempo:</b> %{y:.2f} seg<extra></extra>"
        ))
    else:
        fig_tiempo.add_trace(go.Scatter(
            x=x_vals,
            y=y_vals,
            mode="lines",
            name=util.traducir("TIEMPO (SEG)", idioma),
            line=dict(color=color_linea, width=3)
        ))

        fig_tiempo.add_trace(go.Scatter(
            x=x_vals,
            y=y_vals,
            mode="markers",
            name="",
            marker=dict(size=10, color=colores_puntos),
            showlegend=False,
            hovertemplate="<b>Fecha:</b> %{x}<br><b>Tiempo:</b> %{y:.2f} seg<extra></extra>"
        ))

    if prom is not None and not pd.isna(prom):
        fig_tiempo.add_hline(
            y=prom,
            line=dict(color="green", dash="dash"),
            annotation_text=f"{prom:.2f} seg",
            annotation_position="top left",
            annotation=dict(font=dict(color="black", size=14))
        )

        promedio = util.traducir("PROMEDIO", idioma)
        categoria = util.traducir(categoria.upper(), idioma)
        tl = util.traducir("TIEMPO OPTIMO", idioma)

        fig_tiempo.add_trace(go.Scatter(
            x=[None], y=[None],
            mode="lines",
            name=f"{tl} ({promedio} {categoria} {equipo})".upper(),
            line=dict(color="green", dash="dash")
        ))

    if len(df) > 1 or not barras:
        df_max = df[df[metricas[0]] == min(y_vals)].sort_values(by=columna_fecha_registro, ascending=False)
        if not df_max.empty:
            maxl = util.traducir("Min", idioma)
            fila = df_max.iloc[0]
            fig_tiempo.add_annotation(
                x=fila[columna_x],
                y=fila[metricas[0]],
                text=f"{maxl}: {fila['MEDIDA EN TIEMPO (SEG)']:.2f} seg",
                showarrow=True,
                arrowhead=2,
                ax=0,
                ay=-30,
                bgcolor="gray",
                font=dict(color="white")
            )

    if prom is not None and not pd.isna(prom):
        rel_promedio = (prom - ymin) / (ymax - ymin)
        colorscale = [
            [0.0, "green"],
            [rel_promedio * 0.7, "yellow"],
            [rel_promedio, "orange"],
            [1.0, "red"]
        ]
    else:
        colorscale = [
            [0.0, "green"],
            [0.5, "yellow"],
            [0.7, "orange"],
            [1.0, "red"]
        ]

    fig_tiempo.add_trace(go.Scatter(
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
                ticks="",
                tickfont=dict(color="white"),
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

    fig_tiempo.update_layout(
        title=util.traducir("Evolución del Tiempo Total en Repeticiones de Sprint", idioma),
        xaxis=dict(
            tickmode="array",
            tickvals=tickvals,
            ticktext=ticktext,
            type="category",
            showticklabels=not barras
        ),
        yaxis=dict(
            title=title,
            range=[ymin, ymax]
        ),
        template="plotly_white",
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=-0.3,
            xanchor="center",
            x=0.5
        )
    )

    st.plotly_chart(fig_tiempo, use_container_width=True)
    return fig_tiempo

def get_rsa_velocity_graph(df_rsa, df_promedios_rsa, categoria, equipo, metric, fecha_registro, idioma="es", barras=False):
    df = df_rsa.copy()
    df[fecha_registro] = pd.to_datetime(df[fecha_registro], format="%d/%m/%Y", errors="coerce")
    df = df.sort_values(by=fecha_registro)

    title = util.traducir("VELOCIDAD (M/S)", idioma)

    promedio_row = df_promedios_rsa[
        (df_promedios_rsa["CATEGORIA"] == categoria) &
        (df_promedios_rsa["EQUIPO"] == equipo)
    ]

    prom = None
    if not promedio_row.empty and metric in promedio_row.columns:
        valor_crudo = promedio_row[metric].values[0]
        if pd.notna(valor_crudo):
            prom = valor_crudo * 3.6
        else:
            st.warning("No se encontraron promedios para esta categoría y equipo.")
    else:
        st.warning("No se encontraron promedios para esta categoría y equipo.")

    tolerancia = 0.3 * 3.6
    color_linea = "#66c2ff"
    color_promedio = "green"

    # Preparar datos
    df_fechas_unicas = df[fecha_registro].drop_duplicates().sort_values()
    periodos = pd.Series(df_fechas_unicas).dt.to_period("M").unique()
    fecha_formato = "%d-%b-%Y" if len(periodos) == 1 else "%b-%Y"
    df["FECHA TEXTO"] = df[fecha_registro].dt.strftime(fecha_formato)
    x_vals = df["FECHA TEXTO"].tolist()
    y_vals = df[metric].tolist()

    colores_puntos = []
    for valor in y_vals:
        if prom is not None and not pd.isna(prom):
            if valor >= prom:
                colores_puntos.append("rgba(0, 200, 0, 0.8)")
            elif abs(valor - prom) <= tolerancia:
                colores_puntos.append("rgba(255, 215, 0, 0.9)")
            else:
                colores_puntos.append("rgba(255, 0, 0, 0.8)")
        else:
            colores_puntos.append(color_linea)

    valores = y_vals.copy()
    if prom is not None and not pd.isna(prom):
        valores.append(prom)
    ymin = min(valores) - 5
    ymax = max(valores) + ((max(valores) - min(valores)) * 0.5)

    fig = go.Figure()

    if barras:
        ancho_barra = 0.2 if len(df) == 1 else 0.3
        size = 20 if len(x_vals) == 1 else 14
        fig.add_trace(go.Bar(
            x=x_vals,
            y=y_vals,
            name=title,
            marker_color=colores_puntos,
            text=[f"{v:.2f} m/s" for v in y_vals],
            textposition="inside",
            textfont=dict(size=size),
            width=ancho_barra,
            hovertemplate="<b>Fecha:</b> %{x}<br><b>Velocidad:</b> %{y:.2f} m/s<extra></extra>"
        ))
    else:
        fig.add_trace(go.Scatter(
            x=x_vals,
            y=y_vals,
            mode="lines",
            name=title,
            line=dict(color=color_linea, width=3),
            showlegend=True
        ))
        fig.add_trace(go.Scatter(
            x=x_vals,
            y=y_vals,
            mode="markers",
            marker=dict(size=10, color=colores_puntos, line=dict(width=0)),
            name=title,
            showlegend=False,
            hovertemplate="<b>Fecha:</b> %{x}<br><b>Velocidad:</b> %{y:.2f} m/s<extra></extra>"
        ))

    if prom is not None and not pd.isna(prom):
        fig.add_hline(
            y=prom,
            line=dict(color=color_promedio, dash="dash"),
            annotation_text=f"{prom:.2f} m/s",
            annotation=dict(font=dict(color="black", size=14))
        )
        promedio = util.traducir("PROMEDIO", idioma)
        categoria_trad = util.traducir(categoria.upper(), idioma)
        vl = util.traducir("VELOCIDAD ÓPTIMA", idioma)
        
        fig.add_trace(go.Scatter(
            x=[None], y=[None],
            mode="lines",
            name=f"{vl} ({promedio} {categoria_trad} {equipo})".upper(),
            line=dict(color=color_promedio, dash="dash")
        ))

    if len(df) > 1 or not barras:
        max_valor = df[metric].max()
        fila_max = df[df[metric] == max_valor].sort_values(fecha_registro, ascending=False).iloc[0]
        maxl = util.traducir("Max", idioma)
        fig.add_annotation(
            x=fila_max["FECHA TEXTO"],
            y=fila_max[metric],
            text=f"{maxl}: {fila_max[metric]:.2f} m/s",
            showarrow=True,
            arrowhead=2,
            ax=0,
            ay=-30,
            bgcolor=color_linea,
            font=dict(color="white")
        )

    # Calcular el punto relativo del promedio para el colorscale
    if prom is not None and not pd.isna(prom):
        rel_prom = (prom - ymin) / (ymax - ymin)
        rel_prom = max(0.0, min(1.0, rel_prom))  # Clamp entre 0 y 1
        colorscale = [
            [0.0, "red"],
            [rel_prom * 0.7, "orange"],
            [rel_prom, "green"],
            [1.0, "green"]
        ]
    else:
        rel_prom = 0.5  # Punto medio si no hay promedio válido
        colorscale = [
            [0.0, "red"],
            [0.5, "orange"],
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
                ticks="",
                tickfont=dict(color="white"),
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
        title=util.traducir("Evolución de la Velocidad en Repeticiones de Sprint", idioma),
        yaxis=dict(title=title, range=[ymin, ymax]),
        xaxis=dict(
            tickmode="array",
            tickvals=x_vals,
            ticktext=x_vals,
            type="category",
            showticklabels=not barras
        ),
        template="plotly_white",
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
