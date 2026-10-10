import pytest
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from backend.app.models.hospital import Hospital, InsurerHospitalRecord
from backend.app.models.document import Document, DocumentChunk
from backend.app.models.chat import Conversation, Message
from backend.app.models.evaluation import EvaluationResult


def test_hospital_and_insurer_record_models(db_session: Session):
    """Verify Hospital and InsurerHospitalRecord creation and relationship."""
    hospital = Hospital(
        hospital_name="Apollo Hospital Bannerghatta",
        state="Karnataka",
        district="Bengaluru Urban",
        pincode="560076",
        total_beds=250,
    )
    db_session.add(hospital)
    db_session.commit()
    db_session.refresh(hospital)

    assert hospital.id is not None
    assert hospital.hospital_name == "Apollo Hospital Bannerghatta"

    # Add insurer specific network record linked to the directory hospital
    insurer_record = InsurerHospitalRecord(
        insurer_name="Star Health",
        hospital_name="Apollo Hospital Bannerghatta Road",
        city="Bengaluru",
        state="Karnataka",
        pincode="560076",
        network_type="Cashless",
        matched_hospital_id=hospital.id,
    )
    db_session.add(insurer_record)
    db_session.commit()
    db_session.refresh(insurer_record)

    assert insurer_record.id is not None
    assert insurer_record.matched_hospital.hospital_name == "Apollo Hospital Bannerghatta"
    assert len(hospital.insurer_records) == 1


def test_document_and_chunks_preservation(db_session: Session):
    """Verify Document and DocumentChunk fields: document ref, page, heading, index, hash."""
    doc = Document(
        title="Star Comprehensive Insurance Policy",
        document_type="policy",
        source_path="data/policies/Policy_Star_Comprehensive_Insurance_Policy_V_21_3a414ab104.pdf",
        file_format="pdf",
        file_size_bytes=3572004,
        is_processed=True,
    )
    db_session.add(doc)
    db_session.commit()
    db_session.refresh(doc)

    chunk = DocumentChunk(
        document_id=doc.id,
        text="Section 1: Coverage details for hospitalisation expenses...",
        page_number=4,
        section_heading="Section 1: Scope of Cover",
        chunk_index=0,
        content_hash="a1b2c3d4e5f67890abcdef1234567890abcdef1234567890abcdef1234567890",
        token_count=120,
    )
    db_session.add(chunk)
    db_session.commit()
    db_session.refresh(chunk)

    assert chunk.id is not None
    assert chunk.document_id == doc.id
    assert chunk.page_number == 4
    assert chunk.section_heading == "Section 1: Scope of Cover"
    assert chunk.chunk_index == 0
    assert chunk.content_hash.startswith("a1b2c3")

    # Verify unique constraint on (document_id, chunk_index)
    duplicate_chunk = DocumentChunk(
        document_id=doc.id,
        text="Duplicate chunk text",
        chunk_index=0,
        content_hash="different_hash_same_index",
    )
    db_session.add(duplicate_chunk)
    with pytest.raises(IntegrityError):
        db_session.commit()
    db_session.rollback()


def test_conversation_and_message_cascade(db_session: Session):
    """Verify Conversation and Message creation and cascade deletion."""
    conv = Conversation(title="Query about cataract coverage")
    db_session.add(conv)
    db_session.commit()
    db_session.refresh(conv)

    msg1 = Message(
        conversation_id=conv.id,
        role="user",
        content="Is cataract surgery covered under Star Comprehensive?",
    )
    msg2 = Message(
        conversation_id=conv.id,
        role="assistant",
        content="Yes, cataract treatment is covered up to specified sub-limits.",
        citations='[{"doc_id": 1, "page": 8}]',
    )
    db_session.add_all([msg1, msg2])
    db_session.commit()

    assert len(conv.messages) == 2

    # Cascade delete
    db_session.delete(conv)
    db_session.commit()

    remaining_msgs = db_session.query(Message).filter(Message.conversation_id == conv.id).all()
    assert len(remaining_msgs) == 0


def test_evaluation_result_model(db_session: Session):
    """Verify EvaluationResult model creation."""
    eval_record = EvaluationResult(
        test_suite="rag_benchmark_v1",
        test_case_id="tc_policy_cataract_001",
        category="policy_qa",
        metric_name="faithfulness",
        score=0.95,
        passed=True,
        details='{"expected": "Covered with limit", "retrieved_pages": [8]}',
    )
    db_session.add(eval_record)
    db_session.commit()
    db_session.refresh(eval_record)

    assert eval_record.id is not None
    assert eval_record.passed is True
    assert eval_record.score == 0.95
