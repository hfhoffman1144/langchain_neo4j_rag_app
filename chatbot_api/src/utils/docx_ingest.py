import os
import json
from typing import List
from io import BytesIO

from docx import Document
import numpy as np
from src.utils.local_embeddings import LocalEmbeddings as OpenAIEmbeddings

# Simple local store for uploaded docs: JSONL with {id, text, embedding}
UPLOAD_STORE = os.getenv("UPLOAD_STORE_PATH", "./data/uploaded_docs.jsonl")
USE_FAISS = os.getenv("UPLOAD_USE_FAISS", "false").lower() in ("1", "true", "yes")
FAISS_INDEX_PATH = os.getenv("FAISS_INDEX_PATH", "./data/faiss_index.index")
FAISS_IDS_PATH = os.getenv("FAISS_IDS_PATH", "./data/faiss_ids.npy")

if USE_FAISS:
    try:
        import faiss
    except Exception:
        faiss = None


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

    # If FAISS mode enabled, append to a simple FAISS index
    if USE_FAISS and faiss is not None:
        dim = len(embedding)
        # ensure index dir
        _ensure_store_dir(FAISS_INDEX_PATH)

        # Load or create index
        index = None
        ids = []
        if os.path.exists(FAISS_INDEX_PATH) and os.path.exists(FAISS_IDS_PATH):
            try:
                index = faiss.read_index(FAISS_INDEX_PATH)
                ids = list(np.load(FAISS_IDS_PATH, allow_pickle=True))
            except Exception:
                index = None
                ids = []

        vec = np.array(embedding, dtype=np.float32)
        # normalize for cosine similarity via inner product
        norm = np.linalg.norm(vec) + 1e-10
        vec_norm = vec / norm

        if index is None:
            # use inner product index on normalized vectors
            index = faiss.IndexFlatIP(dim)
        index.add(vec_norm.reshape(1, -1))
        ids.append(doc_id)

        # persist index and ids
        faiss.write_index(index, FAISS_INDEX_PATH)
        np.save(FAISS_IDS_PATH, np.array(ids, dtype=object))

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
    # If FAISS is enabled and available, load FAISS-like numpy store
    if USE_FAISS and faiss is not None and os.path.exists(FAISS_INDEX_PATH) and os.path.exists(FAISS_IDS_PATH):
        try:
            index = faiss.read_index(FAISS_INDEX_PATH)
            ids = list(np.load(FAISS_IDS_PATH, allow_pickle=True))
            emb = OpenAIEmbeddings()
            q_emb = np.array(emb.embed_query(query), dtype=np.float32)
            q_emb = q_emb / (np.linalg.norm(q_emb) + 1e-10)
            D, I = index.search(q_emb.reshape(1, -1), k)
            entries = load_uploaded_entries()
            out = []
            for idx in I[0]:
                if idx < 0 or idx >= len(ids):
                    continue
                doc_id = ids[idx]
                for e in entries:
                    if e["id"] == doc_id:
                        out.append(e)
                        break
            return out
        except Exception:
            pass

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
