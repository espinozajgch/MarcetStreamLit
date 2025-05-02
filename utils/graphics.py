
import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import matplotlib.pyplot as plt
from utils import util

def get_anthropometrics_graph(df_antropometria, df_promedios, categoria, equipo):
    df = pd.DataFrame(df_antropometria)
    df["FECHA REGISTRO"] = pd.to_datetime(df["FECHA REGISTRO"], format="%d/%m/%Y")
    df = df.sort_values(by="FECHA REGISTRO")

    metricas = ["PESO (KG)", "GRASA (%)"]
    df = df[["FECHA REGISTRO"] + metricas]

    # Colores de líneas del jugador
    color_lineas = {
        "PESO (KG)": "#1f77b4",  # Azul oscuro
        "GRASA (%)": "#66c2ff"   # Azul claro
    }

    # Colores de líneas de promedio
    color_promedios = {
        "PESO (KG)": "purple",
        "GRASA (%)": "orange"
    }

    # Obtener promedios
    promedio_row = df_promedios[
        (df_promedios["CATEGORIA"] == categoria) &
        (df_promedios["EQUIPO"] == equipo)
    ]

    promedios = {}
    if not promedio_row.empty:
        for metrica in metricas:
            if metrica in promedio_row.columns:
                valor = promedio_row[metrica].values[0]
                if pd.notna(valor):
                    promedios[metrica] = valor
    else:
        st.warning("No se encontraron promedios para la categoría y equipo especificados.")

    # Crear figura
    fig = go.Figure()
    tolerancia = 0.5

    for metrica in metricas:
        if metrica not in df.columns:
            continue

        y_vals = df[metrica].tolist()
        x_vals = df["FECHA REGISTRO"].tolist()

        colores_puntos = []
        for valor in y_vals:
            if metrica in promedios:
                prom = promedios[metrica]
                if abs(valor - prom) <= tolerancia:
                    colores_puntos.append("rgba(255, 215, 0, 0.9)")  # Amarillo
                else:
                    if metrica == "GRASA (%)":
                        colores_puntos.append(
                            "rgba(0, 200, 0, 0.8)" if valor < prom else "rgba(255, 0, 0, 0.8)"
                        )
                    else:  # PESO (KG) y otros
                        colores_puntos.append(
                            "rgba(0, 200, 0, 0.8)" if valor > prom else "rgba(255, 0, 0, 0.8)"
                        )
            else:
                colores_puntos.append(color_lineas[metrica])

        # Línea (sin puntos) → aparece en la leyenda
        fig.add_trace(go.Scatter(
            x=x_vals,
            y=y_vals,
            mode="lines",
            name=metrica,
            line=dict(color=color_lineas[metrica], width=3),
            showlegend=True
        ))

        # Puntos coloreados → NO aparece en la leyenda
        fig.add_trace(go.Scatter(
            x=x_vals,
            y=y_vals,
            mode="markers",
            name=metrica,
            marker=dict(size=10, color=colores_puntos, line=dict(width=0)),
            showlegend=False,
            hovertemplate=f"<b>Fecha:</b> %{{x|%d-%m-%Y}}<br><b>Métrica:</b> {metrica}<br><b>Valor:</b> %{{y:.2f}}<extra></extra>"
        ))

        # Anotar máximo (más reciente en caso de empate)
        df_filtro = df[["FECHA REGISTRO", metrica]].dropna()
        if not df_filtro.empty:
            max_valor = df_filtro[metrica].max()
            fila_max = df_filtro[df_filtro[metrica] == max_valor].sort_values(by="FECHA REGISTRO", ascending=False).iloc[0]

            color_fondo = color_lineas.get(metrica, "gray")
            texto = f"Max: {fila_max[metrica]:.1f} {metrica}" if fila_max[metrica] > 0 else f"{fila_max[metrica]:.1f} {metrica}"

            fig.add_annotation(
                x=fila_max["FECHA REGISTRO"],
                y=fila_max[metrica],
                text=texto,
                showarrow=True,
                arrowhead=2,
                ax=0,
                ay=-30,
                bgcolor=color_fondo,
                font=dict(color="white")
            )

    # Añadir líneas de promedio
    for metrica, valor_prom in promedios.items():
        fig.add_hline(
            y=valor_prom,
            line=dict(color=color_promedios[metrica], dash="dash"),
            annotation_text=f"Promedio ({categoria} {equipo}): {valor_prom:.1f}",
            annotation_position="top left",
            annotation=dict(font=dict(color="black", size=12, family="Arial"))
        )
        fig.add_trace(go.Scatter(
            x=[None], y=[None],
            mode="lines",
            name=f"{metrica} PROMEDIO",
            line=dict(color=color_promedios[metrica], dash="dash")
        ))

    fig.update_layout(
        title="📈 Evolución de las Medidas Antropométricas",
        xaxis_title=None,
        yaxis_title="MEDIDAS",
        #legend_title="MÉTRICA",
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
    import pandas as pd
    import plotly.graph_objects as go
    import streamlit as st

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

    # Colores personalizados
    color_linea = {"CMJ (CM)": "#1f77b4"}       # Azul oscuro
    color_promedio = {"CMJ (CM)": "orange"}

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

    # Preparar figura manualmente
    fig = go.Figure()
    tolerancia = 0.5

    for metrica in metricas:
        df_filtro = df_melted[df_melted["MÉTRICA"] == metrica]
        x_vals = df_filtro["FECHA REGISTRO"].tolist()
        y_vals = df_filtro["VALOR"].tolist()

        # 1️⃣ Línea con leyenda
        fig.add_trace(go.Scatter(
            x=x_vals,
            y=y_vals,
            mode="lines",
            name=metrica,
            line=dict(color=color_linea[metrica], width=3),
            hoverinfo="skip"
        ))

        # 2️⃣ Puntos coloreados sin leyenda
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
                colores_puntos.append("gray")

        fig.add_trace(go.Scatter(
            x=x_vals,
            y=y_vals,
            mode="markers",
            name=metrica,
            showlegend=False,
            marker=dict(size=10, color=colores_puntos),
            hovertemplate=f"<b>Fecha:</b> %{{x|%d-%m-%Y}}<br><b>Métrica:</b> {metrica}<br><b>Valor:</b> %{{y:.2f}}<extra></extra>"
        ))

        # Máximo más reciente
        if not df_filtro.empty:
            max_val = df_filtro["VALOR"].max()
            fila_max = df_filtro[df_filtro["VALOR"] == max_val].sort_values(by="FECHA REGISTRO", ascending=False).iloc[0]

            fig.add_annotation(
                x=fila_max["FECHA REGISTRO"],
                y=fila_max["VALOR"],
                text=f"Max: {fila_max['VALOR']:.1f} {metrica}",
                showarrow=True,
                arrowhead=2,
                ax=0,
                ay=-30,
                bgcolor=color_linea[metrica],
                font=dict(color="white")
            )

    # Promedio
    for metrica, valor_prom in promedios.items():
        fig.add_hline(
            y=valor_prom,
            line=dict(color=color_promedio.get(metrica, "gray"), dash="dash"),
            annotation_text=f"Promedio ({categoria} {equipo}): {valor:.2f} (cm)",
            annotation_position="top left",
            annotation=dict(font=dict(color="black", size=12, family="Arial"))
        )
        fig.add_trace(go.Scatter(
            x=[None], y=[None],
            mode="lines",
            name="ALTURA DE SALTO PROMEDIO (CM)",
            line=dict(color="orange", dash="dash")
        ))

    fig.update_layout(
        title="📈 Evolución de la Potencia Muscular de Salto (CMJ)",
        xaxis_title=None,
        yaxis_title="ALTURA DE SALTO (CM)",
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

    # Colorear puntos según comparación con el promedio
    colores_puntos = []
    tolerancia = 10
    for valor in df[metrica]:
        if valor_prom is not None:
            if abs(valor - valor_prom) <= tolerancia:
                colores_puntos.append("rgba(255, 215, 0, 0.9)")   # dorado
            elif valor > valor_prom:
                colores_puntos.append("rgba(0, 200, 0, 0.8)")     # verde
            else:
                colores_puntos.append("rgba(255, 0, 0, 0.8)")     # rojo
        else:
            colores_puntos.append("blue")

    # Crear figura
    fig = go.Figure()

    # Línea
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
    if valor_prom is not None:
        fig.add_hline(
            y=valor_prom,
            line=dict(color="orange", dash="dash"),
            annotation_text=f"Promedio ({categoria} {equipo}): {valor_prom:.2f}",
            annotation_position="top left",
            #annotation_font=dict(color="orange"),
            annotation=dict(font=dict(color="black", size=12, family="Arial"))
        )
        fig.add_trace(go.Scatter(
            x=[None], y=[None],
            mode="lines",
            name="DISTANCIA PROMEDIO (M)",
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

    # Eje X por mes
    fig.update_layout(
        title="📈 Evolución de la Distancia Acumulada",
        xaxis_title="FECHA",
        yaxis_title="DISTANCIA ACUMULADA (M)",
        xaxis=dict(tickformat="%b", dtick="M1"),
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

    color_linea = "#1f77b4"  # Azul
    prom = promedios.get("MEDIDA EN TIEMPO (SEG)", None)
    tolerancia = 0.1
    colores_puntos = []

    for val in y_vals:
        if prom is not None:
            if abs(val - prom) <= tolerancia:
                colores_puntos.append("rgba(255, 215, 0, 0.9)")
            elif val < prom:
                colores_puntos.append("rgba(0, 200, 0, 0.8)")
            else:
                colores_puntos.append("rgba(255, 0, 0, 0.8)")
        else:
            colores_puntos.append(color_linea)

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
    if prom is not None:
        fig_tiempo.add_hline(
            y=prom,
            line=dict(color="orange", dash="dash"),
            annotation_text=f"Promedio ({categoria} {equipo}): {prom:.2f}",
            annotation_position="top left",
            annotation=dict(font=dict(color="black", size=12))
        )

        # Agregar a la leyenda
        fig_tiempo.add_trace(go.Scatter(
            x=[None], y=[None],
            mode="lines",
            name="TIEMPO PROMEDIO (SEG)",
            line=dict(color="orange", dash="dash")
        ))

    # Anotación de máximo más reciente
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

    fig_tiempo.update_layout(
        title="📈 Evolución del Tiempo Total en Repeticiones de Sprint",
        xaxis_title="Fecha",
        yaxis_title="Tiempo (Seg)",
        xaxis=dict(
            tickformat="%b",  # Mostrar mes abreviado
            dtick="M1",
            title=None
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

    promedios = {}
    if not promedio_row.empty and "VELOCIDAD (M*SEG)" in promedio_row.columns:
        prom = promedio_row["VELOCIDAD (M*SEG)"].values[0] * 3.6
        if pd.notna(prom):
            promedios[metric] = prom
    else:
        prom = None

    # Crear figura
    fig = go.Figure()
    tolerancia = 0.2 * 3.6  # adaptar tolerancia al nuevo rango

    color_linea = "#66c2ff"
    color_promedio = "orange"

    y_vals = df[metric].tolist()
    x_vals = df["FECHA REGISTRO"].tolist()

    colores_puntos = []
    for valor in y_vals:
        if metric in promedios:
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

    # Línea de promedio
    if prom is not None:
        fig.add_hline(
            y=prom,
            line=dict(color=color_promedio, dash="dash"),
            annotation_text=f"Promedio ({categoria} {equipo}): {prom:.2f} km/h",
            annotation=dict(font=dict(color="black", size=12))
        )
        fig.add_trace(go.Scatter(
            x=[None], y=[None],
            mode="lines",
            name="VELOCIDAD PROMEDIO (KM/H)",
            line=dict(color=color_promedio, dash="dash")
        ))

    fig.update_layout(
        title="📈 Evolución de la Velocidad en Repeticiones de Sprint",
        yaxis_title="Velocidad (km/h)",
        xaxis=dict(
            tickformat="%b",
            dtick="M1",
            title=None
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

import matplotlib.pyplot as plt

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
