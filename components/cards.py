import streamlit as st
import pandas as pd
from datetime import datetime
import time
from .notifications import mostrar_toast
from utils.helpers import registrar_lectura
## ubicacion de components/cards.py aqui es todo porfavor 
def mostrar_grid_noticias(df_filtrado, noticias_por_pagina=9):
    """Grid de noticias con mejor layout responsivo"""
    if df_filtrado.empty:
        st.markdown("""
        <div class="empty-state">
            <div class="empty-state-icon">📰</div>
            <h3>No se encontraron noticias</h3>
            <p>Intenta ajustar tus filtros de búsqueda</p>
        </div>
        """, unsafe_allow_html=True)
        return
    
    # Contador de resultados
    st.markdown(f"""
    <div class="result-count">
        📄 Se encontraron <strong>{len(df_filtrado)}</strong> noticias
        {f"en {df_filtrado['categoria'].nunique()} categorías" if not df_filtrado.empty else ''}
    </div>
    """, unsafe_allow_html=True)
    
    # Controles de visualización
    col1, col2, col3 = st.columns([2, 1, 1])
    with col2:
        # Opción para cambiar entre vista normal y compacta
        vista_compacta = st.toggle("📱 Vista compacta", value=False, 
                                 help="Mostrar más noticias en menos espacio")
    
    with col3:
        # Opción para ordenar
        orden = st.selectbox(
            "Ordenar por",
            ["Más recientes", "Más leídas", "A-Z"],
            key="orden_noticias"
        )
    
    # Aplicar ordenamiento
    if orden == "Más recientes":
        df_filtrado = df_filtrado.sort_values('fecha_scraping', ascending=False)
    elif orden == "Más leídas":
        df_filtrado = df_filtrado.copy()
        df_filtrado['_lecturas'] = df_filtrado['id'].apply(
            lambda x: st.session_state.lecturas.get(x, 0)
        )
        df_filtrado = df_filtrado.sort_values('_lecturas', ascending=False)
    elif orden == "A-Z":
        df_filtrado = df_filtrado.sort_values('titulo')
    
    # Ajustar número de noticias por página según la vista
    noticias_por_pagina = 12 if vista_compacta else 9
    
    # Paginación mejorada
    total_noticias = len(df_filtrado)
    total_paginas = max(1, (total_noticias - 1) // noticias_por_pagina + 1)
    
    if total_paginas > 1:
        col1, col2, col3 = st.columns([1, 2, 1])
        with col2:
            pagina_actual = st.selectbox(
                "Navegar por páginas",
                range(1, total_paginas + 1),
                format_func=lambda x: f"Página {x} ({((x-1)*noticias_por_pagina)+1}-{min(x*noticias_por_pagina, total_noticias)} de {total_noticias})",
                key="pagination_main"
            )
        
        inicio = (pagina_actual - 1) * noticias_por_pagina
        fin = min(inicio + noticias_por_pagina, total_noticias)
        df_pagina = df_filtrado.iloc[inicio:fin]
        
        # Indicador de paginación
        st.markdown(f"""
        <div style="text-align: center; margin: 0.5rem 0; color: #666; font-size: 0.9rem;">
            Mostrando noticias {inicio + 1}-{fin} de {total_noticias}
        </div>
        """, unsafe_allow_html=True)
    else:
        df_pagina = df_filtrado.head(noticias_por_pagina)
    
    # Grid responsivo adaptativo
    columnas_por_fila = 4 if vista_compacta else 3
    
    for i in range(0, len(df_pagina), columnas_por_fila):
        cols = st.columns(columnas_por_fila, gap="medium")
        for j in range(columnas_por_fila):
            if i + j < len(df_pagina):
                noticia = df_pagina.iloc[i + j]
                with cols[j]:
                    if vista_compacta:
                        mostrar_card_compacta(noticia)
                    else:
                        mostrar_card_noticia_mejorada(noticia)

def mostrar_card_compacta(noticia):
    """Versión compacta de la card para vista de lista"""
    es_favorito = noticia['id'] in st.session_state.favoritos
    lecturas = st.session_state.lecturas.get(noticia['id'], 0)
    
    # Calcular tiempo relativo
    try:
        fecha_scraping = pd.to_datetime(noticia['fecha_scraping'])
        tiempo_transcurrido = datetime.now() - fecha_scraping
        if tiempo_transcurrido.days > 0:
            tiempo_str = f"{tiempo_transcurrido.days}d"
        elif tiempo_transcurrido.seconds > 3600:
            tiempo_str = f"{tiempo_transcurrido.seconds // 3600}h"
        else:
            tiempo_str = f"{tiempo_transcurrido.seconds // 60}m"
    except:
        tiempo_str = "1d"
    
    # Card compacta
    with st.container():
        st.markdown(f"""
        <div class="compact-card">
            <div class="compact-header">
                <span class="compact-category">{noticia.get('categoria', 'General')}</span>
                <span class="compact-time">⏰ {tiempo_str}</span>
            </div>
            <h5 class="compact-title" title="{noticia['titulo']}">
                {noticia['titulo'][:70]}{'...' if len(noticia['titulo']) > 70 else ''}
            </h5>
            <div class="compact-footer">
                <span class="compact-views">👁️ {lecturas}</span>
                <span class="compact-fav">{'⭐' if es_favorito else '☆'}</span>
            </div>
        </div>
        """, unsafe_allow_html=True)
        
        # Botones compactos
        col1, col2 = st.columns(2)
        with col1:
            if st.button("📖", key=f"leer_compact_{noticia['id']}", 
                        use_container_width=True, help="Leer noticia completa"):
                st.session_state.noticia_seleccionada = noticia['id']
                registrar_lectura(noticia['id'])
                st.rerun()
        
        with col2:
            fav_icon = "💝" if es_favorito else "🤍"
            if st.button(fav_icon, key=f"fav_compact_{noticia['id']}", 
                        use_container_width=True, help="Agregar a favoritos"):
                if es_favorito:
                    st.session_state.favoritos.remove(noticia['id'])
                    mostrar_toast("❌ Eliminado de favoritos", "warning")
                else:
                    st.session_state.favoritos.add(noticia['id'])
                    mostrar_toast("✅ Agregado a favoritos", "success")
                time.sleep(0.3)
                st.rerun()

def mostrar_card_noticia_mejorada(noticia):
    """Card de noticia con mejor diseño y UX - VERSIÓN MEJORADA"""
    es_favorito = noticia['id'] in st.session_state.favoritos
    lecturas = st.session_state.lecturas.get(noticia['id'], 0)
    
    # Calcular tiempo relativo mejorado
    try:
        fecha_scraping = pd.to_datetime(noticia['fecha_scraping'])
        tiempo_transcurrido = datetime.now() - fecha_scraping
        
        if tiempo_transcurrido.days > 30:
            meses = tiempo_transcurrido.days // 30
            tiempo_str = f"{meses} mes{'es' if meses > 1 else ''}"
        elif tiempo_transcurrido.days > 0:
            tiempo_str = f"{tiempo_transcurrido.days} día{'s' if tiempo_transcurrido.days > 1 else ''}"
        elif tiempo_transcurrido.seconds > 3600:
            horas = tiempo_transcurrido.seconds // 3600
            tiempo_str = f"{horas} hora{'s' if horas > 1 else ''}"
        elif tiempo_transcurrido.seconds > 60:
            minutos = tiempo_transcurrido.seconds // 60
            tiempo_str = f"{minutos} min"
        else:
            tiempo_str = "Ahora"
    except:
        tiempo_str = "Reciente"
    
    # Obtener fuente del URL si está disponible
    fuente = "Noticia"
    if noticia.get('url_original'):
        try:
            from urllib.parse import urlparse
            dominio = urlparse(noticia['url_original']).netloc
            fuente = dominio.replace('www.', '').split('.')[0].title()
        except:
            pass
    
    # Card mejorada con más información
    with st.container():
    
        # Imagen optimizada con mejor manejo de errores
        if noticia.get('imagen'):
            try:
                # Contenedor para la imagen con aspect ratio
                st.markdown("""
                <div style="border-radius: 8px; overflow: hidden; margin: 0.5rem 0;">
                """, unsafe_allow_html=True)
                st.image(
                    noticia["imagen"], 
                    use_container_width=True,
                    caption=""
                )
                st.markdown("</div>", unsafe_allow_html=True)
            except Exception as e:
                st.markdown("""
                <div class="image-placeholder">
                    <div class="placeholder-icon">📷</div>
                    <div class="placeholder-text">Imagen no disponible</div>
                </div>
                """, unsafe_allow_html=True)
        else:
            st.markdown("""
            <div class="image-placeholder">
                <div class="placeholder-icon">📄</div>
                <div class="placeholder-text">Sin imagen</div>
            </div>
            """, unsafe_allow_html=True)
        
        # Resumen optimizado con mejor legibilidad
        contenido = noticia['contenido'].strip()
        if len(contenido) > 0:
            resumen = contenido[:150] + "..." if len(contenido) > 150 else contenido
            st.markdown(f"""
            <div class="news-content">
                <p style="margin: 0; line-height: 1.5; color: #4b5563;">{resumen}</p>
            </div>
            """, unsafe_allow_html=True)
        
        # Botones de acción mejorados con mejor UX
        col1, col2, col3 = st.columns([2, 2, 1])
        
        with col1:
            if st.button("📖 Leer completo", key=f"leer_{noticia['id']}", 
                        use_container_width=True, type="primary"):
                st.session_state.noticia_seleccionada = noticia['id']
                registrar_lectura(noticia['id'])
                st.rerun()
        
        with col2:
            fav_text = "💝 Quitar favorito" if es_favorito else "🤍 Agregar a favoritos"
            fav_type = "secondary" if es_favorito else "primary"    
            if st.button(fav_text, key=f"fav_{noticia['id']}", 
                        use_container_width=True, type=fav_type):
                if es_favorito:
                    st.session_state.favoritos.remove(noticia['id'])
                    mostrar_toast("❌ Eliminado de favoritos", "warning")
                else:
                    st.session_state.favoritos.add(noticia['id'])
                    mostrar_toast("✅ Agregado a favoritos", "success")
                time.sleep(0.3)
                st.rerun()
        
        with col3:
            if noticia.get('url_original'):
                if st.button("🔗", key=f"link_{noticia['id']}", 
                            use_container_width=True, help="Abrir enlace original"):
                    st.markdown(f'<a href="{noticia["url_original"]}" target="_blank"></a>', 
                              unsafe_allow_html=True)
                    st.toast("🌐 Abriendo enlace original...")