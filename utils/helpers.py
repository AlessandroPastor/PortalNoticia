import streamlit as st

def registrar_lectura(noticia_id):
    """Registrar una lectura de noticia"""
    if 'lecturas' not in st.session_state:
        st.session_state.lecturas = {}
    
    st.session_state.lecturas[noticia_id] = st.session_state.lecturas.get(noticia_id, 0) + 1

def inicializar_session_state():
    """Inicializar el estado de la sesión"""
    if 'favoritos' not in st.session_state:
        st.session_state.favoritos = set()
    if 'lecturas' not in st.session_state:
        st.session_state.lecturas = {}
    if 'noticia_seleccionada' not in st.session_state:
        st.session_state.noticia_seleccionada = None
    if 'busqueda' not in st.session_state:
        st.session_state.busqueda = ""
    if 'filtro_categoria' not in st.session_state:
        st.session_state.filtro_categoria = "Todas"