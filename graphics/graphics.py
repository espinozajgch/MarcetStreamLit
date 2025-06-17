
import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import matplotlib.pyplot as plt
from utils import util

def get_height_graph(df_altura, idioma="es", barras=False):
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
        maxl = util.traducir("Max",idioma)
        fig.add_annotation(
            x=fila_max["FECHA REGISTRO"],
            y=fila_max["ALTURA (CM)"],
            text=f"{maxl}: {fila_max['ALTURA (CM)']:.1f} cm",
            showarrow=True,
            arrowhead=2,
            ax=0,
            ay=-30,
            bgcolor="gray",
            font=dict(color="white")
        )

    title_layout = "ALTURA (CM)" if barras else "Evolución de la Altura (cm)"
    fig.update_layout(
        title=util.traducir(title_layout, idioma).upper(),
        xaxis_title=None,
        yaxis_title=util.traducir("ALTURA (CM)", idioma),
        template="plotly_white",
        xaxis=dict(
            tickmode="array",
            tickvals=tickvals,
            ticktext=ticktext,
            showticklabels=not barras
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

def get_anthropometrics_graph(df_antropometria, categoria, zona_optima_min, zona_optima_max, idioma="es", barras=False):
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

    # --- Ajuste de rango para cmin y cmax (grasa) ---
    grasa_min = df["GRASA (%)"].min()
    grasa_max = df["GRASA (%)"].max()

    cmin = min(3, grasa_min - 1 if grasa_min < 3 else grasa_min)
    cmax = max(25, grasa_max + 1 if grasa_max > 25 else grasa_max)

    if cmax - cmin < 5:
        cmax = cmin + 5

    color_lineas = {
        "PESO (KG)": "#2989d2",
        "GRASA (%)": "#12527c"
    }

    fig = go.Figure()

    if len(df) == 1:
        new_row = {
            "FECHA REGISTRO": df["FECHA REGISTRO"].iloc[0] + pd.Timedelta(days=5),
            "PESO (KG)": None,
            "GRASA (%)": None
        }
        df = pd.concat([df, pd.DataFrame([new_row])], ignore_index=True)

    # --- PESO como barra ---
    if "PESO (KG)" in df.columns:
        fig.add_trace(go.Bar(
            x=df["FECHA REGISTRO"],
            y=df["PESO (KG)"],
            name=util.traducir("PESO (KG)", idioma),
            marker_color=color_lineas["PESO (KG)"],
            text=df["PESO (KG)"].round(1),
            textposition="inside",
            textfont=dict(size=14),
            yaxis="y1",
            hovertemplate="<b>Fecha:</b> %{x|%d-%m-%Y}<br><b>PESO (KG):</b> %{y:.1f} kg<extra></extra>"
        ))

    # --- GRASA como línea con puntos coloreados ---
    if "GRASA (%)" in df.columns:
        x_vals = df["FECHA REGISTRO"]
        y_vals = df["GRASA (%)"]
        colores_puntos = []

        for valor in y_vals:
            if valor >= 25 or 20 <= valor < 21 or 22 <= valor < 23 or 3 <= valor <= 5:
                colores_puntos.append("#FF0000")  # Rojo
            elif 18 <= valor < 20 or 6 <= valor < 7:
                colores_puntos.append("#FFA500")  # Naranja
            elif 16 <= valor < 18 or 7 <= valor < 8:
                colores_puntos.append("#FFFF00")  # Amarillo
            elif 14 <= valor < 16 or 8 <= valor < 10:
                colores_puntos.append("#006400")  # Verde Oscuro
            elif 10 <= valor < 14:
                colores_puntos.append("#7CFC00")  # Verde Manzana
            else:
                colores_puntos.append("gray")

        fig.add_trace(go.Scatter(
            x=x_vals,
            y=y_vals,
            mode="lines+markers",
            name=util.traducir("GRASA (%)", idioma),
            line=dict(color="gray", width=3),
            marker=dict(color=colores_puntos, size=10),
            yaxis="y2",
            hovertemplate="<b>Fecha:</b> %{x|%d-%m-%Y}<br><b>GRASA (%):</b> %{y:.2f} %<extra></extra>"
        ))

        df_filtro = df[["FECHA REGISTRO", "GRASA (%)"]].dropna()
        if not df_filtro.empty:
            max_valor = df_filtro["GRASA (%)"].max()
            fila_max = df_filtro[df_filtro["GRASA (%)"] == max_valor].sort_values(by="FECHA REGISTRO", ascending=False).iloc[0]
            fig.add_annotation(
                x=fila_max["FECHA REGISTRO"],
                y=fila_max["GRASA (%)"],
                yref="y2",
                text=f"{util.traducir('Max', idioma)}: {fila_max['GRASA (%)']:.1f} %",
                showarrow=True,
                arrowhead=2,
                ax=0,
                ay=30,
                bgcolor="gray",
                font=dict(size=14,color="white")
            )

            x_min = df["FECHA REGISTRO"].min() - pd.Timedelta(days=15)
            x_max = df["FECHA REGISTRO"].max() + pd.Timedelta(days=15)

            fig.add_trace(go.Scatter(x=[x_min, x_max], y=[zona_optima_max, zona_optima_max], mode="lines",
                                     line=dict(color="green", dash="dash"), yaxis="y2", showlegend=False))
            fig.add_annotation(x=x_min, y=zona_optima_max, yref="y2", text=zona_optima_max,
                               showarrow=False, font=dict(size=11), xanchor="left", yanchor="bottom")

            fig.add_trace(go.Scatter(x=[x_min, x_max], y=[zona_optima_min, zona_optima_min], mode="lines",
                                     line=dict(color="green", dash="dash"), yaxis="y2", showlegend=False))
            fig.add_annotation(x=x_min, y=zona_optima_min, yref="y2", text=zona_optima_min,
                               showarrow=False, font=dict(size=11), xanchor="left", yanchor="top")

            namel = util.traducir('Zona Optima', idioma)
            cat = util.traducir(categoria.upper(), idioma)
            prom  = util.traducir("PROMEDIO", idioma)
            fig.add_trace(go.Scatter(
                x=[None], y=[None],
                mode="lines",
                name=f"{namel} ({prom} {cat} A)".upper(),
                line=dict(color="green", dash="dash"),
                yaxis="y2"
            ))

    # --- Barra de color para GRASA (%) ---
    if "GRASA (%)" in df.columns and not df["GRASA (%)"].isnull().all():
        fig.add_trace(go.Heatmap(
            z=[[0]],
            x=[df["FECHA REGISTRO"].min()],
            y=[(cmin + cmax) / 2],
            colorscale=[
                [(3 - cmin)/(cmax - cmin), "#FF0000"],     # Rojo
                [(6 - cmin)/(cmax - cmin), "#FFA500"],     # Naranja
                [(7 - cmin)/(cmax - cmin), "#FFFF00"],     # Amarillo
                [(8 - cmin)/(cmax - cmin), "#006400"],     # Verde Oscuro
                [(10 - cmin)/(cmax - cmin), "#7CFC00"],    # Verde Manzana
                [(14 - cmin)/(cmax - cmin), "#006400"],    # Verde Oscuro
                [(16 - cmin)/(cmax - cmin), "#FFFF00"],    # Amarillo
                [(18 - cmin)/(cmax - cmin), "#FFA500"],    # Naranja
                [(20 - cmin)/(cmax - cmin), "#FF0000"],    # Rojo
                [(25 - cmin)/(cmax - cmin), "#FF0000"],    # Rojo
            ],
            zmin=cmin,
            zmax=cmax,
            showscale=True,
            colorbar=dict(
                title=dict(text=util.traducir("GRASA (%)", idioma), side="right"),
                orientation="v",
                y=-0.02,
                yanchor="bottom",
                len=1.05,
                lenmode="fraction",
                x=1.03,
                xanchor="left",
                thickness=20,
                tickfont=dict(color="white"),
            ),
            hoverinfo="skip"
        ))

    title_layout = "PESO Y % GRASA" if barras else "Evolución del Peso y % Grasa"

    fig.update_layout(
        title=util.traducir(title_layout, idioma).upper(),
        xaxis=dict(
            tickformat="%b",
            dtick="M1",
            tickmode="array",
            tickvals=tickvals,
            ticktext=ticktext,
            showticklabels=not barras
        ),
        yaxis=dict(
            title=util.traducir("PESO (KG)", idioma),
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
