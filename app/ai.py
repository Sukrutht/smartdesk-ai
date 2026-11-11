"""Small, explicit Gemini REST client. The API key is read only from environment."""
import httpx
from app.config import settings

BASE_URL = "https://generativelanguage.googleapis.com/v1beta"


class AIConfigurationError(RuntimeError):
    pass


class AIServiceError(RuntimeError):
    pass


def _require_key() -> str:
    if not settings.gemini_api_key:
        raise AIConfigurationError("Gemini is not configured. Add GEMINI_API_KEY to your environment.")
    return settings.gemini_api_key


async def embed_text(text: str, task_type: str) -> list[float]:
    key = _require_key()
    url = f"{BASE_URL}/models/{settings.gemini_embedding_model}:embedContent"
    payload = {
        "model": f"models/{settings.gemini_embedding_model}",
        "content": {"parts": [{"text": text}]},
        "taskType": task_type,
        "outputDimensionality": 768,
    }
    try:
        async with httpx.AsyncClient(timeout=45) as client:
            response = await client.post(url, params={"key": key}, json=payload)
            response.raise_for_status()
            return response.json()["embedding"]["values"]
    except (httpx.HTTPError, KeyError, ValueError) as exc:
        raise AIServiceError(f"Embedding request failed: {exc}") from exc


async def generate_text(prompt: str) -> str:
    key = _require_key()
    url = f"{BASE_URL}/models/{settings.gemini_model}:generateContent"
    payload = {"contents": [{"role": "user", "parts": [{"text": prompt}]}],
               "generationConfig": {"temperature": 0.2, "maxOutputTokens": 900}}
    try:
        async with httpx.AsyncClient(timeout=60) as client:
            response = await client.post(url, params={"key": key}, json=payload)
            response.raise_for_status()
            data = response.json()
            return data["candidates"][0]["content"]["parts"][0]["text"].strip()
    except (httpx.HTTPError, KeyError, IndexError, ValueError) as exc:
        raise AIServiceError(f"Text generation request failed: {exc}") from exc


async def classify_ticket(title: str, description: str) -> dict:
    prompt = f"""You are an IT service-desk triage assistant. Analyze this ticket.
Return ONLY valid JSON with keys category, priority, suggested_response.
category must be one of: Access, Network, Software, Hardware, Data, Other.
priority must be one of: Low, Medium, High, Critical.
Be conservative: do not claim a fix has been performed. The suggested response should ask for useful diagnostic details or give safe first checks.
Ticket title: {title}
Ticket description: {description}
"""
    import json
    raw = await generate_text(prompt)
    try:
        result = json.loads(raw.replace("```json", "").replace("```", "").strip())
        if result.get("category") not in {"Access", "Network", "Software", "Hardware", "Data", "Other"}:
            raise ValueError("Invalid category")
        if result.get("priority") not in {"Low", "Medium", "High", "Critical"}:
            raise ValueError("Invalid priority")
        return result
    except (json.JSONDecodeError, ValueError, AttributeError) as exc:
        raise AIServiceError("The AI returned an invalid ticket classification. Please retry.") from exc
