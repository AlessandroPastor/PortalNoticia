import streamlit as st

def barra_busqueda_avanzada(df):
    """Barra de búsqueda con filtros avanzados"""
    st.markdown('<h3> Buscar Noticias</h3>', unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns([3, 2, 1])
    
    with col1:
        busqueda = st.text_input(
            "",
            placeholder="Buscar por título, contenido o categoría...",
            key="search_advanced",
            label_visibility="collapsed"
        )
    
    with col2:
        categorias = ["Todas"] + sorted(df['categoria'].unique().tolist()) if not df.empty else ["Todas"]
        categoria = st.selectbox(
            "Categoría",
            categorias,
            key="category_advanced",
            label_visibility="collapsed"
        )
    
    with col3:
        if st.button("🔍 Buscar", type="primary", use_container_width=True):
            st.session_state.busqueda = busqueda
            st.session_state.filtro_categoria = categoria
            st.rerun()
    
    return busqueda, categoria