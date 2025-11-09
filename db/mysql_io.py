# db/mysql_io.py
import pandas as pd
import mysql.connector
from mysql.connector import Error
from config import DatabaseConfig

def conectar_mysql():
    """Usa la config centralizada"""
    return DatabaseConfig.get_connection()

def crear_tablas():
    """Reutiliza la creación desde config.py"""
    DatabaseConfig.setup_tables()

def guardar_en_mysql(noticias):
    """
    noticias: lista de tuplas (titulo, fecha, categoria, contenido, imagen, url_original)
    """
    conn = conectar_mysql()
    if not conn:
        return 0
    cur = conn.cursor()

    sql = """INSERT INTO SCRAP (titulo, fecha, categoria, contenido, imagen, url_original)
            VALUES (%s, %s, %s, %s, %s, %s)"""

    insertados = 0
    for row in noticias:
        try:
            cur.execute(sql, row)
            insertados += 1
        except mysql.connector.IntegrityError:
            # Evita duplicados por UNIQUE(titulo)
            pass
        except Exception as e:
            print(f"[DB] Error insertando: {e}")

    conn.commit()
    cur.close()
    conn.close()
    return insertados

def cargar_noticias():
    conn = conectar_mysql()
    if not conn:
        return pd.DataFrame()
    try:
        df = pd.read_sql("SELECT * FROM SCRAP ORDER BY fecha_scraping DESC", conn)
        conn.close()
        return df
    except Exception as e:
        print(f"[DB] Error leyendo noticias: {e}")
        conn.close()
        return pd.DataFrame()

def registrar_lectura(noticia_id, ip_address=None, user_agent=None):
    conn = conectar_mysql()
    if not conn:
        return
    try:
        cur = conn.cursor()
        cur.execute(
            "INSERT INTO lecturas (noticia_id, ip_address, user_agent) VALUES (%s, %s, %s)",
            (int(noticia_id), ip_address, user_agent)
        )
        conn.commit()
    except Exception as e:
        print(f"[DB] Error al registrar lectura: {e}")
    finally:
        cur.close()
        conn.close()
