import streamlit as st
import pandas as pd
from fpdf import FPDF
import numpy as np
import requests
from datetime import datetime
from utils.pdf import PDF
from utils import util

def add_footer(pdf, invertido=False, idioma="es"):

    page_height = pdf.get_height()
    margen_inferior = 33
    y_final = page_height - margen_inferior
    pdf.draw_gradient_scale(x=10, y=y_final, invertido=True, idioma=idioma)

def generate_pdf_avanzado(df_jugador, df_anthropometrics, df_agilty, df_sprint, df_cmj, df_yoyo, df_rsa, figs_dict, idioma="es"):
    pdf = PDF(idioma=idioma)
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

def generate_pdf_simple(df_jugador, df_anthropometrics, df_agilty, df_sprint, df_cmj, df_yoyo, df_rsa, figs_dict, idioma="es"):
    pdf = PDF(idioma=idioma)
    pdf.add_page()
    pdf.header()
    pdf.add_player_block(df_jugador, idioma=idioma)

    seccion_ya_impresa = set()

    # Datos de medición (altura/peso/grasa)
    if df_anthropometrics is not None and not df_anthropometrics.empty:
        altura = df_anthropometrics['ALTURA (CM)'].iloc[0]
        peso = df_anthropometrics['PESO (KG)'].iloc[0]
        grasa = df_anthropometrics['GRASA (%)'].iloc[0]
        pdf.section_title(util.traducir("COMPOSICIÓN CORPORAL", idioma), idioma)
        pdf.add_last_measurements(altura, peso, grasa, idioma=idioma)

    # Preparar lista de figuras disponibles
    graficos = []
    if figs_dict.get("Peso y Grasa"):
        graficos.append(("Peso y % Grasa", figs_dict["Peso y Grasa"]))
    if figs_dict.get("CMJ"):
        graficos.append(("POTENCIA MUSCULAR (SALTO CON CONTRAMOVIMIENTO)", figs_dict["CMJ"]))
    if figs_dict.get("SPRINT 0-40"):
        graficos.append(("SPRINT (0-40M)", figs_dict["SPRINT 0-40"]))
    if figs_dict.get("AGILIDAD"):
        graficos.append(("VELOCIDAD EN EL CAMBIO DE DIRECCIÓN (AGILIDAD 505)", figs_dict["AGILIDAD"]))

    # Mostrar gráficos: 2 por fila
    i = 0
    while i < len(graficos):
        if i % 2 == 0:
            pdf.ln(5)

        y_titulo = pdf.get_y()

        for col in range(2):
            if i + col >= len(graficos):
                break
            titulo, fig = graficos[i + col]
            x = 10 if col == 0 else 105
            pdf.set_xy(x, y_titulo)
            pdf.section_title(util.traducir(titulo.upper(), idioma), idioma, simple=True)

        #pdf.ln(5)
        y_grafico = pdf.get_y()

        for col in range(2):
            if i + col >= len(graficos):
                break
            _, fig = graficos[i + col]
            x = 10 if col == 0 else 105
            pdf.add_plotly_figure(fig, "", x=x, y=y_grafico, w=95, h=48, idioma=idioma)

        pdf.ln(48)  # espacio para la fila de gráficos
        i += 2

    add_footer(pdf, idioma=idioma)
    return pdf.output(dest='S')
