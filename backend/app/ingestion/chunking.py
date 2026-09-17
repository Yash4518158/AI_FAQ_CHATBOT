import os

def chunk_text(text: str) -> list[str]:
    """
    Splits text into chunks, preferring paragraph breaks, then sentence breaks, then character limits.
    Configurable via CHUNK_SIZE and CHUNK_OVERLAP environment variables.
    """
    chunk_size = int(os.getenv("CHUNK_SIZE", 500))
    chunk_overlap = int(os.getenv("CHUNK_OVERLAP", 50))
    
    if not text:
        return []
        
    # We will split text based on paragraphs first (double newline)
    # This naturally keeps Question + Answer together if they don't exceed chunk size
    paragraphs = text.split('\n\n')
    
    chunks = []
    current_chunk = ""
    
    for para in paragraphs:
        # If the paragraph itself is larger than chunk_size, we need to split it by sentences
        if len(para) > chunk_size:
            sentences = para.replace('? ', '?\n').replace('. ', '.\n').replace('! ', '!\n').split('\n')
            for sentence in sentences:
                sentence = sentence.strip()
                if not sentence:
                    continue
                    
                if len(current_chunk) + len(sentence) + 1 <= chunk_size:
                    current_chunk += (" " + sentence if current_chunk else sentence)
                else:
                    if current_chunk:
                        chunks.append(current_chunk.strip())
                        # Start new chunk with overlap
                        overlap_start = max(0, len(current_chunk) - chunk_overlap)
                        current_chunk = current_chunk[overlap_start:] + " " + sentence if chunk_overlap > 0 else sentence
                    else:
                        # Sentence is massive, force split it
                        for i in range(0, len(sentence), chunk_size - chunk_overlap):
                            chunks.append(sentence[i:i + chunk_size])
                        current_chunk = ""
        else:
            # Paragraph fits, check if it fits in current chunk
            if len(current_chunk) + len(para) + 2 <= chunk_size:
                current_chunk += ("\n\n" + para if current_chunk else para)
            else:
                if current_chunk:
                    chunks.append(current_chunk.strip())
                    current_chunk = para
                else:
                    current_chunk = para
                    
    if current_chunk:
        chunks.append(current_chunk.strip())
        
    return chunks
