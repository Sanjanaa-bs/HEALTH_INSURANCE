from fastapi.testclient import TestClient
from sqlalchemy.orm import Session
from backend.app.models.hospital import Hospital
from backend.app.models.document import Document, DocumentChunk


def test_hospitals_pagination_and_search(client: TestClient, db_session: Session):
    """Test hospitals listing, search filtering, and pagination."""
    # Seed 3 hospitals
    h1 = Hospital(
        hospital_name="Apollo Hospital",
        state="Karnataka",
        district="Bengaluru",
        pincode="560076",
    )
    h2 = Hospital(
        hospital_name="Fortis Hospital",
        state="Karnataka",
        district="Bengaluru",
        pincode="560076",
    )
    h3 = Hospital(
        hospital_name="Manipal Hospital",
        state="Karnataka",
        district="Bengaluru",
        pincode="560017",
    )
    db_session.add_all([h1, h2, h3])
    db_session.commit()

    # Test all
    res = client.get("/api/v1/hospitals?page=1&page_size=2")
    assert res.status_code == 200
    data = res.json()
    assert len(data["items"]) == 2
    assert data["pagination"]["total_items"] == 3
    assert data["pagination"]["total_pages"] == 2

    # Test search
    search_res = client.get("/api/v1/hospitals?search=Fortis")
    assert search_res.status_code == 200
    search_data = search_res.json()
    assert len(search_data["items"]) == 1
    assert search_data["items"][0]["hospital_name"] == "Fortis Hospital"

    # Test individual hospital by ID
    single_res = client.get(f"/api/v1/hospitals/{h1.id}")
    assert single_res.status_code == 200
    assert single_res.json()["hospital_name"] == "Apollo Hospital"

    # Test 404 for nonexistent hospital
    not_found_res = client.get("/api/v1/hospitals/99999")
    assert not_found_res.status_code == 404
    error_data = not_found_res.json()
    assert "error" in error_data
    assert error_data["error"]["code"] == "HTTP_404"


def test_documents_endpoints(client: TestClient, db_session: Session):
    """Test documents listing and chunk retrieval."""
    doc = Document(
        title="Customer Information Sheet",
        document_type="cis",
        source_path="data/policies/CIS_Star.pdf",
        file_format="pdf",
        is_processed=True,
    )
    db_session.add(doc)
    db_session.commit()
    db_session.refresh(doc)

    chunk = DocumentChunk(
        document_id=doc.id,
        text="Sample CIS chunk text",
        chunk_index=0,
        content_hash="abc123hash",
    )
    db_session.add(chunk)
    db_session.commit()

    # List documents
    res = client.get("/api/v1/documents")
    assert res.status_code == 200
    data = res.json()
    assert len(data["items"]) == 1
    assert data["items"][0]["chunk_count"] == 1

    # Filter documents by type
    filter_res = client.get("/api/v1/documents?document_type=policy")
    assert filter_res.status_code == 200
    assert len(filter_res.json()["items"]) == 0

    # Get single document
    doc_res = client.get(f"/api/v1/documents/{doc.id}")
    assert doc_res.status_code == 200
    assert doc_res.json()["title"] == "Customer Information Sheet"

    # Get chunks
    chunks_res = client.get(f"/api/v1/documents/{doc.id}/chunks")
    assert chunks_res.status_code == 200
    chunks_data = chunks_res.json()
    assert len(chunks_data) == 1
    assert chunks_data[0]["text"] == "Sample CIS chunk text"


def test_validation_error_structure(client: TestClient):
    """Test that validation errors return the structured error envelope."""
    # page must be >= 1, pass page=0
    res = client.get("/api/v1/hospitals?page=0")
    assert res.status_code == 422
    data = res.json()
    assert "error" in data
    assert data["error"]["code"] == "VALIDATION_ERROR"
