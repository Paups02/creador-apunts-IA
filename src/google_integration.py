"""
Google Integration - Integración con Google Drive y Gmail
Permite leer/escribir documentos en Drive y enviar correos via Gmail
"""

import os
import io
import base64
from typing import Dict, List, Optional, Any
from datetime import datetime
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email import encoders

from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload, MediaIoBaseDownload
from google.oauth2.credentials import Credentials
from google.auth.transport.requests import Request
from google_auth_oauthlib.flow import InstalledAppFlow
import json

from rich.console import Console
from dotenv import load_dotenv

load_dotenv()
console = Console()


class GoogleDriveManager:
    """
    Gestor de Google Drive para lectura/escritura de documentos
    """

    # Scopes necesarios para Drive
    SCOPES = ['https://www.googleapis.com/auth/drive']

    def __init__(self, credentials_path: Optional[str] = None):
        """
        Inicializa el gestor de Google Drive

        Args:
            credentials_path: Ruta al archivo de credenciales (opcional)
        """
        self.console = console
        self.credentials_path = credentials_path or "./google_credentials.json"
        self.token_path = "./google_token.json"
        self.service = None

        # Intentar autenticación
        try:
            self.service = self._authenticate()
            if self.service:
                console.print("[green]✓[/green] Google Drive conectado")
            else:
                console.print("[yellow]⚠[/yellow] Google Drive no disponible (requiere autenticación OAuth)")
        except Exception as e:
            console.print(f"[yellow]⚠[/yellow] Google Drive no disponible: {str(e)}")

    def _authenticate(self):
        """Autentica con Google Drive usando OAuth2"""
        creds = None

        # Cargar token existente
        if os.path.exists(self.token_path):
            try:
                with open(self.token_path, 'r') as token_file:
                    token_data = json.load(token_file)
                    creds = Credentials.from_authorized_user_info(token_data, self.SCOPES)
            except:
                pass

        # Si no hay credenciales válidas
        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                try:
                    creds.refresh(Request())
                except:
                    return None
            else:
                # Requiere archivo de credenciales OAuth
                if not os.path.exists(self.credentials_path):
                    console.print(f"[yellow]⚠[/yellow] No se encontró {self.credentials_path}")
                    console.print("[dim]Google Drive requiere OAuth2. Usa la API key para funcionalidad básica.[/dim]")
                    return None

                try:
                    flow = InstalledAppFlow.from_client_secrets_file(
                        self.credentials_path, self.SCOPES
                    )
                    creds = flow.run_local_server(port=0)
                except:
                    return None

            # Guardar token
            try:
                with open(self.token_path, 'w') as token_file:
                    json.dump(json.loads(creds.to_json()), token_file)
            except:
                pass

        try:
            return build('drive', 'v3', credentials=creds)
        except:
            return None

    def list_files(self, query: str = "", max_results: int = 20) -> List[Dict[str, Any]]:
        """
        Lista archivos en Google Drive

        Args:
            query: Consulta de búsqueda (ej: "name contains 'informe'")
            max_results: Número máximo de resultados

        Returns:
            Lista de archivos
        """
        if not self.service:
            return []

        try:
            results = self.service.files().list(
                q=query,
                pageSize=max_results,
                fields="files(id, name, mimeType, size, createdTime, modifiedTime)"
            ).execute()

            files = results.get('files', [])
            console.print(f"[green]✓[/green] Encontrados {len(files)} archivos en Drive")
            return files

        except Exception as e:
            console.print(f"[red]✗[/red] Error listando archivos: {str(e)}")
            return []

    def download_file(self, file_id: str, destination_path: str) -> bool:
        """
        Descarga un archivo de Google Drive

        Args:
            file_id: ID del archivo en Drive
            destination_path: Ruta local donde guardar

        Returns:
            True si tuvo éxito
        """
        if not self.service:
            return False

        try:
            request = self.service.files().get_media(fileId=file_id)
            fh = io.BytesIO()
            downloader = MediaIoBaseDownload(fh, request)

            done = False
            while not done:
                status, done = downloader.next_chunk()

            # Guardar archivo
            with open(destination_path, 'wb') as f:
                f.write(fh.getvalue())

            console.print(f"[green]✓[/green] Archivo descargado: {destination_path}")
            return True

        except Exception as e:
            console.print(f"[red]✗[/red] Error descargando archivo: {str(e)}")
            return False

    def upload_file(self, file_path: str, folder_id: Optional[str] = None) -> Optional[str]:
        """
        Sube un archivo a Google Drive

        Args:
            file_path: Ruta del archivo local
            folder_id: ID de la carpeta destino (opcional)

        Returns:
            ID del archivo subido o None si falló
        """
        if not self.service:
            return None

        try:
            file_metadata = {
                'name': os.path.basename(file_path)
            }

            if folder_id:
                file_metadata['parents'] = [folder_id]

            # Determinar tipo MIME
            mime_types = {
                '.pdf': 'application/pdf',
                '.docx': 'application/vnd.openxmlformats-officedocument.wordprocessingml.document',
                '.xlsx': 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
                '.txt': 'text/plain',
                '.csv': 'text/csv'
            }

            ext = os.path.splitext(file_path)[1].lower()
            mime_type = mime_types.get(ext, 'application/octet-stream')

            media = MediaFileUpload(file_path, mimetype=mime_type)

            file = self.service.files().create(
                body=file_metadata,
                media_body=media,
                fields='id'
            ).execute()

            file_id = file.get('id')
            console.print(f"[green]✓[/green] Archivo subido a Drive: {file_id}")
            return file_id

        except Exception as e:
            console.print(f"[red]✗[/red] Error subiendo archivo: {str(e)}")
            return None

    def create_folder(self, folder_name: str, parent_id: Optional[str] = None) -> Optional[str]:
        """
        Crea una carpeta en Google Drive

        Args:
            folder_name: Nombre de la carpeta
            parent_id: ID de la carpeta padre (opcional)

        Returns:
            ID de la carpeta creada
        """
        if not self.service:
            return None

        try:
            file_metadata = {
                'name': folder_name,
                'mimeType': 'application/vnd.google-apps.folder'
            }

            if parent_id:
                file_metadata['parents'] = [parent_id]

            folder = self.service.files().create(
                body=file_metadata,
                fields='id'
            ).execute()

            folder_id = folder.get('id')
            console.print(f"[green]✓[/green] Carpeta creada: {folder_name} ({folder_id})")
            return folder_id

        except Exception as e:
            console.print(f"[red]✗[/red] Error creando carpeta: {str(e)}")
            return None

    def search_files(self, filename: str, mime_type: Optional[str] = None) -> List[Dict[str, Any]]:
        """
        Busca archivos por nombre y tipo

        Args:
            filename: Nombre del archivo a buscar
            mime_type: Tipo MIME (opcional)

        Returns:
            Lista de archivos encontrados
        """
        query = f"name contains '{filename}'"

        if mime_type:
            query += f" and mimeType='{mime_type}'"

        return self.list_files(query=query)


class GmailManager:
    """
    Gestor de Gmail para envío de correos electrónicos
    """

    # Scopes necesarios para Gmail
    SCOPES = ['https://www.googleapis.com/auth/gmail.send']

    def __init__(self, credentials_path: Optional[str] = None):
        """
        Inicializa el gestor de Gmail

        Args:
            credentials_path: Ruta al archivo de credenciales (opcional)
        """
        self.console = console
        self.credentials_path = credentials_path or "./google_credentials.json"
        self.token_path = "./gmail_token.json"
        self.service = None

        # Intentar autenticación
        try:
            self.service = self._authenticate()
            if self.service:
                console.print("[green]✓[/green] Gmail conectado")
            else:
                console.print("[yellow]⚠[/yellow] Gmail no disponible (requiere autenticación OAuth)")
        except Exception as e:
            console.print(f"[yellow]⚠[/yellow] Gmail no disponible: {str(e)}")

    def _authenticate(self):
        """Autentica con Gmail usando OAuth2"""
        creds = None

        # Cargar token existente
        if os.path.exists(self.token_path):
            try:
                with open(self.token_path, 'r') as token_file:
                    token_data = json.load(token_file)
                    creds = Credentials.from_authorized_user_info(token_data, self.SCOPES)
            except:
                pass

        # Si no hay credenciales válidas
        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                try:
                    creds.refresh(Request())
                except:
                    return None
            else:
                # Requiere archivo de credenciales OAuth
                if not os.path.exists(self.credentials_path):
                    console.print(f"[yellow]⚠[/yellow] No se encontró {self.credentials_path}")
                    console.print("[dim]Gmail requiere OAuth2. Descarga las credenciales desde Google Cloud Console.[/dim]")
                    return None

                try:
                    flow = InstalledAppFlow.from_client_secrets_file(
                        self.credentials_path, self.SCOPES
                    )
                    creds = flow.run_local_server(port=0)
                except:
                    return None

            # Guardar token
            try:
                with open(self.token_path, 'w') as token_file:
                    json.dump(json.loads(creds.to_json()), token_file)
            except:
                pass

        try:
            return build('gmail', 'v1', credentials=creds)
        except:
            return None

    def send_email(self,
                   to: str,
                   subject: str,
                   body: str,
                   cc: Optional[List[str]] = None,
                   bcc: Optional[List[str]] = None,
                   attachments: Optional[List[str]] = None,
                   is_html: bool = False) -> bool:
        """
        Envía un correo electrónico via Gmail

        Args:
            to: Destinatario principal
            subject: Asunto del correo
            body: Cuerpo del mensaje
            cc: Lista de destinatarios en copia (opcional)
            bcc: Lista de destinatarios en copia oculta (opcional)
            attachments: Lista de rutas de archivos adjuntos (opcional)
            is_html: Si el body es HTML

        Returns:
            True si se envió correctamente
        """
        if not self.service:
            console.print("[yellow]⚠[/yellow] Gmail no está autenticado")
            return False

        try:
            # Crear mensaje
            message = MIMEMultipart()
            message['To'] = to
            message['Subject'] = subject

            if cc:
                message['Cc'] = ', '.join(cc)
            if bcc:
                message['Bcc'] = ', '.join(bcc)

            # Añadir cuerpo
            if is_html:
                message.attach(MIMEText(body, 'html'))
            else:
                message.attach(MIMEText(body, 'plain'))

            # Añadir adjuntos
            if attachments:
                for file_path in attachments:
                    if os.path.exists(file_path):
                        with open(file_path, 'rb') as f:
                            part = MIMEBase('application', 'octet-stream')
                            part.set_payload(f.read())
                            encoders.encode_base64(part)
                            part.add_header(
                                'Content-Disposition',
                                f'attachment; filename= {os.path.basename(file_path)}'
                            )
                            message.attach(part)

            # Enviar
            raw_message = base64.urlsafe_b64encode(message.as_bytes()).decode()
            send_message = {'raw': raw_message}

            self.service.users().messages().send(
                userId='me',
                body=send_message
            ).execute()

            console.print(f"[green]✓[/green] Correo enviado a: {to}")
            return True

        except Exception as e:
            console.print(f"[red]✗[/red] Error enviando correo: {str(e)}")
            return False

    def send_email_with_ai_content(self,
                                   to: str,
                                   ai_generated_content: str,
                                   attachments: Optional[List[str]] = None) -> bool:
        """
        Envía un correo usando contenido generado por IA

        Args:
            to: Destinatario
            ai_generated_content: Contenido generado que incluye asunto y cuerpo
            attachments: Archivos adjuntos (opcional)

        Returns:
            True si se envió correctamente
        """
        # Extraer asunto del contenido generado
        lines = ai_generated_content.split('\n')
        subject = "Mensaje generado por IA"
        body = ai_generated_content

        for i, line in enumerate(lines):
            if line.lower().startswith('asunto:'):
                subject = line.split(':', 1)[1].strip()
                body = '\n'.join(lines[i+1:]).strip()
                break

        return self.send_email(to, subject, body, attachments=attachments)


class GoogleIntegration:
    """
    Clase unificada para integración con servicios de Google
    """

    def __init__(self):
        """Inicializa todas las integraciones de Google"""
        console.print("\n[cyan]🔗 Inicializando integraciones de Google...[/cyan]\n")

        self.drive = GoogleDriveManager()
        self.gmail = GmailManager()

        console.print()

    def is_drive_available(self) -> bool:
        """Verifica si Google Drive está disponible"""
        return self.drive.service is not None

    def is_gmail_available(self) -> bool:
        """Verifica si Gmail está disponible"""
        return self.gmail.service is not None

    def get_status(self) -> Dict[str, bool]:
        """Obtiene el estado de todas las integraciones"""
        return {
            "drive": self.is_drive_available(),
            "gmail": self.is_gmail_available()
        }
