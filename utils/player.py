import streamlit as st
import pandas as pd
from utils import util

def player_block(df_datos_filtrado, df_datos, df_final, unavailable="N/A", idioma="es"):
    
    # Obtener ID del jugador seleccionado (único y limpio)
    ids_disponibles = df_datos_filtrado["ID"].dropna().astype(str).str.strip().unique().tolist()
    #st.dataframe(ids_disponibles)
    if not ids_disponibles or any(isinstance(id, str) and id.strip().lower() == 'nan' for id in ids_disponibles):
        names_disponibles = df_datos_filtrado["JUGADOR"].dropna().astype(str).str.strip().unique().tolist()
        jugador_id = names_disponibles[0]
        # Filtrar los DataFrames por el ID seleccionado
        df_jugador = df_datos[df_datos["JUGADOR"].astype(str).str.strip() == jugador_id]
        df_joined_filtrado = df_final[df_final["JUGADOR"].astype(str).str.strip() == jugador_id]
        id = unavailable

        df_jugador = df_jugador.fillna(unavailable)
    else:
        jugador_id = ids_disponibles[0]
        # Filtrar los DataFrames por el ID seleccionado
        df_jugador = df_datos[df_datos["ID"].astype(str).str.strip() == jugador_id]
        df_joined_filtrado = df_final[df_final["ID"].astype(str).str.strip() == jugador_id]
        id = df_jugador['ID'].iloc[0]

    # Validar que exista al menos un registro para el jugador seleccionado
    if ids_disponibles or names_disponibles:
        
        jugador = df_jugador.iloc[0]
        
        response = util.get_photo(df_jugador['FOTO PERFIL'].iloc[0])

        nombre = df_jugador['JUGADOR'].iloc[0]
        nacionalidad = df_jugador['NACIONALIDAD'].iloc[0]
        categoria = df_jugador['CATEGORIA'].iloc[0]
        equipo = df_jugador['EQUIPO'].iloc[0]
        fnacimiento = df_jugador['FECHA DE NACIMIENTO'].iloc[0]
        edad = df_jugador['EDAD'].iloc[0]
        demarcacion = df_jugador['DEMARCACION'].iloc[0]
        
        if edad != unavailable:
            edad = f"{edad:,.0f} años"

        if nacionalidad == unavailable:
            bandera = ""
        else:
            bandera = util.obtener_bandera(str(nacionalidad).replace(",", "."))

        #referencia = df_datos[df_datos["EDAD"] == jugador["EDAD"]]
        #referencia_test = df_data_test[df_data_test["ID"].isin(referencia["ID"])]
            
        # Mostrar DataFrame principal
        #st.dataframe(df_joined)
        #st.badge("New")
        #st.badge("Success", icon=":material/check:", color="green")

        st.markdown(f"## {nombre} ")
        st.markdown(f"##### **_:blue[ID:]_** _{id}_ | **_:blue[NACIONALIDAD:]_** _{nacionalidad}_ {bandera}")

        col1, col2, col3 = st.columns([1, 2, 2])

        with col1:
            if response:
                st.image(response.content, width=150)
            else:
                #"https://cdn-icons-png.flaticon.com/512/5281/5281619.png"
                st.image("assets/images/profile.png", width=180)
        with col2:

            if(categoria.upper() == "CHECK-IN") or (categoria.upper() == "CHECKIN") or (categoria.upper() == "CHECK IN"):
                st.metric(label="Categoria", value=f" {categoria}", border=True)
                st.metric(label="F. Nacimiento", value=f"{fnacimiento}", border=True)
                
                categoria = "Juvenil"
                equipo = "A"

            else:
                st.metric(label="Categoria - Equipo", value=f" {util.traducir(categoria.upper(), idioma).capitalize()} {equipo}", border=True)
                st.metric(label="F. Nacimiento", value=f"{fnacimiento}", border=True)

        with col3:
            st.metric(label="Posición", value=f"{util.traducir(demarcacion.upper(), idioma).capitalize()}", border=True)
            st.metric(label="Edad", value=edad, border=True)

        #st.markdown(":green-badge[:material/check: Antropometria] :red-badge[:material/dangerous: CMJ] :gray-badge[Deprecated]")

    else:
        st.warning("⚠️ No se encontró ningún ID válido en los datos filtrados.")

    return df_joined_filtrado, df_jugador, categoria, equipo