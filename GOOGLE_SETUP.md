# 🔗 Configuración de Integraciones Google

Guía completa para habilitar Google Drive y Gmail en el Agente de IA Documental.

---

## 📋 Requisitos Previos

- Cuenta de Google
- Acceso a Google Cloud Console
- Python 3.8+ instalado

---

## 🚀 Configuración Paso a Paso

### 1. Crear Proyecto en Google Cloud

1. Ve a [Google Cloud Console](https://console.cloud.google.com/)
2. Crea un nuevo proyecto o selecciona uno existente
3. Anota el nombre del proyecto

### 2. Habilitar APIs Necesarias

1. En el menú lateral, ve a **"APIs y Servicios" > "Biblioteca"**
2. Busca y habilita las siguientes APIs:
   - **Google Drive API**
   - **Gmail API**

### 3. Crear Credenciales OAuth 2.0

1. Ve a **"APIs y Servicios" > "Credenciales"**
2. Haz clic en **"Crear credenciales"**
3. Selecciona **"ID de cliente de OAuth"**
4. Si es la primera vez, configura la pantalla de consentimiento OAuth:
   - Tipo: **Externo** (o Interno si es Google Workspace)
   - Nombre de la aplicación: **"Agente IA Documental"**
   - Email de asistencia: Tu email
   - Ámbitos: No añadas ninguno aquí (se configuran en el código)
   - Usuarios de prueba: Añade tu email
   - Guardar y continuar

5. Configurar el ID de cliente OAuth:
   - Tipo de aplicación: **"Aplicación de escritorio"**
   - Nombre: **"Agente IA Desktop"**
   - Crear

6. **Descargar el archivo JSON:**
   - Haz clic en el botón de descarga (icono de flecha hacia abajo)
   - Guarda el archivo como `google_credentials.json`

### 4. Colocar las Credenciales

1. Mueve el archivo `google_credentials.json` a la raíz del proyecto:
   ```bash
   mv ~/Descargas/client_secret_*.json /home/user/creador-apunts-IA/google_credentials.json
   ```

2. Verifica que el archivo esté en el lugar correcto:
   ```bash
   ls -la /home/user/creador-apunts-IA/google_credentials.json
   ```

### 5. Primer Uso - Autenticación OAuth

1. **Inicia la aplicación:**
   ```bash
   python app.py
   ```

2. **Abre el navegador en:** http://localhost:7860

3. **Ve a la pestaña "📁 Google Drive" o "✉️ Gmail"**

4. **Proceso de autenticación:**
   - Al intentar usar Google Drive o Gmail por primera vez, se abrirá automáticamente tu navegador
   - Selecciona tu cuenta de Google
   - Acepta los permisos solicitados:
     - Google Drive: Leer y escribir archivos
     - Gmail: Enviar correos
   - Serás redirigido a una página de confirmación

5. **Tokens guardados:**
   - Se crearán automáticamente dos archivos:
     - `google_token.json` (para Drive)
     - `gmail_token.json` (para Gmail)
   - Estos archivos NO se commitean (están en .gitignore)
   - Mantén estos archivos seguros

---

## ✨ Funcionalidades Disponibles

### 📁 Google Drive

Una vez configurado, podrás:

#### Listar Archivos
```
Pestaña: 📁 Google Drive
- Buscar archivos por nombre
- Ver todos tus archivos en Drive
- Obtener IDs de archivos
```

#### Importar Documentos
```
1. Copia el ID del archivo de la lista
2. Pégalo en "ID del archivo en Drive"
3. Añade tags y descripción (opcional)
4. Clic en "⬇️ Importar a Repositorio"

El documento se descargará y procesará automáticamente.
```

#### Exportar Documentos
```
1. Sube un documento al repositorio local
2. Ve a la pestaña Google Drive
3. (Opcional) Pega el ID de una carpeta destino
4. Clic en "⬆️ Exportar Documento Actual"

El documento se subirá a tu Google Drive.
```

### ✉️ Gmail

Una vez configurado, podrás:

#### Enviar Correos con IA
```
1. Sube un documento (PDF, Word, Excel, etc.)
2. Ve a la pestaña "✉️ Gmail"
3. Ingresa el email del destinatario
4. Selecciona el tipo de correo:
   - correo: Email profesional estándar
   - informe: Informe ejecutivo
   - resumen: Resumen conciso
5. Añade instrucciones (ej: "tono formal", "incluir datos clave")
6. Clic en "📧 Generar y Enviar"

La IA generará el correo y lo enviará automáticamente.
```

---

## 🛠️ Solución de Problemas

### Error: "No se encontró google_credentials.json"

**Solución:**
- Verifica que el archivo esté en la raíz del proyecto
- Asegúrate de que el nombre sea exactamente `google_credentials.json`
- Ejecuta: `ls -la google_credentials.json`

### Error: "Access blocked: This app's request is invalid"

**Solución:**
1. Ve a Google Cloud Console
2. "APIs y Servicios" > "Pantalla de consentimiento OAuth"
3. Añade tu email en "Usuarios de prueba"
4. Guarda los cambios
5. Intenta de nuevo

### Error: "Invalid grant" o token expirado

**Solución:**
```bash
# Eliminar tokens antiguos
rm google_token.json gmail_token.json

# Reiniciar la aplicación
python app.py

# Volver a autenticarse
```

### Google Drive/Gmail no aparece disponible

**Solución:**
1. Verifica que las APIs estén habilitadas en Google Cloud Console
2. Revisa que `google_credentials.json` exista
3. Mira los logs en la terminal al iniciar la app
4. Asegúrate de tener conexión a internet

### Error: "Forbidden" al intentar subir/descargar

**Solución:**
1. Revisa los permisos en Google Cloud Console
2. Asegúrate de que las APIs están habilitadas
3. Verifica que el token no haya expirado
4. Intenta eliminar los tokens y re-autenticar

---

## 🔐 Seguridad

### Archivos Sensibles

Los siguientes archivos contienen información sensible y **NO deben compartirse**:

- `google_credentials.json` - Credenciales OAuth
- `google_token.json` - Token de Drive
- `gmail_token.json` - Token de Gmail
- `.env` - API Keys

**Estos archivos ya están protegidos en `.gitignore`**

### Mejores Prácticas

1. **Nunca compartas las credenciales** en repositorios públicos
2. **Revoca el acceso** si las credenciales se comprometen:
   - Google Cloud Console > Credenciales > Eliminar ID de cliente
3. **Renueva los tokens** periódicamente eliminándolos y re-autenticando
4. **Usa usuarios de prueba** mientras desarrollas
5. **Publica la app** solo cuando esté lista para producción

---

## 📊 Límites de Uso

Google impone límites de cuota para sus APIs:

### Google Drive API
- **Consultas por día:** 1,000,000,000
- **Consultas por minuto por usuario:** 1,000

### Gmail API
- **Envíos diarios:** 500 (cuenta gratuita) / 2,000 (Google Workspace)
- **Destinatarios por mensaje:** 500

**Para uso normal, estos límites son más que suficientes.**

---

## 🆘 Soporte

Si tienes problemas:

1. Revisa esta guía completa
2. Verifica los logs en la terminal
3. Consulta la [documentación oficial de Google](https://developers.google.com/drive)
4. Revisa el estado en la pestaña "📈 Estadísticas" > "Estado de Google"

---

## 🎯 Próximos Pasos

Una vez configurado:

1. ✅ Prueba importar un documento desde Drive
2. ✅ Genera contenido con IA sobre ese documento
3. ✅ Envía un correo con el resultado via Gmail
4. ✅ Explora todas las capacidades del agente

---

**¡Disfruta de tu Agente de IA Documental con superpoderes de Google!** 🚀
