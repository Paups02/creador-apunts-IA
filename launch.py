#!/usr/bin/env python3
"""
Simple launcher for Cornell Notes Converter web interface
Just run: python launch.py
"""

import sys
import os

# Fix encoding for Windows
if sys.platform == 'win32':
    import codecs
    sys.stdout = codecs.getwriter('utf-8')(sys.stdout.buffer, 'strict')
    sys.stderr = codecs.getwriter('utf-8')(sys.stderr.buffer, 'strict')

def main():
    """Launch the web interface"""
    print("=" * 70)
    print("🚀 Launching Cornell Notes Converter")
    print("=" * 70)
    print()

    # Check Gradio installation
    try:
        import gradio
        print(f"✓ Gradio {gradio.__version__} detected")
    except ImportError:
        print("⚠️  Gradio not installed. Installing now...")
        import subprocess
        subprocess.check_call([sys.executable, "-m", "pip", "install", "gradio>=4.0.0"])
        print("✓ Gradio installed")

    print()
    print("📱 Starting web server...")
    print("   Your browser should open automatically")
    print("   If not, visit: http://127.0.0.1:7861")
    print()
    print("💡 Press Ctrl+C to stop the server")
    print("=" * 70)
    print()

    # Launch the app
    from src.web_app import launch_app
    launch_app(server_port=7861)

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n👋 Server stopped. Goodbye!")
        sys.exit(0)
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
