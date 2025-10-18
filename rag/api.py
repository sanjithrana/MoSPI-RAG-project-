# rag/api.py
import os
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from rag.retriever import retrieve
from rag.prompt import build_prompt
import uvicorn
from typing import List

app = FastAPI()

class AskRequest(BaseModel):
    question: str
    k: int = 4

class AskResponse(BaseModel):
    answer: str
    citations: List[dict]

@app.post("/ask", response_model=AskResponse)
def ask(req: AskRequest):
    # retrieve
    ctx = retrieve(req.question, k=req.k)
    if not ctx:
        raise HTTPException(status_code=404, detail="No context available")
    # build prompt
    prompt = build_prompt(ctx, req.question)
    # **Placeholder generator**: in real deployment call LLaMA (Ollama/llama.cpp)
    # For this starter, we will do a naive extractive: return joined top chunks or fallback.
    joined = "\n\n".join([c["text"] for c in ctx])
    # very naive answer
    answer = joined[:2000] + ("\n\n[truncated]" if len(joined) > 2000 else "")
    citations = [{"title": f"Doc {c['document_id']}", "url": f"(local_doc_id:{c['document_id']})"} for c in ctx]
    return {"answer": answer, "citations": citations}

@app.get("/health")
def health():
    return {"status": "ok"}

@app.post("/ingest")
def ingest():
    # trigger pipeline - in compose, map to a script that runs pipeline.run:build_index
    return {"status": "ok", "note": "Trigger pipeline externally (e.g. make index)"}

if __name__ == "__main__":
    uvicorn.run("rag.api:app", host="0.0.0.0", port=int(os.getenv("API_PORT", "8000")), reload=False)
