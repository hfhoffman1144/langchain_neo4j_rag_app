import os
import requests

OLLAMA_URL = os.getenv("OLLAMA_URL", "http://localhost:11434")
OLLAMA_MODEL = os.getenv("HOSPITAL_AGENT_MODEL", "llama3.2")


def generate_with_ollama(prompt: str, model: str | None = None, max_tokens: int = 512) -> str:
    model = model or OLLAMA_MODEL
    url = f"{OLLAMA_URL}/api/generate"
    payload = {"model": model, "prompt": prompt, "max_tokens": max_tokens}
    resp = requests.post(url, json=payload, timeout=30)
    resp.raise_for_status()
    data = resp.json()
    # Ollama generate response shape may vary; try to extract text sensibly
    if isinstance(data, dict):
        # Some Ollama builds return {'results': [{'text': '...'}]}
        if "results" in data and isinstance(data["results"], list):
            return "".join([r.get("text", "") for r in data["results"]])
        if "text" in data:
            return data["text"]

    # Fallback: return raw JSON if unexpected
    return str(data)
