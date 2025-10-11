import io
import json
import numpy as np
from fastapi.testclient import TestClient
from src.main import app


def create_sample_docx_bytes(text: str) -> bytes:
    # Create a minimal .docx in-memory using python-docx
    from docx import Document

    doc = Document()
    doc.add_paragraph(text)
    bio = io.BytesIO()
    doc.save(bio)
    return bio.getvalue()


def test_upload_docx_endpoint(monkeypatch):
    # Mock embeddings to avoid network/OpenAI calls
    class MockEmb:
        def embed_documents(self, docs):
            return [[0.1] * 8 for _ in docs]

        def embed_query(self, q):
            return [0.1] * 8

    monkeypatch.setattr("src.utils.docx_ingest.OpenAIEmbeddings", lambda: MockEmb())

    client = TestClient(app)
    data = {"file": ("sample.docx", create_sample_docx_bytes("Hello world"), "application/vnd.openxmlformats-officedocument.wordprocessingml.document")}
    resp = client.post("/upload-docx", files=data)
    assert resp.status_code == 200
    payload = resp.json()
    assert payload["status"] == "ok"
    assert "id" in payload
    assert "text_snippet" in payload


def test_faiss_path(monkeypatch, tmp_path):
    # Prepare fake faiss module
    class FakeIndex:
        def __init__(self, dim):
            self.mat = np.zeros((0, dim), dtype=np.float32)

        def add(self, vecs):
            self.mat = np.vstack([self.mat, vecs])

        def search(self, q, k):
            D = self.mat @ q.T
            I = np.argsort(D[:, 0])[::-1][:k]
            return D[[0]], I.reshape(1, -1)

    class FakeFaiss:
        IndexFlatIP = FakeIndex

        @staticmethod
        def write_index(idx, path):
            np.savez(path, mat=idx.mat)

        @staticmethod
        def read_index(path):
            arr = np.load(path)['mat']
            fi = FakeIndex(arr.shape[1])
            fi.mat = arr
            return fi

    monkeypatch.setenv("UPLOAD_USE_FAISS", "true")
    monkeypatch.setenv("FAISS_INDEX_PATH", str(tmp_path / "faiss.index"))
    monkeypatch.setenv("FAISS_IDS_PATH", str(tmp_path / "faiss_ids.npy"))
    monkeypatch.setattr("src.utils.docx_ingest.faiss", FakeFaiss(), raising=False)
    # Mock embeddings
    class MockEmb:
        def embed_documents(self, docs):
            return [[0.2] * 8 for _ in docs]

        def embed_query(self, q):
            return [0.2] * 8

    monkeypatch.setattr("src.utils.docx_ingest.OpenAIEmbeddings", lambda: MockEmb())

    # Call embed_and_store and then search
    from src.utils.docx_ingest import embed_and_store, simple_search

    entry = embed_and_store("legal text example", "doc1")
    results = simple_search("legal text", k=1)
    assert isinstance(results, list)
    # Results should include the stored doc
    assert any(r["id"] == "doc1" for r in results)
