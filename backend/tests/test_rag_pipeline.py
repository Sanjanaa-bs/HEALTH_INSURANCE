import pytest
from unittest.mock import patch, MagicMock
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from backend.app.models.document import Document, DocumentChunk
from backend.app.services.embeddings import LocalDenseEmbeddingProvider, get_embedding_provider
from backend.app.services.vector_store import LocalVectorStore, vector_store_instance
from backend.app.services.retrieval import hybrid_search
from backend.app.services.llm_provider import (
    OllamaLLMProvider,
    OpenAILLMProvider,
    GeminiLLMProvider,
    get_llm_provider,
)
from backend.app.schemas.qa import CitationItem, QuestionRequest, QuestionResponse
from backend.app.services.qa import build_evidence_grounded_answer
from backend.app.config import settings


@pytest.fixture
def rag_seed_docs(db_session: Session):
    """Seed test documents and document chunks for RAG tests."""
    # Policy document
    p_doc = Document(
        title="Star Comprehensive Insurance Policy - Terms & Conditions Wording",
        document_type="policy",
        source_path="data/policies/Policy_Star_Comprehensive_clean.pdf",
        file_format="pdf",
        version="POL / COMP / V.24 / 2025 (UIN: SHAHLIP26044V092526)",
        is_processed=True,
    )
    # CIS document
    c_doc = Document(
        title="Star Comprehensive Insurance Policy - Customer Information Sheet (CIS)",
        document_type="cis",
        source_path="data/policies/CIS_Star.pdf",
        file_format="pdf",
        version="V.2 / 2025",
        is_processed=True,
    )
    db_session.add_all([p_doc, c_doc])
    db_session.flush()

    c1 = DocumentChunk(
        document_id=p_doc.id,
        text="Pre-existing disease waiting period is 24 months of continuous coverage without break. Continuous coverage without break under policy is mandatory.",
        page_number=41,
        section_heading="Waiting Periods",
        chunk_index=0,
        content_hash="chash_rag_01",
    )
    c2 = DocumentChunk(
        document_id=p_doc.id,
        text="Room Rent: Single Private A/C room. No capping on room rent. ICU charges covered at actuals up to sum insured.",
        page_number=9,
        section_heading="Room Rent Charges",
        chunk_index=1,
        content_hash="chash_rag_02",
    )
    c3 = DocumentChunk(
        document_id=c_doc.id,
        text="Customer Information Sheet: 24 months waiting period for specified illnesses and pre-existing conditions. Cataract sub-limits apply.",
        page_number=8,
        section_heading="CIS Summary",
        chunk_index=0,
        content_hash="chash_rag_03",
    )
    db_session.add_all([c1, c2, c3])
    db_session.commit()

    from backend.app.search import sync_fts5_index
    sync_fts5_index(db_session)

    # Index in vector store for tests
    embedder = get_embedding_provider()
    vector_store_instance.clear()
    for chunk in [c1, c2, c3]:
        doc = chunk.document
        page_label = f"Physical Page {chunk.page_number} (Printed Page {chunk.page_number - 1}/47)" if doc.document_type == "policy" else f"Physical Page {chunk.page_number} (Printed Page {chunk.page_number - 1}/19)"
        vector_store_instance.add_chunk(
            chunk_id=chunk.id,
            document_id=doc.id,
            document_title=doc.title,
            document_type=doc.document_type,
            version=doc.version,
            page_number=chunk.page_number,
            printed_page_number=chunk.page_number - 1,
            page_label=page_label,
            section_heading=chunk.section_heading,
            text=chunk.text,
            content_hash=chunk.content_hash,
            vector=embedder.embed_text(f"{doc.title} {chunk.text}"),
        )

    return {"policy": p_doc, "cis": c_doc}


def test_embedding_generation():
    """Verify local dense embedding generator returns normalized vector."""
    provider = LocalDenseEmbeddingProvider(vector_dim=128)
    vec = provider.embed_text("Waiting period for pre-existing diseases")
    assert len(vec) == 128
    norm = sum(x * x for x in vec) ** 0.5
    assert abs(norm - 1.0) < 1e-4


def test_rag_compatibility_exports_share_live_vector_store():
    """Startup, indexing, and retrieval must operate on one vector store singleton."""
    from backend.app.rag.vector_store import vector_store_instance as compatibility_store

    assert compatibility_store is vector_store_instance


def test_vector_store_uses_configured_path(monkeypatch, tmp_path):
    configured_path = tmp_path / "custom-index.json"
    monkeypatch.setattr(settings, "VECTOR_STORE_PATH", str(configured_path))

    store = LocalVectorStore()

    assert store.filepath == str(configured_path)


def test_ollama_is_the_default_local_llm_provider(monkeypatch):
    monkeypatch.setattr(settings, "LLM_PROVIDER", "ollama")

    provider = get_llm_provider()

    assert isinstance(provider, OllamaLLMProvider)
    assert provider.model_name == settings.OLLAMA_MODEL_NAME


def test_ollama_provider_parses_grounded_response(monkeypatch):
    from backend.app.services import llm_provider

    response = MagicMock()
    response.json.return_value = {"message": {"content": "### Direct Policy Answer\nSupported answer."}}
    monkeypatch.setattr(llm_provider.httpx, "post", MagicMock(return_value=response))
    provider = OllamaLLMProvider("http://localhost:11434/", "llama3.2")

    answer, provider_name = provider.generate_answer("Question", [{"supporting_text": "Evidence."}])

    assert answer == "### Direct Policy Answer\nSupported answer."
    assert provider_name == "ollama"
    response.raise_for_status.assert_called_once()


def test_fallback_answer_does_not_invent_topic_facts():
    citation = CitationItem(
        chunk_id=1,
        document_id=1,
        document_title="Policy excerpt",
        document_type="policy",
        supporting_text="This excerpt does not state a cataract waiting period.",
        content_hash="hash",
    )

    answer = build_evidence_grounded_answer("What is the cataract waiting period?", [citation])

    assert citation.supporting_text in answer
    assert "24-month" not in answer


def test_hybrid_retrieval_applies_alpha_weight(monkeypatch, db_session):
    from backend.app.services import retrieval

    monkeypatch.setattr(
        retrieval,
        "search_document_chunks",
        lambda **kwargs: [{"chunk_id": 1, "excerpt": "keyword result"}],
    )
    monkeypatch.setattr(
        retrieval,
        "get_embedding_provider",
        lambda: MagicMock(embed_text=lambda query: [1.0]),
    )
    monkeypatch.setattr(
        retrieval.vector_store_instance,
        "search",
        lambda **kwargs: [{"chunk_id": 2, "supporting_text": "vector result"}],
    )

    keyword_only, _ = hybrid_search(db_session, "query", top_k=2, alpha=1.0)
    vector_only, _ = hybrid_search(db_session, "query", top_k=2, alpha=0.0)

    assert keyword_only[0]["chunk_id"] == 1
    assert keyword_only[0]["rrf_score"] > keyword_only[1]["rrf_score"]
    assert vector_only[0]["chunk_id"] == 2
    assert vector_only[0]["rrf_score"] > vector_only[1]["rrf_score"]


def test_vector_store_search(rag_seed_docs):
    """Verify vector store returns relevant passages by cosine similarity."""
    embedder = get_embedding_provider()
    query_vec = embedder.embed_text("room rent capping ICU charges")
    results = vector_store_instance.search(query_vec, top_k=2)
    assert len(results) > 0
    top = results[0]
    assert "room" in top["supporting_text"].lower()
    assert top["similarity_score"] > 0.0


def test_hybrid_retrieval_combines_and_deduplicates(db_session: Session, rag_seed_docs):
    """Verify hybrid retrieval returns passages with RRF scores and deduplicated chunks."""
    passages, mode = hybrid_search(db_session, "waiting period for pre-existing disease", top_k=3)
    assert len(passages) > 0
    assert mode in ["hybrid", "keyword", "vector"]
    chunk_ids = [p["chunk_id"] for p in passages]
    assert len(chunk_ids) == len(set(chunk_ids))  # No duplicates
    assert "rrf_score" in passages[0]


def test_citation_page_numbers_and_version(client: TestClient, rag_seed_docs):
    """Verify citations preserve exact physical page and printed page labels."""
    res = client.post("/api/v1/qa/ask", json={"question": "What is the room rent limit?"})
    assert res.status_code == 200
    data = res.json()
    assert data["status"] == "answered"
    assert len(data["citations"]) > 0
    cite = data["citations"][0]
    assert "Physical Page" in cite["page_label"]
    assert "Printed Page" in cite["page_label"]
    assert cite["version"] is not None


def test_cis_evidence_separate_from_policy(client: TestClient, rag_seed_docs):
    """Verify CIS citations remain distinct and do not confuse full policy."""
    res = client.post("/api/v1/qa/ask", json={"question": "Cataract sub-limits summary", "document_type": "cis"})
    assert res.status_code == 200
    data = res.json()
    for c in data["citations"]:
        assert c["document_type"] == "cis"
        assert c["version"] == "V.2 / 2025"


def test_unsupported_question_clean_abstention(client: TestClient, rag_seed_docs):
    """Verify unsupported queries cleanly abstain without hallucination."""
    res = client.post("/api/v1/qa/ask", json={"question": "What is the policy for deep space hyperdrive warp navigation?"})
    assert res.status_code == 200
    data = res.json()
    assert data["status"] == "insufficient_evidence"
    assert data["is_sufficient_evidence"] is False
    assert len(data["citations"]) == 0
    assert "strictly abstains when verified evidence is absent" in data["answer"]


def test_missing_llm_credentials_safe_fallback(client: TestClient, rag_seed_docs):
    """Verify system safely falls back when no external LLM credentials are provided."""
    with patch("backend.app.services.qa.get_llm_provider") as mock_llm:
        mock_instance = MagicMock()
        mock_instance.generate_answer.return_value = (None, "fallback")
        mock_llm.return_value = mock_instance

        res = client.post("/api/v1/qa/ask", json={"question": "What is the waiting period for pre-existing diseases?"})
        assert res.status_code == 200
        data = res.json()
        assert data["status"] == "answered"
        assert data["generation_mode"] in ["Hybrid Retrieval", "Keyword Retrieval Fallback"]
        assert data["llm_provider"] == "fallback"
        assert "Direct Policy Answer" in data["answer"]


def test_llm_success_mode_label(client: TestClient, rag_seed_docs):
    """Verify that when a real LLM succeeds, generation_mode is marked RAG + LLM."""
    with patch("backend.app.services.qa.get_llm_provider") as mock_llm:
        mock_instance = MagicMock()
        mock_instance.generate_answer.return_value = ("### Direct Policy Answer\nPre-existing diseases have a 24-month waiting period.", "openai")
        mock_llm.return_value = mock_instance

        res = client.post("/api/v1/qa/ask", json={"question": "What is the waiting period for pre-existing diseases?"})
        assert res.status_code == 200
        data = res.json()
        assert data["generation_mode"] == "RAG + LLM"
        assert data["llm_provider"] == "openai"
        assert "24-month waiting period" in data["answer"]


def test_api_response_schema_compatibility(client: TestClient, rag_seed_docs):
    """Verify response includes all required legacy and RAG fields."""
    res = client.post("/api/v1/qa/ask", json={"question": "What does the policy say about room rent?"})
    assert res.status_code == 200
    data = res.json()
    assert "question" in data
    assert "answer" in data
    assert "status" in data
    assert "is_sufficient_evidence" in data
    assert "provider" in data
    assert "generation_mode" in data
    assert "retrieval_mode" in data
    assert "embedding_provider" in data
    assert "llm_provider" in data
    assert "citations" in data
    assert "disclaimer" in data
    assert "conversation_id" in data
