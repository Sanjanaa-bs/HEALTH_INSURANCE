import json
import re
import uuid
from datetime import datetime, timezone
from typing import Optional, List, Dict, Any
from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from backend.app.models.chat import Conversation, Message
from backend.app.schemas.qa import (
    QuestionRequest,
    QuestionResponse,
    CitationItem,
)
from backend.app.config import settings
from backend.app.search import search_document_chunks
from backend.app.services.retrieval import hybrid_search
from backend.app.services.llm_provider import get_llm_provider

STOPWORDS = {
    "what", "is", "the", "for", "are", "about", "does", "say", "to", "of",
    "in", "and", "a", "an", "policy", "tell", "me", "how", "can", "do",
    "it", "any", "which", "with", "from", "on", "under", "this", "that",
    "these", "those", "have", "has", "had", "be", "been", "being", "there",
    "cover", "covered", "coverage", "says", "mean", "means", "give", "gives",
    "before", "after", "related", "terms", "term", "high", "low", "provide",
    "provides", "provided", "details", "detail"
}

DISCLAIMER_TEXT = (
    "Disclaimer: This guidance is grounded strictly in indexed source documents. "
    "Hospital directory listing does not guarantee Star Health network membership, "
    "and network listing does not guarantee cashless authorization or claim approval. "
    "This does not substitute for professional medical advice or official insurer pre-authorization."
)

NETWORK_STATUS_CLARIFICATION = (
    "**Important Clarification on Network Status**: The national hospital directory and the local insurer sample are separate datasets. "
    "A directory entry or absence from this sample does not establish current Star Health network status, and a network listing "
    "does not guarantee cashless approval. Confirm current participation and authorization with Star Health."
)


def extract_meaningful_keywords(text_str: str) -> List[str]:
    """Extract non-trivial query keywords for relevance verification."""
    expanded = text_str.lower()
    expanded = re.sub(r"\b(before|prior to)\s+(hospitali[sz]ation)\b", "prehospitalization", expanded)
    expanded = re.sub(r"\b(after|post|following)\s+(hospitali[sz]ation)\b", "posthospitalization", expanded)
    tokens = [w.lower() for w in re.findall(r"\b[a-zA-Z0-9]+\b", expanded)]
    return [t for t in tokens if t not in STOPWORDS and len(t) > 2]


def build_evidence_grounded_answer(
    question: str,
    citations: List[CitationItem],
) -> str:
    """
    Construct a clean, synthesized answer strictly from retrieved citations,
    separating plain-language explanations from citation cards.
    """
    if not citations:
        return (
            f"I cannot verify an answer to your question ('{question}') from the available policy documents or claims guidance. "
            "The system strictly abstains when verified evidence is absent to prevent inaccurate statements regarding insurance coverage, waiting periods, or exclusions. "
            "Note that the absence of a search match does not prove that a condition is excluded or not covered—please verify with official Star Health policy wording or your insurance provider."
        )

    # Keep the offline answer strictly extractive: topic-specific summaries can
    # introduce conditions or limits that are not present in the retrieved clauses.
    passages = []
    for citation in citations:
        passage = citation.supporting_text.strip()
        if passage and passage not in passages:
            passages.append(passage)

    if not passages:
        return (
            f"I cannot verify an answer to your question ('{question}') from the retrieved evidence. "
            "Please check the cited source document or contact the insurer."
        )

    answer = "### Direct Policy Answer\n\n" + "\n\n".join(f"- {passage}" for passage in passages)
    answer += "\n\n**Sources:**\n" + "\n".join(
        f"- {citation.document_title}"
        + (f" (Version: {citation.version})" if citation.version else "")
        for citation in citations
    )
    if any(keyword in question.lower() for keyword in ("hospital", "network", "cashless", "directory")):
        answer += "\n\n" + NETWORK_STATUS_CLARIFICATION
    return answer


def answer_insurance_question(
    db: Session,
    request: QuestionRequest,
) -> QuestionResponse:
    """
    Core question answering service:
    1. Validates query.
    2. Retrieves matching document passages from FTS5 index.
    3. Checks keyword relevance to detect unsupported questions.
    4. Builds grounded answer with exact citations or abstains.
    5. Persists conversation and message history.
    """
    clean_q = request.question.strip()
    if not clean_q:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="Question cannot be empty or whitespace only.",
        )

    # Execute Hybrid Retrieval (BM25 Keyword + Vector Semantic Search)
    try:
        raw_results, retrieval_mode = hybrid_search(
            db=db,
            query_text=clean_q,
            document_type=request.document_type,
            top_k=request.max_citations,
            alpha=settings.RAG_HYBRID_ALPHA,
        )
    except Exception:
        # Safe fallback to standard BM25 retrieval
        raw_results = search_document_chunks(
            db=db,
            query_text=clean_q,
            document_type=request.document_type,
            limit=request.max_citations,
        )
        retrieval_mode = "keyword"

    # Extract keywords for relevance check
    keywords = extract_meaningful_keywords(clean_q)

    # Check relevance overlap between question keywords and retrieved text
    is_relevant = False
    valid_citations: List[CitationItem] = []

    if raw_results and keywords:
        required_matches = 2 if len(keywords) >= 3 else 1
        for r in raw_results:
            full_content = (f"{r.get('section_heading', '')} {r.get('full_text', '')} {r.get('supporting_text', '')} {r.get('excerpt', '')}").lower()
            matching_kw = [kw for kw in keywords if kw in full_content]
            if len(matching_kw) >= required_matches:
                is_relevant = True
                clean_passage = (
                    r.get("supporting_text")
                    or r.get("excerpt", "")
                    .replace("<b>", "")
                    .replace("</b>", "")
                    .strip()
                )
                valid_citations.append(
                    CitationItem(
                        chunk_id=r["chunk_id"],
                        document_id=r["document_id"],
                        document_title=r["document_title"],
                        document_type=r["document_type"],
                        version=r.get("version"),
                        page_number=r.get("page_number"),
                        printed_page_number=r.get("printed_page_number"),
                        page_label=r.get("page_label"),
                        section_heading=r.get("section_heading"),
                        supporting_text=clean_passage,
                        content_hash=r.get("content_hash", ""),
                    )
                )

    # Determine status & synthesize answer
    if not is_relevant or not valid_citations:
        status_label = "insufficient_evidence"
        is_sufficient = False
        generation_mode = "Keyword Retrieval Fallback"
        llm_provider_name = "fallback"
        answer_text = (
            f"I cannot verify an answer to your question ('{clean_q}') from the available policy documents or claims guidance. "
            "The system strictly abstains when verified evidence is absent to prevent inaccurate statements regarding insurance coverage, waiting periods, or exclusions. "
            "Note that the absence of a search match does not prove that a condition is excluded or not covered—please verify with official Star Health policy wording or your insurance provider."
        )
        citations_output = []
    else:
        status_label = "answered"
        is_sufficient = True
        citations_output = valid_citations

        # Attempt Generative RAG via LLM provider if configured
        llm = get_llm_provider()
        llm_answer, used_llm = llm.generate_answer(
            clean_q,
            [c.model_dump() for c in valid_citations],
        )

        if llm_answer:
            # Keep source identity and the mandatory network-status warning visible
            # regardless of which language model generated the answer.
            source_lines = list(dict.fromkeys(
                f"- {citation.document_title}"
                + (f" (Version: {citation.version})" if citation.version else "")
                for citation in valid_citations
            ))
            answer_text = llm_answer + "\n\n**Sources:**\n" + "\n".join(source_lines)
            if any(keyword in clean_q.lower() for keyword in ("hospital", "network", "cashless", "directory")):
                answer_text += "\n\n" + NETWORK_STATUS_CLARIFICATION
            generation_mode = "RAG + LLM"
            llm_provider_name = used_llm
        else:
            answer_text = build_evidence_grounded_answer(clean_q, valid_citations)
            generation_mode = "Hybrid Retrieval" if retrieval_mode in ["hybrid", "vector"] else "Keyword Retrieval Fallback"
            llm_provider_name = "fallback"

    # Manage conversation session
    conv_id = request.conversation_id or str(uuid.uuid4())
    existing_conv = db.query(Conversation).filter(Conversation.id == conv_id).first()
    if not existing_conv:
        existing_conv = Conversation(id=conv_id, title=clean_q[:80])
        db.add(existing_conv)
        db.flush()

    # Save user message
    user_msg = Message(
        conversation_id=conv_id,
        role="user",
        content=clean_q,
    )
    # Save assistant message
    asst_msg = Message(
        conversation_id=conv_id,
        role="assistant",
        content=answer_text,
        citations=json.dumps([c.model_dump() for c in citations_output]),
    )
    db.add_all([user_msg, asst_msg])
    db.commit()

    return QuestionResponse(
        question=clean_q,
        answer=answer_text,
        status=status_label,
        is_sufficient_evidence=is_sufficient,
        provider="retrieval_grounded_guidance",
        generation_mode=generation_mode,
        retrieval_mode=retrieval_mode,
        embedding_provider=settings.EMBEDDING_PROVIDER,
        llm_provider=llm_provider_name,
        citations=citations_output,
        disclaimer=DISCLAIMER_TEXT,
        conversation_id=conv_id,
        created_at=datetime.now(timezone.utc),
    )
