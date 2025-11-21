import streamlit as st
import requests
from bs4 import BeautifulSoup
import pandas as pd
from urllib.parse import urljoin
from datetime import datetime
import time
import concurrent.futures
from urllib.parse import urlparse, urljoin
import urllib.robotparser as urobot
from hashlib import md5
from streamlit_autorefresh import st_autorefresh
from ui.styles import load_css, aplicar_tema
from db.mysql_io import (
    crear_tablas,
    cargar_noticias,
    guardar_en_mysql,
    registrar_lectura,
)
from urllib.parse import urlencode
import os
import sys
import components.cards as cards
from pathlib import Path
from datetime import timezone
from email.utils import parsedate_to_datetime

# Asegura que el directorio del archivo esté en sys.path
BASE_DIR = Path(__file__).resolve().parent
if str(BASE_DIR) not in sys.path:
    sys.path.append(str(BASE_DIR))
# Agregar el directorio actual al path para imports
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
st.markdown("""
<style>

</style>
""", unsafe_allow_html=True)

# Ahora hacer los imports
try:
    from components.search import barra_busqueda_avanzada
    from components.cards import mostrar_grid_noticias, mostrar_card_noticia_mejorada
    from views.detail import mostrar_detalle_noticia_mejorado
    from views.favorites import mostrar_favoritos_mejorado
    from views.dashboard import mostrar_dashboard_analisis
    from views.admin_dashboard import mostrar_dashboard_admin
    from db.admin import (
        tiene_permiso_admin,
        obtener_fuentes_permitidas_por_rol,
        verificar_permiso_scraping
    )
    from utils.helpers import inicializar_session_state, registrar_lectura
    from components.notifications import mostrar_toast
    from components.login import (
        mostrar_login,
        mostrar_header_usuario,
        verificar_autenticacion,
        requerir_autenticacion,
        mostrar_perfil
    )
except ImportError as e:
    st.error(f"Error de importación: {e}")
    st.info("Asegúrate de que la estructura de archivos sea correcta")

# Configuración de página mejorada
st.set_page_config(
    page_title="Pastor Noticias",
    page_icon="📰",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Inicialización del estado de sesión
def init_session_state():
    # Autenticación
    if 'autenticado' not in st.session_state:
        st.session_state.autenticado = False
    if 'usuario' not in st.session_state:
        st.session_state.usuario = None
    if 'session_token' not in st.session_state:
        st.session_state.session_token = None
    if 'mostrar_perfil' not in st.session_state:
        st.session_state.mostrar_perfil = False
    
    # Otros estados
    if 'favoritos' not in st.session_state:
        st.session_state.favoritos = set()
    if 'lecturas' not in st.session_state:
        st.session_state.lecturas = {}
    if 'dark_mode' not in st.session_state:
        st.session_state.dark_mode = False
    if 'last_scrape' not in st.session_state:
        st.session_state.last_scrape = None
    if 'filtro_categoria' not in st.session_state:
        st.session_state.filtro_categoria = "Todas"
    if 'busqueda' not in st.session_state:
        st.session_state.busqueda = ""
    if 'noticia_seleccionada' not in st.session_state:
        st.session_state.noticia_seleccionada = None
    if 'vista_actual' not in st.session_state:
        st.session_state.vista_actual = "portada"
    if 'notificaciones' not in st.session_state:
        st.session_state.notificaciones = []
    if 'confirmar_reset' not in st.session_state:
        st.session_state.confirmar_reset = False

def extraer_titulo(soup):
    """Extraer título LIMPIO (sin HTML)"""
    selectors = [
        "h1",
        ".entry-title",
        ".post-title", 
        "[class*='title']",
        "title"
    ]
    
    for selector in selectors:
        element = soup.select_one(selector)
        if element:
            # USAR get_text() para obtener solo texto, sin HTML
            title = element.get_text(strip=True)
            if len(title) > 10:
                return title
    return None

def _parse_datetime(s):
    try:
        # RFC2822
        dt = parsedate_to_datetime(s)
        return dt.astimezone(timezone.utc).isoformat()
    except:
        pass
    # otros intentos simples...
    try:
        return pd.to_datetime(s, errors="coerce", utc=True).isoformat()
    except:
        return None

def extraer_fecha(soup):
    # <time> con datetime
    time_elem = soup.find("time")
    if time_elem:
        v = time_elem.get("datetime") or time_elem.get_text(strip=True)
        dt = _parse_datetime(v)
        if dt: return dt
    # og/article metas
    for sel in [
        ("meta", {"property":"article:published_time"}),
        ("meta", {"name":"article:published_time"}),
        ("meta", {"name":"pubdate"}),
        ("meta", {"name":"date"}),
        ("meta", {"itemprop":"datePublished"}),
    ]:
        m = soup.find(*sel)
        if m and m.get("content"):
            dt = _parse_datetime(m["content"])
            if dt: return dt
    # fallback: now UTC
    return datetime.utcnow().replace(tzinfo=timezone.utc).isoformat()

def extraer_categoria(soup):
    """Extraer categoría"""
    cat_link = soup.find("a", {"rel": "category tag"})
    if cat_link:
        return cat_link.get_text(strip=True)
    
    cat_classes = [".category", ".tag", "[class*='cat']"]
    for cls in cat_classes:
        elem = soup.select_one(cls)
        if elem:
            return elem.get_text(strip=True)
    
    return "General"

def extraer_contenido(soup):
    """Extraer contenido del artículo"""
    article = soup.find("article")
    if article:
        paragraphs = article.find_all("p")
        content = " ".join([p.get_text(strip=True) for p in paragraphs])
        if len(content) > 50:
            return content
    
    content_selectors = [".entry-content", ".post-content", ".article-content", ".content"]
    for selector in content_selectors:
        elem = soup.select_one(selector)
        if elem:
            paragraphs = elem.find_all("p")
            content = " ".join([p.get_text(strip=True) for p in paragraphs])
            if len(content) > 50:
                return content
    
    paragraphs = soup.find_all("p")
    return " ".join([p.get_text(strip=True) for p in paragraphs[:10]])

def extraer_imagen(soup, base_url):
    img_selectors = ["img.wp-post-image",".featured-image img",".post-thumbnail img","article img:first-of-type"]
    for selector in img_selectors:
        img = soup.select_one(selector)
        if img and img.get("src"):
            return urljoin(base_url, img["src"])
    for meta_name in [
        ("meta", {"property":"og:image"}),
        ("meta", {"name":"og:image"}),
        ("meta", {"name":"twitter:image"}),
        ("meta", {"property":"twitter:image"}),
    ]:
        m = soup.find(*meta_name)
        if m and m.get("content"):
            return urljoin(base_url, m["content"])
    return None

def filtrar_noticias(df, categoria, busqueda):
    """Filtrar noticias mejorado"""
    if df.empty:
        return df
        
    if categoria != "Todas":
        df = df[df['categoria'].str.contains(categoria, case=False, na=False)]
    
    if busqueda:
        df = df[
            df['titulo'].str.contains(busqueda, case=False, na=False) | 
            df['contenido'].str.contains(busqueda, case=False, na=False) |
            df['categoria'].str.contains(busqueda, case=False, na=False)
        ]
    
    return df

# Diccionario de fuentes disponibles
fuentes_disponibles = {
    "Diario Sin Fronteras": "https://diariosinfronteras.com.pe/",
    "El Peruano": "https://elperuano.pe/",
    "La República": "https://larepublica.pe/",
    "Andina": "https://andina.pe/",
    "Perú21": "https://peru21.pe/",
    "El Comercio": "https://elcomercio.pe/",
    "Gestión": "https://gestion.pe/",
    "Expreso": "https://expreso.com.pe/",
    "Correo": "https://diariocorreo.pe/",
    "Ojo": "https://ojo.pe/",
    "Publimetro": "https://publimetro.pe/",
    "Willax": "https://willax.pe/",
    "Exitosa Noticias": "https://exitosanoticias.pe/",
    "RPP Noticias": "https://rpp.pe/",
    "América Noticias": "https://americatv.com.pe/noticias/",
    "Panamericana": "https://panamericana.pe/",
    "Canal N": "https://canaln.pe/",
    "ATV Noticias": "https://www.atv.pe/noticias",
    "La Industria": "https://laindustria.pe/",
    "Diario Uno": "https://diariouno.pe/"
}

# Patrones por dominio
PATTERNS_POR_MEDIO = {
    "diariosinfronteras.com.pe": ["/202", "/noticia", "/local", "/actualidad", "/policial", "/regional"],
    "elperuano.pe": ["/noticia", "/edicion", "/202", "/economia", "/politica", "/nacional"],
    "larepublica.pe": ["/politica", "/economia", "/sociedad", "/deportes", "/mundo", "/202"],
    "andina.pe": ["/noticia", "/202", "/edicion"],
    "peru21.pe": ["/politica", "/economia", "/mundo", "/deportes", "/espectaculos", "/202"],
    "elcomercio.pe": ["/politica", "/economia", "/peru", "/mundo", "/deporte", "/luces", "/202"],
    "gestion.pe": ["/economia", "/peru", "/mundo", "/empresas", "/202"],
    "expreso.com.pe": ["/politica", "/economia", "/actualidad", "/202"],
    "diariocorreo.pe": ["/politica", "/peru", "/mundo", "/deportes", "/espectaculos", "/202"],
    "ojo.pe": ["/actualidad", "/policial", "/202"],
    "publimetro.pe": ["/noticias", "/deportes", "/entretenimiento", "/202"],
    "willax.pe": ["/politica", "/actualidad", "/202"],
    "exitosanoticias.pe": ["/politica", "/actualidad", "/202"],
    "rpp.pe": ["/politica", "/economia", "/mundo", "/peru", "/202"],
    "americatv.com.pe": ["/noticias", "/202"],
    "panamericana.pe": ["/politica", "/nacionales", "/internacionales", "/202"],
    "canaln.pe": ["/actualidad", "/politica", "/202"],
    "atv.pe": ["/noticias", "/202"],
    "laindustria.pe": ["/actualidad", "/politica", "/202"],
    "diariouno.pe": ["/politica", "/actualidad", "/202"],
}

RSS_CANDIDATOS = ["rss", "feed", "feeds", "rss.xml", "feed.xml", "rss2.xml", "index.xml"]

EXTENSIONES_PROHIBIDAS = (
    ".jpg",".jpeg",".png",".gif",".webp",".svg",
    ".pdf",".doc",".docx",".xls",".xlsx",".ppt",".pptx",".zip",".rar"
)

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Accept-Language": "es-PE,es;q=0.9,en;q=0.8"
}

def es_permitido_por_robots(base, path):
    try:
        p = urlparse(base)
        robots_url = f"{p.scheme}://{p.netloc}/robots.txt"
        rp = urobot.RobotFileParser()
        rp.set_url(robots_url)
        rp.read()
        return rp.can_fetch(HEADERS["User-Agent"], urljoin(base, path))
    except:
        return True  # si falla robots, seguimos con cautela

def normaliza_url(base, href):
    if not href:
        return None
    href = href.strip()
    if any(href.lower().endswith(ext) for ext in EXTENSIONES_PROHIBIDAS):
        return None
    full = urljoin(base, href)
    u = urlparse(full)
    clean = u._replace(fragment="", query="").geturl()
    return clean

def parece_articulo(url):
    u = urlparse(url)
    host = u.netloc.replace("www.", "")
    path = u.path.rstrip("/").lower()
    patterns = PATTERNS_POR_MEDIO.get(host, [])
    if any(p in path for p in patterns):
        return True
    if "/2024" in path or "/2025" in path:
        return True
    # slug rico: /algo/algo/slug-con-3-palabras
    parts = [p for p in path.split("/") if p]
    slug = parts[-1] if parts else ""
    if "-" in slug and len(slug.split("-")) >= 3 and len(path) > 20:
        return True
    return False

def descubre_desde_rss(base_url):
    urls = set()
    for r in RSS_CANDIDATOS:
        rss_url = urljoin(base_url, f"/{r}")
        try:
            resp = requests.get(rss_url, headers=HEADERS, timeout=10)
            if resp.status_code == 200 and ("<rss" in resp.text or "<feed" in resp.text):
                soup = BeautifulSoup(resp.text, "xml")
                for item in soup.find_all(["item","entry"]):
                    link = item.find("link")
                    href = link.get("href") if link and link.has_attr("href") else (link.get_text(strip=True) if link else None)
                    u = normaliza_url(base_url, href)
                    if u:
                        urls.add(u)
        except:
            continue
    return urls

def descubre_desde_home(base_url, max_links=400):
    urls = set()
    try:
        resp = requests.get(base_url, headers=HEADERS, timeout=15)
        resp.raise_for_status()
        soup = BeautifulSoup(resp.text, "html.parser")
        for a in soup.find_all("a", href=True):
            u = normaliza_url(base_url, a["href"])
            if u and parece_articulo(u):
                urls.add(u)
            if len(urls) >= max_links:
                break
    except:
        pass
    return urls

def _with_query(url, **params):
    u = urlparse(url)
    q = dict([p.split("=",1) for p in u.query.split("&") if p])  # simple
    q.update(params)
    return u._replace(query=urlencode(q)).geturl()

def descubre_paginacion(base_url, max_pages=12):
    urls = set()
    for i in range(2, max_pages+1):
        candidates = [
            urljoin(base_url, f"/page/{i}/"),
            urljoin(base_url, f"/pagina/{i}/"),
            _with_query(base_url, page=i),
        ]
        for url in candidates:
            try:
                r = requests.get(url, headers=HEADERS, timeout=10)
                if r.status_code == 200 and len(r.text) > 2000:
                    soup = BeautifulSoup(r.text, "html.parser")
                    for a in soup.find_all("a", href=True):
                        u = normaliza_url(base_url, a["href"])
                        if u and parece_articulo(u):
                            urls.add(u)
            except:
                continue
    return urls

def descubre_desde_sitemap(base_url, max_items=600):
    urls = set()
    try:
        u = urlparse(base_url)
        sitemap_url = f"{u.scheme}://{u.netloc}/sitemap.xml"
        r = requests.get(sitemap_url, headers=HEADERS, timeout=15)
        if r.status_code == 200:
            soup = BeautifulSoup(r.text, "xml")
            if soup.find("sitemapindex"):
                for sm in soup.find_all("sitemap"):
                    loc = sm.find("loc")
                    if not loc: 
                        continue
                    sm_url = loc.get_text(strip=True)
                    try:
                        r2 = requests.get(sm_url, headers=HEADERS, timeout=15)
                        if r2.status_code == 200:
                            soup2 = BeautifulSoup(r2.text, "xml")
                            for loc2 in soup2.find_all("loc"):
                                u3 = normaliza_url(base_url, loc2.get_text(strip=True))
                                if u3 and parece_articulo(u3):
                                    urls.add(u3)
                                if len(urls) >= max_items:
                                    return urls
                    except:
                        continue
            else:
                for loc in soup.find_all("loc"):
                    u2 = normaliza_url(base_url, loc.get_text(strip=True))
                    if u2 and parece_articulo(u2):
                        urls.add(u2)
                    if len(urls) >= max_items:
                        break
    except:
        pass
    return urls

def extrae_mejor_texto(soup):
    """Extrae contenido LIMPIO (sin HTML)"""
    # PRIMERO: Intentar con article
    article = soup.find("article")
    if article:
        # USAR get_text() para obtener solo texto
        txt = article.get_text(" ", strip=True)
        if len(txt) > 200:
            return txt
    
    # SEGUNDO: Buscar en contenedores de contenido
    for sel in [".entry-content", ".post-content", ".article-content", ".content", "#content"]:
        box = soup.select_one(sel)
        if box:
            # USAR get_text() para obtener solo texto
            txt = box.get_text(" ", strip=True)
            if len(txt) > 200:
                return txt
    
    # TERCERO: Todos los párrafos
    ps = soup.find_all("p")
    if ps:
        # USAR get_text() en cada párrafo
        txt = " ".join(p.get_text(" ", strip=True) for p in ps[:10])
        if len(txt) > 150:
            return txt
    
    # ÚLTIMO: Todo el body como fallback (SOLO TEXTO)
    return soup.get_text(" ", strip=True)[:1000]

def fetch_articulo(url, base_url):
    try:
        if not es_permitido_por_robots(base_url, urlparse(url).path):
            return None

        for intento in range(3):
            try:
                r = requests.get(url, headers=HEADERS, timeout=15)
                if r.status_code in (429, 503):
                    time.sleep(1.5 * (intento + 1))
                    continue
                r.raise_for_status()
                break
            except:
                if intento == 2:
                    return None
                time.sleep(1.2 * (intento + 1))

        soup = BeautifulSoup(r.text, "html.parser")

        titulo = extraer_titulo(soup)
        if not titulo or len(titulo) < 8:
            return None

        contenido = extrae_mejor_texto(soup)
        if not contenido or len(contenido) < 150:
            return None

        fecha = extraer_fecha(soup)
        categoria = extraer_categoria(soup)
        imagen = extraer_imagen(soup, url)

        return (titulo.strip(), fecha or "", categoria or "General", contenido.strip(), imagen, url)
    except:
        return None

def scrapear_noticias_exhaustivo(base_url, progress_callback=None, max_links=600, max_pages=12, max_workers=10):
    """Devuelve lista de tuplas (titulo, fecha, categoria, contenido, imagen, url)"""
    urls = set()

    if progress_callback: progress_callback(5, "🔎 RSS…")
    urls |= descubre_desde_rss(base_url)

    if progress_callback: progress_callback(15, "🏠 Portada…")
    urls |= descubre_desde_home(base_url, max_links=max_links//2)

    if progress_callback: progress_callback(35, "🧭 Paginación…")
    urls |= descubre_paginacion(base_url, max_pages=max_pages)

    if progress_callback: progress_callback(55, "🗺️ Sitemap…")
    urls |= descubre_desde_sitemap(base_url, max_items=max_links)

    urls = [u for u in urls if u and not any(u.lower().endswith(ext) for ext in EXTENSIONES_PROHIBIDAS)]
    urls = list(dict.fromkeys(urls))
    if len(urls) > max_links:
        urls = urls[:max_links]

    if not urls:
        if progress_callback: progress_callback(100, "⚠️ No se hallaron artículos.")
        return []

    resultados, vistos_hash = [], set()

    def _task(u):
        h = md5(u.encode("utf-8")).hexdigest()
        if h in vistos_hash:
            return None
        vistos_hash.add(h)
        return fetch_articulo(u, base_url)

    total = len(urls)
    with concurrent.futures.ThreadPoolExecutor(max_workers=max_workers) as ex:
        futs = {ex.submit(_task, u): idx for idx, u in enumerate(urls)}
        for i, fut in enumerate(concurrent.futures.as_completed(futs)):
            res = fut.result()
            if res:
                resultados.append(res)
            if progress_callback:
                progress = 60 + int((i + 1) / total * 40)
                progress_callback(progress, f"📥 Descargando artículos ({i+1}/{total})…")

    if progress_callback:
        progress_callback(100, f" Completado - {len(resultados)} artículos válidos")

    return resultados

# Función principal
def main():
    load_css()
    init_session_state()
    crear_tablas()
    aplicar_tema()

    # Verificar autenticación
    autenticado = verificar_autenticacion()
    
    # Si no está autenticado, mostrar login y detener ejecución
    if not autenticado:
        mostrar_login()
        return
    
    # Si el usuario quiere ver su perfil
    if st.session_state.get('mostrar_perfil', False):
        mostrar_perfil()
        return
    
    # Usuario autenticado - mostrar aplicación
    mostrar_header_usuario()
    
    # Header principal
    st.markdown("""
    <div class="main-header">
        <h1>Q' PASA</h1>
        <p>Tu portal inteligente de noticias con la mejor experiencia de usuario</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Sidebar
    with st.sidebar:
        # ============ SECCIÓN: CONTROL RÁPIDO ============
        st.markdown('<div class="sidebar-section">', unsafe_allow_html=True)
        st.markdown('<h3 class="sidebar-title">⚡ Control Rápido</h3>', unsafe_allow_html=True)
        
        # Control de tema
        col_theme1, col_theme2 = st.columns([3, 2])
        with col_theme1:
            st.markdown('<div class="sidebar-subtitle">🎨 Apariencia</div>', unsafe_allow_html=True)
        with col_theme2:
            nuevo_modo = st.toggle("", value=st.session_state.get("dark_mode", False), 
                                   key="toggle_dark", help="🌙 Modo Oscuro / ☀️ Modo Claro")
            if nuevo_modo != st.session_state.get("dark_mode", False):
                st.session_state.dark_mode = nuevo_modo
                aplicar_tema()
                st.rerun()
        
        st.markdown('</div>', unsafe_allow_html=True)

        # ============ SECCIÓN: SCRAPING DE NOTICIAS ============
        st.markdown('<div class="sidebar-section">', unsafe_allow_html=True)
        st.markdown('<h3 class="sidebar-title">🌐 Obtener Noticias</h3>', unsafe_allow_html=True)
        
        # Obtener fuentes permitidas según el rol del usuario
        usuario_actual = st.session_state.get('usuario', {})
        rol_usuario = usuario_actual.get('rol', 'usuario')
        
        # Obtener fuentes permitidas para este rol
        fuentes_permitidas = obtener_fuentes_permitidas_por_rol(rol_usuario, fuentes_disponibles)
        
        if not fuentes_permitidas:
            st.warning("⚠️ No tienes permisos para scrapear ninguna fuente. Contacta al administrador.")
            st.markdown('</div>', unsafe_allow_html=True)
            st.stop()
        
        # Selección de fuentes (solo las permitidas)
        fuentes_default = fuentes_permitidas[:2] if len(fuentes_permitidas) >= 2 else fuentes_permitidas
        
        fuentes_seleccionadas = st.multiselect(
            f"Fuentes disponibles ({len(fuentes_permitidas)} permitidas):",
            options=fuentes_permitidas,
            default=fuentes_default,
            help=f"Puedes scrapear {len(fuentes_permitidas)} fuente(s) según tu rol ({rol_usuario})",
            key="fuentes_multi"
        )
        
        if len(fuentes_seleccionadas) > len(fuentes_permitidas):
            st.error("⚠️ Has seleccionado más fuentes de las permitidas para tu rol")
            fuentes_seleccionadas = fuentes_seleccionadas[:len(fuentes_permitidas)]
        
        # Botón de scraping
        col_btn1, col_btn2 = st.columns([3, 1])
        with col_btn1:
            scrape_btn = st.button(
                "🔄 Obtener Noticias", 
                type="primary", 
                use_container_width=True,
                disabled=len(fuentes_seleccionadas) == 0,
                key="scrape_btn"
            )
        with col_btn2:
            if len(fuentes_seleccionadas) > 0:
                st.markdown(f'<div style="text-align:center;padding-top:8px;color:#3b82f6;font-weight:bold;">{len(fuentes_seleccionadas)}</div>', 
                           unsafe_allow_html=True)
        
        if scrape_btn:
            progress_container = st.empty()
            status_container = st.empty()
            
            def update_progress(percent, message):
                with progress_container:
                    st.progress(percent / 100)
                with status_container:
                    st.info(f"⚙️ {message}")
            
            total_insertados = 0
            fuentes_no_permitidas = []
            
            for idx, fuente in enumerate(fuentes_seleccionadas, start=1):
                # Verificar permiso para esta fuente
                if not verificar_permiso_scraping(rol_usuario, fuente):
                    fuentes_no_permitidas.append(fuente)
                    continue
                
                url = fuentes_disponibles[fuente]
                update_progress(
                    int((idx / len(fuentes_seleccionadas)) * 100), 
                    f"Procesando {fuente} ({idx}/{len(fuentes_seleccionadas)})"
                )
                noticias = scrapear_noticias_exhaustivo(
                    url,
                    update_progress,
                    max_links=600,
                    max_pages=12,
                    max_workers=10
                )
                
                if noticias:
                    insertados = guardar_en_mysql(noticias)
                    total_insertados += insertados
            
            # Mostrar advertencia si hay fuentes no permitidas
            if fuentes_no_permitidas:
                status_container.warning(
                    f"⚠️ No tienes permisos para scrapear: {', '.join(fuentes_no_permitidas)}"
                )
            
            progress_container.empty()
            if total_insertados > 0:
                st.session_state.last_scrape = datetime.now()
                st.session_state.nuevas_noticias = total_insertados
                status_container.success(f"✅ {total_insertados} noticias nuevas agregadas!")
                time.sleep(2)
                status_container.empty()
                st.rerun()
            else:
                status_container.info("ℹ️ No se encontraron noticias nuevas")
                time.sleep(2)
                status_container.empty()
        
        # Información del último scraping
        if st.session_state.last_scrape:
            tiempo_transcurrido = datetime.now() - st.session_state.last_scrape
            minutos = int(tiempo_transcurrido.total_seconds() / 60)
            horas = minutos // 60
            mins = minutos % 60
            
            if horas > 0:
                tiempo_str = f"{horas}h {mins}m"
            else:
                tiempo_str = f"{mins}m"
            
            st.markdown(f"""
            <div style="
                background: linear-gradient(135deg, #3b82f6, #8b5cf6);
                padding: 0.75rem;
                border-radius: 8px;
                margin-top: 0.5rem;
                text-align: center;
            ">
                <div style="color: white; font-size: 0.85rem;">⏰ Última actualización</div>
                <div style="color: white; font-weight: bold; font-size: 1rem;">hace {tiempo_str}</div>
            </div>
            """, unsafe_allow_html=True)
        
        st.markdown('</div>', unsafe_allow_html=True)
        
        # ============ SECCIÓN: NAVEGACIÓN ============
        st.markdown('<div class="sidebar-section">', unsafe_allow_html=True)
        st.markdown('<h3 class="sidebar-title">🧭 Navegación</h3>', unsafe_allow_html=True)

        nav_items = [
            {"icon": "🏠", "label": "Portada", "view": "portada"},
            {"icon": "⭐", "label": "Favoritos", "view": "favoritos"},
            {"icon": "🔥", "label": "Lo Más Leído", "view": "mas_leidas"},
            {"icon": "📊", "label": "Análisis", "view": "analisis"},
        ]
        
        # Agregar dashboard admin si el usuario tiene permisos
        usuario_actual = st.session_state.get('usuario', {})
        if usuario_actual and tiene_permiso_admin(usuario_actual.get('rol', '')):
            nav_items.append({"icon": "👑", "label": "Panel Admin", "view": "admin"})

        vista_actual = st.session_state.get("vista_actual", "portada")

        for item in nav_items:
            is_active = item["view"] == vista_actual
            
            if is_active:
                st.markdown(f"""
                <div style="
                    background: linear-gradient(135deg, #3b82f6, #8b5cf6);
                    padding: 0.75rem;
                    border-radius: 8px;
                    margin-bottom: 0.5rem;
                    text-align: center;
                    color: white;
                    font-weight: bold;
                    box-shadow: 0 4px 16px rgba(0, 0, 0, 0.3);
                ">
                    {item['icon']} {item['label']} ✓
                </div>
                """, unsafe_allow_html=True)
            else:
                if st.button(
                    f"{item['icon']} {item['label']}", 
                    key=f"nav_{item['view']}", 
                    use_container_width=True
                ):
                    st.session_state.vista_actual = item["view"]
                    st.rerun()

        current_view = st.session_state.get("vista_actual", "portada")
        st.markdown('</div>', unsafe_allow_html=True)
        
        # ============ SECCIÓN: CONFIGURACIÓN ============
        st.markdown('<div class="sidebar-section">', unsafe_allow_html=True)
        st.markdown('<h3 class="sidebar-title">⚙️ Configuración</h3>', unsafe_allow_html=True)
        
        # Auto-refresh
        refresh_options = {
            "⏸️ Desactivado": 0,
            "⚡ 1 minuto": 60,
            "🔄 5 minutos": 300,
            "⏱️ 10 minutos": 600
        }
        
        auto_refresh = st.selectbox(
            "Auto-actualización:",
            list(refresh_options.keys()),
            help="Frecuencia de actualización automática",
            key="auto_refresh_select"
        )
        
        refresh_seconds = refresh_options[auto_refresh]
        if refresh_seconds > 0:
            st_autorefresh(interval=refresh_seconds * 1000, key="auto_refresh_main")
            st.markdown(f"""
            <div style="
                background: #10b981;
                color: white;
                padding: 0.5rem;
                border-radius: 6px;
                text-align: center;
                font-size: 0.85rem;
                margin-top: 0.5rem;
            ">
                ✅ Actualización activa
            </div>
            """, unsafe_allow_html=True)
        
        st.markdown('</div>', unsafe_allow_html=True)
        
        # ============ SECCIÓN: LIMPIEZA DE DATOS ============
        if st.session_state.favoritos or st.session_state.lecturas:
            st.markdown('<div class="sidebar-section">', unsafe_allow_html=True)
            st.markdown('<h3 class="sidebar-title">🧹 Mantenimiento</h3>', unsafe_allow_html=True)
            
            col_reset1, col_reset2 = st.columns([3, 2])
            with col_reset1:
                if st.button("🗑️ Reiniciar Datos", use_container_width=True, key="reset_btn"):
                    if st.session_state.get('confirmar_reset', False):
                        st.session_state.favoritos.clear()
                        st.session_state.lecturas.clear()
                        st.session_state.confirmar_reset = False
                        st.success("✅ Datos reiniciados")
                        time.sleep(1)
                        st.rerun()
                    else:
                        st.session_state.confirmar_reset = True
            
            with col_reset2:
                if st.session_state.get('confirmar_reset', False):
                    st.markdown("""
                    <div style="
                        background: #f59e0b;
                        color: white;
                        padding: 0.5rem;
                        border-radius: 6px;
                        text-align: center;
                        font-size: 0.75rem;
                        font-weight: bold;
                    ">
                        ⚠️ Confirmar
                    </div>
                    """, unsafe_allow_html=True)
            
            st.markdown('</div>', unsafe_allow_html=True)
    
    # ============ CONTENIDO PRINCIPAL ============
    # ============ CONTENIDO PRINCIPAL ============
    df = cargar_noticias()

    # 🔥🔥🔥 LIMPIEZA NUCLEAR DE HTML - ESTO SÍ FUNCIONA 🔥🔥🔥
    if not df.empty:
        import html
        import re
        
    def limpieza_nuclear(texto):
        if pd.isna(texto) or not texto:
            return ""
        texto_str = str(texto)
        
        # ELIMINACIÓN COMPLETA DE HTML
        texto_str = re.sub(r'<[^>]*>', '', texto_str)  # Elimina <cualquier_tag>
        texto_str = re.sub(r'&[a-z]+;', '', texto_str)  # Elimina &nbsp; &amp; etc.
        
        # DECODIFICAR entidades HTML
        texto_str = html.unescape(texto_str)
        
        # ELIMINAR caracteres especiales problemáticos
        texto_str = re.sub(r'[\x00-\x1f\x7f-\x9f]', '', texto_str)
        
        # LIMPIAR espacios y saltos de línea
        texto_str = ' '.join(texto_str.split())
        
        return texto_str.strip()
    
    # APLICAR LIMPIEZA NUCLEAR
        df['titulo'] = df['titulo'].apply(limpieza_nuclear)
        df['contenido'] = df['contenido'].apply(limpieza_nuclear)
        
    # VERIFICAR en consola
    print("✅ LIMPIEZA NUCLEAR APLICADA")
    if not df.empty:
        print(f"📰 Primer título: {df.iloc[0]['titulo'][:50]}")
        print(f"📄 Primer contenido: {df.iloc[0]['contenido'][:50]}")
    
    # Mostrar notificaciones
    if 'nuevas_noticias' in st.session_state and st.session_state.nuevas_noticias > 0:
        mostrar_toast(f"🎉 {st.session_state.nuevas_noticias} noticias nuevas agregadas!", "success")
        del st.session_state.nuevas_noticias
    
    # Router de vistas
    if st.session_state.get('noticia_seleccionada'):
        mostrar_detalle_noticia_mejorado(df, st.session_state.noticia_seleccionada)
    else:
        if current_view == "portada":
            if not df.empty:
                # Búsqueda avanzada
                busqueda, categoria = barra_busqueda_avanzada(df)
                df_filtrado = filtrar_noticias(df, categoria, busqueda)
                
                # Estadísticas de filtrado
                if busqueda or categoria != "Todas":
                    st.markdown(f"""
                    <div style="
                        background: linear-gradient(135deg, #3b82f6, #8b5cf6);
                        padding: 1rem;
                        border-radius: 12px;
                        text-align: center;
                        margin: 1rem 0;
                        box-shadow: 0 8px 32px rgba(0, 0, 0, 0.3);
                    ">
                        <span style="color: white; font-size: 1.1rem;">
                            📊 Mostrando <strong>{len(df_filtrado)}</strong> de <strong>{len(df)}</strong> noticias
                        </span>
                    </div>
                    """, unsafe_allow_html=True)
                
                mostrar_grid_noticias(df_filtrado)
            else:
                st.markdown("""
                <div style="
                    text-align: center;
                    padding: 4rem 2rem;
                    background: linear-gradient(135deg, #0f172a, #1e293b);
                    border-radius: 20px;
                    border: 2px solid #475569;
                    margin: 2rem 0;
                    box-shadow: 0 16px 48px rgba(0, 0, 0, 0.5);
                ">
                    <div style="font-size: 5rem; margin-bottom: 1rem;">📰</div>
                    <h2 style="color: #f8fafc; margin-bottom: 1rem;">¡Bienvenido a Pastor Noticias!</h2>
                    <p style="color: #cbd5e1; font-size: 1.1rem; margin-bottom: 2rem;">
                        Tu portal inteligente de noticias está listo para empezar
                    </p>
                    <div style="
                        background: linear-gradient(135deg, #3b82f6, #8b5cf6);
                        color: white;
                        padding: 1rem 2rem;
                        border-radius: 12px;
                        display: inline-block;
                        font-weight: bold;
                        box-shadow: 0 8px 32px rgba(0, 0, 0, 0.3);
                    ">
                        👈 Usa el botón "🔄 Obtener Noticias" en la barra lateral
                    </div>
                </div>
                """, unsafe_allow_html=True)
        
        elif current_view == "favoritos":
            mostrar_favoritos_mejorado(df)
        
        elif current_view == "mas_leidas":
            st.markdown('<div class="section-title">🔥 Lo Más Leído</div>', unsafe_allow_html=True)
            if st.session_state.lecturas:
                st.info("📊 Sección en desarrollo - Próximamente verás las noticias más leídas")
            else:
                st.markdown("""
                <div style="
                    text-align: center;
                    padding: 3rem 2rem;
                    background: #334155;
                    border-radius: 12px;
                    border: 1px solid #475569;
                ">
                    <div style="font-size: 4rem; margin-bottom: 1rem;">📚</div>
                    <h3 style="color: #f8fafc;">Aún no hay lecturas registradas</h3>
                    <p style="color: #cbd5e1;">Comienza a leer noticias para ver estadísticas aquí</p>
                </div>
                """, unsafe_allow_html=True)
            
        elif current_view == "analisis":
            mostrar_dashboard_analisis(df)
        
        elif current_view == "admin":
            # Verificar permisos antes de mostrar el dashboard admin
            usuario_actual = st.session_state.get('usuario', {})
            if usuario_actual and tiene_permiso_admin(usuario_actual.get('rol', '')):
                mostrar_dashboard_admin()
            else:
                st.error("❌ No tienes permisos para acceder al Panel de Administración")
                st.info("💡 Solo usuarios con rol 'admin' o 'super_admin' pueden acceder")
    
    # ============ FOOTER CON ESTADÍSTICAS ============
    st.markdown("---")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown("""
        <div class="stats-card">
            <div style="font-size: 2rem; margin-bottom: 0.5rem;">📊</div>
            <div style="font-weight: bold; color: #f8fafc; font-size: 1.1rem;">Estado del Sistema</div>
        """, unsafe_allow_html=True)
        
        if not df.empty:
            ultima_act = df['fecha_scraping'].max()
            tiempo_ultima = pd.to_datetime(ultima_act).strftime("%H:%M - %d/%m")
            st.markdown(f"""
            <div style="
                background: #10b981;
                color: white;
                padding: 0.75rem;
                border-radius: 8px;
                text-align: center;
                margin-top: 0.5rem;
                font-weight: bold;
            ">
                ✅ Sistema activo<br>
                <small>{tiempo_ultima}</small>
            </div>
            """, unsafe_allow_html=True)
        else:
            st.markdown("""
            <div style="
                background: #f59e0b;
                color: white;
                padding: 0.75rem;
                border-radius: 8px;
                text-align: center;
                margin-top: 0.5rem;
                font-weight: bold;
            ">
                ⏳ Sistema listo<br>
                <small>Sin datos</small>
            </div>
            """, unsafe_allow_html=True)
        
        st.markdown('</div>', unsafe_allow_html=True)
    
    with col2:
        st.markdown("""
        <div class="stats-card">
            <div style="font-size: 2rem; margin-bottom: 0.5rem;">📰</div>
            <div style="font-weight: bold; color: #f8fafc; font-size: 1.1rem;">Base de Datos</div>
        """, unsafe_allow_html=True)
        
        total_noticias = len(df)
        st.markdown(f"""
        <div style="
            background: linear-gradient(135deg, #3b82f6, #8b5cf6);
            color: white;
            padding: 0.75rem;
            border-radius: 8px;
            text-align: center;
            margin-top: 0.5rem;
            font-weight: bold;
            box-shadow: 0 8px 32px rgba(0, 0, 0, 0.3);
        ">
            {total_noticias} noticias<br>
            <small>Disponibles</small>
        </div>
        """, unsafe_allow_html=True)
        
        st.markdown('</div>', unsafe_allow_html=True)
    
    with col3:
        st.markdown("""
        <div class="stats-card">
            <div style="font-size: 2rem; margin-bottom: 0.5rem;">👤</div>
            <div style="font-weight: bold; color: #f8fafc; font-size: 1.1rem;">Actividad Personal</div>
        """, unsafe_allow_html=True)
        
        total_lecturas = sum(st.session_state.lecturas.values())
        total_favoritos = len(st.session_state.favoritos)
        
        if total_lecturas > 0 or total_favoritos > 0:
            st.markdown(f"""
            <div style="
                background: #ec4899;
                color: white;
                padding: 0.75rem;
                border-radius: 8px;
                text-align: center;
                margin-top: 0.5rem;
                font-weight: bold;
            ">
                👁️ {total_lecturas} lecturas<br>
                ⭐ {total_favoritos} favoritos
            </div>
            """, unsafe_allow_html=True)
        else:
            st.markdown("""
            <div style="
                background: #94a3b8;
                color: white;
                padding: 0.75rem;
                border-radius: 8px;
                text-align: center;
                margin-top: 0.5rem;
                font-weight: bold;
            ">
                👋 ¡Empieza a leer!<br>
                <small>Sin actividad</small>
            </div>
            """, unsafe_allow_html=True)
        
        st.markdown('</div>', unsafe_allow_html=True)
    
    # ============ FOOTER DE CRÉDITOS ============
    st.markdown("---")
    st.markdown("""
    <div style="
        text-align: center;
        padding: 1.5rem;
        background: linear-gradient(135deg, #0f172a, #1e293b);
        border-radius: 12px;
        border: 1px solid #475569;
        margin-top: 2rem;
        box-shadow: 0 16px 48px rgba(0, 0, 0, 0.5);
    ">
        <div style="font-size: 2rem; margin-bottom: 0.5rem;">💻</div>
        <div style="color: #f8fafc; font-size: 1.2rem; font-weight: bold; margin-bottom: 0.5rem;">
            Pastor Noticias
        </div>
        <div style="color: #cbd5e1; font-size: 0.95rem;">
            Sistema inteligente de gestión y análisis de noticias
        </div>
        <div style="
            margin-top: 1rem;
            padding-top: 1rem;
            border-top: 1px solid #475569;
            color: #94a3b8;
            font-size: 0.85rem;
        ">
            Desarrollado con ❤️ usando Streamlit
        </div>
    </div>
    """, unsafe_allow_html=True)

if __name__ == "__main__":
    main()