#!/usr/bin/env python3
"""
Test script for the Medical Document to Report Orchestration workflow
"""

import asyncio
import os
import sys
from pathlib import Path

# Add the current directory to Python path
sys.path.append('.')

# Import the orchestrator
from medical_orchestrator import MedicalDocumentOrchestrator

def setup_test_environment():
    """Set up test environment and check requirements."""
    print("🔧 Setting up test environment...")
    
    # Check if input directory exists and has PDFs
    input_dir = Path("./input")
    if not input_dir.exists():
        input_dir.mkdir(parents=True, exist_ok=True)
        print(f"📁 Created input directory: {input_dir}")
    
    pdf_files = list(input_dir.glob("*.pdf"))
    print(f"📄 Found {len(pdf_files)} PDF files in input directory")
    
    if not pdf_files:
        print("⚠️  Warning: No PDF files found in ./input/ directory")
        print("   Please add PDF files to ./input/ before running the workflow")
        return False
    
    # Check for Gemini API key
    api_key = os.getenv('GEMINI_API_KEY')
    if not api_key:
        print("⚠️  Warning: GEMINI_API_KEY environment variable not set")
        print("   The Gemini synthesis step will fail without this")
        print("   Set it with: export GEMINI_API_KEY='your-api-key'")
    else:
        print("✅ Gemini API key found")
    
    # Check for pdflatex
    import subprocess
    try:
        result = subprocess.run(['pdflatex', '--version'], capture_output=True)
        if result.returncode == 0:
            print("✅ pdflatex found")
        else:
            print("⚠️  Warning: pdflatex not working properly")
    except FileNotFoundError:
        print("⚠️  Warning: pdflatex not found")
        print("   Install with: sudo apt-get install texlive-latex-base texlive-latex-extra")
    
    return True

async def run_test():
    """Run the medical document orchestration test."""
    print("🚀 Starting Medical Document to Report Orchestration Test")
    print("=" * 70)
    
    # Setup environment
    if not setup_test_environment():
        print("\n❌ Test environment setup incomplete")
        print("Please address the warnings above and try again")
        return
    
    print("\n🎯 Initializing orchestrator...")
    orchestrator = MedicalDocumentOrchestrator()
    
    print("🔄 Executing workflow...")
    results = await orchestrator.execute_workflow()
    
    print("\n📊 Generating final report...")
    report = orchestrator.generate_execution_report(results)
    
    # Save reports
    with open("./output/execution_report.txt", "w") as f:
        f.write(report)
    
    with open("./output/execution_log.txt", "w") as f:
        f.write("\n".join(orchestrator.execution_log))
    
    print("\n" + "=" * 70)
    print("📋 FINAL EXECUTION REPORT")
    print("=" * 70)
    print(report)
    
    # Check final output
    final_pdf = Path("./output/Final_Medical_Report.pdf")
    if final_pdf.exists():
        print(f"\n✅ SUCCESS! Final medical report generated: {final_pdf}")
        print(f"📊 File size: {final_pdf.stat().st_size} bytes")
    else:
        print(f"\n❌ Final PDF not generated. Check execution log for errors.")
    
    print("\n📁 Output files:")
    output_dir = Path("./output")
    for file in output_dir.rglob("*"):
        if file.is_file():
            print(f"   {file}")

def main():
    """Main function to run the test."""
    try:
        asyncio.run(run_test())
    except KeyboardInterrupt:
        print("\n\n⏹️  Test interrupted by user")
    except Exception as e:
        print(f"\n❌ Test failed with error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
