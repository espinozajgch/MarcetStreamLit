import streamlit as st
import pandas as pd
from utils import util
import re
from utils import traslator

def convert_drive_url(original_url):
    """
    Convierte una URL de Google Drive en una URL directa para acceder a la imagen,
    excepto si ya está en formato final o es None.
    """
    if original_url is None or not isinstance(original_url, str):
        return original_url

    # Si ya es una URL directa (uc?export=view&id=...), no hacer nada
    if "drive.google.com/uc?" in original_url:
        return original_url

    # Extraer ID de la URL tipo /file/d/<id>/view
    match = re.search(r"/d/([a-zA-Z0-9_-]+)", original_url)
    if match:
        file_id = match.group(1)
        return f"https://drive.google.com/uc?export=view&id={file_id}"

    return original_url  # Si no coincide, devuelve lo original


def player_block(df_datos_filtrado, df_datos, df_final, unavailable="N/A", idioma="es"):

    # Obtener ID del jugador seleccionado (único y limpio)
    ids_disponibles = df_datos_filtrado["ID"].dropna().astype(str).str.strip().unique().tolist()

    if not ids_disponibles or any(isinstance(id, str) and id.strip().lower() == 'nan' for id in ids_disponibles):

        # Crear combinación única de jugador + categoría
        df_datos_filtrado["JUGADOR_CATEGORIA"] = (
            df_datos_filtrado["JUGADOR"].astype(str).str.strip() + " - " +
            df_datos_filtrado["CATEGORIA"].astype(str).str.strip())

        # Lista de combinaciones únicas disponibles
        names_disponibles = df_datos_filtrado["JUGADOR_CATEGORIA"].dropna().unique().tolist()
        jugador_cat = names_disponibles[0]  # selección por defecto

        # Separar nombre y categoría desde la selección
        nombre_jugador, categoria_jugador = [x.strip() for x in jugador_cat.split(" - ")]

        # Filtrar DataFrames por nombre y categoría
        df_jugador = df_datos[
            (df_datos["JUGADOR"].astype(str).str.strip() == nombre_jugador) &
            (df_datos["CATEGORIA"].astype(str).str.strip() == categoria_jugador)
        ]
        df_joined_filtrado = df_final[
            (df_final["JUGADOR"].astype(str).str.strip() == nombre_jugador) &
            (df_final["CATEGORIA"].astype(str).str.strip() == categoria_jugador)
        ]

        # Manejo de valores nulos/vacíos
        id = unavailable
        df_jugador = df_jugador.applymap(lambda x: unavailable if pd.isna(x) or str(x).strip().lower() in ["nan", "none", ""] else x)

    else:
        jugador_id = ids_disponibles[0]
        # Filtrar los DataFrames por el ID seleccionado
        df_jugador = df_datos[df_datos["ID"].astype(str).str.strip() == jugador_id]
        df_joined_filtrado = df_final[df_final["ID"].astype(str).str.strip() == jugador_id]
        id = df_jugador['ID'].iloc[0]

    # Validar que exista al menos un registro para el jugador seleccionado
    if ids_disponibles or names_disponibles:
        
        nombre = df_jugador['JUGADOR'].iloc[0]
        nacionalidad = df_jugador['NACIONALIDAD'].iloc[0]
        categoria = df_jugador['CATEGORIA'].iloc[0]
        equipo = df_jugador['EQUIPO'].iloc[0]
        fnacimiento = df_jugador['FECHA DE NACIMIENTO'].iloc[0]
        edad = df_jugador['EDAD'].iloc[0]
        demarcacion = df_jugador['DEMARCACION'].iloc[0]
        genero =  df_jugador['GENERO'].iloc[0]
        color = "violet" if genero == "M" else "blue"
        
        if genero == "M":
            genero_icono = ":material/girl:"
        elif genero == "H":
            genero_icono = ":material/boy:"
        else:
            genero_icono = "" 

        if nacionalidad == unavailable:
            bandera = ""
        else:
            nb = "ESPANA" if nacionalidad.upper() == "ESPAÑA" else nacionalidad.upper()
            bandera = util.obtener_bandera(str(nb).replace(",", "."))

        st.markdown(f"## {nombre} {genero_icono}")
        st.markdown(f"##### **_:blue[ID:]_** _{id.upper()}_ | **_:blue[NACIONALIDAD:]_** _{traslator.traducir_pais(nacionalidad.upper(),idioma).upper()}_ {bandera} ")

        col1, col2, col3 = st.columns([1, 2, 2])

        with col1:
            url_drive = df_jugador['FOTO PERFIL'].iloc[0]

            if genero == "M":
                profile_image = "female" 
            elif genero == "H":
                profile_image = "male" 
            else:
                profile_image = "profile" 

            if pd.notna(url_drive) and url_drive and url_drive != "No Disponible":
                response = util.get_photo(url_drive)

                if response and response.status_code == 200 and 'image' in response.headers.get("Content-Type", ""):
                    st.image(response.content, width=150)
                else:
                    #"https://cdn-icons-png.flaticon.com/512/5281/5281619.png"
                    st.image(f"assets/images/{profile_image}.png", width=180)
            else:
                    #"https://cdn-icons-png.flaticon.com/512/5281/5281619.png"
                    st.image(f"assets/images/{profile_image}.png", width=180)
        with col2:

            if(categoria.upper() == "CHECK-IN") or (categoria.upper() == "CHECKIN") or (categoria.upper() == "CHECK IN"):

                st.metric(label=f":{color}[Categoría]", value=f" {traslator.traducir(categoria.upper(), idioma).capitalize()}", border=True)
                st.metric(label=f":{color}[F. Nacimiento]", value=f"{fnacimiento}", border=True)
                
                if isinstance(edad, (int, float)) and edad >= 16:
                    categoria = "Juvenil"
                else:
                    categoria = "Cadete"
                    
                equipo = "A"

            else:
                st.metric(label=f":{color}[Categoria - Equipo]", value=f" {traslator.traducir(categoria.upper(), idioma).capitalize()} {equipo}", border=True)
                st.metric(label=f":{color}[F. Nacimiento]", value=f"{fnacimiento}", border=True)

        with col3:
            anios = traslator.traducir("años",idioma)
            if edad != unavailable:
                edad = f"{edad:,.0f} {anios}"
            
            st.metric(label=f":{color}[Posición]", value=f"{traslator.traducir(demarcacion.upper(), idioma).capitalize()}", border=True)
            st.metric(label=f":{color}[Edad]", value=edad, border=True)

    else:
        st.warning("⚠️ No se encontró ningún ID válido en los datos filtrados.")

    return df_joined_filtrado, df_jugador, categoria, equipo, genero