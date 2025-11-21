# db/admin.py - Funciones de administración de usuarios y permisos
from config import DatabaseConfig
import mysql.connector
from mysql.connector import Error
from typing import List, Dict, Optional, Tuple

def obtener_todos_usuarios():
    """Obtener todos los usuarios"""
    conn = DatabaseConfig.get_connection()
    if not conn:
        return []
    
    try:
        cursor = conn.cursor(dictionary=True)
        cursor.execute("""
            SELECT id, username, email, nombre_completo, rol, activo, 
                   fecha_registro, ultimo_acceso
            FROM usuarios
            ORDER BY fecha_registro DESC
        """)
        usuarios = cursor.fetchall()
        cursor.close()
        conn.close()
        return usuarios
    except Error as e:
        if conn:
            conn.close()
        return []

def obtener_usuario_por_id(usuario_id: int):
    """Obtener un usuario por su ID"""
    conn = DatabaseConfig.get_connection()
    if not conn:
        return None
    
    try:
        cursor = conn.cursor(dictionary=True)
        cursor.execute("""
            SELECT id, username, email, nombre_completo, rol, activo,
                   fecha_registro, ultimo_acceso
            FROM usuarios
            WHERE id = %s
        """, (usuario_id,))
        usuario = cursor.fetchone()
        cursor.close()
        conn.close()
        return usuario
    except Error as e:
        if conn:
            conn.close()
        return None

def actualizar_usuario(usuario_id: int, nombre_completo: Optional[str] = None,
                      rol: Optional[str] = None, activo: Optional[bool] = None,
                      email: Optional[str] = None):
    """Actualizar datos de un usuario"""
    conn = DatabaseConfig.get_connection()
    if not conn:
        return False, "Error de conexión"
    
    try:
        cursor = conn.cursor()
        
        # Construir query dinámicamente
        updates = []
        valores = []
        
        if nombre_completo is not None:
            updates.append("nombre_completo = %s")
            valores.append(nombre_completo)
        
        if rol is not None:
            updates.append("rol = %s")
            valores.append(rol)
        
        if activo is not None:
            updates.append("activo = %s")
            valores.append(activo)
        
        if email is not None:
            updates.append("email = %s")
            valores.append(email)
        
        if not updates:
            cursor.close()
            conn.close()
            return False, "No hay campos para actualizar"
        
        valores.append(usuario_id)
        query = f"UPDATE usuarios SET {', '.join(updates)} WHERE id = %s"
        
        cursor.execute(query, valores)
        conn.commit()
        cursor.close()
        conn.close()
        
        return True, None
    except Error as e:
        if conn:
            conn.rollback()
            conn.close()
        return False, str(e)

def eliminar_usuario(usuario_id: int):
    """Eliminar un usuario (soft delete - desactivar)"""
    return actualizar_usuario(usuario_id, activo=False)

def obtener_estadisticas_usuarios():
    """Obtener estadísticas de usuarios"""
    conn = DatabaseConfig.get_connection()
    if not conn:
        return {}
    
    try:
        cursor = conn.cursor(dictionary=True)
        
        # Total usuarios
        cursor.execute("SELECT COUNT(*) as total FROM usuarios")
        total = cursor.fetchone()['total']
        
        # Usuarios activos
        cursor.execute("SELECT COUNT(*) as total FROM usuarios WHERE activo = TRUE")
        activos = cursor.fetchone()['total']
        
        # Usuarios por rol
        cursor.execute("""
            SELECT rol, COUNT(*) as cantidad
            FROM usuarios
            GROUP BY rol
        """)
        por_rol = {row['rol']: row['cantidad'] for row in cursor.fetchall()}
        
        # Usuarios registrados hoy
        cursor.execute("""
            SELECT COUNT(*) as total
            FROM usuarios
            WHERE DATE(fecha_registro) = CURDATE()
        """)
        registrados_hoy = cursor.fetchone()['total']
        
        cursor.close()
        conn.close()
        
        return {
            'total': total,
            'activos': activos,
            'inactivos': total - activos,
            'por_rol': por_rol,
            'registrados_hoy': registrados_hoy
        }
    except Error as e:
        if conn:
            conn.close()
        return {}

def obtener_permisos_scraping_por_rol(rol: str):
    """Obtener permisos de scraping para un rol específico"""
    conn = DatabaseConfig.get_connection()
    if not conn:
        return []
    
    try:
        cursor = conn.cursor(dictionary=True)
        cursor.execute("""
            SELECT id, fuente_nombre, fuente_url, permitido
            FROM permisos_scraping_rol
            WHERE rol = %s
            ORDER BY fuente_nombre
        """, (rol,))
        permisos = cursor.fetchall()
        cursor.close()
        conn.close()
        return permisos
    except Error as e:
        if conn:
            conn.close()
        return []

def obtener_todos_permisos():
    """Obtener todos los permisos agrupados por rol"""
    conn = DatabaseConfig.get_connection()
    if not conn:
        return {}
    
    try:
        cursor = conn.cursor(dictionary=True)
        cursor.execute("""
            SELECT rol, fuente_nombre, fuente_url, permitido
            FROM permisos_scraping_rol
            ORDER BY rol, fuente_nombre
        """)
        permisos_raw = cursor.fetchall()
        cursor.close()
        conn.close()
        
        # Agrupar por rol
        permisos_por_rol = {}
        for permiso in permisos_raw:
            rol = permiso['rol']
            if rol not in permisos_por_rol:
                permisos_por_rol[rol] = []
            permisos_por_rol[rol].append(permiso)
        
        return permisos_por_rol
    except Error as e:
        if conn:
            conn.close()
        return {}

def actualizar_permiso_scraping(rol: str, fuente_nombre: str, fuente_url: str, permitido: bool):
    """Actualizar o crear un permiso de scraping"""
    conn = DatabaseConfig.get_connection()
    if not conn:
        return False, "Error de conexión"
    
    try:
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO permisos_scraping_rol (rol, fuente_nombre, fuente_url, permitido)
            VALUES (%s, %s, %s, %s)
            ON DUPLICATE KEY UPDATE permitido = %s, fecha_actualizacion = NOW()
        """, (rol, fuente_nombre, fuente_url, permitido, permitido))
        
        conn.commit()
        cursor.close()
        conn.close()
        return True, None
    except Error as e:
        if conn:
            conn.rollback()
            conn.close()
        return False, str(e)

def verificar_permiso_scraping(rol: str, fuente_nombre: str) -> bool:
    """Verificar si un rol tiene permiso para scrapear una fuente"""
    # Super admin tiene acceso a todo
    if rol == 'super_admin':
        return True
    
    conn = DatabaseConfig.get_connection()
    if not conn:
        return False
    
    try:
        cursor = conn.cursor()
        cursor.execute("""
            SELECT permitido
            FROM permisos_scraping_rol
            WHERE rol = %s AND fuente_nombre = %s
        """, (rol, fuente_nombre))
        
        result = cursor.fetchone()
        cursor.close()
        conn.close()
        
        # Si no existe el permiso, por defecto no tiene acceso (excepto super_admin)
        if result:
            return bool(result[0])
        return False
    except Error as e:
        if conn:
            conn.close()
        return False

def obtener_fuentes_permitidas_por_rol(rol: str, todas_las_fuentes: Dict[str, str]) -> List[str]:
    """Obtener lista de fuentes permitidas para un rol"""
    if rol == 'super_admin':
        return list(todas_las_fuentes.keys())
    
    permisos = obtener_permisos_scraping_por_rol(rol)
    fuentes_permitidas = []
    
    for permiso in permisos:
        if permiso['permitido'] and permiso['fuente_nombre'] in todas_las_fuentes:
            fuentes_permitidas.append(permiso['fuente_nombre'])
    
    return fuentes_permitidas

def es_super_admin(rol: str) -> bool:
    """Verificar si un rol es super admin"""
    return rol == 'super_admin'

def tiene_permiso_admin(rol: str) -> bool:
    """Verificar si un rol tiene permisos de administración"""
    return rol in ['super_admin', 'admin']

