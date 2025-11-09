import streamlit as st
import pandas as pd
from components.cards import mostrar_grid_noticias
from components.notifications import mostrar_toast

def mostrar_favoritos_mejorado(df):
    """Vista de favoritos con mejor organización"""
    st.markdown('<div class="section-title">⭐ Mis Noticias Favoritas</div>', unsafe_allow_html=True)
    
    if not st.session_state.favoritos:
        st.markdown("""
        <div class="empty-state">
            <div class="empty-state-icon">⭐</div>
            <h3>No tienes noticias favoritas</h3>
            <p>Haz clic en ☆ en cualquier noticia para agregarla a favoritos</p>
        </div>
        """, unsafe_allow_html=True)
        return
    
    favoritas = df[df['id'].isin(st.session_state.favoritos)]
    
    if favoritas.empty:
        st.warning("Las noticias favoritas ya no están disponibles")
        if st.button("🗑️ Limpiar favoritos"):
            st.session_state.favoritos.clear()
            st.rerun()
        return
    
    # Estadísticas de favoritos
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.markdown(f"""
        <div class="stats-card">
            <div class="stats-number">{len(favoritas)}</div>
            <div class="stats-label">Favoritos</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        categorias_fav = favoritas['categoria'].nunique()
        st.markdown(f"""
        <div class="stats-card">
            <div class="stats-number">{categorias_fav}</div>
            <div class="stats-label">Categorías</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        total_lecturas = sum([st.session_state.lecturas.get(fav_id, 0) for fav_id in st.session_state.favoritos])
        st.markdown(f"""
        <div class="stats-card">
            <div class="stats-number">{total_lecturas}</div>
            <div class="stats-label">Lecturas Total</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col4:
        if st.button("🗑️ Limpiar Todo", use_container_width=True):
            if st.session_state.get('confirmar_limpiar', False):
                st.session_state.favoritos.clear()
                st.session_state.confirmar_limpiar = False
                mostrar_toast("Favoritos eliminados", "success")
                st.rerun()
            else:
                st.session_state.confirmar_limpiar = True
                st.info("Haz clic nuevamente para confirmar")
    
    st.markdown("---")
    
    # Grid de favoritos mejorado
    mostrar_grid_noticias(favoritas, noticias_por_pagina=6)