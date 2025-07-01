import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import matplotlib.pyplot as plt
from utils import util

ESCALAS_COLOR_AGILIDAD = {
    "H": {
        "cadete": [
            [0.0, "#7CFC00"],
            [0.6, "#006400"],
            [0.7, "#FFD700"],
            [0.8, "#FFA500"],
            [1.0, "#FF4500"]
        ],
        "juvenil": [
            [0.0, "#7CFC00"],
            [0.6, "#006400"],
            [0.7, "#FFD700"],
            [0.8, "#FFA500"],
            [1.0, "#FF4500"]
        ]
    },
    "M": {
        "cadete": [
            [0.0, "#7CFC00"],
            [0.40, "#006400"],
            [0.50, "#FFD700"],
            [0.60, "#FFA500"],
            [0.70, "#FF4500"],
            [1.0, "#FF4500"]
        ],
        "juvenil": [
            [0.0, "#7CFC00"],
            [0.30, "#006400"],
            [0.40, "#FFD700"],
            [0.55, "#FFA500"],
            [0.70, "#FF4500"],
            [1.0, "#FF4500"]
        ]
    }
}

def get_escala_color_agilidad(genero: str, categoria: str) -> list:
    """
    Retorna la escala de colores de agilidad según el género y categoría.
    """
    genero = genero.upper()
    categoria = categoria.lower()
    return ESCALAS_COLOR_AGILIDAD.get(genero, {}).get(categoria, ESCALAS_COLOR_AGILIDAD["H"]["juvenil"])

def calcular_color_diferencia_agilidad(diferencia: float, genero: str = "H", categoria: str = "juvenil") -> str:
    """
    Determina el color correspondiente a un porcentaje de diferencia en agilidad según género y categoría.

    Args:
        diferencia (float): Diferencia porcentual.
        genero (str): Género del jugador ('H' o 'M').
        categoria (str): Categoría ('cadete', 'juvenil', etc.)

    Returns:
        str: Código hexadecimal del color correspondiente.
    """
    escala = get_escala_color_agilidad(genero, categoria)

    if pd.isna(diferencia) or not escala:
        # Siempre devolver el color del peor umbral (último en la escala) si no hay dato válido
        return escala[-1][1]
    
    # Normaliza la diferencia al rango [0, 1]
    max_dif = 10.0
    valor_normalizado = min(diferencia / max_dif, 1.0)

    for i in range(1, len(escala)):
        if valor_normalizado < escala[i][0]:
            return escala[i - 1][1]

    return escala[-1][1]

def get_agilidad_colorbar_agregada(fig, y_min, y_max, gender, categoria):
    escala = get_escala_color_agilidad(gender, categoria)
    tickvals = [round(umbral * 10, 2) for umbral, _ in escala]
    ticktext = [str(round(umbral * 10, 1)) for umbral, _ in escala]

    fig.add_trace(go.Scatter(
        x=[None],
        y=[None],
        mode="markers",
        marker=dict(
            size=0,
            color=[10],
            cmin=0,
            cmax=round(tickvals[-1] + 1, 1),
            colorscale=escala,
            colorbar=dict(
                title=dict(text="DIF %"),
                tickvals=tickvals,
                ticktext=ticktext,
                tickfont=dict(size=12, color="black"),
                thickness=20,
                len=1,
                lenmode="fraction",
                y=0.5,
                yanchor="middle",
                x=1.03,
                xanchor="left"
            ),
            showscale=True
        ),
        showlegend=False,
        hoverinfo="skip"
    ))
    return fig

def get_agility_graph_combined_simple(df_agility, df_promedios, categoria, equipo, metricas, columnas_fecha_registro, idioma="es", barras=False, cat_label="U19", gender="H"):

    df = pd.DataFrame(df_agility)
    df[columnas_fecha_registro] = pd.to_datetime(df[columnas_fecha_registro], format="%d/%m/%Y", errors="coerce")
    df = df.sort_values(by=columnas_fecha_registro)

    fechas_unicas = pd.to_datetime(df[columnas_fecha_registro].dropna().unique())
    periodos = pd.Series(fechas_unicas).dt.to_period("M").unique()
    fecha_formato = "%d-%b-%Y" if len(periodos) == 1 else "%b-%Y"
    df["FECHA TEXTO"] = df[columnas_fecha_registro].dt.strftime(fecha_formato)

    columna_x = "FECHA TEXTO"
    color_linea_dom = "#1f77b4"
    color_linea_nd = "#66c2ff"
    fig = go.Figure()

    promedio_row = df_promedios[
        (df_promedios["CATEGORIA"] == categoria) &
        (df_promedios["EQUIPO"] == equipo)
    ]

    promedios = {}
    for metrica in metricas:
        if not promedio_row.empty and metrica in promedio_row.columns:
            valor = promedio_row[metrica].values[0]
            if pd.notna(valor):
                promedios[metrica] = valor

    valores = []
    for metrica in metricas:
        valores += df[metrica].dropna().tolist()

    if valores:
        ymin = min(valores) - 0.1
        ymax = max(valores) + 0.5
        margen = (ymax - ymin) * 0.3
        ymin = min(0, ymin - margen) 
        ymax += margen
    else:
        ymin, ymax = 0, 1

    for metrica, color, dash in zip(metricas, [color_linea_nd, color_linea_dom], ["solid", "dash"]):
        df_metric = df[[columna_x, columnas_fecha_registro, metrica]].dropna()
        x_vals = df_metric[columna_x].tolist()
        y_vals = df_metric[metrica].tolist()

        if barras or len(x_vals) == 1:
            size = 20 if len(x_vals) == 1 else 14
            fig.add_trace(go.Bar(
                x=x_vals,
                y=y_vals,
                name=util.traducir(metrica, idioma),
                marker_color=color,
                text=[f"{val:.2f} seg" for val in y_vals],
                textposition="auto",
                textfont=dict(size=size),
                hovertemplate=f"<b>Fecha:</b> %{{x}}<br><b>{util.traducir(metrica, idioma)}:</b> %{{y:.2f}} seg<extra></extra>"
            ))
        else:
            fig.add_trace(go.Scatter(
                x=x_vals,
                y=y_vals,
                mode="lines+markers",
                name=util.traducir(metrica, idioma),
                line=dict(color=color, width=3, dash=dash),
                marker=dict(size=8, color=color),
                hovertemplate=f"<b>Fecha:</b> %{{x}}<br><b>{metrica}:</b> %{{y:.2f}} seg<extra></extra>"
            ))

        if (not df_metric.empty and len(df_metric) > 1) and not barras:
            min_val = df_metric[metrica].min()
            fila_min = df_metric[df_metric[metrica] == min_val].sort_values(by=columnas_fecha_registro, ascending=False).iloc[0]
            maxl = util.traducir("Min ", idioma)
            xshift_val = -20 if barras and metrica == metricas[0] else 20 if barras and metrica == metricas[1] else 0
            offset_y = -30 if metrica == metricas[1] else -60
            offset_x = 60 if metrica == metricas[1] else -60
            fig.add_annotation(
                x=fila_min[columna_x],
                y=fila_min[metrica],
                text=f"{maxl}: {fila_min[metrica]:.2f} seg",
                showarrow=True,
                arrowhead=2,
                ax=offset_x,
                ay=offset_y,
                xshift=xshift_val,
                bgcolor="gray",
                font=dict(color="white")
            )

    added_to_legend = False
    for idx, row in df.iterrows():
        fecha = row[columna_x]
        dom = row.get(metricas[0], None)
        nd = row.get(metricas[1], None)
        sizet = 20 if len(df) == 1 else 13
        sizec = 55 if len(df) == 1 else 40

        if pd.notna(dom) and pd.notna(nd) and nd != 0:
            diferencia = (abs(dom - nd) / nd) * 100
            color = calcular_color_diferencia_agilidad(diferencia, gender)

            if diferencia < 1:
                y_pos = 0.5
            elif 0 <= diferencia <= 10:
                y_pos = ymin + (diferencia / 12) * (ymax - ymin)
            else:
                y_pos = 3

            diferenciat = util.traducir("DIFERENCIA %", idioma);
            fig.add_trace(go.Scatter(
                x=[fecha],
                y=[y_pos],
                mode="markers+text",
                marker=dict(size=sizec, color=color, opacity=0.9),
                text=f"{diferencia:.1f}%",
                textfont=dict(size=sizet, color="black"),
                textposition="middle center",
                showlegend=not added_to_legend,
                name=f"{diferenciat} ({cat_label})",
                hoverinfo="skip"
            ))
            added_to_legend = True

    tickvals = df["FECHA TEXTO"].drop_duplicates().tolist()
    ticktext = tickvals

    title_layout = "AGILIDAD (Pierna Izquierda y Pierna Derecha)" if barras else "Evolución de la Agilidad (Pierna Izquierda y Pierna Derecha)"
    fig.update_layout(
        title=util.traducir(title_layout, idioma).upper(),
        xaxis=dict(
            tickmode="array",
            tickvals=tickvals,
            ticktext=ticktext,
            type="category",
            showticklabels=not barras
        ),
        yaxis=dict(
            title=util.traducir("TIEMPO (SEG)", idioma),
            range=[ymin, ymax],
            side="left"
        ),
        template="plotly_white",
        barmode="group" if barras or len(df) == 1 else "overlay",
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=-0.3,
            xanchor="center",
            x=0.5
        )
    )

    fig = get_agilidad_colorbar_agregada(fig, ymin, ymax, gender, categoria)

    st.plotly_chart(fig, use_container_width=True)
    return fig

# def get_agility_graph_combined_simple(df_agility, df_promedios, categoria, equipo, metricas, columnas_fecha_registro, idioma="es", barras=False):

#     df = pd.DataFrame(df_agility)
#     df[columnas_fecha_registro] = pd.to_datetime(df[columnas_fecha_registro], format="%d/%m/%Y", errors="coerce")
#     df = df.sort_values(by=columnas_fecha_registro)

#     fechas_unicas = pd.to_datetime(df[columnas_fecha_registro].dropna().unique())
#     periodos = pd.Series(fechas_unicas).dt.to_period("M").unique()
#     fecha_formato = "%d-%b-%Y" if len(periodos) == 1 else "%b-%Y"
#     df["FECHA TEXTO"] = df[columnas_fecha_registro].dt.strftime(fecha_formato)

#     columna_x = "FECHA TEXTO"

#     color_linea_dom = "#1f77b4"   # azul
#     color_linea_nd = "#66c2ff"    # celeste

#     fig = go.Figure()

#     promedio_row = df_promedios[
#         (df_promedios["CATEGORIA"] == categoria) &
#         (df_promedios["EQUIPO"] == equipo)
#     ]

#     promedios = {}
#     for metrica in metricas:
#         if not promedio_row.empty and metrica in promedio_row.columns:
#             valor = promedio_row[metrica].values[0]
#             if pd.notna(valor):
#                 promedios[metrica] = valor

#     valores = []
#     for metrica in metricas:
#         valores += df[metrica].dropna().tolist()

#     if valores:
#         ymin = min(valores) - 0.1
#         ymax = max(valores) + 0.1
#         margen = (ymax - ymin) * 0.8
#         ymin -= margen
#         ymax += margen
#     else:
#         ymin, ymax = 0, 1

#     for metrica, color, dash in zip(metricas, [color_linea_nd, color_linea_dom], ["solid", "dash"]):
#         df_metric = df[[columna_x, columnas_fecha_registro, metrica]].dropna()
#         x_vals = df_metric[columna_x].tolist()
#         y_vals = df_metric[metrica].tolist()

#         if barras:
#             size = 20 if len(x_vals) == 1 else 14
#             fig.add_trace(go.Bar(
#                 x=x_vals,
#                 y=y_vals,
#                 name=util.traducir(metrica, idioma),
#                 marker_color=color,
#                 text=[f"{val:.2f} seg" for val in y_vals],
#                 textposition="auto",
#                 textfont=dict(size=size),
#                 hovertemplate=f"<b>Fecha:</b> %{{x}}<br><b>{util.traducir(metrica, idioma)}:</b> %{{y:.2f}} seg<extra></extra>"
#             ))
#         else:
#             fig.add_trace(go.Scatter(
#                 x=x_vals,
#                 y=y_vals,
#                 mode="lines+markers",
#                 name=util.traducir(metrica, idioma),
#                 line=dict(color=color, width=3, dash=dash),
#                 marker=dict(size=8, color=color),
#                 hovertemplate=f"<b>Fecha:</b> %{{x}}<br><b>{metrica}:</b> %{{y:.2f}} seg<extra></extra>"
#             ))

#         if (not df_metric.empty and len(df_metric) > 1) or not barras:
#             min_val = df_metric[metrica].min()
#             fila_min = df_metric[df_metric[metrica] == min_val].sort_values(by=columnas_fecha_registro, ascending=False).iloc[0]
#             maxl = util.traducir("Min ", idioma)
#             xshift_val = -20 if barras and metrica == metricas[0] else 20 if barras and metrica == metricas[1] else 0
#             offset_y = -30 if metrica == metricas[1] else -60
#             offset_x = 60 if metrica == metricas[1] else -60
#             fig.add_annotation(
#                 x=fila_min[columna_x],
#                 y=fila_min[metrica],
#                 text=f"{maxl}: {fila_min[metrica]:.2f} seg",
#                 showarrow=True,
#                 arrowhead=2,
#                 ax=offset_x,
#                 ay=offset_y,
#                 xshift=xshift_val,
#                 bgcolor="gray",
#                 font=dict(color="white")
#             )

#     added_to_legend = False
#     for idx, row in df.iterrows():
#         fecha = row[columna_x]
#         dom = row.get(metricas[0], None)
#         nd = row.get(metricas[1], None)
#         size = 20 if len(x_vals) == 1 else 14
#         if pd.notna(dom) and pd.notna(nd) and nd != 0:
#             diferencia = ((dom - nd) / nd) * 100
#             fig.add_trace(go.Scatter(
#                 x=[fecha],
#                 y=[max(dom, nd) + 0.2],
#                 mode="markers+text",
#                 marker=dict(size=20, color="orange", opacity=0.7),
#                 text=f"{diferencia:.1f}%",
#                 textfont=dict(size=size,color="black"),
#                 textposition="top center",
#                 showlegend=not added_to_legend,
#                 name=util.traducir("DIFERENCIA %", idioma),
#                 hoverinfo="skip"
#             ))
#             added_to_legend = True

#     # if valores:
#     #     prom_dom = promedios.get(metricas[0], (ymin + ymax) / 2)
#     #     fig.add_trace(go.Scatter(
#     #         x=[None],
#     #         y=[None],
#     #         mode="markers",
#     #         marker=dict(
#     #             size=0,
#     #             color=[prom_dom],
#     #             colorscale=[
#     #                 [0.0, "green"],
#     #                 [0.5, "orange"],
#     #                 [1.0, "red"]
#     #             ],
#     #             cmin=ymin,
#     #             cmax=ymax,
#     #             colorbar=dict(
#     #                 title="",
#     #                 ticks="outside",
#     #                 tickfont=dict(color="black"),
#     #                 thickness=20,
#     #                 len=1,
#     #                 lenmode="fraction",
#     #                 y=0,
#     #                 yanchor="bottom",
#     #                 x=1.05,
#     #                 xanchor="left"
#     #             ),
#     #             showscale=True
#     #         ),
#     #         showlegend=False,
#     #         hoverinfo="skip"
#     #     ))

#     tickvals = df["FECHA TEXTO"].drop_duplicates().tolist()
#     ticktext = tickvals

#     title_layout = "AGILIDAD (IZQ Y DER)" if barras else "Evolución de la Agilidad (IZQ y DER)"
#     fig.update_layout(
#         title=util.traducir(title_layout, idioma).upper(),
#         xaxis=dict(
#             tickmode="array",
#             tickvals=tickvals,
#             ticktext=ticktext,
#             type="category",
#             showticklabels=not barras
#         ),
#         yaxis=dict(
#             title=util.traducir("TIEMPO (SEG)", idioma),
#             range=[ymin, ymax],
#             side="left"
#         ),
#         template="plotly_white",
#         barmode="group" if barras else "overlay",
#         legend=dict(
#             orientation="h",
#             yanchor="bottom",
#             y=-0.3,
#             xanchor="center",
#             x=0.5
#         )
#     )

#     st.plotly_chart(fig, use_container_width=True)
#     return fig

def get_diferencia_agilidad(df_agility, metricas, columna_fecha):
    """
    Calcula la diferencia porcentual entre pierna dominante y no dominante en agilidad (505).
    
    Parámetros:
        df_agility (pd.DataFrame): Datos del test de agilidad.
        metricas (list): Lista con dos métricas, [dominante, no dominante].
        columna_fecha (str): Nombre de la columna de fecha.
        
    Retorna:
        list[dict]: Lista con fecha y diferencia porcentual para cada fila válida.
    """
    df = df_agility.copy()
    df[columna_fecha] = pd.to_datetime(df[columna_fecha], format="%d/%m/%Y", errors="coerce")
    df = df.sort_values(by=columna_fecha)

    diferencias = []

    for _, row in df.iterrows():
        dom = row.get(metricas[0])
        nd = row.get(metricas[1])
        fecha = row.get(columna_fecha)

        if pd.notna(dom) and pd.notna(nd) and nd != 0:
            diferencia = (abs(dom - nd) / nd) * 100
            diferencias.append({
                "fecha": fecha,
                "diferencia_%": round(diferencia, 2)
            })

    return diferencias

def get_agility_graph_combined(df_agility, df_promedios, categoria, equipo, metricas, columnas_fecha_registro, idioma="es"):

    df = pd.DataFrame(df_agility)
    df[columnas_fecha_registro] = pd.to_datetime(df[columnas_fecha_registro], format="%d/%m/%Y", errors="coerce")
    df = df.sort_values(by=columnas_fecha_registro)

    #metricas = ["PIERNA IZQ (SEG)", "PIERNA DER (SEG)"]

    color_linea_dom = "#1f77b4"   # azul
    color_linea_nd = "#66c2ff"    # celeste
    #color_promedio = "green"

    fig = go.Figure()

    # --- Calcular promedios ---
    promedio_row = df_promedios[
        (df_promedios["CATEGORIA"] == categoria) &
        (df_promedios["EQUIPO"] == equipo)
    ]

    promedios = {}
    for metrica in metricas:
        if not promedio_row.empty and metrica in promedio_row.columns:
            valor = promedio_row[metrica].values[0]
            if pd.notna(valor):
                promedios[metrica] = valor

    # --- Calcular rango Y ---
    valores = []
    for metrica in metricas:
        valores += df[metrica].dropna().tolist()
    if valores:
        ymin = min(valores) - 0.1
        ymax = max(valores) + 0.1
        margen = (ymax - ymin) * 0.8
        ymin -= margen
        ymax += margen
    else:
        ymin, ymax = 0, 1

    # --- Trazas de las piernas ---
    for metrica, color, dash in zip(
        metricas, [color_linea_nd, color_linea_dom], ["solid", "dash"]
    ):
        df_metric = df[[columnas_fecha_registro, metrica]].dropna()
        x_vals = df_metric[columnas_fecha_registro].tolist()
        y_vals = df_metric[metrica].tolist()

        fig.add_trace(go.Scatter(
            x=x_vals,
            y=y_vals,
            mode="lines+markers",
            name=util.traducir(metrica,idioma),
            line=dict(color=color, width=3, dash=dash),
            marker=dict(size=8, color=color),
            hovertemplate=f"<b>Fecha:</b> %{{x|%d-%m-%Y}}<br><b>{metrica}:</b> %{{y:.2f}} seg<extra></extra>"
        ))

        # Mejor registro
        if not df_metric.empty:
            min_val = df_metric[metrica].min()
            fila_min = df_metric[df_metric[metrica] == min_val].sort_values(by=columnas_fecha_registro, ascending=False).iloc[0]
            maxl = util.traducir("Max",idioma)
            offset_y = -40 if metrica == metricas[1] else -90
            fig.add_annotation(
                x=fila_min[columnas_fecha_registro],
                y=fila_min[metrica],
                text=f"{maxl}: {fila_min[metrica]:.2f} seg",
                showarrow=True,
                arrowhead=2,
                ax=80,
                ay=offset_y,
                bgcolor=color,
                font=dict(color="white")
            )

    # --- Calcular y marcar % diferencia (DOM vs ND) ---
    added_to_legend = False  # solo la primera vez
    for idx, row in df.iterrows():
        fecha = row[columnas_fecha_registro]
        dom = row.get(metricas[0], None)
        nd = row.get(metricas[1], None)
        if pd.notna(dom) and pd.notna(nd) and nd != 0:
            diferencia = ((dom - nd) / nd) * 100
            fig.add_trace(go.Scatter(
                x=[fecha],
                y=[max(dom, nd) + 0.05],
                mode="markers+text",
                marker=dict(size=15, color="orange", opacity=0.7),
                text=f"{diferencia:.1f}%",
                textposition="top center",
                showlegend=not added_to_legend,  # solo la primera vez
                name=util.traducir("DIFERENCIA %",idioma),
                hoverinfo="skip"
            ))
            added_to_legend = True

    # --- Barra de colores a la derecha ---
    if valores:
        prom_dom = promedios.get(metricas[0], (ymin + ymax) / 2)
        fig.add_trace(go.Scatter(
            x=[None],
            y=[None],
            mode="markers",
            marker=dict(
                size=0,
                color=[prom_dom],
                colorscale=[
                    [0.0, "green"],  # mejor es más bajo
                    [0.5, "orange"],
                    [1.0, "red"]
                ],
                cmin=ymin,
                cmax=ymax,
                colorbar=dict(
                    title= "",
                    #titleside="right",
                    ticks="outside",
                    tickfont=dict(color="black"),
                    #titlefont=dict(color="black"),
                    thickness=20,
                    len=1,
                    lenmode="fraction",
                    y=0,
                    yanchor="bottom",
                    x=1.05,
                    xanchor="left"
                ),
                showscale=True
            ),
            showlegend=False,
            hoverinfo="skip"
        ))

    # --- Etiquetas eje X dinámicas ---
    df_fechas_unicas = df[columnas_fecha_registro].dropna().drop_duplicates().sort_values()
    tickvals = df_fechas_unicas

    # Verificamos si todas las fechas son del mismo mes y año
    meses_anio = df_fechas_unicas.dt.to_period("M").unique()
    if len(meses_anio) == 1:
        ticktext = df_fechas_unicas.dt.strftime("%d-%b-%Y")  # formato completo
    else:
        ticktext = df_fechas_unicas.dt.strftime("%b-%Y")     # solo mes-año

    # --- Layout final ---
    fig.update_layout(
        title=util.traducir("Evolución de la Agilidad (IZQ y DER)", idioma),
        xaxis=dict(
            tickmode="array",
            tickvals=tickvals,
            ticktext=ticktext
        ),
        yaxis=dict(
            title=util.traducir("TIEMPO (SEG)", idioma),
            range=[ymin, ymax],
            side="left"
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

def get_agility_graph_dom(df_agility, df_promedios, categoria, equipo):
    return _render_agility_graph(
        df_agility, df_promedios, categoria, equipo,
        metrica="505-DOM (SEG)",
        nombre_legenda="Cambio de Dirección con Pierna Dominante",
        color="#1f77b4",
        color_promedio="orange"
    )

def get_agility_graph_nd(df_agility, df_promedios, categoria, equipo):
    return _render_agility_graph(
        df_agility, df_promedios, categoria, equipo,
        metrica="505-ND (SEG)",
        nombre_legenda="Cambio de Dirección con Pierna No Dominante",
        color="#66c2ff",
        color_promedio="purple"
    )

def _render_agility_graph(df_agility, df_promedios, categoria, equipo, metrica, nombre_legenda, color, color_promedio):
    df = pd.DataFrame(df_agility)
    df["FECHA REGISTRO"] = pd.to_datetime(df["FECHA REGISTRO"], format="%d/%m/%Y", errors="coerce")
    df = df.sort_values(by="FECHA REGISTRO")

    tolerancia = 0.05

    promedio_row = df_promedios[
        (df_promedios["CATEGORIA"] == categoria) &
        (df_promedios["EQUIPO"] == equipo)
    ]

    prom = None
    if not promedio_row.empty and metrica in promedio_row.columns:
        prom_val = promedio_row[metrica].values[0]
        if pd.notna(prom_val):
            prom = prom_val

    df_metric = df[["FECHA REGISTRO", metrica]].dropna()
    x_vals = df_metric["FECHA REGISTRO"].tolist()
    y_vals = df_metric[metrica].tolist()

    colores_puntos = []
    for val in y_vals:
        if prom is not None:
            if abs(val - prom) <= tolerancia:
                colores_puntos.append("rgba(255, 215, 0, 0.9)")
            elif val > prom:
                colores_puntos.append("rgba(255, 0, 0, 0.8)")
            else:
                colores_puntos.append("rgba(0, 200, 0, 0.8)")
        else:
            colores_puntos.append("gray")

    fig = go.Figure()

    fig.add_trace(go.Scatter(
        x=x_vals,
        y=y_vals,
        mode="lines",
        name=metrica,
        line=dict(color=color, width=3),
        showlegend=True
    ))

    fig.add_trace(go.Scatter(
        x=x_vals,
        y=y_vals,
        mode="markers",
        name=metrica,
        showlegend=False,
        marker=dict(size=10, color=colores_puntos),
        hovertemplate=f"<b>Fecha:</b> %{{x|%d-%m-%Y}}<br><b>{metrica}:</b> %{{y:.2f}} seg<extra></extra>"
    ))

    if not df_metric.empty:
        max_val = df_metric[metrica].min()
        fila_max = df_metric[df_metric[metrica] == max_val].sort_values(by="FECHA REGISTRO", ascending=False).iloc[0]
        fig.add_annotation(
            x=fila_max["FECHA REGISTRO"],
            y=fila_max[metrica],
            text=f"Mejor Registro: {fila_max[metrica]:.2f} seg",
            showarrow=True,
            arrowhead=2,
            ax=0,
            ay=-30,
            bgcolor=color,
            font=dict(color="white")
        )

    if prom is not None:
        fig.add_hline(
            y=prom,
            line=dict(color=color_promedio, dash="dash"),
            annotation_text=f"Promedio ({categoria} {equipo}): {prom:.2f} seg",
            annotation_position="top right",
            annotation=dict(font=dict(color="black", size=12, family="Arial"))
        )
        fig.add_trace(go.Scatter(
            x=[None], y=[None],
            mode="lines",
            name=f"{metrica} PROMEDIO {categoria} {equipo}".upper(),
            line=dict(color=color_promedio, dash="dash")
        ))

    fig.update_layout(
        title=f"📈 Evolución de la Agilidad ({nombre_legenda})",
        xaxis_title=None,
        yaxis_title="Tiempo (Seg)",
        xaxis=dict(tickformat="%b", dtick="M1"),
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

