import streamlit as st
from pathlib import Path
import plotly.io as pio
import matplotlib.pyplot as pl

def load_css():
    css_path = Path(__file__).parent / "styles.css"
    if css_path.exists():
        with open(css_path, encoding="utf-8") as f:
            st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)



def aplicar_tema():
    """Activa modo claro/oscuro con transición suave y temas consistentes para gráficos."""
    oscuro = st.session_state.get("dark_mode", False)

    # Configurar temas de gráficos según el modo
    if oscuro:
        pio.templates.default = "plotly_dark"
        try:
            plt.style.use("dark_background")
        except Exception:
            pass
    else:
        pio.templates.default = "plotly_white"
        try:
            plt.style.use("seaborn-v0_8-whitegrid")  # Más limpio que 'default'
        except Exception:
            try:
                plt.style.use("default")
            except Exception:
                pass
    
    # CSS unificado con modo oscuro/claro
    st.markdown(f"""
    <style>
      /* ============ TRANSICIÓN SUAVE ============ */
      .stApp, .news-card, .sidebar-section, .stats-card, .main-header {{
        transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
      }}
      
      /* ============ MODO {'OSCURO' if oscuro else 'CLARO'} ============ */
      .stApp {{
        /* Variables de color */
        --primary-black: {'#0a0a0f' if oscuro else '#f8fafc'};
        --rich-black:    {'#13131a' if oscuro else '#ffffff'};
        --charcoal:      {'#1a1a24' if oscuro else '#f1f5f9'};
        --dark-gray:     {'#2a2a38' if oscuro else '#e5e7eb'};
        --medium-gray:   {'#3a3a4a' if oscuro else '#d1d5db'};
        --light-gray:    {'#4a4a5c' if oscuro else '#9ca3af'};
        --silver:        {'#6a6a7e' if oscuro else '#64748b'};
        --platinum:      {'#8a8a9e' if oscuro else '#334155'};
        --white:         {'#e8e8f0' if oscuro else '#0f172a'};
        --off-white:     {'#f8f8fc' if oscuro else '#111827'};
        
        /* Acentos vibrantes (sin cambios) */
        --neon-blue:       #00a3ff;
        --electric-purple: #7c3aed;
        --cyber-green:     #10b981;
        --hot-pink:        #db2777;
        --golden-yellow:   #d97706;
        --fire-orange:     #f97316;
        
        /* Sombras adaptativas */
        --shadow-glow: {'0 0 20px rgba(0, 163, 255, 0.3)' if oscuro else '0 0 20px rgba(0, 163, 255, 0.15)'};
        --shadow-deep: {'0 12px 24px -8px rgba(0,0,0,0.7)' if oscuro else '0 12px 24px -8px rgba(0,0,0,0.15)'};
        --shadow-neon: {'0 0 12px rgba(0, 163, 255, 0.5), 0 0 24px rgba(124, 58, 237, 0.3)' if oscuro else '0 0 12px rgba(0, 163, 255, 0.25), 0 0 24px rgba(124, 58, 237, 0.15)'};
        --shadow-cyber: {'0 0 18px rgba(16, 185, 129, 0.4)' if oscuro else '0 0 18px rgba(16, 185, 129, 0.2)'};
        --shadow-fire: {'0 0 16px rgba(249, 115, 22, 0.4)' if oscuro else '0 0 16px rgba(249, 115, 22, 0.2)'};
      }}
      
      /* ============ FONDOS BASE ============ */
      html, body, .stApp {{
        background: {'linear-gradient(135deg, var(--primary-black) 0%, var(--rich-black) 100%)' if oscuro else 'linear-gradient(135deg, #f8fafc 0%, #eef2f7 100%)'} !important;
        color: var(--{'white' if oscuro else 'off-white'}) !important;
      }}
      
      /* ============ COMPONENTES ============ */
      .news-card, .sidebar-section, .stats-card {{
        background: {'linear-gradient(135deg, var(--charcoal) 0%, rgba(26, 26, 36, 0.95) 100%)' if oscuro else 'linear-gradient(135deg, rgba(255,255,255,0.95) 0%, rgba(248, 250, 252, 0.9) 100%)'} !important;
        border: 1px solid var(--dark-gray) !important;
        box-shadow: var(--shadow-deep) !important;
      }}
      
      .news-title {{
        color: var(--{'white' if oscuro else 'off-white'}) !important;
      }}
      
      .news-content {{
        color: var(--{'platinum' if oscuro else 'platinum'}) !important;
      }}
      
      .sidebar-title {{
        -webkit-text-fill-color: {'transparent' if oscuro else 'initial'} !important;
        color: var(--{'white' if oscuro else 'off-white'}) !important;
        {'background: linear-gradient(135deg, var(--neon-blue), var(--electric-purple)); -webkit-background-clip: text;' if oscuro else ''}
      }}
      
      /* ============ HEADER ============ */
      .main-header {{
        background: {'linear-gradient(135deg, var(--charcoal) 0%, var(--rich-black) 100%)' if oscuro else 'linear-gradient(135deg, #ffffff 0%, #f3f6fb 100%)'} !important;
        border: 1px solid var(--dark-gray) !important;
        box-shadow: var(--shadow-deep) !important;
      }}
      
      /* ============ SCROLLBAR ============ */
      ::-webkit-scrollbar {{
        width: 10px;
        height: 10px;
      }}
      
      ::-webkit-scrollbar-track {{
        background: {'var(--primary-black)' if oscuro else '#eef2f7'};
      }}
      
      ::-webkit-scrollbar-thumb {{
        background: {'linear-gradient(180deg, var(--neon-blue), var(--electric-purple))' if oscuro else 'linear-gradient(180deg, #00a3ff, #7c3aed)'};
        border-radius: 10px;
        border: 2px solid {'var(--primary-black)' if oscuro else '#eef2f7'};
        box-shadow: {'inset 0 0 6px rgba(0, 163, 255, 0.5)' if oscuro else 'inset 0 0 6px rgba(0, 163, 255, 0.25)'};
      }}
      
      ::-webkit-scrollbar-thumb:hover {{
        background: {'linear-gradient(180deg, var(--electric-purple), var(--hot-pink))' if oscuro else 'linear-gradient(180deg, #7c3aed, #db2777)'};
      }}
      
      /* ============ ELEMENTOS DE STREAMLIT ============ */
      .stSelectbox label, .stMultiSelect label, .stSlider label {{
        color: var(--{'white' if oscuro else 'off-white'}) !important;
      }}
      
      /* Input backgrounds */
      .stSelectbox > div > div, .stMultiSelect > div > div {{
        background-color: {'var(--charcoal)' if oscuro else '#ffffff'} !important;
        color: var(--{'white' if oscuro else 'off-white'}) !important;
        border-color: var(--dark-gray) !important;
      }}
      
      /* Botones */
      .stButton > button {{
        background: linear-gradient(135deg, var(--neon-blue), var(--electric-purple)) !important;
        color: white !important;
        border: none !important;
        box-shadow: var(--shadow-neon) !important;
        transition: all 0.3s ease !important;
      }}
      
      .stButton > button:hover {{
        box-shadow: 0 0 20px rgba(0, 163, 255, 0.6), 0 0 40px rgba(124, 58, 237, 0.4) !important;
        transform: translateY(-2px) !important;
      }}
    </style>
    """, unsafe_allow_html=True)
    oscuro = st.session_state.get("dark_mode", False)

    if oscuro:
        # Oscuro = tu CSS ya lo maneja. Solo aseguro gráficos oscuros.
        pio.templates.default = "plotly_dark"
        try:
            plt.style.use("dark_background")
        except Exception:
            pass
        # Opcional: sutil refuerzo del fondo para la app (no pisa tu CSS, solo acompaña)
        st.markdown("""
        <style>
          .stApp { background: var(--primary-black) !important; }
        </style>
        """, unsafe_allow_html=True)
    else:
        # Claro = override de variables + fondos; no tocamos tu archivo, solo sobreescribimos aquí.
        st.markdown("""
        <style>
          /* Variables en modo CLARO, mismas llaves que definen el look pero invertidas */
          .stApp {
            --primary-black: #f8fafc;       /* base clara */
            --rich-black:   #ffffff;
            --charcoal:     #f1f5f9;        /* cards claras */
            --dark-gray:    #e5e7eb;        /* bordes claros */
            --medium-gray:  #d1d5db;
            --light-gray:   #9ca3af;
            --silver:       #64748b;
            --platinum:     #334155;
            --white:        #0f172a;        /* texto oscuro */
            --off-white:    #111827;

            /* mantengo tus acentos vibrantes */
            --neon-blue:       #00a3ff;
            --electric-purple: #7c3aed;
            --cyber-green:     #10b981;
            --hot-pink:        #db2777;
            --golden-yellow:   #d97706;
            --fire-orange:     #f97316;

            /* sombras suavizadas para claro */
            --shadow-glow: 0 0 20px rgba(0, 163, 255, 0.15);
            --shadow-deep: 0 12px 24px -8px rgba(0,0,0,0.15);
            --shadow-neon: 0 0 12px rgba(0, 163, 255, 0.25), 0 0 24px rgba(124, 58, 237, 0.15);
            --shadow-cyber: 0 0 18px rgba(16, 185, 129, 0.2);
            --shadow-fire: 0 0 16px rgba(249, 115, 22, 0.2);
          }

          /* Fondo claro para body y contenedor principal */
          html, body, .stApp {
            background: linear-gradient(135deg, #f8fafc 0%, #eef2f7 100%) !important;
            color: var(--off-white) !important;
          }

          /* Cartas y sidebar en claro aprovechando tu misma maqueta */
          .news-card, .sidebar-section, .stats-card {
            background: linear-gradient(135deg, rgba(255,255,255,0.95) 0%, rgba(248, 250, 252, 0.9) 100%) !important;
            border: 1px solid var(--dark-gray) !important;
            box-shadow: var(--shadow-deep) !important;
          }

          .news-title { color: var(--off-white) !important; }
          .news-content { color: var(--platinum) !important; }
          .sidebar-title { -webkit-text-fill-color: initial !important; color: var(--off-white) !important; }

          /* Header claro manteniendo efectos */
          .main-header {
            background: linear-gradient(135deg, #ffffff 0%, #f3f6fb 100%) !important;
            border: 1px solid var(--dark-gray) !important;
            box-shadow: var(--shadow-deep) !important;
          }

          /* Scrollbar claro */
          ::-webkit-scrollbar-track { background: #eef2f7; }
          ::-webkit-scrollbar-thumb {
            border: 2px solid #eef2f7;
            box-shadow: inset 0 0 6px rgba(0, 163, 255, 0.25);
          }
        </style>
        """, unsafe_allow_html=True)

        # Plotly y Matplotlib claros
        pio.templates.default = "plotly"
        try:
            plt.style.use("default")
        except Exception:
            pass

