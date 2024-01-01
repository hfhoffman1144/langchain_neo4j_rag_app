import os
import logging
from fastapi import FastAPI
from agents.hospital_rag_agent import hospital_rag_agent
from models.hospital_rag_query import HospitalQueryInput, HospitalQueryOutput
from utils.async_utils import async_retry

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s]: %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)


LOGGER = logging.getLogger(__name__)

agent_model_name = os.getenv("HOSPITAL_RAG_AGENT_MODEL")
cypher_generation_model_name = os.getenv("HOSPITAL_CYPHER_MODEL")
rag_qa_model_name = os.getenv("HOSPITAL_QA_MODEL")

LOGGER.info(f"Using {agent_model_name} as the agent model")
LOGGER.info(f"Using {cypher_generation_model_name} to generate Cypher queries")
LOGGER.info(f"Using {rag_qa_model_name} for RAG QA")

app = FastAPI(
    title="Hospital Chatbot",
    description="Endpoints for a hospital graph RAG chatbot",
)

@async_retry(max_retries=10, delay=1)
async def invoke_agent_with_retry(query: str):
    """Retry the agent if a tool fails to run. This can help when there
    are intermitten connect issues to external APIs."""

    return await hospital_rag_agent.ainvoke({"input":query})


@app.get("/")
async def get_status():
    return {"status": "running"}


@app.post("/hospital-rag-agent")
async def query_hospital_agent(query: HospitalQueryInput) -> HospitalQueryOutput:
    
    query_response = await invoke_agent_with_retry(query.text)
    query_response['intermediate_steps'] = [str(s) for s in query_response['intermediate_steps']]
    
    return query_response