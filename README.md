# 🤖 Agente de IA Documental Profesional

**Sistema inteligente de gestión documental con capacidades avanzadas de IA**

Transforme sus documentos en conocimiento accionable con el poder de Claude Anthropic y Google AI.

---

## ✨ Características Principales

### 📄 Gestión Multi-Formato
- **PDF**: Extracción completa de texto, tablas e imágenes
- **Word (DOCX)**: Procesamiento de párrafos, tablas y metadatos
- **Excel (XLSX/CSV)**: Análisis de datos y estadísticas
- **Imágenes**: Soporte para PNG, JPG, JPEG, BMP, GIF, WEBP
- **Texto**: TXT, MD, JSON

### 🤖 IA Avanzada (Claude Anthropic)
- **Informes profesionales**: Genera informes completos con análisis detallado
- **Correos corporativos**: Redacta emails profesionales basados en documentos
- **Resúmenes inteligentes**: Síntesis automática de contenido
- **Traducciones**: Traducción multilingüe manteniendo el contexto
- **Análisis profundo**: Identifica patrones, tendencias e insights
- **Respuestas a preguntas**: Chat interactivo con tus documentos
- **Extracción de datos**: Obtén información específica automáticamente
- **Comparaciones**: Analiza diferencias entre documentos
- **Mejora de contenido**: Optimiza y perfecciona textos

### 📊 Visualizaciones Profesionales
- **Gráficos automáticos**: Barras, líneas, pastel, dispersión, histogramas
- **Dashboards completos**: Múltiples visualizaciones en un solo panel
- **Mapas de calor**: Análisis de correlaciones
- **Tablas visuales**: Representación profesional de datos
- **Infografías**: Resúmenes visuales atractivos

### 💬 Interfaz Intuitiva
- **Web moderna**: Interfaz Gradio responsive y elegante
- **Chat interactivo**: Conversación natural con documentos
- **Búsqueda inteligente**: Encuentra documentos por contenido, tags o descripción
- **Gestión completa**: Organiza, etiqueta y administra tu repositorio

---

## 🚀 Instalación Rápida

### Requisitos Previos

- **Python 3.8+**
- **API Keys**:
  - [Anthropic API Key](https://console.anthropic.com/) (Obligatoria)
  - [Google AI API Key](https://makersuite.google.com/app/apikey) (Opcional, para visualizaciones)

### Pasos de Instalación

1. **Clonar el repositorio**:
   ```bash
   git clone <repository-url>
   cd creador-apunts-IA
   ```

2. **Instalar dependencias**:
   ```bash
   pip install -r requirements.txt
   ```

3. **Configurar API Keys**:

   Crea un archivo `.env` en la raíz del proyecto:
   ```bash
   # API Keys
   ANTHROPIC_API_KEY=sk-ant-api03-tu-api-key-aqui
   GOOGLE_API_KEY=tu-google-api-key-aqui
   ```

4. **Lanzar la aplicación**:
   ```bash
   python app.py
   ```

5. **Abrir el navegador**:
   ```
   http://localhost:7860
   ```

---

## 📖 Guía de Uso

### 1. Subir Documentos

1. Ve a la pestaña **"📤 Subir Documentos"**
2. Selecciona tu archivo (PDF, Word, Excel, etc.)
3. Añade tags opcionales (ej: "ventas, 2024, trimestral")
4. Agrega una descripción
5. Haz clic en **"Subir Documento"**

El sistema procesará automáticamente el documento y lo añadirá al repositorio.

### 2. Ejecutar Tareas de IA

1. Ve a la pestaña **"🤖 Tareas de IA"**
2. Selecciona el tipo de tarea:
   - **Informe**: Genera un análisis completo
   - **Correo**: Redacta un email profesional
   - **Resumen**: Crea una síntesis concisa
   - **Traducción**: Traduce a otro idioma
   - **Análisis**: Análisis profundo de datos
   - Y más...
3. Añade instrucciones específicas (opcional)
4. Haz clic en **"Ejecutar Tarea"**

**Ejemplo**:
- Tarea: `traduccion`
- Instrucciones: `Traducir al inglés manteniendo el tono profesional`

### 3. Chat con Documentos

1. Ve a la pestaña **"💬 Chat Inteligente"**
2. Escribe tu pregunta sobre el documento
3. El agente responderá usando el contexto del documento

**Ejemplos de preguntas**:
- "¿Cuáles son los puntos clave del documento?"
- "Resume el capítulo 3"
- "¿Qué recomendaciones propone el informe?"
- "Extrae todas las fechas mencionadas"

### 4. Crear Visualizaciones

1. Sube un archivo **Excel** con datos
2. Ve a la pestaña **"📊 Visualizaciones"**
3. Selecciona el tipo de gráfico:
   - **Dashboard**: Vista completa con múltiples gráficos
   - **Auto**: Selección automática según los datos
   - **Bar/Line/Pie**: Gráficos específicos
   - **Heatmap**: Mapa de correlaciones
   - **Table**: Tabla visual profesional
4. Añade un título (opcional)
5. Haz clic en **"Generar Visualización"**

### 5. Buscar Documentos

1. Ve a la pestaña **"🔍 Buscar Documentos"**
2. Ingresa tu término de búsqueda
3. El sistema buscará en:
   - Nombres de archivos
   - Descripciones
   - Tags
   - Contenido de los documentos

---

## 🏗️ Arquitectura del Sistema

```
creador-apunts-IA/
├── app.py                          # Punto de entrada principal
├── .env                            # API Keys (crear manualmente)
├── requirements.txt                # Dependencias Python
├── README.md                       # Esta documentación
│
├── src/                            # Código fuente
│   ├── __init__.py
│   ├── document_manager.py         # Gestión de documentos y storage
│   ├── document_processor.py       # Procesamiento multi-formato
│   ├── ai_agent.py                 # Agente IA con Claude
│   ├── visualization_generator.py  # Generador de gráficos
│   ├── web_interface.py            # Interfaz web Gradio
│   │
│   └── [Módulos legacy]
│       ├── config.py
│       ├── main.py
│       ├── pdf_extractor.py
│       ├── note_generator.py
│       └── docx_formatter.py
│
├── document_storage/               # Repositorio de documentos
│   ├── metadata.json              # Base de datos de metadatos
│   ├── pdf/                       # Documentos PDF
│   ├── word/                      # Documentos Word
│   ├── excel/                     # Archivos Excel
│   ├── text/                      # Archivos de texto
│   └── image/                     # Imágenes
│
└── output/                        # Archivos generados
    ├── charts/                    # Gráficos
    ├── tables/                    # Tablas visuales
    ├── dashboards/                # Dashboards
    └── infographics/              # Infografías
```

---

## 🎯 Casos de Uso

### Para Estudiantes 🎓

1. **Resumen de PDFs académicos**:
   - Sube un paper o libro de texto
   - Genera resúmenes por capítulo
   - Crea notas de estudio Cornell (función legacy)

2. **Análisis de datos de investigación**:
   - Importa datos Excel de experimentos
   - Genera dashboards automáticos
   - Obtén análisis estadísticos con IA

3. **Traducción de bibliografía**:
   - Sube documentos en otros idiomas
   - Traduce automáticamente
   - Mantiene formato y referencias

### Para Empresas 💼

1. **Informes ejecutivos**:
   - Sube reportes largos
   - Genera resúmenes ejecutivos
   - Crea presentaciones visuales

2. **Análisis de datos de ventas**:
   - Importa Excel con datos de ventas
   - Genera gráficos y dashboards
   - Obtén insights automáticos con IA

3. **Redacción de correos**:
   - Sube documentos base (propuestas, informes)
   - Genera correos profesionales automáticamente
   - Personaliza con instrucciones específicas

4. **Gestión documental**:
   - Centraliza todos los documentos
   - Búsqueda inteligente de contenido
   - Organización con tags

---

## 🔧 Configuración Avanzada

### Modelos de IA

El sistema usa por defecto:
- **Claude Opus 4.5** (`claude-opus-4-5-20251101`) - Máxima calidad
- Puedes cambiar el modelo en `src/ai_agent.py`

Modelos disponibles:
- `claude-opus-4-5-20251101` (Recomendado)
- `claude-sonnet-4-5-20250929` (Más rápido)
- `claude-haiku-4-5-20250122` (Económico)

### Personalización de Visualizaciones

Edita `src/visualization_generator.py` para:
- Cambiar paletas de colores
- Ajustar tamaños de gráficos
- Modificar estilos de tablas

### Storage Personalizado

Por defecto, los documentos se guardan en `./document_storage/`

Para cambiar la ubicación, edita en `src/web_interface.py`:
```python
self.doc_manager = DocumentManager(storage_path="./tu/ruta/personalizada")
```

---

## 📊 Ejemplos de Prompts

### Informes
```
"Genera un informe ejecutivo destacando los KPIs principales y las recomendaciones estratégicas"
```

### Correos
```
"Redacta un correo formal para el equipo de ventas resumiendo los resultados del trimestre"
```

### Análisis
```
"Identifica las tendencias de crecimiento y los puntos de mejora en los datos"
```

### Traducciones
```
"Traducir al francés manteniendo el tono técnico y profesional"
```

---

## 🛠️ Solución de Problemas

### Error: "API Key no encontrada"
- Verifica que el archivo `.env` existe en la raíz
- Confirma que la variable `ANTHROPIC_API_KEY` está configurada
- Reinicia la aplicación

### Error al procesar PDF
- Asegúrate de que el PDF no esté protegido con contraseña
- Verifica que el PDF tiene texto seleccionable (no es escaneado)
- Prueba con un PDF más pequeño primero

### Visualizaciones no se generan
- Solo funcionan con archivos Excel/CSV
- Verifica que el archivo tiene datos numéricos
- Comprueba que `GOOGLE_API_KEY` está configurada (opcional)

### Interfaz web no carga
- Verifica que el puerto 7860 no esté en uso
- Prueba con otro puerto: modificar en `app.py`
- Comprueba los logs en la terminal

---

## 📦 Dependencias

```
# IA
anthropic>=0.18.0          # Claude API
google-generativeai>=0.3.0 # Gemini API

# Procesamiento de documentos
python-docx>=1.1.0         # Word
PyPDF2>=3.0.0              # PDF
pdfplumber>=0.10.0         # PDF avanzado
openpyxl>=3.1.0            # Excel
pandas>=2.0.0              # Datos

# Visualización
matplotlib>=3.7.0          # Gráficos
seaborn>=0.12.0            # Gráficos estadísticos
Pillow>=10.0.0             # Imágenes

# Web
gradio>=4.0.0              # Interfaz web

# Utilidades
python-dotenv>=1.0.0       # Variables de entorno
rich>=13.0.0               # Terminal UI
numpy>=1.24.0              # Cálculos numéricos
```

---

## 🔐 Seguridad

- **Nunca** compartas tu archivo `.env` o tus API keys
- El archivo `.env` está en `.gitignore` por defecto
- Las API keys se cargan de forma segura usando `python-dotenv`
- Los documentos se almacenan localmente en tu máquina

---

## 🚧 Roadmap

- [ ] Soporte para OCR en PDFs escaneados
- [ ] Exportación de resultados a PDF
- [ ] Integración con más modelos de IA
- [ ] API REST para integración con otros sistemas
- [ ] Modo colaborativo multi-usuario
- [ ] Análisis de sentimiento en documentos
- [ ] Generación de presentaciones PowerPoint

---

## 🤝 Contribuciones

Este proyecto fue desarrollado como herramienta profesional para gestión documental con IA.

Para reportar bugs o sugerir mejoras, contacta con el desarrollador.

---

## 📄 Licencia

Este proyecto se proporciona tal cual para uso educativo y profesional.

---

## 🙏 Agradecimientos

- **Anthropic** - Por Claude, el mejor modelo de lenguaje
- **Google** - Por Gemini y herramientas de IA
- **Gradio** - Por la fantástica interfaz web
- **Python Community** - Por todas las increíbles bibliotecas

---

## 📞 Soporte

Para preguntas o asistencia:

1. Revisa esta documentación completa
2. Consulta la [Documentación de Claude API](https://docs.anthropic.com/)
3. Verifica que todas las dependencias están instaladas correctamente

---

**Desarrollado con ❤️ usando Claude Opus 4.5**

*Ideal para estudiantes y empresas que buscan transformar sus documentos en conocimiento accionable.*

🚀 **¡Comienza ahora y potencia tu productividad con IA!**
