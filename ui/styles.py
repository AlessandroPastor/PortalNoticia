import streamlit as st
from pathlib import Path
import plotly.io as pio
import matplotlib.pyplot as plt

import streamlit as st
import os
from pathlib import Path

def load_css():
    """Cargar el CSS desde el archivo styles.css"""
    try:
        # Obtener la ruta del directorio actual
        current_dir = Path(__file__).parent
        css_file = current_dir / "styles.css"
        
        # Verificar si el archivo existe
        if css_file.exists():
            with open(css_file, "r", encoding="utf-8") as f:
                css_content = f.read()
            
            # Inyectar el CSS en Streamlit
            st.markdown(f"<style>{css_content}</style>", unsafe_allow_html=True)
        else:
            st.error(f"❌ Archivo CSS no encontrado: {css_file}")
            # Cargar CSS de respaldo
            _load_fallback_css()
            
    except Exception as e:
        st.error(f"❌ Error cargando CSS: {e}")
        _load_fallback_css()

def _load_fallback_css():
    """CSS de respaldo en caso de error"""
    fallback_css = """
    <style>
    .main-header {
        background: #1e293b;
        padding: 3rem 2rem;
        border-radius: 20px;
        text-align: center;
        margin: 2rem;
        border: 2px solid #3b82f6;
    }
    
    .main-header h1 {
        color: #3b82f6;
        font-size: 3rem;
        font-weight: bold;
    }
    
    .news-card {
        background: #334155;
        padding: 2rem;
        border-radius: 15px;
        margin-bottom: 1.5rem;
        border: 2px solid #475569;
    }
    </style>
    """
    st.markdown(fallback_css, unsafe_allow_html=True)


def aplicar_tema():
    """Aplica el tema claro/oscuro de manera integral con gráficos y CSS variables"""
    oscuro = st.session_state.get("dark_mode", False)
    
    # Configurar temas de gráficos
    if oscuro:
        pio.templates.default = "plotly_dark"
        plt.style.use("dark_background")
        _aplicar_css_oscuro()
    else:
        pio.templates.default = "plotly_white"
        plt.style.use("default")
        _aplicar_css_claro()

def _aplicar_css_oscuro():
    """Aplica variables CSS para modo oscuro"""
    css_oscuro = """
    <style>
    :root {
        /* Paleta de colores oscura - Vibrante y moderna */
        --background-primary: #0f172a;
        --background-secondary: #1e293b;
        --background-card: #334155;
        --background-elevated: #475569;
        
        --text-primary: #f8fafc;
        --text-secondary: #cbd5e1;
        --text-muted: #94a3b8;
        
        --accent-primary: #3b82f6;
        --accent-secondary: #8b5cf6;
        --accent-tertiary: #06b6d4;
        --accent-warning: #f59e0b;
        --accent-error: #ef4444;
        --accent-success: #10b981;
        
        --border-subtle: #475569;
        --border-medium: #64748b;
        --border-strong: #94a3b8;
        
        /* Sombras para modo oscuro */
        --shadow-sm: 0 2px 8px rgba(0, 0, 0, 0.4);
        --shadow-md: 0 4px 16px rgba(0, 0, 0, 0.5);
        --shadow-lg: 0 8px 32px rgba(0, 0, 0, 0.6);
        --shadow-xl: 0 16px 48px rgba(0, 0, 0, 0.7);
    }
    
    /* Ajustes específicos para Streamlit en modo oscuro */
    .stApp {
        background: linear-gradient(135deg, var(--background-primary) 0%, var(--background-secondary) 100%);
        color: var(--text-primary);
    }
    
    /* Mejora contraste en elementos de Streamlit */
    .stButton > button {
        background: var(--accent-primary);
        color: white;
        border: 2px solid var(--accent-primary);
    }
    
    .stButton > button:hover {
        background: #2563eb;
        border-color: #2563eb;
        transform: translateY(-2px);
    }
    
    /* Inputs y selects */
    .stTextInput > div > div > input,
    .stSelectbox > div > div,
    .stMultiselect > div > div {
        background: var(--background-card);
        color: var(--text-primary);
        border: 2px solid var(--border-medium);
    }
    
    /* Sidebar de Streamlit */
    section[data-testid="stSidebar"] {
        background: linear-gradient(135deg, var(--background-secondary) 0%, var(--background-primary) 100%);
    }
    
    /* Progress bars */
    .stProgress > div > div > div {
        background: linear-gradient(90deg, var(--accent-primary), var(--accent-secondary));
    }
    </style>
    """
    st.markdown(css_oscuro, unsafe_allow_html=True)

def _aplicar_css_claro():
    """Aplica variables CSS para modo claro con colores vibrantes"""
    css_claro = """
    <style>
    :root {
        /* Paleta de colores clara - Vibrante y energética */
        --background-primary: #f8fafc;
        --background-secondary: #ffffff;
        --background-card: #ffffff;
        --background-elevated: #f1f5f9;
        
        --text-primary: #0f172a;
        --text-secondary: #475569;
        --text-muted: #64748b;
        
        --accent-primary: #3b82f6;
        --accent-secondary: #8b5cf6;
        --accent-tertiary: #06b6d4;
        --accent-warning: #f59e0b;
        --accent-error: #ef4444;
        --accent-success: #10b981;
        
        --border-subtle: #e5e7eb;
        --border-medium: #d1d5db;
        --border-strong: #9ca3af;
        
        /* Sombras para modo claro */
        --shadow-sm: 0 2px 8px rgba(0, 0, 0, 0.1);
        --shadow-md: 0 4px 16px rgba(0, 0, 0, 0.15);
        --shadow-lg: 0 8px 32px rgba(0, 0, 0, 0.2);
        --shadow-xl: 0 16px 48px rgba(0, 0, 0, 0.25);
    }
    
    /* Ajustes específicos para Streamlit en modo claro */
    .stApp {
        background: linear-gradient(135deg, var(--background-primary) 0%, var(--background-secondary) 100%);
        color: var(--text-primary);
    }
    
    /* Header principal en modo claro */
    .main-header {
        background: linear-gradient(135deg, var(--background-secondary) 0%, var(--background-elevated) 100%) !important;
        border: 2px solid var(--accent-primary) !important;
        box-shadow: var(--shadow-lg) !important;
    }
    
    .main-header h1 {
        background: linear-gradient(135deg, var(--text-primary) 0%, var(--accent-primary) 100%) !important;
        -webkit-background-clip: text !important;
        -webkit-text-fill-color: transparent !important;
        background-clip: text !important;
    }
      
    /* Botones en modo claro */
    .stButton > button {
        background: var(--accent-primary);
        color: white;
        border: 2px solid var(--accent-primary);
        font-weight: 600;
    }
    
    .stButton > button:hover {
        background: #2563eb;
        border-color: #2563eb;
        transform: translateY(-2px);
        box-shadow: var(--shadow-md);
    }
    
    /* Sidebar sections en modo claro */
    .sidebar-section {
        background: linear-gradient(145deg, var(--background-card) 0%, var(--background-elevated) 100%) !important;
        border: 2px solid var(--border-medium) !important;
        box-shadow: var(--shadow-sm) !important;
    }
    
    /* Inputs y selects en modo claro */
    .stTextInput > div > div > input,
    .stSelectbox > div > div,
    .stMultiselect > div > div {
        background: var(--background-card);
        color: var(--text-primary);
        border: 2px solid var(--border-medium);
        border-radius: 8px;
    }
    
    .stTextInput > div > div > input:focus,
    .stSelectbox > div > div:focus,
    .stMultiselect > div > div:focus {
        border-color: var(--accent-primary);
        box-shadow: 0 0 0 2px rgba(59, 130, 246, 0.2);
    }
    
    /* Progress bars en modo claro */
    .stProgress > div > div > div {
        background: linear-gradient(90deg, var(--accent-primary), var(--accent-secondary));
    }
    
    /* Toggle switch styling */
    .stCheckbox > div > label {
        color: var(--text-primary) !important;
    }
    
    /* Mejoras de contraste para texto */
    .stMarkdown, .stText, .stTitle {
        color: var(--text-primary) !important;
    }
    </style>
    """
    st.markdown(css_claro, unsafe_allow_html=True)

def toggle_tema():
    """Función para cambiar el tema y rerenderizar"""
    st.session_state.dark_mode = not st.session_state.get("dark_mode", False)
    st.rerun()

def get_tema_actual():
    """Retorna el tema actual como string"""
    return "dark" if st.session_state.get("dark_mode", False) else "light"