# rag/retriever.py
import os
import json
import faiss
import pandas as pd
from sentence_transformers import SentenceTransformer
from typing import List, Dict
from pathlib import Path

INDEX_DIR = Path(os.getenv("INDEX_DIR", "data/processed/index"))
EMBED_MODEL_NAME = os.getenv("EMBED_MODEL", "all-MiniLM-L6-v2")
K = int(os.getenv("RAG_K", "4"))

_model = None
_index = None
_mapping = None

def load_resources():
    global _model, _index, _mapping
    if _model is None:
        _model = SentenceTransformer(EMBED_MODEL_NAME)
    if _index is None:
        _index = faiss.read_index(str(INDEX_DIR / "faiss.index"))
    if _mapping is None:
        _mapping = pd.read_parquet(INDEX_DIR / "mapping.parquet")
    return _model, _index, _mapping

def retrieve(question: str, k: int = K) -> List[Dict]:
    model, index, mapping = load_resources()
    q_emb = model.encode([question], convert_to_numpy=True)
    D, I = index.search(q_emb, k)
    results = []
    for idx in I[0]:
        row = mapping.iloc[idx]
        results.append({"score": float(1.0), "text": row["text"], "document_id": int(row["document_id"])})
    return results
