import charset_normalizer

def load_txt(file_bytes: bytes, filename: str) -> str:
    """
    Load text from a .txt file, attempting to detect and handle different encodings.
    Rejects empty files.
    """
    if not file_bytes:
        raise ValueError("File is empty.")

    # Try utf-8 first
    try:
        text = file_bytes.decode('utf-8')
    except UnicodeDecodeError:
        # Fallback using charset_normalizer
        result = charset_normalizer.detect(file_bytes)
        encoding = result.get('encoding')
        if encoding:
            text = file_bytes.decode(encoding, errors='replace')
        else:
            text = file_bytes.decode('utf-8', errors='replace')
            
    if not text.strip():
        raise ValueError("File contains no extractable text.")
        
    return text
