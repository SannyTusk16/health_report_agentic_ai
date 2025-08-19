#!/usr/bin/env python3
"""
Medical Document to Report Orchestration
A multi-agent workflow to process PDF medical records, synthesize them into a coherent report using an LLM,
and format the final output as a PDF using LaTeX.
"""

import asyncio
import os
import json
import subprocess
import time
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional
from dataclasses import dataclass, asdict
from enum import Enum

# Load environment variables
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    print("⚠️  python-dotenv not installed. Environment variables will be read from system.")
    pass

try:
    import google.generativeai as genai
except ImportError:
    print("⚠️  Warning: google-generativeai not installed. Install with: pip install google-generativeai")
    genai = None

class AgentStatus(Enum):
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"

@dataclass
class AgentResult:
    agent_name: str
    status: AgentStatus
    input_path: str
    output_path: str
    execution_time: float
    error_message: Optional[str] = None
    metadata: Optional[Dict] = None

from dotenv import load_dotenv

load_dotenv()

class MedicalDocumentOrchestrator:
    def __init__(self):
        self.agents = {}
        self.execution_log = []
        self.setup_directories()
        
        # Load configuration from environment
        self.config = self.load_configuration()
        
        # Configure Gemini API
        api_key = os.getenv("GEMINI_API_KEY")
        if api_key and api_key != 'your-gemini-api-key-here' and genai:
            genai.configure(api_key=api_key)
            self.gemini_model = genai.GenerativeModel('gemini-2.0-flash')
            self.log_execution("Gemini API configured successfully")
        else:
            if not genai:
                self.log_execution("⚠️  Warning: google-generativeai package not available")
            else:
                self.log_execution("⚠️  Warning: GEMINI_API_KEY not configured properly")
            self.gemini_model = None
    
    def load_configuration(self) -> Dict[str, str]:
        """Load configuration from environment variables with defaults."""
        config = {
            'GEMINI_API_KEY': os.getenv('GEMINI_API_KEY', ''),
            'TESSERACT_PATH': os.getenv('TESSERACT_PATH', '/usr/bin/tesseract'),
            'PADDLEOCR_LANG': os.getenv('PADDLEOCR_LANG', 'en'),
            'PDFLATEX_PATH': os.getenv('PDFLATEX_PATH', 'pdflatex'),
            'LOG_LEVEL': os.getenv('LOG_LEVEL', 'INFO'),
            'LOG_FILE': os.getenv('LOG_FILE', './output/orchestrator.log'),
            'MAX_PDF_SIZE_MB': int(os.getenv('MAX_PDF_SIZE_MB', '50')),
            'PROCESSING_TIMEOUT_SECONDS': int(os.getenv('PROCESSING_TIMEOUT_SECONDS', '300')),
        }
        return config
    
    def setup_directories(self):
        """Create necessary directories for the workflow."""
        directories = [
            "./input",
            "./output", 
            "./output/latex"
        ]
        for directory in directories:
            Path(directory).mkdir(parents=True, exist_ok=True)
    
    def log_execution(self, message: str, agent_name: str = "ORCHESTRATOR"):
        """Log execution messages with timestamps."""
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        log_entry = f"[{timestamp}] {agent_name}: {message}"
        self.execution_log.append(log_entry)
        print(log_entry)
    
    async def execute_ocr_agent(self) -> AgentResult:
        """
        OCR_Agent: Perform Optical Character Recognition on all PDF files in ./input/
        """
        agent_name = "OCR_Agent"
        start_time = time.time()
        
        self.log_execution("Starting OCR extraction from ./input/ directory", agent_name)
        
        try:
            input_dir = Path("./input")
            output_file = Path("./output/text.txt")
            
            # Find all PDF files
            pdf_files = list(input_dir.glob("*.pdf"))
            
            # Check if there are existing OCR files to use
            ocr_dir = Path("./output/OCR")
            existing_ocr_files = list(ocr_dir.glob("*.txt")) if ocr_dir.exists() else []
            
            if not pdf_files and not existing_ocr_files:
                raise Exception("No PDF files found in ./input/ directory and no existing OCR files in ./output/OCR/")
            
            self.log_execution(f"Found {len(pdf_files)} PDF files and {len(existing_ocr_files)} existing OCR files", agent_name)
            
            # Clear the output file
            if output_file.exists():
                output_file.unlink()
            
            # Check if there are existing OCR files to use
            ocr_dir = Path("./output/OCR")
            existing_ocr_files = list(ocr_dir.glob("*.txt")) if ocr_dir.exists() else []
            
            all_extracted_text = []
            
            if existing_ocr_files:
                self.log_execution(f"Found {len(existing_ocr_files)} existing OCR files to consolidate", agent_name)
                
                # Use existing OCR files
                for ocr_file in existing_ocr_files:
                    self.log_execution(f"Reading existing OCR file: {ocr_file.name}", agent_name)
                    
                    with open(ocr_file, 'r', encoding='utf-8') as f:
                        extracted_text = f.read()
                    
                    # Add file separator and metadata
                    separator = "\n" + "="*80 + "\n"
                    file_header = f"SOURCE FILE: {ocr_file.name}\nEXTRACTED: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n"
                    all_extracted_text.append(f"{separator}{file_header}{separator}\n{extracted_text}\n")
                    
                    self.log_execution(f"Successfully read OCR text from {ocr_file.name}", agent_name)
            else:
                # Process PDF files with OCR
                for i, pdf_file in enumerate(pdf_files, 1):
                    self.log_execution(f"Processing PDF {i}/{len(pdf_files)}: {pdf_file.name}", agent_name)
                    
                    # Use the existing OCR test script
                    result = subprocess.run([
                        "python", "OCR_Agent/test_ocr.py", str(pdf_file)
                    ], capture_output=True, text=True, cwd=".")
                    
                    if result.returncode == 0:
                        # Read the extracted text from OCR output
                        ocr_output_files = list(Path("./output/OCR").glob(f"{pdf_file.stem}*.txt"))
                        if ocr_output_files:
                            with open(ocr_output_files[0], 'r', encoding='utf-8') as f:
                                extracted_text = f.read()
                            
                            # Add file separator and metadata
                            separator = "\n" + "="*80 + "\n"
                            file_header = f"SOURCE FILE: {pdf_file.name}\nEXTRACTED: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n"
                            all_extracted_text.append(f"{separator}{file_header}{separator}\n{extracted_text}\n")
                            
                            self.log_execution(f"Successfully extracted text from {pdf_file.name}", agent_name)
                        else:
                            self.log_execution(f"Warning: No OCR output found for {pdf_file.name}", agent_name)
                    else:
                        self.log_execution(f"Error processing {pdf_file.name}: {result.stderr}", agent_name)
            
            # Write concatenated text to output file
            final_text = "\n".join(all_extracted_text)
            with open(output_file, 'w', encoding='utf-8') as f:
                f.write(final_text)
            
            execution_time = time.time() - start_time
            self.log_execution(f"OCR processing completed. Output saved to {output_file}", agent_name)
            
            total_files = len(pdf_files) + len(existing_ocr_files)
            return AgentResult(
                agent_name=agent_name,
                status=AgentStatus.COMPLETED,
                input_path="./input/",
                output_path=str(output_file),
                execution_time=execution_time,
                metadata={"processed_files": total_files, "output_size": len(final_text)}
            )
            
        except Exception as e:
            execution_time = time.time() - start_time
            self.log_execution(f"OCR processing failed: {str(e)}", agent_name)
            
            return AgentResult(
                agent_name=agent_name,
                status=AgentStatus.FAILED,
                input_path="./input/",
                output_path="./output/text.txt",
                execution_time=execution_time,
                error_message=str(e)
            )
    
    async def execute_gemini_synthesizer_agent(self) -> AgentResult:
        """
        Gemini_Report_Synthesizer_Agent: Analyze OCR text and compile into coherent medical report
        """
        agent_name = "Gemini_Report_Synthesizer_Agent"
        start_time = time.time()
        
        self.log_execution("Starting report synthesis using Gemini API", agent_name)
        
        try:
            input_file = Path("./output/text.txt")
            output_file = Path("./output/synthesized_report.txt")
            
            if not input_file.exists():
                raise Exception("Input file ./output/text.txt not found")
            
            # Read the OCR text
            with open(input_file, 'r', encoding='utf-8') as f:
                ocr_text = f.read()
            
            if not ocr_text.strip():
                raise Exception("OCR text file is empty")
            
            self.log_execution(f"Read {len(ocr_text)} characters of OCR text", agent_name)
            
            # Prepare the prompt
            prompt = """You are an expert medical scribe. Your task is to synthesize the provided text, which has been extracted from multiple medical documents, into a single, well-structured medical report. 

It is critical that you preserve the exact timeline of events as they occurred. Organize the information chronologically, detailing patient history, consultations, diagnoses, procedures, and outcomes in the order they happened. 

Do not infer information not present in the text. 

**IMPORTANT FORMATTING REQUIREMENTS:**
Please format your output using the following structure with exact markdown-style headers:

**SECTION 1: PATIENT PARTICULARS**
[Patient demographic and contact information]

**SECTION 2: DOCTOR PARTICULARS** 
[Doctor information and credentials]

**SECTION 3: MEDICAL HISTORY**
[Chronological medical history and background]

**SECTION 4: CLINICAL EXAMINATION**
[Physical examination findings and assessments]

**SECTION 5: DIAGNOSIS**
[Medical diagnoses and clinical impressions]

**SECTION 6: TREATMENT AND RECOMMENDATIONS**
[Treatment plans, medications, and recommendations]

**SECTION 7: MENTAL CAPACITY ASSESSMENT** (if applicable)
[Mental capacity evaluation details]

Use bullet points (*) for lists and maintain chronological order within each section.

Here is the extracted text from multiple medical documents:

""" + ocr_text
            
            # Use Gemini to synthesize the report
            if not self.gemini_model:
                raise Exception("Gemini API not configured. Please set GEMINI_API_KEY environment variable.")
            
            self.log_execution("Sending request to Gemini API for report synthesis", agent_name)
            
            response = self.gemini_model.generate_content(prompt)
            synthesized_report = response.text
            
            # Save the synthesized report
            with open(output_file, 'w', encoding='utf-8') as f:
                f.write(synthesized_report)
            
            execution_time = time.time() - start_time
            self.log_execution(f"Report synthesis completed. Output saved to {output_file}", agent_name)
            
            return AgentResult(
                agent_name=agent_name,
                status=AgentStatus.COMPLETED,
                input_path=str(input_file),
                output_path=str(output_file),
                execution_time=execution_time,
                metadata={"input_size": len(ocr_text), "output_size": len(synthesized_report)}
            )
            
        except Exception as e:
            execution_time = time.time() - start_time
            self.log_execution(f"Report synthesis failed: {str(e)}", agent_name)
            
            return AgentResult(
                agent_name=agent_name,
                status=AgentStatus.FAILED,
                input_path="./output/text.txt",
                output_path="./output/synthesized_report.txt",
                execution_time=execution_time,
                error_message=str(e)
            )
    
    async def execute_latex_code_agent(self) -> AgentResult:
        """
        LaTeX_Code_Agent: Convert synthesized report text into professionally formatted LaTeX
        """
        agent_name = "LaTeX_Code_Agent"
        start_time = time.time()
        
        self.log_execution("Starting LaTeX conversion", agent_name)
        
        try:
            input_file = Path("./output/synthesized_report.txt")
            output_file = Path("./output/latex/final_report.tex")
            
            if not input_file.exists():
                raise Exception("Input file ./output/synthesized_report.txt not found")
            
            # Read the synthesized report
            with open(input_file, 'r', encoding='utf-8') as f:
                report_text = f.read()
            
            self.log_execution(f"Converting {len(report_text)} characters to LaTeX", agent_name)
            
            # Create LaTeX document
            latex_content = self.create_medical_report_latex(report_text)
            
            # Save LaTeX file
            with open(output_file, 'w', encoding='utf-8') as f:
                f.write(latex_content)
            
            execution_time = time.time() - start_time
            self.log_execution(f"LaTeX conversion completed. Output saved to {output_file}", agent_name)
            
            return AgentResult(
                agent_name=agent_name,
                status=AgentStatus.COMPLETED,
                input_path=str(input_file),
                output_path=str(output_file),
                execution_time=execution_time,
                metadata={"input_size": len(report_text), "latex_size": len(latex_content)}
            )
            
        except Exception as e:
            execution_time = time.time() - start_time
            self.log_execution(f"LaTeX conversion failed: {str(e)}", agent_name)
            
            return AgentResult(
                agent_name=agent_name,
                status=AgentStatus.FAILED,
                input_path="./output/synthesized_report.txt",
                output_path="./output/latex/final_report.tex",
                execution_time=execution_time,
                error_message=str(e)
            )
    
    def create_medical_report_latex(self, report_text: str) -> str:
        """Create professional LaTeX document for medical report."""
        
        # Escape LaTeX special characters with better handling
        def escape_latex(text):
            latex_chars = {
                '&': r'\&', '%': r'\%', '$': r'\$', '#': r'\#',
                '^': r'\^{}', '_': r'\_', '{': r'\{', '}': r'\}',
                '~': r'\~{}', '\\': r'\textbackslash{}'
            }
            for char, replacement in latex_chars.items():
                text = text.replace(char, replacement)
            
            # Only apply breaking to truly problematic sequences
            import re
            # Only NRIC numbers (S1234567A format) - these need breaking
            text = re.sub(r'\b([STG]\d{7}[A-Z])\b', r'\\seqsplit{\1}', text)
            # Only very long unbroken number sequences (10+ digits)
            text = re.sub(r'\b(\d{10,})\b', r'\\seqsplit{\1}', text)
            
            return text
        
        # Process and structure the content
        def format_medical_content(text):
            lines = text.split('\n')
            formatted_lines = []
            skip_first_header = True  # Skip the initial "MEDICAL REPORT" header
            in_itemize = False
            
            for line in lines:
                line = line.strip()
                if not line:
                    # Close itemize if we hit empty line
                    if in_itemize:
                        formatted_lines.append("\\end{itemize}")
                        in_itemize = False
                    continue
                
                # Skip the first "MEDICAL REPORT" header as it's redundant
                if skip_first_header and line.upper().strip() == "MEDICAL REPORT":
                    skip_first_header = False
                    continue
                
                # Convert structured markdown sections to LaTeX sections
                if line.startswith('**SECTION') and line.endswith('**'):
                    # Close any open itemize before starting new section
                    if in_itemize:
                        formatted_lines.append("\\end{itemize}")
                        in_itemize = False
                    # Extract section text and create LaTeX section
                    section_text = line.strip('*').strip()
                    formatted_lines.append(f"\\section{{{escape_latex(section_text)}}}")
                elif line.startswith('**') and line.endswith('**') and len(line) > 4:
                    # Close any open itemize before starting subsection
                    if in_itemize:
                        formatted_lines.append("\\end{itemize}")
                        in_itemize = False
                    # Bold subsections for other ** headers
                    subsection_text = line.strip('*').strip()
                    formatted_lines.append(f"\\subsection{{{escape_latex(subsection_text)}}}")
                elif line.startswith('*') and not line.startswith('**'):
                    # Handle bullet points
                    if not in_itemize:
                        formatted_lines.append("\\begin{itemize}")
                        in_itemize = True
                    
                    content = line[1:].strip()  # Remove leading *
                    if ':' in content and len(content.split(':')) == 2:
                        # Key-value bullet points
                        key, value = content.split(':', 1)
                        key_clean = escape_latex(key.strip())
                        value_clean = escape_latex(value.strip())
                        formatted_lines.append(f"\\item \\textbf{{{key_clean}:}} {value_clean}")
                    else:
                        # Simple bullet points
                        formatted_lines.append(f"\\item {escape_latex(content)}")
                elif ':' in line and len(line.split(':')) == 2 and not line.startswith('*'):
                    # Close any open itemize before key-value pairs
                    if in_itemize:
                        formatted_lines.append("\\end{itemize}")
                        in_itemize = False
                    # Format key-value pairs with proper line breaking
                    key, value = line.split(':', 1)
                    key_clean = escape_latex(key.strip())
                    value_clean = escape_latex(value.strip())
                    # Use parbox for better text wrapping on long values
                    if len(value_clean) > 60:
                        formatted_lines.append(f"\\noindent\\textbf{{{key_clean}:}} \\\\")
                        formatted_lines.append(f"\\parbox{{\\textwidth}}{{{value_clean}}}")
                    else:
                        formatted_lines.append(f"\\textbf{{{key_clean}:}} {value_clean}")
                else:
                    # Close any open itemize before regular text
                    if in_itemize:
                        formatted_lines.append("\\end{itemize}")
                        in_itemize = False
                    # Regular paragraph text with proper wrapping
                    escaped_line = escape_latex(line)
                    formatted_lines.append(escaped_line)
                
                formatted_lines.append('')  # Add spacing
            
            # Close any remaining itemize
            if in_itemize:
                formatted_lines.append("\\end{itemize}")
            
            return '\n'.join(formatted_lines)
        
        formatted_content = format_medical_content(report_text)
        
        latex_template = r'''\documentclass[11pt,a4paper]{article}
\usepackage[utf8]{inputenc}
\usepackage[margin=1in]{geometry}
\usepackage{fancyhdr}
\usepackage{graphicx}
\usepackage{tabularx}
\usepackage{booktabs}
\usepackage{enumitem}
\usepackage{url}
\usepackage{hyperref}
\usepackage{xcolor}
\usepackage{tcolorbox}
\usepackage{microtype}
\usepackage{ragged2e}

% Better text wrapping and overflow handling
\setlength{\emergencystretch}{3em}
\tolerance=1000
\hbadness=10000

% Header settings
\setlength{\headheight}{15pt}
\pagestyle{fancy}
\fancyhf{}
\rhead{\thepage}
\lhead{Synthesized Medical Report}

% Better line breaking
\hyphenpenalty=50
\exhyphenpenalty=50

% Define seqsplit for very specific cases
\makeatletter
\newcommand{\seqsplit}[1]{%
  \def\@tempa##1{\ifx\relax##1\relax\else##1\discretionary{}{}{}\expandafter\@tempa\fi}%
  \@tempa#1\relax%
}
\makeatother

% Custom itemize environment for better spacing
\setlist[itemize]{leftmargin=20pt, itemsep=2pt, parsep=0pt, topsep=5pt}

\title{Synthesized Medical Report}
\author{Medical Document Processing System}
\date{\today}

\begin{document}
\maketitle

\begin{abstract}
This document contains a synthesized medical report generated from multiple source documents using automated processing. The report maintains chronological order and preserves all relevant medical information from the source materials.
\end{abstract}

\tableofcontents
\newpage

''' + formatted_content + r'''

\vspace{2cm}

\noindent\rule{\textwidth}{0.5pt}
\begin{center}
\textit{This report was automatically generated from multiple medical documents}\\
\textit{Generated on: ''' + datetime.now().strftime("%Y-%m-%d %H:%M:%S") + r'''}
\end{center}

\end{document}'''
        
        return latex_template
    
    async def execute_pdf_compilation_agent(self) -> AgentResult:
        """
        PDF_Compilation_Agent: Compile LaTeX file into final PDF document
        """
        agent_name = "PDF_Compilation_Agent"
        start_time = time.time()
        
        self.log_execution("Starting PDF compilation", agent_name)
        
        try:
            input_file = Path("./output/latex/final_report.tex")
            output_file = Path("./output/Final_Medical_Report.pdf")
            
            if not input_file.exists():
                raise Exception("Input file ./output/latex/final_report.tex not found")
            
            self.log_execution("Compiling LaTeX to PDF using pdflatex", agent_name)
            
            # Run pdflatex
            result = subprocess.run([
                "pdflatex", 
                "-interaction=nonstopmode",
                "-output-directory", "./output",
                str(input_file)
            ], capture_output=True, text=True, cwd=".")
            
            # Check if PDF was generated (pdflatex can succeed with warnings)
            compiled_pdf = Path("./output/final_report.pdf")
            if compiled_pdf.exists():
                # Move and rename the PDF
                compiled_pdf.rename(output_file)
                self.log_execution("PDF compilation succeeded with warnings", agent_name)
            elif result.returncode != 0:
                raise Exception(f"pdflatex compilation failed: {result.stderr}")
            else:
                raise Exception("PDF compilation succeeded but output file not found")
            
            # Clean up auxiliary files
            aux_files = ["./output/final_report.aux", "./output/final_report.log", "./output/final_report.out", "./output/final_report.toc"]
            for aux_file in aux_files:
                aux_path = Path(aux_file)
                if aux_path.exists():
                    aux_path.unlink()
            
            execution_time = time.time() - start_time
            self.log_execution(f"PDF compilation completed. Final report: {output_file}", agent_name)
            
            return AgentResult(
                agent_name=agent_name,
                status=AgentStatus.COMPLETED,
                input_path=str(input_file),
                output_path=str(output_file),
                execution_time=execution_time,
                metadata={"pdf_size": output_file.stat().st_size if output_file.exists() else 0}
            )
            
        except Exception as e:
            execution_time = time.time() - start_time
            self.log_execution(f"PDF compilation failed: {str(e)}", agent_name)
            
            return AgentResult(
                agent_name=agent_name,
                status=AgentStatus.FAILED,
                input_path="./output/latex/final_report.tex",
                output_path="./output/Final_Medical_Report.pdf",
                execution_time=execution_time,
                error_message=str(e)
            )
    
    async def execute_workflow(self) -> Dict:
        """Execute the complete medical document orchestration workflow."""
        
        self.log_execution("Starting Medical Document to Report Orchestration")
        self.log_execution("="*80)
        
        workflow_start = time.time()
        results = {}
        
        # Step 1: OCR_Agent
        self.log_execution("STEP 1: Executing OCR_Agent")
        ocr_result = await self.execute_ocr_agent()
        results['OCR_Agent'] = ocr_result
        
        if ocr_result.status != AgentStatus.COMPLETED:
            self.log_execution("Workflow terminated: OCR_Agent failed")
            return results
        
        # Step 2: Gemini_Report_Synthesizer_Agent  
        self.log_execution("STEP 2: Executing Gemini_Report_Synthesizer_Agent")
        synthesizer_result = await self.execute_gemini_synthesizer_agent()
        results['Gemini_Report_Synthesizer_Agent'] = synthesizer_result
        
        if synthesizer_result.status != AgentStatus.COMPLETED:
            self.log_execution("Workflow terminated: Gemini_Report_Synthesizer_Agent failed")
            return results
        
        # Step 3: LaTeX_Code_Agent
        self.log_execution("STEP 3: Executing LaTeX_Code_Agent")
        latex_result = await self.execute_latex_code_agent()
        results['LaTeX_Code_Agent'] = latex_result
        
        if latex_result.status != AgentStatus.COMPLETED:
            self.log_execution("Workflow terminated: LaTeX_Code_Agent failed")
            return results
        
        # Step 4: PDF_Compilation_Agent
        self.log_execution("STEP 4: Executing PDF_Compilation_Agent")
        pdf_result = await self.execute_pdf_compilation_agent()
        results['PDF_Compilation_Agent'] = pdf_result
        
        total_time = time.time() - workflow_start
        
        if pdf_result.status == AgentStatus.COMPLETED:
            self.log_execution("="*80)
            self.log_execution("✅ WORKFLOW COMPLETED SUCCESSFULLY!")
            self.log_execution(f"📄 Final Medical Report: {pdf_result.output_path}")
            self.log_execution(f"⏱️  Total execution time: {total_time:.2f} seconds")
        else:
            self.log_execution("❌ WORKFLOW FAILED at PDF compilation step")
        
        return results
    
    def generate_execution_report(self, results: Dict) -> str:
        """Generate a summary report of the workflow execution."""
        report_lines = []
        report_lines.append("MEDICAL DOCUMENT ORCHESTRATION - EXECUTION REPORT")
        report_lines.append("=" * 60)
        report_lines.append(f"Executed at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        report_lines.append("")
        
        total_time = sum(r.execution_time for r in results.values())
        successful_agents = sum(1 for r in results.values() if r.status == AgentStatus.COMPLETED)
        
        report_lines.append(f"Total Agents: {len(results)}")
        report_lines.append(f"Successful: {successful_agents}")
        report_lines.append(f"Failed: {len(results) - successful_agents}")
        report_lines.append(f"Total Execution Time: {total_time:.2f} seconds")
        report_lines.append("")
        
        for agent_name, result in results.items():
            status_emoji = "✅" if result.status == AgentStatus.COMPLETED else "❌"
            report_lines.append(f"{status_emoji} {agent_name}")
            report_lines.append(f"   Status: {result.status.value}")
            report_lines.append(f"   Time: {result.execution_time:.2f}s")
            report_lines.append(f"   Input: {result.input_path}")
            report_lines.append(f"   Output: {result.output_path}")
            if result.error_message:
                report_lines.append(f"   Error: {result.error_message}")
            report_lines.append("")
        
        return "\n".join(report_lines)

async def main():
    """Main execution function."""
    orchestrator = MedicalDocumentOrchestrator()
    
    # Execute the workflow
    results = await orchestrator.execute_workflow()
    
    # Generate and save execution report
    report = orchestrator.generate_execution_report(results)
    
    with open("./output/execution_report.txt", "w") as f:
        f.write(report)
    
    print("\n" + report)
    
    # Save execution log
    with open("./output/execution_log.txt", "w") as f:
        f.write("\n".join(orchestrator.execution_log))

if __name__ == "__main__":
    asyncio.run(main())
