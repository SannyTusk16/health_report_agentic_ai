import os
import subprocess
import shutil
from pathlib import Path

def latex_to_pdf():
    """Convert LaTeX files in ../output/latex to PDF and delete the LaTeX files."""
    
    print("🏥 Healthcare LaTeX to PDF Converter")
    print("=" * 40)
    
    latex_dir = Path("../output/latex")
    pdf_dir = Path("../output/pdf")
    
    print(f"📂 LaTeX source: {latex_dir.absolute()}")
    print(f"📂 PDF output: {pdf_dir.absolute()}")
    
    # Create PDF output directory if it doesn't exist
    pdf_dir.mkdir(parents=True, exist_ok=True)
    print(f"✅ Created output directory: {pdf_dir}")
    
    # Check if latex directory exists
    if not latex_dir.exists():
        print("❌ LaTeX directory ../output/latex does not exist")
        return
    
    # Find all .tex files
    tex_files = list(latex_dir.glob("*.tex"))
    
    if not tex_files:
        print("❌ No .tex files found in ../output/latex")
        return
    
    print(f"📄 Found {len(tex_files)} LaTeX file(s): {[f.name for f in tex_files]}")
    
    for tex_file in tex_files:
        try:
            print(f"\n🔄 Starting conversion: {tex_file.name}")
            print(f"📁 Input: {tex_file}")
            print(f"📁 Output directory: {pdf_dir}")
            
            # Run pdflatex with verbose output and interaction disabled
            command = [
                "pdflatex", 
                "-interaction=nonstopmode",  # Don't stop for errors
                "-output-directory", str(pdf_dir), 
                str(tex_file)
            ]
            
            print(f"🚀 Running command: {' '.join(command)}")
            
            # Run with real-time output
            process = subprocess.Popen(
                command,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                text=True,
                cwd=latex_dir.parent,
                bufsize=1,
                universal_newlines=True
            )
            
            # Print output in real-time
            for line in process.stdout:
                print(f"📝 {line.strip()}")
            
            process.wait()
            
            if process.returncode == 0:
                print(f"✅ Successfully converted {tex_file.name} to PDF")
                # Delete the .tex file after successful conversion
                tex_file.unlink()
                print(f"🗑️  Deleted {tex_file.name}")
            else:
                print(f"❌ Error converting {tex_file.name} (exit code: {process.returncode})")
                print("Check the output above for LaTeX errors")
                
        except FileNotFoundError:
            print("❌ pdflatex not found. Please install LaTeX (e.g., texlive)")
            return
        except Exception as e:
            print(f"❌ Error processing {tex_file.name}: {e}")
    
    # Clean up auxiliary files in PDF directory
    print("\n🧹 Cleaning up auxiliary files...")
    aux_files_removed = 0
    for ext in ["*.aux", "*.log", "*.out"]:
        for aux_file in pdf_dir.glob(ext):
            aux_file.unlink()
            aux_files_removed += 1
            print(f"🗑️  Removed: {aux_file.name}")
    
    print(f"✅ Cleanup complete! Removed {aux_files_removed} auxiliary files")
    print("🎉 LaTeX to PDF conversion finished!")

if __name__ == "__main__":
    latex_to_pdf()