"""
Web-based interface for PDF to Learning Notes converter
Beautiful, user-friendly UI with drag-and-drop upload
"""

import os
import sys
import tempfile
import logging
from datetime import datetime
from pathlib import Path
import gradio as gr
from typing import Tuple, Optional

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s | %(levelname)s | %(message)s',
    datefmt='%H:%M:%S',
    stream=sys.stdout
)
logger = logging.getLogger(__name__)

# Fix encoding for Windows console
if sys.platform == 'win32':
    import codecs
    if hasattr(sys.stdout, 'buffer'):
        sys.stdout = codecs.getwriter('utf-8')(sys.stdout.buffer, 'strict')
    if hasattr(sys.stderr, 'buffer'):
        sys.stderr = codecs.getwriter('utf-8')(sys.stderr.buffer, 'strict')

from .pdf_extractor import PDFExtractor
from .note_generator import NoteGenerator, ImageGenerator
from .docx_formatter import create_cornell_docx
from .config import ErrorMessages, DEFAULT_OUTPUT_SUFFIX


class WebApp:
    """Web application for Learning Notes conversion"""

    def __init__(self):
        """Initialize the web app"""
        self.temp_dir = Path(tempfile.gettempdir()) / "learning_notes"
        self.temp_dir.mkdir(exist_ok=True)

    def process_pdf(
        self,
        pdf_file,
        progress=gr.Progress()
    ) -> Tuple[str, str, Optional[str]]:
        """
        Process uploaded PDF and return Cornell notes

        Args:
            pdf_file: Uploaded PDF file object
            progress: Gradio progress tracker

        Returns:
            Tuple of (status_message, details, output_file_path)
        """
        if pdf_file is None:
            return "Error", "Please upload a PDF file first.", None

        try:
            # Get the uploaded file path
            pdf_path = pdf_file.name
            pdf_filename = Path(pdf_path).stem

            logger.info(f"Processing PDF: {pdf_filename}")
            progress(0.1, desc="Reading PDF file...")

            # Step 1: Extract PDF content
            logger.info("Step 1: Extracting content from PDF...")
            progress(0.2, desc="Extracting content...")
            try:
                extractor = PDFExtractor(pdf_path)
                extractor.extract()
                structured_content = extractor.get_structured_content()
                summary = extractor.get_summary()
                logger.info(f"   Extracted {summary['total_pages']} pages, {summary['total_words']} words")

                details = f"""
Document Analysis
Pages: {summary['total_pages']}
Words: {summary['total_words']:,}
Tables: {summary['table_count']}
Images: {'Yes' if summary['has_images'] else 'No'}
"""
            except Exception as e:
                logger.error(f"   PDF extraction failed: {str(e)}")
                return (
                    "Extraction Failed",
                    f"Could not extract content from PDF.\n\nError: {str(e)}\n\n{ErrorMessages.PDF_EXTRACTION_FAILED}",
                    None
                )

            # Step 2: Generate Cornell notes with AI
            logger.info("Step 2: Generating notes...")
            progress(0.4, desc="Generating notes...")
            try:
                generator = NoteGenerator()
                notes_data = generator.generate_notes(structured_content, summary["title"])
                logger.info(f"   Generated {len(notes_data.get('sections', []))} sections")
            except ValueError as e:
                logger.error(f"   API config error: {str(e)}")
                return (
                    "Configuration Error",
                    f"API key not configured.\n\nError: {str(e)}\n\n{ErrorMessages.MISSING_API_KEY}",
                    None
                )
            except Exception as e:
                logger.error(f"   Note generation failed: {str(e)}")
                return (
                    "Generation Failed",
                    f"Could not generate notes.\n\nError: {str(e)}\n\n{ErrorMessages.API_CALL_FAILED}",
                    None
                )

            # Step 2.5: Generate images if any image items exist
            image_count = sum(
                1 for section in notes_data.get("sections", [])
                for item in section.get("content", [])
                if item.get("type") == "image"
            )

            logger.info(f"   Found {image_count} image items in notes")

            # Log all image items for debugging
            for section in notes_data.get("sections", []):
                for item in section.get("content", []):
                    if item.get("type") == "image":
                        logger.info(f"   Image item found - prompt: {item.get('prompt', 'NO PROMPT')[:50]}...")

            if image_count > 0:
                logger.info(f"Step 2.5: Generating {image_count} images...")
                progress(0.6, desc=f"Generating {image_count} images...")
                try:
                    image_generator = ImageGenerator()
                    logger.info(f"   ImageGenerator initialized, client: {image_generator.client is not None}")
                    notes_data = image_generator.process_notes_images(notes_data)
                    notes_data["_image_generator"] = image_generator

                    # Log results
                    for section in notes_data.get("sections", []):
                        for item in section.get("content", []):
                            if item.get("type") == "image":
                                logger.info(f"   Image result - path: {item.get('image_path', 'NONE')}, failed: {item.get('image_failed', False)}")
                except Exception as e:
                    logger.error(f"   Image generation EXCEPTION: {str(e)}")
                    import traceback
                    logger.error(traceback.format_exc())

            # Step 3: Create formatted DOCX
            logger.info("Step 3: Creating DOCX file...")
            progress(0.8, desc="Creating DOCX file...")
            try:
                output_filename = f"{pdf_filename}{DEFAULT_OUTPUT_SUFFIX}.docx"
                output_path = self.temp_dir / output_filename

                create_cornell_docx(notes_data, str(output_path))
                logger.info(f"   Created: {output_filename}")

                # Count generated images
                generated_images = sum(
                    1 for section in notes_data.get("sections", [])
                    for item in section.get("content", [])
                    if item.get("type") == "image" and item.get("image_path")
                )

                details += f"""

Processing Complete

Your notes have been generated with:
- Cue questions
- Main notes
- Summary
- Formatting
{f'- {generated_images} educational images' if generated_images > 0 else ''}

Sections Created: {len(notes_data.get('sections', []))}

"""

                progress(1.0, desc="Complete")
                logger.info(f"Processing complete! File saved to: {output_path}")

                return (
                    "Success",
                    details,
                    str(output_path)
                )

            except Exception as e:
                logger.error(f"   File creation failed: {str(e)}")
                return (
                    "File Creation Failed",
                    f"Could not create DOCX file.\n\nError: {str(e)}\n\n{ErrorMessages.FILE_WRITE_FAILED}",
                    None
                )

        except Exception as e:
            logger.error(f"Unexpected error: {str(e)}")
            return (
                "Unexpected Error",
                f"An unexpected error occurred:\n\n{str(e)}",
                None
            )

    def create_interface(self) -> gr.Blocks:
        """
        Create the Gradio interface with Apple-style minimalist design

        Returns:
            Gradio Blocks interface
        """
        # Apple-inspired minimalist theme using SF styles
        theme = gr.themes.Soft(
            primary_hue="blue",
            secondary_hue="slate",
            neutral_hue="slate",
            font=[gr.themes.GoogleFont("Inter"), "system-ui", "-apple-system", "sans-serif"],
        ).set(
            body_background_fill="#F5F5F7",
            layout_gap="32px",
            block_background_fill="white",
            block_border_width="0px",
            block_shadow="none",
            button_primary_background_fill="#0071E3",
            button_primary_background_fill_hover="#0077ED",
            button_primary_text_color="white",
            input_background_fill="#F5F5F7",
            input_border_color="transparent",
            input_border_width="0px",
        )

        css = """
            @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap');
            
            .container {
                max-width: 560px;
                margin: 0 auto;
                padding: 80px 24px;
                font-family: 'Inter', -apple-system, system-ui, sans-serif;
            }

            /* Content Card */
            .apple-card {
                background: white;
                border-radius: 24px;
                padding: 48px 40px;
                box-shadow: 0 2px 20px rgba(0,0,0,0.06);
            }
            
            /* Title */
            .card-title {
                font-size: 28px;
                font-weight: 600;
                letter-spacing: -0.02em;
                color: #1D1D1F;
                text-align: center;
                margin-bottom: 32px;
            }
            
            /* Drag and Drop Zone */
            .upload-zone {
                border: 1.5px dashed #C7C7CC !important;
                border-radius: 16px !important;
                background: #FAFAFA !important;
                padding: 32px !important;
                transition: all 0.2s ease !important;
            }
            .upload-zone:hover {
                border-color: #0071E3 !important;
                background: white !important;
            }
            
            /* Primary Button */
            .primary-button {
                background: #0071E3 !important;
                border: none !important;
                padding: 16px 28px !important;
                font-size: 16px !important;
                font-weight: 600 !important;
                border-radius: 12px !important;
                transition: all 0.15s ease !important;
                color: white !important;
                width: 100% !important;
                margin-top: 16px !important;
            }
            .primary-button:hover {
                background: #0077ED !important;
                transform: translateY(-1px);
                box-shadow: 0 4px 12px rgba(0,113,227,0.3);
            }
            .primary-button:active {
                transform: translateY(0);
            }

            /* Summary View */
            .summary-box {
                background: #FAFAFA;
                border-radius: 12px;
                padding: 20px;
                margin-top: 24px;
                font-size: 14px;
                color: #48484A;
                line-height: 1.6;
            }
            
            /* Download area */
            .download-area {
                margin-top: 20px;
            }

            /* Gradio Fixes */
            .gradio-container {
                background: #F5F5F7 !important;
            }
            footer { display: none !important; }
            
            /* Label styling */
            label { 
                font-weight: 500 !important; 
                color: #48484A !important;
                font-size: 14px !important;
            }
        """

        with gr.Blocks(title="Converter") as interface:
            interface.theme = theme
            interface.css = css

            with gr.Column(elem_classes=["container"]):
                
                # Card
                with gr.Group(elem_classes=["apple-card"]):
                    
                    gr.HTML('<h1 class="card-title">PDF to Cornell Notes</h1>')
                    
                    # Upload
                    pdf_input = gr.File(
                        label="Drop your document here",
                        file_types=[".pdf"],
                        file_count="single",
                        height=120,
                        elem_classes=["upload-zone"]
                    )
                    
                    # Convert Button
                    convert_btn = gr.Button(
                        "Generate Notes",
                        variant="primary",
                        elem_classes=["primary-button"]
                    )

                    # Output areas
                    status_output = gr.Textbox(visible=False)
                    details_output = gr.Markdown(visible=True, elem_classes=["summary-box"])
                    
                    # Download file
                    file_output = gr.File(
                        label="Your document is ready",
                        interactive=False,
                        visible=True,
                        elem_classes=["download-area"]
                    )

            # Execution logic
            convert_btn.click(
                fn=self.process_pdf,
                inputs=[pdf_input],
                outputs=[status_output, details_output, file_output]
            )

        return interface


def launch_app(share=False, server_name="127.0.0.1", server_port=7860):
    """
    Launch the web application

    Args:
        share: Whether to create a public link
        server_name: Server host
        server_port: Server port
    """
    app = WebApp()
    interface = app.create_interface()

    print("-" * 50)
    print("Notes Converter")
    print("-" * 50)
    print(f"Local URL: http://{server_name}:{server_port}")
    print("Press Ctrl+C to stop")
    print("-" * 50)

    # Launch the web interface
    interface.launch(
        share=share,
        server_name=server_name,
        server_port=server_port,
        theme=interface.theme,
        css=interface.css
    )


if __name__ == "__main__":
    launch_app()
