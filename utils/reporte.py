import streamlit as st
import pandas as pd
from fpdf import FPDF
import numpy as np
import requests
from datetime import datetime
from utils.pdf import PDF
from utils import traslator
from datetime import date


def add_footer(pdf, invertido=False, idioma="es"):
    """Simple footer without gradient scale for reports"""
    page_height = pdf.get_height()
    margen_inferior = 15
    y_final = page_height - margen_inferior
    
    pdf.set_xy(10, y_final)
    pdf.set_font("Arial", "I", 8)
    pdf.set_text_color(150, 150, 150)
    pdf.cell(0, 10, f"Página {pdf.page_no()}", align="C")


def add_footer_con_texto(pdf, texto, idioma="es"):
    page_height = pdf.get_height()
    margen_inferior = 33
    y_final = page_height - margen_inferior

    # === Texto de Observaciones ===
    pdf.set_xy(10, y_final)

    if(idioma == "ar"):
        pdf.set_font("Amiri", "", 11)
    else:
        pdf.set_font("Arial", "", 11)
    #pdf.set_font("Arial", "B", 11)

    pdf.set_text_color(0, 51, 102)  # Azul oscuro
    pdf.cell(0, 6, traslator.traducir("Observaciones", idioma).upper(), ln=True)

    if(idioma == "ar"):
        pdf.set_font("Amiri", "", 10)
    else:
        pdf.set_font("Arial", "", 10)
        
    pdf.set_text_color(0, 0, 0)
    pdf.multi_cell(0, 5, texto)


def add_observation(pdf, obs_text, idioma="es"):
    """Add observations between section title and graphic"""
    if not obs_text:
        return
    
    # Add space after section title
    pdf.ln(3)

    # Set font style same as generate_pdf_simple
    if idioma == "ar":
        pdf.set_font("Amiri", "I", 6.6)
    else:
        pdf.set_font("Arial", "I", 6.6)
    
    pdf.set_text_color(0, 0, 0)  # Black text
    pdf.multi_cell(190, 3, obs_text)
    pdf.ln(3)  # Space between observation and graphic


def create_section_mapping():
    """Create consistent mapping with proper order and individual chart handling"""
    return {
        "COMPOSICIÓN CORPORAL - ALTURA": {
            "figures": ["Altura"],
            "observation_key": None,
            "dataframe_check": "anthropometrics",
            "order": 1
        },
        "COMPOSICIÓN CORPORAL - PESO Y GRASA": {
            "figures": ["Peso y Grasa"],
            "observation_key": "Peso y % Grasa",
            "dataframe_check": "anthropometrics", 
            "order": 2
        },
        "POTENCIA MUSCULAR (SALTO CON CONTRAMOVIMIENTO)": {
            "figures": ["CMJ"],
            "observation_key": "POTENCIA MUSCULAR (SALTO CON CONTRAMOVIMIENTO)",
            "dataframe_check": None,  
            "order": 3
        },
        "SPRINT (0-5M)": {
            "figures": ["SPRINT 0-5"],
            "observation_key": "SPRINT (0-5M)",
            "dataframe_check": None,  
            "order": 4
        },
        "SPRINT (0-40M)": {
            "figures": ["SPRINT 0-40"],
            "observation_key": "SPRINT (0-40M)",
            "dataframe_check": None,  
            "order": 4
        },
        "VELOCIDAD EN EL CAMBIO DE DIRECCIÓN (AGILIDAD 505)": {
            "figures": ["AGILIDAD"],
            "observation_key": "VELOCIDAD EN EL CAMBIO DE DIRECCIÓN (AGILIDAD 505)",
            "dataframe_check": None,  
            "order": 5
        },
        "RESISTENCIA INTERMITENTE DE ALTA INTENSIDAD (YO-YO TEST)": {
            "figures": ["YO-YO"],
            "observation_key": None,
            "dataframe_check": "yoyo",
            "order": 6
        },
        "CAPACIDAD DE REALIZAR SPRINT'S REPETIDOS (RSA)": {
            "figures": ["RSA Tiempo", "RSA Velocidad"],
            "observation_key": None,
            "dataframe_check": "rsa",
            "order": 7
        }
    }


def create_pdf_optimized_figures(figs_dict, fig_params_dict, idioma="es"):
    """
    DEBUG VERSION: Log what happens specifically with Peso y Grasa
    """
    import graphics.graphics as graphics
    import graphics.sprint as sprintg
    import graphics.agilidad as agilidadg
    import graphics.cmj as cmjg
    import graphics.yoyo as yoyog
    import graphics.rsa as rsag
    import copy
    
    pdf_figs = {}
    
    function_map = {
        'height': graphics.get_height_graph,
        'anthropometrics': graphics.get_anthropometrics_graph,
        'cmj': cmjg.get_cmj_graph,
        'sprint': sprintg.get_sprint_graph,
        'yoyo': yoyog.get_yoyo_graph,
        'agility': agilidadg.get_agility_graph_combined_simple,
        'rsa': rsag.get_rsa_graph,
        'rsa_velocity': rsag.get_rsa_velocity_graph
    }
    
    for fig_name, original_fig in figs_dict.items():
        if original_fig is None:
            pdf_figs[fig_name] = None
            print(f"SKIPPED - No original figure for {fig_name}")
            continue
            
        # SPECIAL DEBUG for Peso y Grasa
        if fig_name == "Peso y Grasa":
            # FORCE post-processing only for this figure
            pdf_figs[fig_name] = create_pdf_version_of_figure(copy.deepcopy(original_fig))
            print(f"DEBUG - Peso y Grasa: Created PDF VERSION figure without params")
            continue
            
        # Normal processing for others...
        if fig_name in fig_params_dict:
            try:
                params = copy.deepcopy(fig_params_dict[fig_name]['params'])
                function_type = fig_params_dict[fig_name]['function_type']
                
                params['pdf_mode'] = True
                params['idioma'] = idioma
                
                if function_type in function_map:
                    pdf_fig = function_map[function_type](**params)
                    pdf_figs[fig_name] = pdf_fig
                    print(f"EXISTS - Created PDF figure for {fig_name} with params.")
                else:
                    pdf_figs[fig_name] = create_pdf_version_of_figure(copy.deepcopy(original_fig))
                    print(f"FALLBACK - Created PDF VERSION figure for {fig_name} with params.")
                    
            except Exception as e:
                pdf_figs[fig_name] = create_pdf_version_of_figure(copy.deepcopy(original_fig))
                print(f"EXCEPTION - Created PDF VERSION figure for {fig_name} with params")
        else:
            pdf_figs[fig_name] = create_pdf_version_of_figure(copy.deepcopy(original_fig))
            print(f"NO PARAMS - Created PDF VERSION figure for {fig_name} without params")
    
    return pdf_figs

def create_pdf_version_of_figure(fig):
    """
    IMPROVED: Better post-processing fallback with proper text scaling
    """
    import plotly.graph_objects as go
    
    if fig is None:
        return None
    
    # Deep copy
    pdf_fig = go.Figure(fig)
    
    # ENHANCED: More aggressive text scaling for PDF readability
    pdf_fig.update_layout(
        title=dict(font=dict(size=48)),          # INCREASED from 36
        xaxis=dict(
            title=dict(font=dict(size=40)),       # INCREASED from 28
            tickfont=dict(size=36)                # INCREASED from 22
        ),
        yaxis=dict(
            title=dict(font=dict(size=40)),       # INCREASED from 28
            tickfont=dict(size=36)                # INCREASED from 22
        ),
        yaxis2=dict(
            title=dict(font=dict(size=40)),       # INCREASED from 28
            tickfont=dict(size=36)                # INCREASED from 22
        ),
        legend=dict(
            font=dict(size=32),                   # INCREASED from 20
            y=-0.18                               # MOVED LOWER from -0.03
        ),
        margin=dict(l=180, r=320, t=160, b=200)  # INCREASED margins
    )
    
    # ENHANCED: Preserve original text colors and angles for bar charts
    for trace in pdf_fig.data:
        if trace.type == 'bar' and hasattr(trace, 'textfont'):
            current_color = getattr(trace.textfont, 'color', 'white')
            current_size = getattr(trace.textfont, 'size', 12)
            current_angle = getattr(trace, 'textangle', 0)
            
            # FIXED: Preserve original color and angle, significantly increase size
            trace.update(textfont=dict(
                size=max(30, int(current_size * 2.0)),   # INCREASED multiplier
                color=current_color,  # PRESERVE original contrast color
                family='Arial'
            ))
            
            # PRESERVE text angle
            if hasattr(trace, 'textangle'):
                trace.update(textangle=current_angle)
    
    # ENHANCED: Much larger annotation text for PDF  
    if pdf_fig.layout.annotations:
        updated_annotations = []
        for ann in pdf_fig.layout.annotations:
            ann_dict = ann.to_plotly_json()
            if 'font' in ann_dict and ann_dict['font']:
                if 'size' in ann_dict['font']:
                    ann_dict['font']['size'] = max(24, int(ann_dict['font']['size'] * 2.0))  # INCREASED
            updated_annotations.append(ann_dict)
        
        pdf_fig.update_layout(annotations=updated_annotations)
    
    return pdf_fig


def generate_pdf_unified(df_jugador, df_anthropometrics, df_agilty, df_sprint, df_cmj, 
                         df_yoyo, df_rsa, figs_dict, fecha_actual, idioma="es", 
                         observaciones_dict=None, report_type="simple", 
                         fig_params_dict=None, verbose=False):
    """
    FIXED: Proper height calculation and observation handling
    """
    pdf = PDF(fecha_actual=fecha_actual, idioma=idioma)
    pdf.add_page()
    pdf.header()
    
    # Player information block
    pdf.add_player_block(df_jugador, idioma=idioma)

    if observaciones_dict is None:
        observaciones_dict = {}
    
    if fig_params_dict is None:
        fig_params_dict = {}

    # Skip measurements block entirely
    pdf_figs_dict = create_pdf_optimized_figures(figs_dict, fig_params_dict, idioma)

    section_mapping = create_section_mapping()
    charts_to_add = []
    sorted_sections = sorted(section_mapping.items(), key=lambda x: x[1]["order"])
    
    for section_name, mapping in sorted_sections:
        for fig_name in mapping["figures"]:
            if fig_name in pdf_figs_dict and pdf_figs_dict[fig_name] is not None:
                fig = pdf_figs_dict[fig_name]
                obs_key = mapping.get("observation_key")
                obs_text = observaciones_dict.get(obs_key, "") if obs_key else ""
                charts_to_add.append((fig, section_name, obs_text))

    total_charts = len(charts_to_add)
    
    # EXACT COORDINATE MEASUREMENTS
    first_page_start_y = pdf.get_y()
    footer_start_y = pdf.h - 20  # Increased footer margin for safety
    
    # FIRST PAGE: Available space after player block
    first_page_space = footer_start_y - first_page_start_y
    # Account for section titles and spacing (estimated ~15mm per chart)
    first_page_chart_height = (first_page_space - 30) / 2  # Subtract space for titles
    
    # SUBSEQUENT PAGES: Measure header space
    current_page = pdf.page
    pdf.add_page()
    subsequent_page_start_y = pdf.get_y()
    subsequent_page_space = footer_start_y - subsequent_page_start_y
    # Account for section titles and spacing (estimated ~15mm per chart)
    subsequent_page_chart_height = (subsequent_page_space - 45) / 3  # Subtract space for titles
    
    # Return to original page
    pdf.page = current_page
    pdf.set_y(first_page_start_y)
    
    if verbose:
        print(f"EXACT MEASUREMENTS:")
        print(f"First page Y start: {first_page_start_y}")
        print(f"Footer Y start: {footer_start_y}")
        print(f"First page space: {first_page_space}")
        print(f"First page chart height: {first_page_chart_height}")
        print(f"Subsequent page start Y: {subsequent_page_start_y}")
        print(f"Subsequent page space: {subsequent_page_space}")
        print(f"Subsequent page chart height: {subsequent_page_chart_height}")
    
    for i, (fig, section_name, obs_text) in enumerate(charts_to_add):
        
        # PAGE BREAK LOGIC
        if i <= 1:
            # FIRST PAGE: Charts 0 and 1
            chart_height = first_page_chart_height
            if verbose:
                print(f"Chart {i}: {section_name}, Height: {chart_height} (FIRST PAGE)")
            
        else:
            # SUBSEQUENT PAGES: Charts 2, 3, 4 then 5, 6, 7 etc.
            page_position = (i - 2) % 3  # 0, 1, 2 for charts 2,3,4 then 5,6,7 etc.
            
            if page_position == 0:
                # Start new page for charts 2, 5, 8, etc.
                pdf.add_page()
                if verbose:
                    print(f"NEW PAGE for chart {i}")
                
            chart_height = subsequent_page_chart_height
            if verbose:
                print(f"Chart {i}: {section_name}, Height: {chart_height} (SUBSEQUENT PAGE, position: {page_position})")

        # FIXED: Don't override calculated height - only ensure minimum
        chart_height = max(35, chart_height)  # Only minimum bound, no maximum
        
        # Layout ratios
        if obs_text.strip():
            chart_width_ratio = 0.68
            obs_width_ratio = 0.30
        else:
            chart_width_ratio = 0.93
            obs_width_ratio = 0.0
        
        if verbose:
            print(f"BEFORE add_individual_chart: Page {pdf.page}, Y: {pdf.get_y()}")
        
        # CALL THE FUNCTION WITH DISABLED PAGE BREAKS
        pdf.add_individual_chart(fig, section_name, obs_text, idioma, 
                               chart_width_ratio, obs_width_ratio, chart_height,
                               disable_page_breaks=True)
        
        if verbose:
            print(f"AFTER add_individual_chart: Page {pdf.page}, Y: {pdf.get_y()}")

    return pdf.output(dest='S')


def generate_pdf_simple(df_jugador, df_anthropometrics, 
                        figs_dict, fecha_actual, 
                        idioma="es", observaciones_dict=None, 
                        fig_params_dict=None):
    """Simple report - Fixed to include all required charts"""
    simple_figs = {}
    # Add all available figures that should be in simple report
    required_charts = ["Peso y Grasa", "CMJ", "SPRINT 0-40", "AGILIDAD"]
    
    for chart_name in required_charts:
        if chart_name in figs_dict and figs_dict[chart_name] is not None:
            simple_figs[chart_name] = figs_dict[chart_name]
    
    return generate_pdf_unified(
        df_jugador, df_anthropometrics, None, None, None, None, None,
        simple_figs, fecha_actual, idioma, observaciones_dict, "simple",
        fig_params_dict=fig_params_dict
    )

def generate_pdf_avanzado(df_jugador, df_anthropometrics, df_agilty, df_sprint, df_cmj, df_yoyo, 
                          df_rsa, figs_dict, fecha_actual, idioma="es", observaciones_dict=None, 
                          fig_params_dict=None):
    """Advanced report - matches original logic"""
    return generate_pdf_unified(
        df_jugador, df_anthropometrics, df_agilty, df_sprint, df_cmj, df_yoyo, df_rsa,
        figs_dict, fecha_actual, idioma, observaciones_dict, "advanced",
        fig_params_dict=fig_params_dict
    )