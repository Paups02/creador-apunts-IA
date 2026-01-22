"""
Document Manager - Sistema de gestión de documentos multi-formato
Soporta: PDF, Word (docx), Excel (xlsx, csv), TXT, e imágenes
"""

import os
import json
from pathlib import Path
from typing import Dict, List, Optional, Tuple
from datetime import datetime
import hashlib

# Importaciones para procesamiento de archivos
import PyPDF2
import pdfplumber
from docx import Document
import pandas as pd
from PIL import Image
import io

from rich.console import Console

console = Console()


class DocumentManager:
    """Gestor centralizado de documentos con soporte multi-formato"""

    SUPPORTED_FORMATS = {
        'pdf': ['pdf'],
        'word': ['docx', 'doc'],
        'excel': ['xlsx', 'xls', 'csv'],
        'text': ['txt', 'md', 'json'],
        'image': ['png', 'jpg', 'jpeg', 'bmp', 'gif', 'webp']
    }

    def __init__(self, storage_path: str = "./document_storage"):
        """
        Inicializa el gestor de documentos

        Args:
            storage_path: Ruta donde se almacenarán los documentos y metadatos
        """
        self.storage_path = Path(storage_path)
        self.metadata_file = self.storage_path / "metadata.json"
        self._ensure_storage_structure()
        self.metadata = self._load_metadata()

    def _ensure_storage_structure(self):
        """Crea la estructura de directorios necesaria"""
        self.storage_path.mkdir(parents=True, exist_ok=True)

        # Crear subdirectorios por tipo
        for doc_type in self.SUPPORTED_FORMATS.keys():
            (self.storage_path / doc_type).mkdir(exist_ok=True)

    def _load_metadata(self) -> Dict:
        """Carga el archivo de metadatos"""
        if self.metadata_file.exists():
            with open(self.metadata_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        return {"documents": {}, "last_updated": None}

    def _save_metadata(self):
        """Guarda el archivo de metadatos"""
        self.metadata["last_updated"] = datetime.now().isoformat()
        with open(self.metadata_file, 'w', encoding='utf-8') as f:
            json.dump(self.metadata, f, indent=2, ensure_ascii=False)

    def _calculate_file_hash(self, file_path: str) -> str:
        """Calcula el hash SHA256 de un archivo"""
        sha256 = hashlib.sha256()
        with open(file_path, 'rb') as f:
            for chunk in iter(lambda: f.read(8192), b''):
                sha256.update(chunk)
        return sha256.hexdigest()

    def _get_file_type(self, filename: str) -> Optional[str]:
        """Determina el tipo de documento según la extensión"""
        ext = filename.lower().split('.')[-1]
        for doc_type, extensions in self.SUPPORTED_FORMATS.items():
            if ext in extensions:
                return doc_type
        return None

    def add_document(self, file_path: str, tags: List[str] = None,
                    description: str = "") -> str:
        """
        Añade un documento al repositorio

        Args:
            file_path: Ruta del documento a añadir
            tags: Etiquetas para clasificar el documento
            description: Descripción opcional del documento

        Returns:
            ID único del documento añadido
        """
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"Archivo no encontrado: {file_path}")

        # Detectar tipo de documento
        filename = os.path.basename(file_path)
        doc_type = self._get_file_type(filename)

        if not doc_type:
            raise ValueError(f"Formato de archivo no soportado: {filename}")

        # Calcular hash y crear ID único
        file_hash = self._calculate_file_hash(file_path)
        doc_id = f"{doc_type}_{file_hash[:16]}_{datetime.now().strftime('%Y%m%d_%H%M%S')}"

        # Copiar archivo al storage
        dest_path = self.storage_path / doc_type / f"{doc_id}_{filename}"

        import shutil
        shutil.copy2(file_path, dest_path)

        # Extraer contenido del documento
        content_preview = self._extract_content_preview(str(dest_path), doc_type)

        # Guardar metadata
        self.metadata["documents"][doc_id] = {
            "id": doc_id,
            "filename": filename,
            "type": doc_type,
            "path": str(dest_path),
            "size": os.path.getsize(file_path),
            "hash": file_hash,
            "tags": tags or [],
            "description": description,
            "uploaded_at": datetime.now().isoformat(),
            "content_preview": content_preview,
            "processed": False
        }

        self._save_metadata()

        console.print(f"[green]✓[/green] Documento añadido: {filename} (ID: {doc_id})")
        return doc_id

    def _extract_content_preview(self, file_path: str, doc_type: str,
                                 max_chars: int = 500) -> str:
        """Extrae una vista previa del contenido del documento"""
        try:
            if doc_type == 'pdf':
                return self._extract_pdf_preview(file_path, max_chars)
            elif doc_type == 'word':
                return self._extract_word_preview(file_path, max_chars)
            elif doc_type == 'excel':
                return self._extract_excel_preview(file_path, max_chars)
            elif doc_type == 'text':
                return self._extract_text_preview(file_path, max_chars)
            elif doc_type == 'image':
                return f"Imagen: {os.path.basename(file_path)}"
            return ""
        except Exception as e:
            console.print(f"[yellow]Advertencia: No se pudo extraer preview - {str(e)}[/yellow]")
            return ""

    def _extract_pdf_preview(self, file_path: str, max_chars: int) -> str:
        """Extrae preview de PDF"""
        try:
            with pdfplumber.open(file_path) as pdf:
                if len(pdf.pages) > 0:
                    text = pdf.pages[0].extract_text() or ""
                    return text[:max_chars]
        except:
            pass
        return ""

    def _extract_word_preview(self, file_path: str, max_chars: int) -> str:
        """Extrae preview de Word"""
        try:
            doc = Document(file_path)
            text = "\n".join([para.text for para in doc.paragraphs[:5]])
            return text[:max_chars]
        except:
            pass
        return ""

    def _extract_excel_preview(self, file_path: str, max_chars: int) -> str:
        """Extrae preview de Excel"""
        try:
            df = pd.read_excel(file_path) if file_path.endswith(('.xlsx', '.xls')) else pd.read_csv(file_path)
            preview = f"Filas: {len(df)}, Columnas: {len(df.columns)}\n"
            preview += f"Columnas: {', '.join(df.columns[:5])}"
            return preview[:max_chars]
        except:
            pass
        return ""

    def _extract_text_preview(self, file_path: str, max_chars: int) -> str:
        """Extrae preview de texto"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                return f.read(max_chars)
        except:
            pass
        return ""

    def get_document(self, doc_id: str) -> Optional[Dict]:
        """Obtiene la metadata de un documento por su ID"""
        return self.metadata["documents"].get(doc_id)

    def list_documents(self, doc_type: Optional[str] = None,
                      tags: Optional[List[str]] = None) -> List[Dict]:
        """
        Lista documentos con filtros opcionales

        Args:
            doc_type: Filtrar por tipo de documento
            tags: Filtrar por etiquetas

        Returns:
            Lista de documentos que cumplen los criterios
        """
        documents = list(self.metadata["documents"].values())

        if doc_type:
            documents = [d for d in documents if d["type"] == doc_type]

        if tags:
            documents = [d for d in documents if any(tag in d["tags"] for tag in tags)]

        return documents

    def delete_document(self, doc_id: str) -> bool:
        """Elimina un documento del repositorio"""
        doc = self.get_document(doc_id)
        if not doc:
            return False

        # Eliminar archivo físico
        if os.path.exists(doc["path"]):
            os.remove(doc["path"])

        # Eliminar metadata
        del self.metadata["documents"][doc_id]
        self._save_metadata()

        console.print(f"[green]✓[/green] Documento eliminado: {doc['filename']}")
        return True

    def search_documents(self, query: str) -> List[Dict]:
        """
        Busca documentos por nombre, descripción o contenido

        Args:
            query: Término de búsqueda

        Returns:
            Lista de documentos que coinciden
        """
        query_lower = query.lower()
        results = []

        for doc in self.metadata["documents"].values():
            if (query_lower in doc["filename"].lower() or
                query_lower in doc.get("description", "").lower() or
                query_lower in doc.get("content_preview", "").lower() or
                any(query_lower in tag.lower() for tag in doc.get("tags", []))):
                results.append(doc)

        return results

    def get_storage_stats(self) -> Dict:
        """Obtiene estadísticas del repositorio"""
        total_docs = len(self.metadata["documents"])
        total_size = sum(doc["size"] for doc in self.metadata["documents"].values())

        by_type = {}
        for doc in self.metadata["documents"].values():
            doc_type = doc["type"]
            by_type[doc_type] = by_type.get(doc_type, 0) + 1

        return {
            "total_documents": total_docs,
            "total_size_mb": round(total_size / (1024 * 1024), 2),
            "by_type": by_type,
            "storage_path": str(self.storage_path)
        }
