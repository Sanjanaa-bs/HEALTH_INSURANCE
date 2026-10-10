import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from backend.app.models.document import Document, DocumentChunk
from backend.app.models.chat import Conversation, Message


@pytest.fixture
def seed_qa_documents(db_session: Session):
    """Seed sample documents and chunks across policy, CIS, and guidance."""
    # 1. Full Policy
    p_doc = Document(
        title="Star Comprehensive Insurance Policy - Terms & Conditions Wording",
        document_type="policy",
        source_path="data/policies/Policy_Star_Comprehensive_clean.pdf",
        file_format="pdf",
        version="POL / COMP / V.24 / 2025 (UIN: SHAHLIP26044V092526)",
        is_processed=True,
    )
    # 2. CIS
    c_doc = Document(
        title="Star Comprehensive Insurance Policy - Customer Information Sheet (CIS)",
        document_type="cis",
        source_path="data/policies/CIS_Star.pdf",
        file_format="pdf",
        version="V.2 / 2025",
        is_processed=True,
    )
    # 3. Claims Guidance
    g_doc = Document(
        title="Star Cashless Claims Process Guide",
        document_type="claim_guidance",
        source_path="data/claim_guidance/star_cashless_claims.mhtml",
        file_format="mhtml",
        version="2025",
        is_processed=True,
    )
    db_session.add_all([p_doc, c_doc, g_doc])
    db_session.flush()

    # Chunks
    p_chunk = DocumentChunk(
        document_id=p_doc.id,
        text="Waiting period for Pre-Existing Diseases: 24 months of continuous coverage without break. If any specified disease falls under waiting period, the longer applies.",
        page_number=31,
        section_heading="EXCLUSIONS AND WAITING PERIODS",
        chunk_index=0,
        content_hash="phash001",
    )
    p_chunk_room = DocumentChunk(
        document_id=p_doc.id,
        text="Room Rent: Room Rent means amount charged for Room and Boarding expenses. Expenses varying with room rent occupied will be considered in proportion.",
        page_number=9,
        section_heading="Room Rent Charges",
        chunk_index=1,
        content_hash="phash002",
    )
    c_chunk = DocumentChunk(
        document_id=c_doc.id,
        text="Customer Information Sheet: 24 months waiting period for pre-existing conditions. Cataract treatment covered with sub-limits after waiting period.",
        page_number=8,
        section_heading="Waiting Periods Summary",
        chunk_index=0,
        content_hash="chash001",
    )
    g_chunk = DocumentChunk(
        document_id=g_doc.id,
        text="Cashless claims procedure: Submit pre-authorization request at network hospital desk at least 48 hours prior to planned hospitalization.",
        page_number=1,
        section_heading="Cashless Hospitalization Intimation",
        chunk_index=0,
        content_hash="ghash001",
    )
    db_session.add_all([p_chunk, p_chunk_room, c_chunk, g_chunk])
    db_session.commit()
    from backend.app.search import sync_fts5_index
    sync_fts5_index(db_session)
    return {"policy": p_doc, "cis": c_doc, "guidance": g_doc}


def test_qa_with_relevant_policy_evidence(client: TestClient, seed_qa_documents):
    """Test question answering with relevant policy evidence and correct citations."""
    payload = {"question": "What is the waiting period for pre-existing diseases?"}
    res = client.post("/api/v1/qa/ask", json=payload)
    assert res.status_code == 200
    data = res.json()

    assert data["status"] == "answered"
    assert data["is_sufficient_evidence"] is True
    assert data["provider"] == "retrieval_grounded_guidance"
    assert len(data["citations"]) > 0

    # Verify citation fields
    top_citation = data["citations"][0]
    assert "document_title" in top_citation
    assert top_citation["document_type"] in ["policy", "cis"]
    assert top_citation["page_number"] in [8, 31]
    assert "supporting_text" in top_citation
    assert "waiting period" in data["answer"].lower()


def test_qa_correct_version_and_page_labels(client: TestClient, seed_qa_documents):
    """Verify citations preserve exact physical page, printed page, and policy version."""
    payload = {"question": "What does the policy say about room rent?"}
    res = client.post("/api/v1/qa/ask", json=payload)
    assert res.status_code == 200
    data = res.json()

    assert data["status"] == "answered"
    policy_cites = [c for c in data["citations"] if c["document_type"] == "policy"]
    assert len(policy_cites) > 0
    cite = policy_cites[0]
    assert cite["version"] == "POL / COMP / V.24 / 2025 (UIN: SHAHLIP26044V092526)"
    assert cite["page_number"] == 9
    assert cite["printed_page_number"] == 8
    assert "Physical Page 9 (Printed Page 8/47)" in cite["page_label"]


def test_qa_separation_of_full_policy_and_cis(client: TestClient, seed_qa_documents):
    """Verify answer distinguishes full policy terms from CIS and guidance."""
    payload = {"question": "waiting period for pre-existing conditions"}
    res = client.post("/api/v1/qa/ask", json=payload)
    assert res.status_code == 200
    answer = res.json()["answer"]

    # Verify distinct document attribution headers in answer
    assert "Star Comprehensive Insurance Policy Terms & Conditions Wording" in answer
    assert "POL / COMP / V.24 / 2025" in answer


def test_qa_unsupported_question_abstains(client: TestClient, seed_qa_documents):
    """Verify clean abstention on questions without supporting evidence."""
    payload = {"question": "What is the policy for orbital space flight and planetary excursion?"}
    res = client.post("/api/v1/qa/ask", json=payload)
    assert res.status_code == 200
    data = res.json()

    assert data["status"] == "insufficient_evidence"
    assert data["is_sufficient_evidence"] is False
    assert len(data["citations"]) == 0
    assert "strictly abstains when verified evidence is absent" in data["answer"]


def test_qa_empty_input_validation(client: TestClient):
    """Verify validation error on empty or whitespace question."""
    res = client.post("/api/v1/qa/ask", json={"question": "   "})
    assert res.status_code == 422
    data = res.json()
    assert "error" in data
    assert data["error"]["code"] == "VALIDATION_ERROR"


def test_qa_hospital_network_status_warning(client: TestClient, seed_qa_documents):
    """Verify hospital network inquiries include non-guarantee disclosure."""
    payload = {"question": "How do cashless hospital network claims work?"}
    res = client.post("/api/v1/qa/ask", json=payload)
    assert res.status_code == 200
    answer = res.json()["answer"]
    assert "Important Clarification on Network Status" in answer
    assert "does not guarantee cashless approval" in answer


def test_qa_compatibility_endpoint(client: TestClient, seed_qa_documents):
    """Verify POST /api/v1/documents/ask compatibility endpoint."""
    payload = {"question": "What are the policy exclusions?"}
    res = client.post("/api/v1/documents/ask", json=payload)
    assert res.status_code == 200
    data = res.json()
    assert "answer" in data
    assert "citations" in data


def test_qa_conversation_history_persistence(client: TestClient, seed_qa_documents, db_session: Session):
    """Verify conversation and message records are persisted in database."""
    conv_id = "test-session-uuid-1234"
    payload = {
        "question": "What is the waiting period for pre-existing diseases?",
        "conversation_id": conv_id,
    }
    res = client.post("/api/v1/qa/ask", json=payload)
    assert res.status_code == 200

    # Query DB for stored conversation and messages
    conv = db_session.query(Conversation).filter(Conversation.id == conv_id).first()
    assert conv is not None
    messages = db_session.query(Message).filter(Message.conversation_id == conv_id).all()
    assert len(messages) == 2
    assert messages[0].role == "user"
    assert messages[1].role == "assistant"
    assert messages[1].citations is not None


def test_qa_unrelated_query_clean_abstention(client: TestClient, seed_qa_documents):
    """Verify clean abstention on completely unrelated non-insurance queries."""
    payload = {"question": "How do I bake sourdough bread at high altitude?"}
    res = client.post("/api/v1/qa/ask", json=payload)
    assert res.status_code == 200
    data = res.json()
    assert data["status"] == "insufficient_evidence"
    assert data["is_sufficient_evidence"] is False
    assert len(data["citations"]) == 0
    assert "strictly abstains when verified evidence is absent" in data["answer"]


def test_qa_cis_vs_policy_page_citation_accuracy(client: TestClient, seed_qa_documents):
    """Verify citations accurately distinguish CIS (printed /19) from full policy (printed /47)."""
    payload = {"question": "What are the cataract treatment conditions?"}
    res = client.post("/api/v1/qa/ask", json=payload)
    assert res.status_code == 200
    data = res.json()
    assert data["status"] == "answered"
    assert len(data["citations"]) > 0

    # The seeded CIS chunk (chunk_id for c_chunk) has page 8
    cis_cites = [c for c in data["citations"] if c["document_type"] == "cis"]
    assert len(cis_cites) > 0
    c_cite = cis_cites[0]
    assert c_cite["document_title"] == "Star Comprehensive Insurance Policy - Customer Information Sheet (CIS)"
    assert c_cite["page_number"] == 8
    assert c_cite["printed_page_number"] == 7
    assert c_cite["page_label"] == "Physical Page 8 (Printed Page 7/19)"
