import os
import re
from datetime import datetime
from typing import Dict, List, Optional
import openai
from pathlib import Path

class HealthCareLatexAgent:
    def __init__(self, api_key: str = None):
        """Initialize the healthcare LaTeX conversion agent."""
        self.api_key = api_key or os.getenv('OPENAI_API_KEY')
        if self.api_key:
            openai.api_key = self.api_key
        
        self.latex_template = {
            'header': r'''\documentclass[11pt,a4paper]{article}
\usepackage[utf8]{inputenc}
\usepackage{geometry}
\usepackage{fancyhdr}
\usepackage{graphicx}
\usepackage{tabularx}
\usepackage{booktabs}
\usepackage{enumitem}
\usepackage{url}
\usepackage{hyperref}

\geometry{margin=1in}
\pagestyle{fancy}
\fancyhf{}
\rhead{\thepage}
\lhead{Healthcare Report}

\title{Healthcare Report}
\author{Medical Facility}
\date{\today}

\begin{document}
\maketitle
''',
            'footer': r'\end{document}'
        }
    
    def preprocess_text(self, text: str) -> str:
        """Clean and preprocess the input text."""
        # Remove extra whitespace and normalize line breaks
        text = re.sub(r'\s+', ' ', text.strip())
        text = re.sub(r'\n\s*\n', '\n\n', text)
        
        # Escape LaTeX special characters
        latex_chars = {
            '&': r'\&',
            '%': r'\%',
            '$': r'\$',
            '#': r'\#',
            '^': r'\^{}',
            '_': r'\_',
            '{': r'\{',
            '}': r'\}',
            '~': r'\~{}',
            '\\': r'\textbackslash{}'
        }
        
        for char, replacement in latex_chars.items():
            text = text.replace(char, replacement)
        
        return text
    
    def identify_sections(self, text: str) -> Dict[str, str]:
        """Identify common healthcare report sections."""
        sections = {}
        
        # Common healthcare report section patterns
        section_patterns = {
            'patient_info': r'(?i)(patient\s+information|demographics|personal\s+details)',
            'chief_complaint': r'(?i)(chief\s+complaint|presenting\s+complaint|reason\s+for\s+visit)',
            'history': r'(?i)(medical\s+history|patient\s+history|history\s+of\s+present\s+illness)',
            'examination': r'(?i)(physical\s+examination|clinical\s+examination|examination\s+findings)',
            'assessment': r'(?i)(assessment|diagnosis|clinical\s+impression)',
            'plan': r'(?i)(treatment\s+plan|management\s+plan|recommendations)',
            'medications': r'(?i)(medications|prescriptions|drug\s+therapy)',
            'vitals': r'(?i)(vital\s+signs|vitals|blood\s+pressure)'
        }
        
        # Split text and identify sections
        lines = text.split('\n')
        current_section = 'general'
        current_content = []
        
        for line in lines:
            line = line.strip()
            if not line:
                continue
                
            section_found = False
            for section_key, pattern in section_patterns.items():
                if re.search(pattern, line):
                    if current_content:
                        sections[current_section] = '\n'.join(current_content)
                    current_section = section_key
                    current_content = []
                    section_found = True
                    break
            
            if not section_found:
                current_content.append(line)
        
        if current_content:
            sections[current_section] = '\n'.join(current_content)
        
        return sections
    
    def format_patient_info(self, content: str) -> str:
        """Format patient information section."""
        return f'''\\section{{Patient Information}}
\\begin{{itemize}}[leftmargin=*]
{self._format_as_items(content)}
\\end{{itemize}}
'''
    
    def format_clinical_section(self, title: str, content: str) -> str:
        """Format a clinical section."""
        formatted_title = title.replace('_', ' ').title()
        return f'''\\section{{{formatted_title}}}
{content}

'''
    
    def format_vitals_table(self, content: str) -> str:
        """Format vital signs as a table."""
        return f'''\\section{{Vital Signs}}
\\begin{{center}}
\\begin{{tabular}}{{ll}}
\\toprule
Parameter & Value \\\\
\\midrule
{self._extract_vitals(content)}
\\bottomrule
\\end{{tabular}}
\\end{{center}}

'''
    
    def _format_as_items(self, content: str) -> str:
        """Convert content to LaTeX itemize format."""
        lines = content.split('\n')
        items = []
        for line in lines:
            if line.strip():
                items.append(f'\\item {line.strip()}')
        return '\n'.join(items)
    
    def _extract_vitals(self, content: str) -> str:
        """Extract and format vital signs data."""
        # Simple pattern matching for common vitals
        vital_patterns = {
            r'(?i)blood\s+pressure[:\s]+(\d+\/\d+)': 'Blood Pressure',
            r'(?i)heart\s+rate[:\s]+(\d+)': 'Heart Rate',
            r'(?i)temperature[:\s]+(\d+\.?\d*)[°]?[CF]?': 'Temperature',
            r'(?i)respiratory\s+rate[:\s]+(\d+)': 'Respiratory Rate',
            r'(?i)oxygen\s+saturation[:\s]+(\d+)%?': 'Oxygen Saturation'
        }
        
        rows = []
        for pattern, label in vital_patterns.items():
            match = re.search(pattern, content)
            if match:
                value = match.group(1)
                rows.append(f'{label} & {value} \\\\')
        
        return '\n'.join(rows) if rows else 'No vital signs data found & \\\\'
    
    def convert_to_latex(self, text_file_path: str, output_path: str = None) -> str:
        """Convert text file to LaTeX healthcare report."""
        # Read input file
        with open(text_file_path, 'r', encoding='utf-8') as file:
            raw_text = file.read()
        
        # Preprocess text
        cleaned_text = self.preprocess_text(raw_text)
        
        # Identify sections
        sections = self.identify_sections(cleaned_text)
        
        # Build LaTeX document
        latex_content = [self.latex_template['header']]
        
        # Process each section
        for section_key, content in sections.items():
            if section_key == 'patient_info':
                latex_content.append(self.format_patient_info(content))
            elif section_key == 'vitals':
                latex_content.append(self.format_vitals_table(content))
            else:
                latex_content.append(self.format_clinical_section(section_key, content))
        
        latex_content.append(self.latex_template['footer'])
        
        # Combine all content
        final_latex = '\n'.join(latex_content)
        
        # Save output
        if output_path is None:
            output_path = text_file_path.replace('.txt', '.tex')
        
        with open(output_path, 'w', encoding='utf-8') as file:
            file.write(final_latex)
        
        return final_latex
    
    def batch_convert(self, input_directory: str, output_directory: str = None):
        """Convert multiple text files to LaTeX."""
        input_path = Path(input_directory)
        output_path = Path(output_directory) if output_directory else input_path
        
        txt_files = list(input_path.glob('*.txt'))
        
        for txt_file in txt_files:
            output_file = output_path / f'{txt_file.stem}.tex'
            try:
                self.convert_to_latex(str(txt_file), str(output_file))
                print(f'Converted: {txt_file.name} -> {output_file.name}')
            except Exception as e:
                print(f'Error converting {txt_file.name}: {str(e)}')

# Usage example
if __name__ == "__main__":
    # Initialize the agent
    agent = HealthCareLatexAgent()
    
    # Convert a single file
    # agent.convert_to_latex('patient_report.txt', 'patient_report.tex')
    
    # Batch convert files in a directory
    # agent.batch_convert('input_reports/', 'output_latex/')
    
    print("Healthcare LaTeX Agent initialized. Use convert_to_latex() or batch_convert() methods.")