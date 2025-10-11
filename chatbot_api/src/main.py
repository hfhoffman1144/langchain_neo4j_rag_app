from fastapi import FastAPI
from src.agents.hospital_rag_agent import hospital_rag_agent_executor
from src.models.hospital_rag_query import HospitalQueryInput, HospitalQueryOutput
from src.utils.async_utils import async_retry
from fastapi import UploadFile, File, HTTPException
from uuid import uuid4
from src.utils.docx_ingest import docx_to_text, embed_and_store

app = FastAPI(
    title="Hospital Chatbot",
    description="Endpoints for a hospital system graph RAG chatbot",
)


@async_retry(max_retries=10, delay=1)
async def invoke_agent_with_retry(query: str):
    """
    Retry the agent if a tool fails to run. This can help when there
    are intermittent connection issues to external APIs.
    """

    return await hospital_rag_agent_executor.ainvoke({"input": query})


@app.get("/")
async def get_status():
    return {"status": "running"}


@app.post("/hospital-rag-agent")
async def ask_hospital_agent(query: HospitalQueryInput) -> HospitalQueryOutput:
    query_response = await invoke_agent_with_retry(query.text)
    query_response["intermediate_steps"] = [
        str(s) for s in query_response["intermediate_steps"]
    ]

    return query_response


@app.post("/upload-docx")
async def upload_docx(file: UploadFile = File(...)) -> dict:
    if not file.filename.lower().endswith(".docx"):
        raise HTTPException(status_code=400, detail="Only .docx files are supported")

    content = await file.read()
    text = docx_to_text(content)
    if not text.strip():
        raise HTTPException(status_code=400, detail="Uploaded document contains no text")

    doc_id = str(uuid4())
    entry = embed_and_store(text, doc_id)

    return {"status": "ok", "id": entry["id"], "text_snippet": entry["text"][:200]}
