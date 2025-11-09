#!/bin/bash
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
