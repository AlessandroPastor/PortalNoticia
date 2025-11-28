# 📖 Manual de Usuario - Portal de Noticias Pastor

## 🚀 Acceso al Sistema

### Primer Inicio
1. **Ejecutar aplicación:** `streamlit run app.py`
2. **Credenciales iniciales:**
   - 👤 Usuario: `admin`
   - 🔑 Contraseña: `admin123`
   - 📧 Email: `admin@pastornoticias.com`

> ⚠️ **Cambia la contraseña después del primer acceso**

### Inicio de Sesión Regular
- Ingresa usuario y contraseña
- El sistema mantiene tu sesión activa
- Cierra sesión manualmente cuando termines

---

## 👥 Roles del Sistema

| Rol | Permisos | Acciones |
|-----|----------|----------|
| **Admin** | Control total | Gestión completa de usuarios y noticias |
| **Editor** | Edición limitada | Editar noticias, scraping básico |
| **Usuario** | Acceso básico | Ver noticias, gestionar favoritos |

---

## 🎯 Navegación Principal

### Menú Lateral
- **🏠 Inicio** - Noticias recientes
- **🔍 Buscar** - Búsqueda avanzada
- **⭐ Favoritos** - Tus noticias guardadas
- **📖 Lecturas** - Historial de lectura
- **⚙️ Admin** - Panel administrativo (solo admins)

### Tarjetas de Noticias
Cada noticia muestra:
- 🖼️ Imagen destacada
- 📰 Título y resumen
- 🏷️ Categoría y fecha
- ⭐ Botón para favoritos

---

## 🔍 Búsqueda de Noticias

### Búsqueda Básica
1. Click en **"Buscar"** en el menú
2. Escribe palabras clave
3. Resultados en tiempo real

### Filtros Disponibles
- **📅 Fecha:** 24h, 7 días, 30 días, Todo
- **🏷️ Categoría:** Política, Economía, Deportes, etc.
- **🔤 Orden:** Más reciente, Más antiguo

---

## 📰 Visualización de Noticias

### Vista Detallada
Al hacer click en una noticia:
- ✅ Contenido completo expandido
- ✅ Imágenes y multimedia
- ✅ Fuente original y fecha
- ✅ Botones de acción

### Acciones Disponibles
- **⭐ Favorito** - Guardar/eliminar de favoritos
- **🔗 Fuente** - Ver noticia original
- **← Volver** - Regresar al listado

---

## ❤️ Gestión de Favoritos

### Agregar Favoritos
1. Click en ⭐ en cualquier tarjeta
2. Ícono cambia a amarillo ✅
3. Se guarda automáticamente

### Ver Favoritos
1. Click en **"Favoritos"** en menú lateral
2. Lista completa de noticias guardadas
3. Click para leer contenido completo

### Eliminar Favoritos
- Click en ⭐ nuevamente (se desactiva)
- Se elimina de la lista automáticamente

---

## 📊 Panel de Administración

> 🔒 Solo para usuarios Admin

### Estadísticas
- 📈 Total de noticias
- 👥 Usuarios registrados
- 📊 Noticias activas/inactivas
- 📈 Actividad reciente

### Gestión de Noticias
- **📋 Listar** - Ver todas las noticias
- **✏️ Editar** - Modificar contenido
- **🚫 Desactivar** - Ocultar sin eliminar
- **🗑️ Eliminar** - Borrar permanentemente

### Gestión de Usuarios
- **👥 Crear usuario** - Agregar nuevos usuarios
- **⚙️ Editar permisos** - Cambiar roles
- **🔒 Activar/desactivar** - Control de acceso
- **🗑️ Eliminar usuario** - Remover del sistema

---

## 🔄 Scraping de Noticias

### Scraping Manual (Admins)
1. Ir a **Panel Admin → Scraping**
2. Seleccionar fuentes permitidas
3. Click en **"Ejecutar Scraping"**
4. Revisar resultados en logs

### Fuentes Disponibles
- **Básicas:** Diario Sin Fronteras, La República
- **Avanzadas:** El Peruano, Andina, Perú21, El Comercio

---

## 🎨 Personalización

### Modo Oscuro/Claro
- Click en **🌙/☀️** en barra superior
- Cambio instantáneo
- Preferencia guardada

### Cerrar Sesión
1. Click en nombre de usuario (barra superior)
2. Seleccionar **"Cerrar Sesión"**
3. Redirección automática a login

---

## ❓ Solución de Problemas

### Problemas Comunes
| Problema | Solución |
|----------|----------|
| **No puedo iniciar sesión** | Verificar credenciales, revisar estado de BD |
| **No veo noticias** | Ejecutar scraping manual, verificar noticias activas |
| **Error de conexión** | Verificar MySQL ejecutándose, revisar config.py |
| **Scraping falla** | Verificar URLs, permisos de fuente, revisar logs |

### Contacto de Soporte
- 📧 Email: admin@pastornoticias.com
- 📖 Documentación: Revisar README.md
- 🔧 Soporte técnico: Contactar administrador

---

## 💡 Consejos de Uso

### ✅ Mejores Prácticas
- Cambiar contraseña regularmente
- Ejecutar scraping en horarios de baja demanda
- Revisar logs periódicamente
- Mantener solo noticias relevantes activas

### ❌ Qué Evitar
- Múltiples scraping simultáneos
- Modificación directa de base de datos
- Permisos admin a usuarios no verificados
- Eliminación sin verificar dependencias

---

## 🎊 ¡Listo para Usar!

**¡Bienvenido al Portal de Noticias Pastor!** 🎉

- Explora las noticias más recientes
- Guarda tus favoritos para leer después
- Usa la búsqueda para encontrar temas específicos
- Disfruta de una experiencia personalizada

¿Necesitas ayuda? Contacta al administrador del sistema.
