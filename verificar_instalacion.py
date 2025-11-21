#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Script de verificación de instalación
Verifica que todo esté configurado correctamente para Pastor Noticias
"""

import sys
import os
from pathlib import Path

def verificar_python():
    """Verificar versión de Python"""
    print("🐍 Verificando Python...")
    if sys.version_info < (3, 8):
        print(f"   ❌ Python {sys.version_info.major}.{sys.version_info.minor} detectado")
        print("   ⚠️ Se requiere Python 3.8 o superior")
        return False
    print(f"   ✅ Python {sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}")
    return True

def verificar_dependencias():
    """Verificar dependencias instaladas"""
    print("\n📦 Verificando dependencias...")
    dependencias = [
        'streamlit',
        'pandas',
        'requests',
        'beautifulsoup4',
        'mysql.connector',
        'streamlit_autorefresh',
    ]
    
    faltantes = []
    for dep in dependencias:
        try:
            if dep == 'beautifulsoup4':
                __import__('bs4')
            elif dep == 'mysql.connector':
                __import__('mysql.connector')
            else:
                __import__(dep)
            print(f"   ✅ {dep}")
        except ImportError:
            print(f"   ❌ {dep} - NO INSTALADO")
            faltantes.append(dep)
    
    if faltantes:
        print(f"\n   ⚠️ Dependencias faltantes: {', '.join(faltantes)}")
        print("   💡 Ejecuta: pip install -r requirements.txt")
        return False
    return True

def verificar_archivos():
    """Verificar que existan los archivos necesarios"""
    print("\n📁 Verificando archivos...")
    archivos = [
        'app.py',
        'config.py',
        'db/__init__.py',
        'db/auth.py',
        'db/mysql_io.py',
        'components/__init__.py',
        'components/login.py',
        'requirements.txt',
    ]
    
    todos_ok = True
    for archivo in archivos:
        if Path(archivo).exists():
            print(f"   ✅ {archivo}")
        else:
            print(f"   ❌ {archivo} - NO ENCONTRADO")
            todos_ok = False
    
    return todos_ok

def verificar_mysql():
    """Verificar conexión a MySQL"""
    print("\n🗄️ Verificando MySQL...")
    try:
        from config import DatabaseConfig
        
        print(f"   📍 Host: {DatabaseConfig.HOST}")
        print(f"   📍 Puerto: {DatabaseConfig.PORT}")
        print(f"   📍 Usuario: {DatabaseConfig.USER}")
        print(f"   📍 Base de datos: {DatabaseConfig.DATABASE}")
        
        # Intentar conexión
        conn = DatabaseConfig.get_connection()
        if conn:
            print("   ✅ Conexión a MySQL exitosa")
            conn.close()
            return True
        else:
            print("   ❌ No se pudo conectar a MySQL")
            print("   💡 Verifica que MySQL esté ejecutándose")
            print("   💡 Verifica la configuración en config.py")
            return False
            
    except Exception as e:
        print(f"   ❌ Error: {e}")
        return False

def verificar_tablas():
    """Verificar que las tablas existan"""
    print("\n🗃️ Verificando tablas...")
    try:
        from config import DatabaseConfig
        import mysql.connector
        
        conn = DatabaseConfig.get_connection()
        if not conn:
            print("   ⚠️ No se pudo conectar para verificar tablas")
            return False
        
        cursor = conn.cursor()
        
        # Verificar tablas principales
        tablas_requeridas = [
            'SCRAP',
            'usuarios',
            'sesiones',
            'favoritos_usuario',
            'lecturas_usuario'
        ]
        
        cursor.execute("SHOW TABLES")
        tablas_existentes = [row[0] for row in cursor.fetchall()]
        
        todos_ok = True
        for tabla in tablas_requeridas:
            if tabla in tablas_existentes:
                print(f"   ✅ Tabla '{tabla}' existe")
            else:
                print(f"   ❌ Tabla '{tabla}' NO EXISTE")
                todos_ok = False
        
        cursor.close()
        conn.close()
        
        if not todos_ok:
            print("\n   💡 Ejecuta: python config.py para crear las tablas")
        
        return todos_ok
        
    except Exception as e:
        print(f"   ❌ Error verificando tablas: {e}")
        return False

def verificar_usuario_admin():
    """Verificar que exista el usuario admin"""
    print("\n👤 Verificando usuario administrador...")
    try:
        from db.auth import autenticar_usuario
        
        usuario, error = autenticar_usuario('admin', 'admin123')
        if usuario:
            print("   ✅ Usuario 'admin' existe y funciona")
            print(f"   📧 Email: {usuario.get('email', 'N/A')}")
            print(f"   👑 Rol: {usuario.get('rol', 'N/A')}")
            return True
        else:
            print(f"   ❌ Usuario admin no encontrado o error: {error}")
            print("   💡 Ejecuta: python config.py para crear el usuario admin")
            return False
            
    except Exception as e:
        print(f"   ❌ Error: {e}")
        return False

def main():
    """Función principal"""
    print("=" * 60)
    print("🔍 VERIFICACIÓN DE INSTALACIÓN - PASTOR NOTICIAS")
    print("=" * 60)
    
    resultados = {
        'Python': verificar_python(),
        'Dependencias': verificar_dependencias(),
        'Archivos': verificar_archivos(),
        'MySQL': verificar_mysql(),
        'Tablas': False,
        'Usuario Admin': False,
    }
    
    # Solo verificar tablas si MySQL funciona
    if resultados['MySQL']:
        resultados['Tablas'] = verificar_tablas()
        
        # Solo verificar usuario admin si las tablas existen
        if resultados['Tablas']:
            resultados['Usuario Admin'] = verificar_usuario_admin()
    
    # Resumen
    print("\n" + "=" * 60)
    print("📊 RESUMEN")
    print("=" * 60)
    
    for item, ok in resultados.items():
        status = "✅ OK" if ok else "❌ ERROR"
        print(f"{item:20s} {status}")
    
    # Resultado final
    todo_ok = all(resultados.values())
    
    print("\n" + "=" * 60)
    if todo_ok:
        print("🎉 ¡TODO ESTÁ CORRECTO! Puedes ejecutar la aplicación:")
        print("   streamlit run app.py")
        print("\n🔐 Credenciales de acceso:")
        print("   Usuario: admin")
        print("   Contraseña: admin123")
    else:
        print("⚠️ HAY PROBLEMAS QUE RESOLVER:")
        print("\nPasos recomendados:")
        print("1. Instala dependencias faltantes: pip install -r requirements.txt")
        print("2. Verifica que MySQL esté ejecutándose")
        print("3. Ejecuta: python config.py para crear tablas")
        print("4. Vuelve a ejecutar este script para verificar")
    print("=" * 60)
    
    return todo_ok

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)

