
import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import matplotlib.pyplot as plt
from utils import util
from utils import traslator

# Define rangos y colores semáforo por género
SEMAFORO_GRASA = {
    "H": {
        "juvenil": [
            (3, "#FF0000"),
            (6, "#FFA500"),
            (7, "#FFFF00"),
            (8, "#006400"),
            (10, "#7CFC00"),
            (14, "#006400"),
            (15, "#FFFF00"),
            (17, "#FFA500"),
            (18, "#FF0000"),
            (22, "#FF0000"),
            (25, "#FF0000")
        ],
        "cadete": [
            (3, "#FF0000"),
            (6, "#FFA500"),
            (7, "#FFFF00"),
            (8, "#006400"),
            (9, "#7CFC00"),
            (14, "#006400"),
            (16, "#FFFF00"),
            (17, "#FFA500"),
            (19, "#FF0000"),
            (22, "#FF0000"),
            (25, "#FF0000")
        ]
    },
    "M": {
        "juvenil": [
            (3, "#FF0000"),
            (7, "#FFA500"),
            (8, "#FFFF00"),
            (9, "#006400"),
            (10, "#7CFC00"),
            (14, "#006400"),
            (16, "#FFFF00"),
            (18, "#FFA500"),
            (20, "#FF0000"),
            (22, "#FF0000"),
            (25, "#FF0000")
        ],
        "cadete": [
            (3, "#FF0000"),
            (7, "#FFA500"),
            (8, "#FFFF00"),
            (9, "#006400"),
            (10, "#7CFC00"),
            (18, "#006400"),
            (19, "#FFFF00"),
            (20, "#FFA500"),
            (21, "#FF0000"),
            (22, "#FF0000"),
            (25, "#FF0000")
        ]
    },
}

def get_range(gender, categoria):  # Changed from 'genero' to 'gender'
    return SEMAFORO_GRASA.get(gender.upper(), {}).get(categoria.lower(), [])


def get_color_scale(gender, categoria, cmin, cmax):  # Changed from 'genero' to 'gender'
    gender = gender.upper()
    categoria = categoria.lower()
    semaforo = SEMAFORO_GRASA.get(gender, {}).get(categoria, [])

    def norm(v):
        # Avoid division by zero
        if cmax == cmin:
            return 0.5
        return max(0, min(1, (v - cmin) / (cmax - cmin)))

    escala = []
    for umbral, color in semaforo:
        normalized_val = norm(umbral)
        escala.append([normalized_val, color])
    
    # Ensure the scale goes from 0 to 1
    if not escala:
        return [[0, "#FF0000"], [1, "#00FF00"]]
    
    # Sort by normalized value
    escala.sort(key=lambda x: x[0])
    
    # Ensure we start at 0 and end at 1
    if escala[0][0] > 0:
        escala.insert(0, [0, escala[0][1]])
    if escala[-1][0] < 1:
        escala.append([1, escala[-1][1]])
    
    return escala


def asignar_color_grasa(valor, gender, categoria):  # Changed from 'genero' to 'gender'
    if pd.isna(valor):
        return "gray"

    gender = gender.upper()
    categoria = categoria.lower()
    semaforo = SEMAFORO_GRASA.get(gender, {}).get(categoria, [])

    # Asegurar que esté ordenado
    semaforo = sorted(semaforo, key=lambda x: x[0])

    for idx in range(1, len(semaforo)):
        lim_inf, color_inf = semaforo[idx - 1]
        lim_sup, _ = semaforo[idx]

        if lim_inf <= valor < lim_sup:
            return color_inf

    # Si es menor que el primer umbral, devolver el color del primer umbral
    if valor < semaforo[0][0]:
        return semaforo[0][1]

    # Si supera todos los umbrales, devolver el color del último umbral
    return semaforo[-1][1]


def calcular_rango_visual(df_grasa, rango_color, margen=1, rango_minimo=5):
    grasa_min = df_grasa.min()
    grasa_max = df_grasa.max()

    semaforo_vals = [umbral for umbral, _ in rango_color]
    semaforo_min = min(semaforo_vals)
    semaforo_max = max(semaforo_vals)

    cmin = min(grasa_min - margen, semaforo_min)
    cmax = max(grasa_max + margen, semaforo_max)

    if cmax - cmin < rango_minimo:
        delta = (rango_minimo - (cmax - cmin)) / 2
        cmin -= delta
        cmax += delta

    return round(cmin, 2), round(cmax, 2)

def asignar_color_grasa(valor, genero, categoria):
    if pd.isna(valor):
        return "gray"

    genero = genero.upper()
    categoria = categoria.lower()
    semaforo = SEMAFORO_GRASA.get(genero, {}).get(categoria, [])

    # Asegurar que esté ordenado
    semaforo = sorted(semaforo, key=lambda x: x[0])

    for idx in range(1, len(semaforo)):
        lim_inf, color_inf = semaforo[idx - 1]
        lim_sup, _ = semaforo[idx]

        if lim_inf <= valor < lim_sup:
            return color_inf

    # Si es menor que el primer umbral, devolver el color del primer umbral
    if valor < semaforo[0][0]:
        return semaforo[0][1]

    # Si supera todos los umbrales, devolver el color del último umbral
    return semaforo[-1][1]


def get_anthropometrics_colorbar_agregada(fig, y_min, y_max, gender, 
                                        categoria, gradient=True, 
                                        pdf_mode=False):
    """
    Add anthropometrics colorbar using shapes for precise control (same approach as CMJ)
    """
    escala = get_range(gender, categoria)
    
    # PDF-SPECIFIC: Different font sizes for colorbar
    if pdf_mode:
        tick_font_size = 16      
        title_font_size = 20     
    else:
        tick_font_size = 9       
        title_font_size = 10     
    
    if gradient:
        gradient_steps = 50
        
        for i in range(len(escala) - 1):
            y_start = escala[i][0]
            y_end = escala[i + 1][0]
            color_start = escala[i][1]
            color_end = escala[i + 1][1]
            
            if color_start != color_end:
                for step in range(gradient_steps):
                    y_bottom = y_start + (y_end - y_start) * (step / gradient_steps)
                    y_top = y_start + (y_end - y_start) * ((step + 1) / gradient_steps)
                    
                    ratio = step / gradient_steps
                    interpolated_color = util.interpolate_color(color_start, color_end, ratio)
                                        
                    fig.add_shape(
                        type="rect",
                        x0=1.05, x1=1.07,           
                        y0=y_bottom, y1=y_top + 0.09,
                        xref="paper", yref="y2",    
                        fillcolor=interpolated_color,
                        line=dict(width=0, color=interpolated_color)
                    )
            else:
                fig.add_shape(
                    type="rect",
                    x0=1.05, x1=1.07,           
                    y0=y_start, y1=y_end,      
                    xref="paper", yref="y2",    
                    fillcolor=color_start,
                    line=dict(width=0)
                )
        
        # ENHANCED: Larger tick labels for PDF
        for umbral, _ in escala:
            fig.add_annotation(
                x=1.075,                     
                y=umbral,
                text=str(int(umbral)),
                xref="paper",
                yref="y2",                 
                showarrow=False,
                font=dict(size=tick_font_size, color="black"),  # PDF-aware size
                xanchor='left'
            )
        
        # ENHANCED: Larger title for PDF
        fig.add_annotation(
            x=1.057,                        
            y=1.08,                        
            text="% Grasa",                
            xref="paper",
            yref="paper",                  
            showarrow=False,
            font=dict(size=title_font_size, color="black", family="Arial"),  # PDF-aware size
            xanchor='center'               
        )
        
    else:
        # Solid colors approach with PDF-aware fonts
        num_segments = len(escala) - 1
        
        for i in range(num_segments):
            y_bottom = escala[i][0]
            y_top = escala[i + 1][0] if i < num_segments - 1 else y_max
            color = escala[i][1]
            
            fig.add_shape(
                type="rect",
                x0=1.05, x1=1.07,          
                y0=y_bottom, y1=y_top,      
                xref="paper", yref="y2",   
                fillcolor=color,
                line=dict(width=0)
            )
        
        # ENHANCED: Larger tick labels for PDF
        for umbral, _ in escala:
            fig.add_annotation(
                x=1.075,                     
                y=umbral,
                text=str(int(umbral)),
                xref="paper",
                yref="y2",                  
                showarrow=False,
                font=dict(size=tick_font_size, color="black"),  # PDF-aware size
                xanchor='left'
            )
        
        # ENHANCED: Larger title for PDF
        fig.add_annotation(
            x=1.057,                        
            y=1.08,                        
            text="% Grasa",                
            xref="paper",
            yref="paper",                  
            showarrow=False,
            font=dict(size=title_font_size, color="black", family="Arial"),  # PDF-aware size
            xanchor='center'               
        )
    
    return fig


def get_anthropometrics_graph(df_antropometria, categoria, zona_optima_min, 
                              zona_optima_max, idioma="es", barras=False, 
                              gender="H", cat_label="U19", enhanced_style=True,
                              gradient_colorbar=True,
                              pdf_mode=False):
    df = pd.DataFrame(df_antropometria)
    df["FECHA REGISTRO"] = pd.to_datetime(df["FECHA REGISTRO"], format="%d/%m/%Y")
    df = df.sort_values(by="FECHA REGISTRO")

    metricas = ["PESO (KG)", "GRASA (%)"]
    df = df[["FECHA REGISTRO"] + metricas]

    # Enhanced styling
    if enhanced_style:
        template = "plotly_white"
        font_family = "Arial, sans-serif"
        title_font_size = 16
        axis_font_size = 12
        legend_font_size = 11
    else:
        template = "plotly_white"
        font_family = "Arial"
        title_font_size = 14
        axis_font_size = 10
        legend_font_size = 9

    df_fechas_unicas = df["FECHA REGISTRO"].drop_duplicates().sort_values()
    años_unicos = df_fechas_unicas.dt.year.unique()

    if len(años_unicos) == 1:
        tickvals = df_fechas_unicas
        ticktext = df_fechas_unicas.dt.strftime("%b")
    else:
        tickvals = df_fechas_unicas
        ticktext = df_fechas_unicas.dt.strftime("%b-%Y")

    rango_color = get_range(gender, categoria)  
    cmin, cmax = calcular_rango_visual(df["GRASA (%)"], rango_color)
    
    # Enhanced color scheme
    color_lineas = {
        "PESO (KG)": "#2E86AB",
        "GRASA (%)": "#A23B72"
    }

    fig = go.Figure()

    # Handle single data point
    if len(df) == 1:
        new_row = {
            "FECHA REGISTRO": df["FECHA REGISTRO"].iloc[0] + pd.Timedelta(days=5),
            "PESO (KG)": None,
            "GRASA (%)": None
        }
        df = pd.concat([df, pd.DataFrame([new_row])], ignore_index=True)

    # PESO trace
    if "PESO (KG)" in df.columns:
        size = 22 if len(df) <= 2 else 16

        # Calculate contrasting text color for PESO (solid color)
        peso_color = color_lineas["PESO (KG)"]  # "#2E86AB"
        peso_text_color = util.get_contrasting_text_color(peso_color)

        fig.add_trace(go.Bar(
            x=df["FECHA REGISTRO"],
            y=df["PESO (KG)"],
            name=traslator.traducir("PESO (KG)", idioma),
            marker_color=color_lineas["PESO (KG)"],
            marker_line=dict(width=1, color="rgba(0,0,0,0.1)"),
            offsetgroup="peso",
            text=df["PESO (KG)"].apply(lambda x: f"{x:.1f} kg" if pd.notna(x) else ""),
            textposition="inside",
            textangle=-90,
            textfont=dict(size=size, color=peso_text_color, family=font_family),
            yaxis="y1",
            hovertemplate="<b>Fecha:</b>%{x|%d-%m-%Y}<br><b>Peso:</b> %{y:.1f} kg<extra></extra>"            
        ))

    # GRASA trace
    if "GRASA (%)" in df.columns:
        x_vals = df["FECHA REGISTRO"]
        y_vals = df["GRASA (%)"]
        colores_puntos = y_vals.apply(lambda x: asignar_color_grasa(x, gender, categoria))  # Fixed parameter name
        
        if barras or len(y_vals) <= 2:
            size = 24 if pdf_mode else (22 if len(x_vals) <= 2 else 16)  # PDF-aware size

            for i, (x_val, y_val, bar_color) in enumerate(zip(x_vals, y_vals, colores_puntos)):
                if pd.notna(y_val):                    
                    text_color = util.get_contrasting_text_color(bar_color)
                    
                    fig.add_trace(go.Bar(
                        x=[x_val],
                        y=[y_val],
                        name=traslator.traducir("GRASA (%)", idioma) if i == 0 else None,
                        showlegend=(i == 0),
                        marker_color=bar_color,
                        marker_line=dict(width=1, color="rgba(0,0,0,0.1)"),
                        offsetgroup="grasa",
                        yaxis="y2",
                        text=f"{y_val:.1f} %",
                        textposition="inside",
                        textangle=-90,
                        textfont=dict(size=size, color=text_color, family=font_family),  # PROPER contrast
                        hovertemplate="<b>Fecha:</b> %{x|%d-%m-%Y}<br><b>Grasa:</b> %{y:.1f} %<extra></extra>"
                    ))
        else:
            fig.add_trace(go.Scatter(
                x=x_vals,
                y=y_vals,
                mode="lines+markers",
                name=traslator.traducir("GRASA (%)", idioma),
                line=dict(color=color_lineas["GRASA (%)"], width=3, shape="spline"),
                marker=dict(
                    color=colores_puntos, 
                    size=12,
                    line=dict(width=2, color="white")
                ),
                yaxis="y2",
                hovertemplate="<b>Fecha:</b> %{x|%d-%m-%Y}<br><b>Grasa:</b> %{y:.1f} %<extra></extra>"
            ))

        # Enhanced optimal zone
        df_filtro = df[["FECHA REGISTRO", "GRASA (%)"]].dropna()
        if not df_filtro.empty:
            x_min = df["FECHA REGISTRO"].min() - pd.Timedelta(days=20)
            x_max = df["FECHA REGISTRO"].max() + pd.Timedelta(days=15)

            # Optimal zone fill
            fig.add_trace(go.Scatter(
                x=[x_min, x_max, x_max, x_min, x_min],
                y=[zona_optima_min, zona_optima_min, zona_optima_max, zona_optima_max, zona_optima_min],
                fill="toself",
                fillcolor="rgba(0, 128, 0, 0.1)",
                line=dict(color="rgba(0, 128, 0, 0)"),
                name=f"{traslator.traducir('ZONA ÓPTIMA', idioma)} ({cat_label})",
                yaxis="y2",
                hoverinfo="skip"
            ))

            # Optimal zone borders with labels
            for i, (y_linea, label_type) in enumerate([(zona_optima_max, "MÁXIMO"), (zona_optima_min, "MÍNIMO")]):
                # Add the dashed line
                fig.add_trace(go.Scatter(
                    x=[x_min, x_max],
                    y=[y_linea, y_linea],
                    mode="lines",
                    line=dict(color="green", dash="dash", width=2),
                    yaxis="y2",
                    showlegend=False,
                    hoverinfo="skip"
                ))
                
                # ADDED: Labels for optimal zone boundaries
                fig.add_annotation(
                    x=x_max,  # Position at the end of the line
                    y=y_linea,
                    text=f"{traslator.traducir(label_type, idioma)}: {y_linea:.1f}%",
                    showarrow=True,
                    arrowhead=2,
                    arrowsize=1,
                    arrowwidth=1.5,
                    arrowcolor="green",
                    ax=15 if i == 0 else 15,  # Arrow offset to the right
                    ay=-10 if i == 0 else 10,  # Arrow offset (up for max, down for min)
                    bgcolor="rgba(255, 255, 255, 0.9)",
                    bordercolor="green",
                    borderwidth=1,
                    font=dict(
                        color="green", 
                        size=10, 
                        family=font_family
                    ),
                    xref="x",
                    yref="y2"
                )

    # Enhanced layout
    # PDF-SPECIFIC: Different font sizes and margins for PDF
    if pdf_mode:
        title_font_size = 48        
        axis_font_size = 40        
        tick_font_size = 36         
        legend_font_size = 32       
        margin_left = 180           
        margin_right = 320          
        margin_top = 160            
        margin_bottom = 220         
        legend_y = -0.20           
    else:
        # App display (original sizes)
        title_font_size = 16
        axis_font_size = 12
        tick_font_size = 10
        legend_font_size = 12
        margin_left = 50
        margin_right = 130
        margin_top = 60
        margin_bottom = 80
        legend_y = -0.15

    # Get peso range - FORCE to start at 0
    peso_values = df["PESO (KG)"].dropna()
    if not peso_values.empty:
        peso_max = peso_values.max()
        peso_padding = peso_max * 0.1  # 10% padding above max
        peso_range_min = 0  # ALWAYS start at 0
        peso_range_max = peso_max + peso_padding
    else:
        peso_range_min = 0
        peso_range_max = 100

    # Get grasa range - FORCE to start at 0  
    grasa_range_min = 0  # ALWAYS start at 0
    grasa_range_max = cmax  # Use calculated max

    # Enhanced layout
    title_text = "PESO Y % GRASA" if barras else "Evolución del Peso y % Grasa"
    
    # Enhanced layout with FIXED Y2 axis positioning
    fig.update_layout(
        title=dict(
            text=traslator.traducir(title_text, idioma).upper(),
            font=dict(size=title_font_size, family=font_family, color="#1f2937"),
            x=0.5,
            xanchor="center"
        ),
        xaxis=dict(
            title=dict(
                text=traslator.traducir("FECHA", idioma) if not barras else None,
                font=dict(size=axis_font_size, family=font_family)
            ),
            tickfont=dict(size=tick_font_size, family=font_family),
            gridcolor="rgba(0,0,0,0.1)",
            tickmode="array",
            tickvals=tickvals,
            ticktext=ticktext,
            showticklabels=not barras and len(tickvals) > 2
        ),
        yaxis=dict(
            title=dict(
                text=traslator.traducir("PESO (KG)", idioma),
                font=dict(size=axis_font_size, family=font_family)
            ),
            side="left",
            tickfont=dict(size=tick_font_size, family=font_family),
            gridcolor="rgba(0,0,0,0.1)",
            range=[0, peso_range_max],
            rangemode="tozero"
        ),
        yaxis2=dict(
            title=dict(
                text=traslator.traducir("GRASA (%)", idioma),
                font=dict(size=axis_font_size, family=font_family)
            ),
            overlaying="y",
            side="right",
            showgrid=False,
            tickfont=dict(size=tick_font_size, family=font_family),
            range=[0, grasa_range_max],
            rangemode="tozero",
            # FIXED: Ensure right axis ticks are visible
            tickmode="linear",
            dtick=grasa_range_max / 5,  # Show 5-6 ticks on right axis
            showticklabels=True,
            tickcolor="black",
            ticklen=5
        ),
        template=template,
        barmode="group",
        legend=dict(
            orientation="h",
            yanchor="top",
            y=legend_y,  # FIXED: Moved up to avoid FECHA overlap
            xanchor="center",
            x=0.5,
            font=dict(size=legend_font_size, family=font_family)
        ),
        margin=dict(l=margin_left, r=margin_right, t=margin_top, b=margin_bottom),
        paper_bgcolor="white",
        plot_bgcolor="white"
    )

    # PDF-SPECIFIC: Enhance optimal zone annotations
    if pdf_mode:
        # Update existing optimal zone annotations with larger fonts
        if fig.layout.annotations:
            updated_annotations = []
            for ann in fig.layout.annotations:
                ann_dict = ann.to_plotly_json()
                if 'font' in ann_dict and ann_dict['font']:
                    if 'size' in ann_dict['font']:
                        ann_dict['font']['size'] = max(18, int(ann_dict['font']['size'] * 2))  # At least 18pt, double current
                updated_annotations.append(ann_dict)
            fig.update_layout(annotations=updated_annotations)

    # ADD THE ANTHROPOMETRICS COLORBAR with PDF mode
    fig = get_anthropometrics_colorbar_agregada(fig, cmin, cmax, gender, 
                                                categoria,
                                                gradient=gradient_colorbar,
                                                pdf_mode=pdf_mode)

    # Display the chart
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

    st.dataframe(df)

def get_height_graph(df_altura, idioma="es", barras=False, 
                     enhanced_style=True, pdf_mode=False):
    df = pd.DataFrame(df_altura)
    df["FECHA REGISTRO"] = pd.to_datetime(df["FECHA REGISTRO"], format="%d/%m/%Y")
    df = df.sort_values(by="FECHA REGISTRO")

    if "ALTURA (CM)" not in df.columns:
        return None

    # PDF-SPECIFIC: Different font sizes
    if pdf_mode:
        template = "plotly_white"
        font_family = "Arial, sans-serif"
        title_font_size = 40        # LARGE for PDF
        axis_font_size = 28         # LARGE for PDF
        marker_size = 20            # LARGER markers
        line_width = 4              # THICKER lines
        annotation_size = 18        # LARGER annotations
    elif enhanced_style:
        template = "plotly_white"
        font_family = "Arial, sans-serif"
        title_font_size = 16
        axis_font_size = 12
        marker_size = 16
        line_width = 3
        annotation_size = 11
    else:
        template = "plotly_white"
        font_family = "Arial"
        title_font_size = 14
        axis_font_size = 10
        marker_size = 14
        line_width = 2
        annotation_size = 9

    fig = go.Figure()

    # Enhanced height trace with PDF-aware sizing
    fig.add_trace(go.Scatter(
        x=df["FECHA REGISTRO"],
        y=df["ALTURA (CM)"],
        mode="markers+lines",
        name="Altura (cm)",
        marker=dict(
            size=marker_size,                    # PDF-aware size
            color="#3B82F6",
            line=dict(width=3, color="white"),
            symbol="circle"
        ),
        line=dict(color="#1E40AF", width=line_width, shape="spline"),  # PDF-aware width
        hovertemplate="<b>%{x|%d-%m-%Y}</b><br>Altura: <b>%{y:.1f} cm</b><extra></extra>"
    ))

    # Enhanced date formatting
    df_fechas_unicas = df["FECHA REGISTRO"].drop_duplicates().sort_values()
    años_unicos = df_fechas_unicas.dt.year.unique()

    if len(años_unicos) == 1:
        tickvals = df_fechas_unicas
        ticktext = df_fechas_unicas.dt.strftime("%b")
    else:
        tickvals = df_fechas_unicas
        ticktext = df_fechas_unicas.dt.strftime("%b-%Y")

    # Enhanced annotation
    if not df.empty:
        max_valor = df["ALTURA (CM)"].max()
        fila_max = df[df["ALTURA (CM)"] == max_valor].sort_values(by="FECHA REGISTRO", ascending=False).iloc[0]
        
        fig.add_annotation(
            x=fila_max["FECHA REGISTRO"],
            y=fila_max["ALTURA (CM)"],
            text=f"Máx: {fila_max['ALTURA (CM)']:.1f} cm",
            showarrow=True,
            arrowhead=2,
            arrowsize=1,
            arrowwidth=2,
            arrowcolor="#1f2937",
            ax=0,
            ay=-40,
            bgcolor="#1f2937",
            bordercolor="white",
            borderwidth=2,
            font=dict(color="white", size=annotation_size, family=font_family)  # PDF-aware size
        )

    # Enhanced layout with PDF-aware fonts
    title_text = "ALTURA (CM)" if barras else "Evolución de la Altura"
    
    fig.update_layout(
        title=dict(
            text=traslator.traducir(title_text, idioma).upper(),
            font=dict(size=title_font_size, family=font_family, color="#1f2937"),  # PDF-aware size
            x=0.5,
            xanchor="center"
        ),
        xaxis=dict(
            title=None,
            tickfont=dict(size=axis_font_size-4, family=font_family),  # Slightly smaller than axis title
            gridcolor="rgba(0,0,0,0.1)",
            tickmode="array",
            tickvals=tickvals,
            ticktext=ticktext,
            showticklabels=not barras
        ),
        yaxis=dict(
            title=dict(
                text=traslator.traducir("ALTURA (CM)", idioma),
                font=dict(size=axis_font_size, family=font_family)  # PDF-aware size
            ),
            tickfont=dict(size=axis_font_size-4, family=font_family),  # PDF-aware size
            gridcolor="rgba(0,0,0,0.1)"
        ),
        template=template,
        legend=dict(
            orientation="h",
            yanchor="top",
            y=-0.15 if not pdf_mode else -0.05,  # Closer for PDF
            xanchor="center",
            x=0.5,
            font=dict(size=axis_font_size, family=font_family)  # PDF-aware size
        ),
        margin=dict(
            l=80 if pdf_mode else 50, 
            r=80 if pdf_mode else 50, 
            t=100 if pdf_mode else 60, 
            b=100 if pdf_mode else 80
        ),  # Larger margins for PDF
        paper_bgcolor="white",
        plot_bgcolor="white"
    )

    if not pdf_mode:  # Only display in app
        st.plotly_chart(fig, use_container_width=True)

    return fig
