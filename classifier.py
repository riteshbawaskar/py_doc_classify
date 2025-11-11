"""
Document Classifier - Python 3.12 Compatible
Uses PaddleOCR, LangGraph, and Gemini AI
"""
import os
from typing import TypedDict
from langgraph.graph import StateGraph, END
import google.generativeai as genai
from paddleocr import PaddleOCR, draw_ocr
from pathlib import Path
from PIL import Image
import PyPDF2
from docx import Document

# Configure Gemini AI
genai.configure(api_key="AIzaSyCmjq7zKXLKIDtJEW6G-z5anvgRwIao3Hs")
model = genai.GenerativeModel('gemini-2.5-flash-preview-05-20')
MODEL_DIR = Path(__file__).parent / "paddleocr"

# Initialize PaddleOCR (English language)
ocr = PaddleOCR(use_angle_cls=True, lang='en', show_log=False, 
    det_model_dir=str(MODEL_DIR / 'detection' / 'en_ppocr_mobile_v2.0_det_infer'),
    rec_model_dir=str(MODEL_DIR / 'recognition' / 'en_number_mobile_v2.0_rec_infer'),
    cls_model_dir=str(MODEL_DIR / 'cls' / 'ch_ppocr_mobile_v2.0_cls_infer'),)
print("✓ PaddleOCR initialized")

# Define state
class DocumentState(TypedDict):
    file_path: str
    document_text: str
    document_type: str
    confidence: str

def extract_text_from_image(image_path: str) -> str:
    """Extract text from image using PaddleOCR"""
    result = ocr.ocr(image_path, cls=True)
    text_parts = []
    if result and result[0]:
        for line in result[0]:
            if line and len(line) > 1:
                text_parts.append(line[1][0])
    return ' '.join(text_parts)

def extract_text_from_pdf(pdf_path: str) -> str:
    """Extract text from PDF"""
    text = ""
    with open(pdf_path, 'rb') as file:
        pdf_reader = PyPDF2.PdfReader(file)
        for page in pdf_reader.pages:
            text += page.extract_text()
    return text

def extract_text_from_docx(docx_path: str) -> str:
    """Extract text from Word document"""
    doc = Document(docx_path)
    text = ""
    for paragraph in doc.paragraphs:
        text += paragraph.text + "\n"
    return text

def extract_text(state: DocumentState) -> DocumentState:
    """Extract text based on file format"""
    file_path = state['file_path']
    file_ext = os.path.splitext(file_path)[1].lower()
    
    print(f"Extracting text from: {file_path}")
    
    if file_ext in ['.jpg', '.jpeg', '.png', '.bmp']:
        text = extract_text_from_image(file_path)
    elif file_ext == '.pdf':
        text = extract_text_from_pdf(file_path)
    elif file_ext == '.docx':
        text = extract_text_from_docx(file_path)
    else:
        raise ValueError(f"Unsupported file format: {file_ext}")
    
    return {
        "file_path": file_path,
        "document_text": text,
        "document_type": "",
        "confidence": ""
    }

def classify_document(state: DocumentState) -> DocumentState:
    """Classify document using Gemini AI"""
    
    prompt = f"""Classify this document into ONE of these types:
    - AADHAAR (Indian national ID card)
    - PASSPORT (travel document)
    - PAN_CARD (Permanent Account Number)
    - RESUME (CV/job application)
    - CONTRACT (legal agreement)
    - EXPERIENCE_LETTER (employment letter)
    
    Document text:
    {state['document_text'][:2000]}
    
    Respond ONLY in this format:
    DOCUMENT_TYPE: <type>
    CONFIDENCE: <HIGH/MEDIUM/LOW>
    """
    
    response = model.generate_content(prompt)
    result = response.text.strip()
    
    doc_type = "UNKNOWN"
    confidence = "LOW"
    
    for line in result.split('\n'):
        if 'DOCUMENT_TYPE:' in line:
            doc_type = line.split('DOCUMENT_TYPE:')[1].strip()
        if 'CONFIDENCE:' in line:
            confidence = line.split('CONFIDENCE:')[1].strip()
    
    return {
        "file_path": state["file_path"],
        "document_text": state["document_text"],
        "document_type": doc_type,
        "confidence": confidence
    }

def create_graph():
    """Create LangGraph workflow"""
    workflow = StateGraph(DocumentState)
    workflow.add_node("extract", extract_text)
    workflow.add_node("classify", classify_document)
    workflow.set_entry_point("extract")
    workflow.add_edge("extract", "classify")
    workflow.add_edge("classify", END)
    return workflow.compile()

def classify_file(file_path: str) -> dict:
    """Classify a document file"""
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"File not found: {file_path}")
    
    graph = create_graph()
    result = graph.invoke({
        "file_path": file_path,
        "document_text": "",
        "document_type": "",
        "confidence": ""
    })
    
    return result

if __name__ == "__main__":
    import sys
    
    if len(sys.argv) < 2:
        print("Usage: python classifier.py <document_file>")
        print("Supported: .jpg, .jpeg, .png, .pdf, .docx")
        sys.exit(1)
    
    file_path = sys.argv[1]
    result = classify_file(file_path)
    
    print(f"\n{'='*60}")
    print("CLASSIFICATION RESULT")
    print('='*60)
    print(f"Document Type: {result['document_type']}")
    print(f"Confidence: {result['confidence']}")
    print(f"\nText Preview: {result['document_text'][:200]}...")
    print('='*60)