import streamlit as st
import time
from components.notifications import mostrar_toast
from utils.helpers import registrar_lectura

def mostrar_detalle_noticia_mejorado(df, noticia_id):
    """Vista detalle con mejor UX y navegación"""
    if df.empty or noticia_id not in df['id'].values:
        st.error("Noticia no encontrada")
        if st.button("← Volver al inicio"):
            del st.session_state.noticia_seleccionada
            st.rerun()
        return
    
    noticia = df[df['id'] == noticia_id].iloc[0]
    registrar_lectura(noticia_id)
    
    # Breadcrumb navigation
    col1, col2 = st.columns([1, 4])
    with col1:
        if st.button("← Volver", key="volver_detalle"):
            del st.session_state.noticia_seleccionada
            st.rerun()
    
    with col2:
        st.markdown(f"<small>📂 {noticia.get('categoria', 'General')} > {noticia['titulo'][:50]}...</small>", unsafe_allow_html=True)
    
    # Header de la noticia mejorado
    es_favorito = noticia_id in st.session_state.favoritos
    lecturas = st.session_state.lecturas.get(noticia_id, 0)
    
    st.markdown(f"""
    <div class="news-card" style="margin: 2rem 0;">
        <div style="display: flex; justify-content: space-between; align-items: flex-start; margin-bottom: 1rem;">
            <div class="category-tag">{noticia.get('categoria', 'General')}</div>
            <div style="display: flex; gap: 1rem; align-items: center;">
                <span style="color: #6b7280; font-size: 0.9rem;">👁️ {lecturas} lecturas</span>
                <span style="color: #6b7280; font-size: 0.9rem;">📅 {noticia.get('fecha', 'Sin fecha')[:10]}</span>
            </div>
        </div>
        <h1 style="color: #1f2937; margin-bottom: 1.5rem; line-height: 1.2; font-size: 2rem;">{noticia['titulo']}</h1>
    </div>
    """, unsafe_allow_html=True)
    
    # Botones de acción principales
    col1, col2, col3, col4 = st.columns([1, 1, 2, 1])
    
    with col1:
        fav_icon = "⭐ Quitar Favorito" if es_favorito else "☆ Agregar Favorito"
        if st.button(fav_icon, key="fav_detalle", use_container_width=True):
            if es_favorito:
                st.session_state.favoritos.remove(noticia_id)
                mostrar_toast("Eliminado de favoritos", "warning")
            else:
                st.session_state.favoritos.add(noticia_id)
                mostrar_toast("Agregado a favoritos", "success")
            time.sleep(0.5)
            st.rerun()
    
    with col2:
        if st.button("📤 Compartir", key="compartir_detalle", use_container_width=True):
            st.info("Función de compartir en desarrollo")
    
    with col4:
        if noticia.get('url_original'):
            st.link_button("🔗 Ver Original", noticia['url_original'], use_container_width=True)
    
    # Imagen destacada con mejor presentación
    if noticia.get('imagen'):
        st.markdown("### 📸 Imagen Destacada")
        try:
            st.image(noticia['imagen'], width=800, caption="", use_column_width=True)
        except:
            st.info("No se pudo cargar la imagen")
    
    # Contenido principal con mejor formato
    st.markdown("---")
    st.markdown("### 📄 Contenido Completo")
    
    # Formatear contenido en párrafos legibles
    contenido_html = noticia['contenido'].replace('\n\n', '</p><p>').replace('\n', '<br>')
    st.markdown(f"""
    <div style="
        font-size: 1.1rem; 
        line-height: 1.8; 
        text-align: justify; 
        color: #374151;
        background: #f9fafb;
        padding: 2rem;
        border-radius: 12px;
        border-left: 4px solid var(--primary-color);
    ">
        <p>{contenido_html}</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Noticias relacionadas mejoradas
    st.markdown("---")
    st.markdown("### 🔗 Noticias Relacionadas")
    
    noticias_relacionadas = df[
        (df['categoria'] == noticia['categoria']) & 
        (df['id'] != noticia_id)
    ].head(3)
    
    if not noticias_relacionadas.empty:
        cols = st.columns(3)
        for idx, (_, relacionada) in enumerate(noticias_relacionadas.iterrows()):
            with cols[idx]:
                st.markdown(f"""
                <div class="news-card" style="min-height: 250px;">
                    <div class="category-tag">{relacionada.get('categoria', 'General')}</div>
                    <h5 style="margin-bottom: 1rem;">{relacionada['titulo'][:60]}...</h5>
                    <small style="color: #6b7280;">📅 {relacionada.get('fecha', 'Sin fecha')[:10]}</small>
                    <div style="margin-top: 1rem;">
                        <small>{relacionada['contenido'][:80]}...</small>
                    </div>
                </div>
                """, unsafe_allow_html=True)
                
                if st.button("📖 Leer", key=f"relacionada_{relacionada['id']}", use_container_width=True):
                    st.session_state.noticia_seleccionada = relacionada['id']
                    st.rerun()