#!/usr/bin/env python3
"""
Command-line tool to convert OCR text files to LaTeX using HealthCareLatexAgent.
Usage:
    python convert_to_latex_cli.py ./output/OCR/yourfile.txt [output_dir]
"""
import sys
import os
from pathlib import Path

# Ensure the script can import ocr_to_latex from the current directory
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from ocr_to_latex import HealthCareLatexAgent

def main():
    if len(sys.argv) < 2:
        print("Usage: python convert_to_latex_cli.py <input_txt_file> [output_dir]")
        sys.exit(1)
    
    input_file = sys.argv[1]
    output_dir = sys.argv[2] if len(sys.argv) > 2 else None
    
    if not os.path.exists(input_file):
        print(f"❌ Input file not found: {input_file}")
        sys.exit(1)
    
    agent = HealthCareLatexAgent()
    
    if output_dir:
        os.makedirs(output_dir, exist_ok=True)
        output_path = os.path.join(output_dir, f"{Path(input_file).stem}.tex")
    else:
        output_path = input_file.replace('.txt', '.tex')
    
    try:
        latex_code = agent.convert_to_latex(input_file, output_path)
        print(f"✅ LaTeX file created: {output_path}")
        print(f"📝 Preview (first 300 chars):\n{latex_code[:300]}...")
    except Exception as e:
        print(f"❌ Error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
