# 🚀 Guía de Instalación - Pastor Noticias "Q Pasa"

## 📋 Pasos para hacer funcionar todo

### **Paso 1: Verificar e instalar dependencias**

Abre PowerShell o CMD en la carpeta del proyecto y ejecuta:

```powershell
# Activar el entorno virtual (si lo tienes)
.\venv\Scripts\Activate.ps1

# O si no tienes venv, instala directamente:
pip install -r requirements.txt
```

Si `mysql-connector-python` no está en requirements.txt, instálalo manualmente:

```powershell
pip install mysql-connector-python
```

### **Paso 2: Configurar MySQL/MariaDB**

1. **Asegúrate de tener MySQL o MariaDB instalado y ejecutándose**

2. **Verifica/ajusta la configuración en `config.py`**:

   - Abre `config.py`
   - Verifica las líneas 10-14:
     ```python
     HOST = "127.0.0.1"
     PORT = 3306
     USER = "root"
     PASSWORD = ""  # ⚠️ Cambia esto si tu MySQL tiene contraseña
     DATABASE = "pastor_noticias_db"
     ```

3. **Crea la base de datos y tablas**:

   ```powershell
   python config.py
   ```

   Esto creará:

   - ✅ La base de datos `pastor_noticias_db`
   - ✅ Todas las tablas necesarias (noticias, usuarios, sesiones, etc.)
   - ✅ El usuario administrador por defecto

### **Paso 3: Usuario administrador por defecto**

Después de ejecutar `config.py`, tendrás un usuario admin:

- **Usuario:** `admin`
- **Contraseña:** `admin123`
- **Email:** `admin@pastornoticias.com`
- **Rol:** `admin`

⚠️ **IMPORTANTE:** Cambia esta contraseña después del primer login por seguridad.

### **Paso 4: Ejecutar la aplicación**

```powershell
streamlit run app.py
```

O si prefieres usar el script de inicio:

```powershell
.\start_pastor_noticias.bat
```

### **Paso 5: Acceder a la aplicación**

1. Abre tu navegador en: `http://localhost:8501`
2. Verás la pantalla de login
3. Inicia sesión con:
   - Usuario: `admin`
   - Contraseña: `admin123`

### **Paso 6: Crear nuevos usuarios (opcional)**

Una vez dentro, puedes:

- Crear nuevos usuarios desde la pestaña "✨ Registrarse" del login
- O usar el usuario admin para crear más cuentas

---

## 🔧 Solución de Problemas

### **Error: "ModuleNotFoundError: No module named 'mysql.connector'"**

```powershell
pip install mysql-connector-python
```

### **Error: "Can't connect to MySQL server"**

1. Verifica que MySQL esté ejecutándose:

   - Windows: Busca "Services" → Busca "MySQL" → Inicia si está detenido
   - O ejecuta: `net start MySQL` en CMD como administrador

2. Verifica la contraseña en `config.py`

### **Error: "Access denied for user 'root'@'localhost'"**

- Verifica que el usuario y contraseña en `config.py` sean correctos
- Si no tienes contraseña, deja `PASSWORD = ""`
- Si tienes contraseña, ponla en `PASSWORD = "tu_contraseña"`

### **Error al crear tablas**

1. Asegúrate de tener permisos en MySQL
2. Ejecuta MySQL como administrador y crea la base de datos manualmente:
   ```sql
   CREATE DATABASE IF NOT EXISTS pastor_noticias_db CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
   ```
3. Luego ejecuta `python config.py` nuevamente

### **El login no funciona**

1. Verifica que las tablas se crearon correctamente:

   ```powershell
   python -c "from config import DatabaseConfig; DatabaseConfig.setup_tables()"
   ```

2. Verifica que el usuario admin existe:
   - Abre MySQL
   - Ejecuta: `USE pastor_noticias_db; SELECT * FROM usuarios;`

---

## 📁 Estructura de Archivos Necesaria

Asegúrate de tener esta estructura:

```
I UNIDAD/
├── app.py                    ✅ Archivo principal
├── config.py                 ✅ Configuración BD
├── db/
│   ├── __init__.py          ✅
│   ├── auth.py              ✅ Funciones de autenticación
│   └── mysql_io.py          ✅ Funciones MySQL
├── components/
│   ├── __init__.py          ✅
│   ├── login.py             ✅ Componente de login
│   ├── cards.py             ✅
│   ├── search.py            ✅
│   └── notifications.py     ✅
├── views/
│   ├── detail.py            ✅
│   ├── favorites.py         ✅
│   └── dashboard.py         ✅
└── requirements.txt         ✅ Dependencias
```

---

## 🎯 Comandos Rápidos de Resumen

```powershell
# 1. Instalar dependencias
pip install -r requirements.txt
pip install mysql-connector-python

# 2. Crear base de datos y tablas
python config.py

# 3. Ejecutar aplicación
streamlit run app.py

# 4. Acceder
# Abre: http://localhost:8501
# Usuario: admin
# Contraseña: admin123
```

---

## ✅ Verificación Final

Ejecuta este comando para verificar que todo esté bien:

```powershell
python -c "from db.auth import autenticar_usuario; u, e = autenticar_usuario('admin', 'admin123'); print('✅ Login OK' if u else f'❌ Error: {e}')"
```

Si ves "✅ Login OK", todo está funcionando correctamente.

---

## 📞 Soporte

Si tienes problemas:

1. Verifica que MySQL esté ejecutándose
2. Verifica que la configuración en `config.py` sea correcta
3. Revisa los logs en la consola de PowerShell
4. Asegúrate de tener todas las dependencias instaladas Pastor
