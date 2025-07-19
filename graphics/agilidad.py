import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import matplotlib.pyplot as plt
from utils import util
from utils import traslator

AGILITY_SEMAFORO = {
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
    return AGILITY_SEMAFORO.get(genero, {}).get(categoria, AGILITY_SEMAFORO["H"]["juvenil"])


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


def get_agilidad_colorbar_agregada(fig, y_min, y_max, gender, categoria, gradient=True, pdf_mode=False):
    """
    Add Agilidad colorbar using shapes for precise control - INDEPENDENT positioning with PDF support
    """
    escala = get_escala_color_agilidad(gender, categoria)
    
    # PDF-SPECIFIC: Different font sizes for colorbar
    if pdf_mode:
        tick_font_size = 24         
        title_font_size = 28        
    else:
        tick_font_size = 9          
        title_font_size = 10        
    
    tickvals = [round(umbral * 10, 2) for umbral, _ in escala]  # Convert 0.0-1.0 to 0-10%
    ticktext = [str(round(umbral * 10, 1)) for umbral, _ in escala]  # Text labels
 
    # Position it in paper coordinates for consistency
    colorbar_bottom = 0.2  # Fixed bottom position
    colorbar_top = 0.8     # Fixed top position
    colorbar_height = colorbar_top - colorbar_bottom
    
    if gradient:
        gradient_steps = 50  # SAME as working versions
        
        for i in range(len(escala) - 1):
            # Use the original 0.0-1.0 scale for positioning within colorbar
            y_start_norm = escala[i][0]  # 0.0-1.0 
            y_end_norm = escala[i + 1][0]  # 0.0-1.0
            color_start = escala[i][1]
            color_end = escala[i + 1][1]
            
            # Convert to paper coordinates within colorbar area
            y_start_paper = colorbar_bottom + (y_start_norm * colorbar_height)
            y_end_paper = colorbar_bottom + (y_end_norm * colorbar_height)
            
            # Only create gradient if colors are different
            if color_start != color_end:
                # Create gradient steps between current and next color
                for step in range(gradient_steps):
                    y_bottom = y_start_paper + (y_end_paper - y_start_paper) * (step / gradient_steps)
                    y_top = y_start_paper + (y_end_paper - y_start_paper) * ((step + 1) / gradient_steps)
                    
                    # Interpolate between colors
                    ratio = step / gradient_steps
                    interpolated_color = util.interpolate_color(color_start, color_end, ratio)
                    
                    # Add rectangle using PAPER coordinates for both X and Y
                    fig.add_shape(
                        type="rect",
                        x0=1.02, x1=1.04,           
                        y0=y_bottom, y1=y_top + 0.01,  
                        xref="paper", yref="paper",  
                        fillcolor=interpolated_color,
                        line=dict(width=0, color=interpolated_color)
                    )
            else:
                # Same color, create a solid block
                fig.add_shape(
                    type="rect",
                    x0=1.02, x1=1.04,           
                    y0=y_start_paper, y1=y_end_paper,      
                    xref="paper", yref="paper",  
                    fillcolor=color_start,
                    line=dict(width=0)
                )
        
        # Add tick labels using paper coordinates with PDF-aware sizes
        for i, (umbral, _) in enumerate(escala):
            # Convert normalized position to paper coordinates
            y_position_paper = colorbar_bottom + (umbral * colorbar_height)
            label = ticktext[i]
            
            fig.add_annotation(
                x=1.045,                     
                y=y_position_paper,         
                text=f"{label}%",            
                xref="paper",
                yref="paper",                
                showarrow=False,
                font=dict(size=tick_font_size, color="black"),  
                xanchor='left'
            )
        
        # Add title for gradient version with PDF-aware size
        fig.add_annotation(
            x=1.03,                        
            y=0.89,                        
            text="Dif %",                  
            xref="paper",
            yref="paper",                  
            showarrow=False,
            font=dict(size=title_font_size, color="black", family="Arial"), 
            xanchor='center'               
        )
        
    else:
        # SOLID COLORS APPROACH: Same logic with paper coordinates and PDF-aware fonts
        for i in range(len(escala) - 1):
            y_start_norm = escala[i][0]
            y_end_norm = escala[i + 1][0]
            color = escala[i][1]
            
            y_start_paper = colorbar_bottom + (y_start_norm * colorbar_height)
            y_end_paper = colorbar_bottom + (y_end_norm * colorbar_height)
            
            fig.add_shape(
                type="rect",
                x0=1.02, x1=1.04,           
                y0=y_start_paper, y1=y_end_paper,      
                xref="paper", yref="paper",  
                fillcolor=color,
                line=dict(width=0)
            )
        
        # Add tick labels using paper coordinates with PDF-aware sizes
        for i, (umbral, _) in enumerate(escala):
            y_position_paper = colorbar_bottom + (umbral * colorbar_height)
            label = ticktext[i]
            
            fig.add_annotation(
                x=1.045,                     
                y=y_position_paper,
                text=f"{label}%",
                xref="paper",
                yref="paper",                
                showarrow=False,
                font=dict(size=tick_font_size, color="black"),  
                xanchor='left'
            )
        
        # Add title with PDF-aware size
        fig.add_annotation(
            x=1.03,                        
            y=0.89,                        
            text="Dif %",                
            xref="paper",
            yref="paper",                  
            showarrow=False,
            font=dict(size=title_font_size, color="black", family="Arial"),  
            xanchor='center'               
        )
    
    return fig


def get_agility_graph_combined_simple(df_agility, df_promedios, categoria, equipo, 
                                      metricas, columnas_fecha_registro, 
                                      idioma="es", barras=False, cat_label="U19", 
                                      gender="H", gradient_colorbar=True,
                                      pdf_mode=False): 
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

    # PDF-SPECIFIC: Different font sizes for layout
    if pdf_mode:
        title_font_size = 44        
        axis_font_size = 36         
        tick_font_size = 30        
        legend_font_size = 26       
        annotation_font_size = 24   
        margin_left = 160           
        margin_right = 260          
        margin_top = 140            
        margin_bottom = 160         
        legend_y = -0.12            
        bar_text_size = 30          
        circle_text_size = 26       
        circle_size = 65            
    else:
        title_font_size = 16
        axis_font_size = 12
        tick_font_size = 10
        legend_font_size = 12
        annotation_font_size = 11
        margin_left = 50
        margin_right = 100
        margin_top = 60
        margin_bottom = 80
        legend_y = -0.3
        bar_text_size = 20 if len(df) == 1 else 14
        circle_text_size = 20 if len(df) == 1 else 13
        circle_size = 55 if len(df) == 1 else 40

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

    # Calculate Y-axis range for TIME (single axis approach)
    valores_tiempo = []
    for metrica in metricas:
        valores_tiempo += df[metrica].dropna().tolist()

    if valores_tiempo:
        # OUTLIER DETECTION: Remove extreme values (likely data errors)
        # Agility times should typically be 1-10 seconds, anything above 30s is likely an error
        valores_tiempo_filtered = [v for v in valores_tiempo if v <= 30.0]  # Filter extreme outliers
        
        if valores_tiempo_filtered:  # Use filtered values if any remain
            ymin_tiempo = min(valores_tiempo_filtered)
            ymax_tiempo = max(valores_tiempo_filtered)
            
            # FORCE Y-AXIS TO INCLUDE 0: Always start at 0 or below
            ymin_tiempo = min(0, ymin_tiempo)  # Ensure 0 is always visible
            
            # Add reasonable padding (10-20% of range)
            padding = (ymax_tiempo - ymin_tiempo) * 0.15
            ymin_tiempo = min(ymin_tiempo - padding, 0)  # Ensure 0 remains visible
            ymax_tiempo += padding
            
            # Ensure minimum range for readability
            if ymax_tiempo - ymin_tiempo < 1.0:
                ymax_tiempo = max(ymin_tiempo + 1.0, 1.0)
        else:
            # Fallback if all values were outliers
            ymin_tiempo, ymax_tiempo = 0, 10
    else:
        ymin_tiempo, ymax_tiempo = 0, 10

    # === TIME TRACES (Single Y-axis) with DYNAMIC TEXT POSITIONING ===
    for metrica, color, dash in zip(metricas, [color_linea_nd, color_linea_dom], ["solid", "dash"]):
        df_metric = df[[columna_x, columnas_fecha_registro, metrica]].dropna()
        
        # FILTER OUT OUTLIERS from traces too
        df_metric = df_metric[df_metric[metrica] <= 30.0]  # Same filter as Y-axis calculation
        
        x_vals = df_metric[columna_x].tolist()
        y_vals = df_metric[metrica].tolist()

        if barras or len(x_vals) == 1:
            # DYNAMIC TEXT POSITIONING: Same logic as sprint graph
            # Calculate text height based on actual data range
            tiempo_range = ymax_tiempo - ymin_tiempo
            tiempo_text_height = (bar_text_size / 400.0) * tiempo_range
            tiempo_min_height_for_inside = tiempo_text_height * 2.5
            
            # Calculate proper contrast colors and positions for each bar
            text_colors = []
            text_positions = []
            text_angles = []
            
            for i, valor in enumerate(y_vals):
                # Calculate bar height from baseline (ymin_tiempo) to bar top
                bar_height = valor - ymin_tiempo
                
                if bar_height >= tiempo_min_height_for_inside:
                    # Bar is tall enough for inside text
                    text_positions.append("inside")
                    text_colors.append(util.get_contrasting_text_color(color))
                    text_angles.append(-90)  # Vertical text inside
                else:
                    # Bar is too short, place text outside on top
                    text_positions.append("outside")
                    text_colors.append("black")  # Always black when outside
                    text_angles.append(0)  # Horizontal text outside
            
            # Create individual bar traces for proper text positioning
            for i, (x_val, y_val, text_color, text_pos, text_angle) in enumerate(
                zip(x_vals, y_vals, text_colors, text_positions, text_angles)):
                
                fig.add_trace(go.Bar(
                    x=[x_val],
                    y=[y_val],
                    name=traslator.traducir(metrica, idioma) if i == 0 else None,
                    showlegend=(i == 0),
                    marker_color=color,
                    text=f"{y_val:.2f} seg",
                    textposition=text_pos,
                    #textangle=text_angle,
                    textfont=dict(
                        size=bar_text_size,
                        color=text_color,
                        family="Arial"
                    ),
                    hovertemplate=f"<b>Fecha:</b> %{{x}}<br><b>{traslator.traducir(metrica, idioma)}:</b> %{{y:.2f}} seg<extra></extra>"
                ))
        else:
            fig.add_trace(go.Scatter(
                x=x_vals,
                y=y_vals,
                mode="lines+markers",
                name=traslator.traducir(metrica, idioma),
                line=dict(color=color, width=3, dash=dash),
                marker=dict(size=8, color=color),
                hovertemplate=f"<b>Fecha:</b> %{{x}}<br><b>{metrica}:</b> %{{y:.2f}} seg<extra></extra>"
            ))

        # Add min annotations for time with PDF-aware font sizes
        if (not df_metric.empty and len(df_metric) > 1) and not barras:
            min_val = df_metric[metrica].min()
            fila_min = df_metric[df_metric[metrica] == min_val].sort_values(by=columnas_fecha_registro, ascending=False).iloc[0]
            maxl = traslator.traducir("Min ", idioma)
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
                font=dict(color="white", size=annotation_font_size, family="Arial")
            )

    # === DIFFERENCE CIRCLES (positioned properly within range) ===
    added_to_legend = False
    for idx, row in df.iterrows():
        fecha = row[columna_x]
        dom = row.get(metricas[0], None)
        nd = row.get(metricas[1], None)

        # FILTER OUTLIERS in difference calculation too
        if pd.notna(dom) and pd.notna(nd) and nd != 0 and dom <= 30.0 and nd <= 30.0:
            diferencia = (abs(dom - nd) / nd) * 100
            color = calcular_color_diferencia_agilidad(diferencia, gender, categoria)
            
            # FIXED: Position circles ABOVE the highest visible value, within Y-axis range
            max_visible_value = max([v for v in [dom, nd] if v <= 30.0])
            y_position = min(ymax_tiempo * 0.85, max_visible_value + (ymax_tiempo - ymin_tiempo) * 0.1)
            
            diferenciat = traslator.traducir("DIFERENCIA %", idioma)
            fig.add_trace(go.Scatter(
                x=[fecha],
                y=[y_position],  # Positioned within visible range
                mode="markers+text",
                marker=dict(size=circle_size, color=color, opacity=0.9),
                text=f"{diferencia:.1f}%",
                textfont=dict(size=circle_text_size, color="black"),
                textposition="middle center",
                showlegend=not added_to_legend,
                name=f"{diferenciat} ({cat_label})",
                hoverinfo="skip"
            ))
            added_to_legend = True

    tickvals = df["FECHA TEXTO"].drop_duplicates().tolist()
    ticktext = tickvals

    title_layout = "AGILIDAD (Pierna Izquierda y Pierna Derecha)" if barras else "Evolución de la Agilidad (Pierna Izquierda y Pierna Derecha)"
    
    # === LAYOUT with SINGLE Y-AXIS (like original) with PDF-aware fonts ===
    fig.update_layout(
        title=dict(
            text=traslator.traducir(title_layout, idioma).upper(),
            font=dict(size=title_font_size, family="Arial", color="#1f2937"),  # PDF-aware size
            x=0.5,
            xanchor="center"
        ),
        xaxis=dict(
            title=dict(
                text=traslator.traducir("FECHA", idioma) if not barras else None,
                font=dict(size=axis_font_size, family="Arial")  # PDF-aware size
            ),
            tickmode="array",
            tickvals=tickvals,
            ticktext=ticktext,
            tickfont=dict(size=tick_font_size, family="Arial"),  # PDF-aware size
            type="category",
            showticklabels=not barras
        ),
        yaxis=dict(
            title=dict(
                text=traslator.traducir("TIEMPO (SEG)", idioma),
                font=dict(size=axis_font_size, family="Arial")  # PDF-aware size
            ),
            tickfont=dict(size=tick_font_size, family="Arial"),  # PDF-aware size
            range=[ymin_tiempo, ymax_tiempo],  # FIXED: Ensure 0 is always visible
            dtick=None,  # Let Plotly auto-calculate ticks to ensure 0 is shown
            tick0=0,     # FORCE 0 to be a tick mark
            side="left"
        ),
        template="plotly_white",
        barmode="group" if barras or len(df) == 1 else "overlay",
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=legend_y,  # PDF-aware position
            xanchor="center",
            x=0.5,
            font=dict(size=legend_font_size, family="Arial")  # PDF-aware size
        ),
        margin=dict(l=margin_left, r=margin_right, t=margin_top, b=margin_bottom)  # PDF-aware margins
    )

    # === ADD INDEPENDENT COLORBAR (not linked to any axis) with PDF support ===
    fig = get_agilidad_colorbar_agregada(fig, 0, 10,  # Fixed 0-10% range
                                         gender, categoria,
                                         gradient=gradient_colorbar,
                                         pdf_mode=pdf_mode)  # Pass PDF mode

    # Only display in app, not PDF
    if not pdf_mode:
        st.plotly_chart(fig, use_container_width=True)
    
    return fig

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
            name=traslator.traducir(metrica,idioma),
            line=dict(color=color, width=3, dash=dash),
            marker=dict(size=8, color=color),
            hovertemplate=f"<b>Fecha:</b> %{{x|%d-%m-%Y}}<br><b>{metrica}:</b> %{{y:.2f}} seg<extra></extra>"
        ))

        # Mejor registro
        if not df_metric.empty:
            min_val = df_metric[metrica].min()
            fila_min = df_metric[df_metric[metrica] == min_val].sort_values(by=columnas_fecha_registro, ascending=False).iloc[0]
            maxl = traslator.traducir("Max",idioma)
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
                name=traslator.traducir("DIFERENCIA %",idioma),
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
        title=traslator.traducir("Evolución de la Agilidad (IZQ y DER)", idioma),
        xaxis=dict(
            tickmode="array",
            tickvals=tickvals,
            ticktext=ticktext
        ),
        yaxis=dict(
            title=traslator.traducir("TIEMPO (SEG)", idioma),
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

