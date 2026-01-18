# PDF to Cornell Notes Converter 📚

Transform your PDF documents into beautifully formatted Cornell Method study notes with AI enhancement.

## Features

- **Cornell Method Formatting**: Professional two-column layout with cue questions, main notes, and summary
- **AI-Enhanced Notes**: Uses Claude AI to transform raw PDF content into structured, study-optimized notes
- **Visual Hierarchy**: Colored titles, headings, tables, and emphasis for easy scanning
- **Mixed Content Support**: Handles text, tables, and images from PDFs
- **Interactive Interface**: Beautiful command-line menu for easy operation
- **Batch Processing**: Handles long PDFs by intelligently chunking content

## What is the Cornell Method?

The Cornell Method is a note-taking system that divides the page into three sections:
1. **Cue Column (left)**: Questions and keywords that trigger recall
2. **Notes Column (right)**: Main notes with hierarchical structure
3. **Summary (bottom)**: Synthesis of key concepts

This format is proven to enhance learning and retention through active recall.

## Installation

### Prerequisites

- Python 3.8 or higher
- Anthropic API key ([get one here](https://console.anthropic.com/))

### Setup Steps

1. **Clone or download this repository**

2. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

3. **Set up your API key**:
   - Copy `.env.example` to `.env`:
     ```bash
     cp .env.example .env
     ```
   - Edit `.env` and add your Anthropic API key:
     ```
     ANTHROPIC_API_KEY=your_api_key_here
     ```

## Usage

### Interactive Mode (Recommended)

Simply run the main script:

```bash
python -m src.main
```

The interactive menu will guide you through:
1. Selecting a PDF file
2. Choosing output location
3. Converting to Cornell notes

### Example Session

```
╔═══════════════════════════════════════════════════════════════╗
║                                                               ║
║         📚 PDF to Cornell Notes Converter 📝                  ║
║                                                               ║
║   Transform PDFs into beautifully formatted study notes      ║
║   using the Cornell Method with AI enhancement               ║
║                                                               ║
╚═══════════════════════════════════════════════════════════════╝

Step 1: Select PDF File
Enter path to PDF file: my_textbook.pdf
✓ Selected: my_textbook.pdf (1,234.5 KB)

Step 2: Choose Output Location
Default: my_textbook_cornell_notes.docx
Use default output path? [y/n]: y
✓ Output: my_textbook_cornell_notes.docx

Step 3: Converting to Cornell Notes
⠋ Extracting content from PDF...
Pages     │ 15
Words     │ 8,432
Tables    │ 3
Images    │ Yes

⠋ Generating Cornell Method notes with AI...
⠋ Creating formatted DOCX file...

╭─────────────────────────────────────────────────────────────╮
│                                                             │
│ ✓ Success! Your Cornell Method notes have been created:    │
│   📄 my_textbook_cornell_notes.docx                         │
│                                                             │
│ Open the file to view your beautifully formatted notes!    │
│                                                             │
╰─────────────────────────────────────────────────────────────╯

Convert another PDF? [y/n]: n

Thank you for using Cornell Notes Converter!
Happy studying! 📚
```

## Output Format

The generated DOCX file includes:

### Title Section
- Large, colored title at the top
- Centered and prominent

### Cornell Layout (for each section)
```
┌─────────────┬────────────────────────────────┐
│             │                                │
│ Cue         │ Main Notes                     │
│ Questions:  │ • Clear hierarchical structure │
│             │ • Bullet points                │
│ • What is   │ • Tables for data              │
│   X?        │ • Definitions highlighted      │
│ • Why does  │ • Examples clearly marked      │
│   Y matter? │                                │
│             │                                │
├─────────────┴────────────────────────────────┤
│ Summary:                                     │
│ 3-5 sentences synthesizing key concepts     │
└──────────────────────────────────────────────┘
```

### Visual Elements
- **Color-coded sections**: Titles, headings, and summaries use professional blue tones
- **Tables**: Structured data with headers and clear formatting
- **Emphasis**: Key terms and definitions highlighted
- **Hierarchy**: Multiple levels of indentation and formatting

## Project Structure

```
Experiments/
├── .env                    # Your API key (create this)
├── .env.example           # Template for API key
├── requirements.txt       # Python dependencies
├── README.md             # This file
└── src/
    ├── __init__.py
    ├── main.py           # Interactive menu interface
    ├── pdf_extractor.py  # PDF content extraction
    ├── note_generator.py # Claude API integration
    ├── docx_formatter.py # Cornell Method formatting
    └── config.py         # Configuration and constants
```

## Configuration

Edit `src/config.py` to customize:
- Color scheme
- Font sizes and styles
- Cornell layout dimensions
- API settings (model, tokens, timeout)
- Prompts for AI generation

## Troubleshooting

### "API Key Not Found"
- Make sure you created a `.env` file (not `.env.example`)
- Check that your API key is correct
- Verify the `.env` file is in the project root directory

### "PDF Extraction Failed"
- Ensure the PDF is not password-protected
- Check that the file is a valid PDF
- For scanned PDFs, OCR is not currently supported

### "File Write Failed"
- Close the output file if it's open in another program
- Check you have write permissions for the output directory
- Ensure sufficient disk space

### Long Processing Time
- Large PDFs (50+ pages) take longer to process
- API calls may take 30-60 seconds for complex content
- Be patient - quality takes time!

## Tips for Best Results

1. **Use text-based PDFs**: Works best with PDFs that have selectable text
2. **Clean PDFs**: Better formatting in the source PDF leads to better notes
3. **Moderate length**: 10-30 page documents work great; very long documents are chunked
4. **Review and edit**: AI-generated notes are excellent starting points - personalize them!
5. **Print or export**: Cornell notes work great both digitally and on paper

## Dependencies

- **anthropic**: Claude API client
- **python-docx**: DOCX file creation and formatting
- **pdfplumber**: Advanced PDF content extraction
- **python-dotenv**: Environment variable management
- **rich**: Beautiful terminal user interface
- **PyPDF2**: PDF file handling
- **Pillow**: Image processing support

## License

This project is provided as-is for educational and personal use.

## Support

For issues or questions:
1. Check the Troubleshooting section above
2. Review the [Anthropic API documentation](https://docs.anthropic.com/)
3. Ensure all dependencies are correctly installed

## Acknowledgments

- Cornell Method developed by Walter Pauk at Cornell University
- Powered by Claude AI from Anthropic
- Built with Python and love for learning ❤️

---

**Happy studying!** 📚✨
