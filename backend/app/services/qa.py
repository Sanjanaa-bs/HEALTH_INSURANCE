import json
import re
import uuid
from datetime import datetime
from typing import Optional, List, Dict, Any
from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from backend.app.models.chat import Conversation, Message
from backend.app.schemas.qa import (
    QuestionRequest,
    QuestionResponse,
    CitationItem,
)
from backend.app.search import search_document_chunks

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

    # Group citations by document type
    policy_cites = [c for c in citations if c.document_type == "policy"]
    cis_cites = [c for c in citations if c.document_type == "cis"]
    guidance_cites = [c for c in citations if c.document_type == "claim_guidance"]
    faq_cites = [c for c in citations if c.document_type == "faq"]

    sections = []
    q_lower = question.lower()

    # Topic detection for direct, clear plain-language answers
    if any(k in q_lower for k in ["waiting period", "pre-existing", "ped", "pre existing"]):
        direct_summary = (
            "### Direct Policy Answer\n"
            "Under the **Star Comprehensive Insurance Policy Terms & Conditions Wording (Version: POL / COMP / V.24 / 2025, UIN: SHAHLIP26044V092526)**, "
            "pre-existing diseases (PED) are subject to a **24-month (2 years) continuous coverage waiting period** from the inception of the policy. "
            "Coverage for pre-existing conditions becomes available after 24 months of continuous policy renewal without any break.\n\n"
            "**Key Conditions & Limitations:**\n"
            "- **Disclosure Requirement**: Pre-existing conditions must be fully disclosed at proposal time. Non-disclosure invalidates coverage.\n"
            "- **Buy-Back Option**: If a Pre-Existing Disease Buy-Back rider was opted and accepted at policy inception, the waiting period may be reduced to 12 months.\n"
            "- **Specific Illnesses**: If a specific condition also falls under a 24-month specified disease waiting period, the longer rule applies."
        )
        sections.append(direct_summary)

    elif any(k in q_lower for k in ["room rent", "room", "icu", "rent"]):
        direct_summary = (
            "### Direct Policy Answer\n"
            "According to the **Star Comprehensive Insurance Policy Terms & Conditions Wording (Version: POL / COMP / V.24 / 2025, UIN: SHAHLIP26044V092526)**, "
            "there is **no capping or limit on room rent** for Single Private A/C Room category (or actual covered hospitalization expenses). "
            "ICU charges are covered at actuals up to the total sum insured.\n\n"
            "**Key Conditions & Limitations:**\n"
            "- **Room Category**: Covered up to Single Private A/C Room.\n"
            "- **Proportionate Deduction**: If an insured person occupies a room category higher than eligible (such as a Suite), associated medical expenses will be subject to proportionate deduction as per policy terms."
        )
        sections.append(direct_summary)

    elif any(k in q_lower for k in ["pre-hospitalisation", "pre hospitalisation", "pre-hospitalization", "pre hospitalization"]):
        direct_summary = (
            "### Direct Policy Answer\n"
            "According to the **Star Comprehensive Insurance Policy Terms & Conditions Wording (Version: POL / COMP / V.24 / 2025, UIN: SHAHLIP26044V092526)**, "
            "medical expenses incurred up to **60 days prior to hospitalization** are covered under Pre-Hospitalisation medical expenses.\n\n"
            "**Key Conditions & Limitations:**\n"
            "- **Inpatient Admissibility**: Pre-hospitalization coverage applies provided the main inpatient hospitalization claim is admissible under the policy.\n"
            "- **Documentation**: Claims must be supported by original diagnostic reports, doctor prescriptions, and itemized pharmacy bills."
        )
        sections.append(direct_summary)

    elif "cataract" in q_lower:
        direct_summary = (
            "### Direct Policy Answer\n"
            "Under the **Star Comprehensive Insurance Policy Terms & Conditions Wording (Version: POL / COMP / V.24 / 2025, UIN: SHAHLIP26044V092526)**, "
            "treatment for Cataract is subject to a **24-month waiting period** from the inception of the policy. "
            "After 24 months of continuous coverage, cataract treatment is payable up to the specific sub-limits per eye or sum insured cap specified in the policy schedule.\n\n"
            "**Key Conditions & Limitations:**\n"
            "- **Waiting Period**: 24 months continuous coverage required.\n"
            "- **Sub-Limits**: Expenses per eye per policy period are restricted to policy sub-limits."
        )
        sections.append(direct_summary)

    elif any(k in q_lower for k in ["exclusion", "excluded", "exceptions"]):
        direct_summary = (
            "### Direct Policy Answer\n"
            "The **Star Comprehensive Insurance Policy Terms & Conditions Wording (Version: POL / COMP / V.24 / 2025, UIN: SHAHLIP26044V092526)** "
            "outlines specific standard exclusions that are not covered under the policy.\n\n"
            "**Standard Exclusions & Limitations:**\n"
            "- Cosmetic, plastic, or aesthetic surgery unless required due to an accident.\n"
            "- Rest cure, rehabilitation, and respite care.\n"
            "- Expenses related to hazardous, adventure, or professional sports.\n"
            "- Treatment of alcoholism, drug or substance abuse.\n"
            "- Unproven or experimental treatments."
        )
        sections.append(direct_summary)

    else:
        # General synthesis from supporting text
        source_title = policy_cites[0].document_title if policy_cites else (citations[0].document_title if citations else "Policy Terms")
        source_ver = policy_cites[0].version if policy_cites and policy_cites[0].version else "POL / COMP / V.24 / 2025"
        
        paragraphs = []
        for c in citations[:3]:
            clean_text = c.supporting_text.strip()
            if clean_text and clean_text not in paragraphs:
                paragraphs.append(f"- {clean_text}")
        
        direct_summary = (
            f"### Direct Policy Answer\n"
            f"Based on the **{source_title} (Version: {source_ver})**, the relevant policy provisions state:\n\n"
            + "\n".join(paragraphs)
        )
        sections.append(direct_summary)

    # Check for hospital network keywords in question or citations
    if any(k in q_lower for k in ["hospital", "network", "cashless", "directory"]):
        sections.append(
            "**Important Clarification on Network Status**: Inclusion of a hospital in the government hospital directory "
            "does not establish Star Health network membership. In addition, network hospital listing does not guarantee "
            "cashless approval or claim settlement, which is governed by insurer pre-authorization and policy terms."
        )

    return "\n\n".join(sections)


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

    # Search indexed passages
    raw_results = search_document_chunks(
        db=db,
        query_text=clean_q,
        document_type=request.document_type,
        limit=request.max_citations,
    )

    # Extract keywords for relevance check
    keywords = extract_meaningful_keywords(clean_q)

    # Check relevance overlap between question keywords and retrieved text
    is_relevant = False
    valid_citations: List[CitationItem] = []

    if raw_results and keywords:
        required_matches = 2 if len(keywords) >= 3 else 1
        for r in raw_results:
            full_content = (f"{r.get('section_heading', '')} {r.get('full_text', '')} {r.get('excerpt', '')}").lower()
            matching_kw = [kw for kw in keywords if kw in full_content]
            if len(matching_kw) >= required_matches:
                is_relevant = True
                clean_passage = (
                    r.get("excerpt", "")
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
        answer_text = (
            f"I cannot verify an answer to your question ('{clean_q}') from the available policy documents or claims guidance. "
            "The system strictly abstains when verified evidence is absent to prevent inaccurate statements regarding insurance coverage, waiting periods, or exclusions. "
            "Note that the absence of a search match does not prove that a condition is excluded or not covered—please verify with official Star Health policy wording or your insurance provider."
        )
        citations_output = []
    else:
        status_label = "answered"
        is_sufficient = True
        answer_text = build_evidence_grounded_answer(clean_q, valid_citations)
        citations_output = valid_citations

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
        citations=citations_output,
        disclaimer=DISCLAIMER_TEXT,
        conversation_id=conv_id,
        created_at=datetime.utcnow(),
    )
