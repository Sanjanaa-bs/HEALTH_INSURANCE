import json
import logging
from typing import List, Dict, Any, Optional, Tuple
import httpx

from backend.app.config import settings

logger = logging.getLogger(__name__)

SYSTEM_PROMPT = """You are an official Health Insurance Assistant for Star Health Comprehensive Insurance Policy.
You must answer questions strictly and only using the provided policy evidence passages.

Strict Rules:
1. Answer in simple, plain, understandable language.
2. Distinguish formal policy terms & conditions from general guidance.
3. Explicitly include relevant limitations, exclusions, and waiting periods mentioned in the evidence.
4. Never make claim-approval promises or guarantees.
5. Never fabricate policy clauses, waiting periods, coverage limits, source quotations, or page numbers.
6. Never treat a national hospital directory entry as proof of Star Health network membership.
7. If the provided evidence is insufficient or conflicting, clearly state that evidence is insufficient and abstain from guessing.

Formulate your response in Markdown with clear sections:
### Direct Policy Answer
[Clear plain-language explanation]

**Key Conditions & Limitations:**
- [Bullet points of limitations/conditions]
"""


class BaseLLMProvider:
    """Abstract interface for LLM answer generation."""

    def generate_answer(
        self,
        question: str,
        evidence_passages: List[Dict[str, Any]],
    ) -> Tuple[Optional[str], str]:
        """
        Generate grounded answer from evidence passages.
        Returns (answer_text, provider_name).
        """
        raise NotImplementedError


class OpenAILLMProvider(BaseLLMProvider):
    """OpenAI API provider implementation using httpx."""

    def __init__(self, api_key: str, model_name: str = "gpt-4o-mini"):
        self.api_key = api_key
        self.model_name = model_name

    def generate_answer(
        self,
        question: str,
        evidence_passages: List[Dict[str, Any]],
    ) -> Tuple[Optional[str], str]:
        if not self.api_key:
            return None, "fallback"

        evidence_text = "\n\n".join([
            f"Passage {idx+1} ({p.get('document_title', 'Policy')} - {p.get('page_label', '')}):\n{p.get('supporting_text', '')}"
            for idx, p in enumerate(evidence_passages)
        ])

        user_content = f"Question: {question}\n\nRetrieved Evidence Passages:\n{evidence_text}"

        try:
            headers = {
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json",
            }
            payload = {
                "model": self.model_name,
                "messages": [
                    {"role": "system", "content": SYSTEM_PROMPT},
                    {"role": "user", "content": user_content},
                ],
                "temperature": 0.2,
                "max_tokens": 600,
            }
            with httpx.Client(timeout=15.0) as client:
                res = client.post("https://api.openai.com/v1/chat/completions", headers=headers, json=payload)
                if res.status_code == 200:
                    data = res.json()
                    ans = data["choices"][0]["message"]["content"].strip()
                    return ans, "openai"
                else:
                    logger.warning(f"OpenAI API error {res.status_code}: {res.text}")
                    return None, "fallback"
        except Exception as e:
            logger.error(f"OpenAI LLM provider error: {e}")
            return None, "fallback"


class GeminiLLMProvider(BaseLLMProvider):
    """Google Gemini API provider implementation using httpx."""

    def __init__(self, api_key: str, model_name: str = "gemini-1.5-flash"):
        self.api_key = api_key
        self.model_name = model_name

    def generate_answer(
        self,
        question: str,
        evidence_passages: List[Dict[str, Any]],
    ) -> Tuple[Optional[str], str]:
        if not self.api_key:
            return None, "fallback"

        evidence_text = "\n\n".join([
            f"Passage {idx+1} ({p.get('document_title', 'Policy')} - {p.get('page_label', '')}):\n{p.get('supporting_text', '')}"
            for idx, p in enumerate(evidence_passages)
        ])

        prompt = f"{SYSTEM_PROMPT}\n\nQuestion: {question}\n\nRetrieved Evidence Passages:\n{evidence_text}"

        try:
            url = f"https://generativelanguage.googleapis.com/v1beta/models/{self.model_name}:generateContent?key={self.api_key}"
            payload = {
                "contents": [{"parts": [{"text": prompt}]}],
                "generationConfig": {"temperature": 0.2, "maxOutputTokens": 600},
            }
            with httpx.Client(timeout=15.0) as client:
                res = client.post(url, json=payload)
                if res.status_code == 200:
                    data = res.json()
                    ans = data["candidates"][0]["content"]["parts"][0]["text"].strip()
                    return ans, "gemini"
                else:
                    logger.warning(f"Gemini API error {res.status_code}: {res.text}")
                    return None, "fallback"
        except Exception as e:
            logger.error(f"Gemini LLM provider error: {e}")
            return None, "fallback"


def get_llm_provider(provider_name: Optional[str] = None) -> BaseLLMProvider:
    """Factory to instantiate LLM provider based on environment settings and API key availability."""
    name = (provider_name or settings.LLM_PROVIDER).lower()

    if name in ["openai", "auto"] and settings.OPENAI_API_KEY:
        return OpenAILLMProvider(api_key=settings.OPENAI_API_KEY, model_name=settings.LLM_MODEL_NAME)

    if name in ["gemini", "auto"] and settings.GEMINI_API_KEY:
        return GeminiLLMProvider(api_key=settings.GEMINI_API_KEY)

    # Fallback provider if no external credentials exist
    return OpenAILLMProvider(api_key="")
