from fastapi.testclient import TestClient
from sqlalchemy.orm import Session
from backend.app.models.hospital import Hospital
from backend.app.models.document import Document


def test_dashboard_summary_empty_db(client: TestClient):
    """Test dashboard summary returns real database zero counts when empty."""
    response = client.get("/api/v1/dashboard/summary")
    assert response.status_code == 200

    data = response.json()
    assert data["total_hospitals"] == 0
    assert data["total_insurer_records"] == 0
    assert data["total_documents"] == 0
    assert data["total_document_chunks"] == 0
    assert data["total_conversations"] == 0
    assert data["total_evaluations"] == 0
    assert "dataset_status" in data
    # Source dataset checks
    assert data["dataset_status"]["hospitals_csv_exists"] is True


def test_dashboard_summary_with_records(client: TestClient, db_session: Session):
    """Test dashboard summary reflects real database increments."""
    # Add 2 hospitals
    h1 = Hospital(hospital_name="Hospital Alpha")
    h2 = Hospital(hospital_name="Hospital Beta")
    doc = Document(
        title="Test Policy",
        document_type="policy",
        source_path="data/policies/test.pdf",
        file_format="pdf",
    )
    db_session.add_all([h1, h2, doc])
    db_session.commit()

    response = client.get("/api/v1/dashboard/summary")
    assert response.status_code == 200

    data = response.json()
    assert data["total_hospitals"] == 2
    assert data["total_documents"] == 1
    assert data["total_insurer_records"] == 0
