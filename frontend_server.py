#!/usr/bin/env python3
"""
Servidor Frontend para el Agente de IA Documental
=================================================

Servidor HTTP simple para servir la interfaz web HTML/CSS/JS.
"""

import http.server
import socketserver
import os
from pathlib import Path

PORT = 3000
DIRECTORY = Path(__file__).parent / "frontend"

class MyHTTPRequestHandler(http.server.SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=str(DIRECTORY), **kwargs)

    def end_headers(self):
        # Habilitar CORS
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        super().end_headers()

def start_server(port=PORT):
    """Iniciar servidor frontend"""

    os.chdir(DIRECTORY)

    with socketserver.TCPServer(("", port), MyHTTPRequestHandler) as httpd:
        print(f"""
    ╔════════════════════════════════════════════╗
    ║     🌐 FRONTEND - AGENTE IA DOCUMENTAL    ║
    ╚════════════════════════════════════════════╝

    🖥️  Interfaz web disponible en:
       http://localhost:{port}
       http://127.0.0.1:{port}

    📱 Abre tu navegador y accede a la URL

    Presiona Ctrl+C para detener el servidor
        """)

        try:
            httpd.serve_forever()
        except KeyboardInterrupt:
            print("\n\n⚠️  Servidor frontend detenido")
            httpd.shutdown()

if __name__ == "__main__":
    start_server()
