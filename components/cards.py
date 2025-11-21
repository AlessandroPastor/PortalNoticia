import logging
import html as html_lib
import re
import time
from datetime import datetime, timezone
from urllib.parse import urlparse

import streamlit as st
import pandas as pd
from bs4 import BeautifulSoup

from components.notifications import mostrar_toast
from utils.helpers import registrar_lectura

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def calcular_tiempo_relativo(fecha_scraping):
    """Calcula tiempo relativo desde fecha de scraping."""
    try:
        if not fecha_scraping:
            return "Reciente"
        fecha = pd.to_datetime(fecha_scraping)
        diff = datetime.now() - fecha

        if diff.days > 30:
            m = diff.days // 30
            return f"{m} mes{'es' if m > 1 else ''}"
        if diff.days > 0:
            return f"{diff.days} día{'s' if diff.days > 1 else ''}"
        h = diff.seconds // 3600
        if h > 0:
            return f"{h} hora{'s' if h > 1 else ''}"
        m = diff.seconds // 60
        if m > 0:
            return f"{m} min"
        return "Ahora"
    except:
        return "Reciente"

def obtener_fuente(url):
    """Extrae dominio legible desde una URL."""
    try:
        if not url:
            return "Desconocida"
        host = urlparse(url).netloc.replace("www.", "")
        return host.split('.')[0].title() if '.' in host else host
    except Exception:
        return "Desconocida"

def toggle_favorito(nid, es_fav):
    """Alterna favorito en session_state."""
    try:
        if "favoritos" not in st.session_state:
            st.session_state.favoritos = set()
        if es_fav:
            st.session_state.favoritos.discard(nid)
            mostrar_toast("❌ Eliminado de favoritos", "warning")
        else:
            st.session_state.favoritos.add(nid)
            mostrar_toast("⭐ Agregado a favoritos", "success")
    except Exception as e:
        logger.error(f"Error toggling favorito: {e}")
        mostrar_toast("❌ Error al actualizar favoritos", "error")

def limpiar_contenido_html(texto):
    """Limpia contenido HTML y siempre retorna string (sin tags peligrosos)."""
    try:
        if texto is None:
            return ""
        if not isinstance(texto, str):
            texto = str(texto)
        texto = texto.strip()
        if not texto:
            return ""
        
        # Si no tiene tags HTML, retornar directamente
        if '<' not in texto and '>' not in texto:
            return texto
            
        texto = html_lib.unescape(texto)
        soup = BeautifulSoup(texto, "html.parser")
        
        # Eliminar elementos no deseados
        for tag in soup.find_all(["script", "style", "img", "picture", "figure", "iframe"]):
            tag.decompose()
        
        # Quitar atributos peligrosos
        for el in soup.find_all(True):
            for attr in list(el.attrs):
                if attr.lower().startswith("on") or attr.lower() in ("style", "srcset"):
                    del el.attrs[attr]
        
        texto_limpio = soup.get_text(" ", strip=True)
        return texto_limpio or ""
        
    except Exception as e:
        logger.exception("Error limpiando HTML")
        return re.sub(r"<[^>]+>", "", str(texto) or "")

def mostrar_card_noticia_mejorada(noticia):
    """Muestra una card única y robusta para una noticia (versión corregida)."""
    try:
        if noticia is None:
            st.warning("Noticia vacía")
            return

        # Asegurar session_state básicos
        if "favoritos" not in st.session_state:
            st.session_state.favoritos = set()
        if "lecturas" not in st.session_state:
            st.session_state.lecturas = {}

        nid = noticia.get("id") or noticia.get("id_noticia")
        if nid is None:
            logger.warning("Noticia sin ID, saltando")
            return

        es_favorito = nid in st.session_state.favoritos
        lecturas = st.session_state.lecturas.get(nid, 0)

        # TÍTULO CORREGIDO - SIN html_lib.escape
        titulo = str(noticia.get("titulo") or "Sin título")
        titulo_limpio = limpiar_contenido_html(titulo)
        titulo_html = titulo_limpio[:400]  # SIN ESCAPE

        # IMAGEN
        imagen = noticia.get("imagen") or noticia.get("imagen_url") or ""
        if imagen and isinstance(imagen, str) and imagen not in [None, "None", ""]:
            imagen_esc = html_lib.escape(imagen)
            imagen_html = f"""
            <div class="news-image-wrapper">
                <img src="{imagen_esc}" class="news-image" alt="Imagen noticia" loading="lazy" />
            </div>
            """
        else:
            imagen_html = """
            <div class="image-placeholder">
                <div class="placeholder-icon">📰</div>
                <div class="placeholder-text">Sin imagen</div>
            </div>
            """

        # CONTENIDO CORREGIDO - SIN html_lib.escape
        contenido_raw = noticia.get("contenido") or noticia.get("resumen") or ""
        contenido_limpio = limpiar_contenido_html(contenido_raw)
        
        if contenido_limpio and contenido_limpio.strip():
            resumen = contenido_limpio[:220] + "..." if len(contenido_limpio) > 220 else contenido_limpio
            contenido_html = f'<div class="news-content">{resumen}</div>'  # SIN ESCAPE
        else:
            contenido_html = '<div class="news-content no-content">Sin contenido disponible</div>'

        # CATEGORIA CORREGIDA - SIN html_lib.escape
        categoria = noticia.get("categoria") or "General"
        cat_slug = re.sub(r"[^a-z0-9]+", "-", str(categoria).lower()).strip("-")
        categoria_class = f"category-{cat_slug}" if cat_slug else "category-general"
        categoria_html = str(categoria)  # SIN ESCAPE

        # TIEMPO Y FUENTE
        tiempo_str = calcular_tiempo_relativo(noticia.get("fecha_scraping"))
        fuente = obtener_fuente(noticia.get("url_original"))

        # CARD HTML CORREGIDA
        card_html = f"""
        <div class="news-card">
            <div class="category-tag {categoria_class}">{categoria_html}</div>
            {imagen_html}
            <h3 class="news-title">{titulo_html}</h3>
            <div class="news-meta">
                <span class="meta-time">⏰ {tiempo_str}</span>
                <span class="meta-views">👁️ {lecturas}</span>
                <span class="meta-source">📰 {fuente}</span>
            </div>
            {contenido_html}
        </div>
        """

        st.markdown(card_html, unsafe_allow_html=True)

        # BOTONES DE ACCIÓN
        col1, col2, col3 = st.columns([2, 2, 1])
        
        with col1:
            if st.button("📖 Leer", key=f"leer_{nid}", use_container_width=True):
                st.session_state.noticia_seleccionada = nid
                try:
                    registrar_lectura(nid)
                except Exception as e:
                    logger.error(f"Error registrando lectura: {e}")
                st.rerun()

        with col2:
            fav_text = "💝 Quitar" if es_favorito else "🤍 Fav"
            if st.button(fav_text, key=f"fav_{nid}", use_container_width=True):
                toggle_favorito(nid, es_favorito)
                st.rerun()

        with col3:
            url_original = noticia.get("url_original")
            if url_original and st.button("🔗", key=f"link_{nid}", use_container_width=True):
                st.markdown(f'<a href="{html_lib.escape(url_original)}" target="_blank" style="display:none;">Link</a>', unsafe_allow_html=True)
                mostrar_toast("🌐 Abriendo enlace original...", "info")

    except Exception as e:
        logger.exception("Error mostrando card de noticia")
        st.error(f"Error mostrando noticia: {str(e)}")

def mostrar_grid_noticias(df_filtrado: pd.DataFrame, noticias_por_pagina=9):
    """Muestra un grid simple con paginación básica."""
    try:    
        if df_filtrado is None:
            st.info("No hay datos para mostrar")
            return
        
        if not isinstance(df_filtrado, pd.DataFrame):
            try:
                df_filtrado = pd.DataFrame(df_filtrado)
            except Exception:   
                st.info("No hay noticias para mostrar")
                return

        if df_filtrado.empty:
            st.markdown("""
            <div class="empty-state">
                <div class="empty-state-icon">📰</div>
                <h3>No se encontraron noticias</h3>
                <p>Intenta ajustar tus filtros de búsqueda</p>
            </div>
            """, unsafe_allow_html=True)
            return

        # Paginación
        if "pagina_noticias" not in st.session_state:
            st.session_state.pagina_noticias = 1

        total = len(df_filtrado)
        total_pag = max(1, (total - 1) // noticias_por_pagina + 1)
        pagina = max(1, min(st.session_state.pagina_noticias, total_pag))

        inicio = (pagina - 1) * noticias_por_pagina
        fin = inicio + noticias_por_pagina
        df_pagina = df_filtrado.iloc[inicio:fin]

        st.markdown(f"""
        <div style="text-align: center; margin: 1rem 0; padding: 1rem; background: #1e293b; border-radius: 8px;">
            <span style="color: #f8fafc;">📄 Se encontraron <strong>{total}</strong> noticias</span>
        </div>
        """, unsafe_allow_html=True)

        # Grid de 3 columnas
        cols = st.columns(3)
        for idx, row in enumerate(df_pagina.to_dict(orient="records")):
            col = cols[idx % 3]
            with col:
                mostrar_card_noticia_mejorada(row)

        # Controles de paginación
        if total_pag > 1:
            st.markdown("---")
            col_prev, col_info, col_next = st.columns([1, 2, 1])
            with col_prev:
                if st.button("◀ Anterior", use_container_width=True, disabled=(pagina <= 1)):
                    st.session_state.pagina_noticias = max(1, pagina - 1)
                    st.rerun()
            with col_info:
                st.markdown(f"<div style='text-align: center; color: #64748b;'>Página {pagina} de {total_pag}</div>", unsafe_allow_html=True)
            with col_next:
                if st.button("Siguiente ▶", use_container_width=True, disabled=(pagina >= total_pag)):
                    st.session_state.pagina_noticias = min(total_pag, pagina + 1)
                    st.rerun()

    except Exception as e:
        logger.exception("Error mostrando grid de noticias")
        st.error(f"Error al mostrar noticias: {str(e)}")

def mostrar_card_compacta(noticia):
    """Card compacta para listas."""
    try:
        nid = noticia.get("id")
        if nid is None:
            return

        es_fav = nid in st.session_state.favoritos
        lecturas = st.session_state.lecturas.get(nid, 0)
        tiempo_str = calcular_tiempo_relativo(noticia.get("fecha_scraping"))

        # TÍTULO CORREGIDO - SIN html_lib.escape
        titulo = str(noticia.get("titulo") or "Sin título")
        titulo_limpio = limpiar_contenido_html(titulo)
        titulo_corto = titulo_limpio[:70] + "..." if len(titulo_limpio) > 70 else titulo_limpio

        st.markdown(f"""
        <div class="compact-card">
            <div class="compact-header">
                <span class="compact-category">{noticia.get('categoria', 'General')}</span>
                <span class="compact-time">⏰ {tiempo_str}</span>
            </div>
            <h5 class="compact-title">{titulo_corto}</h5>
            <div class="compact-footer">
                <span>👁️ {lecturas}</span>
                <span>{'⭐' if es_fav else '☆'}</span>
            </div>
        </div>
        """, unsafe_allow_html=True)

        col1, col2 = st.columns(2)
        with col1:
            if st.button("📖 Leer", key=f"compact_read_{nid}", use_container_width=True):
                registrar_lectura(nid)
                st.session_state.noticia_seleccionada = nid
                st.rerun()
        with col2:
            icon = "💝" if es_fav else "🤍"
            if st.button(icon, key=f"compact_fav_{nid}", use_container_width=True):
                toggle_favorito(nid, es_fav)
                st.rerun()

    except Exception as e:
        logger.exception("Error mostrando card compacta")
        st.error(f"Error en card compacta: {str(e)}")