from fpdf import FPDF
import requests
import tempfile
from utils import util
from PIL import Image
from io import BytesIO
import tempfile
import plotly.io as pio
from utils import traslator

class PDF(FPDF):
    def __init__(self, fecha_actual, idioma="es"):
        super().__init__()
        self.idioma = idioma  # Idioma predeterminado para traducciones
        self.fecha_actual = fecha_actual

        if(idioma == "ar"):
            self.add_font("Amiri", "", "assets/fonts/Amiri-0.111/Amiri-Regular.ttf", uni=True)  # Añadir fuente Unicode
            self.add_font("Amiri", "B", "assets/fonts/Amiri-0.111/Amiri-Bold.ttf", uni=True)
            self.add_font("Amiri", "I", "assets/fonts/Amiri-0.111/Amiri-Slanted.ttf", uni=True)
            self.set_font("Amiri", "", 12)

        self.add_font("DejaVu", "", "assets/fonts/dejavu-2.37/DejaVuSans.ttf", uni=True)  # Añadir fuente Unicode
        self.add_font("DejaVu", "B", "assets/fonts/dejavu-2.37/DejaVuSans-Bold.ttf", uni=True)
        
    def footer(self):
        # Posición a 15 mm del final de la página
        self.set_y(-15)
        self.set_font("Arial", "I", 8)
        self.set_text_color(150, 150, 150)
        self.cell(0, 10, f"Página {self.page_no()}", align="C")

    def header(self):
        
        # Dibujar solo el borde inferior del header
        self.set_draw_color(0, 0, 0)     # Color del borde: negro
        self.set_line_width(0.5)         # Grosor de la línea

        x = 5                            # Coordenada X inicial
        y = 5                            # Coordenada Y del rectángulo superior
        w = 200                          # Ancho del rectángulo
        h = 30                           # Alto del rectángulo

        # Línea inferior → de (x, y+h) a (x+w, y+h)
        self.line(x, y + h, x + w, y + h)

        # Color de fondo azul oscuro
        #self.set_fill_color(13, 27, 62)  # #0d1b3e
        #self.rect(0, 0, 210, 40, 'F')  # Rectángulo superior

        # Logo (izquierda)
        self.image("assets/images/marcet.png", 10, 8, 33)

        # Texto cabecera derecha
        self.set_text_color(0, 0, 0)
        if(self.idioma == "ar"):
            self.set_font("Amiri", "I", 8)
        else:
            self.set_font("Arial", "I", 8)
        
        self.set_xy(120, 8)
        self.cell(80, 5, traslator.traducir("DEPARTAMENTO DE OPTIMIZACIÓN DEL RENDIMIENTO DEPORTIVO", self.idioma), align="R")

        # Título central
        if(self.idioma == "ar"):
            self.set_font("Amiri", "B", 14)
        else:
            self.set_font("Arial", "B", 14)
        
        self.set_text_color(249, 178, 51)  # amarillo
        self.set_xy(0, 14)
        self.cell(210, 10, traslator.traducir("INFORME INDIVIDUAL - INFORME FÍSICO", self.idioma), align="C")
        
        self.set_text_color(0, 0, 0)
        self.set_xy(0, 24)
        self.cell(210, 10, traslator.traducir("FECHA", self.idioma) + ":" + self.fecha_actual, align="C")
        
        #self.set_xy(0, 25)
        #self.cell(210, 10, self.idioma, align="C")

        #self.ln(5)

    def add_player_block(self, df, idioma="es"):

        # === Borde alrededor del bloque ===
        pdf_x = 5
        pdf_y = 43
        pdf_w = 200
        pdf_h = 60

        self.set_draw_color(0, 0, 0)
        self.set_line_width(0.5)

        # Línea inferior del "rectángulo"
        #self.line(pdf_x, pdf_y + pdf_h, pdf_x + pdf_w, pdf_y + pdf_h)

        # Extraer la primera fila como diccionario
        data = df.iloc[0].to_dict()

        # === Imagen del jugador ===
        foto_path = str(data.get("FOTO PERFIL", ""))

        imagen_insertada = False

        if foto_path.startswith("https"):
            try:
                response = requests.get(foto_path)
                if response.status_code == 200:
                    with tempfile.NamedTemporaryFile(suffix=".png", delete=False) as tmp_file:
                        tmp_file.write(response.content)
                        self.image(tmp_file.name, x=10, y=48, w=35)
                        imagen_insertada = True
            except Exception as e:
                print("Error cargando imagen desde URL:", e)

        elif foto_path and isinstance(foto_path, str):
            try:
                self.image(foto_path, x=10, y=45, w=40)
                imagen_insertada = True
            except:
                pass

        if not imagen_insertada:
            gender = data["GENERO"]
            if gender == "H":
                self.image("assets/images/male.png", 8, 55, 40)
            elif gender == "M":
                self.image("assets/images/female.png", 8, 55, 40)
            else:
                self.image("assets/images/profile.png", 8, 55, 40)
            
        # Nombre
        if(idioma == "ar"):
            self.set_font("Amiri", "B", 10)
        else:
            self.set_font("Arial", "B", 18)
        #self.set_fill_color(0, 51, 102)
        self.set_text_color(0, 0, 0)
        self.set_xy(10, 40)
        self.cell(140, 10, data["JUGADOR"], ln=False)
        #self.cell(0, 8, title, ln=True, fill=True)

        # Datos personales
        if(idioma == "ar"):
            self.set_font("Amiri", "B", 10)
        else:
            self.set_font("Arial", "B", 10)
        self.set_xy(50, 55)
        self.cell(37, 6, traslator.traducir("ID", idioma)+":", 0)
        
        if(idioma == "ar"):
            self.set_font("Amiri", "", 10)
        else:
            self.set_font("Arial", "", 10)
        self.cell(50, 6, str(traslator.traducir(data["ID"], idioma)).upper(), ln=True)

        if(idioma == "ar"):
            self.set_font("Amiri", "B", 10)
        else:
            self.set_font("Arial", "B", 10)
        self.set_x(50)
        
        self.cell(37, 6, traslator.traducir("NACIONALIDAD", idioma)+":", 0)
        
        if(idioma == "ar"):
            self.set_font("Amiri", "", 10)
        else:
            self.set_font("DejaVu", "", 10)
        
        if data["NACIONALIDAD"].upper() == "NO DISPONIBLE":
            self.cell(50, 6, traslator.traducir("No Disponible", idioma).upper(), ln=True)
        else:
            self.cell(50, 6, traslator.traducir_pais(data["NACIONALIDAD"].upper(), idioma).upper(), ln=True)

        if(idioma == "ar"):
            self.set_font("Amiri", "B", 10)
        else:
            self.set_font("Arial", "B", 10)
        
        self.set_x(50)
        self.cell(37, 6, traslator.traducir("F. DE NACIMIENTO", idioma)+":", 0)
        
        if(idioma == "ar"):
            self.set_font("Amiri", "", 10)
        else:
            self.set_font("Arial", "", 10)
        
        self.cell(50, 6, traslator.traducir(data["FECHA DE NACIMIENTO"], idioma).upper(), ln=True)

        if(idioma == "ar"):
            self.set_font("Amiri", "B", 10)
        else:
            self.set_font("Arial", "B", 10)
        self.set_x(50)
        self.cell(37, 6, traslator.traducir("EDAD", idioma)+":", 0)

        if(idioma == "ar"):
            self.set_font("Amiri", "", 10)
        else:        
            self.set_font("Arial", "", 10)
        self.cell(50, 6, traslator.traducir(str(data.get("EDAD", "")), idioma).upper(), ln=True)

        if(idioma == "ar"):
            self.set_font("Amiri", "B", 10)
        else:
            self.set_font("Arial", "B", 10)
        self.set_x(50)
        self.cell(37, 6, traslator.traducir("DEMARCACIÓN", idioma)+":", 0)
        
        if(idioma == "ar"):
            self.set_font("Amiri", "", 10)
        else:
            self.set_font("Arial", "", 10)
        self.cell(50, 6, traslator.traducir(data["DEMARCACION"], idioma).upper(), ln=True)

        if(idioma == "ar"):
            self.set_font("Amiri", "B", 10)
        else:
            self.set_font("Arial", "B", 10)
        
        self.set_x(50)
        self.cell(37, 6, traslator.traducir("CATEGORIA", idioma)+":", 0)
        if(idioma == "ar"):
            self.set_font("Amiri", "", 10)
        else:
            self.set_font("Arial", "", 10)
        self.cell(50, 6, traslator.traducir(data["CATEGORIA"].upper(), idioma).upper(), ln=True)

        if(idioma == "ar"):
            self.set_font("Amiri", "B", 10)
        else:
            self.set_font("Arial", "B", 10)
        
        self.set_x(50)
        self.cell(37, 6, traslator.traducir("EQUIPO", idioma)+":", 0)
        
        if(idioma == "ar"):
            self.set_font("Amiri", "", 10)
        else:
            self.set_font("Arial", "", 10)
        self.cell(50, 6, traslator.traducir(data["EQUIPO"], idioma).upper(), ln=True)

        # Imagen del campo (derecha)
        #self.image("assets/images/test/505.jpg", 130, 50, 70)

        demarcacion_larga = data.get("DEMARCACION", "").upper()
        MAPA_DEMARCACIONES = util.get_demarcaciones()
        codigod = MAPA_DEMARCACIONES.get(demarcacion_larga)

        if codigod:
            img_path = f"assets/images/pitch/campo_{codigod}.png"
            try:
                self.image(img_path, x=130, y=50, w=70)
            except:
                txt = f"Imagen para {codigod} no encontrada"
                self.cell(0, 6, txt, ln=True)

        self.ln(2)

    def add_img(self, img_path, x, y, w):
        self.image(img_path, x, y, w)

    def section_title(self, title, idioma="es", simple=False):
        
        self.set_fill_color(0, 51, 102)
        self.set_text_color(255, 255, 255)
        
        if simple:
            lenght = 95
            size = 8
        else:
            lenght = 0
            size = 11

        if(idioma == "ar"):
            self.set_font("Amiri", "B", size)
        else:
            self.set_font("Arial", "B", size)
        

        self.cell(lenght, 8, title, ln=True, fill=True)

        self.set_text_color(0, 0, 0)
        self.ln(2)

    def section_subtitle(self, subtitle, idioma="es"):
        if(idioma == "ar"):
            self.set_font("Amiri", "B", 10)
        else:
            self.set_font("Arial", "B", 10)
        
        self.set_text_color(0, 51, 102)  # Azul oscuro para continuidad visual
        self.cell(0, 6, subtitle, ln=True)
        self.set_text_color(0, 0, 0)
        self.ln(1)

    def add_key_value_block(self, data_dict, col_width=60):
        self.set_font("Arial", "", 10)
        for key, val in data_dict.items():
            self.cell(col_width, 8, f"{key}:", 0, 0)
            self.cell(0, 8, str(val), ln=True)

    def add_table(self, headers, rows, col_width=35):
        self.set_font("Arial", "B", 10)
        for header in headers:
            self.cell(col_width, 8, header, 1, 0, 'C')
        self.ln()
        self.set_font("Arial", "", 10)
        for row in rows:
            for item in row:
                self.cell(col_width, 8, str(item), 1, 0, 'C')
            self.ln()
        self.ln(2)

    def add_test_results(self, tests):
        self.set_font("Arial", "", 10)
        for key, val in tests.items():
            self.cell(60, 8, f"{key}:", 0, 0)
            self.cell(0, 8, str(val), ln=True)

    def add_reference(self, text):
        self.ln(5)
        self.set_font("Arial", "I", 8)
        self.multi_cell(0, 5, text)

    def add_imc_table(self, categoria_jugador, x, y):
        self.set_xy(x, y)

        # Datos simplificados
        rangos = ["< 18.5", "18.5 - 24.9", "25 - 29.9", "> 30"]
        clasificaciones = ["PESO BAJO", "PESO NORMAL", "SOBREPESO", "OBESIDAD"]
        colores = [
            (255, 255, 102),   # amarillo claro
            (52, 235, 58),     # verde #34eb3a
            (255, 165, 0),     # naranja
            (255, 0, 0)        # rojo
        ]

        # Encabezado
        self.set_font("Arial", "B", 10)
        self.set_fill_color(38, 50, 56)  # gris oscuro
        self.set_text_color(255, 255, 255)
        self.cell(35, 8, "IMC (kg/m2)", 1, 0, 'C', fill=True)
        self.cell(45, 8, "CLASIFICACIÓN", 1, 1, 'C', fill=True)

        # Filas
        self.set_font("Arial", "", 10)
        for i, (rango, clasificacion) in enumerate(zip(rangos, clasificaciones)):
            # === COLUMNA 1: RANGO con color fondo ===
            r, g, b = colores[i]
            self.set_x(x)
            self.set_fill_color(r, g, b)
            self.set_text_color(0, 0, 0)
            self.set_font("Arial", "", 10)
            self.cell(35, 8, rango, 1, 0, 'C', fill=True)

            # === COLUMNA 2: Clasificación ===
            if categoria_jugador.upper() in clasificacion.upper():
                self.set_fill_color(r, g, b)
                self.set_font("Arial", "B", 10)
            else:
                self.set_fill_color(255, 255, 255)
                self.set_font("Arial", "", 10)

            self.cell(45, 8, clasificacion, 1, 1, 'C', fill=True)

        # Pie
        self.ln(1)
        self.set_text_color(0, 0, 0)
        self.set_font("Arial", "I", 7)
        self.set_x(x)
        self.multi_cell(0, 5, "Clasificación del IMC basada en criterios generales de salud.")
    
    def add_percentile_semaforo_table(self, jugador: dict, percentiles: dict, x, y, wm=30, wv=20, wi=50, footer=None):
        self.set_xy(x, y)

        self.set_font("Arial", "B", 10)
        self.set_fill_color(38, 50, 56)  # encabezado gris oscuro
        self.set_text_color(255, 255, 255)

        # Encabezado
        self.cell(wm, 8, "MÉTRICA", 1, 0, 'C', fill=True)
        self.cell(wv, 8, "VALOR", 1, 0, 'C', fill=True)
        #self.cell(25, 8, "PERCENTIL", 1, 0, 'C', fill=True)
        self.cell(wi, 8, "INTERPRETACIÓN", 1, 1, 'C', fill=True)

        self.set_font("Arial", "", 10)

        for metrica, percentil in percentiles.items():
            color, texto = util.obtener_color_percentil(percentil)
            valor_real = jugador.get(metrica, "")
            #print(valor_real)

            # Columna: MÉTRICA
            self.set_x(x)
            self.set_fill_color(245, 245, 245)
            self.set_text_color(0, 0, 0)
            self.cell(wm, 8, metrica, 1, 0, 'C', fill=True)

            # Columna: VALOR
            r, g, b = color
            self.set_fill_color(r, g, b)
            self.set_text_color(0, 0, 0)
            self.cell(wv, 8, f"{valor_real}", 1, 0, 'C', fill=True)

            # Columna: PERCENTIL (color tipo semáforo)
            #r, g, b = color
            #self.set_fill_color(r, g, b)
            #self.set_text_color(0, 0, 0)
            #self.cell(25, 8, f"{percentil:.1f}", 1, 0, 'C', fill=True)

            # Columna: Interpretación
            self.set_fill_color(r, g, b)
            self.set_text_color(0, 0, 0)
            self.cell(wi, 8, texto, 1, 1, 'C', fill=True)

        if footer:
            # Nota inferior
            self.ln(2)
            self.set_font("Arial", "I", 8)
            #self.sety(y)
            self.multi_cell(0, 5, footer)

    def add_indices_table(self, jugador: dict, x, y):
        self.set_xy(x, y)
        # Encabezado
        self.set_font("Arial", "B", 10)
        self.set_fill_color(38, 50, 56)
        self.set_text_color(255, 255, 255)
        self.cell(30, 8, "MÉTRICA", 1, 0, 'C', fill=True)
        self.cell(20, 8, "VALOR", 1, 0, 'C', fill=True)
        self.cell(35, 8, "CLASIFICACIÓN", 1, 1, 'C', fill=True)

        # Datos
        filas = [
            ("IMC", jugador.get("IMC"), jugador.get("Categoría IMC")),
            ("Índice de Grasa", jugador.get("Índice de grasa"), jugador.get("Categoría Grasa"))
        ]

        self.set_font("Arial", "", 10)
        self.set_text_color(0, 0, 0)

        for metrica, valor, clasificacion in filas:
            # Columna: MÉTRICA
            self.set_x(x)
            self.set_fill_color(245, 245, 245)
            self.cell(30, 8, metrica, 1, 0, 'C', fill=True)

            # Columna: VALOR
            r, g, b = util.get_rgb_from_categoria(clasificacion)
            self.set_fill_color(r, g, b)
            self.cell(20, 8, f"{valor:.2f}" if valor is not None else "-", 1, 0, 'C', fill=True)

            # Columna: CLASIFICACIÓN con color dinámico
            self.set_fill_color(r, g, b)
            self.cell(35, 8, clasificacion or "-", 1, 1, 'C', fill=True)

        # Pie de tabla
        self.ln(2)
        self.set_x(x)
        self.set_font("Arial", "I", 8)
        self.multi_cell(0, 5, "Índices calculados a partir de las mediciones antropométricas.")

    def draw_gradient_scale(self, x=10, y=None, width=190, height=6, steps=100, invertido=False, idioma="es"):
        
        if y is None:
            y = self.get_y()

        step_width = width / steps

        for i in range(steps):
            t = i / (steps - 1)  # Normalizado [0, 1]
            if invertido:
                t = 1 - t  # Invertir el gradiente

            r = int(255 * (1 - t))  # Rojo decrece (o crece si invertido)
            g = int(255 * t)        # Verde crece (o decrece si invertido)
            b = 0                   # Azul fijo en 0

            self.set_fill_color(r, g, b)
            self.rect(x + i * step_width, y, step_width, height, 'F')

        self.set_xy(x - 1, y - height - 1.5)
        if(idioma == "ar"):
            self.set_font("Amiri", "B", 10)
        else:
            self.set_font("Arial", "B", 10)
        self.set_text_color(0, 51, 102)
        self.cell(0, 6, util.traducir("Escala de valoración", idioma), ln=True)
        self.set_text_color(0, 0, 0)
        self.ln(1)

        # Etiquetas
        self.set_xy(x, y + height + 1.5)

        if(idioma == "ar"):
            self.set_font("Amiri", "", 8)
        else:
            self.set_font("Arial", "", 8)

        optimo = util.traducir("Óptimo", idioma)
        promedio = util.traducir("Promedio", idioma)
        critico = util.traducir("Crítico", idioma)

        if invertido:
            self.cell(30, 5, optimo, 0, 0, 'L')
            self.set_x(x + width/2 - 15)
            self.cell(30, 5, promedio, 0, 0, 'C')
            self.set_x(x + width - 30)
            self.cell(30, 5, critico, 0, 1, 'R')
        else:
            self.cell(30, 5, critico, 0, 0, 'L')
            self.set_x(x + width/2 - 15)
            self.cell(30, 5, promedio, 0, 0, 'C')
            self.set_x(x + width - 30)
            self.cell(30, 5, optimo, 0, 1, 'R')

    def get_height(self):
        return self.h
    
    def get_altura(self):
        return self.get_y()
    
    # def add_plotly_figure(self, fig, title=None, w=190, idioma="es"):
    #     if title:
    #         if(idioma == "ar"):
    #             self.set_font("Amiri", "", 10)
    #         else:
    #             self.set_font("Arial", "B", 12)
            
    #         self.cell(0, 10, title, ln=True)

    #     # Convertir la figura a imagen en memoria
    #     image_bytes = pio.to_image(fig, format="png", width=900, height=450, scale=2)

    #     # Crear archivo temporal
    #     with tempfile.NamedTemporaryFile(suffix=".png", delete=False) as tmpfile:
    #         tmpfile.write(image_bytes)
    #         tmpfile.flush()
    #         tmpfile_path = tmpfile.name

    #     # Insertar en PDF
    #     self.image(tmpfile_path, x=None, y=None, w=w)

    #     # Eliminar el archivo temporal manualmente
    #     import os
    #     os.remove(tmpfile_path)

    def add_last_measurements(self, altura, peso, grasa, icon_path=None, idioma="es", simple=False):
        if(idioma == "ar"):
            self.set_font("Amiri", "", 10)
        else:
            self.set_font("Helvetica", "B", 14)

        if icon_path:
            self.image(icon_path, x=self.get_x(), y=self.get_y(), w=6)
            self.cell(8)

        #self.cell(0, 10, "Últimas Mediciones", ln=1)

        self.ln(1.5)

        if(idioma == "ar"):
            self.set_font("Amiri", "", 10)
        else:
            self.set_font("Helvetica", "", 10)

        # Posiciones base
        x_start = self.get_x()
        y_start = self.get_y() - 3

        col_width = 60  # ajustable

        def add_metric(label, value, x, idioma="es"):
            self.set_xy(x, y_start)
            if(idioma == "ar"):
                self.set_font("Amiri", "", 10)
            else:
                self.set_font("Helvetica", "", 10)
            
            self.set_text_color(0, 0, 0)
            self.cell(col_width, 6, label, align="C")
            self.set_xy(x, y_start + (3 if simple else 6))

            if(idioma == "ar"):
                self.set_font("Amiri", "B", 15 if simple else 18)
            else:
                self.set_font("Helvetica", "B", 15 if simple else 18)

            self.set_text_color(0, 51, 102) # Azul oscuro
            self.cell(col_width, 10, f"{value:.2f}", align="C")
            

        x1 = x_start
        x2 = x1 + col_width + 0
        x3 = x2 + col_width + 0

        add_metric(traslator.traducir("ALTURA (CM)",idioma), altura, x1, idioma)
        add_metric(traslator.traducir("PESO (KG)",idioma), peso, x2, idioma)
        add_metric(traslator.traducir("GRASA (%)",idioma), grasa, x3, idioma)

        self.ln(7)  # salto tras bloque

    def add_plotly_figure(self, fig, title=None, x=None, y=None, w=190, h=100, idioma="es"):
        #import plotly.io as pio
        #import tempfile
        import os

        if title:
            if idioma == "ar":
                self.set_font("Amiri", "", 10)
            else:
                self.set_font("Arial", "B", 12)
            self.cell(0, 10, title, ln=True)

        # Convertir la figura a imagen PNG
        image_bytes = pio.to_image(fig, format="png", width=900, height=450, scale=2)

        # Crear archivo temporal
        with tempfile.NamedTemporaryFile(suffix=".png", delete=False) as tmpfile:
            tmpfile.write(image_bytes)
            tmpfile.flush()
            tmpfile_path = tmpfile.name

        # Insertar en PDF con posición personalizada si se proporciona
        if x is not None and y is not None:
            self.image(tmpfile_path, x=x, y=y, w=w, h=h)
        elif x is not None:
            self.image(tmpfile_path, x=x, w=w, h=h)
        else:
            self.image(tmpfile_path, w=w, h=h)

        # Eliminar archivo temporal
        os.remove(tmpfile_path)

    def add_observation_block(self, title="OBSERVACIONES:", text="", x=None, y=None, font_size=8, style="I", w=90):
        """
        Añade un bloque de observaciones debajo de un gráfico o en cualquier parte.

        Parameters:
            title (str): Título de la sección de observaciones.
            text (str): Texto de las observaciones.
            x (float): Posición X. Si None, se mantiene la actual.
            y (float): Posición Y. Si None, se mantiene la actual.
            font_size (int): Tamaño de fuente.
            style (str): Estilo de fuente: "", "B", "I", "BI".
            w (int): Ancho del bloque.
        """
        if x is not None and y is not None:
            self.set_xy(x, y)
        
        self.set_font("Arial", "B", font_size)
        self.cell(w, 5, title, ln=True)

        self.set_font("Arial", style, font_size)
        self.multi_cell(w, 4, text)
        self.ln(2)