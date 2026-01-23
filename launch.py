#!/usr/bin/env python3
"""
Launcher - Agente de IA Documental
===================================

Inicia tanto el servidor backend (API) como el frontend (interfaz web).
"""

import subprocess
import sys
import os
import time
import signal
from pathlib import Path

# Colores para la terminal
class Colors:
    HEADER = '\033[95m'
    BLUE = '\033[94m'
    CYAN = '\033[96m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    RED = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'

processes = []

def print_banner():
    """Imprime el banner de inicio"""
    banner = f"""
{Colors.CYAN}{Colors.BOLD}
    ╔═══════════════════════════════════════════════════════════════╗
    ║                                                               ║
    ║         🤖 AGENTE DE IA DOCUMENTAL PROFESIONAL 🤖            ║
    ║                                                               ║
    ║            Powered by Claude Anthropic & Google AI           ║
    ║                                                               ║
    ╚═══════════════════════════════════════════════════════════════╝
{Colors.ENDC}

{Colors.BOLD}    📄 Gestión Inteligente de Documentos Multi-Formato
    🤖 IA Avanzada para Análisis y Generación de Contenido
    📊 Visualizaciones y Gráficos Profesionales
    💬 Chat Interactivo con tus Documentos{Colors.ENDC}

    {Colors.YELLOW}✨ Ideal para Estudiantes y Empresas ✨{Colors.ENDC}
    """
    print(banner)

def cleanup(signum=None, frame=None):
    """Limpia procesos al salir"""
    print(f"\n{Colors.YELLOW}🛑 Deteniendo servidores...{Colors.ENDC}")

    for process in processes:
        try:
            process.terminate()
            process.wait(timeout=5)
        except subprocess.TimeoutExpired:
            process.kill()
        except Exception as e:
            print(f"{Colors.RED}Error al detener proceso: {e}{Colors.ENDC}")

    print(f"{Colors.GREEN}✅ Servidores detenidos correctamente{Colors.ENDC}")
    sys.exit(0)

def check_dependencies():
    """Verifica dependencias necesarias"""
    print(f"{Colors.CYAN}🔍 Verificando dependencias...{Colors.ENDC}\n")

    required_packages = {
        'fastapi': 'FastAPI',
        'uvicorn': 'Uvicorn',
        'anthropic': 'Anthropic',
        'dotenv': 'python-dotenv'
    }

    missing = []

    for package, name in required_packages.items():
        try:
            __import__(package)
            print(f"{Colors.GREEN}✓ {name}{Colors.ENDC}")
        except ImportError:
            print(f"{Colors.RED}✗ {name}{Colors.ENDC}")
            missing.append(name)

    if missing:
        print(f"\n{Colors.RED}❌ Faltan dependencias: {', '.join(missing)}{Colors.ENDC}")
        print(f"{Colors.YELLOW}Instala con: pip install fastapi uvicorn{Colors.ENDC}\n")
        return False

    print(f"\n{Colors.GREEN}✅ Todas las dependencias están instaladas{Colors.ENDC}\n")
    return True

def start_backend():
    """Inicia el servidor backend"""
    print(f"{Colors.CYAN}🚀 Iniciando servidor backend (API REST)...{Colors.ENDC}")

    backend_process = subprocess.Popen(
        [sys.executable, "backend_api.py"],
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        universal_newlines=True,
        bufsize=1
    )

    processes.append(backend_process)

    # Esperar a que el backend esté listo
    time.sleep(3)

    if backend_process.poll() is None:
        print(f"{Colors.GREEN}✅ Backend iniciado correctamente en http://localhost:8000{Colors.ENDC}\n")
        return True
    else:
        print(f"{Colors.RED}❌ Error al iniciar el backend{Colors.ENDC}\n")
        return False

def start_frontend():
    """Inicia el servidor frontend"""
    print(f"{Colors.CYAN}🚀 Iniciando servidor frontend (Interfaz Web)...{Colors.ENDC}")

    frontend_process = subprocess.Popen(
        [sys.executable, "frontend_server.py"],
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        universal_newlines=True,
        bufsize=1
    )

    processes.append(frontend_process)

    # Esperar a que el frontend esté listo
    time.sleep(2)

    if frontend_process.poll() is None:
        print(f"{Colors.GREEN}✅ Frontend iniciado correctamente en http://localhost:3000{Colors.ENDC}\n")
        return True
    else:
        print(f"{Colors.RED}❌ Error al iniciar el frontend{Colors.ENDC}\n")
        return False

def get_ip_address():
    """Obtiene la dirección IP del sistema"""
    import socket
    try:
        # Intentar obtener la IP de WSL
        result = subprocess.run(['hostname', '-I'], capture_output=True, text=True)
        if result.returncode == 0:
            ip = result.stdout.strip().split()[0]
            return ip
    except:
        pass

    # Método alternativo
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        ip = s.getsockname()[0]
        s.close()
        return ip
    except:
        return "127.0.0.1"

def open_browser():
    """Intenta abrir el navegador automáticamente"""
    import webbrowser
    ip = get_ip_address()

    try:
        print(f"{Colors.CYAN}🌐 Intentando abrir navegador...{Colors.ENDC}\n")
        # Intentar con la IP del sistema primero
        webbrowser.open(f'http://{ip}:3000')
    except Exception as e:
        print(f"{Colors.YELLOW}⚠️  No se pudo abrir el navegador automáticamente{Colors.ENDC}")
        print(f"{Colors.YELLOW}   Abre manualmente una de estas URLs{Colors.ENDC}\n")

def main():
    """Función principal"""
    # Configurar señales para limpieza
    signal.signal(signal.SIGINT, cleanup)
    signal.signal(signal.SIGTERM, cleanup)

    # Mostrar banner
    print_banner()

    # Verificar dependencias
    if not check_dependencies():
        sys.exit(1)

    # Iniciar servidores
    print(f"\n{Colors.BOLD}{'='*60}{Colors.ENDC}\n")

    if not start_backend():
        cleanup()
        sys.exit(1)

    if not start_frontend():
        cleanup()
        sys.exit(1)

    print(f"{Colors.BOLD}{'='*60}{Colors.ENDC}\n")

    # Obtener IP del sistema
    system_ip = get_ip_address()

    # Mostrar información
    print(f"""
{Colors.GREEN}{Colors.BOLD}✅ SISTEMA INICIADO CORRECTAMENTE{Colors.ENDC}

{Colors.BOLD}🌐 URLs de acceso (usa cualquiera):{Colors.ENDC}

{Colors.CYAN}{Colors.BOLD}   → RECOMENDADO (para Windows/WSL):{Colors.ENDC}
   {Colors.BLUE}Frontend:{Colors.ENDC}  http://{system_ip}:3000
   {Colors.BLUE}Backend: {Colors.ENDC}  http://{system_ip}:8000

{Colors.BOLD}   → Alternativas (localhost):{Colors.ENDC}
   Frontend:  http://localhost:3000
   Backend:   http://localhost:8000
   API Docs:  http://localhost:8000/docs

{Colors.BOLD}💡 Instrucciones:{Colors.ENDC}
   1. Abre tu navegador en {Colors.CYAN}http://{system_ip}:3000{Colors.ENDC}
   2. Sube documentos desde la pestaña "Subir Documentos"
   3. Usa las tareas de IA para procesar contenido
   4. Chatea con tus documentos en "Chat Inteligente"

{Colors.YELLOW}Presiona Ctrl+C para detener ambos servidores{Colors.ENDC}
    """)

    # Abrir navegador
    time.sleep(1)
    open_browser()

    # Mantener el script corriendo
    try:
        while True:
            time.sleep(1)
            # Verificar que los procesos sigan corriendo
            for i, process in enumerate(processes):
                if process.poll() is not None:
                    print(f"\n{Colors.RED}❌ Un servidor se detuvo inesperadamente{Colors.ENDC}")
                    cleanup()
                    sys.exit(1)
    except KeyboardInterrupt:
        cleanup()

if __name__ == "__main__":
    main()
