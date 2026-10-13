import logging
from typing import Any, Dict, List, Optional, Tuple

import httpx

from backend.app.config import settings

logger = logging.getLogger(__name__)

SYSTEM_PROMPT = """You are an assistant answering questions about the Star Health Comprehensive Insurance Policy.
Use only the supplied evidence passages. Distinguish policy terms from general guidance.
Include relevant limitations stated in the evidence. Never promise claim approval or invent clauses,
limits, waiting periods, quotations, or page numbers. If evidence is insufficient or conflicting,
say so. Format the response in Markdown with a direct answer and key conditions when supported."""


class BaseLLMProvider:
    """Interface for evidence-grounded answer generation."""

    def generate_answer(
        self, question: str, evidence_passages: List[Dict[str, Any]]
    ) -> Tuple[Optional[str], str]:
        raise NotImplementedError


def _evidence_text(evidence_passages: List[Dict[str, Any]]) -> str:
    return "\n\n".join(
        f"Passage {idx + 1} ({p.get('document_title', 'Policy')} - {p.get('page_label', '')}):\n"
        f"{p.get('supporting_text', '')}"
        for idx, p in enumerate(evidence_passages)
    )


class OpenAILLMProvider(BaseLLMProvider):
    """OpenAI chat completions provider."""

    def __init__(self, api_key: str, model_name: str = "gpt-4o-mini"):
        self.api_key = api_key
        self.model_name = model_name

    def generate_answer(
        self, question: str, evidence_passages: List[Dict[str, Any]]
    ) -> Tuple[Optional[str], str]:
        if not self.api_key:
            return None, "fallback"
        try:
            response = httpx.post(
                "https://api.openai.com/v1/chat/completions",
                headers={"Authorization": f"Bearer {self.api_key}"},
                json={
                    "model": self.model_name,
                    "messages": [
                        {"role": "system", "content": SYSTEM_PROMPT},
                        {
                            "role": "user",
                            "content": f"Question: {question}\n\nRetrieved Evidence Passages:\n{_evidence_text(evidence_passages)}",
                        },
                    ],
                    "temperature": 0.2,
                    "max_tokens": 600,
                },
                timeout=15.0,
            )
            response.raise_for_status()
            answer = response.json()["choices"][0]["message"]["content"].strip()
            return (answer, "openai") if answer else (None, "fallback")
        except Exception as exc:
            logger.warning("OpenAI LLM provider error: %s", exc)
            return None, "fallback"


class GeminiLLMProvider(BaseLLMProvider):
    """Google Gemini generateContent provider."""

    def __init__(self, api_key: str, model_name: str = "gemini-1.5-flash"):
        self.api_key = api_key
        self.model_name = model_name

    def generate_answer(
        self, question: str, evidence_passages: List[Dict[str, Any]]
    ) -> Tuple[Optional[str], str]:
        if not self.api_key:
            return None, "fallback"
        try:
            response = httpx.post(
                f"https://generativelanguage.googleapis.com/v1beta/models/{self.model_name}:generateContent",
                params={"key": self.api_key},
                json={
                    "systemInstruction": {"parts": [{"text": SYSTEM_PROMPT}]},
                    "contents": [{
                        "parts": [{
                            "text": f"Question: {question}\n\nRetrieved Evidence Passages:\n{_evidence_text(evidence_passages)}"
                        }]
                    }],
                    "generationConfig": {"temperature": 0.2, "maxOutputTokens": 600},
                },
                timeout=15.0,
            )
            response.raise_for_status()
            answer = response.json()["candidates"][0]["content"]["parts"][0]["text"].strip()
            return (answer, "gemini") if answer else (None, "fallback")
        except Exception as exc:
            logger.warning("Gemini LLM provider error: %s", exc)
            return None, "fallback"


class OllamaLLMProvider(BaseLLMProvider):
    """Local Ollama chat provider; no cloud credentials are required."""

    def __init__(self, base_url: str, model_name: str):
        self.base_url = base_url.rstrip("/")
        self.model_name = model_name

    def generate_answer(
        self, question: str, evidence_passages: List[Dict[str, Any]]
    ) -> Tuple[Optional[str], str]:
        try:
            response = httpx.post(
                f"{self.base_url}/api/chat",
                json={
                    "model": self.model_name,
                    "stream": False,
                    "messages": [
                        {"role": "system", "content": SYSTEM_PROMPT},
                        {
                            "role": "user",
                            "content": f"Question: {question}\n\nRetrieved Evidence Passages:\n{_evidence_text(evidence_passages)}",
                        },
                    ],
                    "options": {"temperature": 0.2},
                },
                timeout=httpx.Timeout(60.0, connect=1.0),
            )
            response.raise_for_status()
            answer = response.json().get("message", {}).get("content", "").strip()
            return (answer, "ollama") if answer else (None, "fallback")
        except Exception as exc:
            logger.warning("Ollama provider error: %s", exc)
            return None, "fallback"


def get_llm_provider(provider_name: Optional[str] = None) -> BaseLLMProvider:
    """Build the configured provider, falling back when credentials are absent."""
    name = (provider_name or settings.LLM_PROVIDER).lower()
    if name in {"openai", "auto"} and settings.OPENAI_API_KEY:
        return OpenAILLMProvider(settings.OPENAI_API_KEY, settings.LLM_MODEL_NAME)
    if name in {"gemini", "auto"} and settings.GEMINI_API_KEY:
        return GeminiLLMProvider(settings.GEMINI_API_KEY)
    if name in {"ollama", "auto"}:
        return OllamaLLMProvider(settings.OLLAMA_BASE_URL, settings.OLLAMA_MODEL_NAME)
    return OpenAILLMProvider(api_key="")
