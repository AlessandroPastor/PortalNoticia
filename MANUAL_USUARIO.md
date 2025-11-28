# Manual de Usuario - Portal de Noticias Pastor

## 📖 Guía de Uso del Sistema

### 1. Acceso al Sistema

#### Primer Inicio de Sesión
1. Ejecuta la aplicación con: `python app.py`
2. Accede con las credenciales por defecto:
   - **Usuario:** `admin`
   - **Contraseña:** `admin123`
3. **Importante:** Cambia la contraseña después del primer acceso

#### Inicio de Sesión Regular
- Ingresa tu usuario y contraseña en la pantalla de login
- El sistema recordará tu sesión hasta que cierres sesión manualmente

---

### 2. Roles y Permisos

El sistema cuenta con 4 niveles de usuarios:

| Rol | Permisos |
|-----|----------|
| **Super Admin** | Control total del sistema, gestión de usuarios, todas las fuentes de scraping |
| **Admin** | Gestión de noticias y usuarios, todas las fuentes de scraping |
| **Editor** | Edición de noticias, fuentes de scraping básicas y algunas avanzadas |
| **Usuario** | Lectura de noticias, favoritos, fuentes de scraping básicas |

---

### 3. Panel Principal (Dashboard)

#### Navegación
- **Inicio:** Vista principal con las últimas noticias
- **Buscar:** Busca noticias por título, categoría o contenido
- **Favoritos:** Noticias que has marcado como favoritas
- **Lecturas:** Historial de noticias que has leído
- **Admin:** Panel de administración (solo para admins)

#### Visualización de Noticias
Las noticias se muestran en tarjetas con:
- Imagen destacada
- Título
- Categoría
- Fecha de publicación
- Resumen del contenido

#### Acciones sobre Noticias
- **Click en tarjeta:** Ver detalle completo
- **⭐ Favorito:** Marcar/desmarcar como favorita
- **📖 Leer:** Acceder al contenido completo

---

### 4. Búsqueda de Noticias

1. Click en **"Buscar"** en el menú lateral
2. Escribe tu término de búsqueda
3. Filtra por:
   - **Categoría:** Todas, Política, Economía, Deportes, etc.
   - **Fecha:** Últimas 24h, 7 días, 30 días, Todo
4. Los resultados se actualizan automáticamente

---

### 5. Detalle de Noticia

Al hacer click en una noticia verás:
- **Título completo**
- **Imagen principal**
- **Fecha y categoría**
- **Contenido completo**
- **Enlace a la fuente original**

**Acciones disponibles:**
- ⭐ **Agregar/Quitar favoritos**
- 🔗 **Ver fuente original**
- ← **Volver al inicio**

---

### 6. Gestión de Favoritos

#### Agregar a Favoritos
1. Haz click en el ícono ⭐ en cualquier tarjeta de noticia
2. El ícono cambiará de color para confirmar

#### Ver Favoritos
1. Click en **"Favoritos"** en el menú lateral
2. Verás todas tus noticias favoritas
3. Click en cualquier tarjeta para leer el contenido

#### Eliminar de Favoritos
- Click en ⭐ nuevamente para desmarcar

---

### 7. Historial de Lecturas

El sistema registra automáticamente las noticias que lees:
1. Click en **"Lecturas"** en el menú lateral
2. Verás tu historial ordenado por fecha
3. Información incluye:
   - Noticias leídas
   - Fecha y hora de lectura
   - Tiempo de lectura

---

### 8. Panel de Administración

> **Nota:** Solo disponible para usuarios con rol Admin o Super Admin

#### Estadísticas Generales
- Total de noticias en el sistema
- Noticias activas
- Total de usuarios
- Actividad reciente

#### Gestión de Noticias
- **Ver todas:** Lista completa de noticias
- **Editar:** Modificar título, contenido, categoría
- **Activar/Desactivar:** Ocultar noticias sin eliminarlas
- **Eliminar:** Borrar permanentemente (requiere confirmación)

#### Gestión de Usuarios
- **Crear usuario:** Agregar nuevos usuarios al sistema
- **Editar usuario:** Modificar datos y permisos
- **Cambiar rol:** Asignar permisos (usuario, editor, admin, super admin)
- **Activar/Desactivar:** Bloquear acceso temporal
- **Eliminar:** Borrar usuario permanentemente

#### Scraping Manual
1. Selecciona una fuente de noticias permitida
2. Click en **"Ejecutar Scraping"**
3. Espera a que se complete el proceso
4. Revisa el log de resultados:
   - Noticias encontradas
   - Noticias nuevas agregadas
   - Errores (si los hay)

#### Configuración del Sistema
Ajusta parámetros como:
- Intervalo de scraping automático
- Máximo de noticias por sesión
- Modo debug
- URLs de scraping

---

### 9. Scraping Automático

El sistema puede obtener noticias automáticamente:

#### Configuración en el archivo `.env`
```env
AUTO_SCRAPING=true          # Activar scraping automático
SCRAPING_INTERVAL=120       # Intervalo en segundos (120 = 2 minutos)
MAX_NEWS_PER_SCRAPE=50     # Máximo de noticias por ejecución
```

#### Daemon de Scraping
Ejecuta en otra terminal:
```bash
python scraping_daemon.py
```

El daemon:
- Ejecuta scraping cada X segundos (según configuración)
- Registra logs de cada ejecución
- Evita duplicados automáticamente
- Funciona en segundo plano

---

### 10. Fuentes de Scraping Permitidas

Según tu rol, puedes scrapear diferentes fuentes:

#### Fuentes Básicas (Todos los usuarios)
- Diario Sin Fronteras
- La República

#### Fuentes Avanzadas (Editor y superiores)
- El Peruano
- Andina
- Perú21
- El Comercio

#### Agregar Nuevas Fuentes
Los Super Admin pueden agregar fuentes desde el panel de configuración.

---

### 11. Modo Oscuro/Claro

1. Click en el botón **🌙/☀️** en la barra superior
2. El tema se cambia automáticamente
3. La preferencia se guarda para futuras sesiones

---

### 12. Cerrar Sesión

1. Click en tu nombre de usuario en la barra superior
2. Selecciona **"Cerrar Sesión"**
3. Serás redirigido a la pantalla de login

---

### 13. Solución de Problemas Comunes

#### No puedo iniciar sesión
- Verifica que la base de datos esté funcionando
- Confirma que el usuario existe
- Intenta con las credenciales por defecto

#### No veo noticias
- Ejecuta scraping manual desde el panel de admin
- Verifica que haya noticias activas en la base de datos
- Revisa los logs de scraping

#### Error de conexión a la base de datos
- Verifica la configuración en `config.py`
- Confirma que MySQL esté corriendo en el puerto correcto
- Revisa las credenciales en `.env`

#### El scraping no encuentra noticias
- Verifica que la URL de la fuente sea correcta
- Confirma que tienes permisos para esa fuente
- Revisa los logs en la tabla `scraping_logs`

---

### 14. Atajos de Teclado

| Atajo | Acción |
|-------|--------|
| `Ctrl + F` | Abrir búsqueda |
| `Esc` | Cerrar vista de detalle |
| `Ctrl + D` | Ir al dashboard |
| `Ctrl + L` | Cerrar sesión |

---

### 15. Consejos de Uso

✅ **Buenas Prácticas:**
- Cambia la contraseña por defecto en el primer acceso
- Ejecuta scraping manual en horarios de baja actividad
- Revisa los logs de scraping regularmente
- Mantén activas solo las noticias relevantes
- Haz backup de la base de datos periódicamente

❌ **Evita:**
- Ejecutar múltiples scraping simultáneos
- Modificar directamente la base de datos sin el panel
- Dar permisos de admin a usuarios no confiables
- Eliminar noticias sin verificar dependencias

---

### 16. Contacto y Soporte

Para dudas o problemas:
- Revisa la documentación en `README.md`
- Consulta la guía de instalación en `GUIA_INSTALACION.md`
- Contacta al administrador del sistema

---

**¡Listo! Ahora estás preparado para usar el Portal de Noticias Pastor** 🎉
