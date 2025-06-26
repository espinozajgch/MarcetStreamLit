import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import matplotlib.pyplot as plt
from utils import util

CMJ_SEMAFORO = {
    "H": {
        "juvenil": [
            (15, "#FF0000"),
            (32, "#FFA500"),
            (34, "#FFFF00"),
            (37, "#006400"),
            (39, "#7CFC00"),
            (45, "#7CFC00"),
            (50, "#7CFC00")
        ],
        "cadete": [
            (15, "#FF0000"),
            (26, "#FFA500"),
            (29, "#FFFF00"),
            (32, "#006400"),
            (35, "#7CFC00"),
            (42, "#7CFC00"),
            (50, "#7CFC00")
        ]
    },
    "M": {
        "juvenil": [
            (15, "#FF0000"),
            (21, "#FF0000"),
            (22, "#FFA500"),
            (23, "#FFFF00"),
            (24, "#006400"),
            (25, "#7CFC00"),
            (35, "#7CFC00")
        ],
        "cadete": [
            (15, "#FF0000"),
            (18, "#FF0000"),
            (19, "#FFA500"),
            (20, "#FFFF00"),
            (21, "#006400"),
            (22, "#7CFC00"),
            (35, "#7CFC00")
        ]
    }
}

def get_cmj_color_scale(genero, categoria):
    return CMJ_SEMAFORO.get(genero.upper(), {}).get(categoria.lower(), [])

def asignar_color_cmj(valor, genero, categoria):
    if pd.isna(valor):
        return "gray"
    
    escala = get_cmj_color_scale(genero, categoria)

    # Recorremos en orden descendente para que el primer umbral menor o igual al valor se aplique
    for umbral_min, color in reversed(escala):
        if valor >= umbral_min:
            return color

    # Si no cumple ningún umbral (menor que todos), usamos el color del más bajo
    return escala[0][1] if escala else "gray"

def get_color_scale(genero, categoria, cmin, cmax):
    genero = genero.upper()
    categoria = categoria.lower()
    semaforo = get_cmj_color_scale(genero, categoria)

    def norm(v):
        return max(0, min(1, round((v - cmin) / (cmax - cmin), 4)))

    escala = []
    for umbral, color in semaforo:
        escala.append([norm(umbral), color])
    if escala[-1][0] < 1:
        escala.append([1, semaforo[-1][1]])
    return escala


# def obtener_colorscale_cmj(genero, categoria, cmin, cmax):
#     escala = get_cmj_color_scale(genero, categoria)
#     if not escala:
#         return []
#     def norm(v):
#         return max(0, min(1, round((v - cmin) / (cmax - cmin), 4)))
#     return [[norm(umbral), color] for umbral, color in escala]

def calcular_rango_cmj(valores, escala, genero):
    if not escala:
        return min(valores), max(valores)
    umbrales = [umbral for umbral, _ in escala]
    minimo = min(15, min(umbrales)) - 1
    maximo = max(50 if genero == "H" else 40, max(umbrales)) + 1
    if maximo - minimo < 10:
        maximo = minimo + 10
    return minimo, maximo

def get_cmj_graph(df_cmj, promedios, categoria, equipo, metricas, columna_fecha_registro, idioma="es", barras=False, gender="H", cat_label="U19"):
    df = pd.DataFrame(df_cmj)
    df[columna_fecha_registro] = pd.to_datetime(df[columna_fecha_registro], format="%d/%m/%Y")
    df = df.sort_values(by=columna_fecha_registro)

    fechas_unicas = df[columna_fecha_registro].dropna().drop_duplicates().sort_values()
    periodos = fechas_unicas.dt.to_period("M").unique()
    formato_fecha = "%d-%b-%Y" if len(periodos) == 1 else "%b-%Y"

    if barras:
        df["FECHA TEXTO"] = df[columna_fecha_registro].dt.strftime(formato_fecha)
        columna_x = "FECHA TEXTO"
    else:
        columna_x = columna_fecha_registro

    color_linea = {metricas[0]: "#163B5B"}
    color_promedio = {metricas[0]: "green"}

    id_vars = [columna_fecha_registro] if columna_x == columna_fecha_registro else [columna_fecha_registro, columna_x]
    df_melted = df.melt(id_vars=id_vars, value_vars=metricas, var_name="MÉTRICA", value_name="VALOR").dropna()

    fig = go.Figure()
    valores = df_melted["VALOR"].tolist() + list(promedios.values())

    # --- Rango dinámico con base entre 20-50 ---
    maxg = (50 if gender == "H" else 35)
    cmj_min = min(valores)
    cmj_max = max(valores)
    cmin = min(15, cmj_min - 1 if cmj_min < 20 else cmj_min)
    cmax = max(maxg, cmj_max + 1 if cmj_max > maxg else cmj_max)
    if cmax - cmin < 10:
        cmax = cmin + 10

    tickvals = df["FECHA TEXTO"].unique().tolist() if barras else fechas_unicas
    ticktext = tickvals if barras else fechas_unicas.dt.strftime(formato_fecha)

    for metrica in metricas:
        df_filtro = df_melted[df_melted["MÉTRICA"] == metrica]
        x_vals = df_filtro[columna_x].tolist()
        y_vals = df_filtro["VALOR"].tolist()

        colores_puntos = [asignar_color_cmj(v, gender, categoria) for v in y_vals]

        if barras or len(y_vals) == 1:
            ancho_barra = 0.2 if len(x_vals) == 1 else 0.3
            size = 19 if len(x_vals) == 1 else 14
            fig.add_trace(go.Bar(
                x=x_vals,
                y=y_vals,
                name=util.traducir(metrica, idioma).replace("-", " "),
                marker_color=colores_puntos,
                width=ancho_barra,
                yaxis="y1",
                text=[f"{v:.2f} cm" for v in y_vals],
                textposition="inside",
                textfont=dict(size=size),
                hovertemplate=f"<b>Fecha:</b> %{{x}}<br><b>{metrica}:</b> %{{y:.2f}} cm<extra></extra>"
            ))
        else:
            fig.add_trace(go.Scatter(
                x=x_vals,
                y=y_vals,
                mode="lines",
                name=util.traducir(metrica, idioma),
                line=dict(color=color_linea[metrica], width=3),
                hoverinfo="skip"
            ))
            fig.add_trace(go.Scatter(
                x=x_vals,
                y=y_vals,
                mode="markers",
                name=metrica,
                showlegend=False,
                marker=dict(size=10, color=colores_puntos),
                hovertemplate=f"<b>Fecha:</b> %{{x|%d-%m-%Y}}<br><b>{metrica}:</b> %{{y:.2f}} cm<extra></extra>"
            ))

        if not barras and len(df_filtro) > 1:
            max_val = df_filtro["VALOR"].max()
            fila_max = df_filtro[df_filtro["VALOR"] == max_val].sort_values(by=columna_fecha_registro, ascending=False).iloc[0]
            maxl = util.traducir("Max", idioma)
            fig.add_annotation(
                x=fila_max[columna_x],
                y=fila_max["VALOR"],
                text=f"{maxl}: {fila_max['VALOR']:.2f} cm",
                showarrow=True,
                arrowhead=2,
                ax=0,
                ay=-30,
                bgcolor="gray",
                font=dict(color="white")
            )

    for metrica, valor_prom in promedios.items():
        fig.add_hline(
            y=valor_prom,
            line=dict(color=color_promedio.get(metrica, "gray"), dash="dash"),
            annotation_text=f"{valor_prom:.2f} cm",
            annotation_position="top right",
            annotation=dict(font=dict(color="black", size=14, family="Arial")),
            layer="above"
        )
        fig.add_trace(go.Scatter(
            x=[None], y=[None],
            mode="lines",
            name=f"{util.traducir('ALTURA OPTIMA', idioma)} ({util.traducir('PROMEDIO', idioma)} {cat_label})".upper(),
            line=dict(color=color_promedio.get(metrica, "gray"), dash="dash")
        ))

    # --- Colorbar lateral según categoría ---
    colorscale = get_color_scale(gender, categoria, cmin, cmax)

    fig.add_trace(go.Scatter(
        x=[None], y=[None],
        mode="markers",
        marker=dict(
            size=0,
            color=[(cmin + cmax) / 2],
            colorscale=colorscale,
            cmin=cmin,
            cmax=cmax,
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

    title_layout = "POTENCIA MUSCULAR DE SALTO (CMJ)" if barras else "Evolución de la Potencia Muscular de Salto (CMJ)"
    fig.update_layout(
        title=util.traducir(title_layout, idioma).upper(),
        xaxis=dict(
            tickmode="array",
            tickvals=tickvals,
            ticktext=ticktext,
            type="category" if barras else "date",
            showticklabels=not barras and len(tickvals) > 1
        ),
        yaxis=dict(
            title=util.traducir("ALTURA DE SALTO (CM)", idioma),
            range=[cmin, cmax]
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
