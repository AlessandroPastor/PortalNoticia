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
            
            # Tabla de usuarios
            cursor.execute("""
            CREATE TABLE IF NOT EXISTS usuarios (
                id INT AUTO_INCREMENT PRIMARY KEY,
                username VARCHAR(100) UNIQUE NOT NULL,
                email VARCHAR(255) UNIQUE NOT NULL,
                password_hash VARCHAR(255) NOT NULL,
                nombre_completo VARCHAR(200),
                rol ENUM('super_admin', 'admin', 'editor', 'usuario') DEFAULT 'usuario',
                activo BOOLEAN DEFAULT TRUE,
                fecha_registro TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                ultimo_acceso TIMESTAMP NULL,
                avatar TEXT
            ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
            """)
            
            # Tabla de sesiones
            cursor.execute("""
            CREATE TABLE IF NOT EXISTS sesiones (
                id INT AUTO_INCREMENT PRIMARY KEY,
                usuario_id INT NOT NULL,
                session_token VARCHAR(255) UNIQUE NOT NULL,
                ip_address VARCHAR(45),
                user_agent TEXT,
                fecha_inicio TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                fecha_expiracion TIMESTAMP NOT NULL,
                activa BOOLEAN DEFAULT TRUE,
                FOREIGN KEY (usuario_id) REFERENCES usuarios(id) ON DELETE CASCADE,
                INDEX idx_session_token (session_token),
                INDEX idx_usuario_activa (usuario_id, activa)
            ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
            """)
            
            # Tabla de favoritos de usuario (relación usuario-noticia)
            cursor.execute("""
            CREATE TABLE IF NOT EXISTS favoritos_usuario (
                id INT AUTO_INCREMENT PRIMARY KEY,
                usuario_id INT NOT NULL,
                noticia_id INT NOT NULL,
                fecha_favorito TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (usuario_id) REFERENCES usuarios(id) ON DELETE CASCADE,
                FOREIGN KEY (noticia_id) REFERENCES SCRAP(id) ON DELETE CASCADE,
                UNIQUE KEY unique_usuario_noticia (usuario_id, noticia_id)
            ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
            """)
            
            # Tabla de lecturas de usuario (relación usuario-noticia)
            cursor.execute("""
            CREATE TABLE IF NOT EXISTS lecturas_usuario (
                id INT AUTO_INCREMENT PRIMARY KEY,
                usuario_id INT NOT NULL,
                noticia_id INT NOT NULL,
                fecha_lectura TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                tiempo_lectura INT DEFAULT 0,
                completado BOOLEAN DEFAULT FALSE,
                FOREIGN KEY (usuario_id) REFERENCES usuarios(id) ON DELETE CASCADE,
                FOREIGN KEY (noticia_id) REFERENCES SCRAP(id) ON DELETE CASCADE,
                INDEX idx_usuario_fecha (usuario_id, fecha_lectura)
            ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
            """)
            
            # Tabla de permisos de scraping por rol
            cursor.execute("""
            CREATE TABLE IF NOT EXISTS permisos_scraping_rol (
                id INT AUTO_INCREMENT PRIMARY KEY,
                rol VARCHAR(50) NOT NULL,
                fuente_nombre VARCHAR(200) NOT NULL,
                fuente_url VARCHAR(500) NOT NULL,
                permitido BOOLEAN DEFAULT TRUE,
                fecha_creacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                fecha_actualizacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
                UNIQUE KEY unique_rol_fuente (rol, fuente_nombre),
                INDEX idx_rol (rol)
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
            
            # Insertar usuario administrador por defecto
            # Contraseña: admin123 (se debe cambiar después del primer login)
            import hashlib
            import secrets
            salt = secrets.token_hex(16)
            password_default = "admin123"
            password_hash = hashlib.sha256((password_default + salt).encode()).hexdigest()
            
            cursor.execute("""
            INSERT IGNORE INTO usuarios (username, email, password_hash, nombre_completo, rol, activo)
            VALUES ('admin', 'admin@pastornoticias.com', %s, 'Administrador del Sistema', 'super_admin', TRUE)
            """, (f"{salt}:{password_hash}",))
            
            # Inicializar permisos de scraping por rol
            # Super admin y admin pueden scrapear todas las fuentes
            # Editor puede scrapear fuentes básicas y algunas avanzadas
            # Usuario solo puede scrapear fuentes básicas
            fuentes_basicas = [
                ("Diario Sin Fronteras", "https://diariosinfronteras.com.pe/"),
                ("La República", "https://larepublica.pe/"),
            ]
            
            fuentes_avanzadas = [
                ("El Peruano", "https://elperuano.pe/"),
                ("Andina", "https://andina.pe/"),
                ("Perú21", "https://peru21.pe/"),
                ("El Comercio", "https://elcomercio.pe/"),
            ]
            
            # Super admin y admin: todas las fuentes
            for rol_permiso in ['super_admin', 'admin']:
                for fuente_nombre, fuente_url in fuentes_basicas + fuentes_avanzadas:
                    cursor.execute("""
                    INSERT IGNORE INTO permisos_scraping_rol (rol, fuente_nombre, fuente_url, permitido)
                    VALUES (%s, %s, %s, TRUE)
                    """, (rol_permiso, fuente_nombre, fuente_url))
            
            # Editor: fuentes básicas y algunas avanzadas
            for fuente_nombre, fuente_url in fuentes_basicas + fuentes_avanzadas[:2]:
                cursor.execute("""
                INSERT IGNORE INTO permisos_scraping_rol (rol, fuente_nombre, fuente_url, permitido)
                VALUES ('editor', %s, %s, TRUE)
                """, (fuente_nombre, fuente_url))
            
            # Usuario: solo fuentes básicas
            for fuente_nombre, fuente_url in fuentes_basicas:
                cursor.execute("""
                INSERT IGNORE INTO permisos_scraping_rol (rol, fuente_nombre, fuente_url, permitido)
                VALUES ('usuario', %s, %s, TRUE)
                """, (fuente_nombre, fuente_url))
            
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