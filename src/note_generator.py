"""
Note generator module
Uses Claude API to transform PDF content into Cornell Method notes
Includes image generation with Gemini API (Imagen 3)
"""

import os
import json
import tempfile
from pathlib import Path
from typing import Dict, Optional, List
from anthropic import Anthropic
from dotenv import load_dotenv

from .config import (
    CLAUDE_MODEL, MAX_TOKENS, API_TIMEOUT,
    SYSTEM_PROMPT, USER_PROMPT_TEMPLATE,
    MAX_CONTENT_LENGTH, CHUNK_OVERLAP,
    IMAGE_MODEL, IMAGE_MAX_PER_DOCUMENT
)


class ImageGenerator:
    """Generate educational images using Google Gemini 3 Pro Image"""

    def __init__(self, api_key: Optional[str] = None):
        """
        Initialize image generator with Google Gemini API

        Args:
            api_key: Google API key (if None, loads from environment)
        """
        # Load environment variables
        project_root = Path(__file__).parent.parent
        env_path = project_root / ".env"
        load_dotenv(dotenv_path=env_path, override=True)

        self.api_key = api_key or os.getenv("GOOGLE_API_KEY")
        self.client = None
        self.temp_dir = tempfile.mkdtemp(prefix="learning_notes_images_")

        if self.api_key:
            try:
                from google import genai
                self.client = genai.Client(api_key=self.api_key)
                print("[OK] Google Gemini 3 Pro Image API inicialitzada per generacio d'imatges")
            except ImportError:
                print("[WARN] google-genai no instal-lat. Imatges deshabilitades.")
            except Exception as e:
                print(f"[WARN] Error inicialitzant Gemini: {e}. Imatges deshabilitades.")
        else:
            print("[WARN] GOOGLE_API_KEY no trobada. Generacio d'imatges deshabilitada.")

    def generate_image(self, prompt: str, index: int = 0) -> Optional[str]:
        """
        Generate an image from a text prompt using Google Gemini 3 Pro Image

        Args:
            prompt: Descriptive text prompt for image generation
            index: Index for unique filename

        Returns:
            Path to generated image file, or None if generation fails
        """
        if not self.client:
            return None

        try:
            from google.genai import types

            # Prompt in English for better Gemini understanding, but requesting Catalan text in image
            enhanced_prompt = f"Create an educational diagram image based on: {prompt}. Style: clean, professional, suitable for study notes, white background. CRITICAL REQUIREMENT: ALL text, labels, titles, and annotations inside the image MUST be written in CATALAN language (not English, not Spanish). Use Catalan words for everything visible in the image."

            print(f"[IMG] Generant imatge {index + 1} amb Gemini 3 Pro Image...")

            # Use Gemini 3 Pro Image - generates images through chat
            response = self.client.models.generate_content(
                model=IMAGE_MODEL,
                contents=enhanced_prompt,
                config=types.GenerateContentConfig(
                    response_modalities=['IMAGE', 'TEXT']
                )
            )

            # Extract image from response
            if response.candidates and response.candidates[0].content.parts:
                for part in response.candidates[0].content.parts:
                    if hasattr(part, 'inline_data') and part.inline_data:
                        # Save image to temp file
                        image_path = Path(self.temp_dir) / f"image_{index}.png"
                        image_bytes = part.inline_data.data
                        with open(image_path, 'wb') as f:
                            f.write(image_bytes)
                        print(f"[OK] Imatge {index + 1} generada: {image_path.name}")
                        return str(image_path)

            print(f"[WARN] No s'ha pogut generar la imatge {index + 1}")
            return None

        except Exception as e:
            print(f"[WARN] Error generant imatge {index + 1}: {e}")
            return None

    def process_notes_images(self, notes_data: Dict) -> Dict:
        """
        Process all image items in notes and generate actual images

        Args:
            notes_data: Notes dictionary with potential image items

        Returns:
            Updated notes dictionary with image paths
        """
        if not self.client:
            return notes_data

        image_count = 0
        sections = notes_data.get("sections", [])

        for section in sections:
            content_items = section.get("content", [])
            for item in content_items:
                if item.get("type") == "image" and image_count < IMAGE_MAX_PER_DOCUMENT:
                    prompt = item.get("prompt", "")
                    if prompt:
                        image_path = self.generate_image(prompt, image_count)
                        if image_path:
                            item["image_path"] = image_path
                            image_count += 1
                        else:
                            # Mark as failed so formatter can skip it
                            item["image_failed"] = True

        if image_count > 0:
            print(f"[IMG] Total imatges generades: {image_count}")

        return notes_data

    def cleanup(self):
        """Clean up temporary image files"""
        import shutil
        try:
            shutil.rmtree(self.temp_dir, ignore_errors=True)
        except Exception:
            pass


class NoteGenerator:
    """Generate Cornell Method notes using Claude API"""

    def __init__(self, api_key: Optional[str] = None):
        """
        Initialize note generator

        Args:
            api_key: Anthropic API key (if None, loads from environment)
        """
        # Load environment variables from project root .env file
        project_root = Path(__file__).parent.parent
        env_path = project_root / ".env"

        print(f"[KEY] Carregant clau API des de: {env_path}")
        print(f"      Fitxer existeix: {env_path.exists()}")

        # Load with override=True to ensure it takes precedence
        load_dotenv(dotenv_path=env_path, override=True)

        # Get API key
        self.api_key = api_key or os.getenv("ANTHROPIC_API_KEY")

        if self.api_key:
            print(f"[OK] Clau API trobada: {self.api_key[:20]}...")
        else:
            print(f"[ERROR] Clau API NO trobada")
            print(f"        Variables d'entorn disponibles: {list(os.environ.keys())[:10]}")
            raise ValueError("Anthropic API key not found. Please set ANTHROPIC_API_KEY in .env file")

        # Initialize client
        self.client = Anthropic(api_key=self.api_key)
        print("[OK] Client d'Anthropic inicialitzat correctament")

    def generate_notes(self, content: str, title: str = "Study Notes") -> Dict:
        """
        Generate Cornell Method notes from PDF content

        Args:
            content: Extracted PDF content
            title: Document title

        Returns:
            Structured notes dictionary
        """
        # Check content length and chunk if necessary
        if len(content) > MAX_CONTENT_LENGTH:
            return self._generate_chunked_notes(content, title)
        else:
            return self._generate_single_notes(content, title)

    def _generate_single_notes(self, content: str, title: str) -> Dict:
        """
        Generate notes for content that fits in one API call

        Args:
            content: PDF content
            title: Document title

        Returns:
            Structured notes dictionary
        """
        # Prepare prompt
        user_prompt = USER_PROMPT_TEMPLATE.format(content=content)

        try:
            # Call Claude API
            response = self.client.messages.create(
                model=CLAUDE_MODEL,
                max_tokens=MAX_TOKENS,
                system=SYSTEM_PROMPT,
                messages=[
                    {"role": "user", "content": user_prompt}
                ],
                timeout=API_TIMEOUT
            )

            # Extract response text
            response_text = response.content[0].text

            # Log response for debugging
            print(f"[OK] Resposta de la IA rebuda ({len(response_text)} caracters)")

            # Parse JSON response
            notes_data = self._parse_response(response_text)

            # Override title if provided
            if title:
                notes_data["title"] = title

            print("[OK] Notes generades correctament en CATALA")
            return notes_data

        except json.JSONDecodeError as e:
            # If JSON parsing fails, create a basic structure
            print(f"[ERROR] Error parsejant JSON de la resposta de la IA")
            print(f"        Resposta (primers 500 caracters): {response_text[:500] if 'response_text' in locals() else 'No disponible'}")
            return self._create_fallback_notes(content, title, f"JSON parse error: {str(e)}")
        except Exception as e:
            print(f"[ERROR] Error cridant la API de Claude: {str(e)}")
            # Try fallback instead of failing completely
            return self._create_fallback_notes(content, title, f"API error: {str(e)}")

    def _generate_chunked_notes(self, content: str, title: str) -> Dict:
        """
        Generate notes for long content by chunking

        Args:
            content: Long PDF content
            title: Document title

        Returns:
            Combined structured notes dictionary
        """
        # Split content into chunks
        chunks = self._chunk_content(content)

        # Process each chunk
        all_sections = []
        for chunk_idx, chunk in enumerate(chunks):
            chunk_title = f"{title} - Part {chunk_idx + 1}"
            chunk_notes = self._generate_single_notes(chunk, chunk_title)

            # Collect sections
            if chunk_notes and "sections" in chunk_notes:
                all_sections.extend(chunk_notes["sections"])

        # Create combined notes
        combined_notes = {
            "title": title,
            "sections": all_sections,
            "summary": self._generate_overall_summary(all_sections)
        }

        return combined_notes

    def _chunk_content(self, content: str) -> list:
        """
        Split long content into manageable chunks

        Args:
            content: Long text content

        Returns:
            List of content chunks
        """
        chunks = []
        start = 0

        while start < len(content):
            # Calculate end position
            end = start + MAX_CONTENT_LENGTH

            # If not at the end, try to break at a paragraph
            if end < len(content):
                # Look for paragraph break near the end
                last_break = content.rfind("\n\n", start, end)
                if last_break > start + (MAX_CONTENT_LENGTH // 2):
                    end = last_break

            # Extract chunk
            chunk = content[start:end]
            chunks.append(chunk)

            # Move start position (with overlap)
            start = end - CHUNK_OVERLAP if end < len(content) else end

        return chunks

    def _generate_overall_summary(self, sections: list) -> str:
        """
        Generate a summary from multiple sections

        Args:
            sections: List of note sections

        Returns:
            Overall summary text
        """
        # Collect main points from all sections
        main_points = []
        for section in sections:
            if "main_notes" in section and "heading" in section["main_notes"]:
                main_points.append(section["main_notes"]["heading"])

        if main_points:
            return f"This document covers: {', '.join(main_points[:5])}. " + \
                   "Key concepts and relationships are detailed in the notes above."
        else:
            return "Comprehensive notes covering the main topics from the document."

    def _parse_response(self, response_text: str) -> Dict:
        """
        Parse Claude's JSON response with robust error handling

        Args:
            response_text: Raw response text

        Returns:
            Parsed notes dictionary
        """
        # Try to find JSON in response (might have markdown code blocks)
        response_text = response_text.strip()

        # Remove markdown code blocks if present
        if response_text.startswith("```json"):
            response_text = response_text[7:]  # Remove ```json
        elif response_text.startswith("```"):
            response_text = response_text[3:]  # Remove ```

        if response_text.endswith("```"):
            response_text = response_text[:-3]  # Remove trailing ```

        response_text = response_text.strip()

        # Try direct parsing first
        try:
            notes_data = json.loads(response_text)
            if "sections" not in notes_data:
                notes_data["sections"] = []
            return notes_data
        except json.JSONDecodeError as e:
            print(f"[WARN] JSON incomplet detectat, intentant reparar...")
            
        # Try to repair truncated JSON
        repaired = self._try_repair_json(response_text)
        if repaired:
            print("[OK] JSON reparat correctament")
            return repaired
            
        # If repair failed, raise exception to trigger fallback
        raise json.JSONDecodeError("Could not parse or repair JSON", response_text, 0)

    def _try_repair_json(self, text: str) -> Optional[Dict]:
        """
        Attempt to repair truncated or malformed JSON

        Args:
            text: Potentially broken JSON string

        Returns:
            Parsed dict if successful, None otherwise
        """
        import re
        
        # Strategy 1: Find complete sections and build valid JSON
        try:
            # Look for the sections array start
            sections_match = re.search(r'"sections"\s*:\s*\[', text)
            if sections_match:
                # Find all complete section objects
                sections = []
                section_pattern = r'\{\s*"heading"\s*:\s*"[^"]*"[^}]*"content"\s*:\s*\[[^\]]*\][^}]*\}'
                
                for match in re.finditer(section_pattern, text, re.DOTALL):
                    try:
                        section = json.loads(match.group())
                        sections.append(section)
                    except:
                        continue
                
                if sections:
                    # Extract title if present
                    title_match = re.search(r'"title"\s*:\s*"([^"]*)"', text)
                    title = title_match.group(1) if title_match else "Notes"
                    
                    # Extract key_takeaways if present
                    takeaways = []
                    takeaway_match = re.search(r'"key_takeaways"\s*:\s*\[([^\]]*)\]', text)
                    if takeaway_match:
                        takeaway_items = re.findall(r'"([^"]+)"', takeaway_match.group(1))
                        takeaways = takeaway_items[:5]
                    
                    return {
                        "title": title,
                        "sections": sections,
                        "key_takeaways": takeaways if takeaways else ["Contingut processat parcialment"]
                    }
        except Exception as e:
            print(f"   Estratègia 1 fallida: {e}")
        
        # Strategy 2: Try adding closing brackets
        for suffix in [']}', '"]}', '"}]}', '"}],"key_takeaways":[]}']:
            try:
                test = text + suffix
                result = json.loads(test)
                if "sections" in result:
                    return result
            except:
                continue
        
        # Strategy 3: Try to extract just the content before the error
        try:
            # Find last complete object/array
            depth = 0
            last_valid = 0
            in_string = False
            escape_next = False
            
            for i, char in enumerate(text):
                if escape_next:
                    escape_next = False
                    continue
                if char == '\\':
                    escape_next = True
                    continue
                if char == '"' and not escape_next:
                    in_string = not in_string
                    continue
                if in_string:
                    continue
                if char in '{[':
                    depth += 1
                elif char in '}]':
                    depth -= 1
                    if depth == 0:
                        last_valid = i + 1
            
            if last_valid > 0:
                truncated = text[:last_valid]
                result = json.loads(truncated)
                if isinstance(result, dict):
                    if "sections" not in result:
                        result["sections"] = []
                    return result
        except:
            pass
        
        return None

    def _create_fallback_notes(self, content: str, title: str, error_msg: str) -> Dict:
        """
        Create basic notes structure when AI parsing fails

        Args:
            content: Original content
            title: Document title
            error_msg: Error message

        Returns:
            Basic notes structure
        """
        print(f"[WARN] AVIS: Error generant notes amb IA: {error_msg}")
        print("    Creant notes bàsiques del contingut extret...")

        # Split content into paragraphs
        paragraphs = [p.strip() for p in content.split("\n\n") if p.strip()]

        # Create basic section IN CATALAN
        section = {
            "heading": "Contingut del Document",
            "content": [
                {"type": "intro", "text": "Aquest document conté informació que no s'ha pogut processar completament amb la IA. A continuació es mostra el contingut extret del PDF.", "level": 0}
            ] + [
                {"type": "explanation", "text": para, "level": 0}
                for para in paragraphs[:20]  # Limit to first 20 paragraphs
            ] + [
                {"type": "warning", "text": f"Error en el processament automàtic: {error_msg[:100]}", "level": 0}
            ]
        }

        return {
            "title": title,
            "sections": [section],
            "key_takeaways": [
                "El contingut s'ha extret del PDF però no s'ha processat completament",
                "Revisa el contingut manualment per assegurar-ne la qualitat",
                "Considera pujar de nou el PDF o contactar amb suport si el problema persisteix"
            ]
        }


def generate_cornell_notes(content: str, title: str = "Study Notes", api_key: Optional[str] = None,
                          generate_images: bool = True, google_api_key: Optional[str] = None) -> Dict:
    """
    Convenience function to generate Cornell notes with optional image generation

    Args:
        content: PDF content
        title: Document title
        api_key: Optional Anthropic API key
        generate_images: Whether to generate images (default True)
        google_api_key: Optional Google API key for image generation

    Returns:
        Structured notes dictionary with image paths if images were generated
    """
    generator = NoteGenerator(api_key)
    notes_data = generator.generate_notes(content, title)

    # Generate images if enabled
    if generate_images:
        image_generator = ImageGenerator(google_api_key)
        notes_data = image_generator.process_notes_images(notes_data)
        # Store reference for cleanup later
        notes_data["_image_generator"] = image_generator

    return notes_data


def cleanup_images(notes_data: Dict):
    """
    Clean up temporary image files after document creation

    Args:
        notes_data: Notes dictionary that may contain image generator reference
    """
    if "_image_generator" in notes_data:
        notes_data["_image_generator"].cleanup()
        del notes_data["_image_generator"]
