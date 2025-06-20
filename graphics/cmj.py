import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import matplotlib.pyplot as plt
from utils import util

def get_cmj_graph(df_cmj, df_promedios_cmj, categoria, equipo, metricas, columna_fecha_registro, idioma="es", barras=False):
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
    valores = df_melted["VALOR"].tolist() + list(promedios.values())

    # --- Rango dinámico con base entre 20-50 ---
    cmj_min = min(valores)
    cmj_max = max(valores)
    cmin = min(15, cmj_min - 1 if cmj_min < 20 else cmj_min)
    cmax = max(50, cmj_max + 1 if cmj_max > 50 else cmj_max)
    if cmax - cmin < 10:
        cmax = cmin + 10

    tickvals = df["FECHA TEXTO"].unique().tolist() if barras else fechas_unicas
    ticktext = tickvals if barras else fechas_unicas.dt.strftime(formato_fecha)

    es_cadete = "cadete" in categoria.lower()

    for metrica in metricas:
        df_filtro = df_melted[df_melted["MÉTRICA"] == metrica]
        x_vals = df_filtro[columna_x].tolist()
        y_vals = df_filtro["VALOR"].tolist()

        colores_puntos = []

        for valor in y_vals:
            if pd.isna(valor):
                colores_puntos.append("gray")
                continue

            if es_cadete:
                if valor > 33:
                    colores_puntos.append("#7CFC00")  # Verde Manzana
                elif 30 <= valor <= 33:
                    colores_puntos.append("#006400")  # Verde Oscuro
                elif 27 <= valor < 30:
                    colores_puntos.append("#FFFF00")  # Amarillo
                elif 25 <= valor < 27:
                    colores_puntos.append("#FFA500")  # Naranja
                elif valor < 25:
                    colores_puntos.append("#FF0000")  # Rojo
                else:
                    colores_puntos.append("gray")
            else:  # Juvenil
                if valor > 39:
                    colores_puntos.append("#7CFC00")  # Verde Manzana
                elif 35 <= valor <= 38:
                    colores_puntos.append("#006400")  # Verde Oscuro
                elif 33 <= valor < 35:
                    colores_puntos.append("#FFFF00")  # Amarillo
                elif 31 <= valor < 33:
                    colores_puntos.append("#FFA500")  # Naranja
                elif valor < 31:
                    colores_puntos.append("#FF0000")  # Rojo
                else:
                    colores_puntos.append("gray")


        if barras:
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

        if len(df_filtro) > 1 or not barras:
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
            name=f"{util.traducir('ALTURA OPTIMA', idioma)} ({util.traducir('PROMEDIO', idioma)} {util.traducir(categoria.upper(), idioma)} {equipo})".upper(),
            line=dict(color=color_promedio.get(metrica, "gray"), dash="dash")
        ))

    # --- Colorbar lateral según categoría ---
    if es_cadete:
        colorscale = [
            [(15 - cmin) / (cmax - cmin), "#FF0000"],
            [(24 - cmin) / (cmax - cmin), "#FF0000"],
            [(25 - cmin) / (cmax - cmin), "#FFA500"],
            [(26 - cmin) / (cmax - cmin), "#FFA500"],
            [(27 - cmin) / (cmax - cmin), "#FFFF00"],
            [(29 - cmin) / (cmax - cmin), "#FFFF00"],
            [(30 - cmin) / (cmax - cmin), "#006400"],
            [(32 - cmin) / (cmax - cmin), "#006400"],
            [(33 - cmin) / (cmax - cmin), "#7CFC00"],
            [(50 - cmin) / (cmax - cmin), "#7CFC00"]
        ]
    else:
        colorscale = [
            [(15 - cmin) / (cmax - cmin), "#FF0000"],
            [(30 - cmin) / (cmax - cmin), "#FF0000"],
            [(31 - cmin) / (cmax - cmin), "#FFA500"],
            [(32 - cmin) / (cmax - cmin), "#FFA500"],
            [(33 - cmin) / (cmax - cmin), "#FFFF00"],
            [(34 - cmin) / (cmax - cmin), "#FFFF00"],
            [(35 - cmin) / (cmax - cmin), "#006400"],
            [(38 - cmin) / (cmax - cmin), "#006400"],
            [(39 - cmin) / (cmax - cmin), "#7CFC00"],
            [(50 - cmin) / (cmax - cmin), "#7CFC00"]
        ]

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
            showticklabels=not barras
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
