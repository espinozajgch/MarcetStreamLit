import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import matplotlib.pyplot as plt
from utils import util
from utils import traslator

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


def get_cmj_color_scale(gender, categoria):  
    return CMJ_SEMAFORO.get(gender.upper(), {}).get(categoria.lower(), [])


def asignar_color_cmj(valor, gender, categoria): 
    if pd.isna(valor):
        return "gray"
    
    escala = get_cmj_color_scale(gender, categoria)  

    for umbral_min, color in reversed(escala):
        if valor >= umbral_min:
            return color

    return escala[0][1] if escala else "gray"


def get_color_scale(gender, categoria, cmin, cmax):  
    gender = gender.upper()
    categoria = categoria.lower()
    semaforo = get_cmj_color_scale(gender, categoria)  

    def norm(v):
        return max(0, min(1, round((v - cmin) / (cmax - cmin), 4)))

    escala = []
    for umbral, color in semaforo:
        escala.append([norm(umbral), color])
    if escala and escala[-1][0] < 1:
        escala.append([1, semaforo[-1][1]])
    return escala


def calcular_rango_cmj(valores, escala, gender): 
    if not escala:
        return min(valores), max(valores)
    umbrales = [umbral for umbral, _ in escala]
    minimo = min(15, min(umbrales)) - 1
    maximo = max(50 if gender == "H" else 40, max(umbrales)) + 1
    if maximo - minimo < 10:
        maximo = minimo + 10
    return minimo, maximo


def get_cmj_colorbar_agregada(fig, y_min, y_max, gender, 
                              categoria, gradient=True,
                              pdf_mode=False):
    """
    Add CMJ colorbar using shapes for precise control
    """
    escala = get_cmj_color_scale(gender, categoria)

    # PDF-SPECIFIC: Different font sizes for colorbar
    if pdf_mode:
        tick_font_size = 16      
        title_font_size = 20     
    else:
        tick_font_size = 9       
        title_font_size = 10     
    
    if gradient:
        gradient_steps = 50  # Fewer steps to avoid visual artifacts
        
        for i in range(len(escala) - 1):
            y_start = escala[i][0]
            y_end = escala[i + 1][0]
            color_start = escala[i][1]
            color_end = escala[i + 1][1]
            
            # Only create gradient if colors are different
            if color_start != color_end:
                # Create gradient steps between current and next color
                for step in range(gradient_steps):
                    y_bottom = y_start + (y_end - y_start) * (step / gradient_steps)
                    y_top = y_start + (y_end - y_start) * ((step + 1) / gradient_steps)
                    
                    # Interpolate between colors
                    ratio = step / gradient_steps
                    interpolated_color = util.interpolate_color(color_start, color_end, ratio)
                    
                    # Add rectangle with NO BORDERS and SLIGHT OVERLAP to avoid gaps
                    fig.add_shape(
                        type="rect",
                        x0=1.02, x1=1.04,           
                        y0=y_bottom, y1=y_top + 0.09,  # Slight overlap to avoid gaps
                        xref="paper", yref="y",     
                        fillcolor=interpolated_color,
                        line=dict(width=0, color=interpolated_color)  # Line color matches fill
                    )
            else:
                # Same color, create a solid block
                fig.add_shape(
                    type="rect",
                    x0=1.02, x1=1.04,           
                    y0=y_start, y1=y_end,      
                    xref="paper", yref="y",     
                    fillcolor=color_start,
                    line=dict(width=0)
                )
        
        # Add tick labels for gradient version with PDF-aware sizes
        for umbral, _ in escala:
            fig.add_annotation(
                x=1.045,                     
                y=umbral,
                text=str(int(umbral)),
                xref="paper",
                yref="y",                   
                showarrow=False,
                font=dict(size=tick_font_size, color="black"),  
                xanchor='left'
            )
        
        # Add title for gradient version with PDF-aware size
        fig.add_annotation(
            x=1.03,                        
            y=1.08,                       
            text="Altura (cm)",
            xref="paper",
            yref="paper",                  
            showarrow=False,
            font=dict(size=title_font_size, color="black", family="Arial"),  
            xanchor='center'               
        )
        
    else:
        # SOLID COLORS APPROACH: Original behavior with discrete color blocks
        num_segments = len(escala) - 1
        
        for i in range(num_segments):
            y_bottom = escala[i][0]
            y_top = escala[i + 1][0] if i < num_segments - 1 else y_max
            color = escala[i][1]
            
            fig.add_shape(
                type="rect",
                x0=1.02, x1=1.04,           
                y0=y_bottom, y1=y_top,      
                xref="paper", yref="y",     
                fillcolor=color,
                line=dict(width=0)
            )
        
        # Add tick labels with PDF-aware sizes
        for umbral, _ in escala:
            fig.add_annotation(
                x=1.045,                     
                y=umbral,
                text=str(int(umbral)),
                xref="paper",
                yref="y",                   
                showarrow=False,
                font=dict(size=tick_font_size, color="black"),  
                xanchor='left'
            )
        
        # Add title with PDF-aware size
        fig.add_annotation(
            x=1.03,                        
            y=1.08,                       
            text="Altura (cm)",
            xref="paper",
            yref="paper",                  
            showarrow=False,
            font=dict(size=title_font_size, color="black", family="Arial"),  
            xanchor='center'               
        )
    
    return fig


def get_cmj_graph(df_cmj, promedios, categoria, equipo, metricas, 
                  columna_fecha_registro, idioma="es", 
                  barras=False, gender="H",
                  cat_label="U19",
                  gradient_colorbar=True,
                  pdf_mode=False):
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
            
            # PDF-SPECIFIC: Larger text size for PDF
            size = 24 if pdf_mode else (19 if len(x_vals) == 1 else 14)
            
            # Calculate proper contrast colors for each bar
            text_colors = []
            for color in colores_puntos:
                text_color = util.get_contrasting_text_color(color)
                text_colors.append(text_color)
            
            for i, (x_val, y_val, bar_color, text_color) in enumerate(zip(x_vals, y_vals, colores_puntos, text_colors)):
                fig.add_trace(go.Bar(
                    x=[x_val],
                    y=[y_val],
                    name=traslator.traducir(metrica, idioma).replace("-", " ") if i == 0 else None,
                    showlegend=(i == 0),
                    marker_color=bar_color,
                    width=ancho_barra,
                    yaxis="y1",
                    text=f"{y_val:.2f} cm",
                    textposition="inside",
                    #textangle=-90,  # KEEP CONSISTENT VERTICAL TEXT
                    textfont=dict(
                        size=size,
                        color=text_color,  # PROPER contrast for each individual bar
                        family="Arial"
                    ),
                    hovertemplate=f"<b>Fecha:</b> %{{x}}<br><b>{metrica}:</b> %{{y:.2f}} cm<extra></extra>"
                ))
        else:
            fig.add_trace(go.Scatter(
                x=x_vals,
                y=y_vals,
                mode="lines",
                name=traslator.traducir(metrica, idioma),
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
            maxl = traslator.traducir("Max", idioma)
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
            name=f"{traslator.traducir('ALTURA OPTIMA', idioma)} ({traslator.traducir('PROMEDIO', idioma)} {cat_label})".upper(),
            line=dict(color=color_promedio.get(metrica, "gray"), dash="dash")
        ))

    # PDF-SPECIFIC: Different font sizes for layout
    if pdf_mode:
        title_font_size = 36
        axis_font_size = 28
        tick_font_size = 22
        legend_font_size = 20
        margin_left = 120
        margin_right = 180
        margin_top = 100
        margin_bottom = 100
        legend_y = -0.15
    else:
        title_font_size = 16
        axis_font_size = 12
        tick_font_size = 10
        legend_font_size = 12
        margin_left = 50
        margin_right = 100
        margin_top = 60
        margin_bottom = 80
        legend_y = -0.3

    title_layout = "POTENCIA MUSCULAR DE SALTO (CMJ)" if barras else "Evolución de la Potencia Muscular de Salto (CMJ)"
    fig.update_layout(
        title=dict(
            text=traslator.traducir(title_layout, idioma).upper(),
            font=dict(size=title_font_size, family="Arial", color="#1f2937"),
            x=0.5,
            xanchor="center"
        ),
        xaxis=dict(
            title=dict(
                text=traslator.traducir("FECHA", idioma) if not barras else None,
                font=dict(size=axis_font_size, family="Arial")
            ),
            tickfont=dict(size=tick_font_size, family="Arial"),
            tickmode="array",
            tickvals=tickvals,
            ticktext=ticktext,
            type="category" if barras else "date",
            showticklabels=not barras and len(tickvals) > 1
        ),
        yaxis=dict(
            title=dict(
                text=traslator.traducir("ALTURA DE SALTO (CM)", idioma),
                font=dict(size=axis_font_size, family="Arial")
            ),
            tickfont=dict(size=tick_font_size, family="Arial"),
            range=[cmin, cmax]
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

    # ADD THE CMJ COLORBAR with PDF mode
    fig = get_cmj_colorbar_agregada(fig, cmin, cmax, gender, 
                                    categoria,
                                    gradient=gradient_colorbar,
                                    pdf_mode=pdf_mode)  # Pass PDF mode

    # Only display in app, not PDF
    if not pdf_mode:
        st.plotly_chart(fig, use_container_width=True)
        
    return fig
