import io
from pypdf import PdfReader

def load_pdf(file_bytes: bytes, filename: str) -> str:
    """
    Extracts text from a PDF file.
    Rejects PDFs with no extractable text (e.g. image-only scans).
    """
    if not file_bytes:
        raise ValueError("File is empty.")

    f = io.BytesIO(file_bytes)
    
    try:
        reader = PdfReader(f)
    except Exception as e:
        raise ValueError(f"Invalid or corrupted PDF file: {e}")
        
    extracted_text = []
    
    for page in reader.pages:
        text = page.extract_text()
        if text:
            extracted_text.append(text)
            
    final_text = "\n".join(extracted_text)
    
    if not final_text.strip():
        raise ValueError("PDF contains no extractable text. Scanned or image-only PDFs are unsupported.")
        
    return final_text
