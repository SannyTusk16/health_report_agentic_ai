OCR Agent API - FastAPI service for PDF text extraction and timeline processing
This FastAPI application provides OCR (Optical Character Recognition) capabilities
to extract text from PDF documents and convert them into timeline format.
Dependencies:
    - fastapi: Web framework for building APIs
    - pytesseract: Python wrapper for Google's Tesseract OCR engine
    - pdf2image: Library to convert PDF pages to PIL images
    - PIL (Pillow): Python Imaging Library for image processing
    - uvicorn: ASGI server for running FastAPI applications
Installation Requirements:
    pip install fastapi pytesseract pdf2image pillow uvicorn
    System Requirements:
    - Tesseract OCR engine must be installed on the system
    - poppler-utils for PDF to image conversion
Usage:
    1. Start the server:
       python ocrmowa.py
    2. API will be available at http://localhost:8000
    3. Send POST request to /timeline/from-text with JSON body:
       {
           "pdf_base64": "base64_encoded_pdf_content"
       }
    4. Response format:
       {
           "extracted_text": "Full extracted text from PDF",
           "timeline_data": [
               {
                   "content": "Text segment",
                   "timestamp": null,
               }
           ]
       }
Example usage with curl:
    curl -X POST "http://localhost:8000/timeline/from-text" \
         -H "Content-Type: application/json" \
         -d '{"pdf_base64": "your_base64_encoded_pdf_here"}'
Example usage with Python requests:
    with open("document.pdf", "rb") as f:
        pdf_base64 = base64.b64encode(f.read()).decode()
    response = requests.post(
        "http://localhost:8000/timeline/from-text",
        json={"pdf_base64": pdf_base64}
    result = response.json()
    print(result["extracted_text"])
API Documentation:
    - Interactive docs: http://localhost:8000/docs
    - OpenAPI schema: http://localhost:8000/openapi.json
Note: The timeline processing is currently basic and extracts text segments.
Customize the process_text_to_timeline() function for specific timeline
requirements such as date parsing, event categorization, or custom formatting.