from fastapi import FastAPI
from agents.hospital_rag_agent import hospital_rag_agent
from models.hospital_rag_query import HospitalQuery

app = FastAPI(
    title="Hospital Chatbot",
    description="Endpoints for a hospital graph RAG chatbot",
)

@app.get("/")
async def get_status():
    
    return {"status":"running"}


@app.post("/hospital-rag-agent")
async def query_hospital_agent(query: HospitalQuery):
    
    query_response = hospital_rag_agent.run(query.text)
    
    return query_response


