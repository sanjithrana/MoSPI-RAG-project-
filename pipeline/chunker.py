# pipeline/chunker.py
from typing import List

def chunk_text(text: str, chunk_size: int = 1000, overlap: int = 100) -> List[str]:
    words = text.split()
    chunks = []
    step = chunk_size - overlap
    for i in range(0, len(words), step):
        chunk = " ".join(words[i:i + chunk_size])
        if chunk.strip():
            chunks.append(chunk)
    return chunks