# Medical Document to Report Orchestration

A sophisticated multi-agent workflow system that processes PDF medical records, synthesizes them into a coherent report using an LLM, and formats the final output as a professional PDF using LaTeX.

## 🏗️ System Architecture

The system consists of 4 specialized agents working in sequence:

1. **OCR_Agent** - Extracts text from all PDF files in the input directory
2. **Gemini_Report_Synthesizer_Agent** - Uses Google's Gemini AI to synthesize a coherent medical report
3. **LaTeX_Code_Agent** - Converts the report into professionally formatted LaTeX
4. **PDF_Compilation_Agent** - Compiles the LaTeX into a final PDF document

## 📋 Workflow Overview

```
./input/*.pdf → OCR_Agent → ./output/text.txt 
                     ↓
Gemini_Report_Synthesizer_Agent → ./output/synthesized_report.txt
                     ↓
           LaTeX_Code_Agent → ./output/latex/final_report.tex
                     ↓
        PDF_Compilation_Agent → ./output/Final_Medical_Report.pdf
```

## 🚀 Quick Start

### Prerequisites

1. **Python Environment**
   ```bash
   pip install google-generativeai
   ```

2. **LaTeX Installation**
   ```bash
   # Ubuntu/Debian
   sudo apt-get install texlive-latex-base texlive-latex-extra
   
   # macOS
   brew install mactex
   
   # Windows
   # Download and install MiKTeX from https://miktex.org/
   ```

3. **Gemini API Key**
   ```bash
   export GEMINI_API_KEY='your-gemini-api-key-here'
   ```
   Get your API key from: https://makersuite.google.com/app/apikey

### Setup

1. **Prepare Input Directory**
   ```bash
   mkdir -p ./input
   # Place your PDF medical documents in ./input/
   ```

2. **Run the Orchestrator**
   ```bash
   python test_medical_orchestrator.py
   ```

### Expected Output Structure

```
./output/
├── text.txt                    # Raw OCR text from all PDFs
├── synthesized_report.txt      # AI-generated medical report
├── Final_Medical_Report.pdf    # Final formatted PDF
├── execution_report.txt        # Workflow execution summary
├── execution_log.txt          # Detailed execution log
└── latex/
    └── final_report.tex       # LaTeX source code
```

## 🔧 Configuration

### Environment Variables

- `GEMINI_API_KEY` - Required for AI report synthesis
- `PYTHONPATH` - Should include the project directory

### Input Requirements

- **File Format**: PDF files only
- **Location**: Place all PDF files in `./input/` directory
- **Naming**: Any valid filename (will be processed in alphabetical order)

## 📊 Agent Details

### OCR_Agent
- **Input**: `./input/*.pdf`
- **Output**: `./output/text.txt`
- **Task**: Optical Character Recognition on all PDFs
- **Technology**: Uses existing OCR infrastructure (PaddleOCR/Tesseract)

### Gemini_Report_Synthesizer_Agent
- **Input**: `./output/text.txt`
- **Output**: `./output/synthesized_report.txt`
- **Task**: AI-powered synthesis into coherent medical report
- **Key Instruction**: Maintain strict chronological timeline of events
- **Technology**: Google Gemini Pro API

### LaTeX_Code_Agent
- **Input**: `./output/synthesized_report.txt`
- **Output**: `./output/latex/final_report.tex`
- **Task**: Convert to professionally formatted LaTeX document
- **Features**: Medical report template, proper escaping, metadata

### PDF_Compilation_Agent
- **Input**: `./output/latex/final_report.tex`
- **Output**: `./output/Final_Medical_Report.pdf`
- **Task**: Compile LaTeX to final PDF
- **Technology**: pdflatex with automatic cleanup

## 🔍 Monitoring and Debugging

### Execution Logs
- Real-time progress displayed in console
- Detailed logs saved to `./output/execution_log.txt`
- Execution summary in `./output/execution_report.txt`

### Error Handling
- Each agent has independent error handling
- Workflow stops if any agent fails
- Error messages included in execution report

### Common Issues

1. **No PDF files found**
   - Ensure PDFs are in `./input/` directory
   - Check file permissions

2. **Gemini API errors**
   - Verify `GEMINI_API_KEY` is set correctly
   - Check API quotas and limits

3. **LaTeX compilation errors**
   - Ensure pdflatex is installed and in PATH
   - Check for special characters in report text

## 🎯 Usage Examples

### Basic Usage
```bash
# 1. Place PDFs in input directory
cp /path/to/medical-records/*.pdf ./input/

# 2. Set API key
export GEMINI_API_KEY='your-key'

# 3. Run orchestrator
python test_medical_orchestrator.py
```

### Programmatic Usage
```python
from medical_orchestrator import MedicalDocumentOrchestrator
import asyncio

async def process_medical_documents():
    orchestrator = MedicalDocumentOrchestrator()
    results = await orchestrator.execute_workflow()
    return results

# Run the workflow
results = asyncio.run(process_medical_documents())
```

## 📁 Project Structure

```
./
├── medical_orchestrator.py         # Main orchestrator class
├── test_medical_orchestrator.py    # Test runner script
├── README.md                       # This file
├── input/                          # Place PDF files here
├── output/                         # Generated outputs
├── OCR_Agent/                      # OCR processing modules
├── LaTEX_Code_Agent/              # LaTeX conversion modules
└── PDF_Agent/                     # PDF generation modules
```

## 🚨 Important Notes

- **Data Privacy**: Ensure compliance with medical data regulations (HIPAA, etc.)
- **API Costs**: Gemini API usage incurs costs based on token consumption
- **Processing Time**: Large PDFs or many files may take several minutes
- **Dependencies**: All agents must complete successfully for final PDF generation

## 🔮 Future Enhancements

- Support for additional OCR engines
- Integration with other LLM providers
- Batch processing optimization
- Custom LaTeX templates
- Web interface for easier usage
- Docker containerization for easy deployment

## 📞 Support

For issues or questions:
1. Check the execution logs in `./output/execution_log.txt`
2. Review the error messages in the execution report
3. Ensure all prerequisites are properly installed
