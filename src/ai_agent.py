"""
AI Agent - Agente inteligente con múltiples capacidades usando Claude Anthropic
Capacidades: Informes, Correos, Resúmenes, Traducciones, Análisis, etc.
"""

import os
from typing import Dict, List, Optional, Any
from datetime import datetime
import json

from anthropic import Anthropic
from rich.console import Console
from rich.markdown import Markdown
from dotenv import load_dotenv

# Cargar variables de entorno
load_dotenv()

console = Console()


class AIAgent:
    """
    Agente de IA versátil para procesamiento de documentos y generación de contenido
    """

    # Plantillas de prompts para diferentes tareas
    TASK_PROMPTS = {
        "informe": """Eres un analista profesional experto. Analiza el siguiente contenido y crea un informe detallado y profesional.

El informe debe incluir:
1. Resumen ejecutivo
2. Análisis detallado
3. Puntos clave y hallazgos
4. Conclusiones y recomendaciones

Formato: Markdown profesional con secciones claras, bullets, y énfasis donde sea apropiado.

Contenido a analizar:
{content}

Instrucciones adicionales del usuario:
{user_instructions}
""",

        "correo": """Eres un redactor profesional de correos corporativos. Basándote en el siguiente contenido, redacta un correo profesional.

El correo debe:
1. Tener un asunto claro y conciso
2. Ser profesional y cortés
3. Estar bien estructurado
4. Incluir los puntos principales del contenido
5. Tener un cierre apropiado

Contenido base:
{content}

Instrucciones adicionales:
{user_instructions}

Formato:
Asunto: [asunto del correo]

[Cuerpo del correo]
""",

        "resumen": """Eres un experto en síntesis de información. Crea un resumen claro y conciso del siguiente contenido.

El resumen debe:
1. Capturar las ideas principales
2. Ser conciso pero completo
3. Mantener la información más relevante
4. Estar bien estructurado

Contenido:
{content}

Longitud deseada: {user_instructions}
""",

        "traduccion": """Eres un traductor profesional multilingüe. Traduce el siguiente contenido manteniendo:
1. El tono y estilo original
2. La precisión del significado
3. La naturalidad en el idioma destino
4. El formato y estructura

Idioma destino: {user_instructions}

Contenido a traducir:
{content}
""",

        "analisis": """Eres un analista de datos y contenido experto. Realiza un análisis profundo del siguiente contenido.

Tu análisis debe incluir:
1. Patrones y tendencias identificadas
2. Insights clave
3. Métricas relevantes (si aplica)
4. Interpretación de datos
5. Implicaciones y recomendaciones

Contenido:
{content}

Enfoque del análisis:
{user_instructions}
""",

        "preguntas": """Eres un asistente que responde preguntas basándose en documentos. Analiza el siguiente contenido y responde la pregunta del usuario.

Contenido de referencia:
{content}

Pregunta del usuario:
{user_instructions}

Responde de forma clara, precisa y completa, citando el contenido cuando sea relevante.
""",

        "extraccion": """Eres un experto en extracción de información. Del siguiente contenido, extrae específicamente:

{user_instructions}

Contenido:
{content}

Presenta la información extraída de forma clara y estructurada.
""",

        "comparacion": """Eres un analista comparativo. Compara y contrasta los siguientes documentos o secciones.

Tu comparación debe incluir:
1. Similitudes
2. Diferencias clave
3. Ventajas y desventajas de cada uno
4. Conclusiones

Contenido:
{content}

Aspectos a comparar:
{user_instructions}
""",

        "mejora": """Eres un editor profesional. Mejora y optimiza el siguiente contenido manteniendo su esencia.

Aspectos a mejorar:
{user_instructions}

Contenido original:
{content}

Proporciona el contenido mejorado con explicación de los cambios realizados.
"""
    }

    def __init__(self, api_key: Optional[str] = None, model: str = "claude-opus-4-5-20251101"):
        """
        Inicializa el agente de IA

        Args:
            api_key: API key de Anthropic (si no se proporciona, se lee de .env)
            model: Modelo de Claude a utilizar
        """
        self.api_key = api_key or os.getenv("ANTHROPIC_API_KEY")
        if not self.api_key:
            raise ValueError("No se encontró ANTHROPIC_API_KEY. Configúrela en .env o pásela como parámetro.")

        self.client = Anthropic(api_key=self.api_key)
        self.model = model
        self.console = console

    def execute_task(self,
                    task_type: str,
                    content: str,
                    user_instructions: str = "",
                    temperature: float = 0.7,
                    max_tokens: int = 4096) -> Dict[str, Any]:
        """
        Ejecuta una tarea específica sobre el contenido

        Args:
            task_type: Tipo de tarea (informe, correo, resumen, etc.)
            content: Contenido del documento a procesar
            user_instructions: Instrucciones específicas del usuario
            temperature: Temperatura para la generación (0-1)
            max_tokens: Máximo de tokens a generar

        Returns:
            Dict con el resultado de la tarea
        """
        if task_type not in self.TASK_PROMPTS:
            available = ", ".join(self.TASK_PROMPTS.keys())
            raise ValueError(f"Tipo de tarea '{task_type}' no soportado. Disponibles: {available}")

        # Construir prompt
        prompt = self.TASK_PROMPTS[task_type].format(
            content=content[:50000],  # Limitar contenido para no exceder límites
            user_instructions=user_instructions or "Ninguna instrucción adicional."
        )

        console.print(f"\n[cyan]🤖 Ejecutando tarea: {task_type.upper()}[/cyan]")
        console.print(f"[dim]Modelo: {self.model}[/dim]\n")

        try:
            # Llamar a Claude API
            message = self.client.messages.create(
                model=self.model,
                max_tokens=max_tokens,
                temperature=temperature,
                messages=[
                    {
                        "role": "user",
                        "content": prompt
                    }
                ]
            )

            # Extraer respuesta
            result_text = message.content[0].text

            result = {
                "success": True,
                "task_type": task_type,
                "result": result_text,
                "model": self.model,
                "timestamp": datetime.now().isoformat(),
                "usage": {
                    "input_tokens": message.usage.input_tokens,
                    "output_tokens": message.usage.output_tokens
                }
            }

            console.print(f"[green]✓ Tarea completada exitosamente[/green]")
            console.print(f"[dim]Tokens: {message.usage.input_tokens} in / {message.usage.output_tokens} out[/dim]\n")

            return result

        except Exception as e:
            console.print(f"[red]✗ Error ejecutando tarea: {str(e)}[/red]")
            return {
                "success": False,
                "task_type": task_type,
                "error": str(e),
                "timestamp": datetime.now().isoformat()
            }

    def generate_report(self, content: str, instructions: str = "") -> str:
        """Genera un informe profesional"""
        result = self.execute_task("informe", content, instructions)
        return result.get("result", "") if result["success"] else f"Error: {result.get('error')}"

    def generate_email(self, content: str, instructions: str = "") -> str:
        """Genera un correo profesional"""
        result = self.execute_task("correo", content, instructions)
        return result.get("result", "") if result["success"] else f"Error: {result.get('error')}"

    def generate_summary(self, content: str, length: str = "medio") -> str:
        """Genera un resumen"""
        result = self.execute_task("resumen", content, length)
        return result.get("result", "") if result["success"] else f"Error: {result.get('error')}"

    def translate(self, content: str, target_language: str) -> str:
        """Traduce contenido"""
        result = self.execute_task("traduccion", content, target_language)
        return result.get("result", "") if result["success"] else f"Error: {result.get('error')}"

    def analyze(self, content: str, focus: str = "") -> str:
        """Analiza contenido"""
        result = self.execute_task("analisis", content, focus)
        return result.get("result", "") if result["success"] else f"Error: {result.get('error')}"

    def answer_question(self, content: str, question: str) -> str:
        """Responde preguntas sobre el contenido"""
        result = self.execute_task("preguntas", content, question)
        return result.get("result", "") if result["success"] else f"Error: {result.get('error')}"

    def extract_info(self, content: str, what_to_extract: str) -> str:
        """Extrae información específica"""
        result = self.execute_task("extraccion", content, what_to_extract)
        return result.get("result", "") if result["success"] else f"Error: {result.get('error')}"

    def compare_content(self, content: str, comparison_aspects: str = "") -> str:
        """Compara contenidos"""
        result = self.execute_task("comparacion", content, comparison_aspects)
        return result.get("result", "") if result["success"] else f"Error: {result.get('error')}"

    def improve_content(self, content: str, improvement_areas: str = "") -> str:
        """Mejora contenido"""
        result = self.execute_task("mejora", content, improvement_areas)
        return result.get("result", "") if result["success"] else f"Error: {result.get('error')}"

    def custom_task(self, content: str, custom_prompt: str,
                   temperature: float = 0.7, max_tokens: int = 4096) -> Dict[str, Any]:
        """
        Ejecuta una tarea personalizada con un prompt libre

        Args:
            content: Contenido a procesar
            custom_prompt: Prompt personalizado del usuario
            temperature: Temperatura (0-1)
            max_tokens: Máximo de tokens

        Returns:
            Resultado de la tarea
        """
        full_prompt = f"{custom_prompt}\n\nContenido:\n{content[:50000]}"

        console.print(f"\n[cyan]🤖 Ejecutando tarea personalizada[/cyan]\n")

        try:
            message = self.client.messages.create(
                model=self.model,
                max_tokens=max_tokens,
                temperature=temperature,
                messages=[
                    {
                        "role": "user",
                        "content": full_prompt
                    }
                ]
            )

            result_text = message.content[0].text

            result = {
                "success": True,
                "task_type": "custom",
                "result": result_text,
                "model": self.model,
                "timestamp": datetime.now().isoformat(),
                "usage": {
                    "input_tokens": message.usage.input_tokens,
                    "output_tokens": message.usage.output_tokens
                }
            }

            console.print(f"[green]✓ Tarea completada[/green]\n")
            return result

        except Exception as e:
            console.print(f"[red]✗ Error: {str(e)}[/red]")
            return {
                "success": False,
                "task_type": "custom",
                "error": str(e),
                "timestamp": datetime.now().isoformat()
            }

    def chat(self, content: str, conversation_history: List[Dict[str, str]] = None) -> Dict[str, Any]:
        """
        Modo de chat interactivo con contexto del documento

        Args:
            content: Contenido del documento como contexto
            conversation_history: Historial de la conversación

        Returns:
            Respuesta del agente
        """
        if conversation_history is None:
            conversation_history = []

        # Preparar mensajes
        messages = []

        # Primer mensaje con el contexto del documento
        if len(conversation_history) == 0:
            messages.append({
                "role": "user",
                "content": f"Tengo el siguiente documento que quiero que analices. Responderé preguntas o pediré tareas sobre él.\n\nDocumento:\n{content[:50000]}"
            })
            messages.append({
                "role": "assistant",
                "content": "Perfecto, he analizado el documento. ¿Qué te gustaría saber o qué tarea puedo realizar sobre él?"
            })

        # Añadir historial de conversación
        for msg in conversation_history:
            messages.append(msg)

        try:
            message = self.client.messages.create(
                model=self.model,
                max_tokens=4096,
                messages=messages
            )

            result_text = message.content[0].text

            return {
                "success": True,
                "response": result_text,
                "usage": {
                    "input_tokens": message.usage.input_tokens,
                    "output_tokens": message.usage.output_tokens
                }
            }

        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }

    def get_available_tasks(self) -> List[str]:
        """Retorna la lista de tareas disponibles"""
        return list(self.TASK_PROMPTS.keys())

    def get_task_description(self, task_type: str) -> str:
        """Obtiene la descripción de una tarea"""
        descriptions = {
            "informe": "Genera un informe profesional detallado con análisis completo",
            "correo": "Redacta un correo profesional basado en el contenido",
            "resumen": "Crea un resumen conciso del contenido",
            "traduccion": "Traduce el contenido a otro idioma",
            "analisis": "Realiza un análisis profundo del contenido",
            "preguntas": "Responde preguntas específicas sobre el contenido",
            "extraccion": "Extrae información específica del contenido",
            "comparacion": "Compara y contrasta diferentes partes o documentos",
            "mejora": "Mejora y optimiza el contenido"
        }
        return descriptions.get(task_type, "Tarea personalizada")
