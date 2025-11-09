@echo off
echo Iniciando Pastor Noticias...
start "Scraping Daemon" python scraping_daemon.py
timeout /t 3
start "Streamlit App" streamlit run pastor_noticias.py --server.port 8501
echo Pastor Noticias iniciado correctamente
pause
