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
        async with httpx.AsyncClient(timeout=httpx.Timeout(45.0, connect=10.0)) as client:
            response = await client.post(url, headers={"x-goog-api-key": key}, json=payload)
            response.raise_for_status()
            return response.json()["embedding"]["values"]
    except httpx.HTTPStatusError as exc:
        try:
            detail = exc.response.json().get("error", {}).get("message", "Request rejected")
        except ValueError:
            detail = "Request rejected"
        raise AIServiceError(
            f"Gemini embedding failed (HTTP {exc.response.status_code}): {detail}"
        ) from None
    except (httpx.HTTPError, KeyError, ValueError) as exc:
        raise AIServiceError(
            f"Gemini embedding failed ({type(exc).__name__}). Check the service logs."
        ) from None


async def generate_text(prompt: str) -> str:
    key = _require_key()
    url = f"{BASE_URL}/models/{settings.gemini_model}:generateContent"
    payload = {
        "contents": [{"role": "user", "parts": [{"text": prompt}]}],
        "generationConfig": {"maxOutputTokens": 1024},
    }
    try:
        async with httpx.AsyncClient(timeout=httpx.Timeout(90.0, connect=10.0)) as client:
            response = await client.post(
                url,
                headers={"x-goog-api-key": key},
                json=payload,
            )
            response.raise_for_status()
            data = response.json()
            candidates = data.get("candidates") or []
            if not candidates:
                feedback = data.get("promptFeedback", {})
                reason = feedback.get("blockReason", "No candidate returned")
                raise AIServiceError(f"Gemini returned no text candidate: {reason}")
            parts = candidates[0].get("content", {}).get("parts", [])
            text_parts = [part["text"] for part in parts if isinstance(part.get("text"), str)]
            if not text_parts:
                raise AIServiceError("Gemini returned an empty text response.")
            return "\n".join(text_parts).strip()
    except httpx.HTTPStatusError as exc:
        try:
            detail = exc.response.json().get("error", {}).get("message", "Request rejected")
        except ValueError:
            detail = "Request rejected"
        raise AIServiceError(
            f"Gemini text generation failed (HTTP {exc.response.status_code}): {detail}"
        ) from None
    except httpx.ReadTimeout:
        raise AIServiceError(
            "Gemini text generation timed out after 90 seconds. Check Gemini API availability and service logs."
        ) from None
    except httpx.ConnectTimeout:
        raise AIServiceError(
            "Could not connect to Gemini within 10 seconds. Check outbound network access and service logs."
        ) from None
    except (httpx.HTTPError, ValueError) as exc:
        raise AIServiceError(
            f"Gemini text generation failed ({type(exc).__name__}). Check model access and service logs."
        ) from None


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
        if not isinstance(result.get("suggested_response"), str):
            raise ValueError("Invalid suggested response")
        return result
    except (json.JSONDecodeError, ValueError, AttributeError) as exc:
        raise AIServiceError("The AI returned an invalid ticket classification. Please retry.") from exc
