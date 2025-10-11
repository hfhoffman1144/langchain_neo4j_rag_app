import io
import json
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
