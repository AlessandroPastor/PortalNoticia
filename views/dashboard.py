import streamlit as st
import pandas as pd
import plotly.express as px

def mostrar_dashboard_analisis(df):
    """Dashboard de análisis con visualizaciones mejoradas"""
    st.markdown('<div class="section-title">📊 Dashboard de Análisis</div>', unsafe_allow_html=True)
    
    if df.empty:
        st.markdown("""
        <div class="empty-state">
            <div class="empty-state-icon">📊</div>
            <h3>No hay datos para analizar</h3>
            <p>Obtén algunas noticias para ver estadísticas detalladas</p>
        </div>
        """, unsafe_allow_html=True)
        return
    
    # KPIs principales
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.markdown(f"""
        <div class="stats-card">
            <div class="stats-number">{len(df)}</div>
            <div class="stats-label">Total Noticias</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        categorias_unicas = df['categoria'].nunique()
        st.markdown(f"""
        <div class="stats-card">
            <div class="stats-number">{categorias_unicas}</div>
            <div class="stats-label">Categorías</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        promedio_lecturas = sum(st.session_state.lecturas.values()) / len(df) if len(df) > 0 else 0
        st.markdown(f"""
        <div class="stats-card">
            <div class="stats-number">{promedio_lecturas:.1f}</div>
            <div class="stats-label">Promedio Lecturas</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col4:
        tasa_favoritos = (len(st.session_state.favoritos) / len(df)) * 100 if len(df) > 0 else 0
        st.markdown(f"""
        <div class="stats-card">
            <div class="stats-number">{tasa_favoritos:.1f}%</div>
            <div class="stats-label">Tasa Favoritos</div>
        </div>
        """, unsafe_allow_html=True)
    
    st.markdown("---")
    
    # Gráficos mejorados
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("#### 📊 Distribución por Categorías")
        cat_counts = df['categoria'].value_counts()
        fig_pie = px.pie(
            values=cat_counts.values,
            names=cat_counts.index,
            color_discrete_sequence=px.colors.qualitative.Set3,
            hole=0.4
        )
        fig_pie.update_layout(
            font=dict(family="Inter", size=12),
            showlegend=True,
            height=400
        )
        st.plotly_chart(fig_pie, use_container_width=True)
    
    with col2:
        st.markdown("#### 📅 Tendencia Temporal")
        try:
            df['fecha_clean'] = pd.to_datetime(df['fecha_scraping']).dt.date
            daily_counts = df['fecha_clean'].value_counts().sort_index()
            
            fig_line = px.line(
                x=daily_counts.index,
                y=daily_counts.values,
                title="",
                color_discrete_sequence=["#667eea"]
            )
            fig_line.update_layout(
                font=dict(family="Inter", size=12),
                xaxis_title="Fecha",
                yaxis_title="Número de Noticias",
                height=400
            )
            fig_line.update_traces(line_width=3)
            st.plotly_chart(fig_line, use_container_width=True)
        except:
            st.info("No se pudo generar el gráfico temporal")
    
    # Análisis de engagement
    st.markdown("---")
    st.markdown("#### 🎯 Análisis de Engagement")
    
    # Crear DataFrame con métricas de engagement
    engagement_data = []
    for _, noticia in df.iterrows():
        lecturas = st.session_state.lecturas.get(noticia['id'], 0)
        es_favorito = noticia['id'] in st.session_state.favoritos
        engagement_data.append({
            'titulo': noticia['titulo'][:40] + '...',
            'categoria': noticia['categoria'],
            'lecturas': lecturas,
            'favorito': 1 if es_favorito else 0
        })
    
    engagement_df = pd.DataFrame(engagement_data)
    
    if not engagement_df.empty:
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("##### Top 10 Más Leídas")
            top_leidas = engagement_df.nlargest(10, 'lecturas')[['titulo', 'lecturas']]
            if not top_leidas.empty:
                fig_bar = px.bar(
                    top_leidas,
                    x='lecturas',
                    y='titulo',
                    orientation='h',
                    color='lecturas',
                    color_continuous_scale='Blues'
                )
                fig_bar.update_layout(
                    font=dict(family="Inter", size=10),
                    height=400,
                    yaxis=dict(tickfont=dict(size=9)),
                    coloraxis_showscale=False
                )
                st.plotly_chart(fig_bar, use_container_width=True)
        
        with col2:
            st.markdown("##### Engagement por Categoría")
            cat_engagement = engagement_df.groupby('categoria').agg({
                'lecturas': 'sum',
                'favorito': 'sum'
            }).reset_index()
            
            if not cat_engagement.empty:
                fig_scatter = px.scatter(
                    cat_engagement,
                    x='lecturas',
                    y='favorito',
                    size='lecturas',
                    color='categoria',
                    hover_data=['categoria']
                )
                fig_scatter.update_layout(
                    font=dict(family="Inter", size=12),
                    height=400,
                    xaxis_title="Total Lecturas",
                    yaxis_title="Total Favoritos"
                )
                st.plotly_chart(fig_scatter, use_container_width=True)