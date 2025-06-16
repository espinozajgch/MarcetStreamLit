import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import matplotlib.pyplot as plt
from utils import util

# Versión final de get_cmj_graph con formato de fecha adaptativo
def get_cmj_graph(df_cmj, df_promedios_cmj, categoria, equipo, metricas, columna_fecha_registro, idioma="es", barras=False):
    df = pd.DataFrame(df_cmj)
    df[columna_fecha_registro] = pd.to_datetime(df[columna_fecha_registro], format="%d/%m/%Y")
    df = df.sort_values(by=columna_fecha_registro)

    # --- Formato adaptativo de fecha ---
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

    promedio_row = df_promedios_cmj[
        (df_promedios_cmj["CATEGORIA"] == categoria) &
        (df_promedios_cmj["EQUIPO"] == equipo)
    ]

    promedios = {}
    if not promedio_row.empty:
        for metrica in metricas:
            if metrica in promedio_row.columns:
                valor = promedio_row[metrica].values[0]
                if pd.notna(valor):
                    promedios[metrica] = valor
    else:
        st.warning("No se encontraron promedios de CMJ para la categoría y equipo especificados.")

    id_vars = [columna_fecha_registro] if columna_x == columna_fecha_registro else [columna_fecha_registro, columna_x]
    df_melted = df.melt(id_vars=id_vars, value_vars=metricas, var_name="MÉTRICA", value_name="VALOR").dropna()

    fig = go.Figure()

    valores = df_melted["VALOR"].tolist()
    for prom in promedios.values():
        valores.append(prom)

    if promedios and metricas[0] in promedios:
        prom = promedios[metricas[0]]
        data_min = min(valores)
        data_max = max(valores)

        margen_inferior = prom - data_min + 10 if data_min < prom else max(1, prom * 0.2)
        margen_superior = data_max - prom + 1 if data_max > prom else max(1, prom * 0.2)

        ymin = max(0, prom - margen_inferior)
        ymax = prom + margen_superior
    else:
        ymin = min(valores) - 2
        ymax = max(valores) + ((max(valores) - min(valores)) * 0.1)

    # --- Etiquetas eje X ---
    if barras:
        tickvals = df["FECHA TEXTO"].unique().tolist()
        ticktext = tickvals
    else:
        tickvals = fechas_unicas
        ticktext = fechas_unicas.dt.strftime(formato_fecha)

    # --- Graficar ---
    for metrica in metricas:
        df_filtro = df_melted[df_melted["MÉTRICA"] == metrica]
        x_vals = df_filtro[columna_x].tolist()
        y_vals = df_filtro["VALOR"].tolist()

        colores_puntos = []
        tolerancia = 5
        for valor in y_vals:
            if metrica in promedios:
                prom = promedios[metrica]
                if valor >= prom:
                    colores_puntos.append("rgba(0, 200, 0, 0.8)")
                elif abs(valor - prom) <= tolerancia:
                    colores_puntos.append("rgba(255, 215, 0, 0.9)")
                else:
                    colores_puntos.append("rgba(255, 0, 0, 0.8)")
            else:
                colores_puntos.append("gray")

        if barras:
            ancho_barra = 0.1 if len(x_vals) == 1 else 0.3
            fig.add_trace(go.Bar(
                x=x_vals,
                y=y_vals,
                name=util.traducir(metrica, idioma),
                marker_color=colores_puntos,
                width=ancho_barra,
                yaxis="y1",
                text=[f"{v:.2f}" for v in y_vals],
                textposition="inside",
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

        if len(df_filtro) > 1:
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
                bgcolor=color_linea[metrica],
                font=dict(color="white")
            )

    for metrica, valor_prom in promedios.items():
        fig.add_hline(
            y=valor_prom,
            line=dict(color=color_promedio.get(metrica, "gray"), dash="dash"),
            annotation_text=f"{valor_prom:.2f} cm",
            annotation_position="top right",
            annotation=dict(font=dict(color="black", size=12, family="Arial")),
            layer="above"
        )

        title = util.traducir("ALTURA DE SALTO (CM)", idioma)
        promedio = util.traducir("PROMEDIO", idioma)
        categoria_trad = util.traducir(categoria.upper(), idioma)

        fig.add_trace(go.Scatter(
            x=[None], y=[None],
            mode="lines",
            name=f"{title} {promedio} ({categoria_trad} {equipo})".upper(),
            line=dict(color=color_promedio.get(metrica, "gray"), dash="dash")
        ))

    if metricas[0] in df.columns and not df[metricas[0]].isnull().all():
        if promedios and metricas[0] in promedios:
            valor_prom = promedios[metricas[0]]
            rel_promedio = (valor_prom - ymin) / (ymax - ymin)
            colorscale = [
                [0.0, "red"],
                [max(rel_promedio * 0.7, 0.001), "orange"],
                [rel_promedio, "green"],
                [1.0, "green"]
            ]
        else:
            colorscale = [
                [0.0, "red"],
                [0.5, "orange"],
                [0.7, "yellow"],
                [1.0, "green"]
            ]

        fig.add_trace(go.Scatter(
            x=[None], y=[None],
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

    title_layout = "POTENCIA MUSCULAR DE SALTO (CMJ)" if barras else "Evolución de la Potencia Muscular de Salto (CMJ)"
    fig.update_layout(
        title=util.traducir(title_layout, idioma).upper(),
        xaxis=dict(
            tickmode="array",
            tickvals=tickvals,
            ticktext=ticktext,
            type="category" if barras else "date"
        ),
        yaxis=dict(
            title=util.traducir("ALTURA DE SALTO (CM)", idioma),
            range=[ymin, ymax]
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
