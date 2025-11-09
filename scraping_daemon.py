# scraping_daemon.py - Servicio de scraping automático

import time
import schedule
import requests
from bs4 import BeautifulSoup
import mysql.connector
from urllib.parse import urljoin
import logging
from datetime import datetime, timedelta
import json
import sys
import signal
import threading
from config import DatabaseConfig

# Configuración de logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('scraping_daemon.log'),
        logging.StreamHandler(sys.stdout)
    ]
)

logger = logging.getLogger(__name__)

class ScrapingDaemon:
    """Demonio para scraping automático de noticias"""
    
    def __init__(self):
        self.running = True
        self.config = self.load_config()
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        })
        
        # Configurar manejadores de señales
        signal.signal(signal.SIGINT, self.signal_handler)
        signal.signal(signal.SIGTERM, self.signal_handler)
    
    def load_config(self):
        """Cargar configuración desde la base de datos"""
        try:
            connection = DatabaseConfig.get_connection()
            cursor = connection.cursor(dictionary=True)
            cursor.execute("SELECT clave, valor FROM configuracion")
            config_rows = cursor.fetchall()
            
            config = {}
            for row in config_rows:
                key = row['clave']
                value = row['valor']
                
                # Convertir valores según el tipo
                if value.lower() in ['true', 'false']:
                    config[key] = value.lower() == 'true'
                elif value.isdigit():
                    config[key] = int(value)
                else:
                    config[key] = value
            
            cursor.close()
            connection.close()
            
            logger.info("Configuración cargada correctamente")
            return config
            
        except Exception as e:
            logger.error(f"Error al cargar configuración: {e}")
            # Configuración por defecto
            return {
                'url_scraping': 'https://diariosinfronteras.com.pe/',
                'intervalo_scraping': 120,
                'max_noticias_scraping': 50,
                'modo_debug': False,
                'auto_scraping': True
            }
    
    def signal_handler(self, signum, frame):
        """Manejador para señales de terminación"""
        logger.info(f"Recibida señal {signum}, cerrando daemon...")
        self.running = False
    
    def scrapear_noticias(self, url):
        """Función principal de scraping"""
        start_time = time.time()
        noticias_encontradas = 0
        noticias_nuevas = 0
        error_message = None
        
        try:
            logger.info(f"Iniciando scraping de: {url}")
            
            response = self.session.get(url, timeout=15)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.text, "html.parser")
            enlaces = soup.find_all("a", href=True)
            
            # Filtrar enlaces válidos
            enlaces_validos = []
            for enlace in enlaces[:self.config.get('max_noticias_scraping', 50)]:
                link = enlace["href"]
                full_link = urljoin(url, link)
                
                # Filtros mejorados
                if self.is_valid_news_link(full_link):
                    enlaces_validos.append(full_link)
            
            logger.info(f"Encontrados {len(enlaces_validos)} enlaces válidos")
            
            # Procesar cada enlace
            noticias = []
            for link in enlaces_validos:
                try:
                    noticia = self.procesar_noticia(link)
                    if noticia:
                        noticias.append(noticia)
                        noticias_encontradas += 1
                        
                        if self.config.get('modo_debug'):
                            logger.debug(f"Noticia procesada: {noticia[0][:50]}...")
                        
                        # Pausa entre requests para ser respetuoso
                        time.sleep(1)
                        
                except Exception as e:
                    if self.config.get('modo_debug'):
                        logger.warning(f"Error procesando {link}: {e}")
                    continue
            
            # Guardar noticias
            if noticias:
                noticias_nuevas = self.guardar_noticias(noticias)
                logger.info(f"Guardadas {noticias_nuevas} noticias nuevas de {noticias_encontradas} encontradas")
            
            # Registrar log de scraping
            duracion = time.time() - start_time
            self.log_scraping(url, noticias_encontradas, noticias_nuevas, duracion, None, 'exitoso')
            
            return noticias_nuevas
            
        except Exception as e:
            error_message = str(e)
            logger.error(f"Error en scraping: {e}")
            
            # Registrar log de error
            duracion = time.time() - start_time
            self.log_scraping(url, noticias_encontradas, noticias_nuevas, duracion, error_message, 'error')
            
            return 0
    
    def is_valid_news_link(self, link):
        """Verificar si un enlace es válido para noticias"""
        # Filtros de exclusión
        exclude_patterns = [
            '.jpg', '.png', '.gif', '.pdf', '.doc', '.zip',
            'mailto:', 'tel:', '#', 'javascript:',
            '/wp-admin/', '/wp-login/', '/feed/',
            '/tag/', '/author/', '/search',
            'facebook.com', 'twitter.com', 'instagram.com'
        ]
        
        for pattern in exclude_patterns:
            if pattern in link.lower():
                return False
        
        # Filtros de inclusión
        include_patterns = ['2024', '2025', '/noticia', '/articulo', '/post']
        
        return any(pattern in link.lower() for pattern in include_patterns)
    
    def procesar_noticia(self, url):
        """Procesar una noticia individual"""
        try:
            response = self.session.get(url, timeout=10)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.text, "html.parser")
            
            # Extraer datos
            titulo = self.extraer_titulo(soup)
            fecha = self.extraer_fecha(soup)
            categoria = self.extraer_categoria(soup)
            contenido = self.extraer_contenido(soup)
            imagen = self.extraer_imagen(soup, url)
            
            # Validar noticia
            if not titulo or not contenido or len(contenido) < 100:
                return None
            
            # Limpiar y validar datos
            titulo = titulo.strip()[:1000]  # Limitar longitud
            contenido = contenido.strip()
            
            return (titulo, fecha, categoria, contenido, imagen, url)
            
        except Exception as e:
            if self.config.get('modo_debug'):
                logger.warning(f"Error procesando noticia {url}: {e}")
            return None
    
    def extraer_titulo(self, soup):
        """Extraer título con múltiples estrategias"""
        selectors = [
            "h1",
            ".entry-title",
            ".post-title",
            ".article-title",
            "[class*='title']",
            "title"
        ]
        
        for selector in selectors:
            elements = soup.select(selector)
            for element in elements:
                title = element.get_text(strip=True)
                if len(title) > 10 and len(title) < 200:
                    return title
        return None
    
    def extraer_fecha(self, soup):
        """Extraer fecha con múltiples estrategias"""
        # Buscar en elementos time
        time_elem = soup.find("time")
        if time_elem:
            datetime_attr = time_elem.get("datetime")
            if datetime_attr:
                return datetime_attr
            text_content = time_elem.get_text(strip=True)
            if text_content:
                return text_content
        
        # Buscar en meta tags
        meta_selectors = [
            {"property": "article:published_time"},
            {"name": "pubdate"},
            {"property": "og:published_time"}
        ]
        
        for selector in meta_selectors:
            meta_elem = soup.find("meta", selector)
            if meta_elem and meta_elem.get("content"):
                return meta_elem.get("content")
        
        # Buscar en clases comunes
        date_classes = [".date", ".published", ".post-date", "[class*='date']"]
        for cls in date_classes:
            elem = soup.select_one(cls)
            if elem:
                date_text = elem.get_text(strip=True)
                if date_text and len(date_text) < 50:
                    return date_text
        
        return datetime.now().strftime("%Y-%m-%d %H:%M")
    
    def extraer_categoria(self, soup):
        """Extraer categoría"""
        # Buscar en enlaces de categoría
        cat_selectors = [
            "a[rel='category tag']",
            ".category a",
            ".cat-links a",
            "[class*='category'] a"
        ]
        
        for selector in cat_selectors:
            elem = soup.select_one(selector)
            if elem:
                cat_text = elem.get_text(strip=True)
                if cat_text and len(cat_text) < 50:
                    return cat_text
        
        # Buscar en meta tags
        meta_cat = soup.find("meta", {"property": "article:section"})
        if meta_cat:
            return meta_cat.get("content")
        
        return "General"
    
    def extraer_contenido(self, soup):
        """Extraer contenido del artículo"""
        # Buscar en contenedores específicos
        content_selectors = [
            "article",
            ".entry-content",
            ".post-content",
            ".article-content",
            ".content",
            ".story-body",
            "[class*='content']"
        ]
        
        for selector in content_selectors:
            container = soup.select_one(selector)
            if container:
                # Eliminar scripts, styles y otros elementos no deseados
                for tag in container(["script", "style", "nav", "aside", "footer"]):
                    tag.decompose()
                
                paragraphs = container.find_all("p")
                if paragraphs:
                    content = " ".join([p.get_text(strip=True) for p in paragraphs])
                    if len(content) > 100:
                        return content
        
        # Último recurso: todos los párrafos
        paragraphs = soup.find_all("p")
        content = " ".join([p.get_text(strip=True) for p in paragraphs[:15]])
        return content if len(content) > 100 else None
    
    def extraer_imagen(self, soup, base_url):
        """Extraer imagen destacada"""
        # Buscar imagen destacada
        img_selectors = [
            "img.wp-post-image",
            ".featured-image img",
            ".post-thumbnail img",
            "article img:first-of-type",
            ".entry-content img:first-of-type"
        ]
        
        for selector in img_selectors:
            img = soup.select_one(selector)
            if img and img.get("src"):
                src = img["src"]
                if src.startswith("http"):
                    return src
                else:
                    return urljoin(base_url, src)
        
        # Buscar en meta tags
        og_img = soup.find("meta", {"property": "og:image"})
        if og_img and og_img.get("content"):
            return og_img.get("content")
        
        return None
    
    def guardar_noticias(self, noticias):
        """Guardar noticias en la base de datos"""
        try:
            connection = DatabaseConfig.get_connection()
            cursor = connection.cursor()
            
            # Obtener títulos existentes
            cursor.execute("SELECT titulo FROM SCRAP WHERE activa = TRUE")
            existentes = set([row[0] for row in cursor.fetchall()])
            
            sql = """INSERT INTO SCRAP (titulo, fecha, categoria, contenido, imagen, url_original) 
                     VALUES (%s, %s, %s, %s, %s, %s)"""
            
            insertados = 0
            for noticia in noticias:
                if noticia[0] not in existentes:
                    try:
                        cursor.execute(sql, noticia)
                        insertados += 1
                    except mysql.connector.IntegrityError:
                        continue
            
            connection.commit()
            cursor.close()
            connection.close()
            
            return insertados
            
        except Exception as e:
            logger.error(f"Error guardando noticias: {e}")
            return 0
    
    def log_scraping(self, url, encontradas, nuevas, duracion, error, estado):
        """Registrar log de scraping"""
        try:
            connection = DatabaseConfig.get_connection()
            cursor = connection.cursor()
            
            cursor.execute("""
            INSERT INTO scraping_logs 
            (url, noticias_encontradas, noticias_nuevas, duracion_segundos, error_message, estado)
            VALUES (%s, %s, %s, %s, %s, %s)
            """, (url, encontradas, nuevas, duracion, error, estado))
            
            connection.commit()
            cursor.close()
            connection.close()
            
        except Exception as e:
            logger.error(f"Error registrando log: {e}")
    
    def job_scraping(self):
        """Job principal de scraping"""
        if not self.config.get('auto_scraping', True):
            return
        
        url = self.config.get('url_scraping', 'https://diariosinfronteras.com.pe/')
        nuevas_noticias = self.scrapear_noticias(url)
        
        if nuevas_noticias > 0:
            logger.info(f"Scraping completado: {nuevas_noticias} noticias nuevas")
        else:
            logger.info("Scraping completado: sin noticias nuevas")
    
    def cleanup_old_data(self):
        """Limpiar datos antiguos"""
        try:
            connection = DatabaseConfig.get_connection()
            cursor = connection.cursor()
            
            # Eliminar logs antiguos (más de 30 días)
            cursor.execute("""
            DELETE FROM scraping_logs 
            WHERE fecha_scraping < DATE_SUB(NOW(), INTERVAL 30 DAY)
            """)
            
            # Marcar noticias muy antiguas como inactivas (más de 90 días)
            cursor.execute("""
            UPDATE SCRAP 
            SET activa = FALSE 
            WHERE fecha_scraping < DATE_SUB(NOW(), INTERVAL 90 DAY) 
            AND activa = TRUE
            """)
            
            connection.commit()
            cursor.close()
            connection.close()
            
            logger.info("Limpieza de datos completada")
            
        except Exception as e:
            logger.error(f"Error en limpieza de datos: {e}")
    
    def run(self):
        """Ejecutar el daemon"""
        logger.info("Iniciando Pastor Noticias Daemon...")
        
        # Configurar jobs
        intervalo = self.config.get('intervalo_scraping', 120)
        schedule.every(intervalo).seconds.do(self.job_scraping)
        schedule.every().day.at("02:00").do(self.cleanup_old_data)
        
        logger.info(f"Daemon configurado - Scraping cada {intervalo} segundos")
        
        # Ejecutar primer scraping
        if self.config.get('auto_scraping', True):
            self.job_scraping()
        
        # Loop principal
        while self.running:
            try:
                schedule.run_pending()
                time.sleep(1)
            except KeyboardInterrupt:
                logger.info("Interrupción por teclado recibida")
                break
            except Exception as e:
                logger.error(f"Error en loop principal: {e}")
                time.sleep(5)
        
        logger.info("Daemon detenido")

def main():
    """Función principal"""
    try:
        daemon = ScrapingDaemon()
        daemon.run()
    except Exception as e:
        logger.error(f"Error crítico: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()