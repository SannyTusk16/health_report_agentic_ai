import os
import re
from datetime import datetime
from typing import Dict, List, Optional
# import google.generativeai as genai  # For Gemini API if needed
from pathlib import Path

class HealthCareLatexAgent:
    def __init__(self, api_key: str = None):
        """Initialize the healthcare LaTeX conversion agent."""
        self.api_key = "aAIzaSyBaOTbQce2Yt2uKtJKOHfOek6o-t0PwSKg"
        
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
\usepackage{amssymb}
% Checkbox macros
\newcommand{\checkbox}{\(\Box\)}
\newcommand{\checkedbox}{\(\boxtimes\)}

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
        # Normalize line endings and remove excessive blank lines
        text = text.replace('\r\n', '\n').replace('\r', '\n')
        text = re.sub(r'\n{3,}', '\n\n', text)
        return text.strip()
    
    def identify_sections(self, text: str) -> Dict[str, Dict]:
        """Identify sections based on 'SECTION X: ...' headers and return a dict with section titles and content."""
        section_regex = re.compile(r'^(SECTION\s*\d+\s*:\s*.+)$', re.IGNORECASE | re.MULTILINE)
        matches = list(section_regex.finditer(text))
        sections = {}
        if not matches:
            # fallback: treat all as one section
            return {"Report": {"title": "Report", "content": text.strip()}}
        for i, match in enumerate(matches):
            start = match.end()
            end = matches[i+1].start() if i+1 < len(matches) else len(text)
            title = match.group(1).strip()
            content = text[start:end].strip()
            sections[title] = {"title": title, "content": content}
        return sections
    
    def format_section(self, title: str, content: str) -> str:
        """Format a section with LaTeX section, using checkboxes for Yes/No and paragraphs for narrative."""
        latex_title = re.sub(r'^SECTION\s*\d+\s*:\s*', '', title, flags=re.IGNORECASE).strip()
        if not latex_title:
            latex_title = title.strip()
        
        # Clean content and remove timeline data
        content = re.sub(r'=== TIMELINE DATA ===.*', '', content, flags=re.DOTALL)
        lines = [l.strip() for l in content.split('\n') if l.strip() and not l.startswith('[')]
        
        kv_pairs = []
        narrative_lines = []
        checkbox_questions = []
        
        i = 0
        while i < len(lines):
            line = lines[i]
            
            # Check for checkbox questions (Yes/No patterns)
            if re.search(r'(OO?\s*Yes|M\s*No|VINo|MYes|OOINo|CJ\s*Not\s*Sure)', line):
                # Clean up checkbox patterns
                clean_line = re.sub(r'OO?\s*Yes', r'\\checkedbox~Yes', line)
                clean_line = re.sub(r'MI?\s*No', r'\\checkbox~No', clean_line)
                clean_line = re.sub(r'VINo', r'\\checkbox~No', clean_line)
                clean_line = re.sub(r'MYes', r'\\checkedbox~Yes', clean_line)
                clean_line = re.sub(r'OOINo', r'\\checkbox~No', clean_line)
                clean_line = re.sub(r'O\s*Yes', r'\\checkedbox~Yes', clean_line)
                clean_line = re.sub(r'M\s*No', r'\\checkbox~No', clean_line)
                clean_line = re.sub(r'CJ\s*Not\s*Sure', r'\\checkbox~Not~Sure', clean_line)
                checkbox_questions.append(clean_line)
            
            # Key-value pairs (simple format)
            elif ':' in line and len(line.split(':')) == 2:
                key, value = line.split(':', 1)
                key = key.strip()
                value = value.strip()
                if len(key) < 100 and len(value) < 200:  # Reasonable length for key-value
                    kv_pairs.append((key, value))
                else:
                    narrative_lines.append(line)
            
            # Everything else is narrative
            else:
                narrative_lines.append(line)
            
            i += 1
        
        # Build LaTeX output
        latex = f'\\section{{{latex_title}}}\n\n'
        
        # Add key-value pairs as table
        if kv_pairs:
            latex += '\\begin{tabularx}{\\textwidth}{l X}\n\\toprule\n'
            for k, v in kv_pairs:
                latex += f'{self.escape_latex(k)} & {self.escape_latex(v)} \\\\\n'
            latex += '\\bottomrule\n\\end{tabularx}\n\n'
        
        # Add narrative as proper paragraphs
        if narrative_lines:
            # Group consecutive lines into paragraphs
            paragraphs = []
            current_paragraph = []
            
            for line in narrative_lines:
                if line.strip():
                    current_paragraph.append(line)
                else:
                    if current_paragraph:
                        paragraphs.append(' '.join(current_paragraph))
                        current_paragraph = []
            
            if current_paragraph:
                paragraphs.append(' '.join(current_paragraph))
            
            for paragraph in paragraphs:
                latex += f'{self.escape_latex(paragraph)}\n\n'
        
        # Add checkbox questions as list
        if checkbox_questions:
            latex += '\\begin{itemize}[leftmargin=*]\n'
            for question in checkbox_questions:
                latex += f'\\item {self.escape_latex(question)}\n'
            latex += '\\end{itemize}\n\n'
        
        return latex

    def escape_latex(self, text: str) -> str:
        """Escape LaTeX special characters in a string."""
        # Don't double-escape already escaped checkbox commands
        if '\\checkedbox' in text or '\\checkbox' in text:
            return text
            
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
        for section in sections.values():
            latex_content.append(self.format_section(section['title'], section['content']))
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