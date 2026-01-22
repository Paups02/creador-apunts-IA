"""
Document Processor - Extrae y procesa contenido de diferentes formatos de documentos
"""

import os
from typing import Dict, List, Optional, Any, Union
from pathlib import Path
import json

# Procesadores específicos
import PyPDF2
import pdfplumber
from docx import Document
import pandas as pd
from PIL import Image
import io
import base64

from rich.console import Console

console = Console()


class DocumentProcessor:
    """Procesador unificado para múltiples formatos de documentos"""

    def __init__(self):
        self.console = console

    def process_document(self, file_path: str, doc_type: Optional[str] = None) -> Dict[str, Any]:
        """
        Procesa un documento y extrae todo su contenido

        Args:
            file_path: Ruta al archivo
            doc_type: Tipo de documento (si no se especifica, se detecta automáticamente)

        Returns:
            Diccionario con el contenido extraído
        """
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"Archivo no encontrado: {file_path}")

        # Detectar tipo si no se especifica
        if not doc_type:
            ext = file_path.lower().split('.')[-1]
            doc_type = self._detect_type_from_extension(ext)

        console.print(f"[cyan]Procesando {doc_type}: {os.path.basename(file_path)}[/cyan]")

        # Procesar según el tipo
        if doc_type == 'pdf':
            return self.process_pdf(file_path)
        elif doc_type == 'word':
            return self.process_word(file_path)
        elif doc_type == 'excel':
            return self.process_excel(file_path)
        elif doc_type == 'text':
            return self.process_text(file_path)
        elif doc_type == 'image':
            return self.process_image(file_path)
        else:
            raise ValueError(f"Tipo de documento no soportado: {doc_type}")

    def _detect_type_from_extension(self, ext: str) -> str:
        """Detecta el tipo de documento según la extensión"""
        ext_map = {
            'pdf': 'pdf',
            'docx': 'word', 'doc': 'word',
            'xlsx': 'excel', 'xls': 'excel', 'csv': 'excel',
            'txt': 'text', 'md': 'text', 'json': 'text',
            'png': 'image', 'jpg': 'image', 'jpeg': 'image',
            'bmp': 'image', 'gif': 'image', 'webp': 'image'
        }
        return ext_map.get(ext, 'unknown')

    def process_pdf(self, file_path: str) -> Dict[str, Any]:
        """
        Procesa archivos PDF completos

        Returns:
            Dict con texto, tablas, imágenes y metadatos
        """
        result = {
            "type": "pdf",
            "filename": os.path.basename(file_path),
            "pages": [],
            "full_text": "",
            "tables": [],
            "images_count": 0,
            "metadata": {}
        }

        try:
            # Usar pdfplumber para extracción avanzada
            with pdfplumber.open(file_path) as pdf:
                result["metadata"] = {
                    "num_pages": len(pdf.pages),
                    "creator": pdf.metadata.get("Creator", ""),
                    "producer": pdf.metadata.get("Producer", ""),
                    "creation_date": str(pdf.metadata.get("CreationDate", ""))
                }

                for i, page in enumerate(pdf.pages):
                    page_data = {
                        "page_num": i + 1,
                        "text": "",
                        "tables": []
                    }

                    # Extraer texto
                    text = page.extract_text()
                    if text:
                        page_data["text"] = text
                        result["full_text"] += text + "\n\n"

                    # Extraer tablas
                    tables = page.extract_tables()
                    if tables:
                        for table in tables:
                            if table:
                                page_data["tables"].append(table)
                                result["tables"].append({
                                    "page": i + 1,
                                    "data": table
                                })

                    # Contar imágenes
                    try:
                        images = page.images
                        result["images_count"] += len(images)
                    except:
                        pass

                    result["pages"].append(page_data)

            console.print(f"[green]✓[/green] PDF procesado: {len(result['pages'])} páginas, "
                        f"{len(result['tables'])} tablas, {result['images_count']} imágenes")

        except Exception as e:
            console.print(f"[red]Error procesando PDF: {str(e)}[/red]")
            result["error"] = str(e)

        return result

    def process_word(self, file_path: str) -> Dict[str, Any]:
        """
        Procesa archivos Word (docx)

        Returns:
            Dict con texto, tablas, imágenes y formato
        """
        result = {
            "type": "word",
            "filename": os.path.basename(file_path),
            "paragraphs": [],
            "tables": [],
            "full_text": "",
            "metadata": {}
        }

        try:
            doc = Document(file_path)

            # Metadatos
            core_props = doc.core_properties
            result["metadata"] = {
                "author": core_props.author or "",
                "title": core_props.title or "",
                "subject": core_props.subject or "",
                "created": str(core_props.created) if core_props.created else "",
                "modified": str(core_props.modified) if core_props.modified else ""
            }

            # Extraer párrafos
            for para in doc.paragraphs:
                if para.text.strip():
                    para_data = {
                        "text": para.text,
                        "style": para.style.name if para.style else ""
                    }
                    result["paragraphs"].append(para_data)
                    result["full_text"] += para.text + "\n"

            # Extraer tablas
            for i, table in enumerate(doc.tables):
                table_data = []
                for row in table.rows:
                    row_data = [cell.text for cell in row.cells]
                    table_data.append(row_data)

                result["tables"].append({
                    "table_num": i + 1,
                    "data": table_data
                })

            console.print(f"[green]✓[/green] Word procesado: {len(result['paragraphs'])} párrafos, "
                        f"{len(result['tables'])} tablas")

        except Exception as e:
            console.print(f"[red]Error procesando Word: {str(e)}[/red]")
            result["error"] = str(e)

        return result

    def process_excel(self, file_path: str) -> Dict[str, Any]:
        """
        Procesa archivos Excel (xlsx, xls, csv)

        Returns:
            Dict con todas las hojas, datos y estadísticas
        """
        result = {
            "type": "excel",
            "filename": os.path.basename(file_path),
            "sheets": [],
            "metadata": {}
        }

        try:
            # Leer archivo
            if file_path.endswith('.csv'):
                df = pd.read_csv(file_path)
                sheets_dict = {"Sheet1": df}
            else:
                sheets_dict = pd.read_excel(file_path, sheet_name=None)

            # Procesar cada hoja
            for sheet_name, df in sheets_dict.items():
                sheet_data = {
                    "name": sheet_name,
                    "rows": len(df),
                    "columns": len(df.columns),
                    "column_names": list(df.columns),
                    "data": df.to_dict('records'),  # Lista de diccionarios
                    "data_types": {col: str(dtype) for col, dtype in df.dtypes.items()},
                    "summary": {}
                }

                # Estadísticas básicas para columnas numéricas
                numeric_cols = df.select_dtypes(include=['number']).columns
                if len(numeric_cols) > 0:
                    sheet_data["summary"] = df[numeric_cols].describe().to_dict()

                result["sheets"].append(sheet_data)

            result["metadata"] = {
                "total_sheets": len(sheets_dict),
                "total_rows": sum(len(df) for df in sheets_dict.values()),
                "total_columns": sum(len(df.columns) for df in sheets_dict.values())
            }

            console.print(f"[green]✓[/green] Excel procesado: {len(result['sheets'])} hojas, "
                        f"{result['metadata']['total_rows']} filas totales")

        except Exception as e:
            console.print(f"[red]Error procesando Excel: {str(e)}[/red]")
            result["error"] = str(e)

        return result

    def process_text(self, file_path: str) -> Dict[str, Any]:
        """
        Procesa archivos de texto (txt, md, json)

        Returns:
            Dict con el contenido del texto
        """
        result = {
            "type": "text",
            "filename": os.path.basename(file_path),
            "content": "",
            "lines": 0,
            "words": 0,
            "chars": 0
        }

        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()

            result["content"] = content
            result["lines"] = len(content.split('\n'))
            result["words"] = len(content.split())
            result["chars"] = len(content)

            # Si es JSON, intentar parsearlo
            if file_path.endswith('.json'):
                try:
                    result["json_data"] = json.loads(content)
                except:
                    pass

            console.print(f"[green]✓[/green] Texto procesado: {result['lines']} líneas, "
                        f"{result['words']} palabras")

        except Exception as e:
            console.print(f"[red]Error procesando texto: {str(e)}[/red]")
            result["error"] = str(e)

        return result

    def process_image(self, file_path: str) -> Dict[str, Any]:
        """
        Procesa archivos de imagen

        Returns:
            Dict con información de la imagen
        """
        result = {
            "type": "image",
            "filename": os.path.basename(file_path),
            "metadata": {}
        }

        try:
            with Image.open(file_path) as img:
                result["metadata"] = {
                    "format": img.format,
                    "mode": img.mode,
                    "size": img.size,
                    "width": img.width,
                    "height": img.height
                }

                # Convertir a base64 para embedding
                buffered = io.BytesIO()
                img.save(buffered, format=img.format)
                img_str = base64.b64encode(buffered.getvalue()).decode()
                result["base64"] = img_str

            console.print(f"[green]✓[/green] Imagen procesada: {img.width}x{img.height} {img.format}")

        except Exception as e:
            console.print(f"[red]Error procesando imagen: {str(e)}[/red]")
            result["error"] = str(e)

        return result

    def extract_text_content(self, processed_data: Dict[str, Any]) -> str:
        """
        Extrae todo el texto de un documento procesado

        Args:
            processed_data: Resultado de process_document()

        Returns:
            Texto completo extraído
        """
        doc_type = processed_data.get("type", "")

        if doc_type == "pdf":
            return processed_data.get("full_text", "")

        elif doc_type == "word":
            return processed_data.get("full_text", "")

        elif doc_type == "excel":
            # Concatenar datos de todas las hojas
            text = ""
            for sheet in processed_data.get("sheets", []):
                text += f"\n\n=== {sheet['name']} ===\n\n"
                text += f"Columnas: {', '.join(sheet['column_names'])}\n\n"
                for row in sheet.get("data", [])[:100]:  # Limitar a 100 filas
                    text += str(row) + "\n"
            return text

        elif doc_type == "text":
            return processed_data.get("content", "")

        elif doc_type == "image":
            return f"Imagen: {processed_data.get('filename', '')} ({processed_data.get('metadata', {}).get('width', 0)}x{processed_data.get('metadata', {}).get('height', 0)})"

        return ""

    def get_document_summary(self, processed_data: Dict[str, Any]) -> str:
        """
        Genera un resumen descriptivo del documento procesado

        Args:
            processed_data: Resultado de process_document()

        Returns:
            Resumen del documento
        """
        doc_type = processed_data.get("type", "")
        filename = processed_data.get("filename", "")

        if doc_type == "pdf":
            pages = len(processed_data.get("pages", []))
            tables = len(processed_data.get("tables", []))
            images = processed_data.get("images_count", 0)
            return f"PDF: {filename} - {pages} páginas, {tables} tablas, {images} imágenes"

        elif doc_type == "word":
            paras = len(processed_data.get("paragraphs", []))
            tables = len(processed_data.get("tables", []))
            return f"Word: {filename} - {paras} párrafos, {tables} tablas"

        elif doc_type == "excel":
            sheets = len(processed_data.get("sheets", []))
            rows = processed_data.get("metadata", {}).get("total_rows", 0)
            return f"Excel: {filename} - {sheets} hojas, {rows} filas"

        elif doc_type == "text":
            lines = processed_data.get("lines", 0)
            words = processed_data.get("words", 0)
            return f"Texto: {filename} - {lines} líneas, {words} palabras"

        elif doc_type == "image":
            meta = processed_data.get("metadata", {})
            return f"Imagen: {filename} - {meta.get('width', 0)}x{meta.get('height', 0)} {meta.get('format', '')}"

        return f"Documento: {filename}"
