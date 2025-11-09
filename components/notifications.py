import streamlit as st

def mostrar_toast(mensaje, tipo="success"):
    """Mostrar notificación toast"""
    st.markdown(f"""
    <div class="toast {tipo}">
        {mensaje}
    </div>
    """, unsafe_allow_html=True)