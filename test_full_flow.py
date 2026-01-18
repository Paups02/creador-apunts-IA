# -*- coding: utf-8 -*-
"""
Test complet del flux de la web app per depurar problemes amb imatges
"""

import sys
import os

# Fix encoding for Windows
if sys.platform == 'win32':
    import codecs
    if hasattr(sys.stdout, 'buffer'):
        sys.stdout = codecs.getwriter('utf-8')(sys.stdout.buffer, 'strict')
    if hasattr(sys.stderr, 'buffer'):
        sys.stderr = codecs.getwriter('utf-8')(sys.stderr.buffer, 'strict')

# Add src to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from src.note_generator import NoteGenerator, ImageGenerator
from src.docx_formatter import create_cornell_docx
import json

def main():
    print("=" * 60)
    print("TEST COMPLET DEL FLUX DE GENERACIO DE NOTES")
    print("=" * 60)

    # Contingut de prova simple
    test_content = """
    FOTOSINTESI: El Proces Fonamental de la Vida

    La fotosintesi es el proces pel qual les plantes converteixen la llum solar en energia quimica.

    Components necessaris:
    - Llum solar (energia)
    - Diòxid de carboni (CO2)
    - Aigua (H2O)
    - Clorofil·la (pigment verd)

    Fases de la fotosintesi:
    1. Fase lluminosa: Es produeix a les membranes dels tilacoïdes
    2. Fase fosca (Cicle de Calvin): Es produeix a l'estroma

    Equacio general:
    6CO2 + 6H2O + llum → C6H12O6 + 6O2

    Importancia:
    - Produeix oxigen per a la respiracio
    - Crea glucosa per alimentar la planta
    - Base de totes les cadenes alimentaries
    """

    print("\n[STEP 1] Generant notes amb Claude API...")
    print("-" * 40)

    try:
        generator = NoteGenerator()
        notes_data = generator.generate_notes(test_content, "Fotosintesi - Notes d'Estudi")

        print(f"[OK] Notes generades!")
        print(f"     Titol: {notes_data.get('title', 'N/A')}")
        print(f"     Seccions: {len(notes_data.get('sections', []))}")

        # Comptar i mostrar items de tipus "image"
        image_items = []
        for section in notes_data.get("sections", []):
            for item in section.get("content", []):
                if item.get("type") == "image":
                    image_items.append(item)

        print(f"\n[STEP 2] Analitzant resposta de Claude...")
        print("-" * 40)
        print(f"     Items de tipus 'image': {len(image_items)}")

        if len(image_items) == 0:
            print("\n[PROBLEMA DETECTAT!]")
            print("Claude NO ha generat cap item de tipus 'image'!")
            print("Aixo significa que el prompt no esta funcionant be.")
            print("\nMostrant estructura de les notes:")
            for i, section in enumerate(notes_data.get("sections", [])):
                print(f"\n  Seccio {i+1}: {section.get('heading', 'N/A')}")
                content = section.get("content", [])
                print(f"    Items: {len(content)}")
                types = {}
                for item in content:
                    t = item.get("type", "unknown")
                    types[t] = types.get(t, 0) + 1
                print(f"    Tipus: {types}")
        else:
            print("\n[OK] Claude HA generat items de tipus 'image'!")
            for i, img in enumerate(image_items):
                print(f"\n  Imatge {i+1}:")
                print(f"    Prompt: {img.get('prompt', 'N/A')[:80]}...")
                print(f"    Caption: {img.get('caption', 'N/A')}")

            print(f"\n[STEP 3] Generant imatges amb Imagen API...")
            print("-" * 40)

            image_generator = ImageGenerator()
            print(f"     Client inicialitzat: {image_generator.client is not None}")

            if image_generator.client:
                notes_data = image_generator.process_notes_images(notes_data)

                # Verificar resultats
                generated = 0
                failed = 0
                for section in notes_data.get("sections", []):
                    for item in section.get("content", []):
                        if item.get("type") == "image":
                            if item.get("image_path"):
                                generated += 1
                                print(f"     [OK] Imatge generada: {item.get('image_path')}")
                            elif item.get("image_failed"):
                                failed += 1
                                print(f"     [FAIL] Imatge fallida")

                print(f"\n     Resultat: {generated} generades, {failed} fallides")

                if generated > 0:
                    print(f"\n[STEP 4] Creant DOCX...")
                    print("-" * 40)

                    output_path = "test_output_with_images.docx"
                    create_cornell_docx(notes_data, output_path)

                    if os.path.exists(output_path):
                        size = os.path.getsize(output_path)
                        print(f"     [OK] DOCX creat: {output_path}")
                        print(f"     Mida: {size} bytes")
                        if size > 100000:
                            print(f"     [OK] El fitxer sembla contenir imatges (>100KB)")
                        else:
                            print(f"     [WARN] El fitxer es petit, potser no te imatges")
                    else:
                        print(f"     [ERROR] El fitxer no s'ha creat!")
            else:
                print("     [ERROR] No s'ha pogut inicialitzar ImageGenerator!")
                print("     Comprova la clau GOOGLE_API_KEY al fitxer .env")

        # Guardar JSON per analisi
        with open("test_notes_output.json", "w", encoding="utf-8") as f:
            # Remove non-serializable items
            clean_data = {k: v for k, v in notes_data.items() if not k.startswith("_")}
            json.dump(clean_data, f, ensure_ascii=False, indent=2)
        print(f"\n[INFO] JSON guardat a: test_notes_output.json")

    except Exception as e:
        print(f"[ERROR] {e}")
        import traceback
        traceback.print_exc()

    print("\n" + "=" * 60)
    print("TEST COMPLETAT")
    print("=" * 60)

if __name__ == "__main__":
    main()
