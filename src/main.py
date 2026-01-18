"""
Main interactive menu for PDF to Learning Notes converter
"""

import os
import sys
from pathlib import Path
from rich.console import Console
from rich.panel import Panel
from rich.progress import Progress, SpinnerColumn, TextColumn
from rich.prompt import Prompt, Confirm
from rich.table import Table
from rich import box

from .pdf_extractor import PDFExtractor
from .note_generator import NoteGenerator, ImageGenerator
from .docx_formatter import create_cornell_docx
from .config import (
    WELCOME_BANNER, SUCCESS_MESSAGE_TEMPLATE,
    ErrorMessages, DEFAULT_OUTPUT_SUFFIX, DEFAULT_OUTPUT_FORMAT
)


class CornellConverterApp:
    """Interactive application for PDF to Learning Notes conversion"""

    def __init__(self):
        """Initialize the application"""
        self.console = Console()

    def run(self):
        """Main application loop"""
        self._show_welcome()

        while True:
            try:
                # Get PDF file
                pdf_path = self._get_pdf_path()
                if not pdf_path:
                    continue

                # Get output path
                output_path = self._get_output_path(pdf_path)
                if not output_path:
                    continue

                # Process the PDF
                success = self._process_pdf(pdf_path, output_path)

                if success:
                    self._show_success(output_path)

                # Ask to convert another
                if not Confirm.ask("\nConvert another PDF?", default=False):
                    break

            except KeyboardInterrupt:
                self.console.print("\n\n[yellow]Operation cancelled by user.[/yellow]")
                break
            except Exception as e:
                self.console.print(f"\n[red]Unexpected error: {str(e)}[/red]")
                if not Confirm.ask("\nTry again?", default=True):
                    break

        self._show_goodbye()

    def _show_welcome(self):
        """Display welcome banner"""
        self.console.print(Panel(
            WELCOME_BANNER,
            box=box.DOUBLE,
            style="bold blue",
            padding=(1, 2)
        ))
        self.console.print()

    def _get_pdf_path(self) -> str:
        """
        Get PDF file path from user

        Returns:
            Path to PDF file or empty string if cancelled
        """
        self.console.print("[bold cyan]Step 1: Select PDF File[/bold cyan]")

        while True:
            pdf_path = Prompt.ask("Enter path to PDF file", default="")

            if not pdf_path:
                self.console.print("[yellow]No file selected.[/yellow]")
                return ""

            # Expand user path and resolve
            pdf_path = Path(pdf_path).expanduser().resolve()

            if not pdf_path.exists():
                self.console.print(f"[red]File not found: {pdf_path}[/red]")
                if not Confirm.ask("Try another file?", default=True):
                    return ""
                continue

            if pdf_path.suffix.lower() != '.pdf':
                self.console.print("[red]File must be a PDF (.pdf extension)[/red]")
                if not Confirm.ask("Try another file?", default=True):
                    return ""
                continue

            # Show file info
            file_size = pdf_path.stat().st_size / 1024  # KB
            self.console.print(f"[green]✓[/green] Selected: {pdf_path.name} ({file_size:.1f} KB)")
            return str(pdf_path)

    def _get_output_path(self, pdf_path: str) -> str:
        """
        Get output path from user

        Args:
            pdf_path: Input PDF path

        Returns:
            Output DOCX path or empty string if cancelled
        """
        self.console.print("\n[bold cyan]Step 2: Choose Output Location[/bold cyan]")

        # Generate default output name
        pdf_file = Path(pdf_path)
        default_output = pdf_file.parent / f"{pdf_file.stem}{DEFAULT_OUTPUT_SUFFIX}{DEFAULT_OUTPUT_FORMAT}"

        self.console.print(f"[dim]Default: {default_output}[/dim]")

        # Ask user
        use_default = Confirm.ask("Use default output path?", default=True)

        if use_default:
            output_path = default_output
        else:
            custom_path = Prompt.ask("Enter output path")
            if not custom_path:
                return ""
            output_path = Path(custom_path).expanduser().resolve()

            # Ensure .docx extension
            if output_path.suffix.lower() != '.docx':
                output_path = output_path.with_suffix('.docx')

        # Check if file exists
        if output_path.exists():
            overwrite = Confirm.ask(f"[yellow]File exists: {output_path.name}[/yellow]\nOverwrite?", default=False)
            if not overwrite:
                return ""

        self.console.print(f"[green]✓[/green] Output: {output_path.name}")
        return str(output_path)

    def _process_pdf(self, pdf_path: str, output_path: str) -> bool:
        """
        Process PDF and create Cornell notes

        Args:
            pdf_path: Input PDF path
            output_path: Output DOCX path

        Returns:
            True if successful, False otherwise
        """
        self.console.print("\n[bold cyan]Step 3: Converting to Learning Notes[/bold cyan]\n")

        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            console=self.console
        ) as progress:

            # Step 1: Extract PDF content
            task1 = progress.add_task("[cyan]Extracting content from PDF...", total=None)
            try:
                extractor = PDFExtractor(pdf_path)
                extractor.extract()
                structured_content = extractor.get_structured_content()
                summary = extractor.get_summary()

                progress.update(task1, completed=True)
                self._show_pdf_summary(summary)

            except Exception as e:
                progress.update(task1, completed=True)
                self.console.print(f"\n[red]PDF extraction failed: {str(e)}[/red]")
                self.console.print(ErrorMessages.PDF_EXTRACTION_FAILED)
                return False

            # Step 2: Generate Cornell notes with AI
            task2 = progress.add_task("[cyan]Generating Deep Learning notes with AI...", total=None)
            try:
                generator = NoteGenerator()
                notes_data = generator.generate_notes(structured_content, summary["title"])
                progress.update(task2, completed=True)

            except ValueError as e:
                progress.update(task2, completed=True)
                self.console.print(f"\n[red]API configuration error: {str(e)}[/red]")
                self.console.print(ErrorMessages.MISSING_API_KEY)
                return False
            except Exception as e:
                progress.update(task2, completed=True)
                self.console.print(f"\n[red]Note generation failed: {str(e)}[/red]")
                self.console.print(ErrorMessages.API_CALL_FAILED)
                return False

            # Step 2.5: Generate images if any image items exist
            image_count = sum(
                1 for section in notes_data.get("sections", [])
                for item in section.get("content", [])
                if item.get("type") == "image"
            )

            if image_count > 0:
                task_img = progress.add_task(f"[cyan]Generating {image_count} educational images...", total=None)
                try:
                    image_generator = ImageGenerator()
                    if image_generator.client:
                        notes_data = image_generator.process_notes_images(notes_data)
                        notes_data["_image_generator"] = image_generator
                    progress.update(task_img, completed=True)
                except Exception as e:
                    progress.update(task_img, completed=True)
                    self.console.print(f"\n[yellow]Image generation warning: {str(e)}[/yellow]")
                    # Continue without images - not a fatal error

            # Step 3: Create formatted DOCX
            task3 = progress.add_task("[cyan]Creating formatted DOCX file...", total=None)
            try:
                create_cornell_docx(notes_data, output_path)
                progress.update(task3, completed=True)

            except Exception as e:
                progress.update(task3, completed=True)
                self.console.print(f"\n[red]DOCX creation failed: {str(e)}[/red]")
                self.console.print(ErrorMessages.FILE_WRITE_FAILED)
                return False

        return True

    def _show_pdf_summary(self, summary: dict):
        """
        Display PDF extraction summary

        Args:
            summary: Summary dictionary from extractor
        """
        table = Table(show_header=False, box=box.SIMPLE, padding=(0, 1))
        table.add_column("Property", style="dim")
        table.add_column("Value", style="cyan")

        table.add_row("Pages", str(summary["total_pages"]))
        table.add_row("Words", f"{summary['total_words']:,}")
        table.add_row("Tables", str(summary["table_count"]) if summary["has_tables"] else "None")
        table.add_row("Images", "Yes" if summary["has_images"] else "No")

        self.console.print(table)
        self.console.print()

    def _show_success(self, output_path: str):
        """
        Display success message

        Args:
            output_path: Path to created file
        """
        success_msg = SUCCESS_MESSAGE_TEMPLATE.format(output_path=output_path)
        self.console.print(Panel(
            success_msg,
            box=box.ROUNDED,
            style="bold green",
            padding=(1, 2)
        ))

    def _show_goodbye(self):
        """Display goodbye message"""
        self.console.print("\n[bold blue]Thank you for using Learning Notes Converter![/bold blue]")
        self.console.print("[dim]Happy studying! 📚[/dim]\n")


def main():
    """Entry point for the application"""
    app = CornellConverterApp()
    try:
        app.run()
    except Exception as e:
        console = Console()
        console.print(f"\n[red]Fatal error: {str(e)}[/red]")
        sys.exit(1)


if __name__ == "__main__":
    main()
