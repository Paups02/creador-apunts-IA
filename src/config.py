# -*- coding: utf-8 -*-
"""
Configuration module for PDF to DOCX converter
Contains all constants, color schemes, and settings
"""

from docx.shared import RGBColor, Pt, Inches

# API CONFIGURATION
CLAUDE_MODEL = "claude-opus-4-5-20251101"
MAX_TOKENS = 16000  # Increased to prevent truncation
API_TIMEOUT = 300

# GEMINI IMAGE GENERATION CONFIGURATION
IMAGE_MODEL = "gemini-3-pro-image-preview"  # Gemini 3 Pro Image per generacio d'imatges
IMAGE_MAX_PER_DOCUMENT = 50  # Sense limit practic - Claude decideix quantes imatges cal
IMAGE_WIDTH_INCHES = 5.0  # Ample maxim de les imatges al DOCX

# CORNELL METHOD LAYOUT DIMENSIONS
CUE_COLUMN_WIDTH = Inches(2.5)
NOTES_COLUMN_WIDTH = Inches(6.0)
TABLE_TOTAL_WIDTH = Inches(8.5)

# COLOR PALETTE
class Colors:
    TITLE = RGBColor(31, 71, 136)
    HEADING = RGBColor(68, 114, 196)
    CUE_QUESTION = RGBColor(64, 64, 64)
    SUMMARY_BG = RGBColor(214, 220, 228)
    TABLE_BORDER = RGBColor(191, 191, 191)
    EMPHASIS_HIGHLIGHT = RGBColor(255, 255, 153)
    BLACK = RGBColor(0, 0, 0)
    WHITE = RGBColor(255, 255, 255)

# TYPOGRAPHY SETTINGS
class FontSizes:
    TITLE = Pt(20)
    SECTION_HEADING = Pt(14)
    MAIN_TEXT = Pt(11)
    CUE_QUESTION = Pt(10)
    SUMMARY = Pt(11)

class FontNames:
    PRIMARY = "Calibri"
    FALLBACK = "Arial"

LINE_SPACING = 1.15
SPACE_AFTER = Pt(6)
SPACE_BEFORE = Pt(0)

# PROMPT TEMPLATES
SYSTEM_PROMPT = """Ets un expert educador creant Notes d'Aprenentatge Profund.

POLÍTICA DE LLENGUA: TOT HA DE SER EN CATALÀ. Absolutament tot: text, explicacions, termes, exemples, prompts d'imatge, captions, etiquetes. ZERO paraules en anglès o castellà.

Transforma el contingut del PDF en notes clares assumint ZERO coneixement previ.

Format JSON de sortida:
{
  "title": "Títol del document",
  "sections": [
    {
      "heading": "Títol de la Secció",
      "content": [
        {"type": "intro", "text": "Introducció en català", "level": 0},
        {"type": "explanation", "text": "Explicació detallada en català", "level": 1},
        {"type": "definition", "text": "Terme: Definició clara en català", "level": 1},
        {"type": "example", "text": "Exemple concret en català", "level": 1},
        {"type": "analogy", "text": "Analogia del món real en català", "level": 1},
        {"type": "bullet", "text": "Punt clau en català", "level": 1},
        {"type": "connection", "text": "Com es relacionen els conceptes en català", "level": 1},
        {"type": "warning", "text": "Error comú a evitar en català", "level": 1},
        {"type": "tldr", "text": "Resum ràpid en català", "level": 1},
        {"type": "table", "headers": ["Columna1", "Columna2"], "rows": [["dada1", "dada2"]], "level": 1},
        {"type": "image", "prompt": "Descripció MOLT detallada EN CATALÀ del que ha de mostrar la imatge", "caption": "Peu de foto en català", "level": 1}
      ]
    }
  ],
  "key_takeaways": ["Punt 1 en català", "Punt 2 en català", "Punt 3 en català"]
}

TAULES: Només afegeix taules (type: "table") quan realment aportin valor per comparar conceptes,
mostrar dades, o organitzar informació de forma més clara.

IMATGES - TU DECIDEIXES:
- Afegeix TANTES imatges com consideris NECESSÀRIES per facilitar la comprensió
- No hi ha límit màxim ni mínim - usa el teu criteri d'expert educador
- Posa imatges allà on siguin CLAU per entendre el contingut:
  * Processos amb passos seqüencials (diagrames de flux, cicles)
  * Estructures complexes (anatomia, arquitectura de sistemes)
  * Comparacions visuals (abans/després, diferències entre conceptes)
  * Conceptes abstractes que es beneficien de visualització
  * Relacions entre elements (mapes conceptuals, jerarquies)
  * Qualsevol concepte difícil d'entendre només amb text

PROMPT DE LA IMATGE (CATALÀ OBLIGATORI):
- El "prompt" ha de ser 100% EN CATALÀ, molt descriptiu
- Especifica l'estil: "diagrama educatiu", "diagrama de flux", "infografia"
- Indica que les ETIQUETES i TEXT dins la imatge han de ser EN CATALÀ
- El "caption" també en CATALÀ

RECORDA: Ets un expert. Si el contingut necessita 10 imatges, posa 10. Si en necessita 1, posa 1."""

USER_PROMPT_TEMPLATE = """Transforma aquest PDF en Notes d'Aprenentatge Profund assumint ZERO coneixement previ.

POLÍTICA ESTRICTA: TOT EN CATALÀ. Absolutament res en anglès ni castellà.

REQUISITS:
1. Explica-ho tot des de zero EN CATALÀ
2. Defineix TOTS els termes tècnics EN CATALÀ
3. Usa exemples, analogies, connexions EN CATALÀ
4. Inclou avisos sobre errors comuns EN CATALÀ
5. Afegeix resums TL;DR EN CATALÀ
6. Crea 3-5 punts clau EN CATALÀ
7. TAULES: Només quan aportin valor real
8. IMATGES - TU DECIDEIXES:
   - Afegeix TANTES imatges com siguin NECESSÀRIES per entendre el contingut
   - SENSE LÍMIT - posa les que facin falta segons el teu criteri expert
   - El "prompt" HA DE SER 100% EN CATALÀ
   - Les etiquetes i text DINS la imatge EN CATALÀ
   - El "caption" EN CATALÀ
   - Posa imatges allà on siguin clau per la comprensió

Fes aquestes notes tan clares que algú sense cap coneixement pugui aprendre 100x més ràpid!

Contingut del PDF:
{content}

Sortida en format JSON amb TOT EN CATALÀ (incloent prompts d'imatge, etiquetes, tot)."""

# ERROR MESSAGES
class ErrorMessages:
    MISSING_API_KEY = "[ERROR] API Key Not Found - Create .env file with ANTHROPIC_API_KEY"
    PDF_EXTRACTION_FAILED = "[ERROR] PDF Extraction Failed - Check if PDF is valid"
    API_CALL_FAILED = "[ERROR] API Call Failed - Check API key and connection"
    FILE_WRITE_FAILED = "[ERROR] File Write Failed - Close open documents"
    INVALID_PDF_PATH = "[ERROR] Invalid PDF Path"

# PDF PROCESSING
MAX_CONTENT_LENGTH = 50000
CHUNK_OVERLAP = 1000
HEADING_FONT_THRESHOLD = 1.2

# OUTPUT SETTINGS
DEFAULT_OUTPUT_SUFFIX = "_learning_notes"
DEFAULT_OUTPUT_FORMAT = ".docx"

# CONSOLE STYLING
WELCOME_BANNER = """
PDF to Deep Learning Notes Converter
Transform PDFs into comprehensive study notes with AI
"""

SUCCESS_MESSAGE_TEMPLATE = "[OK] Success! Notes created: {output_path}"
