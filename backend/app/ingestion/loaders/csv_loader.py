import csv
import io

def load_csv(file_bytes: bytes, filename: str) -> str:
    """
    Load FAQ data from a CSV. Expects columns for Question and Answer.
    Extracts rows into a unified text representation suitable for RAG.
    """
    if not file_bytes:
        raise ValueError("File is empty.")
        
    try:
        text_content = file_bytes.decode('utf-8')
    except UnicodeDecodeError:
        text_content = file_bytes.decode('utf-8', errors='replace')
        
    if not text_content.strip():
        raise ValueError("File contains no extractable text.")

    f = io.StringIO(text_content)
    reader = csv.DictReader(f)
    
    if not reader.fieldnames:
        raise ValueError("Malformed CSV: No headers found.")

    # Detect variations of 'question' and 'answer'
    headers_lower = {h.strip().lower(): h for h in reader.fieldnames if h.strip()}
    
    q_col = None
    a_col = None
    
    for k, v in headers_lower.items():
        if 'question' in k or 'q' == k:
            q_col = v
        elif 'answer' in k or 'a' == k:
            a_col = v
            
    if not q_col or not a_col:
        raise ValueError("CSV must contain a 'Question' and 'Answer' column.")

    output_lines = []
    for idx, row in enumerate(reader):
        q = row.get(q_col, "").strip()
        a = row.get(a_col, "").strip()
        if q and a:
            output_lines.append(f"Question: {q}\nAnswer: {a}\n")

    if not output_lines:
        raise ValueError("No valid Question/Answer pairs found in CSV.")

    return "\n\n".join(output_lines)
