from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import List, Dict, Any
import pytesseract
import pdf2image
from PIL import Image
import io
import base64
import uvicorn
import requests
import os
from pathlib import Path
from datetime import datetime

app = FastAPI(title="OCR Agent API", description="PDF OCR processing service")

class TextInput(BaseModel):
    pdf_base64: str

class TimelineResponse(BaseModel):
    extracted_text: str
    timeline_data: List[Dict[str, Any]]

def save_ocr_text_to_file(text: str, source_info: str = "API Request") -> str:
    """Save OCR text to ./output/text.txt, appending if file exists"""
    try:
        # Ensure output directory exists
        output_dir = Path("./output")
        output_dir.mkdir(parents=True, exist_ok=True)
        
        output_file = output_dir / "text.txt"
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        # Prepare content with separator and metadata
        separator = "\n" + "="*50 + "\n"
        content = f"{separator}[{timestamp}] Source: {source_info}\n{separator}\n{text}\n"
        
        # Append to file (or create if doesn't exist)
        with open(output_file, 'a', encoding='utf-8') as f:
            f.write(content)
        
        print(f"✅ OCR text saved to: {output_file.absolute()}")
        return str(output_file.absolute())
        
    except Exception as e:
        print(f"❌ Error saving OCR text: {e}")
        raise e

def extract_text_from_pdf(pdf_bytes: bytes) -> str:
    """Extract text from PDF using OCR"""
    try:
        # Convert PDF to images
        images = pdf2image.convert_from_bytes(pdf_bytes)
        
        extracted_text = ""
        for image in images:
            # Use OCR to extract text from each page
            text = pytesseract.image_to_string(image)
            extracted_text += text + "\n"
        
        return extracted_text.strip()
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"OCR processing failed: {str(e)}")

def process_text_to_timeline(text: str) -> List[Dict[str, Any]]:
    """Process extracted text into timeline format"""
    # Basic timeline extraction logic (customize as needed)
    lines = text.split('\n')
    timeline_data = []
    
    for line in lines:
        line = line.strip()
        if line and len(line) > 10:  # Filter meaningful content
            timeline_data.append({
                "content": line,
                "timestamp": None,  # Add timestamp logic if needed
                "type": "text_segment"
            })
    
    return timeline_data

@app.get("/health")
def health_check():
    """Health check endpoint to verify server status"""
    return {
        "status": "healthy",
        "message": "OCR Agent API is running and ready to process requests",
        "service": "OCR Agent API"
    }

@app.post("/timeline/from-text", response_model=TimelineResponse)
async def create_timeline_from_text(request: TextInput):
    """
    Extract text from PDF using OCR and convert to timeline format
    """
    try:
        # Decode base64 PDF
        pdf_bytes = base64.b64decode(request.pdf_base64)
        
        # Extract text using OCR
        extracted_text = extract_text_from_pdf(pdf_bytes)
        
        if not extracted_text:
            raise HTTPException(status_code=400, detail="No text could be extracted from PDF")
        
        # Save OCR text to ./output/text.txt
        file_path = save_ocr_text_to_file(extracted_text, "PDF via API")
        
        # Process text into timeline format
        timeline_data = process_text_to_timeline(extracted_text)
        
        return TimelineResponse(
            extracted_text=extracted_text,
            timeline_data=timeline_data
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Processing failed: {str(e)}")

@app.get("/")
async def root():
    return {"message": "OCR Agent API is running"}

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)