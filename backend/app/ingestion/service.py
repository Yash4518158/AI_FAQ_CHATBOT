from sqlalchemy.orm import Session
from app.models.faq import FAQDocument, FAQChunk
from app.ingestion.loaders.txt_loader import load_txt
from app.ingestion.loaders.csv_loader import load_csv
from app.ingestion.loaders.pdf_loader import load_pdf
from app.ingestion.preprocessing import preprocess_text
from app.ingestion.chunking import chunk_text

def process_file_ingestion(file_bytes: bytes, filename: str, user_id: str, db: Session):
    """
    Orchestrates the ingestion pipeline transactionally.
    Returns the created FAQDocument.
    """
    ext = filename.lower().split('.')[-1]
    
    # 1. Load File
    if ext == 'txt':
        raw_text = load_txt(file_bytes, filename)
    elif ext == 'csv':
        raw_text = load_csv(file_bytes, filename)
    elif ext == 'pdf':
        raw_text = load_pdf(file_bytes, filename)
    else:
        raise ValueError(f"Unsupported file type: {ext}")
        
    # 2. Preprocess Text
    clean_text = preprocess_text(raw_text)
    if not clean_text:
        raise ValueError("File contains no usable text after preprocessing.")
        
    # 3. Create Document
    doc = FAQDocument(
        title=filename,
        source=filename,
        content=clean_text,
        created_by=user_id
    )
    db.add(doc)
    db.flush() # Get doc.id
    
    # 4. Chunk Text
    chunks = chunk_text(clean_text)
    
    # 5. Create Chunks
    for idx, chunk_content in enumerate(chunks):
        metadata = {
            "source": filename,
            "title": filename,
            "chunk_index": idx
        }
        
        faq_chunk = FAQChunk(
            document_id=doc.id,
            chunk_index=idx,
            text_chunk=chunk_content,
            chunk_metadata=metadata
        )
        db.add(faq_chunk)
        
    # 6. Transaction handled by caller (but we'll flush to ensure no errors)
    db.flush()
    return doc, len(chunks)
