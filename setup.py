# setup.py - Script de instalación y configuración inicial

import subprocess
import sys
import os
from pathlib import Path

def install_requirements():
    """Instalar dependencias desde requirements.txt"""
    print("📦 Instalando dependencias...")
    try:
        subprocess.check_call([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"])
        print("✅ Dependencias instaladas correctamente")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Error instalando dependencias: {e}")
        return False

def setup_database():
    """Configurar la base de datos"""
    print("🗄️ Configurando base de datos...")
    try:
        from config import DatabaseConfig
        if DatabaseConfig.setup_tables():
            print("✅ Base de datos configurada correctamente")
            return True
        else:
            print("❌ Error configurando base de datos")
            return False
    except Exception as e:
        print(f"❌ Error: {e}")
        print("Asegúrate de tener MySQL/MariaDB ejecutándose")
        return False

def create_env_file():
    """Crear archivo .env con configuraciones"""
    env_content = """# Pastor Noticias - Configuración
MYSQL_HOST=127.0.0.1
MYSQL_PORT=3306
MYSQL_USER=root
MYSQL_PASSWORD=
MYSQL_DATABASE=pastor_noticias_db

# URLs de scraping
DEFAULT_SCRAPING_URL=https://diariosinfronteras.com.pe/

# Configuraciones de scraping
SCRAPING_INTERVAL=120
MAX_NEWS_PER_SCRAPE=50
AUTO_SCRAPING=true

# Configuraciones de la app
DEBUG_MODE=false
DARK_MODE=false
"""
    
    if not os.path.exists('.env'):
        with open('.env', 'w') as f:
            f.write(env_content)
        print("✅ Archivo .env creado")
    else:
        print("ℹ️ Archivo .env ya existe")

def create_directories():
    """Crear directorios necesarios"""
    directories = [
        'logs',
        'data',
        'exports',
        'temp'
    ]
    
    for directory in directories:
        Path(directory).mkdir(exist_ok=True)
    
    print("✅ Directorios creados")

def create_systemd_service():
    """Crear archivo de servicio systemd (Linux)"""
    if sys.platform.startswith('linux'):
        service_content = f"""[Unit]
Description=Pastor Noticias Scraping Daemon
After=network.target mysql.service

[Service]
Type=simple
User=www-data
WorkingDirectory={os.getcwd()}
ExecStart={sys.executable} scraping_daemon.py
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
"""
        
        with open('pastor-noticias.service', 'w') as f:
            f.write(service_content)
        
        print("✅ Archivo de servicio systemd creado")
        print("Para instalarlo: sudo cp pastor-noticias.service /etc/systemd/system/")
        print("Para habilitarlo: sudo systemctl enable pastor-noticias")
        print("Para iniciarlo: sudo systemctl start pastor-noticias")

def create_startup_scripts():
    """Crear scripts de inicio"""
    
    # Script para Windows
    batch_content = """@echo off
echo Iniciando Pastor Noticias...
start "Scraping Daemon" python scraping_daemon.py
timeout /t 3
start "Streamlit App" streamlit run pastor_noticias.py --server.port 8501
echo Pastor Noticias iniciado correctamente
pause
"""
    
    with open('start_pastor_noticias.bat', 'w') as f:
        f.write(batch_content)
    
    # Script para Linux/Mac
    bash_content = """#!/bin/bash
echo "Iniciando Pastor Noticias..."

# Iniciar daemon de scraping en segundo plano
python3 scraping_daemon.py &
DAEMON_PID=$!
echo "Daemon de scraping iniciado (PID: $DAEMON_PID)"

# Esperar un momento
sleep 3

# Iniciar aplicación Streamlit
echo "Iniciando aplicación web..."
streamlit run pastor_noticias.py --server.port 8501

# Cleanup al salir
trap "kill $DAEMON_PID" EXIT
"""
    
    with open('start_pastor_noticias.sh', 'w') as f:
        f.write(bash_content)
    
    # Hacer ejecutable en Unix
    if not sys.platform.startswith('win'):
        os.chmod('start_pastor_noticias.sh', 0o755)
    
    print("✅ Scripts de inicio creados")

def main():
    """Función principal de configuración"""
    print("🚀 Pastor Noticias - Configuración Inicial")
    print("=" * 50)
    
    # Verificar Python
    if sys.version_info < (3, 8):
        print("❌ Se requiere Python 3.8 o superior")
        sys.exit(1)
    
    print(f"✅ Python {sys.version} detectado")
    
    # Paso 1: Instalar dependencias
    if not install_requirements():
        print("❌ Instalación fallida")
        sys.exit(1)
    
    print("-" * 50)
    
    # Paso 2: Crear directorios
    create_directories()
    
    # Paso 3: Crear archivo de configuración
    create_env_file()
    
    # Paso 4: Configurar base de datos
    print("\n🔧 Configurando base de datos...")
    print("Asegúrate de tener MySQL/MariaDB ejecutándose antes de continuar")
    input("Presiona Enter para continuar...")
    
    if not setup_database():
        print("⚠️ Error en configuración de BD. Puedes ejecutar 'python config.py' más tarde")
    
    print("-" * 50)
    
    # Paso 5: Crear scripts de inicio
    create_startup_scripts()
    
    # Paso 6: Crear servicio systemd si es Linux
    create_systemd_service()
    
    print("-" * 50)
    print("🎉 ¡Configuración completada!")
    print("\nPróximos pasos:")
    print("1. Configura tu base de datos MySQL si no está lista")
    print("2. Edita el archivo .env con tus configuraciones")
    print("3. Ejecuta: python scraping_daemon.py (en segundo plano)")
    print("4. Ejecuta: streamlit run pastor_noticias.py")
    print("5. O usa los scripts de inicio creados")
    print("\n📱 La aplicación estará disponible en: http://localhost:8501")

if __name__ == "__main__":
    main()