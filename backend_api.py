#!/usr/bin/env python3
"""
Backend API REST para el Agente de IA Documental
=================================================

API REST con FastAPI para interactuar con el sistema de gestión documental.
"""

import sys
import os
from pathlib import Path
import tempfile

# Añadir src al path
sys.path.insert(0, str(Path(__file__).parent / "src"))

from fastapi import FastAPI, UploadFile, File, Form, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, FileResponse
from pydantic import BaseModel
from typing import List, Optional
import uvicorn
from dotenv import load_dotenv
import json

# Cargar variables de entorno
load_dotenv()

# Importar módulos del sistema
from document_manager import DocumentManager
from document_processor import DocumentProcessor
from ai_agent import AIAgent

# Crear aplicación FastAPI
app = FastAPI(
    title="Agente IA Documental API",
    description="API REST para gestión documental con IA",
    version="1.0.0"
)

# Configurar CORS para permitir peticiones desde el frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Permitir todos los orígenes
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Inicializar componentes
try:
    print("Inicializando DocumentManager...")
    doc_manager = DocumentManager()
    print("✓ DocumentManager inicializado")

    print("Inicializando DocumentProcessor...")
    doc_processor = DocumentProcessor()
    print("✓ DocumentProcessor inicializado")

    print("Inicializando AIAgent...")
    ai_agent = AIAgent()
    print("✓ AIAgent inicializado")
except Exception as e:
    import traceback
    print(f"ERROR al inicializar componentes: {e}")
    print(traceback.format_exc())
    raise

# Modelos Pydantic
class AITaskRequest(BaseModel):
    task_type: str
    content: str
    instructions: Optional[str] = ""
    temperature: Optional[float] = 0.7
    max_tokens: Optional[int] = 4096

class SearchRequest(BaseModel):
    query: str

class ChatRequest(BaseModel):
    message: str
    document_id: Optional[str] = None


# =============== ENDPOINTS ===============

@app.get("/")
async def root():
    """Endpoint raíz"""
    return {
        "message": "Agente IA Documental API",
        "version": "1.0.0",
        "status": "running"
    }

@app.get("/health")
async def health_check():
    """Verificar estado del servidor"""
    return {
        "status": "healthy",
        "ai_agent": "active",
        "document_manager": "active"
    }

# ========== DOCUMENTOS ==========

@app.post("/api/documents/upload")
async def upload_document(
    file: UploadFile = File(...),
    tags: Optional[str] = Form(""),
    description: Optional[str] = Form("")
):
    """Subir un documento al sistema"""
    try:
        # Guardar archivo temporalmente (compatible con Windows)
        temp_dir = Path(tempfile.gettempdir())
        temp_path = temp_dir / file.filename
        with open(temp_path, "wb") as f:
            content = await file.read()
            f.write(content)

        # Procesar documento
        processed = doc_processor.process_document(str(temp_path))

        # Agregar a la base de datos
        tags_list = [t.strip() for t in tags.split(",")] if tags else []
        doc_id = doc_manager.add_document(
            file_path=str(temp_path),
            tags=tags_list,
            description=description
        )

        return {
            "success": True,
            "document_id": doc_id,
            "filename": file.filename,
            "type": processed.get("type"),
            "message": "Documento subido correctamente"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/documents/list")
async def list_documents():
    """Listar todos los documentos"""
    try:
        docs = doc_manager.list_documents()
        return {
            "success": True,
            "documents": docs,
            "total": len(docs)
        }
    except Exception as e:
        import traceback
        error_detail = f"{str(e)}\n\nTraceback:\n{traceback.format_exc()}"
        print(f"ERROR en /api/documents/list: {error_detail}")
        raise HTTPException(status_code=500, detail=error_detail)

@app.get("/api/documents/{doc_id}")
async def get_document(doc_id: str):
    """Obtener información de un documento"""
    try:
        doc = doc_manager.get_document(doc_id)
        if not doc:
            raise HTTPException(status_code=404, detail="Documento no encontrado")
        return {
            "success": True,
            "document": doc
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/documents/search")
async def search_documents(request: SearchRequest):
    """Buscar documentos"""
    try:
        results = doc_manager.search_documents(request.query)
        return {
            "success": True,
            "results": results,
            "total": len(results)
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.delete("/api/documents/{doc_id}")
async def delete_document(doc_id: str):
    """Eliminar un documento"""
    try:
        success = doc_manager.delete_document(doc_id)
        if not success:
            raise HTTPException(status_code=404, detail="Documento no encontrado")
        return {
            "success": True,
            "message": "Documento eliminado correctamente"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# ========== IA ==========

@app.post("/api/ai/task")
async def execute_ai_task(request: AITaskRequest):
    """Ejecutar una tarea de IA"""
    try:
        result = ai_agent.execute_task(
            task_type=request.task_type,
            content=request.content,
            user_instructions=request.instructions,
            temperature=request.temperature,
            max_tokens=request.max_tokens
        )
        return {
            "success": True,
            "result": result
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/ai/chat")
async def chat(request: ChatRequest):
    """Chat con documentos"""
    try:
        # Si hay un document_id, obtener su contenido
        context = ""
        if request.document_id:
            doc = doc_manager.get_document(request.document_id)
            if doc:
                context = f"Documento: {doc.get('metadata', {}).get('name', '')}\n\n{doc.get('content', '')}"

        # Ejecutar tarea de IA tipo "preguntas"
        result = ai_agent.execute_task(
            task_type="preguntas",
            content=context if context else request.message,
            user_instructions=request.message if context else "",
            temperature=0.7,
            max_tokens=2048
        )

        return {
            "success": True,
            "response": result.get("result", ""),
            "document_id": request.document_id
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/ai/task-types")
async def get_task_types():
    """Obtener tipos de tareas disponibles"""
    return {
        "success": True,
        "task_types": [
            {"id": "informe", "name": "Informe Profesional", "description": "Genera informes formales y estructurados"},
            {"id": "correo", "name": "Correo Electrónico", "description": "Redacta correos profesionales"},
            {"id": "resumen", "name": "Resumen", "description": "Crea resúmenes concisos"},
            {"id": "traduccion", "name": "Traducción", "description": "Traduce textos a otros idiomas"},
            {"id": "analisis", "name": "Análisis", "description": "Analiza contenido en profundidad"},
            {"id": "preguntas", "name": "Preguntas y Respuestas", "description": "Responde preguntas sobre el contenido"},
            {"id": "extraccion", "name": "Extracción de Datos", "description": "Extrae información específica"},
            {"id": "comparacion", "name": "Comparación", "description": "Compara documentos o conceptos"},
            {"id": "mejora", "name": "Mejora de Texto", "description": "Mejora y optimiza textos"}
        ]
    }

# ========== ESTADÍSTICAS ==========

@app.get("/api/stats")
async def get_stats():
    """Obtener estadísticas del sistema"""
    try:
        docs = doc_manager.list_documents()
        return {
            "success": True,
            "stats": {
                "total_documents": len(docs),
                "ai_agent_status": "active",
                "available_tasks": 9
            }
        }
    except Exception as e:
        import traceback
        error_detail = f"{str(e)}\n\nTraceback:\n{traceback.format_exc()}"
        print(f"ERROR en /api/stats: {error_detail}")
        raise HTTPException(status_code=500, detail=error_detail)


def start_server(port: int = 8000):
    """Iniciar servidor backend"""
    print(f"""
    ╔════════════════════════════════════════════╗
    ║   🚀 BACKEND API - AGENTE IA DOCUMENTAL   ║
    ╚════════════════════════════════════════════╝

    📡 API REST corriendo en: http://localhost:{port}
    📚 Documentación: http://localhost:{port}/docs
    🔧 Health check: http://localhost:{port}/health

    """)

    uvicorn.run(
        app,
        host="0.0.0.0",
        port=port,
        log_level="info"
    )


if __name__ == "__main__":
    start_server(port=8000)
