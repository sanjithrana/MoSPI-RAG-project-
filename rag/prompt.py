# rag/prompt.py
SYSTEM_PROMPT = """You are an assistant that MUST answer only from the provided context. If answer is not found, reply exactly: "I don't have that in my data." Use bullet citations with the source title and URL when possible."""

def build_prompt(context_chunks, question):
    ctx = "\n\n---\n\n".join([c["text"] for c in context_chunks])
    prompt = f"{SYSTEM_PROMPT}\n\nContext:\n{ctx}\n\nQuestion: {question}\n\nAnswer concisely and include bullet citations."
    return prompt
