#!/usr/bin/env python3
"""
Test script for OCR backend functionality with LaTeX conversion
"""
import requests
import json
import os
import sys
import base64
import subprocess
from pathlib import Path

# Backend URL
BACKEND_URL = "http://localhost:8000"

def test_health_check():
    """Test if the backend is running"""
    try:
        response = requests.get(f"{BACKEND_URL}/health")
        if response.status_code == 200:
            print("✅ Backend is healthy")
            print(f"Response: {response.json()}")
            return True
        else:
            print(f"❌ Backend health check failed: {response.status_code}")
            return False
    except requests.exceptions.ConnectionError:
        print("❌ Cannot connect to backend. Is it running on port 8000?")
        return False

def process_pdf_with_ocr(pdf_path: str, output_file: str = None):
    """Process PDF using OCR and save results to text file"""
    if not os.path.exists(pdf_path):
        print(f"❌ File not found: {pdf_path}")
        return None
    
    print(f"� Processing PDF: {pdf_path}")
    
    try:
        # Read and encode PDF file
        with open(pdf_path, 'rb') as f:
            pdf_bytes = f.read()
            pdf_base64 = base64.b64encode(pdf_bytes).decode()
        
        # Send to OCR API
        data = {"pdf_base64": pdf_base64}
        response = requests.post(f"{BACKEND_URL}/timeline/from-text", json=data)
        
        if response.status_code == 200:
            result = response.json()
            print("✅ OCR processing successful!")
            
            # Display extracted text preview
            extracted_text = result.get("extracted_text", "")
            print(f"📝 Extracted {len(extracted_text)} characters")
            print(f"🔤 First 200 characters: {extracted_text[:200]}...")
            
            # Save to output file
            output_dir = "./output/OCR"
            os.makedirs(output_dir, exist_ok=True)
            if not output_file:
                output_file = f"{output_dir}/{Path(pdf_path).stem}_extracted.txt"
            
            with open(output_file, 'w', encoding='utf-8') as f:
                f.write("=== EXTRACTED TEXT ===\n")
                f.write(extracted_text)
                f.write("\n\n=== TIMELINE DATA ===\n")
                
                timeline_data = result.get("timeline_data", [])
                for i, item in enumerate(timeline_data, 1):
                    f.write(f"\n[{i}] {item.get('content', '')}")
            
            print(f"💾 Results saved to: {output_file}")
            print(f"📊 Timeline items: {len(timeline_data)}")
            
            return output_file
            
        else:
            print(f"❌ OCR processing failed: {response.status_code}")
            print(f"Response: {response.text}")
            return None
            
    except Exception as e:
        print(f"❌ Processing error: {e}")
        return None

def test_text_input():
    """Test direct text input to timeline generation"""
    sample_text = """
    Patient visited on 2024-01-15 for chest pain.
    Blood test results from 2024-01-16 showed elevated troponin levels.
    CT scan performed on 2024-01-17 revealed no abnormalities.
    Prescribed metoprolol 25mg twice daily on 2024-01-18.
    Follow-up appointment scheduled for 2024-02-15.
    """
    
    print("📝 Testing direct text input...")
    
    # Create a fake PDF with this text (for testing purposes)
    # In reality, you would encode an actual PDF
    fake_pdf_data = sample_text.encode()
    pdf_base64 = base64.b64encode(fake_pdf_data).decode()
    
    data = {"pdf_base64": pdf_base64}
    
    try:
        response = requests.post(f"{BACKEND_URL}/timeline/from-text", json=data)
        
        if response.status_code == 200:
            result = response.json()
            print("✅ Text processing successful!")
            print(f"📝 Extracted text: {result.get('extracted_text', '')[:100]}...")
            
            # Save results
            with open("test_text_results.txt", 'w') as f:
                f.write(result.get('extracted_text', ''))
            
            return result
        else:
            print(f"❌ Text processing failed: {response.status_code}")
            print(f"Response: {response.text}")
            return None
            
    except Exception as e:
        print(f"❌ Text processing error: {e}")
        return None

def convert_text_to_latex(text_file_path: str, output_dir: str = "latex_reports"):
    """Convert OCR text file to LaTeX healthcare report"""
    
    if not os.path.exists(text_file_path):
        print(f"❌ Text file not found: {text_file_path}")
        return None
    
    try:
        # Add the LaTeX agent to path
        sys.path.append('/mnt/d/Codes/NEXTJS/LaTEX_Code_Agent')
        from ocr_to_latex import HealthCareLatexAgent
        
        # Initialize LaTeX agent
        agent = HealthCareLatexAgent()
        
        # Create output directory
        os.makedirs(output_dir, exist_ok=True)
        
        # Generate LaTeX file
        filename = Path(text_file_path).stem
        latex_output = os.path.join(output_dir, f"{filename}.tex")
        
        print(f"📄 Converting {text_file_path} to LaTeX...")
        latex_content = agent.convert_to_latex(text_file_path, latex_output)
        
        print(f"✅ LaTeX file created: {latex_output}")
        print(f"📝 LaTeX preview (first 300 chars):")
        print(latex_content[:300] + "...")
        
        return latex_output
        
    except ImportError:
        print(f"❌ Cannot import LaTeX agent. Make sure ocr_to_latex.py exists in /mnt/d/Codes/NEXTJS/LaTEX_Code_Agent/")
        return None
    except Exception as e:
        print(f"❌ LaTeX conversion failed: {str(e)}")
        return None

def compile_latex_to_pdf(tex_file: str):
    """Compile LaTeX file to PDF using pdflatex"""
    try:
        print(f"🔧 Compiling LaTeX to PDF...")
        
        # Change to the directory containing the tex file for proper compilation
        tex_dir = os.path.dirname(tex_file)
        tex_filename = os.path.basename(tex_file)
        
        result = subprocess.run(['pdflatex', '-interaction=nonstopmode', tex_filename], 
                              capture_output=True, text=True, cwd=tex_dir)
        
        if result.returncode == 0:
            pdf_file = tex_file.replace('.tex', '.pdf')
            print(f"📋 PDF compiled successfully: {pdf_file}")
            return pdf_file
        else:
            print("⚠️ PDF compilation failed:")
            print("STDOUT:", result.stdout[:500] + "..." if len(result.stdout) > 500 else result.stdout)
            print("STDERR:", result.stderr[:500] + "..." if len(result.stderr) > 500 else result.stderr)
            return None
            
    except FileNotFoundError:
        print("⚠️ pdflatex not found. Install TeX Live to compile PDF.")
        print("   On Ubuntu: sudo apt-get install texlive-latex-extra")
        print("   On macOS: brew install --cask mactex")
        print("   On Windows: Install MiKTeX or TeX Live")
        return None
    except Exception as e:
        print(f"❌ Compilation error: {str(e)}")
        return None

def process_pdf_with_latex(pdf_path: str, output_dir: str = "latex_reports", compile_pdf: bool = False):
    """Complete workflow: PDF -> OCR -> LaTeX -> (optional) PDF"""
    
    print("🚀 Starting complete PDF processing workflow...")
    print("=" * 50)
    
    # Step 1: OCR processing
    print("Step 1: OCR Processing")
    text_file = process_pdf_with_ocr(pdf_path, None)
    
    if not text_file or not os.path.exists(text_file):
        print("❌ OCR processing failed. Cannot proceed to LaTeX conversion.")
        return None
    
    # Step 2: Convert to LaTeX
    print("\nStep 2: LaTeX Conversion")
    latex_file = convert_text_to_latex(text_file, output_dir)
    
    if not latex_file:
        print("❌ LaTeX conversion failed.")
        return {"ocr_output": text_file, "latex_output": None, "pdf_output": None}
    
    # Step 3: Optional PDF compilation
    pdf_file = None
    if compile_pdf:
        print("\nStep 3: PDF Compilation")
        pdf_file = compile_latex_to_pdf(latex_file)
    
    result = {
        "ocr_output": text_file,
        "latex_output": latex_file,
        "pdf_output": pdf_file
    }
    
    print("\n🎉 Workflow completed!")
    print(f"OCR Text: {result['ocr_output']}")
    print(f"LaTeX File: {result['latex_output']}")
    if result['pdf_output']:
        print(f"PDF File: {result['pdf_output']}")
    
    return result

def main():
    """Main test function with LaTeX conversion support"""
    print("🔬 OCR Backend Test Script with LaTeX Conversion")
    print("=" * 50)
    
    # Check if backend is running
    if not test_health_check():
        print("\n💡 To start the backend, run:")
        print("cd /mnt/d/Codes/NEXTJS/OCR_Agent")
        print("python3 ocrmowa.py")
        return
    
    # Parse command line arguments
    pdf_path = None
    output_file = None
    use_latex = False
    compile_pdf = False
    
    i = 1
    while i < len(sys.argv):
        arg = sys.argv[i]
        if arg == "--latex":
            use_latex = True
        elif arg == "--compile":
            compile_pdf = True
        elif pdf_path is None:
            pdf_path = arg
        elif output_file is None:
            output_file = arg
        i += 1
    
    # Process based on arguments
    if pdf_path:
        if use_latex:
            print(f"\n🚀 Processing PDF with complete LaTeX workflow: {pdf_path}")
            result = process_pdf_with_latex(pdf_path, "latex_reports", compile_pdf)
            
            if result:
                print("\n🎉 Complete workflow finished successfully!")
                if result['pdf_output']:
                    print(f"📋 Final PDF report: {result['pdf_output']}")
            else:
                print("\n❌ Workflow failed!")
        else:
            print(f"\n📄 Processing PDF with OCR only: {pdf_path}")
            text_file = process_pdf_with_ocr(pdf_path, output_file)
            
            if text_file:
                print("\n🎉 OCR processing completed successfully!")
                print(f"💡 To convert to LaTeX, run:")
                print(f"   python test_ocr.py {pdf_path} --latex")
            else:
                print("\n❌ OCR processing failed!")
    else:
        print("\n📝 No PDF provided, testing text input instead...")
        result = test_text_input()
        
        if result:
            print("\n🎉 Text processing completed successfully!")
        else:
            print("\n❌ Text processing failed!")
    
    # Show usage help
    print("\n💡 Usage examples:")
    print("   python test_ocr.py document.pdf                    # OCR only")
    print("   python test_ocr.py document.pdf --latex            # OCR + LaTeX")
    print("   python test_ocr.py document.pdf --latex --compile  # OCR + LaTeX + PDF")

if __name__ == "__main__":
    main()
