#!/usr/bin/env python3
"""
Agente de IA Documental Profesional
====================================

Sistema inteligente de gestión documental con capacidades avanzadas de IA.

Características:
- 📄 Soporte multi-formato: PDF, Word, Excel, imágenes, texto
- 🤖 IA avanzada: Claude Anthropic para procesamiento de lenguaje
- 📊 Visualizaciones: Gráficos y dashboards con Google AI
- 💬 Chat interactivo con documentos
- 🔍 Búsqueda y análisis inteligente

Para estudiantes y empresas.

Uso:
    python app.py

Requisitos:
    - Python 3.8+
    - API Keys configuradas en .env:
        - ANTHROPIC_API_KEY
        - GOOGLE_API_KEY

Autor: Claude AI Agent
Versión: 1.0.0
"""

import sys
import os
from pathlib import Path

# Añadir src al path
sys.path.insert(0, str(Path(__file__).parent / "src"))

from rich.console import Console
from rich.panel import Panel
from rich import print as rprint

console = Console()


def check_environment():
    """Verifica que el entorno esté configurado correctamente"""

    console.print("\n[cyan]🔍 Verificando configuración del entorno...[/cyan]\n")

    issues = []

    # Verificar archivo .env
    if not os.path.exists(".env"):
        issues.append("❌ Archivo .env no encontrado")
        console.print("[red]❌ Archivo .env no encontrado[/red]")
    else:
        console.print("[green]✓ Archivo .env encontrado[/green]")

        # Verificar API keys
        from dotenv import load_dotenv
        load_dotenv()

        anthropic_key = os.getenv("ANTHROPIC_API_KEY")
        google_key = os.getenv("GOOGLE_API_KEY")

        if not anthropic_key:
            issues.append("❌ ANTHROPIC_API_KEY no configurada en .env")
            console.print("[red]❌ ANTHROPIC_API_KEY no configurada[/red]")
        else:
            console.print("[green]✓ ANTHROPIC_API_KEY configurada[/green]")

        if not google_key:
            issues.append("⚠️  GOOGLE_API_KEY no configurada (opcional)")
            console.print("[yellow]⚠️  GOOGLE_API_KEY no configurada (opcional)[/yellow]")
        else:
            console.print("[green]✓ GOOGLE_API_KEY configurada[/green]")

    # Verificar dependencias
    console.print("\n[cyan]📦 Verificando dependencias...[/cyan]\n")

    required_packages = [
        "anthropic",
        "gradio",
        "pandas",
        "matplotlib",
        "seaborn",
        "PIL",
        "docx",
        "PyPDF2",
        "pdfplumber",
        "rich"
    ]

    missing_packages = []

    for package in required_packages:
        try:
            if package == "PIL":
                __import__("PIL")
            elif package == "docx":
                __import__("docx")
            else:
                __import__(package)
            console.print(f"[green]✓ {package}[/green]")
        except ImportError:
            missing_packages.append(package)
            console.print(f"[red]❌ {package}[/red]")

    if missing_packages:
        issues.append(f"❌ Paquetes faltantes: {', '.join(missing_packages)}")
        console.print(f"\n[red]Instala los paquetes faltantes con:[/red]")
        console.print(f"[yellow]pip install -r requirements.txt[/yellow]")

    # Resumen
    console.print()
    if issues:
        rprint(Panel.fit(
            "\n".join(issues),
            title="⚠️  Problemas Encontrados",
            border_style="yellow"
        ))
        return False
    else:
        rprint(Panel.fit(
            "✅ Todas las verificaciones pasaron correctamente",
            title="✓ Sistema Listo",
            border_style="green"
        ))
        return True


def print_banner():
    """Imprime el banner de bienvenida"""

    banner = """
    ╔═══════════════════════════════════════════════════════════════╗
    ║                                                               ║
    ║         🤖 AGENTE DE IA DOCUMENTAL PROFESIONAL 🤖            ║
    ║                                                               ║
    ║            Powered by Claude Anthropic & Google AI           ║
    ║                                                               ║
    ╚═══════════════════════════════════════════════════════════════╝

    📄 Gestión Inteligente de Documentos Multi-Formato
    🤖 IA Avanzada para Análisis y Generación de Contenido
    📊 Visualizaciones y Gráficos Profesionales
    💬 Chat Interactivo con tus Documentos

    ✨ Ideal para Estudiantes y Empresas ✨
    """

    console.print(banner, style="bold cyan")


def main():
    """Función principal"""

    # Imprimir banner
    print_banner()

    # Verificar entorno
    if not check_environment():
        console.print("\n[red]Por favor, corrige los problemas antes de continuar.[/red]")
        console.print("[yellow]Consulta el README.md para más información.[/yellow]\n")
        return 1

    # Iniciar aplicación
    console.print("\n[cyan]🚀 Iniciando interfaz web...[/cyan]\n")

    try:
        from web_interface import DocumentAIWebInterface

        # Crear e iniciar aplicación
        app = DocumentAIWebInterface()

        console.print("[green]✓ Aplicación iniciada correctamente[/green]")
        console.print("\n[bold yellow]🌐 Accede a la interfaz web en:[/bold yellow]")
        console.print("[bold blue]   http://localhost:7860[/bold blue]\n")
        console.print("[dim]Presiona Ctrl+C para detener el servidor[/dim]\n")

        # Lanzar interfaz
        app.launch(share=False, server_port=7860)

    except KeyboardInterrupt:
        console.print("\n\n[yellow]⚠️  Servidor detenido por el usuario[/yellow]")
        return 0
    except Exception as e:
        console.print(f"\n[red]❌ Error al iniciar la aplicación:[/red]")
        console.print(f"[red]{str(e)}[/red]\n")
        import traceback
        console.print("[dim]" + traceback.format_exc() + "[/dim]")
        return 1

    return 0


if __name__ == "__main__":
    sys.exit(main())
