import streamlit as st
import pandas as pd
from utils import util

# Validación simple de usuario y clave con un archivo csv

def validarUsuario(usuario,clave, conn):    
    """Permite la validación de usuario y clave

    Args:
        usuario (str): usuario a validar
        clave (str): clave del usuario

    Returns:
        bool: True usuario valido, False usuario invalido
    """    
    dfusuarios = util.get_usuarios(conn)
    #dfusuarios = pd.read_csv('usuarios.csv')
    if len(dfusuarios[(dfusuarios['USUARIO']==usuario) & (dfusuarios['CLAVE']==clave)])>0:
        return True
    else:
        return False

# def generateMenu():
#     with st.sidebar:
#         st.page_link('app.py', label="Inicio", icon="🏠")
#         st.page_link('pages/player.py', label="PlayerHub", icon="⚽")
#         #st.page_link('pages/team.py', label="StatsLab", icon="📊")

def generarMenu(usuario, conn):
    """Genera el menú dependiendo del usuario

    Args:
        usuario (str): usuario utilizado para generar el menú
    """        
    with st.sidebar:
        st.logo("assets/images/marcet.png", size="large")
        # Cargamos la tabla de usuarios
        dfusuarios = util.get_usuarios(conn)
        # Filtramos la tabla de usuarios
        dfUsuario =dfusuarios[(dfusuarios['USUARIO']==usuario)]
        # Cargamos el nombre del usuario
        nombre= dfUsuario['NOMBRE'].values[0]
        #Mostramos el nombre del usuario
        st.write(f"Hola **:blue-background[{nombre}]** ")
        # Mostramos los enlaces de páginas
        st.page_link("inicio.py", label="Inicio", icon=":material/home:")
        st.subheader("Tableros :material/dashboard:")
        st.page_link("pages/playerhub.py", label="PlayerHub", icon=":material/contacts:")
        #st.page_link('pages/teams.py', label="StatsLab", icon=":material/query_stats:")
        st.subheader("Administrador :material/manage_accounts:")
        st.page_link("pages/players.py", label="Jugadores", icon=":material/account_circle:")  
        st.page_link("pages/tests.py", label="Test Fisicos", icon=":material/directions_run:")
        st.page_link("pages/users.py", label="Usuarios", icon=":material/groups:")
        st.divider()
        #st.subheader("Ajustes")
        btnReload=st.button("Recargar Datos", type="tertiary", icon=":material/update:")
        if btnReload:
            st.session_state["reload_data"] = True  # Activar recarga manual
            st.rerun()

        # Botón para cerrar la sesión
        btnSalir=st.button("Salir", type="tertiary", icon=":material/logout:")
        if btnSalir:
            cerrarSesion()
            #st.session_state.clear()
            # Luego de borrar el Session State reiniciamos la app para mostrar la opción de usuario y clave
            #st.rerun()

def generarLogin(conn):
    """Genera la ventana de login o muestra el menú si el login es válido"""    

    # 🔹 Verificamos si el usuario ya está en la URL o en session_state
    usuario_actual = st.query_params.get("user", None)

    if usuario_actual:
        st.session_state['usuario'] = usuario_actual

    # Si ya hay usuario, mostramos el menú
    if 'usuario' in st.session_state:
        generarMenu(st.session_state['usuario'], conn) 
    else: 
        col1, col2, col3 = st.columns([2, 1.5, 2])
        with col2:
            st.image("assets/images/marcet.png")
        
        col1, col2, col3 = st.columns([2, 1.5, 2])
        with col2:
            # Cargamos el formulario de login       
            with st.form('frmLogin'):
                parUsuario = st.text_input('Usuario')
                parPassword = st.text_input('Password', type='password')
                btnLogin = st.form_submit_button('Ingresar', type='primary')

                if btnLogin:
                    if validarUsuario(parUsuario, parPassword, conn):
                        # Guardamos usuario en session_state y en la URL
                        st.session_state['usuario'] = parUsuario
                        st.query_params.user = parUsuario  # 🔹 Persistencia en la URL
                        st.rerun()
                    else:
                        st.error("Usuario o clave inválidos", icon=":material/gpp_maybe:")

# 🔹 Función para cerrar sesión y limpiar query_params
def cerrarSesion():
    if 'usuario' in st.session_state:
        del st.session_state['usuario']
    st.query_params.clear()  # 🔹 Limpia la URL
    st.session_state.clear()
    st.rerun()


# def generarLogin():
    """Genera la ventana de login o muestra el menú si el login es valido
    """    
    # Validamos si el usuario ya fue ingresado    
    if 'usuario' in st.session_state:
        generarMenu(st.session_state['usuario']) # Si ya hay usuario cargamos el menu        
    else: 
        col1, col2, col3 = st.columns([2, 1.5, 2])
        with col2:
            st.image("assets/images/marcet.png")
        
        col1, col2, col3 = st.columns([2, 1.5, 2])
        with col2:
            # Cargamos el formulario de login       
            with st.form('frmLogin'):
                parUsuario = st.text_input('Usuario')
                parPassword = st.text_input('Password',type='password')
                btnLogin=st.form_submit_button('Ingresar',type='primary')
                if btnLogin:
                    if validarUsuario(parUsuario,parPassword):
                        st.session_state['usuario'] =parUsuario
                        # Si el usuario es correcto reiniciamos la app para que se cargue el menú
                        st.rerun()
                    else:
                        # Si el usuario es invalido, mostramos el mensaje de error
                        st.error("Usuario o clave inválidos",icon=":material/gpp_maybe:")          