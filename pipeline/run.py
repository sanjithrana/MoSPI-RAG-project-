# pipeline/run.py
import os
import json
import sqlite3
from pathlib import Path
from sentence_transformers import SentenceTransformer
import numpy as np
import faiss
import pandas as pd
import hashlib
from typing import List
from datetime import datetime

RAW_PARQUET_DIR = Path(os.getenv("RAW_PARQUET_DIR", "data/raw"))
PROCESSED_DIR = Path(os.getenv("PROCESSED_DIR", "data/processed"))
INDEX_DIR = PROCESSED_DIR / "index"
CHUNKS_DIR = PROCESSED_DIR / "chunks"

PROCESSED_DIR.mkdir(parents=True, exist_ok=True)
CHUNKS_DIR.mkdir(parents=True, exist_ok=True)
INDEX_DIR.mkdir(parents=True, exist_ok=True)

EMBED_MODEL_NAME = os.getenv("EMBED_MODEL", "all-MiniLM-L6-v2")
EMBED_DIM = 384  # for all-MiniLM-L6-v2

def load_texts_from_parquet():
    # Look for txt parquet files created by parser
    txts = []
    for p in RAW_PARQUET_DIR.rglob("*.parquet"):
        df = pd.read_parquet(p)
        for row in df.to_dict(orient="records"):
            txts.append({"document_id": row.get("document_id"), "text": row.get("text")})
    return txts

def chunk_text(text: str, chunk_size: int = 1000, overlap: int = 200) -> List[str]:
    tokens = text.split()
    out = []
    i = 0
    while i < len(tokens):
        chunk = tokens[i:i+chunk_size]
        out.append(" ".join(chunk))
        i += chunk_size - overlap
    return out

def build_index():
    texts = load_texts_from_parquet()
    if not texts:
        print("No texts found under", RAW_PARQUET_DIR)
        return
    # chunk and create manifest
    chunks = []
    for t in texts:
        for chunk in chunk_text(t["text"]):
            chunks.append({"document_id": t["document_id"], "text": chunk})
    df = pd.DataFrame(chunks)
    chunks_path = CHUNKS_DIR / "chunks.parquet"
    df.to_parquet(chunks_path, index=False)
    # embed
    model = SentenceTransformer(EMBED_MODEL_NAME)
    embeddings = model.encode(df["text"].tolist(), show_progress_bar=True, convert_to_numpy=True)
    # build faiss index
    dim = embeddings.shape[1]
    index = faiss.IndexFlatL2(dim)
    index.add(embeddings)
    faiss.write_index(index, str(INDEX_DIR / "faiss.index"))
    # manifest
    meta = {"n_chunks": len(df), "created_at": datetime.utcnow().isoformat()}
    with open(INDEX_DIR / "manifest.json", "w") as f:
        json.dump(meta, f)
    # also save mapping
    df.reset_index().to_parquet(INDEX_DIR / "mapping.parquet", index=False)
    print("Index built:", INDEX_DIR)

if __name__ == "__main__":
    build_index()
