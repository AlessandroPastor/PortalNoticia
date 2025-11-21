# db/auth.py - Funciones de autenticación
import hashlib
import secrets
import uuid
from datetime import datetime, timedelta
from config import DatabaseConfig
import mysql.connector
from mysql.connector import Error

def hash_password(password):
    """Hashea una contraseña con salt"""
    salt = secrets.token_hex(16)
    password_hash = hashlib.sha256((password + salt).encode()).hexdigest()
    return f"{salt}:{password_hash}"

def verify_password(password, stored_hash):
    """Verifica una contraseña contra el hash almacenado"""
    try:
        salt, password_hash = stored_hash.split(":", 1)
        computed_hash = hashlib.sha256((password + salt).encode()).hexdigest()
        return computed_hash == password_hash
    except:
        return False

def crear_usuario(username, email, password, nombre_completo=None, rol='usuario'):
    """Crear un nuevo usuario"""
    conn = DatabaseConfig.get_connection()
    if not conn:
        return None, "Error de conexión a la base de datos"
    
    try:
        cursor = conn.cursor()
        
        # Verificar si el usuario ya existe
        cursor.execute("SELECT id FROM usuarios WHERE username = %s OR email = %s", (username, email))
        if cursor.fetchone():
            cursor.close()
            conn.close()
            return None, "El usuario o email ya existe"
        
        # Crear el usuario
        password_hash = hash_password(password)
        cursor.execute("""
            INSERT INTO usuarios (username, email, password_hash, nombre_completo, rol, activo)
            VALUES (%s, %s, %s, %s, %s, TRUE)
        """, (username, email, password_hash, nombre_completo or username, rol))
        
        user_id = cursor.lastrowid
        conn.commit()
        cursor.close()
        conn.close()
        
        return user_id, None
    except Error as e:
        conn.rollback()
        cursor.close()
        conn.close()
        return None, f"Error al crear usuario: {str(e)}"

def autenticar_usuario(username, password):
    """Autenticar un usuario y devolver sus datos"""
    conn = DatabaseConfig.get_connection()
    if not conn:
        return None, "Error de conexión a la base de datos"
    
    try:
        cursor = conn.cursor(dictionary=True)
        
        # Buscar usuario por username o email
        cursor.execute("""
            SELECT id, username, email, password_hash, nombre_completo, rol, activo
            FROM usuarios
            WHERE (username = %s OR email = %s) AND activo = TRUE
        """, (username, username))
        
        user = cursor.fetchone()
        cursor.close()
        conn.close()
        
        if not user:
            return None, "Usuario o contraseña incorrectos"
        
        # Verificar contraseña
        if not verify_password(password, user['password_hash']):
            return None, "Usuario o contraseña incorrectos"
        
        # Actualizar último acceso
        conn = DatabaseConfig.get_connection()
        cursor = conn.cursor()
        cursor.execute("""
            UPDATE usuarios SET ultimo_acceso = NOW() WHERE id = %s
        """, (user['id'],))
        conn.commit()
        cursor.close()
        conn.close()
        
        # Retornar datos del usuario sin la contraseña
        return {
            'id': user['id'],
            'username': user['username'],
            'email': user['email'],
            'nombre_completo': user['nombre_completo'],
            'rol': user['rol']
        }, None
        
    except Error as e:
        if 'conn' in locals():
            conn.close()
        return None, f"Error de autenticación: {str(e)}"

def crear_sesion(usuario_id, ip_address=None, user_agent=None, duracion_horas=24):
    """Crear una sesión para el usuario"""
    conn = DatabaseConfig.get_connection()
    if not conn:
        return None
    
    try:
        cursor = conn.cursor()
        
        # Generar token único
        session_token = str(uuid.uuid4())
        
        # Calcular fecha de expiración
        fecha_expiracion = datetime.now() + timedelta(hours=duracion_horas)
        
        # Crear sesión
        cursor.execute("""
            INSERT INTO sesiones (usuario_id, session_token, ip_address, user_agent, fecha_expiracion, activa)
            VALUES (%s, %s, %s, %s, %s, TRUE)
        """, (usuario_id, session_token, ip_address, user_agent, fecha_expiracion))
        
        conn.commit()
        session_id = cursor.lastrowid
        cursor.close()
        conn.close()
        
        return session_token
        
    except Error as e:
        if conn:
            conn.rollback()
            conn.close()
        return None

def verificar_sesion(session_token):
    """Verificar si una sesión es válida y devolver el usuario"""
    conn = DatabaseConfig.get_connection()
    if not conn:
        return None
    
    try:
        cursor = conn.cursor(dictionary=True)
        
        # Buscar sesión activa y no expirada
        cursor.execute("""
            SELECT s.usuario_id, u.username, u.email, u.nombre_completo, u.rol
            FROM sesiones s
            INNER JOIN usuarios u ON s.usuario_id = u.id
            WHERE s.session_token = %s 
            AND s.activa = TRUE 
            AND s.fecha_expiracion > NOW()
            AND u.activo = TRUE
        """, (session_token,))
        
        result = cursor.fetchone()
        cursor.close()
        conn.close()
        
        if result:
            return {
                'id': result['usuario_id'],
                'username': result['username'],
                'email': result['email'],
                'nombre_completo': result['nombre_completo'],
                'rol': result['rol']
            }
        
        return None
        
    except Error as e:
        if conn:
            conn.close()
        return None

def cerrar_sesion(session_token):
    """Cerrar una sesión"""
    conn = DatabaseConfig.get_connection()
    if not conn:
        return False
    
    try:
        cursor = conn.cursor()
        cursor.execute("""
            UPDATE sesiones SET activa = FALSE WHERE session_token = %s
        """, (session_token,))
        conn.commit()
        cursor.close()
        conn.close()
        return True
    except Error as e:
        if conn:
            conn.rollback()
            conn.close()
        return False

def cerrar_todas_sesiones(usuario_id):
    """Cerrar todas las sesiones de un usuario"""
    conn = DatabaseConfig.get_connection()
    if not conn:
        return False
    
    try:
        cursor = conn.cursor()
        cursor.execute("""
            UPDATE sesiones SET activa = FALSE WHERE usuario_id = %s
        """, (usuario_id,))
        conn.commit()
        cursor.close()
        conn.close()
        return True
    except Error as e:
        if conn:
            conn.rollback()
            conn.close()
        return False

def obtener_usuario_por_id(usuario_id):
    """Obtener datos de un usuario por su ID"""
    conn = DatabaseConfig.get_connection()
    if not conn:
        return None
    
    try:
        cursor = conn.cursor(dictionary=True)
        cursor.execute("""
            SELECT id, username, email, nombre_completo, rol, activo, fecha_registro, ultimo_acceso
            FROM usuarios
            WHERE id = %s
        """, (usuario_id,))
        
        user = cursor.fetchone()
        cursor.close()
        conn.close()
        return user
    except Error as e:
        if conn:
            conn.close()
        return None

def cambiar_contraseña(usuario_id, nueva_password):
    """Cambiar la contraseña de un usuario"""
    conn = DatabaseConfig.get_connection()
    if not conn:
        return False, "Error de conexión"
    
    try:
        cursor = conn.cursor()
        password_hash = hash_password(nueva_password)
        cursor.execute("""
            UPDATE usuarios SET password_hash = %s WHERE id = %s
        """, (password_hash, usuario_id))
        conn.commit()
        cursor.close()
        conn.close()
        return True, None
    except Error as e:
        if conn:
            conn.rollback()
            conn.close()
        return False, f"Error al cambiar contraseña: {str(e)}"
