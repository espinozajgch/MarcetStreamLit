import streamlit as st

st.session_state.clear()
if 'usuario' in st.session_state:
    del st.session_state['usuario']

st.query_params.clear()  # 🔹 Limpia la URL
st.session_state.clear()
st.switch_page("inicio.py")