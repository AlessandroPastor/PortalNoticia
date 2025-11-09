# config.py - Configuración de la base de datos

import mysql.connector
from mysql.connector import Error

class DatabaseConfig:
    """Configuración centralizada de la base de datos"""
    
    # Configuración de conexión
    HOST = "127.0.0.1"
    PORT = 3306
    USER = "root"
    PASSWORD = ""  # Cambia según tu configuración
    DATABASE = "pastor_noticias_db"
    
    @classmethod
    def get_connection(cls):
        """Obtener conexión a la base de datos"""
        try:
            connection = mysql.connector.connect(
                host=cls.HOST,
                port=cls.PORT,
                user=cls.USER,
                password=cls.PASSWORD,
                database=cls.DATABASE,
                charset='utf8mb4',
                autocommit=False
            )
            return connection
        except Error as e:
            print(f"Error de conexión: {e}")
            return None
    
    @classmethod
    def create_database(cls):
        """Crear la base de datos si no existe"""
        try:
            connection = mysql.connector.connect(
                host=cls.HOST,
                port=cls.PORT,
                user=cls.USER,
                password=cls.PASSWORD
            )
            cursor = connection.cursor()
            cursor.execute(f"CREATE DATABASE IF NOT EXISTS {cls.DATABASE} CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci")
            cursor.close()
            connection.close()
            print(f"Base de datos '{cls.DATABASE}' creada/verificada correctamente")
        except Error as e:
            print(f"Error al crear la base de datos: {e}")
    
    @classmethod
    def setup_tables(cls):
        """Configurar todas las tablas necesarias"""
        cls.create_database()
        
        connection = cls.get_connection()
        if not connection:
            return False
        
        cursor = connection.cursor()
        
        try:
            # Tabla principal de noticias
            cursor.execute("""
            CREATE TABLE IF NOT EXISTS SCRAP (
                id INT AUTO_INCREMENT PRIMARY KEY,
                titulo VARCHAR(1000) NOT NULL,
                fecha VARCHAR(200),
                categoria VARCHAR(200),
                contenido LONGTEXT,
                imagen TEXT,
                url_original TEXT,
                fecha_scraping TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                activa BOOLEAN DEFAULT TRUE,
                UNIQUE KEY unique_titulo (titulo(500))
            ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
            """)
            
            # Tabla de favoritos
            cursor.execute("""
            CREATE TABLE IF NOT EXISTS favoritos (
                id INT AUTO_INCREMENT PRIMARY KEY,
                noticia_id INT NOT NULL,
                fecha_favorito TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (noticia_id) REFERENCES SCRAP(id) ON DELETE CASCADE
            ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
            """)
            
            # Tabla de lecturas
            cursor.execute("""
            CREATE TABLE IF NOT EXISTS lecturas (
                id INT AUTO_INCREMENT PRIMARY KEY,
                noticia_id INT NOT NULL,
                fecha_lectura TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                ip_address VARCHAR(45),
                user_agent TEXT,
                FOREIGN KEY (noticia_id) REFERENCES SCRAP(id) ON DELETE CASCADE
            ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
            """)
            
            # Tabla de configuración
            cursor.execute("""
            CREATE TABLE IF NOT EXISTS configuracion (
                id INT AUTO_INCREMENT PRIMARY KEY,
                clave VARCHAR(100) UNIQUE NOT NULL,
                valor TEXT,
                descripcion TEXT,
                fecha_actualizacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
            ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
            """)
            
            # Tabla de logs de scraping
            cursor.execute("""
            CREATE TABLE IF NOT EXISTS scraping_logs (
                id INT AUTO_INCREMENT PRIMARY KEY,
                url VARCHAR(500) NOT NULL,
                noticias_encontradas INT DEFAULT 0,
                noticias_nuevas INT DEFAULT 0,
                fecha_scraping TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                duracion_segundos DECIMAL(10,2),
                error_message TEXT,
                estado ENUM('exitoso', 'error', 'parcial') DEFAULT 'exitoso'
            ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
            """)
            
            # Insertar configuraciones por defecto
            configuraciones_default = [
                ('url_scraping', 'https://diariosinfronteras.com.pe/', 'URL principal para scraping'),
                ('intervalo_scraping', '120', 'Intervalo de scraping en segundos'),
                ('max_noticias_scraping', '50', 'Máximo de noticias por sesión de scraping'),
                ('modo_debug', 'false', 'Activar modo debug'),
                ('auto_scraping', 'true', 'Activar scraping automático')
            ]
            
            for clave, valor, descripcion in configuraciones_default:
                cursor.execute("""
                INSERT IGNORE INTO configuracion (clave, valor, descripcion) 
                VALUES (%s, %s, %s)
                """, (clave, valor, descripcion))
            
            connection.commit()
            print("Tablas configuradas correctamente")
            return True
            
        except Error as e:
            connection.rollback()
            print(f"Error al configurar tablas: {e}")
            return False
        finally:
            cursor.close()
            connection.close()

# Script para ejecutar la configuración
if __name__ == "__main__":
    print("Configurando base de datos Pastor Noticias...")
    DatabaseConfig.setup_tables()
    print("Configuración completada.")