import re

def preprocess_text(text: str) -> str:
    """
    Safely normalizes text for embedding generation.
    - Normalizes line endings to \n
    - Removes excessive blank lines
    - Removes unnecessary repeated spaces
    - Preserves semantic meaning and punctuation
    """
    if not text:
        return ""

    # Normalize line endings
    text = text.replace('\r\n', '\n').replace('\r', '\n')
    
    # Remove multiple spaces (but keep newlines)
    # Using regex to replace multiple spaces or tabs with a single space
    text = re.sub(r'[ \t]+', ' ', text)
    
    # Remove excessive blank lines (more than 2 consecutive newlines -> 2 newlines)
    text = re.sub(r'\n{3,}', '\n\n', text)
    
    # Strip leading/trailing whitespace
    text = text.strip()
    
    return text
