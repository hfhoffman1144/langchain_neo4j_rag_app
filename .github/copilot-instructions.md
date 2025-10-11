## Repository purpose (short)

This repository is a LangChain-based RAG chatbot demo that combines
unstructured semantic search (OpenAI embeddings + Neo4j vector index)
and structured Text-to-Cypher query generation against a Neo4j graph.
The system is divided into small Docker services (ETL, API, frontend, portal)
defined in `docker-compose.yml`.

## Big-picture architecture

- hospital_neo4j_etl: CSV -> Neo4j loader. Key file: `hospital_neo4j_etl/src/hospital_bulk_csv_write.py`.
- chatbot_api: async FastAPI service exposing `/hospital-rag-agent`. Key files:
  - `chatbot_api/src/main.py` (entrypoint)
  - `chatbot_api/src/agents/hospital_rag_agent.py` (agent + tools)
  - `chatbot_api/src/chains/*` (Cypher & vector chains)
- chatbot_frontend: Streamlit demo at port 8501 (see `chatbot_frontend/src/main.py`).
- cypher_example_portal: Streamlit portal to upload example Q→Cypher pairs for dynamic few-shot prompting. Key: `cypher_example_portal/src/main.py` and `cypher_example_portal/src/graph_utils.py`.

Data flow note: ETL writes nodes and example questions into Neo4j. The API agent either calls a review vector-chain (unstructured) or generates/runs Cypher (structured) via chains in `chatbot_api/src/chains`.

## Key developer workflows (commands & env)

- Environment: create a `.env` in repo root. See `README.md` for required keys (NEO4J_*, OPENAI_API_KEY, CSV paths, model names).
- Local full-run (recommended): Docker Compose builds and wires services. From repo root run:

```pwsh
docker-compose up --build
```

- After startup access:
  - API docs: http://localhost:8000/docs
  - Frontend Streamlit: http://localhost:8501/
  - Cypher portal: http://localhost:8502/

## Project-specific conventions and patterns

- Services are small and self-contained under top-level folders (each has its own `pyproject.toml` and Dockerfile).
- FastAPI endpoints use Pydantic-like models in `chatbot_api/src/models` (e.g. `HospitalQueryInput`) — return value shapes are expected by tests.
- Agent design: tools are plain functions decorated with `@tool` in `chatbot_api/src/agents/hospital_rag_agent.py`. Tools should accept the prompt/argument string exactly as the agent will pass it (see docstrings in the file).
- Chains: Chains live under `chatbot_api/src/chains` and are invoked synchronously via `invoke(...)` or asynchronously via the agent executor. When adding a chain, mirror existing pattern: a callable that accepts a single string question and returns a string result.

## Integration points & external dependencies

- Neo4j (configured via `NEO4J_URI`, `NEO4J_USERNAME`, `NEO4J_PASSWORD`) — ETL expects access to a Neo4j database and uses `neo4j` driver to load CSVs.
- OpenAI (configured via `OPENAI_API_KEY`) — used for embeddings and LLM calls (`langchain_openai.ChatOpenAI`).
- Docker & Docker Compose wire services together and provide `host.docker.internal` for cross-container access to host URLs.

## Tests & quick checks

- Tests live at top-level `tests/` and in sub-packages; project uses `pytest`. Run tests locally (if using Poetry or venv) with:

```pwsh
pytest -q
```

If running in Docker containers the test workflow is manual: start services then run tests that call the API endpoints.

## What to change & where to look for examples

- Add new API endpoints under `chatbot_api/src/main.py` and mirror model classes in `chatbot_api/src/models`.
- Add new tools to the agent by creating a function with `@tool` and adding it to `agent_tools` in `chatbot_api/src/agents/hospital_rag_agent.py`.
- To change or extend Cypher generation, update `chatbot_api/src/chains/hospital_cypher_chain.py` and any prompt templates in `chatbot_api/src/langchain_custom/graph_qa`.

## Safety and constraints for an AI agent editing this repo

- Preserve existing API request/response schemas (see `HospitalQueryInput` in `chatbot_api/src/models/hospital_rag_query.py`). Tests depend on these shapes.
- Do not commit secrets. `.env` should not be added to git.
- Keep Docker service names and port mappings in `docker-compose.yml` unchanged unless you update README and tests that assume those ports.

## Quick references (examples)

- To see how the agent calls tools, read `chatbot_api/src/agents/hospital_rag_agent.py` — tools call `reviews_vector_chain.invoke(question)` and `hospital_cypher_chain.invoke(question)`.
- ETL creates uniqueness constraints and loads CSVs in `hospital_neo4j_etl/src/hospital_bulk_csv_write.py` — follow its CSV column names when producing datasets.

If anything here is unclear or you want more detail on a section (tests, chains, or Docker workflows), tell me which part to expand and I will iterate.
