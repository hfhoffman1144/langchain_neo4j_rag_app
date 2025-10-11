import os
import json
from typing import List
from io import BytesIO

from docx import Document
import numpy as np
from langchain_openai import OpenAIEmbeddings

# Simple local store for uploaded docs: JSONL with {id, text, embedding}
UPLOAD_STORE = os.getenv("UPLOAD_STORE_PATH", "./data/uploaded_docs.jsonl")


def _ensure_store_dir(path: str):
    d = os.path.dirname(path)
    if d and not os.path.exists(d):
        os.makedirs(d, exist_ok=True)


def docx_to_text(file_bytes: bytes) -> str:
    doc = Document(BytesIO(file_bytes))
    paragraphs = [p.text for p in doc.paragraphs if p.text and p.text.strip()]
    return "\n\n".join(paragraphs)


def embed_and_store(text: str, doc_id: str) -> dict:
    """Compute embedding for text and append to the local upload store."""
    emb = OpenAIEmbeddings()
    embedding = emb.embed_documents([text])[0]

    _ensure_store_dir(UPLOAD_STORE)

    entry = {"id": doc_id, "text": text, "embedding": embedding}
    with open(UPLOAD_STORE, "a", encoding="utf-8") as fh:
        fh.write(json.dumps(entry) + "\n")

    return entry


def load_uploaded_entries() -> List[dict]:
    if not os.path.exists(UPLOAD_STORE):
        return []
    out = []
    with open(UPLOAD_STORE, "r", encoding="utf-8") as fh:
        for line in fh:
            try:
                out.append(json.loads(line))
            except Exception:
                continue
    return out


def simple_search(query: str, k: int = 5) -> List[dict]:
    """Brute-force cosine similarity search over uploaded entries."""
    entries = load_uploaded_entries()
    if not entries:
        return []

    emb = OpenAIEmbeddings()
    q_emb = np.array(emb.embed_query(query), dtype=float)

    scores = []
    for e in entries:
        v = np.array(e["embedding"], dtype=float)
        sim = float(np.dot(q_emb, v) / (np.linalg.norm(q_emb) * np.linalg.norm(v) + 1e-10))
        scores.append((sim, e))

    scores.sort(key=lambda x: x[0], reverse=True)
    return [e for _, e in scores[:k]]
