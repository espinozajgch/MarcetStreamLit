import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import matplotlib.pyplot as plt
from utils import util
from utils import traslator

SPRINT_SEMAFORO = {
    "H": {
        "juvenil": {
            "rango": (4.4, 6.3),
            "escala_colores": [
                [0.0, "#7CFC00"],
                [0.35, "#006400"],
                [0.55, "#FFD700"],
                [0.75, "#FFA500"],
                [1.0, "#FF4500"]
            ]
        },
        "cadete": {
            "rango": (4.6, 6.5),
            "escala_colores": [
                [0.0, "#7CFC00"],
                [0.35, "#006400"],
                [0.55, "#FFD700"],
                [0.75, "#FFA500"],
                [1.0, "#FF4500"]
            ]
        }
    },
    "M": {
        "juvenil": {
            "rango": (5.5, 7.0),
            "escala_colores": [
                [0.0, "#7CFC00"],   # Verde Manzana
                [0.53, "#006400"],  # Verde Oscuro (6.3 → (6.3-5.5)/1.5 ≈ 0.53)
                [0.6, "#FFD700"],   # Amarillo (6.4)
                [0.67, "#FFA500"],  # Naranja (6.5)
                [1.0, "#FF4500"]    # Rojo (>7)
            ]
        },
        "cadete": {
            "rango": (6.0, 7.0),
            "escala_colores": [
                [0.0, "#7CFC00"],   # Verde Manzana
                [0.5, "#006400"],   # Verde Oscuro
                [0.6, "#FFD700"],   # Amarillo
                [0.7, "#FFA500"],   # Naranja
                [1.0, "#FF4500"]    # Rojo
            ]
        }
    }
}


def get_sprint_color_scale(gender, categoria):
    """Get sprint color scale from existing SPRINT_SEMAFORO structure"""
    config = SPRINT_SEMAFORO.get(gender.upper(), {}).get(categoria.lower(), {})
    if not config:
        return []
    
    # Extract range and color scale from existing structure
    rango = config.get("rango", (0, 10))
    escala_colores = config.get("escala_colores", [])
    
    # Convert to threshold-color pairs
    thresholds = []
    for ratio, color in escala_colores:
        # Convert ratio to actual value based on range
        valor = rango[0] + (rango[1] - rango[0]) * ratio
        thresholds.append((valor, color))
    
    return thresholds

def asignar_color_sprint(valor, gender, categoria):
    """Assign color based on sprint time using existing structure"""
    if pd.isna(valor):
        return "gray"
    
    config = SPRINT_SEMAFORO.get(gender.upper(), {}).get(categoria.lower(), {})
    if not config:
        return "gray"
    
    rango = config.get("rango", (0, 10))
    escala_colores = config.get("escala_colores", [])
    
    if not escala_colores:
        return "gray"
    
    # Normalize value to 0-1 range
    if rango[1] - rango[0] == 0:
        normalized = 0
    else:
        normalized = (valor - rango[0]) / (rango[1] - rango[0])
        normalized = max(0, min(1, normalized))  # Clamp to 0-1
    
    # Find appropriate color based on normalized position
    for i, (ratio, color) in enumerate(escala_colores):
        if normalized <= ratio:
            return color
    
    # If beyond all ratios, return last color
    return escala_colores[-1][1] if escala_colores else "gray"


def get_sprint_colorbar_agregada(fig, y_min, y_max, gender, 
                                 categoria, gradient=True, pdf_mode=False):
    """
    Add Sprint colorbar using existing SPRINT_SEMAFORO structure
    """
    config = SPRINT_SEMAFORO.get(gender.upper(), {}).get(categoria.lower(), {})
    if not config:
        return fig
    
    rango = config.get("rango", (y_min, y_max))
    escala_colores = config.get("escala_colores", [])
    
    if not escala_colores:
        return fig

    # PDF-SPECIFIC: Different font sizes for colorbar
    if pdf_mode:
        tick_font_size = 16      
        title_font_size = 20     
    else:
        tick_font_size = 9       
        title_font_size = 10     
    
    # Convert ratios to actual values for colorbar
    colorbar_scale = []
    for ratio, color in escala_colores:
        valor = rango[0] + (rango[1] - rango[0]) * ratio
        colorbar_scale.append((valor, color))
    
    if gradient:
        gradient_steps = 50
        
        for i in range(len(colorbar_scale) - 1):
            y_start = colorbar_scale[i][0]
            y_end = colorbar_scale[i + 1][0]
            color_start = colorbar_scale[i][1]
            color_end = colorbar_scale[i + 1][1]
            
            if color_start != color_end:
                for step in range(gradient_steps):
                    y_bottom = y_start + (y_end - y_start) * (step / gradient_steps)
                    y_top = y_start + (y_end - y_start) * ((step + 1) / gradient_steps)
                    
                    ratio = step / gradient_steps
                    interpolated_color = util.interpolate_color(color_start, color_end, ratio)
                    
                    fig.add_shape(
                        type="rect",
                        x0=1.05, x1=1.07,
                        y0=y_bottom, y1=y_top + 0.01,
                        xref="paper", yref="y",
                        fillcolor=interpolated_color,
                        line=dict(width=0, color=interpolated_color)
                    )
            else:
                fig.add_shape(
                    type="rect",
                    x0=1.05, x1=1.07,
                    y0=y_start, y1=y_end,
                    xref="paper", yref="y",
                    fillcolor=color_start,
                    line=dict(width=0)
                )
        
        # Add tick labels with PDF-aware sizes
        for valor, _ in colorbar_scale:
            fig.add_annotation(
                x=1.075,
                y=valor,
                text=f"{valor:.2f}",
                xref="paper",
                yref="y",
                showarrow=False,
                font=dict(size=tick_font_size, color="black"),
                xanchor='left'
            )
        
        # Add title with PDF-aware size
        fig.add_annotation(
            x=1.057,
            y=1.08,
            text="Tiempo (s)",
            xref="paper",
            yref="paper",
            showarrow=False,
            font=dict(size=title_font_size, color="black", family="Arial"),
            xanchor='center'
        )
        
    else:
        # Solid colors approach
        num_segments = len(colorbar_scale) - 1
        
        for i in range(num_segments):
            y_bottom = colorbar_scale[i][0]
            y_top = colorbar_scale[i + 1][0] if i < num_segments - 1 else y_max
            color = colorbar_scale[i][1]
            
            fig.add_shape(
                type="rect",
                x0=1.05, x1=1.07,
                y0=y_bottom, y1=y_top,
                xref="paper", yref="y",
                fillcolor=color,
                line=dict(width=0)
            )
        
        # Add tick labels with PDF-aware sizes
        for valor, _ in colorbar_scale:
            fig.add_annotation(
                x=1.075,
                y=valor,
                text=f"{valor:.2f}",
                xref="paper",
                yref="y",
                showarrow=False,
                font=dict(size=tick_font_size, color="black"),
                xanchor='left'
            )
        
        # Add title with PDF-aware size
        fig.add_annotation(
            x=1.057,
            y=1.08,
            text="Tiempo (s)",
            xref="paper",
            yref="paper",
            showarrow=False,
            font=dict(size=title_font_size, color="black", family="Arial"),
            xanchor='center'
        )
    
    return fig

def get_sprint_graph(
    df_sprint,
    promedio_row,
    categoria,
    equipo,
    metrica_tiempo,
    metrica_velocidad,
    columnas_fecha_registro,
    idioma="es",
    barras=False,
    cat_label="U19",
    gender="H",
    gradient_colorbar=True,
    pdf_mode=False  
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
    else:
        # App display (keep original)
        title_font_size = 16
        axis_font_size = 12
        tick_font_size = 10
        legend_font_size = 12
        annotation_font_size = 11
        margin_left = 50
        margin_right = 130
        margin_top = 60
        margin_bottom = 80
        legend_y = -0.3
        bar_text_size = 20 if len(df) == 1 else 14

    # The text height should be proportional to the actual data range, not just font size
    data_range = y_max - y_min if 'y_max' in locals() and 'y_min' in locals() else 1.0
    estimated_text_height = (bar_text_size / 400.0) * data_range  # More realistic conversion
    min_bar_height_for_inside = estimated_text_height * 3.0  # More generous safety margin

    # === VELOCIDAD (Secondary Y-axis) ===
    cols_vel = [columnas_fecha_registro, metrica_velocidad]
    if columnas_fecha_registro != columna_x:
        cols_vel.insert(1, columna_x)
    df_metric_vel = df[cols_vel].dropna()

    if not df_metric_vel.empty:
        # Calculate velocidad range for better text height estimation
        vel_min = 0  # Velocidad starts from 0
        vel_max = df_metric_vel[metrica_velocidad].max()
        vel_range = vel_max - vel_min
        
        # Recalculate text height for velocidad based on its data range
        vel_text_height = (bar_text_size / 400.0) * vel_range
        vel_min_height_for_inside = vel_text_height * 2.5
        
        if barras or len(df_metric_vel[metrica_velocidad]) == 1:
            # Calculate dynamic text positioning for velocidad bars
            text_colors_vel = []
            text_positions_vel = []
            text_angles_vel = []
            
            vel_values = df_metric_vel[metrica_velocidad].tolist()
            
            for valor in vel_values:
                bar_height = valor  # Since velocidad starts from 0, this is the actual height
                
                if bar_height >= vel_min_height_for_inside:
                    text_positions_vel.append("inside")
                    text_colors_vel.append("white")  # White on blue bars
                    text_angles_vel.append(-90)
                else:
                    text_positions_vel.append("outside")
                    text_colors_vel.append("black")
                    text_angles_vel.append(0)
            
            # Create individual velocidad bar traces
            for i, (x_val, y_val, text_color, text_pos, text_angle) in enumerate(
                zip(df_metric_vel[columna_x], vel_values, 
                    text_colors_vel, text_positions_vel, text_angles_vel)):
                
                fig.add_trace(go.Bar(
                    x=[x_val],
                    y=[y_val],
                    name=traslator.traducir(metrica_velocidad, idioma) if i == 0 else None,
                    showlegend=(i == 0),
                    marker_color=color_linea,
                    offsetgroup="velocidad",
                    yaxis="y2",
                    text=f"{y_val:.2f} m/s",
                    textposition=text_pos,
                    #textangle=text_angle,
                    textfont=dict(
                        size=bar_text_size,
                        color=text_color,
                        family="Arial"
                    ),
                    hovertemplate=f"<b>Fecha:</b> %{{x}}<br><b>{traslator.traducir(metrica_velocidad, idioma)}:</b> %{{y:.2f}} m/s<extra></extra>"
                ))
        else:
            fig.add_trace(go.Scatter(
                x=df_metric_vel[columna_x],
                y=df_metric_vel[metrica_velocidad],
                mode="lines+markers",
                name=traslator.traducir(metrica_velocidad, idioma),
                marker=dict(color=color_linea, size=10),
                line=dict(color=color_linea, width=3),
                yaxis="y2",
                hovertemplate=f"<b>Fecha:</b> %{{x}}<br><b>{traslator.traducir(metrica_velocidad, idioma)}:</b> %{{y:.2f}} m/s<extra></extra>"
            ))

        # Annotation for best velocity (maximum)
        if not barras and len(df_metric_vel) > 1:
            fila_max = df_metric_vel[df_metric_vel[metrica_velocidad] == df_metric_vel[metrica_velocidad].max()].iloc[0]
            fig.add_annotation(
                x=fila_max[columna_x],
                y=fila_max[metrica_velocidad],
                yref="y2",
                text=f"{traslator.traducir('Max', idioma)}: {fila_max[metrica_velocidad]:.2f} m/s",
                showarrow=True,
                arrowhead=2,
                ax=0 if barras else -60,
                ay=-40,
                xshift=-20 if barras else 0,
                bgcolor="gray",
                font=dict(color="white", size=annotation_font_size, family="Arial")
            )

    # === TIEMPO (Primary Y-axis with color coding) ===
    prom_tiempo = None
    if isinstance(promedio_row, dict):
        # If it's a dictionary, get the value directly
        prom_tiempo = promedio_row.get(metrica_tiempo, None)
    elif hasattr(promedio_row, 'empty') and not promedio_row.empty:
        # If it's a DataFrame and not empty
        if metrica_tiempo in promedio_row.columns:
            val = promedio_row[metrica_tiempo].values[0]
            prom_tiempo = val if pd.notna(val) else None
    
    # Ensure the value is valid
    prom_tiempo = prom_tiempo if pd.notna(prom_tiempo) else None

    cols_time = [columnas_fecha_registro, metrica_tiempo]
    if columnas_fecha_registro != columna_x:
        cols_time.insert(1, columna_x)
    df_metric_time = df[cols_time].dropna()

    if not df_metric_time.empty:
        tiempo_min = df_metric_time[metrica_tiempo].min()
        tiempo_max = df_metric_time[metrica_tiempo].max()

        # Dynamic range calculation for tiempo
        config = SPRINT_SEMAFORO.get(gender.upper(), {}).get(categoria.lower(), {})
        if config:
            # Use existing range from SPRINT_SEMAFORO
            rango = config.get("rango", (tiempo_min, tiempo_max))
            y_min = min(tiempo_min - 0.1, rango[0] - 0.1)
            y_max = max(tiempo_max + 0.1, rango[1] + 0.1)
        else:
            # Fallback range
            y_min = tiempo_min - 0.2
            y_max = tiempo_max + 0.2

        # Color-coded bars for tiempo with dynamic text positioning
        colores_tiempo = [asignar_color_sprint(v, gender, categoria) for v in df_metric_time[metrica_tiempo]]
        
        # Calculate proper contrast colors and positions for each bar
        text_colors = []
        text_positions = []
        text_angles = []
        
        # Recalculate text height for tiempo based on its actual data range
        tiempo_range = y_max - y_min
        tiempo_text_height = (bar_text_size / 400.0) * tiempo_range
        tiempo_min_height_for_inside = tiempo_text_height * 2.5
        
        for i, (valor, color) in enumerate(zip(df_metric_time[metrica_tiempo], colores_tiempo)):
            # Calculate bar height properly - use the actual bar height from base to top
            bar_height = valor - y_min  # Height from y_min baseline to the bar top
            
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
        for i, (x_val, y_val, bar_color, text_color, text_pos, text_angle) in enumerate(
            zip(df_metric_time[columna_x], df_metric_time[metrica_tiempo], 
                colores_tiempo, text_colors, text_positions, text_angles)):
            
            fig.add_trace(go.Bar(
                x=[x_val],
                y=[y_val],
                name=traslator.traducir(metrica_tiempo, idioma) if i == 0 else None,
                showlegend=(i == 0),
                marker_color=bar_color,
                offsetgroup="tiempo",
                yaxis="y1",
                text=f"{y_val:.2f} s",
                textposition=text_pos,
                #textangle=text_angle,  # FIXED: Uncommented this line
                textfont=dict(
                    size=bar_text_size, 
                    color=text_color,
                    family="Arial"
                ),
                hovertemplate=f"<b>Fecha:</b> %{{x}}<br><b>{traslator.traducir(metrica_tiempo, idioma)}:</b> %{{y:.2f}} s<extra></extra>"
            ))
        # Annotation for best time (minimum)
        if not barras and len(df_metric_time) > 1:
            fila_min = df_metric_time[df_metric_time[metrica_tiempo] == df_metric_time[metrica_tiempo].min()].iloc[0]
            fig.add_annotation(
                x=fila_min[columna_x],
                y=fila_min[metrica_tiempo],
                yref="y1",
                text=f"{traslator.traducir('Min', idioma)}: {fila_min[metrica_tiempo]:.2f} s",
                showarrow=True,
                arrowhead=2,
                ax=0,
                ay=-40,
                xshift=20 if barras else 0,
                bgcolor="gray",
                font=dict(color="white", size=annotation_font_size, family="Arial")
            )

        # Average line for tiempo
        if prom_tiempo is not None:
            fig.add_hline(
                y=prom_tiempo,
                line=dict(color=color_promedio, dash="dash", width=2),
                annotation_text=f"{prom_tiempo:.2f} s",
                annotation_position="top right",
                annotation=dict(font=dict(color="black", size=annotation_font_size, family="Arial")),
                layer="above"
            )
            fig.add_trace(go.Scatter(
                x=[None], y=[None],
                mode="lines",
                name=f"{traslator.traducir('TIEMPO OPTIMO', idioma)} ({traslator.traducir('PROMEDIO', idioma)} {cat_label})".upper(),
                line=dict(color=color_promedio, dash="dash", width=2),
                showlegend=True
            ))

        # ADD THE SPRINT COLORBAR with PDF mode
        fig = get_sprint_colorbar_agregada(fig, y_min, y_max, gender, 
                                          categoria, 
                                          gradient=gradient_colorbar,
                                          pdf_mode=pdf_mode)

        # Set Y-axis range for tiempo
        fig.update_layout(yaxis=dict(range=[y_min, y_max]))

    # === Layout final ===
    title_layout = "SPRINT" if barras else "Evolución del Sprint"
    fig.update_layout(
        title=dict(
            text=f"{traslator.traducir(title_layout, idioma).upper()} ({traslator.traducir(metrica_tiempo, idioma)} y {traslator.traducir(metrica_velocidad, idioma)})",
            font=dict(size=title_font_size, family="Arial", color="#1f2937"),
            x=0.5,
            xanchor="center"
        ),
        xaxis=dict(
            title=dict(
                text=traslator.traducir("FECHA", idioma) if not barras else None,
                font=dict(size=axis_font_size, family="Arial")
            ),
            tickmode="array",
            tickvals=tickvals,
            ticktext=ticktext,
            tickfont=dict(size=tick_font_size, family="Arial"),
            type="category" if barras else "date",
            showticklabels=not barras and len(tickvals) > 1
        ),
        yaxis=dict(
            title=dict(
                text=traslator.traducir("TIEMPO (SEG)", idioma),
                font=dict(size=axis_font_size, family="Arial")
            ),
            side="left" if not barras else "right",
            tickfont=dict(size=tick_font_size, family="Arial"),
            showgrid=True,
            showticklabels=True,          # ENSURE ALWAYS TRUE
            visible=True,                 # ENSURE AXIS IS VISIBLE
            fixedrange=False             # ALLOW ZOOM/PAN
        ),
        yaxis2=dict(
            title=dict(
                text=traslator.traducir("VELOCIDAD (M/S)", idioma),
                font=dict(size=axis_font_size, family="Arial")
            ),
            overlaying="y",
            side="right" if not barras else "left",
            tickfont=dict(size=tick_font_size, family="Arial"),
            showgrid=False,
            showticklabels=True,          # ENSURE ALWAYS TRUE
            visible=True,                 # ENSURE AXIS IS VISIBLE
            fixedrange=False             # ALLOW ZOOM/PAN
        ),
        template="plotly_white",
        barmode="group" if barras else "overlay",
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=legend_y,
            xanchor="center",
            x=0.5,
            font=dict(size=legend_font_size, family="Arial")
        ),
        margin=dict(l=margin_left, r=margin_right, t=margin_top, b=margin_bottom)
    )

    # Only display in app, not PDF
    if not pdf_mode:
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
                name=traslator.traducir(metrica_velocidad, idioma),
                marker_color=color_barra,
                yaxis="y1",
                text=df_metric_vel[metrica_velocidad].round(2),
                textposition="inside",
                textfont=dict(size=16,color="black"),
                hovertemplate=f"<b>DATE:</b> %{{x|%d-%m-%Y}}<br><b>{traslator.traducir(metrica_velocidad, idioma)}:</b> %{{y:.2f}} m/s<extra></extra>"
            ))

            # Anotación del mejor registro
            max_val = df_metric_vel[metrica_velocidad].max()
            fila_max = df_metric_vel[df_metric_vel[metrica_velocidad] == max_val].sort_values(by=columnas_fecha_registro, ascending=False).iloc[0]
            maxl = traslator.traducir("Max",idioma)
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

                promedio = traslator.traducir("PROMEDIO", idioma)
                categoria = traslator.traducir(categoria.upper(), idioma)

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
                name=traslator.traducir(metrica_tiempo, idioma),
                line=dict(color=color_linea, width=3),
                marker=dict(size=8, color=color_linea),
                yaxis="y2",
                hovertemplate=f"<b>Fecha:</b> %{{x|%d-%m-%Y}}<br><b>{traslator.traducir(metrica_tiempo, idioma)}:</b> %{{y:.2f}} seg<extra></extra>"
            ))

            min_val = df_metric_time[metrica_tiempo].min()
            fila_min = df_metric_time[df_metric_time[metrica_tiempo] == min_val].sort_values(by=columnas_fecha_registro, ascending=False).iloc[0]
            maxl = traslator.traducir("Max",idioma)
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

    title = traslator.traducir("Evolución del Sprint", idioma)

    # --- Layout final ---
    fig.update_layout(
        title=f"{title} ({traslator.traducir(metrica_tiempo, idioma)} y {traslator.traducir(metrica_velocidad, idioma)})",
        xaxis=dict(
            tickmode="array",
            tickvals=tickvals,
            ticktext=ticktext
        ),
        yaxis=dict(
            title=traslator.traducir("VELOCIDAD (M/S)",idioma),
            side="left",
            showgrid=True,
            range=[vel_min, vel_max]
        ),
        yaxis2=dict(
            title=traslator.traducir("TIEMPO (SEG)",idioma),
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
