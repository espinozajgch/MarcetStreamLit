import streamlit as st
import pandas as pd
from fpdf import FPDF
import numpy as np
import requests
from datetime import datetime
from utils.pdf import PDF
from utils import util
from datetime import date

def add_footer(pdf, invertido=False, idioma="es"):

    page_height = pdf.get_height()
    margen_inferior = 33
    y_final = page_height - margen_inferior
    pdf.draw_gradient_scale(x=10, y=y_final, invertido=True, idioma=idioma)

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
    pdf.cell(0, 6, util.traducir("Observaciones", idioma).upper(), ln=True)

    if(idioma == "ar"):
        pdf.set_font("Amiri", "", 10)
    else:
        pdf.set_font("Arial", "", 10)
        
    pdf.set_text_color(0, 0, 0)
    pdf.multi_cell(0, 5, texto)

def generate_pdf_avanzado(df_jugador, df_anthropometrics, df_agilty, df_sprint, df_cmj, df_yoyo, 
                          df_rsa, figs_dict, fecha_actual, idioma="es", observaciones_dict=None):
    pdf = PDF(fecha_actual=fecha_actual, idioma=idioma)
    pdf.add_page()
    pdf.header()
    
    #pdf.add_font("ArialUnicode", "", "assets/fonts/Amiri-0.111/Amiri-Regular.ttf", uni=True)
    #pdf.set_font("ArialUnicode", "", 12)

    # Bloque de datos personales
    pdf.add_player_block(df_jugador, idioma=idioma)

    seccion_ya_impresa = set()

    # Preparar secciones
    secciones = [
        ("COMPOSICIÓN CORPORAL", df_anthropometrics, [
            ("Altura", figs_dict.get("Altura")),
            ("Peso y Grasa", figs_dict.get("Peso y Grasa"))
        ]),
        ("POTENCIA MUSCULAR (SALTO CON CONTRAMOVIMIENTO)", df_cmj, [
            ("CMJ", figs_dict.get("CMJ"))
        ]),
        ("EVOLUCIÓN DEL SPRINT (0-5M)", df_sprint, [
            ("SPRINT 0-5", figs_dict.get("SPRINT 0-5"))
        ]),
        ("EVOLUCIÓN DEL SPRINT (0-40M)", df_sprint, [
            ("SPRINT 0-40", figs_dict.get("SPRINT 0-40"))
        ]),
        ("VELOCIDAD EN EL CAMBIO DE DIRECCIÓN (AGILIDAD 505)", df_agilty, [
            ("AGILIDAD", figs_dict.get("AGILIDAD"))
        ]),
        ("RESISTENCIA INTERMITENTE DE ALTA INTENSIDAD (YO-YO TEST)", df_yoyo, [
            ("YO-YO", figs_dict.get("YO-YO"))
        ]),
        ("CAPACIDAD DE REALIZAR SPRINT'S REPETIDOS (RSA)", df_rsa, [
            ("RSA Tiempo", figs_dict.get("RSA Tiempo")),
            ("RSA Velocidad", figs_dict.get("RSA Velocidad"))
        ])
    ]

    #st.dataframe(secciones)

    # Comprobar si "COMPOSICIÓN CORPORAL" está en los gráficos seleccionados
    tiene_composicion = any(
        nombre_seccion == "COMPOSICIÓN CORPORAL" and any(fig for _, fig in figuras)
        for nombre_seccion, _, figuras in secciones
    )

    # Agregar medidas si se seleccionó "COMPOSICIÓN CORPORAL"
    if tiene_composicion and df_anthropometrics is not None and not df_anthropometrics.empty:
        altura = df_anthropometrics['ALTURA (CM)'].iloc[0]
        peso = df_anthropometrics['PESO (KG)'].iloc[0]
        grasa = df_anthropometrics['GRASA (%)'].iloc[0]
        #pdf.section_title("COMPOSICIÓN CORPORAL")
        pdf.section_title(util.traducir("COMPOSICIÓN CORPORAL", idioma), idioma)
        pdf.add_last_measurements(altura, peso, grasa, idioma=idioma)
        pdf.ln(5)
    # Inicializar contador de gráficos y sección actual
    contador_graficos = 0
    primer_grafico_insertado = False

    # Insertar gráficos de forma ordenada
    for nombre_seccion, df_seccion, figuras in secciones:
        if df_seccion is not None and not df_seccion.empty:
            for nombre_fig, fig in figuras:
                if fig is not None:
                    if not primer_grafico_insertado:
                        if not tiene_composicion and nombre_seccion not in seccion_ya_impresa:
                            #pdf.section_title(nombre_seccion)
                            pdf.section_title(util.traducir(nombre_seccion, idioma), idioma)
                            seccion_ya_impresa.add(nombre_seccion)
                        pdf.add_plotly_figure(fig, "", idioma=idioma)
                        #obs_text = observaciones_dict.get(nombre_seccion, "").strip().replace("\n"," ")

                        add_footer(pdf, idioma=idioma)
                        primer_grafico_insertado = True
                        continue

                    if contador_graficos % 2 == 0:
                        pdf.add_page()
                        pdf.ln(20)

                    if nombre_seccion not in seccion_ya_impresa:
                        #pdf.section_title(nombre_seccion)
                        pdf.section_title(util.traducir(nombre_seccion, idioma), idioma)
                        seccion_ya_impresa.add(nombre_seccion)

                    pdf.add_plotly_figure(fig, "", idioma=idioma)
                    contador_graficos += 1

                    if contador_graficos % 2 == 0:
                        add_footer(pdf, idioma=idioma)

    if contador_graficos % 2 == 1:
        add_footer(pdf, idioma=idioma)

    return pdf.output(dest='S') #.encode('utf-8')

# def generate_pdf_simple(df_jugador, df_anthropometrics, df_agilty, df_sprint, df_cmj, df_yoyo, df_rsa, figs_dict, fecha_actual, idioma="es"):
    
#     pdf = PDF(fecha_actual=fecha_actual, idioma=idioma)
#     pdf.add_page()
#     pdf.header()
#     pdf.add_player_block(df_jugador, idioma=idioma)

#     seccion_ya_impresa = set()

#     # Datos de medición (altura/peso/grasa)
#     if df_anthropometrics is not None and not df_anthropometrics.empty:
#         altura = df_anthropometrics['ALTURA (CM)'].iloc[0]
#         peso = df_anthropometrics['PESO (KG)'].iloc[0]
#         grasa = df_anthropometrics['GRASA (%)'].iloc[0]
#         pdf.section_title(util.traducir("COMPOSICIÓN CORPORAL", idioma), idioma)
#         pdf.add_last_measurements(altura, peso, grasa, idioma=idioma)

#     # Preparar lista de figuras disponibles
#     graficos = []
#     if figs_dict.get("Peso y Grasa"):
#         graficos.append(("Peso y % Grasa", figs_dict["Peso y Grasa"]))
#     if figs_dict.get("CMJ"):
#         graficos.append(("POTENCIA MUSCULAR (SALTO CON CONTRAMOVIMIENTO)", figs_dict["CMJ"]))
#     if figs_dict.get("SPRINT 0-40"):
#         graficos.append(("SPRINT (0-40M)", figs_dict["SPRINT 0-40"]))
#     if figs_dict.get("AGILIDAD"):
#         graficos.append(("VELOCIDAD EN EL CAMBIO DE DIRECCIÓN (AGILIDAD 505)", figs_dict["AGILIDAD"]))

#     # Mostrar gráficos: 2 por fila
#     i = 0
#     while i < len(graficos):
#         if i % 2 == 0:
#             pdf.ln(5)

#         y_titulo = pdf.get_y()

#         for col in range(2):
#             if i + col >= len(graficos):
#                 break
#             titulo, fig = graficos[i + col]
#             x = 10 if col == 0 else 105
#             pdf.set_xy(x, y_titulo)
#             pdf.section_title(util.traducir(titulo.upper(), idioma), idioma, simple=True)

#         #pdf.ln(5)
#         y_grafico = pdf.get_y()

#         for col in range(2):
#             if i + col >= len(graficos):
#                 break
#             _, fig = graficos[i + col]
#             x = 10 if col == 0 else 105
#             pdf.add_plotly_figure(fig, "", x=x-3, y=y_grafico-2, w=99, h=55, idioma=idioma)

#         pdf.ln(48)  # espacio para la fila de gráficos
#         i += 2

#     add_footer_con_texto(pdf, "", idioma=idioma)
#     return pdf.output(dest='S')

def generate_pdf_simple(
    df_jugador,
    df_anthropometrics,
    figs_dict,
    fecha_actual,
    idioma="es",
    observaciones_dict=None
):
    pdf = PDF(fecha_actual=fecha_actual, idioma=idioma)
    pdf.add_page()
    pdf.header()
    pdf.add_player_block(df_jugador, idioma=idioma)

    if df_anthropometrics is not None and not df_anthropometrics.empty:
        altura = df_anthropometrics['ALTURA (CM)'].iloc[0]
        peso = df_anthropometrics['PESO (KG)'].iloc[0]
        grasa = df_anthropometrics['GRASA (%)'].iloc[0]
        pdf.section_title(util.traducir("COMPOSICIÓN CORPORAL", idioma), idioma)
        pdf.add_last_measurements(altura, peso, grasa, idioma=idioma)

    graficos = []
    if figs_dict.get("Peso y Grasa"):
        graficos.append(("Peso y % Grasa", figs_dict["Peso y Grasa"]))
    if figs_dict.get("CMJ"):
        graficos.append(("POTENCIA MUSCULAR (SALTO CON CONTRAMOVIMIENTO)", figs_dict["CMJ"]))
    if figs_dict.get("SPRINT 0-40"):
        graficos.append(("SPRINT (0-40M)", figs_dict["SPRINT 0-40"]))
    if figs_dict.get("AGILIDAD"):
        graficos.append(("VELOCIDAD EN EL CAMBIO DE DIRECCIÓN (AGILIDAD 505)", figs_dict["AGILIDAD"]))

    if observaciones_dict is None:
        observaciones_dict = {}

    i = 0
    while i < len(graficos):
        if i % 2 == 0:
            pdf.ln(3)

        y_titulo = pdf.get_y()

        # Títulos
        for col in range(2):
            if i + col >= len(graficos):
                break
            titulo, _ = graficos[i + col]
            x = 10 if col == 0 else 105
            pdf.set_xy(x, y_titulo)
            pdf.section_title(util.traducir(titulo.upper(), idioma), idioma, simple=True)

        # Gráficos
        y_grafico = pdf.get_y()
        for col in range(2):
            if i + col >= len(graficos):
                break
            _, fig = graficos[i + col]
            x = 10 if col == 0 else 105
            pdf.add_plotly_figure(fig, "", x=x-3, y=y_grafico-3, w=99, h=55, idioma=idioma)

        # Observaciones inmediatamente debajo
        y_obs = pdf.get_y() + 52
        obs_width = 92
        obs_height_max = 7
        obs_line_height = 3

        for col in range(2):
            if i + col >= len(graficos):
                break

            titulo, _ = graficos[i + col]
            x = 9 if col == 0 else 103
            obs_text = observaciones_dict.get(titulo, "").strip().replace("\n"," ")

            # Título observaciones
            pdf.set_xy(x, y_obs)
            #pdf.set_font("Arial", "B", 5)
            if(idioma == "ar"):
                pdf.set_font("Amiri", "B", 5)
            else:
                pdf.set_font("Arial", "B", 5)
            #pdf.cell(obs_width, 3, "OBSERVACIONES:", ln=False)

            # Texto observaciones
            #pdf.set_font("Arial", "I", 6.6)
            if(idioma == "ar"):
                pdf.set_font("Amiri", "I", 6.6)
            else:
                pdf.set_font("Arial", "I", 6.6)

            pdf.set_x(x)
            y_current = pdf.get_y()

            if obs_text:
                pdf.multi_cell(obs_width, obs_line_height, obs_text)
                altura_utilizada = pdf.get_y() - y_current
            else:
                altura_utilizada = 0

            # Rellenar espacio si sobra
            espacio_restante = obs_height_max - altura_utilizada
            if espacio_restante > 0:
                pdf.set_xy(x, y_current + altura_utilizada)
                lineas_extra = int(espacio_restante / obs_line_height)
                for _ in range(lineas_extra):
                    pdf.cell(obs_width, obs_line_height, "", ln=True)

        # Avanzar después de observaciones
        pdf.set_y(y_obs + obs_height_max)
        i += 2

    return pdf.output(dest='S')


