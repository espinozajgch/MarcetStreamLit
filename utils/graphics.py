
import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import matplotlib.pyplot as plt
from utils import util

def get_height_graph(df_altura):
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
        fig.add_annotation(
            x=fila_max["FECHA REGISTRO"],
            y=fila_max["ALTURA (CM)"],
            text=f"Max: {fila_max['ALTURA (CM)']:.1f} cm",
            showarrow=True,
            arrowhead=2,
            ax=0,
            ay=-30,
            bgcolor="#12527c",
            font=dict(color="white")
        )

    fig.update_layout(
        title="📏 Evolución de la Altura (cm)",
        xaxis_title=None,
        yaxis_title="Altura (cm)",
        template="plotly_white",
        xaxis=dict(
            tickmode="array",
            tickvals=tickvals,
            ticktext=ticktext
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

def get_anthropometrics_graph(df_antropometria, categoria, zona_optima_min, zona_optima_max):

    df = pd.DataFrame(df_antropometria)
    df["FECHA REGISTRO"] = pd.to_datetime(df["FECHA REGISTRO"], format="%d/%m/%Y")
    df = df.sort_values(by="FECHA REGISTRO")

    metricas = ["PESO (KG)", "GRASA (%)"]
    df = df[["FECHA REGISTRO"] + metricas]

    # --- Definir etiquetas personalizadas de eje X ---
    df_fechas_unicas = df["FECHA REGISTRO"].drop_duplicates().sort_values()
    años_unicos = df_fechas_unicas.dt.year.unique()

    if len(años_unicos) == 1:
        tickvals = df_fechas_unicas
        ticktext = df_fechas_unicas.dt.strftime("%b")
    else:
        tickvals = df_fechas_unicas
        ticktext = df_fechas_unicas.dt.strftime("%b-%Y")

    grasa_min = df_antropometria["GRASA (%)"].min()
    grasa_max = df_antropometria["GRASA (%)"].max()
    dif_zona_optima_min = zona_optima_min - grasa_min
    dif_zona_optima_max = grasa_max - zona_optima_max
    #st.text(f"Zona óptima: {dif_zona_optima_min} - {dif_zona_optima_max} %")
    
    if(dif_zona_optima_min < 2 and dif_zona_optima_max < 2):
        cmin = zona_optima_min - 5
        cmax = zona_optima_max + 5
    elif(dif_zona_optima_min < 2 and dif_zona_optima_max > 2):
        cmin = zona_optima_min - dif_zona_optima_max - 2
        cmax = grasa_max + 2
    elif(dif_zona_optima_min > 2 and dif_zona_optima_max < 2):
        cmin = grasa_min - 2
        cmax = zona_optima_max + dif_zona_optima_min + 2
    else:
        cmin = grasa_min - 2
        cmax = grasa_max

    color_lineas = {
        "PESO (KG)": "#66c2ff",
        "GRASA (%)": "#12527c"
    }

    fig = go.Figure()

    # Asegurar que la barra de peso se vea si hay un solo registro
    if len(df) == 1:
        new_row = {
            "FECHA REGISTRO": df["FECHA REGISTRO"].iloc[0] + pd.Timedelta(days=1),
            "PESO (KG)": None,
            "GRASA (%)": None
        }
        df = pd.concat([df, pd.DataFrame([new_row])], ignore_index=True)

    # --- PESO como barra (eje izquierdo) ---
    if "PESO (KG)" in df.columns:
        fig.add_trace(go.Bar(
            x=df["FECHA REGISTRO"],
            y=df["PESO (KG)"],
            name="PESO (KG)",
            marker_color=color_lineas["PESO (KG)"],
            text=df["PESO (KG)"].round(1),
            textposition="inside",
            yaxis="y1",
            hovertemplate=(
                "<b>Fecha:</b> %{x|%d-%m-%Y}<br>"
                "<b>PESO (KG):</b> %{y:.1f} kg<extra></extra>"
            )
        ))

    # --- GRASA como línea con puntos coloreados (eje derecho) ---
    if "GRASA (%)" in df.columns:
        x_vals = df["FECHA REGISTRO"]
        y_vals = df["GRASA (%)"]
        colores_puntos = []

        for valor in y_vals:
            if 11 <= valor <= 12.5:
                colores_puntos.append("green")
            elif 9 <= valor < 11 or 12.5 < valor <= 14:
                colores_puntos.append("orange")
            else:
                colores_puntos.append("red")

        fig.add_trace(go.Scatter(
            x=x_vals,
            y=y_vals,
            mode="lines+markers",
            name="GRASA (%)",
            line=dict(color="gray", width=3),
            marker=dict(color=colores_puntos, size=10),
            yaxis="y2",
            hovertemplate="<b>Fecha:</b> %{x|%d-%m-%Y}<br><b>GRASA (%):</b> %{y:.2f} %<extra></extra>"
        ))

        # Anotar máximo
        df_filtro = df[["FECHA REGISTRO", "GRASA (%)"]].dropna()
        if not df_filtro.empty:
            max_valor = df_filtro["GRASA (%)"].max()
            fila_max = df_filtro[df_filtro["GRASA (%)"] == max_valor].sort_values(by="FECHA REGISTRO", ascending=False).iloc[0]

            fig.add_annotation(
                x=fila_max["FECHA REGISTRO"],
                y=fila_max["GRASA (%)"],
                yref="y2",
                text=f"Max: {fila_max['GRASA (%)']:.1f} %",
                showarrow=True,
                arrowhead=2,
                ax=0,
                ay=30,
                bgcolor=color_lineas["GRASA (%)"],
                font=dict(color="white")
            )

            # Líneas discontinuas para zona óptima (en y2)
            x_min = df["FECHA REGISTRO"].min() - pd.Timedelta(days=15)
            x_max = df["FECHA REGISTRO"].max() + pd.Timedelta(days=15)

            fig.add_trace(go.Scatter(
                x=[x_min, x_max],
                y=[12.5, 12.5],
                mode="lines",
                name="",
                line=dict(color="green", dash="dash"),
                yaxis="y2",
                showlegend=False
            ))
            fig.add_annotation(
                x=x_min,
                y=12.5,
                yref="y2",
                text="",
                showarrow=False,
                font=dict(size=11, color="black"),
                xanchor="left",
                yanchor="top"
            )

            fig.add_trace(go.Scatter(
                x=[x_min, x_max],
                y=[11, 11],
                mode="lines",
                name="",
                line=dict(color="green", dash="dash"),
                yaxis="y2",
                showlegend=False
            ))
            fig.add_annotation(
                x=x_min,
                y=11,
                yref="y2",
                text="",
                showarrow=False,
                font=dict(size=11, color="black"),
                xanchor="left",
                yanchor="bottom"
            )

            # Línea discontinua visible en leyenda
            fig.add_trace(go.Scatter(
                x=[None], y=[None],
                mode="lines",
                name=f"Zona %Grasa Promedio {categoria} A",
                line=dict(color="green", dash="dash"),
                yaxis="y2"
            ))

    # --- Barra de color (sin usar yaxis="y2" para evitar error de Kaleido) ---
    if "GRASA (%)" in df.columns and not df["GRASA (%)"].isnull().all():
        fig.add_trace(go.Heatmap(
            z=[[0]],  # dummy heatmap
            x=[df["FECHA REGISTRO"].min()],
            y=[(cmin + cmax) / 2],
            colorscale=[
                [0.0, "red"],
                [0.35, "orange"],
                [0.5, "green"],
                [0.65, "orange"],
                [1.0, "red"]
            ],
            zmin=cmin,
            zmax=cmax,
            showscale=True,
            colorbar=dict(
                title="% Grasa",
                titleside="right",
                orientation="v",
                y=-0.02,
                yanchor="bottom",
                len=1.05,
                lenmode="fraction",
                x=1.03,
                xanchor="left",
                thickness=20,
                #showticklabels=False,
                tickfont=dict(color="white"),
                titlefont=dict(color="gray")
            ),
            hoverinfo="skip"
        ))

    # --- Layout final con dos ejes ---
    fig.update_layout(
        title="⚖️ Evolución del Peso y % Grasa",
        xaxis=dict(
            tickformat="%b",     # Mantén esto si quieres seguir usando el formato base (mes)
            dtick="M1",          # Mantén esto si quieres controlar cada mes
            tickmode="array",    # Usamos arreglo para mostrar solo meses relevantes
            tickvals=tickvals,
            ticktext=ticktext
        ),
        yaxis=dict(
            title="Peso (kg)",
            side="left"
        ),
        yaxis2=dict(
            title="",
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
            name=f"{metrica} PROMEDIO",
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

def get_cmj_graph(df_cmj, df_promedios_cmj, categoria, equipo):
    df = pd.DataFrame(df_cmj)
    df["FECHA REGISTRO"] = pd.to_datetime(df["FECHA REGISTRO"], format="%d/%m/%Y")
    df = df.sort_values(by="FECHA REGISTRO")

    metricas = ["CMJ (CM)"]
    df = df[["FECHA REGISTRO"] + metricas]

    color_linea = {"CMJ (CM)": "#163B5B"}
    color_promedio = {"CMJ (CM)": "green"}

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

    df_melted = df.melt(id_vars=["FECHA REGISTRO"], value_vars=metricas,
                        var_name="MÉTRICA", value_name="VALOR").dropna()

    fig = go.Figure()
    tolerancia = 5

    # --- Calcular rango del eje Y incluyendo el promedio ---
    valores = df_melted["VALOR"].tolist()
    if promedios:
        for valor_prom in promedios.values():
            valores.append(valor_prom)

    ymin = min(valores) - 2  # margen inferior fijo
    ymax = max(valores) + ((max(valores) - min(valores)) * 0.1)  # margen superior dinámico

    # --- Etiquetas personalizadas del eje X ---
    df_fechas_unicas = df["FECHA REGISTRO"].drop_duplicates().sort_values()
    años_unicos = df_fechas_unicas.dt.year.unique()

    if len(años_unicos) == 1:
        tickvals = df_fechas_unicas
        ticktext = df_fechas_unicas.dt.strftime("%b")
    else:
        tickvals = df_fechas_unicas
        ticktext = df_fechas_unicas.dt.strftime("%b-%Y")

    # --- Graficar la métrica principal ---
    for metrica in metricas:
        df_filtro = df_melted[df_melted["MÉTRICA"] == metrica]
        x_vals = df_filtro["FECHA REGISTRO"].tolist()
        y_vals = df_filtro["VALOR"].tolist()

        # Línea
        fig.add_trace(go.Scatter(
            x=x_vals,
            y=y_vals,
            mode="lines",
            name=metrica,
            line=dict(color=color_linea[metrica], width=3),
            hoverinfo="skip"
        ))

        # Puntos coloreados (semáforo)
        colores_puntos = []
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

        fig.add_trace(go.Scatter(
            x=x_vals,
            y=y_vals,
            mode="markers",
            name=metrica,
            showlegend=False,
            marker=dict(size=10, color=colores_puntos),
            hovertemplate=f"<b>Fecha:</b> %{{x|%d-%m-%Y}}<br><b>{metrica}:</b> %{{y:.2f}} cm<extra></extra>"
        ))

        # Máximo más reciente
        if not df_filtro.empty:
            max_val = df_filtro["VALOR"].max()
            fila_max = df_filtro[df_filtro["VALOR"] == max_val].sort_values(by="FECHA REGISTRO", ascending=False).iloc[0]
            fig.add_annotation(
                x=fila_max["FECHA REGISTRO"],
                y=fila_max["VALOR"],
                text=f"Max: {fila_max['VALOR']:.2f} {metrica}",
                showarrow=True,
                arrowhead=2,
                ax=0,
                ay=-30,
                bgcolor=color_linea[metrica],
                font=dict(color="white")
            )

    # Línea de promedio
    for metrica, valor_prom in promedios.items():
        fig.add_hline(
            y=valor_prom,
            line=dict(color=color_promedio.get(metrica, "gray"), dash="dash"),
            annotation_text=f"{valor_prom:.2f} cm",
            annotation_position="top left",
            annotation=dict(font=dict(color="black", size=12, family="Arial"))
        )
        fig.add_trace(go.Scatter(
            x=[None], y=[None],
            mode="lines",
            name=f"ALTURA DE SALTO PROMEDIO (CM) ({categoria} A)",
            line=dict(color="green", dash="dash")
        ))

    # ➕ Barra de color sincronizada con el eje Y y el promedio
    if "CMJ (CM)" in df.columns and not df["CMJ (CM)"].isnull().all():
        if promedios and "CMJ (CM)" in promedios:
            valor_prom = promedios["CMJ (CM)"]
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
                    titleside="right",
                    ticks="outside",
                    tickfont=dict(color="black"),
                    titlefont=dict(color="black"),
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

    # --- Layout final ---
    fig.update_layout(
        title="📈 Evolución de la Potencia Muscular de Salto (CMJ)",
        xaxis=dict(
            tickmode="array",
            tickvals=tickvals,
            ticktext=ticktext
        ),
        yaxis=dict(
            title="ALTURA DE SALTO (CM)",
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

    st.plotly_chart(fig, use_container_width=True)
    return fig

def get_yoyo_graph(df_yoyo, df_promedios_yoyo, categoria, equipo):
    col1, col2 = st.columns([1, 3])

    with col1:
        # Selector de Tipo de Test
        test_type_list = df_yoyo["TEST"].dropna().unique()
        test_type_list.sort()
        selected_test = st.selectbox("Selecciona el tipo de test:", test_type_list)

    df = pd.DataFrame(df_yoyo)
    df["FECHA REGISTRO"] = pd.to_datetime(df["FECHA REGISTRO"], format="%d/%m/%Y", errors='coerce')
    df = df[df["TEST"] == selected_test]

    metrica = "ACCUMULATED SHUTTLE DISTANCE (M)"
    if metrica not in df.columns:
        st.warning("No hay datos de distancia acumulada para mostrar.")
        return

    df = df[["FECHA REGISTRO", metrica]].dropna()
    df = df.sort_values("FECHA REGISTRO")

    # Obtener promedio
    promedio_row = df_promedios_yoyo[
        (df_promedios_yoyo["CATEGORIA"] == categoria) &
        (df_promedios_yoyo["EQUIPO"] == equipo)
    ]
    valor_prom = promedio_row[metrica].values[0] if not promedio_row.empty and metrica in promedio_row.columns else None

    # Calcular rango del eje Y incluyendo el promedio
    valores = df[metrica].tolist()
    if valor_prom is not None and not pd.isna(valor_prom):
        valores.append(valor_prom)

    ymin = min(valores) - 10
    ymax = max(valores) + (max(valores) - min(valores)) * 0.1

    # Etiquetas personalizadas del eje X
    df_fechas_unicas = df["FECHA REGISTRO"].drop_duplicates().sort_values()
    años_unicos = df_fechas_unicas.dt.year.unique()

    if len(años_unicos) == 1:
        tickvals = df_fechas_unicas
        ticktext = df_fechas_unicas.dt.strftime("%b")
    else:
        tickvals = df_fechas_unicas
        ticktext = df_fechas_unicas.dt.strftime("%b-%Y")

    # Colorear puntos según comparación con el promedio
    colores_puntos = []
    tolerancia = 5  # Ajustable
    for valor in df[metrica]:
        if valor_prom is not None and not pd.isna(valor_prom):
            if valor >= valor_prom:
                colores_puntos.append("rgba(0, 200, 0, 0.8)")  # Verde
            elif abs(valor - valor_prom) <= tolerancia:
                colores_puntos.append("rgba(255, 215, 0, 0.9)")  # Amarillo
            else:
                colores_puntos.append("rgba(255, 0, 0, 0.8)")  # Rojo
        else:
            colores_puntos.append("gray")

    # Crear figura
    fig = go.Figure()

    # Línea principal
    fig.add_trace(go.Scatter(
        x=df["FECHA REGISTRO"],
        y=df[metrica],
        mode="lines",
        name="DISTANCIA ACUMULADA (M)",
        line=dict(color="#1f77b4", width=3)
    ))

    # Puntos
    fig.add_trace(go.Scatter(
        x=df["FECHA REGISTRO"],
        y=df[metrica],
        mode="markers",
        name="",
        marker=dict(size=10, color=colores_puntos, line=dict(width=0)),
        showlegend=False,
        hovertemplate=f"<b>Fecha:</b> %{{x|%d-%m-%Y}}<br><b>Valor:</b> %{{y:.2f}}<extra></extra>"
    ))

    # Línea de promedio
    if valor_prom is not None and not pd.isna(valor_prom):
        fig.add_hline(
            y=valor_prom,
            line=dict(color="orange", dash="dash"),
            annotation_text=f"{valor_prom:.2f} m",
            annotation_position="top left",
            annotation=dict(font=dict(color="black", size=12, family="Arial"))
        )
        fig.add_trace(go.Scatter(
            x=[None], y=[None],
            mode="lines",
            name=f"DISTANCIA PROMEDIO (M) ({categoria} {equipo})",
            line=dict(color="orange", dash="dash")
        ))

    # Máximo (más reciente)
    if not df.empty:
        max_valor = df[metrica].max()
        fila_max = df[df[metrica] == max_valor].sort_values("FECHA REGISTRO", ascending=False).iloc[0]
        fig.add_annotation(
            x=fila_max["FECHA REGISTRO"],
            y=fila_max[metrica],
            text=f"Max: {fila_max[metrica]:.0f} (M)",
            showarrow=True,
            arrowhead=2,
            ax=0,
            ay=-30,
            bgcolor="#1f77b4",
            font=dict(color="white")
        )

    # Barra de color sincronizada con el eje Y y el promedio
    if valor_prom is not None and not pd.isna(valor_prom):
        rel_promedio = (valor_prom - ymin) / (ymax - ymin)
        colorscale = [
            [0.0, "red"],
            [max(rel_promedio * 0.7, 0.001), "orange"],  # gradual hasta el promedio
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
                titleside="right",
                ticks="outside",
                tickfont=dict(color="black"),
                titlefont=dict(color="black"),
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

    # Layout final
    fig.update_layout(
        title="📈 Evolución de la Distancia Acumulada",
        xaxis=dict(
            tickmode="array",
            tickvals=tickvals,
            ticktext=ticktext
        ),
        yaxis=dict(
            title="DISTANCIA ACUMULADA (M)",
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
                name=f"{nombre_legenda} PROMEDIO",
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

def get_sprint_velocity_graph(df_sprint, df_promedios, categoria, equipo):
    df = df_sprint.copy()
    df["FECHA REGISTRO"] = pd.to_datetime(df["FECHA REGISTRO"], format="%d/%m/%Y", errors='coerce')
    df = df.sort_values(by="FECHA REGISTRO")

    metricas_originales = ["VEL 0-5M (M/S)", "VEL 20-40M (M/S)"]
    metricas_convertidas = ["VEL 0-5M (KM/H)", "VEL 20-40M (KM/H)"]
    colores_lineas = {
        "VEL 0-5M (KM/H)": "#1f77b4",
        "VEL 20-40M (KM/H)": "#66c2ff"
    }
    colores_promedios = {
        "VEL 0-5M (KM/H)": "orange",
        "VEL 20-40M (KM/H)": "purple"
    }
    tolerancia = 0.5

    # Obtener promedios
    promedio_row = df_promedios[
        (df_promedios["CATEGORIA"] == categoria) &
        (df_promedios["EQUIPO"] == equipo)
    ]
    promedios = {}
    if not promedio_row.empty:
        for original, nueva in zip(metricas_originales, metricas_convertidas):
            if original in promedio_row.columns:
                valor = promedio_row[original].values[0]
                if pd.notna(valor):
                    promedios[nueva] = valor * 3.6

    fig = go.Figure()

    for metrica in metricas_convertidas:
        df_metric = df[["FECHA REGISTRO", metrica]].dropna()
        x_vals = df_metric["FECHA REGISTRO"].tolist()
        y_vals = df_metric[metrica].tolist()
        color_linea = colores_lineas.get(metrica, "gray")
        color_prom = colores_promedios.get(metrica, "gray")
        nombre_legenda = metrica.replace(" (KM/H)", "")

        # Puntos coloreados
        colores_puntos = []
        for valor in y_vals:
            if metrica in promedios:
                prom = promedios[metrica]
                if abs(valor - prom) <= tolerancia:
                    colores_puntos.append("rgba(255, 215, 0, 0.9)")
                elif valor > prom:
                    colores_puntos.append("rgba(0, 200, 0, 0.8)")
                else:
                    colores_puntos.append("rgba(255, 0, 0, 0.8)")
            else:
                colores_puntos.append(color_linea)

        # Línea base
        fig.add_trace(go.Scatter(
            x=x_vals,
            y=y_vals,
            mode="lines",
            name=nombre_legenda,
            line=dict(color=color_linea, width=3),
            showlegend=True
        ))

        # Puntos
        fig.add_trace(go.Scatter(
            x=x_vals,
            y=y_vals,
            mode="markers",
            name=nombre_legenda,
            showlegend=False,
            marker=dict(size=10, color=colores_puntos),
            hovertemplate=f"<b>Fecha:</b> %{{x|%d-%m-%Y}}<br><b>{nombre_legenda}:</b> %{{y:.2f}} km/h<extra></extra>"
        ))

        # Anotar máximo
        if not df_metric.empty:
            max_val = df_metric[metrica].max()
            fila_max = df_metric[df_metric[metrica] == max_val].sort_values(by="FECHA REGISTRO", ascending=False).iloc[0]
            fig.add_annotation(
                x=fila_max["FECHA REGISTRO"],
                y=fila_max[metrica],
                text=f"Mejor Registro: {fila_max[metrica]:.2f} km/h",
                showarrow=True,
                arrowhead=2,
                ax=0,
                ay=-30,
                bgcolor=color_linea,
                font=dict(color="white")
            )

        # Línea de promedio
        if metrica in promedios:
            prom = promedios[metrica]
            fig.add_hline(
                y=prom,
                line=dict(color=color_prom, dash="dash"),
                annotation_text=f"Promedio ({categoria} {equipo}): {prom:.2f} km/h",
                annotation_position="top right",
                annotation=dict(font=dict(color="black", size=12, family="Arial"))
            )
            fig.add_trace(go.Scatter(
                x=[None], y=[None],
                mode="lines",
                name=f"{nombre_legenda} PROMEDIO",
                line=dict(color=color_prom, dash="dash")
            ))

    fig.update_layout(
        title="📈 Evolución de la Velocidad del Sprint 40m (KM/H)",
        xaxis_title=None,
        yaxis_title="Velocidad (km/h)",
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

def get_rsa_graph(df_rsa, df_promedios_rsa, categoria, equipo):
    df = pd.DataFrame(df_rsa)
    df["FECHA REGISTRO"] = pd.to_datetime(df["FECHA REGISTRO"], format="%d/%m/%Y")
    df = df.sort_values(by="FECHA REGISTRO")

    metricas = ["MEDIDA EN TIEMPO (SEG)", "VELOCIDAD (M*SEG)"]
    df = df[["FECHA REGISTRO"] + metricas]

    # Obtener promedios
    promedio_row = df_promedios_rsa[
        (df_promedios_rsa["CATEGORIA"] == categoria) &
        (df_promedios_rsa["EQUIPO"] == equipo)
    ]

    promedios = {}
    if not promedio_row.empty:
        for metrica in metricas:
            if metrica in promedio_row.columns:
                valor = promedio_row[metrica].values[0]
                if pd.notna(valor):
                    promedios[metrica] = valor
    else:
        st.warning("No se encontraron promedios RSA para esta categoría y equipo.")

    # 1️⃣ GRÁFICO DE LÍNEAS PARA TIEMPO
    fig_tiempo = go.Figure()

    y_vals = df["MEDIDA EN TIEMPO (SEG)"].tolist()
    x_vals = df["FECHA REGISTRO"].tolist()

    color_linea = "#1f77b4"
    prom = promedios.get("MEDIDA EN TIEMPO (SEG)", None)
    tolerancia = 1.5
    colores_puntos = []

    for val in y_vals:
        if prom is not None and not pd.isna(prom):
            if val < (prom - tolerancia):
                colores_puntos.append("rgba(0, 200, 0, 0.8)")  # Verde (menorual)
            elif abs(val - prom) <= tolerancia:
                colores_puntos.append("rgba(255, 215, 0, 0.9)")  # Amarillo (cercano)
            else:
                colores_puntos.append("rgba(255, 0, 0, 0.8)")    # Rojo (peor)
        else:
            colores_puntos.append(color_linea)

    # Calcular rango del eje Y incluyendo el promedio
    valores = y_vals.copy()
    if prom is not None and not pd.isna(prom):
        valores.append(prom)

    ymin = min(valores) - 0.5
    ymax = max(valores) + ((max(valores) - min(valores)) * 0.1)

    # Etiquetas personalizadas del eje X
    df_fechas_unicas = df["FECHA REGISTRO"].drop_duplicates().sort_values()
    años_unicos = df_fechas_unicas.dt.year.unique()

    if len(años_unicos) == 1:
        tickvals = df_fechas_unicas
        ticktext = df_fechas_unicas.dt.strftime("%b")
    else:
        tickvals = df_fechas_unicas
        ticktext = df_fechas_unicas.dt.strftime("%b-%Y")

    # Línea
    fig_tiempo.add_trace(go.Scatter(
        x=x_vals,
        y=y_vals,
        mode="lines",
        name="MEDIDA EN TIEMPO",
        line=dict(color=color_linea, width=3)
    ))

    # Puntos
    fig_tiempo.add_trace(go.Scatter(
        x=x_vals,
        y=y_vals,
        mode="markers",
        name="",
        marker=dict(size=10, color=colores_puntos),
        showlegend=False,
        hovertemplate="<b>Fecha:</b> %{x|%d-%m-%Y}<br><b>Tiempo:</b> %{y:.2f} seg<extra></extra>"
    ))

    # Línea de promedio
    if prom is not None and not pd.isna(prom):
        fig_tiempo.add_hline(
            y=prom,
            line=dict(color="orange", dash="dash"),
            annotation_text=f"{prom:.2f} seg",
            annotation_position="top left",
            annotation=dict(font=dict(color="black", size=12))
        )
        fig_tiempo.add_trace(go.Scatter(
            x=[None], y=[None],
            mode="lines",
            name=f"TIEMPO PROMEDIO (SEG) ({categoria} {equipo})",
            line=dict(color="orange", dash="dash")
        ))

    # Anotación de mejor registro (menor tiempo)
    df_max = df[df["MEDIDA EN TIEMPO (SEG)"] == min(y_vals)].sort_values(by="FECHA REGISTRO", ascending=False)
    if not df_max.empty:
        fila = df_max.iloc[0]
        fig_tiempo.add_annotation(
            x=fila["FECHA REGISTRO"],
            y=fila["MEDIDA EN TIEMPO (SEG)"],
            text=f"Mejor Registro: {fila['MEDIDA EN TIEMPO (SEG)']:.2f} seg",
            showarrow=True,
            arrowhead=2,
            ax=0,
            ay=-30,
            bgcolor=color_linea,
            font=dict(color="white")
        )

    # Barra de color sincronizada con el eje Y y promedio
    if prom is not None and not pd.isna(prom):
        rel_promedio = (prom - ymin) / (ymax - ymin)
        colorscale = [
            [0.0, "green"],  # Verde para mejores registros (menor tiempo)
            [rel_promedio * 0.7, "yellow"],
            [rel_promedio, "orange"],
            [1.0, "red"]     # Rojo para peores registros (mayor tiempo)
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
                titleside="right",
                ticks="outside",
                tickfont=dict(color="black"),
                titlefont=dict(color="black"),
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

    # Layout final
    fig_tiempo.update_layout(
        title="📈 Evolución del Tiempo Total en Repeticiones de Sprint",
        xaxis=dict(
            tickmode="array",
            tickvals=tickvals,
            ticktext=ticktext
        ),
        yaxis=dict(
            title="Tiempo (Seg)",
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

def get_rsa_velocity_graph(df_rsa, df_promedios_rsa, categoria, equipo):
    df = df_rsa.copy()
    df["FECHA REGISTRO"] = pd.to_datetime(df["FECHA REGISTRO"], format="%d/%m/%Y", errors="coerce")
    df = df.sort_values(by="FECHA REGISTRO")

    # Convertir m/seg a km/h
    df["VELOCIDAD (KM/H)"] = df["VELOCIDAD (M*SEG)"] * 3.6
    metric = "VELOCIDAD (KM/H)"

    # Obtener promedio y convertir a km/h también
    promedio_row = df_promedios_rsa[
        (df_promedios_rsa["CATEGORIA"] == categoria) &
        (df_promedios_rsa["EQUIPO"] == equipo)
    ]

    prom = None
    if not promedio_row.empty and "VELOCIDAD (M*SEG)" in promedio_row.columns:
        prom = promedio_row["VELOCIDAD (M*SEG)"].values[0] * 3.6
    else:
        st.warning("No se encontraron promedios de Velocidad para esta categoría y equipo.")

    # Crear figura
    fig = go.Figure()
    tolerancia = 0.3 * 3.6

    color_linea = "#66c2ff"
    color_promedio = "orange"

    y_vals = df[metric].tolist()
    x_vals = df["FECHA REGISTRO"].tolist()

    # Colorear puntos
    colores_puntos = []
    for valor in y_vals:
        if prom is not None and not pd.isna(prom):
            if valor >= prom:
                colores_puntos.append("rgba(0, 200, 0, 0.8)")  # Verde
            elif abs(valor - prom) <= tolerancia:
                colores_puntos.append("rgba(255, 215, 0, 0.9)")  # Amarillo
            else:
                colores_puntos.append("rgba(255, 0, 0, 0.8)")  # Rojo
        else:
            colores_puntos.append(color_linea)

    # Rango del eje Y
    valores = y_vals.copy()
    if prom is not None and not pd.isna(prom):
        valores.append(prom)
    ymin = min(valores) - 1
    ymax = max(valores) + ((max(valores) - min(valores)) * 0.1)

    # Etiquetas personalizadas del eje X
    df_fechas_unicas = df["FECHA REGISTRO"].drop_duplicates().sort_values()
    años_unicos = df_fechas_unicas.dt.year.unique()

    if len(años_unicos) == 1:
        tickvals = df_fechas_unicas
        ticktext = df_fechas_unicas.dt.strftime("%b")
    else:
        tickvals = df_fechas_unicas
        ticktext = df_fechas_unicas.dt.strftime("%b-%Y")

    # Línea base
    fig.add_trace(go.Scatter(
        x=x_vals,
        y=y_vals,
        mode="lines",
        name=metric,
        line=dict(color=color_linea, width=3),
        showlegend=True
    ))

    # Puntos
    fig.add_trace(go.Scatter(
        x=x_vals,
        y=y_vals,
        mode="markers",
        marker=dict(size=10, color=colores_puntos, line=dict(width=0)),
        name=metric,
        showlegend=False,
        hovertemplate="<b>Fecha:</b> %{x|%d-%m-%Y}<br><b>Velocidad:</b> %{y:.2f} km/h<extra></extra>"
    ))

    # Línea de promedio
    if prom is not None and not pd.isna(prom):
        fig.add_hline(
            y=prom,
            line=dict(color=color_promedio, dash="dash"),
            annotation_text=f"{prom:.2f} km/h",
            annotation=dict(font=dict(color="black", size=12))
        )
        fig.add_trace(go.Scatter(
            x=[None], y=[None],
            mode="lines",
            name=f"VELOCIDAD PROMEDIO (KM/H) ({categoria} {equipo})",
            line=dict(color=color_promedio, dash="dash")
        ))

    # Anotación del máximo
    df_filtro = df[["FECHA REGISTRO", metric]].dropna()
    if not df_filtro.empty:
        max_valor = df_filtro[metric].max()
        fila_max = df_filtro[df_filtro[metric] == max_valor].sort_values(by="FECHA REGISTRO", ascending=False).iloc[0]

        fig.add_annotation(
            x=fila_max["FECHA REGISTRO"],
            y=fila_max[metric],
            text=f"Mejor Registro: {fila_max[metric]:.2f} km/h",
            showarrow=True,
            arrowhead=2,
            ax=0,
            ay=-30,
            bgcolor=color_linea,
            font=dict(color="white")
        )

    # Barra de color sincronizada con el eje Y y promedio
    if prom is not None and not pd.isna(prom):
        rel_promedio = (prom - ymin) / (ymax - ymin)
        colorscale = [
            [0.0, "red"],
            [rel_promedio * 0.7, "orange"],
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
                titleside="right",
                ticks="outside",
                tickfont=dict(color="black"),
                titlefont=dict(color="black"),
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

    # Layout final
    fig.update_layout(
        title="📈 Evolución de la Velocidad en Repeticiones de Sprint",
        yaxis=dict(
            title="Velocidad (km/h)",
            range=[ymin, ymax]
        ),
        xaxis=dict(
            tickmode="array",
            tickvals=tickvals,
            ticktext=ticktext
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

def get_agility_graph_combined(df_agility, df_promedios, categoria, equipo):

    df = pd.DataFrame(df_agility)
    df["FECHA REGISTRO"] = pd.to_datetime(df["FECHA REGISTRO"], format="%d/%m/%Y", errors="coerce")
    df = df.sort_values(by="FECHA REGISTRO")

    metricas = ["505-DOM (SEG)", "505-ND (SEG)"]

    color_linea_dom = "#1f77b4"   # azul
    color_linea_nd = "#66c2ff"    # celeste
    color_promedio = "orange"

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

    # --- Trazas de las piernas ---
    for metrica, color, dash in zip(
        ["505-ND (SEG)", "505-DOM (SEG)"], [color_linea_nd, color_linea_dom], ["solid", "dash"]
    ):
        df_metric = df[["FECHA REGISTRO", metrica]].dropna()
        x_vals = df_metric["FECHA REGISTRO"].tolist()
        y_vals = df_metric[metrica].tolist()

        fig.add_trace(go.Scatter(
            x=x_vals,
            y=y_vals,
            mode="lines+markers",
            name=metrica,
            line=dict(color=color, width=3, dash=dash),
            marker=dict(size=8, color=color),
            hovertemplate=f"<b>Fecha:</b> %{{x|%d-%m-%Y}}<br><b>{metrica}:</b> %{{y:.2f}} seg<extra></extra>"
        ))

        # Mejor registro
        if not df_metric.empty:
            min_val = df_metric[metrica].min()
            fila_min = df_metric[df_metric[metrica] == min_val].sort_values(by="FECHA REGISTRO", ascending=False).iloc[0]
            fig.add_annotation(
                x=fila_min["FECHA REGISTRO"],
                y=fila_min[metrica],
                text=f"Mejor Registro: {fila_min[metrica]:.2f} seg",
                showarrow=True,
                arrowhead=2,
                ax=0,
                ay=-30,
                bgcolor=color,
                font=dict(color="white")
            )

        # Línea de promedio
        if metrica in promedios:
            prom = promedios[metrica]
            fig.add_hline(
                y=prom,
                line=dict(color=color_promedio, dash="dash"),
                annotation_text=f"Promedio ({metrica}): {prom:.2f} seg",
                annotation_position="top right",
                annotation=dict(font=dict(color="black", size=12, family="Arial"))
            )
            fig.add_trace(go.Scatter(
                x=[None], y=[None],
                mode="lines",
                name=f"{metrica} PROMEDIO",
                line=dict(color=color_promedio, dash="dash")
            ))

    # --- Calcular y marcar % diferencia (DOM vs ND) ---
    for idx, row in df.iterrows():
        fecha = row["FECHA REGISTRO"]
        dom = row.get("505-DOM (SEG)")
        nd = row.get("505-ND (SEG)")
        if pd.notna(dom) and pd.notna(nd) and nd != 0:
            diferencia = ((dom - nd) / nd) * 100
            fig.add_trace(go.Scatter(
                x=[fecha],
                y=[max(dom, nd) + 0.1],  # posición vertical un poco arriba
                mode="markers+text",
                marker=dict(size=15, color="orange", opacity=0.7),
                text=f"{diferencia:.1f}%",
                textposition="top center",
                showlegend=False,
                hoverinfo="skip"
            ))

    # --- Layout final ---
    fig.update_layout(
        title="📈 Evolución de la Agilidad (DOM y ND)",
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
