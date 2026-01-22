"""
Web Interface - Interfaz web profesional para el Agente de IA Documental
Powered by Gradio - Interfaz moderna e intuitiva
"""

import os
import gradio as gr
from pathlib import Path
from typing import Optional, List, Tuple
import pandas as pd
from datetime import datetime
import sys
import os

# Asegurar que src está en el path
if os.path.dirname(__file__) not in sys.path:
    sys.path.insert(0, os.path.dirname(__file__))

from document_manager import DocumentManager
from document_processor import DocumentProcessor
from ai_agent import AIAgent
from visualization_generator import VisualizationGenerator
from google_integration import GoogleIntegration

from rich.console import Console

console = Console()


class DocumentAIWebInterface:
    """
    Interfaz web completa para el sistema de IA documental
    """

    def __init__(self):
        """Inicializa todos los componentes del sistema"""
        console.print("[cyan]🚀 Inicializando Agente de IA Documental...[/cyan]\n")

        # Inicializar componentes
        self.doc_manager = DocumentManager()
        self.doc_processor = DocumentProcessor()
        self.ai_agent = AIAgent()
        self.viz_generator = VisualizationGenerator()

        # Inicializar integraciones de Google
        try:
            self.google = GoogleIntegration()
        except Exception as e:
            console.print(f"[yellow]⚠ Integraciones de Google en modo limitado: {str(e)}[/yellow]")
            self.google = None

        # Estado de sesión
        self.current_doc_id = None
        self.current_doc_content = None

        console.print("[green]✓ Sistema inicializado correctamente[/green]\n")

    def upload_document(self, file, tags_str: str = "", description: str = "") -> Tuple[str, str]:
        """
        Sube un documento al repositorio

        Args:
            file: Archivo subido
            tags_str: Tags separados por comas
            description: Descripción del documento

        Returns:
            Mensaje de estado y tabla de documentos
        """
        if file is None:
            return "⚠️ Por favor, selecciona un archivo", self._get_documents_table()

        try:
            # Procesar tags
            tags = [tag.strip() for tag in tags_str.split(",") if tag.strip()]

            # Añadir documento
            doc_id = self.doc_manager.add_document(
                file.name,
                tags=tags,
                description=description
            )

            # Procesar contenido
            doc_type = self.doc_manager.get_document(doc_id)["type"]
            processed = self.doc_processor.process_document(file.name, doc_type)

            # Guardar ID actual
            self.current_doc_id = doc_id
            self.current_doc_content = self.doc_processor.extract_text_content(processed)

            message = f"✅ **Documento subido exitosamente**\n\n"
            message += f"📄 **ID:** {doc_id}\n"
            message += f"📁 **Tipo:** {doc_type}\n"
            message += f"📊 **Preview:** {processed.get('metadata', {})}\n\n"
            message += f"*Puedes hacer preguntas o solicitar tareas sobre este documento ahora.*"

            return message, self._get_documents_table()

        except Exception as e:
            return f"❌ **Error:** {str(e)}", self._get_documents_table()

    def _get_documents_table(self) -> str:
        """Genera una tabla HTML con todos los documentos"""
        docs = self.doc_manager.list_documents()

        if not docs:
            return "*No hay documentos en el repositorio*"

        # Crear tabla HTML
        html = "<table style='width:100%; border-collapse: collapse;'>"
        html += "<tr style='background-color: #4472C4; color: white;'>"
        html += "<th style='padding: 10px; border: 1px solid #ddd;'>Archivo</th>"
        html += "<th style='padding: 10px; border: 1px solid #ddd;'>Tipo</th>"
        html += "<th style='padding: 10px; border: 1px solid #ddd;'>Tamaño</th>"
        html += "<th style='padding: 10px; border: 1px solid #ddd;'>Tags</th>"
        html += "<th style='padding: 10px; border: 1px solid #ddd;'>Fecha</th>"
        html += "</tr>"

        for i, doc in enumerate(docs):
            bg_color = "#E7E6E6" if i % 2 == 0 else "#FFFFFF"
            html += f"<tr style='background-color: {bg_color};'>"
            html += f"<td style='padding: 8px; border: 1px solid #ddd;'>{doc['filename']}</td>"
            html += f"<td style='padding: 8px; border: 1px solid #ddd;'>{doc['type']}</td>"
            html += f"<td style='padding: 8px; border: 1px solid #ddd;'>{doc['size'] / 1024:.1f} KB</td>"
            html += f"<td style='padding: 8px; border: 1px solid #ddd;'>{', '.join(doc.get('tags', []))}</td>"
            html += f"<td style='padding: 8px; border: 1px solid #ddd;'>{doc['uploaded_at'][:10]}</td>"
            html += "</tr>"

        html += "</table>"
        return html

    def execute_ai_task(self, task_type: str, instructions: str = "") -> str:
        """
        Ejecuta una tarea de IA sobre el documento actual

        Args:
            task_type: Tipo de tarea
            instructions: Instrucciones adicionales

        Returns:
            Resultado de la tarea
        """
        if not self.current_doc_content:
            return "⚠️ **Primero debes subir un documento**"

        try:
            result = self.ai_agent.execute_task(
                task_type=task_type,
                content=self.current_doc_content,
                user_instructions=instructions
            )

            if result["success"]:
                output = f"# ✅ {task_type.upper()} - Completado\n\n"
                output += result["result"]
                output += f"\n\n---\n*Tokens usados: {result['usage']['input_tokens']} entrada / {result['usage']['output_tokens']} salida*"
                return output
            else:
                return f"❌ **Error:** {result.get('error', 'Error desconocido')}"

        except Exception as e:
            return f"❌ **Error ejecutando tarea:** {str(e)}"

    def search_documents(self, query: str) -> str:
        """Busca documentos en el repositorio"""
        if not query:
            return "⚠️ Ingresa un término de búsqueda"

        results = self.doc_manager.search_documents(query)

        if not results:
            return f"🔍 No se encontraron documentos para: **{query}**"

        output = f"# 🔍 Resultados de búsqueda: {query}\n\n"
        output += f"**{len(results)} documento(s) encontrado(s)**\n\n"

        for doc in results:
            output += f"---\n\n"
            output += f"### 📄 {doc['filename']}\n"
            output += f"- **ID:** {doc['id']}\n"
            output += f"- **Tipo:** {doc['type']}\n"
            output += f"- **Descripción:** {doc.get('description', 'N/A')}\n"
            output += f"- **Tags:** {', '.join(doc.get('tags', []))}\n"
            output += f"- **Preview:** {doc.get('content_preview', '')[:200]}...\n\n"

        return output

    def chat_with_document(self, message: str, history: List) -> Tuple[str, List]:
        """
        Chat interactivo con el documento

        Args:
            message: Mensaje del usuario
            history: Historial de chat

        Returns:
            Respuesta y historial actualizado
        """
        if not self.current_doc_content:
            return "⚠️ Primero debes subir un documento", history

        try:
            # Convertir historial de Gradio a formato de la API
            conversation = []
            for user_msg, assistant_msg in history:
                conversation.append({"role": "user", "content": user_msg})
                if assistant_msg:
                    conversation.append({"role": "assistant", "content": assistant_msg})

            # Añadir mensaje actual
            conversation.append({"role": "user", "content": message})

            # Obtener respuesta
            result = self.ai_agent.chat(self.current_doc_content, conversation)

            if result["success"]:
                response = result["response"]
                history.append((message, response))
                return "", history
            else:
                return f"❌ Error: {result.get('error')}", history

        except Exception as e:
            return f"❌ Error en chat: {str(e)}", history

    def generate_visualization(self, viz_type: str, title: str = "") -> Tuple[Optional[str], str]:
        """
        Genera visualización del documento actual

        Args:
            viz_type: Tipo de visualización
            title: Título

        Returns:
            Ruta de imagen y mensaje
        """
        if not self.current_doc_id:
            return None, "⚠️ Primero debes subir un documento"

        try:
            # Obtener documento
            doc = self.doc_manager.get_document(self.current_doc_id)
            doc_type = doc["type"]

            # Solo soportar Excel para visualizaciones de datos
            if doc_type != "excel":
                return None, f"⚠️ Las visualizaciones solo están disponibles para archivos Excel. Tipo actual: {doc_type}"

            # Procesar documento
            processed = self.doc_processor.process_document(doc["path"], doc_type)

            if "sheets" not in processed or not processed["sheets"]:
                return None, "⚠️ No se encontraron datos en el archivo Excel"

            # Obtener primera hoja
            sheet = processed["sheets"][0]
            df = pd.DataFrame(sheet["data"])

            # Generar visualización
            if viz_type == "dashboard":
                img_path = self.viz_generator.create_dashboard(df, title or doc["filename"])
            elif viz_type == "table":
                img_path = self.viz_generator.create_table_image(df.head(20), title or doc["filename"])
            else:
                img_path = self.viz_generator.generate_chart_from_data(df, viz_type, title or doc["filename"])

            return img_path, f"✅ Visualización '{viz_type}' generada exitosamente"

        except Exception as e:
            return None, f"❌ Error generando visualización: {str(e)}"

    def get_storage_stats(self) -> str:
        """Obtiene estadísticas del repositorio"""
        stats = self.doc_manager.get_storage_stats()

        output = "# 📊 Estadísticas del Repositorio\n\n"
        output += f"- **Total de documentos:** {stats['total_documents']}\n"
        output += f"- **Espacio usado:** {stats['total_size_mb']} MB\n"
        output += f"- **Ubicación:** `{stats['storage_path']}`\n\n"
        output += "### Por tipo:\n"
        for doc_type, count in stats['by_type'].items():
            output += f"- **{doc_type}:** {count} documento(s)\n"

        return output

    def list_drive_files(self, search_query: str = "") -> str:
        """Lista archivos en Google Drive"""
        if not self.google or not self.google.is_drive_available():
            return "⚠️ **Google Drive no está disponible**\n\n" + \
                   "Para usar Google Drive:\n" + \
                   "1. Descarga las credenciales OAuth desde Google Cloud Console\n" + \
                   "2. Guárdalas como `google_credentials.json` en la raíz del proyecto\n" + \
                   "3. Reinicia la aplicación"

        try:
            files = self.google.drive.list_files(query=search_query)

            if not files:
                return "📂 **No se encontraron archivos en Google Drive**"

            output = f"# 📂 Archivos en Google Drive\n\n"
            output += f"**{len(files)} archivo(s) encontrado(s)**\n\n"

            for file in files:
                output += f"---\n\n"
                output += f"### 📄 {file['name']}\n"
                output += f"- **ID:** `{file['id']}`\n"
                output += f"- **Tipo:** {file.get('mimeType', 'N/A')}\n"
                output += f"- **Tamaño:** {int(file.get('size', 0)) / 1024:.1f} KB\n"
                output += f"- **Modificado:** {file.get('modifiedTime', 'N/A')[:10]}\n\n"

            return output

        except Exception as e:
            return f"❌ **Error:** {str(e)}"

    def import_from_drive(self, file_id: str, tags_str: str = "", description: str = "") -> str:
        """Importa un archivo desde Google Drive al repositorio local"""
        if not self.google or not self.google.is_drive_available():
            return "⚠️ Google Drive no está disponible"

        try:
            # Descargar archivo temporalmente
            temp_path = f"./temp_drive_download_{file_id}"
            success = self.google.drive.download_file(file_id, temp_path)

            if not success:
                return "❌ Error descargando archivo de Drive"

            # Importar al repositorio
            tags = [tag.strip() for tag in tags_str.split(",") if tag.strip()]
            doc_id = self.doc_manager.add_document(
                temp_path,
                tags=tags,
                description=description or f"Importado desde Google Drive ({file_id})"
            )

            # Procesar contenido
            doc_type = self.doc_manager.get_document(doc_id)["type"]
            processed = self.doc_processor.process_document(temp_path, doc_type)

            # Guardar ID actual
            self.current_doc_id = doc_id
            self.current_doc_content = self.doc_processor.extract_text_content(processed)

            # Limpiar archivo temporal
            import os
            if os.path.exists(temp_path):
                os.remove(temp_path)

            message = f"✅ **Archivo importado desde Drive**\n\n"
            message += f"📄 **ID:** {doc_id}\n"
            message += f"📁 **Tipo:** {doc_type}\n\n"
            message += f"*El documento está listo para usar con las tareas de IA.*"

            return message

        except Exception as e:
            return f"❌ **Error:** {str(e)}"

    def export_to_drive(self, folder_id: str = "") -> str:
        """Exporta el documento actual a Google Drive"""
        if not self.google or not self.google.is_drive_available():
            return "⚠️ Google Drive no está disponible"

        if not self.current_doc_id:
            return "⚠️ Primero debes seleccionar un documento"

        try:
            doc = self.doc_manager.get_document(self.current_doc_id)
            file_id = self.google.drive.upload_file(
                doc["path"],
                folder_id=folder_id if folder_id else None
            )

            if file_id:
                return f"✅ **Documento exportado a Google Drive**\n\n**ID:** `{file_id}`"
            else:
                return "❌ Error exportando a Drive"

        except Exception as e:
            return f"❌ **Error:** {str(e)}"

    def send_email_with_ai(self, to: str, task_type: str = "correo", instructions: str = "") -> str:
        """Genera un correo con IA y lo envía via Gmail"""
        if not self.google or not self.google.is_gmail_available():
            return "⚠️ **Gmail no está disponible**\n\n" + \
                   "Para usar Gmail:\n" + \
                   "1. Descarga las credenciales OAuth desde Google Cloud Console\n" + \
                   "2. Guárdalas como `google_credentials.json` en la raíz del proyecto\n" + \
                   "3. Habilita Gmail API en tu proyecto de Google Cloud\n" + \
                   "4. Reinicia la aplicación"

        if not self.current_doc_content:
            return "⚠️ Primero debes subir un documento"

        if not to or '@' not in to:
            return "⚠️ Ingresa un email válido"

        try:
            # Generar contenido del correo con IA
            result = self.ai_agent.execute_task(
                task_type=task_type,
                content=self.current_doc_content,
                user_instructions=instructions or "Crear un correo profesional"
            )

            if not result["success"]:
                return f"❌ Error generando correo: {result.get('error')}"

            email_content = result["result"]

            # Enviar correo
            success = self.google.gmail.send_email_with_ai_content(to, email_content)

            if success:
                return f"✅ **Correo enviado exitosamente a:** {to}\n\n### Vista previa:\n\n{email_content[:500]}..."
            else:
                return "❌ Error enviando correo"

        except Exception as e:
            return f"❌ **Error:** {str(e)}"

    def get_google_status(self) -> str:
        """Obtiene el estado de las integraciones de Google"""
        if not self.google:
            return "⚠️ **Integraciones de Google no disponibles**"

        status = self.google.get_status()

        output = "# 🔗 Estado de Integraciones Google\n\n"

        # Drive
        if status["drive"]:
            output += "✅ **Google Drive:** Conectado\n"
        else:
            output += "❌ **Google Drive:** No disponible\n"

        # Gmail
        if status["gmail"]:
            output += "✅ **Gmail:** Conectado\n"
        else:
            output += "❌ **Gmail:** No disponible\n"

        output += "\n### Configuración\n\n"
        output += "Para habilitar estas integraciones:\n"
        output += "1. Ve a [Google Cloud Console](https://console.cloud.google.com/)\n"
        output += "2. Crea un proyecto y habilita Drive API y Gmail API\n"
        output += "3. Descarga las credenciales OAuth 2.0\n"
        output += "4. Guárdalas como `google_credentials.json` en la raíz del proyecto\n"
        output += "5. Reinicia la aplicación\n"

        return output

    def create_gradio_interface(self) -> gr.Blocks:
        """Crea la interfaz Gradio completa"""

        interface = gr.Blocks(title="Agente de IA Documental Profesional")

        with interface:
            gr.Markdown("""
            # 🤖 Agente de IA Documental Profesional
            ### Powered by Claude Anthropic & Google AI

            Sistema inteligente de gestión documental con capacidades avanzadas de IA para:
            - 📄 Gestión de documentos multi-formato (PDF, Word, Excel, imágenes, etc.)
            - 🤖 Generación de informes, correos, resúmenes y traducciones
            - 📊 Visualización de datos y creación de gráficos
            - 💬 Chat interactivo con tus documentos
            - 🔍 Búsqueda y análisis inteligente
            - 📁 **NUEVO:** Integración con Google Drive
            - ✉️ **NUEVO:** Envío de correos vía Gmail con IA

            **Ideal para estudiantes y empresas** ✨
            """)

            with gr.Tabs():

                # TAB 1: Subir documentos
                with gr.Tab("📤 Subir Documentos"):
                    gr.Markdown("### Sube tus documentos al repositorio")

                    with gr.Row():
                        with gr.Column(scale=2):
                            file_input = gr.File(
                                label="Selecciona un archivo",
                                file_types=[
                                    ".pdf", ".docx", ".doc",
                                    ".xlsx", ".xls", ".csv",
                                    ".txt", ".md", ".json",
                                    ".png", ".jpg", ".jpeg"
                                ]
                            )
                            tags_input = gr.Textbox(
                                label="Tags (separados por comas)",
                                placeholder="Ej: informe, ventas, 2024"
                            )
                            description_input = gr.Textbox(
                                label="Descripción",
                                placeholder="Descripción breve del documento",
                                lines=3
                            )
                            upload_btn = gr.Button("📤 Subir Documento", variant="primary", size="lg")

                        with gr.Column(scale=3):
                            upload_output = gr.Markdown(label="Estado")

                    gr.Markdown("### 📚 Documentos en el Repositorio")
                    docs_table = gr.HTML(self._get_documents_table())

                    upload_btn.click(
                        fn=self.upload_document,
                        inputs=[file_input, tags_input, description_input],
                        outputs=[upload_output, docs_table]
                    )

                # TAB 2: Tareas de IA
                with gr.Tab("🤖 Tareas de IA"):
                    gr.Markdown("### Ejecuta tareas de IA sobre el documento actual")

                    with gr.Row():
                        with gr.Column(scale=1):
                            task_selector = gr.Dropdown(
                                label="Selecciona una tarea",
                                choices=[
                                    "informe", "correo", "resumen", "traduccion",
                                    "analisis", "preguntas", "extraccion",
                                    "comparacion", "mejora"
                                ],
                                value="resumen"
                            )
                            task_instructions = gr.Textbox(
                                label="Instrucciones adicionales",
                                placeholder="Ej: 'Traducir al inglés' o 'Resumen de máximo 200 palabras'",
                                lines=4
                            )
                            execute_btn = gr.Button("▶️ Ejecutar Tarea", variant="primary", size="lg")

                        with gr.Column(scale=2):
                            task_output = gr.Markdown(label="Resultado")

                    # Descripción de tareas
                    gr.Markdown("""
                    #### 📋 Tareas disponibles:
                    - **Informe**: Genera un informe profesional completo
                    - **Correo**: Redacta un correo profesional
                    - **Resumen**: Crea un resumen conciso
                    - **Traducción**: Traduce a otro idioma
                    - **Análisis**: Análisis profundo de datos
                    - **Preguntas**: Responde preguntas sobre el documento
                    - **Extracción**: Extrae información específica
                    - **Comparación**: Compara diferentes partes
                    - **Mejora**: Mejora y optimiza el contenido
                    """)

                    execute_btn.click(
                        fn=self.execute_ai_task,
                        inputs=[task_selector, task_instructions],
                        outputs=task_output
                    )

                # TAB 3: Chat con documentos
                with gr.Tab("💬 Chat Inteligente"):
                    gr.Markdown("### Chatea con tus documentos de forma natural")

                    chatbot = gr.Chatbot(
                        label="Conversación",
                        height=500,
                        show_label=True
                    )
                    with gr.Row():
                        chat_input = gr.Textbox(
                            label="Tu mensaje",
                            placeholder="Hazme una pregunta sobre el documento...",
                            lines=2,
                            scale=4
                        )
                        chat_btn = gr.Button("Enviar", variant="primary", scale=1)

                    clear_btn = gr.Button("🗑️ Limpiar chat")

                    chat_btn.click(
                        fn=self.chat_with_document,
                        inputs=[chat_input, chatbot],
                        outputs=[chat_input, chatbot]
                    )

                    chat_input.submit(
                        fn=self.chat_with_document,
                        inputs=[chat_input, chatbot],
                        outputs=[chat_input, chatbot]
                    )

                    clear_btn.click(
                        fn=lambda: ([], ""),
                        outputs=[chatbot, chat_input]
                    )

                # TAB 4: Visualizaciones
                with gr.Tab("📊 Visualizaciones"):
                    gr.Markdown("### Genera gráficos y visualizaciones de tus datos")
                    gr.Markdown("*Solo disponible para archivos Excel*")

                    with gr.Row():
                        with gr.Column(scale=1):
                            viz_type = gr.Dropdown(
                                label="Tipo de visualización",
                                choices=[
                                    "dashboard", "auto", "bar", "line",
                                    "pie", "scatter", "heatmap", "histogram", "table"
                                ],
                                value="dashboard"
                            )
                            viz_title = gr.Textbox(
                                label="Título (opcional)",
                                placeholder="Ej: Análisis de Ventas 2024"
                            )
                            viz_btn = gr.Button("📊 Generar Visualización", variant="primary", size="lg")

                        with gr.Column(scale=2):
                            viz_image = gr.Image(label="Visualización Generada", type="filepath")
                            viz_status = gr.Markdown()

                    viz_btn.click(
                        fn=self.generate_visualization,
                        inputs=[viz_type, viz_title],
                        outputs=[viz_image, viz_status]
                    )

                # TAB 5: Búsqueda
                with gr.Tab("🔍 Buscar Documentos"):
                    gr.Markdown("### Busca en todos tus documentos")

                    search_input = gr.Textbox(
                        label="Término de búsqueda",
                        placeholder="Busca por nombre, descripción, tags o contenido...",
                        lines=1
                    )
                    search_btn = gr.Button("🔍 Buscar", variant="primary")
                    search_output = gr.Markdown()

                    search_btn.click(
                        fn=self.search_documents,
                        inputs=search_input,
                        outputs=search_output
                    )

                    search_input.submit(
                        fn=self.search_documents,
                        inputs=search_input,
                        outputs=search_output
                    )

                # TAB 6: Google Drive
                with gr.Tab("📁 Google Drive"):
                    gr.Markdown("### Integración con Google Drive")
                    gr.Markdown("*Importa y exporta documentos desde/hacia tu Drive*")

                    with gr.Row():
                        with gr.Column():
                            gr.Markdown("#### 📥 Importar desde Drive")
                            drive_search = gr.Textbox(
                                label="Buscar archivos (opcional)",
                                placeholder="Ej: nombre del archivo"
                            )
                            list_drive_btn = gr.Button("📂 Listar Archivos", variant="secondary")
                            drive_files_output = gr.Markdown()

                            list_drive_btn.click(
                                fn=self.list_drive_files,
                                inputs=drive_search,
                                outputs=drive_files_output
                            )

                            gr.Markdown("---")

                            file_id_input = gr.Textbox(
                                label="ID del archivo en Drive",
                                placeholder="Copia el ID del archivo de la lista arriba"
                            )
                            import_tags = gr.Textbox(
                                label="Tags",
                                placeholder="Ej: drive, importante"
                            )
                            import_desc = gr.Textbox(
                                label="Descripción",
                                placeholder="Descripción del documento"
                            )
                            import_btn = gr.Button("⬇️ Importar a Repositorio", variant="primary")
                            import_output = gr.Markdown()

                            import_btn.click(
                                fn=self.import_from_drive,
                                inputs=[file_id_input, import_tags, import_desc],
                                outputs=import_output
                            )

                        with gr.Column():
                            gr.Markdown("#### 📤 Exportar a Drive")
                            folder_id_input = gr.Textbox(
                                label="ID de carpeta destino (opcional)",
                                placeholder="Dejar vacío para raíz de Drive"
                            )
                            export_btn = gr.Button("⬆️ Exportar Documento Actual", variant="primary")
                            export_output = gr.Markdown()

                            export_btn.click(
                                fn=self.export_to_drive,
                                inputs=folder_id_input,
                                outputs=export_output
                            )

                # TAB 7: Gmail
                with gr.Tab("✉️ Gmail"):
                    gr.Markdown("### Enviar Correos con IA")
                    gr.Markdown("*Genera correos profesionales con IA y envíalos via Gmail*")

                    with gr.Row():
                        with gr.Column(scale=1):
                            email_to = gr.Textbox(
                                label="Para:",
                                placeholder="destinatario@ejemplo.com"
                            )
                            email_task = gr.Dropdown(
                                label="Tipo de correo",
                                choices=["correo", "informe", "resumen"],
                                value="correo"
                            )
                            email_instructions = gr.Textbox(
                                label="Instrucciones para la IA",
                                placeholder="Ej: Crear un correo formal presentando los resultados",
                                lines=4
                            )
                            send_email_btn = gr.Button("📧 Generar y Enviar", variant="primary", size="lg")

                        with gr.Column(scale=2):
                            email_output = gr.Markdown()

                    gr.Markdown("""
                    #### 📋 Instrucciones:
                    1. Primero sube un documento (pestaña "Subir Documentos")
                    2. Ingresa el email del destinatario
                    3. Selecciona el tipo de correo
                    4. Añade instrucciones específicas (opcional)
                    5. Haz clic en "Generar y Enviar"

                    **Nota:** La IA generará el contenido basado en el documento actual.
                    """)

                    send_email_btn.click(
                        fn=self.send_email_with_ai,
                        inputs=[email_to, email_task, email_instructions],
                        outputs=email_output
                    )

                # TAB 8: Estadísticas
                with gr.Tab("📈 Estadísticas"):
                    gr.Markdown("### Estadísticas del repositorio e integraciones")

                    stats_btn = gr.Button("🔄 Actualizar Estadísticas", variant="secondary")
                    stats_output = gr.Markdown(self.get_storage_stats())

                    stats_btn.click(
                        fn=self.get_storage_stats,
                        outputs=stats_output
                    )

                    gr.Markdown("---")

                    google_status_btn = gr.Button("🔗 Estado de Google", variant="secondary")
                    google_status_output = gr.Markdown(self.get_google_status())

                    google_status_btn.click(
                        fn=self.get_google_status,
                        outputs=google_status_output
                    )

            gr.Markdown("""
            ---
            **Desarrollado con:** Claude Opus 4.5 (Anthropic) + Gemini (Google AI) + Google Drive & Gmail | **Interfaz:** Gradio

            *Sistema versátil y potente para estudiantes y empresas* 🎓💼
            """)

            # Aplicar tema después de crear la interfaz
            interface.theme = gr.themes.Soft()

        return interface

    def launch(self, share: bool = False, server_port: int = 7860):
        """
        Lanza la interfaz web

        Args:
            share: Si crear un link público
            server_port: Puerto del servidor
        """
        interface = self.create_gradio_interface()

        console.print(f"\n[green]🚀 Lanzando interfaz web en http://localhost:{server_port}[/green]\n")

        interface.launch(
            share=share,
            server_port=server_port,
            server_name="0.0.0.0",
            show_error=True,
            quiet=False,
            debug=True,
            inbrowser=True
        )


def main():
    """Función principal"""
    app = DocumentAIWebInterface()
    app.launch(share=True, server_port=7860)


if __name__ == "__main__":
    main()
