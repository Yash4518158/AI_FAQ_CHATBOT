import os
import requests

OLLAMA_URL = os.getenv("OLLAMA_BASE_URL", "http://host.docker.internal:11434")
LLM_MODEL = os.getenv("OLLAMA_LLM_MODEL", "llama3.2:3b")
LLM_TIMEOUT = int(os.getenv("OLLAMA_LLM_TIMEOUT_SECONDS", "120"))

def check_llm_model():
    """Verify the configured LLM is installed in Ollama."""
    try:
        res = requests.get(f"{OLLAMA_URL}/api/tags", timeout=5)
        res.raise_for_status()
        models = [m['name'] for m in res.json().get('models', [])]
        if not any(m.startswith(LLM_MODEL.split(":")[0]) for m in models):
            raise ValueError(f"LLM Model '{LLM_MODEL}' is not installed. Run: ollama pull {LLM_MODEL}")
    except requests.exceptions.RequestException as e:
        raise ValueError(f"Ollama is unreachable at {OLLAMA_URL}: {str(e)}")

def generate_answer(prompt: str) -> str:
    """Generates an answer using the local Ollama LLM."""
    if not prompt.strip():
        raise ValueError("Prompt cannot be empty.")
        
    check_llm_model()
    
    try:
        res = requests.post(f"{OLLAMA_URL}/api/generate", json={
            "model": LLM_MODEL,
            "prompt": prompt,
            "stream": False
        }, timeout=LLM_TIMEOUT)
        
        if res.status_code != 200:
            raise ValueError(f"Ollama error {res.status_code}: {res.text}")
            
        res.raise_for_status()
        
        data = res.json()
        answer = data.get('response', '')
        
        if not answer.strip():
            raise ValueError("Ollama returned an empty answer.")
            
        return answer
        
    except requests.exceptions.Timeout:
        raise ValueError(f"LLM generation timed out after {LLM_TIMEOUT} seconds.")
    except requests.exceptions.RequestException as e:
        raise ValueError(f"Failed to generate answer from LLM: {str(e)}")
