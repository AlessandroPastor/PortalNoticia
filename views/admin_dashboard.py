# views/admin_dashboard.py - Dashboard de administración
import streamlit as st
import pandas as pd
from datetime import datetime
from db.admin import (
    obtener_todos_usuarios,
    obtener_usuario_por_id,
    actualizar_usuario,
    eliminar_usuario,
    obtener_estadisticas_usuarios,
    obtener_permisos_scraping_por_rol,
    obtener_todos_permisos,
    actualizar_permiso_scraping,
    obtener_fuentes_permitidas_por_rol,
    es_super_admin,
    tiene_permiso_admin
)

def mostrar_dashboard_admin():
    """Mostrar dashboard de administración"""
    
    # Verificar permisos
    usuario_actual = st.session_state.get('usuario')
    if not usuario_actual or not tiene_permiso_admin(usuario_actual.get('rol', '')):
        st.error("❌ No tienes permisos para acceder a esta sección")
        st.info("💡 Solo usuarios con rol 'admin' o 'super_admin' pueden acceder")
        return
    
    st.markdown("""
    <div style="
        background: linear-gradient(135deg, #3b82f6, #8b5cf6);
        padding: 2rem;
        border-radius: 15px;
        margin-bottom: 2rem;
        box-shadow: 0 8px 32px rgba(0, 0, 0, 0.3);
    ">
        <h1 style="color: white; margin: 0; text-align: center;">👑 Panel de Administración</h1>
        <p style="color: rgba(255,255,255,0.9); text-align: center; margin: 0.5rem 0 0 0;">
            Gestión de usuarios, roles y permisos de scraping
        </p>
    </div>
    """, unsafe_allow_html=True)
    
    # Tabs principales
    tab1, tab2, tab3 = st.tabs([
        "👥 Gestión de Usuarios",
        "🔐 Permisos de Scraping",
        "📊 Estadísticas"
    ])
    
    with tab1:
        mostrar_gestion_usuarios()
    
    with tab2:
        mostrar_gestion_permisos()
    
    with tab3:
        mostrar_estadisticas()

def mostrar_gestion_usuarios():
    """Mostrar gestión de usuarios"""
    st.markdown("### 👥 Gestión de Usuarios")
    
    # Estadísticas rápidas
    usuarios = obtener_todos_usuarios()
    stats = obtener_estadisticas_usuarios()
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("Total Usuarios", stats.get('total', 0))
    with col2:
        st.metric("Usuarios Activos", stats.get('activos', 0))
    with col3:
        st.metric("Inactivos", stats.get('inactivos', 0))
    with col4:
        st.metric("Registrados Hoy", stats.get('registrados_hoy', 0))
    
    st.markdown("---")
    
    if not usuarios:
        st.info("ℹ️ No hay usuarios registrados")
        return
    
    # Crear DataFrame para mostrar
    df_usuarios = pd.DataFrame(usuarios)
    
    # Formatear fechas
    if 'fecha_registro' in df_usuarios.columns:
        df_usuarios['fecha_registro'] = pd.to_datetime(df_usuarios['fecha_registro']).dt.strftime('%Y-%m-%d %H:%M')
    if 'ultimo_acceso' in df_usuarios.columns:
        df_usuarios['ultimo_acceso'] = df_usuarios['ultimo_acceso'].apply(
            lambda x: pd.to_datetime(x).strftime('%Y-%m-%d %H:%M') if x else 'Nunca'
        )
    
    # Mostrar tabla de usuarios
    st.markdown("### Lista de Usuarios")
    
    # Filtros
    col_filtro1, col_filtro2, col_filtro3 = st.columns(3)
    with col_filtro1:
        filtro_rol = st.selectbox(
            "Filtrar por rol:",
            ["Todos"] + list(df_usuarios['rol'].unique()),
            key="filtro_rol_admin"
        )
    with col_filtro2:
        filtro_activo = st.selectbox(
            "Filtrar por estado:",
            ["Todos", "Activos", "Inactivos"],
            key="filtro_activo_admin"
        )
    with col_filtro3:
        buscar_usuario = st.text_input("🔍 Buscar usuario:", key="buscar_usuario_admin")
    
    # Aplicar filtros
    df_filtrado = df_usuarios.copy()
    if filtro_rol != "Todos":
        df_filtrado = df_filtrado[df_filtrado['rol'] == filtro_rol]
    if filtro_activo == "Activos":
        df_filtrado = df_filtrado[df_filtrado['activo'] == True]
    elif filtro_activo == "Inactivos":
        df_filtrado = df_filtrado[df_filtrado['activo'] == False]
    if buscar_usuario:
        df_filtrado = df_filtrado[
            df_filtrado['username'].str.contains(buscar_usuario, case=False, na=False) |
            df_filtrado['email'].str.contains(buscar_usuario, case=False, na=False) |
            df_filtrado['nombre_completo'].str.contains(buscar_usuario, case=False, na=False)
        ]
    
    st.markdown(f"**Mostrando {len(df_filtrado)} de {len(df_usuarios)} usuarios**")
    
    # Mostrar tabla
    st.dataframe(
        df_filtrado[['id', 'username', 'email', 'nombre_completo', 'rol', 'activo', 'fecha_registro', 'ultimo_acceso']],
        use_container_width=True,
        height=400
    )
    
    st.markdown("---")
    
    # Editar usuario
    st.markdown("### ✏️ Editar Usuario")
    
    usuarios_select = {f"{u['username']} (ID: {u['id']})": u['id'] for u in usuarios}
    usuario_seleccionado_str = st.selectbox(
        "Seleccionar usuario a editar:",
        options=list(usuarios_select.keys()),
        key="select_usuario_editar"
    )
    
    if usuario_seleccionado_str:
        usuario_id = usuarios_select[usuario_seleccionado_str]
        usuario_data = obtener_usuario_por_id(usuario_id)
        
        if usuario_data:
            col_edit1, col_edit2 = st.columns(2)
            
            with col_edit1:
                nuevo_nombre = st.text_input(
                    "Nombre Completo:",
                    value=usuario_data.get('nombre_completo') or '',
                    key=f"edit_nombre_{usuario_id}"
                )
                nuevo_email = st.text_input(
                    "Email:",
                    value=usuario_data.get('email') or '',
                    key=f"edit_email_{usuario_id}"
                )
            
            with col_edit2:
                nuevo_rol = st.selectbox(
                    "Rol:",
                    options=['usuario', 'editor', 'admin', 'super_admin'],
                    index=['usuario', 'editor', 'admin', 'super_admin'].index(usuario_data.get('rol', 'usuario')),
                    key=f"edit_rol_{usuario_id}",
                    help="super_admin: Acceso completo\nadmin: Gestión de usuarios\neditor: Scraping avanzado\nusuario: Scraping básico"
                )
                nuevo_estado = st.selectbox(
                    "Estado:",
                    options=[True, False],
                    index=0 if usuario_data.get('activo') else 1,
                    format_func=lambda x: "✅ Activo" if x else "❌ Inactivo",
                    key=f"edit_activo_{usuario_id}"
                )
            
            col_btn1, col_btn2 = st.columns([3, 1])
            with col_btn1:
                if st.button("💾 Guardar Cambios", type="primary", key=f"btn_guardar_{usuario_id}"):
                    success, error = actualizar_usuario(
                        usuario_id=usuario_id,
                        nombre_completo=nuevo_nombre if nuevo_nombre else None,
                        email=nuevo_email if nuevo_email else None,
                        rol=nuevo_rol,
                        activo=nuevo_estado
                    )
                    
                    if success:
                        st.success("✅ Usuario actualizado correctamente")
                        st.rerun()
                    else:
                        st.error(f"❌ Error: {error}")
            
            with col_btn2:
                if st.button("🗑️ Desactivar", key=f"btn_desactivar_{usuario_id}"):
                    success, error = eliminar_usuario(usuario_id)
                    if success:
                        st.success("✅ Usuario desactivado")
                        st.rerun()
                    else:
                        st.error(f"❌ Error: {error}")

def mostrar_gestion_permisos():
    """Mostrar gestión de permisos de scraping"""
    st.markdown("### 🔐 Permisos de Scraping por Rol")
    
    st.info("💡 Define qué fuentes puede scrapear cada rol. Super Admin tiene acceso a todas las fuentes por defecto.")
    
    # Fuentes disponibles (del app.py)
    fuentes_disponibles = {
        "Diario Sin Fronteras": "https://diariosinfronteras.com.pe/",
        "El Peruano": "https://elperuano.pe/",
        "La República": "https://larepublica.pe/",
        "Andina": "https://andina.pe/",
        "Perú21": "https://peru21.pe/",
        "El Comercio": "https://elcomercio.pe/",
        "Gestión": "https://gestion.pe/",
        "Expreso": "https://expreso.com.pe/",
        "Correo": "https://diariocorreo.pe/",
        "Ojo": "https://ojo.pe/",
        "Publimetro": "https://publimetro.pe/",
        "Willax": "https://willax.pe/",
        "Exitosa Noticias": "https://exitosanoticias.pe/",
        "RPP Noticias": "https://rpp.pe/",
        "América Noticias": "https://americatv.com.pe/noticias/",
        "Panamericana": "https://panamericana.pe/",
        "Canal N": "https://canaln.pe/",
        "ATV Noticias": "https://www.atv.pe/noticias",
        "La Industria": "https://laindustria.pe/",
        "Diario Uno": "https://diariouno.pe/"
    }
    
    # Roles disponibles (excepto super_admin que tiene acceso total)
    roles_gestionables = ['admin', 'editor', 'usuario']
    
    rol_seleccionado = st.selectbox(
        "Seleccionar rol para gestionar permisos:",
        options=roles_gestionables,
        key="select_rol_permisos",
        help="Super Admin tiene acceso a todas las fuentes automáticamente"
    )
    
    st.markdown(f"### Permisos para rol: **{rol_seleccionado.upper()}**")
    
    # Obtener permisos actuales
    permisos_actuales = obtener_permisos_scraping_por_rol(rol_seleccionado)
    permisos_dict = {p['fuente_nombre']: p['permitido'] for p in permisos_actuales}
    
    # Mostrar permisos por columnas
    num_cols = 2
    cols = st.columns(num_cols)
    
    cambios = {}
    for idx, (fuente_nombre, fuente_url) in enumerate(fuentes_disponibles.items()):
        col_idx = idx % num_cols
        with cols[col_idx]:
            permitido_actual = permisos_dict.get(fuente_nombre, False)
            nuevo_valor = st.checkbox(
                fuente_nombre,
                value=permitido_actual,
                key=f"permiso_{rol_seleccionado}_{fuente_nombre}",
                help=fuente_url
            )
            cambios[fuente_nombre] = nuevo_valor
    
    st.markdown("---")
    
    col_btn1, col_btn2 = st.columns([3, 1])
    with col_btn1:
        if st.button("💾 Guardar Permisos", type="primary", key="btn_guardar_permisos"):
            cambios_realizados = 0
            errores = []
            
            for fuente_nombre, permitido in cambios.items():
                fuente_url = fuentes_disponibles[fuente_nombre]
                success, error = actualizar_permiso_scraping(
                    rol_seleccionado,
                    fuente_nombre,
                    fuente_url,
                    permitido
                )
                
                if success:
                    cambios_realizados += 1
                else:
                    errores.append(f"{fuente_nombre}: {error}")
            
            if errores:
                st.error(f"❌ Errores al guardar algunos permisos:\n" + "\n".join(errores))
            else:
                st.success(f"✅ {cambios_realizados} permisos actualizados correctamente")
                st.rerun()
    
    with col_btn2:
        if st.button("🔄 Resetear", key="btn_reset_permisos"):
            st.rerun()
    
    st.markdown("---")
    
    # Vista resumida de todos los permisos
    st.markdown("### 📋 Resumen de Permisos por Rol")
    
    todos_permisos = obtener_todos_permisos()
    
    for rol_permiso in roles_gestionables:
        with st.expander(f"📌 Rol: {rol_permiso.upper()}"):
            permisos_rol = todos_permisos.get(rol_permiso, [])
            permisos_activos = [p for p in permisos_rol if p['permitido']]
            
            if permisos_activos:
                st.markdown(f"**{len(permisos_activos)} fuentes permitidas:**")
                for permiso in permisos_activos:
                    st.markdown(f"  ✅ {permiso['fuente_nombre']}")
            else:
                st.markdown("⚠️ No tiene permisos de scraping")

def mostrar_estadisticas():
    """Mostrar estadísticas del sistema"""
    st.markdown("### 📊 Estadísticas del Sistema")
    
    stats = obtener_estadisticas_usuarios()
    
    # Estadísticas principales
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric(
            "Total Usuarios",
            stats.get('total', 0),
            delta=stats.get('registrados_hoy', 0),
            delta_color="normal"
        )
    
    with col2:
        st.metric("Usuarios Activos", stats.get('activos', 0))
    
    with col3:
        st.metric("Usuarios Inactivos", stats.get('inactivos', 0))
    
    with col4:
        st.metric("Registrados Hoy", stats.get('registrados_hoy', 0))
    
    st.markdown("---")
    
    # Distribución por roles
    st.markdown("### Distribución por Roles")
    
    por_rol = stats.get('por_rol', {})
    if por_rol:
        # Crear gráfico de barras simple
        df_roles = pd.DataFrame([
            {'Rol': rol, 'Cantidad': cantidad}
            for rol, cantidad in por_rol.items()
        ])
        
        st.bar_chart(df_roles.set_index('Rol'))
        
        # Tabla detallada
        st.dataframe(df_roles, use_container_width=True, hide_index=True)
    else:
        st.info("ℹ️ No hay datos de distribución por roles")
    
    st.markdown("---")
    
    # Información del sistema
    st.markdown("### ℹ️ Información del Sistema")
    
    usuario_actual = st.session_state.get('usuario', {})
    
    info_sistema = {
        "Usuario Actual": usuario_actual.get('username', 'N/A'),
        "Rol": usuario_actual.get('rol', 'N/A'),
        "Permisos": "Super Admin" if es_super_admin(usuario_actual.get('rol', '')) else "Administrador",
        "Total Usuarios": stats.get('total', 0),
        "Usuarios Activos": stats.get('activos', 0),
    }
    
    for clave, valor in info_sistema.items():
        st.markdown(f"**{clave}:** {valor}")

