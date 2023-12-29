from retry import retry
from fastapi import FastAPI
from agents.hospital_rag_agent import hospital_rag_agent
from models.hospital_rag_query import HospitalQuery

app = FastAPI(
    title="Hospital Chatbot",
    description="Endpoints for a hospital graph RAG chatbot",
)

@retry(tries=10, delay=1)
def run_agent_with_retry(query: str):
    
    """ Retry the agent if a tool fails to run. This can help when there
    are intermitten connect issues to external APIs."""
    
    return hospital_rag_agent.run(query)

@app.get("/")
async def get_status():
    
    return {"status":"running"}


@app.post("/hospital-rag-agent")
async def query_hospital_agent(query: HospitalQuery):
    
    query_response = run_agent_with_retry(query.text)
    
    return query_response


