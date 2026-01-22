"""
Visualization Generator - Generador de imágenes, gráficos y visualizaciones usando Google AI
Utiliza Gemini para generar visualizaciones inteligentes basadas en datos
"""

import os
from typing import Dict, List, Optional, Any, Tuple
from datetime import datetime
import json
import base64
from io import BytesIO

# Google AI
try:
    import google.generativeai as genai
except ImportError:
    genai = None

# Visualización y gráficos
import matplotlib
matplotlib.use('Agg')  # Backend sin GUI
import matplotlib.pyplot as plt
import seaborn as sns
import pandas as pd
import numpy as np
from PIL import Image, ImageDraw, ImageFont

from rich.console import Console
from dotenv import load_dotenv

load_dotenv()

console = Console()


class VisualizationGenerator:
    """
    Generador de visualizaciones usando Google AI y bibliotecas de gráficos
    """

    def __init__(self, api_key: Optional[str] = None):
        """
        Inicializa el generador de visualizaciones

        Args:
            api_key: API key de Google AI (si no se proporciona, se lee de .env)
        """
        self.api_key = api_key or os.getenv("GOOGLE_API_KEY")
        self.console = console

        # Configurar Google AI si está disponible
        if genai and self.api_key:
            try:
                genai.configure(api_key=self.api_key)
                self.gemini_available = True
                console.print("[green]✓[/green] Google AI (Gemini) configurado")
            except Exception as e:
                self.gemini_available = False
                console.print(f"[yellow]⚠[/yellow] Google AI no disponible: {str(e)}")
        else:
            self.gemini_available = False
            if not genai:
                console.print("[yellow]⚠[/yellow] Instale google-generativeai: pip install google-generativeai")

        # Configurar estilo de gráficos
        sns.set_theme(style="whitegrid")
        plt.rcParams['figure.figsize'] = (12, 6)
        plt.rcParams['font.size'] = 10

    def generate_chart_from_data(self,
                                 data: pd.DataFrame,
                                 chart_type: str = "auto",
                                 title: str = "",
                                 output_path: Optional[str] = None) -> str:
        """
        Genera un gráfico a partir de datos

        Args:
            data: DataFrame con los datos
            chart_type: Tipo de gráfico (bar, line, pie, scatter, heatmap, auto)
            title: Título del gráfico
            output_path: Ruta donde guardar la imagen (si no se especifica, se genera automáticamente)

        Returns:
            Ruta al archivo de imagen generado
        """
        if output_path is None:
            os.makedirs("./output/charts", exist_ok=True)
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            output_path = f"./output/charts/chart_{timestamp}.png"

        console.print(f"[cyan]📊 Generando gráfico tipo '{chart_type}'...[/cyan]")

        try:
            fig, ax = plt.subplots(figsize=(12, 6))

            # Selección automática del tipo de gráfico si es necesario
            if chart_type == "auto":
                chart_type = self._auto_select_chart_type(data)
                console.print(f"[dim]Tipo auto-seleccionado: {chart_type}[/dim]")

            # Generar el gráfico según el tipo
            if chart_type == "bar":
                self._create_bar_chart(data, ax, title)
            elif chart_type == "line":
                self._create_line_chart(data, ax, title)
            elif chart_type == "pie":
                self._create_pie_chart(data, ax, title)
            elif chart_type == "scatter":
                self._create_scatter_chart(data, ax, title)
            elif chart_type == "heatmap":
                self._create_heatmap(data, ax, title)
            elif chart_type == "histogram":
                self._create_histogram(data, ax, title)
            else:
                raise ValueError(f"Tipo de gráfico no soportado: {chart_type}")

            plt.tight_layout()
            plt.savefig(output_path, dpi=300, bbox_inches='tight')
            plt.close()

            console.print(f"[green]✓[/green] Gráfico guardado en: {output_path}")
            return output_path

        except Exception as e:
            console.print(f"[red]✗ Error generando gráfico: {str(e)}[/red]")
            raise

    def _auto_select_chart_type(self, data: pd.DataFrame) -> str:
        """Selecciona automáticamente el mejor tipo de gráfico para los datos"""
        num_cols = len(data.select_dtypes(include=[np.number]).columns)
        num_rows = len(data)

        if num_cols >= 2:
            # Si hay 2+ columnas numéricas, usar scatter o heatmap
            if num_cols > 5:
                return "heatmap"
            return "scatter"
        elif num_cols == 1:
            # Una columna numérica
            if num_rows <= 10:
                return "bar"
            elif num_rows <= 50:
                return "line"
            else:
                return "histogram"
        else:
            # Sin columnas numéricas, usar barras
            return "bar"

    def _create_bar_chart(self, data: pd.DataFrame, ax, title: str):
        """Crea un gráfico de barras"""
        if len(data.columns) >= 2:
            x_col = data.columns[0]
            y_col = data.columns[1]
            data.plot(x=x_col, y=y_col, kind='bar', ax=ax, color='skyblue')
        else:
            data.plot(kind='bar', ax=ax, color='skyblue')

        ax.set_title(title or "Gráfico de Barras", fontsize=14, fontweight='bold')
        ax.set_xlabel(data.columns[0] if len(data.columns) > 0 else "")
        ax.set_ylabel(data.columns[1] if len(data.columns) > 1 else "Valores")
        ax.grid(axis='y', alpha=0.3)
        plt.xticks(rotation=45, ha='right')

    def _create_line_chart(self, data: pd.DataFrame, ax, title: str):
        """Crea un gráfico de líneas"""
        data.plot(kind='line', ax=ax, marker='o', linewidth=2)
        ax.set_title(title or "Gráfico de Líneas", fontsize=14, fontweight='bold')
        ax.grid(True, alpha=0.3)
        ax.legend(loc='best')

    def _create_pie_chart(self, data: pd.DataFrame, ax, title: str):
        """Crea un gráfico de pastel"""
        if len(data.columns) >= 2:
            data.set_index(data.columns[0])[data.columns[1]].plot(
                kind='pie', ax=ax, autopct='%1.1f%%', startangle=90
            )
        else:
            data[data.columns[0]].plot(kind='pie', ax=ax, autopct='%1.1f%%', startangle=90)

        ax.set_title(title or "Gráfico de Pastel", fontsize=14, fontweight='bold')
        ax.set_ylabel("")

    def _create_scatter_chart(self, data: pd.DataFrame, ax, title: str):
        """Crea un gráfico de dispersión"""
        numeric_cols = data.select_dtypes(include=[np.number]).columns
        if len(numeric_cols) >= 2:
            ax.scatter(data[numeric_cols[0]], data[numeric_cols[1]], alpha=0.6, s=100)
            ax.set_xlabel(numeric_cols[0])
            ax.set_ylabel(numeric_cols[1])
        else:
            ax.scatter(range(len(data)), data[numeric_cols[0]], alpha=0.6, s=100)
            ax.set_ylabel(numeric_cols[0])

        ax.set_title(title or "Gráfico de Dispersión", fontsize=14, fontweight='bold')
        ax.grid(True, alpha=0.3)

    def _create_heatmap(self, data: pd.DataFrame, ax, title: str):
        """Crea un mapa de calor"""
        numeric_data = data.select_dtypes(include=[np.number])
        sns.heatmap(numeric_data.corr(), annot=True, fmt='.2f', cmap='coolwarm', ax=ax)
        ax.set_title(title or "Mapa de Calor - Correlaciones", fontsize=14, fontweight='bold')

    def _create_histogram(self, data: pd.DataFrame, ax, title: str):
        """Crea un histograma"""
        numeric_cols = data.select_dtypes(include=[np.number]).columns
        if len(numeric_cols) > 0:
            data[numeric_cols[0]].plot(kind='hist', bins=30, ax=ax, color='steelblue', edgecolor='black')
            ax.set_xlabel(numeric_cols[0])
            ax.set_ylabel("Frecuencia")
        ax.set_title(title or "Histograma", fontsize=14, fontweight='bold')
        ax.grid(axis='y', alpha=0.3)

    def create_table_image(self,
                          data: pd.DataFrame,
                          title: str = "",
                          output_path: Optional[str] = None) -> str:
        """
        Crea una imagen de tabla profesional

        Args:
            data: DataFrame con los datos
            title: Título de la tabla
            output_path: Ruta donde guardar

        Returns:
            Ruta al archivo generado
        """
        if output_path is None:
            os.makedirs("./output/tables", exist_ok=True)
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            output_path = f"./output/tables/table_{timestamp}.png"

        console.print(f"[cyan]📋 Generando tabla visual...[/cyan]")

        try:
            fig, ax = plt.subplots(figsize=(14, len(data) * 0.5 + 2))
            ax.axis('tight')
            ax.axis('off')

            # Crear tabla
            table = ax.table(
                cellText=data.values,
                colLabels=data.columns,
                cellLoc='center',
                loc='center',
                colColours=['#4472C4'] * len(data.columns)
            )

            table.auto_set_font_size(False)
            table.set_fontsize(10)
            table.scale(1, 2)

            # Estilizar encabezados
            for i in range(len(data.columns)):
                table[(0, i)].set_facecolor('#4472C4')
                table[(0, i)].set_text_props(weight='bold', color='white')

            # Alternar colores en filas
            for i in range(1, len(data) + 1):
                for j in range(len(data.columns)):
                    if i % 2 == 0:
                        table[(i, j)].set_facecolor('#E7E6E6')
                    else:
                        table[(i, j)].set_facecolor('#FFFFFF')

            if title:
                plt.title(title, fontsize=16, fontweight='bold', pad=20)

            plt.tight_layout()
            plt.savefig(output_path, dpi=300, bbox_inches='tight')
            plt.close()

            console.print(f"[green]✓[/green] Tabla guardada en: {output_path}")
            return output_path

        except Exception as e:
            console.print(f"[red]✗ Error generando tabla: {str(e)}[/red]")
            raise

    def generate_infographic(self,
                           title: str,
                           data_points: List[Dict[str, Any]],
                           output_path: Optional[str] = None) -> str:
        """
        Genera una infografía simple con datos clave

        Args:
            title: Título de la infografía
            data_points: Lista de puntos de datos [{"label": "X", "value": "Y", "icon": "📊"}]
            output_path: Ruta donde guardar

        Returns:
            Ruta al archivo generado
        """
        if output_path is None:
            os.makedirs("./output/infographics", exist_ok=True)
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            output_path = f"./output/infographics/infographic_{timestamp}.png"

        console.print(f"[cyan]🎨 Generando infografía...[/cyan]")

        try:
            # Crear imagen
            width, height = 1200, 200 + len(data_points) * 150
            img = Image.new('RGB', (width, height), color='white')
            draw = ImageDraw.Draw(img)

            # Intentar cargar fuente, usar default si falla
            try:
                title_font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 48)
                label_font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 32)
                value_font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 40)
            except:
                title_font = ImageFont.load_default()
                label_font = ImageFont.load_default()
                value_font = ImageFont.load_default()

            # Título
            draw.text((width//2, 80), title, fill='#2C3E50', font=title_font, anchor='mm')

            # Línea separadora
            draw.rectangle([100, 150, width-100, 155], fill='#3498DB')

            # Puntos de datos
            y_offset = 220
            for point in data_points:
                # Fondo de la tarjeta
                draw.rectangle([100, y_offset, width-100, y_offset + 120], fill='#ECF0F1', outline='#BDC3C7', width=2)

                # Icono
                icon = point.get('icon', '📊')
                draw.text((150, y_offset + 60), icon, fill='#3498DB', font=value_font, anchor='lm')

                # Label
                label = point.get('label', '')
                draw.text((250, y_offset + 40), label, fill='#34495E', font=label_font, anchor='lm')

                # Valor
                value = str(point.get('value', ''))
                draw.text((250, y_offset + 80), value, fill='#2C3E50', font=value_font, anchor='lm')

                y_offset += 140

            img.save(output_path)
            console.print(f"[green]✓[/green] Infografía guardada en: {output_path}")
            return output_path

        except Exception as e:
            console.print(f"[red]✗ Error generando infografía: {str(e)}[/red]")
            raise

    def generate_ai_image(self,
                         prompt: str,
                         output_path: Optional[str] = None) -> Optional[str]:
        """
        Genera una imagen usando Google AI (Gemini) - Experimental

        Args:
            prompt: Descripción de la imagen a generar
            output_path: Ruta donde guardar

        Returns:
            Ruta al archivo generado o None si falla
        """
        if not self.gemini_available:
            console.print("[yellow]⚠[/yellow] Google AI no está disponible para generar imágenes")
            return None

        if output_path is None:
            os.makedirs("./output/ai_images", exist_ok=True)
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            output_path = f"./output/ai_images/ai_image_{timestamp}.png"

        console.print(f"[cyan]🎨 Generando imagen con IA...[/cyan]")
        console.print(f"[dim]Prompt: {prompt}[/dim]")

        try:
            # Nota: Gemini actualmente no soporta generación de imágenes directamente
            # Esta función es un placeholder para futuras capacidades
            console.print("[yellow]⚠[/yellow] Generación de imágenes con Gemini aún no disponible")
            console.print("[dim]Usando generación de placeholder...[/dim]")

            # Crear imagen placeholder
            img = Image.new('RGB', (800, 600), color='#ECF0F1')
            draw = ImageDraw.Draw(img)

            try:
                font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 24)
            except:
                font = ImageFont.load_default()

            # Texto del prompt envuelto
            words = prompt.split()
            lines = []
            current_line = []
            for word in words:
                current_line.append(word)
                if len(' '.join(current_line)) > 50:
                    lines.append(' '.join(current_line[:-1]))
                    current_line = [word]
            if current_line:
                lines.append(' '.join(current_line))

            y = 250
            for line in lines[:10]:
                draw.text((400, y), line, fill='#34495E', font=font, anchor='mm')
                y += 35

            img.save(output_path)
            console.print(f"[green]✓[/green] Imagen guardada en: {output_path}")
            return output_path

        except Exception as e:
            console.print(f"[red]✗ Error generando imagen: {str(e)}[/red]")
            return None

    def create_dashboard(self,
                        data: pd.DataFrame,
                        title: str = "Dashboard",
                        output_path: Optional[str] = None) -> str:
        """
        Crea un dashboard completo con múltiples visualizaciones

        Args:
            data: DataFrame con los datos
            title: Título del dashboard
            output_path: Ruta donde guardar

        Returns:
            Ruta al archivo generado
        """
        if output_path is None:
            os.makedirs("./output/dashboards", exist_ok=True)
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            output_path = f"./output/dashboards/dashboard_{timestamp}.png"

        console.print(f"[cyan]📊 Generando dashboard completo...[/cyan]")

        try:
            # Crear figura con múltiples subplots
            fig = plt.figure(figsize=(16, 10))
            fig.suptitle(title, fontsize=20, fontweight='bold')

            numeric_cols = data.select_dtypes(include=[np.number]).columns

            # Subplot 1: Resumen estadístico (tabla)
            ax1 = plt.subplot(2, 3, 1)
            ax1.axis('off')
            stats = data[numeric_cols].describe().round(2).T
            table = ax1.table(
                cellText=stats.values,
                rowLabels=stats.index,
                colLabels=stats.columns,
                cellLoc='center',
                loc='center'
            )
            table.auto_set_font_size(False)
            table.set_fontsize(8)
            ax1.set_title("Estadísticas Descriptivas", fontweight='bold')

            # Subplot 2: Gráfico de barras
            if len(numeric_cols) > 0:
                ax2 = plt.subplot(2, 3, 2)
                data[numeric_cols[0]].head(10).plot(kind='bar', ax=ax2, color='steelblue')
                ax2.set_title(f"Top 10 - {numeric_cols[0]}", fontweight='bold')
                ax2.grid(axis='y', alpha=0.3)

            # Subplot 3: Gráfico de líneas
            if len(numeric_cols) > 0:
                ax3 = plt.subplot(2, 3, 3)
                data[numeric_cols].head(20).plot(kind='line', ax=ax3, marker='o')
                ax3.set_title("Tendencias", fontweight='bold')
                ax3.grid(True, alpha=0.3)
                ax3.legend(loc='best', fontsize=8)

            # Subplot 4: Histograma
            if len(numeric_cols) > 0:
                ax4 = plt.subplot(2, 3, 4)
                data[numeric_cols[0]].plot(kind='hist', bins=20, ax=ax4, color='coral', edgecolor='black')
                ax4.set_title(f"Distribución - {numeric_cols[0]}", fontweight='bold')
                ax4.grid(axis='y', alpha=0.3)

            # Subplot 5: Box plot
            if len(numeric_cols) > 0:
                ax5 = plt.subplot(2, 3, 5)
                data[numeric_cols].plot(kind='box', ax=ax5)
                ax5.set_title("Box Plot", fontweight='bold')
                ax5.grid(axis='y', alpha=0.3)

            # Subplot 6: Correlaciones
            if len(numeric_cols) >= 2:
                ax6 = plt.subplot(2, 3, 6)
                corr = data[numeric_cols].corr()
                sns.heatmap(corr, annot=True, fmt='.2f', cmap='coolwarm', ax=ax6, cbar_kws={'shrink': 0.8})
                ax6.set_title("Matriz de Correlación", fontweight='bold')

            plt.tight_layout()
            plt.savefig(output_path, dpi=300, bbox_inches='tight')
            plt.close()

            console.print(f"[green]✓[/green] Dashboard guardado en: {output_path}")
            return output_path

        except Exception as e:
            console.print(f"[red]✗ Error generando dashboard: {str(e)}[/red]")
            raise
