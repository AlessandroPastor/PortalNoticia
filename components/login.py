# components/login.py - Componentes de autenticación
import streamlit as st
from db.auth import (
    autenticar_usuario,
    crear_usuario,
    crear_sesion,
    verificar_sesion,
    cerrar_sesion
)

def mostrar_login():
    """Mostrar formulario de login"""
    st.markdown("""
    <style>
    .login-container {
        max-width: 450px;
        margin: 2rem auto;
        padding: 2rem;
        background: linear-gradient(135deg, #0f172a, #1e293b);
        border-radius: 20px;
        border: 2px solid #475569;
        box-shadow: 0 16px 48px rgba(0, 0, 0, 0.5);
    }
    .login-title {
        text-align: center;
        color: #f8fafc;
        font-size: 2.5rem;
        margin-bottom: 0.5rem;
    }
    .login-subtitle {
        text-align: center;
        color: #cbd5e1;
        margin-bottom: 2rem;
    }
    </style>
    """, unsafe_allow_html=True)
    
    st.markdown('<div class="login-container">', unsafe_allow_html=True)
    st.markdown('<h1 class="login-title">🔐</h1>', unsafe_allow_html=True)
    st.markdown('<h2 class="login-title">Q\' PASA</h2>', unsafe_allow_html=True)
    st.markdown('<p class="login-subtitle">Inicia sesión para continuar</p>', unsafe_allow_html=True)
    
    # Tabs para Login y Registro
    tab1, tab2 = st.tabs(["🔑 Iniciar Sesión", "✨ Registrarse"])
    
    with tab1:
        with st.form("login_form"):
            username = st.text_input(
                "Usuario o Email",
                placeholder="Ingresa tu usuario o email",
                key="login_username"
            )
            password = st.text_input(
                "Contraseña",
                type="password",
                placeholder="Ingresa tu contraseña",
                key="login_password"
            )
            
            col1, col2 = st.columns([2, 1])
            with col1:
                login_submit = st.form_submit_button(
                    "🚀 Iniciar Sesión",
                    type="primary",
                    use_container_width=True
                )
            with col2:
                if st.form_submit_button("🔓 Olvidé mi contraseña", use_container_width=True):
                    st.info("💡 Contacta al administrador para recuperar tu contraseña")
            
            if login_submit:
                if not username or not password:
                    st.error("⚠️ Por favor completa todos los campos")
                else:
                    with st.spinner("⏳ Autenticando..."):
                        usuario, error = autenticar_usuario(username, password)
                        
                        if usuario:
                            # Crear sesión
                            session_token = crear_sesion(
                                usuario_id=usuario['id'],
                                duracion_horas=24
                            )
                            
                            if session_token:
                                # Guardar en session state
                                st.session_state['autenticado'] = True
                                st.session_state['usuario'] = usuario
                                st.session_state['session_token'] = session_token
                                
                                st.success(f"✅ ¡Bienvenido, {usuario['nombre_completo'] or usuario['username']}!")
                                st.balloons()
                                st.rerun()
                            else:
                                st.error("❌ Error al crear la sesión. Intenta nuevamente.")
                        else:
                            st.error(f"❌ {error}")
    
    with tab2:
        with st.form("register_form"):
            st.markdown("### Crear nueva cuenta")
            
            new_username = st.text_input(
                "Usuario *",
                placeholder="Elija un nombre de usuario",
                key="reg_username"
            )
            new_email = st.text_input(
                "Email *",
                placeholder="tu@email.com",
                key="reg_email"
            )
            new_nombre = st.text_input(
                "Nombre Completo",
                placeholder="Opcional",
                key="reg_nombre"
            )
            new_password = st.text_input(
                "Contraseña *",
                type="password",
                placeholder="Mínimo 6 caracteres",
                key="reg_password"
            )
            new_password_confirm = st.text_input(
                "Confirmar Contraseña *",
                type="password",
                placeholder="Repite la contraseña",
                key="reg_password_confirm"
            )
            
            register_submit = st.form_submit_button(
                "✨ Crear Cuenta",
                type="primary",
                use_container_width=True
            )
            
            if register_submit:
                # Validaciones
                if not new_username or not new_email or not new_password:
                    st.error("⚠️ Por favor completa los campos obligatorios (*)")
                elif len(new_password) < 6:
                    st.error("⚠️ La contraseña debe tener al menos 6 caracteres")
                elif new_password != new_password_confirm:
                    st.error("⚠️ Las contraseñas no coinciden")
                elif "@" not in new_email:
                    st.error("⚠️ Ingresa un email válido")
                else:
                    with st.spinner("⏳ Creando cuenta..."):
                        user_id, error = crear_usuario(
                            username=new_username,
                            email=new_email,
                            password=new_password,
                            nombre_completo=new_nombre if new_nombre else None,
                            rol='usuario'
                        )
                        
                        if user_id:
                            st.success("✅ ¡Cuenta creada exitosamente! Ahora puedes iniciar sesión.")
                            st.info("💡 Usa la pestaña 'Iniciar Sesión' para acceder")
                        else:
                            st.error(f"❌ {error}")
    
    st.markdown('</div>', unsafe_allow_html=True)

def mostrar_header_usuario():
    """Mostrar header con información del usuario logueado"""
    if st.session_state.get('autenticado') and st.session_state.get('usuario'):
        usuario = st.session_state['usuario']
        
        col1, col2, col3 = st.columns([4, 1, 1])
        
        with col1:
            nombre_display = usuario.get('nombre_completo') or usuario.get('username', 'Usuario')
            rol_badge = {
                'admin': '👑',
                'editor': '✏️',
                'usuario': '👤'
            }.get(usuario.get('rol', 'usuario'), '👤')
            
            st.markdown(f"""
            <div style="
                background: linear-gradient(135deg, #3b82f6, #8b5cf6);
                padding: 0.75rem 1rem;
                border-radius: 10px;
                color: white;
                font-weight: bold;
                box-shadow: 0 4px 16px rgba(0, 0, 0, 0.3);
            ">
                {rol_badge} {nombre_display} <small>({usuario.get('username', '')})</small>
            </div>
            """, unsafe_allow_html=True)
        
        with col2:
            if st.button("👤 Perfil", use_container_width=True, key="btn_perfil"):
                st.session_state['mostrar_perfil'] = True
                st.rerun()
        
        with col3:
            if st.button("🚪 Salir", use_container_width=True, key="btn_logout"):
                # Cerrar sesión
                if st.session_state.get('session_token'):
                    cerrar_sesion(st.session_state['session_token'])
                
                # Limpiar session state
                st.session_state['autenticado'] = False
                st.session_state['usuario'] = None
                st.session_state['session_token'] = None
                st.session_state['mostrar_perfil'] = False
                
                st.success("✅ Sesión cerrada correctamente")
                st.rerun()

def verificar_autenticacion():
    """Verificar si el usuario está autenticado"""
    # Verificar session state
    if st.session_state.get('autenticado') and st.session_state.get('session_token'):
        session_token = st.session_state['session_token']
        
        # Verificar sesión en BD
        usuario = verificar_sesion(session_token)
        
        if usuario:
            # Actualizar session state si hay cambios
            st.session_state['usuario'] = usuario
            return True
        else:
            # Sesión inválida, limpiar
            st.session_state['autenticado'] = False
            st.session_state['usuario'] = None
            st.session_state['session_token'] = None
            return False
    
    return False

def requerir_autenticacion():
    """Decorador/concepto: requiere autenticación para acceder"""
    if not verificar_autenticacion():
        mostrar_login()
        st.stop()
    return True

def mostrar_perfil():
    """Mostrar perfil del usuario"""
    if not st.session_state.get('autenticado'):
        return
    
    usuario = st.session_state.get('usuario')
    if not usuario:
        return
    
    st.markdown("### 👤 Perfil de Usuario")
    
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.markdown(f"""
        <div style="
            background: linear-gradient(135deg, #0f172a, #1e293b);
            padding: 2rem;
            border-radius: 15px;
            border: 2px solid #475569;
        ">
            <h3 style="color: #f8fafc; margin-bottom: 1rem;">📋 Información Personal</h3>
            <p style="color: #cbd5e1;"><strong>Usuario:</strong> {usuario.get('username', 'N/A')}</p>
            <p style="color: #cbd5e1;"><strong>Email:</strong> {usuario.get('email', 'N/A')}</p>
            <p style="color: #cbd5e1;"><strong>Nombre:</strong> {usuario.get('nombre_completo', 'No especificado')}</p>
            <p style="color: #cbd5e1;"><strong>Rol:</strong> {usuario.get('rol', 'usuario').upper()}</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        if st.button("← Volver", use_container_width=True, key="btn_volver_perfil"):
            st.session_state['mostrar_perfil'] = False
            st.rerun()
    
    st.markdown("---")
    
    # Cambiar contraseña
    with st.expander("🔒 Cambiar Contraseña"):
        with st.form("cambiar_password_form"):
            old_password = st.text_input("Contraseña Actual", type="password", key="old_pass")
            new_password = st.text_input("Nueva Contraseña", type="password", key="new_pass")
            confirm_password = st.text_input("Confirmar Nueva Contraseña", type="password", key="confirm_pass")
            
            if st.form_submit_button("🔄 Cambiar Contraseña", type="primary"):
                if not old_password or not new_password or not confirm_password:
                    st.error("⚠️ Completa todos los campos")
                elif len(new_password) < 6:
                    st.error("⚠️ La nueva contraseña debe tener al menos 6 caracteres")
                elif new_password != confirm_password:
                    st.error("⚠️ Las contraseñas no coinciden")
                else:
                    # Verificar contraseña actual
                    from db.auth import autenticar_usuario, cambiar_contraseña
                    
                    user_check, error = autenticar_usuario(usuario['username'], old_password)
                    if user_check:
                        success, error_msg = cambiar_contraseña(usuario['id'], new_password)
                        if success:
                            st.success("✅ Contraseña actualizada correctamente")
                        else:
                            st.error(f"❌ {error_msg}")
                    else:
                        st.error("❌ Contraseña actual incorrecta")
