import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import matplotlib.pyplot as plt
from utils import util

def get_sprint_graph(
    df_sprint,
    df_promedios,
    categoria,
    equipo,
    metrica_tiempo,
    metrica_velocidad,
    columnas_fecha_registro,
    idioma="es",
    barras=False
):
    df = df_sprint.copy()
    df[columnas_fecha_registro] = pd.to_datetime(df[columnas_fecha_registro], format="%d/%m/%Y", errors='coerce')
    df = df.sort_values(by=columnas_fecha_registro)

    fechas_unicas = df[columnas_fecha_registro].dropna().drop_duplicates().sort_values()
    periodos = fechas_unicas.dt.to_period("M").unique()
    formato_fecha = "%b-%d-%Y" if len(periodos) == 1 else "%b-%Y"
    df["FECHA TEXTO"] = df[columnas_fecha_registro].dt.strftime(formato_fecha)
    columna_x = "FECHA TEXTO" if barras else columnas_fecha_registro

    tickvals = df["FECHA TEXTO"].unique().tolist() if barras else fechas_unicas
    ticktext = tickvals if barras else fechas_unicas.dt.strftime(formato_fecha).tolist()

    color_linea = "#66c2ff"
    color_promedio = "green"

    fig = go.Figure()

    # === VELOCIDAD ===
    cols_vel = [columnas_fecha_registro, metrica_velocidad]
    if columnas_fecha_registro != columna_x:
        cols_vel.insert(1, columna_x)
    df_metric_vel = df[cols_vel].dropna()

    if not df_metric_vel.empty:
        if barras or len(df_metric_vel[metrica_velocidad]) == 1:
            size = 20 if df_metric_vel[metrica_velocidad].notna().sum() == 1 else 14
            fig.add_trace(go.Bar(
                x=df_metric_vel[columna_x],
                y=df_metric_vel[metrica_velocidad],
                name=util.traducir(metrica_velocidad, idioma),
                marker_color=color_linea,
                offsetgroup="velocidad",
                yaxis="y2",
                text=df_metric_vel[metrica_velocidad].apply(lambda x: f"{x:.2f} m/s"),
                textposition="inside",
                textfont=dict(size=size),
                hovertemplate=f"<b>Fecha:</b> %{{x}}<br><b>{util.traducir(metrica_velocidad, idioma)}:</b> %{{y:.2f}} m/s<extra></extra>"
            ))
        else:
            fig.add_trace(go.Scatter(
                x=df_metric_vel[columna_x],
                y=df_metric_vel[metrica_velocidad],
                mode="lines+markers",
                name=util.traducir(metrica_velocidad, idioma),
                marker=dict(color=color_linea, size=10),
                yaxis="y2",
                hovertemplate=f"<b>Fecha:</b> %{{x}}<br><b>{util.traducir(metrica_velocidad, idioma)}:</b> %{{y:.2f}} m/s<extra></extra>"
            ))

        #if not barras:
        if not barras and len(df_metric_vel) > 1:
        #if len(df_metric_vel) > 1 or not barras:
            fila_max = df_metric_vel[df_metric_vel[metrica_velocidad] == df_metric_vel[metrica_velocidad].max()].iloc[0]
            fig.add_annotation(
                x=fila_max[columna_x],
                y=fila_max[metrica_velocidad],
                yref="y2",
                text=f"{util.traducir('Max', idioma)}: {fila_max[metrica_velocidad]:.2f} m/s",
                showarrow=True,
                arrowhead=2,
                ax=0 if barras else -60,
                ay=-40,
                xshift=-20 if barras else 0,
                bgcolor="gray",
                font=dict(color="white")
            )

    # === TIEMPO ===
    promedio_row = df_promedios[
        (df_promedios["CATEGORIA"] == categoria) &
        (df_promedios["EQUIPO"] == equipo)
    ]
    prom_tiempo = promedio_row[metrica_tiempo].values[0] if not promedio_row.empty and metrica_tiempo in promedio_row.columns else None
    prom_tiempo = prom_tiempo if pd.notna(prom_tiempo) else None

    cols_time = [columnas_fecha_registro, metrica_tiempo]
    if columnas_fecha_registro != columna_x:
        cols_time.insert(1, columna_x)
    df_metric_time = df[cols_time].dropna()

    if not df_metric_time.empty:
        tiempo_min = df_metric_time[metrica_tiempo].min()
        tiempo_max = df_metric_time[metrica_tiempo].max()

        # Rango por categoría
        rango_categoria = {
            "Juvenil": (4.4, 6.3),
            "Cadete": (4.6, 6.5)
        }
        base_min, base_max = rango_categoria.get(categoria.capitalize(), (4.4, 6.3))

        y_min = min(base_min, tiempo_min)
        y_max = max(base_max, tiempo_max)
        margen = (y_max - y_min) * 0.5
        y_min -= margen
        y_max += margen

        escala_colores = [
            [0.0, "lightgreen"], [0.35, "green"], [0.55, "#FFD700"], [0.75, "#FFA500"], [1.0, "#FF4500"]
        ] if categoria.lower() in ["juvenil", "cadete"] else [
            [0.0, "lightgreen"], [0.25, "green"], [0.5, "yellow"], [0.75, "orange"], [1.0, "red"]
        ]

        #if barras:
        size = 20 if df_metric_time[metrica_tiempo].notna().sum() == 1 else 14
        fig.add_trace(go.Bar(
            x=df_metric_time[columna_x],
            y=df_metric_time[metrica_tiempo],
            name=util.traducir(metrica_tiempo, idioma),
            marker=dict(
                color=df_metric_time[metrica_tiempo],
                colorscale=escala_colores,
                cmin=y_min,
                cmax=y_max
            ),
            offsetgroup="tiempo",
            yaxis="y1",
            text=df_metric_time[metrica_tiempo].apply(lambda x: f"{x:.2f} seg"),
            #text=df_metric_time[metrica_tiempo].round(2),
            textposition="inside",
            textfont=dict(size=size),
            hovertemplate=f"<b>Fecha:</b> %{{x}}<br><b>{util.traducir(metrica_tiempo, idioma)}:</b> %{{y:.2f}} seg<extra></extra>"
        ))
        # else:
        #     fig.add_trace(go.Scatter(
        #         x=df_metric_time[columna_x],
        #         y=df_metric_time[metrica_tiempo],
        #         mode="markers+lines",
        #         name=util.traducir(metrica_tiempo, idioma),
        #         marker=dict(
        #             size=10,
        #             color=df_metric_time[metrica_tiempo],
        #             colorscale=escala_colores,
        #             cmin=y_min,
        #             cmax=y_max
        #         ),
        #         line=dict(color="gray", width=2),
        #         yaxis="y1",
        #         hovertemplate=f"<b>Fecha:</b> %{{x}}<br><b>{util.traducir(metrica_tiempo, idioma)}:</b> %{{y:.2f}} seg<extra></extra>"
        #     ))

        if not barras and len(df_metric_time) > 1:
            fila_min = df_metric_time[df_metric_time[metrica_tiempo] == df_metric_time[metrica_tiempo].min()].iloc[0]
            fig.add_annotation(
                x=fila_min[columna_x],
                y=fila_min[metrica_tiempo],
                yref="y1",
                text=f"{util.traducir('Min', idioma)}: {fila_min[metrica_tiempo]:.2f} seg",
                showarrow=True,
                arrowhead=2,
                ax=0,
                ay=-40,
                xshift=20 if barras else 0,
                bgcolor="gray",
                font=dict(color="white")
            )

        if prom_tiempo is not None:
            fig.add_hline(
                y=prom_tiempo,
                line=dict(color=color_promedio, dash="dash", width=2),
                annotation_text=f"{prom_tiempo:.2f} seg",
                annotation_position="top right",
                annotation=dict(font=dict(color="black", size=14)),
                layer="above"
            )
            fig.add_trace(go.Scatter(
                x=[None], y=[None],
                mode="lines",
                name=f"{util.traducir('TIEMPO OPTIMO', idioma)} ({util.traducir('PROMEDIO', idioma)} {util.traducir(categoria.upper(), idioma)} {equipo})".upper(),
                line=dict(color=color_promedio, dash="dash", width=2),
                showlegend=True
            ))

        # Barra lateral de color
        fig.add_trace(go.Scatter(
            x=[None], y=[None],
            mode="markers",
            marker=dict(
                size=0,
                color=[prom_tiempo if prom_tiempo is not None else y_min],
                colorscale=escala_colores,
                cmin=y_min,
                cmax=y_max,
                colorbar=dict(
                    title="",
                    ticks="",
                    tickfont=dict(color="white"),
                    thickness=20,
                    len=1,
                    lenmode="fraction",
                    y=0,
                    yanchor="bottom",
                    x=1.12 if barras else -0.19,
                    xanchor="right" if barras else "left"
                ),
                showscale=True
            ),
            showlegend=False,
            hoverinfo="skip"
        ))

        fig.update_layout(yaxis=dict(range=[y_min, y_max]))

    # === Layout final ===
    title_layout = "SPRINT" if barras else "Evolución del Sprint"
    fig.update_layout(
        title=f"{util.traducir(title_layout, idioma).upper()} ({util.traducir(metrica_tiempo, idioma)} y {util.traducir(metrica_velocidad, idioma)})",
        xaxis=dict(
            tickmode="array",
            tickvals=tickvals,
            ticktext=ticktext,
            type="category" if barras else "date",
            showticklabels=not barras
        ),
        yaxis=dict(
            title=util.traducir("TIEMPO (SEG)", idioma),
            side="left" if not barras else "right",
            showgrid=True
        ),
        yaxis2=dict(
            title=util.traducir("VELOCIDAD (M/S)", idioma),
            overlaying="y",
            side="right" if not barras else "left",
            showgrid=False
        ),
        template="plotly_white",
        barmode="group" if barras else "overlay",
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


def get_sprint_graph_vt(
    df_sprint,
    df_promedios,
    categoria,
    equipo,
    metrica_tiempo,
    metrica_velocidad,
    columnas_fecha_registro,
    idioma="es"
):

    df = df_sprint.copy()
    df[columnas_fecha_registro] = pd.to_datetime(df[columnas_fecha_registro], format="%d/%m/%Y", errors='coerce')
    df = df.sort_values(by=columnas_fecha_registro)

    color_barra = "#66c2ff"
    color_linea = "#1f77b4"
    color_promedio = "green"

    fig = go.Figure()

    # Etiquetas del eje X
    df_fechas_unicas = df[columnas_fecha_registro].drop_duplicates().sort_values()
    años_unicos = df_fechas_unicas.dt.year.unique()
    if len(años_unicos) == 1:
        tickvals = df_fechas_unicas
        ticktext = df_fechas_unicas.dt.strftime("%b")
    else:
        tickvals = df_fechas_unicas
        ticktext = df_fechas_unicas.dt.strftime("%b-%Y")

    # Obtener promedio
    promedio_row = df_promedios[
        (df_promedios["CATEGORIA"] == categoria) &
        (df_promedios["EQUIPO"] == equipo)
    ]
    prom_vel = None
    if not promedio_row.empty and metrica_velocidad in promedio_row.columns:
        val = promedio_row[metrica_velocidad].values[0]
        if pd.notna(val):
            prom_vel = val

    # --- Velocidad (barra) ---
    vel_min, vel_max = 0, 10  # valores por defecto
    if metrica_velocidad in df.columns:
        df_metric_vel = df[[columnas_fecha_registro, metrica_velocidad]].dropna()
        if not df_metric_vel.empty:
            data_min = df_metric_vel[metrica_velocidad].min()
            data_max = df_metric_vel[metrica_velocidad].max()

            # Calcular margen inferior y superior dinámico
            margen_inferior = 0
            margen_superior = 0
            if prom_vel is not None:
                if data_min >= prom_vel:
                    margen_inferior = max(1, prom_vel * 0.2)
                else:
                    margen_inferior = prom_vel - data_min + 1

                if data_max <= prom_vel:
                    margen_superior = max(1, prom_vel * 0.2)
                else:
                    margen_superior = data_max - prom_vel + 1

                vel_min = prom_vel - margen_inferior
                vel_max = prom_vel + margen_superior

                # Asegurarse que vel_min no sea negativo
                vel_min = max(0, vel_min)
            else:
                vel_min = data_min * 0.95
                vel_max = data_max * 1.05

            fig.add_trace(go.Bar(
                x=df_metric_vel[columnas_fecha_registro],
                y=df_metric_vel[metrica_velocidad],
                name=util.traducir(metrica_velocidad, idioma),
                marker_color=color_barra,
                yaxis="y1",
                text=df_metric_vel[metrica_velocidad].round(2),
                textposition="inside",
                textfont=dict(size=16,color="black"),
                hovertemplate=f"<b>DATE:</b> %{{x|%d-%m-%Y}}<br><b>{util.traducir(metrica_velocidad, idioma)}:</b> %{{y:.2f}} m/s<extra></extra>"
            ))

            # Anotación del mejor registro
            max_val = df_metric_vel[metrica_velocidad].max()
            fila_max = df_metric_vel[df_metric_vel[metrica_velocidad] == max_val].sort_values(by=columnas_fecha_registro, ascending=False).iloc[0]
            maxl = util.traducir("Max",idioma)
            fig.add_annotation(
                x=fila_max[columnas_fecha_registro],
                y=fila_max[metrica_velocidad],
                yref="y1",
                text=f"{maxl}: {fila_max[metrica_velocidad]:.2f} m/s",
                showarrow=True,
                arrowhead=2,
                ax=0,
                ay=-30,
                bgcolor=color_barra,
                font=dict(color="white")
            )

            # Línea de promedio de velocidad
            if prom_vel is not None:
                fig.add_hline(
                    y=prom_vel,
                    line=dict(color=color_promedio, dash="dash", width=2),
                    annotation_text=f"{prom_vel:.2f} m/s",
                    annotation_position="top right",
                    annotation=dict(font=dict(color="black", size=12, family="Arial")),
                    layer="above"
                )

                promedio = util.traducir("PROMEDIO", idioma)
                categoria = util.traducir(categoria.upper(), idioma)

                fig.add_trace(go.Scatter(
                    x=[None], y=[None],
                    mode="lines",
                    name=f"{metrica_velocidad} {promedio} ({categoria} {equipo})".upper(),
                    line=dict(color=color_promedio, dash="dash", width=2),
                    showlegend=True
                ))

    # --- Tiempo (línea) ---
    if metrica_tiempo in df.columns:
        df_metric_time = df[[columnas_fecha_registro, metrica_tiempo]].dropna()
        if not df_metric_time.empty:
            fig.add_trace(go.Scatter(
                x=df_metric_time[columnas_fecha_registro],
                y=df_metric_time[metrica_tiempo],
                mode="lines+markers",
                name=util.traducir(metrica_tiempo, idioma),
                line=dict(color=color_linea, width=3),
                marker=dict(size=8, color=color_linea),
                yaxis="y2",
                hovertemplate=f"<b>Fecha:</b> %{{x|%d-%m-%Y}}<br><b>{util.traducir(metrica_tiempo, idioma)}:</b> %{{y:.2f}} seg<extra></extra>"
            ))

            min_val = df_metric_time[metrica_tiempo].min()
            fila_min = df_metric_time[df_metric_time[metrica_tiempo] == min_val].sort_values(by=columnas_fecha_registro, ascending=False).iloc[0]
            maxl = util.traducir("Max",idioma)
            fig.add_annotation(
                x=fila_min[columnas_fecha_registro],
                y=fila_min[metrica_tiempo],
                yref="y2",
                text=f"{maxl}: {fila_min[metrica_tiempo]:.2f} seg",
                showarrow=True,
                arrowhead=2,
                ax=0,
                ay=30,
                bgcolor=color_linea,
                font=dict(color="white")
            )

    # --- Barra de colores (semaforo) ---
    if prom_vel is not None:
        fig.add_trace(go.Scatter(
            x=[None],
            y=[None],
            mode="markers",
            marker=dict(
                size=0,
                color=[prom_vel],
                colorscale=[
                    [0.0, "red"],
                    [0.5, "orange"],
                    [1.0, "green"]
                ],
                cmin=vel_min,
                cmax=vel_max,
                colorbar=dict(
                    title="",
                    #titleside="right",
                    ticks="outside",
                    tickfont=dict(color="black"),
                    #titlefont=dict(color="black"),
                    thickness=20,
                    len=1,
                    lenmode="fraction",
                    y=0,
                    yanchor="bottom",
                    x=-0.15,
                    xanchor="left"
                ),
                showscale=True
            ),
            showlegend=False,
            hoverinfo="skip"
        ))

    title = util.traducir("Evolución del Sprint", idioma)
    #metrica_tiempo = util.traducir(metrica_tiempo, idioma)
    # --- Layout final ---
    fig.update_layout(
        title=f"{title} ({util.traducir(metrica_tiempo, idioma)} y {util.traducir(metrica_velocidad, idioma)})",
        xaxis=dict(
            tickmode="array",
            tickvals=tickvals,
            ticktext=ticktext
        ),
        yaxis=dict(
            title=util.traducir("VELOCIDAD (M/S)",idioma),
            side="left",
            showgrid=True,
            range=[vel_min, vel_max]
        ),
        yaxis2=dict(
            title=util.traducir("TIEMPO (SEG)",idioma),
            overlaying="y",
            side="right",
            showgrid=False
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

def get_sprint_time_graph(df_sprint, df_promedios, categoria, equipo):
    df = df_sprint.copy()
    df["FECHA REGISTRO"] = pd.to_datetime(df["FECHA REGISTRO"], format="%d/%m/%Y", errors='coerce')
    df = df.sort_values(by="FECHA REGISTRO")

    metricas = ["TIEMPO 0-5M (SEG)", "TIEMPO 20-40M (SEG)"]
    colores_linea = {
        "TIEMPO 0-5M (SEG)": "#1f77b4",
        "TIEMPO 20-40M (SEG)": "#66c2ff"
    }
    colores_promedio = {
        "TIEMPO 0-5M (SEG)": "orange",
        "TIEMPO 20-40M (SEG)": "purple"
    }

    promedio_row = df_promedios[
        (df_promedios["CATEGORIA"] == categoria) &
        (df_promedios["EQUIPO"] == equipo)
    ]

    promedios = {}
    if not promedio_row.empty:
        for metrica in metricas:
            if metrica in promedio_row.columns:
                val = promedio_row[metrica].values[0]
                if pd.notna(val):
                    promedios[metrica] = val

    fig = go.Figure()
    tolerancia = 0.05

    for metrica in metricas:
        df_metrica = df[["FECHA REGISTRO", metrica]].dropna()
        x_vals = df_metrica["FECHA REGISTRO"]
        y_vals = df_metrica[metrica]

        colores_puntos = []
        for y in y_vals:
            if metrica in promedios:
                prom = promedios[metrica]
                if abs(y - prom) <= tolerancia:
                    colores_puntos.append("rgba(255, 215, 0, 0.9)")
                elif y > prom:
                    colores_puntos.append("rgba(255, 0, 0, 0.8)")
                else:
                    colores_puntos.append("rgba(0, 200, 0, 0.8)")
            else:
                colores_puntos.append("gray")

        nombre_legenda = metrica.replace(" (SEG)", "")

        fig.add_trace(go.Scatter(
            x=x_vals,
            y=y_vals,
            mode="lines",
            name=nombre_legenda,
            line=dict(color=colores_linea[metrica], width=3),
            showlegend=True
        ))

        fig.add_trace(go.Scatter(
            x=x_vals,
            y=y_vals,
            mode="markers",
            marker=dict(size=10, color=colores_puntos),
            name=metrica,
            showlegend=False,
            hovertemplate=f"<b>Fecha:</b> %{{x|%d-%m-%Y}}<br><b>{metrica}:</b> %{{y:.2f}} seg<extra></extra>"
        ))

        if not df_metrica.empty:
            max_val = y_vals.min()
            fila_max = df_metrica[df_metrica[metrica] == max_val].sort_values(by="FECHA REGISTRO", ascending=False).iloc[0]
            fig.add_annotation(
                x=fila_max["FECHA REGISTRO"],
                y=fila_max[metrica],
                text=f"Mejor Registro: {fila_max[metrica]:.2f} seg",
                showarrow=True,
                arrowhead=2,
                ax=0,
                ay=-90,
                bgcolor=colores_linea[metrica],
                font=dict(color="white")
            )

        if metrica in promedios:
            valor_prom = promedios[metrica]
            fig.add_hline(
                y=valor_prom,
                line=dict(color=colores_promedio[metrica], dash="dash"),
                annotation_text=f"Promedio ({categoria} {equipo}): {valor_prom:.2f} seg",
                layer="below",
                annotation=dict(font=dict(color="black", size=12, family="Arial"))
            )
            fig.add_trace(go.Scatter(
                x=[None], y=[None],
                mode="lines",
                name=f"{nombre_legenda} PROMEDIO".upper(),
                line=dict(color=colores_promedio[metrica], dash="dash", width=3)
            ))

    fig.update_layout(
        title="📈 Evolución del Sprint 40m (Tiempos)",
        yaxis_title="Tiempo (seg)",
        xaxis=dict(tickformat="%b", dtick="M1", title=None),
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
