"""
PDF extraction module
Extracts text, tables, and structure from PDF files
"""

import pdfplumber
from pdfminer.pdfcolor import PDFColorSpace
from pathlib import Path
from typing import Dict, List, Optional
import re
import warnings

# Suppress pdfminer warnings about pattern colors
warnings.filterwarnings('ignore', message='.*invalid float value.*')
warnings.filterwarnings('ignore', message='.*gray non-stroke color.*')
warnings.filterwarnings('ignore', message='.*Pattern.*')


class PDFExtractor:
    """Extract content from PDF files with structure preservation"""

    def __init__(self, pdf_path: str):
        """
        Initialize PDF extractor

        Args:
            pdf_path: Path to the PDF file
        """
        self.pdf_path = Path(pdf_path)
        if not self.pdf_path.exists():
            raise FileNotFoundError(f"PDF file not found: {pdf_path}")

        self.content = {
            "title": "",
            "pages": [],
            "full_text": "",
            "tables": [],
            "has_tables": False
        }

    def extract(self) -> Dict:
        """
        Main extraction method

        Returns:
            Dictionary containing extracted content and metadata
        """
        try:
            # Suppress logging warnings from pdfminer about pattern colors
            import logging
            logging.getLogger('pdfminer').setLevel(logging.ERROR)
            
            # Open PDF
            with pdfplumber.open(self.pdf_path) as pdf:
                # Extract title from filename or first page
                self.content["title"] = self._extract_title(pdf)

                # Process each page with error handling
                for page_num, page in enumerate(pdf.pages, 1):
                    try:
                        page_content = self._extract_page_content(page, page_num)
                        self.content["pages"].append(page_content)
                    except Exception as e:
                        # If one page fails, skip it but continue with others
                        print(f"Warning: Could not process page {page_num}: {str(e)}")
                        # Add empty page placeholder
                        self.content["pages"].append({
                            "page_number": page_num,
                            "text": f"[Page {page_num} could not be processed due to PDF formatting issues]",
                            "tables": [],
                            "has_images": False
                        })

                # Combine all text
                self.content["full_text"] = "\n\n".join(
                    page["text"] for page in self.content["pages"] if page["text"]
                )

                # Check if document has tables
                self.content["has_tables"] = any(
                    page["tables"] for page in self.content["pages"]
                )

            return self.content

        except Exception as e:
            raise Exception(f"Failed to extract PDF content: {str(e)}")

    def _extract_title(self, pdf) -> str:
        """
        Extract document title from metadata or filename

        Args:
            pdf: pdfplumber PDF object

        Returns:
            Document title
        """
        # Try to get title from PDF metadata
        if pdf.metadata and pdf.metadata.get("Title"):
            return pdf.metadata["Title"]

        # Try to extract from first page (usually larger font)
        if pdf.pages:
            first_page = pdf.pages[0]
            # Get text from top portion of first page
            top_text = first_page.within_bbox((0, 0, first_page.width, 100)).extract_text()
            if top_text:
                # Get first non-empty line
                lines = [line.strip() for line in top_text.split('\n') if line.strip()]
                if lines:
                    return lines[0]

        # Fallback to filename
        return self.pdf_path.stem.replace('_', ' ').replace('-', ' ').title()

    def _extract_page_content(self, page, page_num: int) -> Dict:
        """
        Extract content from a single page

        Args:
            page: pdfplumber page object
            page_num: Page number

        Returns:
            Dictionary with page content
        """
        page_data = {
            "page_number": page_num,
            "text": "",
            "tables": [],
            "has_images": False
        }

        # Extract text with error handling
        try:
            text = page.extract_text(layout=False)  # layout=False avoids color issues
            if text:
                # Clean up text
                text = self._clean_text(text)
                page_data["text"] = text
        except Exception as e:
            # If text extraction fails, try without any formatting
            try:
                text = page.extract_text()
                if text:
                    page_data["text"] = self._clean_text(text)
            except:
                page_data["text"] = f"[Text extraction failed for this page]"

        # Extract tables with error handling
        try:
            tables = page.extract_tables()
            if tables:
                for table_idx, table in enumerate(tables):
                    if table:  # Skip empty tables
                        try:
                            cleaned_table = self._clean_table(table)
                            if cleaned_table:
                                page_data["tables"].append({
                                    "table_number": table_idx + 1,
                                    "data": cleaned_table
                                })
                        except:
                            # Skip problematic tables
                            pass
        except:
            # If table extraction fails completely, skip tables
            pass

        # Check for images with error handling
        try:
            if page.images:
                page_data["has_images"] = True
        except:
            pass

        return page_data

    def _clean_text(self, text: str) -> str:
        """
        Clean and normalize extracted text

        Args:
            text: Raw extracted text

        Returns:
            Cleaned text
        """
        if not text:
            return ""

        # Remove excessive whitespace
        text = re.sub(r'\s+', ' ', text)

        # Remove page numbers at end (common pattern)
        text = re.sub(r'\s+\d+\s*$', '', text)

        # Restore paragraph breaks (heuristic: sentence ending followed by capital letter)
        text = re.sub(r'([.!?])\s+([A-Z])', r'\1\n\n\2', text)

        # Clean up any multiple newlines
        text = re.sub(r'\n{3,}', '\n\n', text)

        return text.strip()

    def _clean_table(self, table: List[List[str]]) -> List[List[str]]:
        """
        Clean and validate table data

        Args:
            table: Raw table data

        Returns:
            Cleaned table data
        """
        if not table:
            return []

        cleaned = []
        for row in table:
            if row:  # Skip empty rows
                # Clean each cell
                cleaned_row = [
                    str(cell).strip() if cell is not None else ""
                    for cell in row
                ]
                # Only add row if it has at least one non-empty cell
                if any(cleaned_row):
                    cleaned.append(cleaned_row)

        return cleaned if len(cleaned) > 1 else []  # Need at least 2 rows (header + data)

    def get_structured_content(self) -> str:
        """
        Get content formatted with structure markers for better AI processing

        Returns:
            Formatted text with structure markers
        """
        if not self.content["pages"]:
            return ""

        structured_parts = [f"# {self.content['title']}\n"]

        for page in self.content["pages"]:
            if page["text"]:
                structured_parts.append(f"\n## Page {page['page_number']}\n")
                structured_parts.append(page["text"])

            # Add table information
            if page["tables"]:
                for table_info in page["tables"]:
                    structured_parts.append(f"\n### Table {table_info['table_number']}\n")
                    structured_parts.append(self._format_table_as_text(table_info["data"]))

            # Note images
            if page["has_images"]:
                structured_parts.append("\n[Note: This page contains images/diagrams]\n")

        return "\n".join(structured_parts)

    def _format_table_as_text(self, table_data: List[List[str]]) -> str:
        """
        Format table data as readable text

        Args:
            table_data: Table data

        Returns:
            Formatted table string
        """
        if not table_data:
            return ""

        # Get column widths
        col_widths = [
            max(len(str(row[i])) for row in table_data if i < len(row))
            for i in range(max(len(row) for row in table_data))
        ]

        # Format rows
        formatted_rows = []
        for row_idx, row in enumerate(table_data):
            formatted_row = " | ".join(
                str(cell).ljust(col_widths[i])
                for i, cell in enumerate(row)
            )
            formatted_rows.append(formatted_row)

            # Add separator after header
            if row_idx == 0:
                separator = "-+-".join("-" * width for width in col_widths)
                formatted_rows.append(separator)

        return "\n".join(formatted_rows)

    def get_summary(self) -> Dict:
        """
        Get summary statistics about the extracted content

        Returns:
            Dictionary with content statistics
        """
        return {
            "title": self.content["title"],
            "total_pages": len(self.content["pages"]),
            "total_characters": len(self.content["full_text"]),
            "total_words": len(self.content["full_text"].split()),
            "has_tables": self.content["has_tables"],
            "table_count": sum(len(page["tables"]) for page in self.content["pages"]),
            "has_images": any(page["has_images"] for page in self.content["pages"])
        }


def extract_pdf(pdf_path: str) -> Dict:
    """
    Convenience function to extract PDF content

    Args:
        pdf_path: Path to PDF file

    Returns:
        Extracted content dictionary
    """
    extractor = PDFExtractor(pdf_path)
    return extractor.extract()


def get_structured_text(pdf_path: str) -> str:
    """
    Convenience function to get structured text from PDF

    Args:
        pdf_path: Path to PDF file

    Returns:
        Structured text content
    """
    extractor = PDFExtractor(pdf_path)
    extractor.extract()
    return extractor.get_structured_content()
