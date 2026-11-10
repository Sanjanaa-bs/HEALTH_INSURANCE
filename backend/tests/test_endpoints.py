from fastapi.testclient import TestClient
from sqlalchemy.orm import Session
from backend.app.models.hospital import Hospital, InsurerHospitalRecord
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

    # Test case-insensitive and partial-name searching for "manipal"
    for term in ["manipal", "MANIPAL", "MaNiPaL", "manip"]:
        res_mani = client.get(f"/api/v1/hospitals?search={term}")
        assert res_mani.status_code == 200
        data_mani = res_mani.json()
        assert len(data_mani["items"]) == 1
        assert data_mani["items"][0]["hospital_name"] == "Manipal Hospital"

    # Test source parameter and state filter
    res_source = client.get("/api/v1/hospitals?search=manipal&source=govt&state=Karnataka")
    assert res_source.status_code == 200
    data_source = res_source.json()
    assert len(data_source["items"]) == 1
    assert data_source["items"][0]["source_type"] == "Government Directory"

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


def test_hospital_search_network_statuses_and_kerudi(client: TestClient, db_session: Session):
    """
    Test government search for 'kerudi' and verify three distinct network statuses:
    1. 'Listed in Star Health network data' (matched facility)
    2. 'Not found in available network data' (unlisted facility within Bengaluru scope)
    3. 'Network status unverified' (out-of-scope facility like Kerudi in Bagalkot, or empty insurer dataset)
    """
    # 1. First test with empty insurer table: status should be 'Network status unverified'
    kerudi = Hospital(
        hospital_name="Kerudi Hospital And Research Centre",
        state="Karnataka",
        district="Bagalkot",
        pincode="587101",
    )
    db_session.add(kerudi)
    db_session.commit()
    db_session.refresh(kerudi)

    res_empty_insurer = client.get(f"/api/v1/hospitals/{kerudi.id}")
    assert res_empty_insurer.status_code == 200
    assert res_empty_insurer.json()["network_status"] == "Network status unverified"
    assert res_empty_insurer.json()["network_status_code"] == "UNVERIFIED"

    # 2. Seed InsurerHospitalRecord (e.g. Bangalore Baptist Hospital) and an unlisted Bengaluru hospital
    insurer_rec = InsurerHospitalRecord(
        insurer_name="Star Health",
        hospital_name="BANGALORE BAPTIST HOSPITAL",
        city="Bengaluru",
        state="Karnataka",
        pincode="560024",
        address="Bellary Road, Hebbal",
        network_type="Cashless",
    )
    baptist = Hospital(
        hospital_name="Bangalore Baptist Hospital",
        state="Karnataka",
        district="Bengaluru Urban",
        pincode="560024",
    )
    bengaluru_unlisted = Hospital(
        hospital_name="Bengaluru Community Care",
        state="Karnataka",
        district="Bengaluru Urban",
        pincode="560001",
    )
    db_session.add_all([insurer_rec, baptist, bengaluru_unlisted])
    db_session.commit()
    db_session.refresh(baptist)
    db_session.refresh(bengaluru_unlisted)

    # 3. Search for "kerudi" -> Kerudi in Bagalkot is outside the Bengaluru sample scope -> UNVERIFIED
    res_kerudi = client.get("/api/v1/hospitals?search=kerudi&state=Karnataka")
    assert res_kerudi.status_code == 200
    data_kerudi = res_kerudi.json()
    assert len(data_kerudi["items"]) == 1
    item = data_kerudi["items"][0]
    assert item["hospital_name"] == "Kerudi Hospital And Research Centre"
    assert item["district"] == "Bagalkot"
    assert item["pincode"] == "587101"
    assert item["source_type"] == "Government Directory"
    assert item["network_status"] == "Network status unverified"
    assert item["network_status_code"] == "UNVERIFIED"
    assert "The available Star Health dataset contains only a limited Bengaluru sample" in item["network_status_explanation"]
    assert "verify with Star Health before planning cashless treatment" in item["network_status_explanation"]

    # Single hospital endpoint for kerudi
    res_single = client.get(f"/api/v1/hospitals/{kerudi.id}")
    assert res_single.status_code == 200
    single_data = res_single.json()
    assert single_data["network_status"] == "Network status unverified"
    assert single_data["network_status_code"] == "UNVERIFIED"
    assert "The available Star Health dataset contains only a limited Bengaluru sample" in single_data["network_status_explanation"]

    # 4. Search for unlisted Bengaluru hospital within documented scope -> NOT_FOUND
    res_unlisted = client.get(f"/api/v1/hospitals/{bengaluru_unlisted.id}")
    assert res_unlisted.status_code == 200
    unlisted_data = res_unlisted.json()
    assert unlisted_data["network_status"] == "Not found in available network data"
    assert unlisted_data["network_status_code"] == "NOT_FOUND"
    assert "does not prove the hospital is out of network" in unlisted_data["network_status_explanation"]

    # 5. Search for "baptist" -> Matches insurer record ignoring case differences: "Listed in Star Health network data"
    res_baptist = client.get("/api/v1/hospitals?search=baptist")
    assert res_baptist.status_code == 200
    data_baptist = res_baptist.json()
    assert len(data_baptist["items"]) == 1
    assert data_baptist["items"][0]["hospital_name"] == "Bangalore Baptist Hospital"
    assert data_baptist["items"][0]["source_type"] == "Government Directory"
    assert data_baptist["items"][0]["network_status"] == "Listed in Star Health network data"
    assert data_baptist["items"][0]["network_status_code"] == "LISTED"


def test_name_matching_and_conservative_boundaries():
    """
    Test name matching ignoring case, punctuation, whitespace, and harmless legal suffixes,
    while ensuring similar but distinct hospital names are not conflated.
    """
    from backend.app.api.v1.hospitals import normalize_hospital_name, location_compatible

    # Harmless differences in punctuation, case, whitespace, legal suffixes
    assert normalize_hospital_name("Apollo Hospitals - Bangalore") == normalize_hospital_name("Apollo Hospital Bangalore")
    assert normalize_hospital_name("BANGALORE BAPTIST HOSPITAL") == normalize_hospital_name("Bangalore Baptist Hospital")
    assert normalize_hospital_name("Kerudi Hospital & Research Centre") == normalize_hospital_name("Kerudi Hospital And Research Centre")
    assert normalize_hospital_name("St. John's Hospital") == normalize_hospital_name("St Johns Hospital")
    assert normalize_hospital_name("Chaitanya Hospital Pvt Ltd") == normalize_hospital_name("Chaitanya Hospital")

    # Distinct hospital names must NOT match
    assert normalize_hospital_name("Aditi Eye Care") != normalize_hospital_name("Aditi Nursing Home")
    assert normalize_hospital_name("Manipal Northside Hospital") != normalize_hospital_name("Manipal Hospital")
    assert normalize_hospital_name("Apollo Clinic") != normalize_hospital_name("Apollo Hospitals")

    # Location compatibility checks
    assert location_compatible("Karnataka", "Bengaluru", "560024", "Karnataka", "Bengaluru", "560024") is True
    assert location_compatible("Karnataka", "Bagalkot", "587101", "Maharashtra", "Mumbai", "400001") is False


def test_insurer_network_search_and_source_separation(client: TestClient, db_session: Session):
    """
    Test that Star Health network searches its own insurer records table,
    and returns correct source_type and 'Listed in Star Health network data' status.
    """
    # Seed 2 insurer records
    rec1 = InsurerHospitalRecord(
        insurer_name="Star Health",
        hospital_name="Cambridge Hospital",
        city="Bengaluru",
        state="Karnataka",
        pincode="560008",
        address="Halasuru, Bangalore",
        network_type="Cashless",
    )
    rec2 = InsurerHospitalRecord(
        insurer_name="Star Health",
        hospital_name="Chinmaya Mission Hospital",
        city="Bengaluru",
        state="Karnataka",
        pincode="560038",
        address="Indiranagar, Bangalore",
        network_type="Cashless",
    )
    db_session.add_all([rec1, rec2])
    db_session.commit()

    # Query insurer-network endpoint directly
    res = client.get("/api/v1/hospitals/insurer-network?search=Cambridge")
    assert res.status_code == 200
    data = res.json()
    assert len(data["items"]) == 1
    assert data["items"][0]["hospital_name"] == "Cambridge Hospital"
    assert data["items"][0]["source_type"] == "Insurer Network (Star Health)"
    assert data["items"][0]["network_status"] == "Listed in Star Health network data"

    # Query /api/v1/hospitals with source=insurer
    res_source = client.get("/api/v1/hospitals?search=Chinmaya&source=insurer")
    assert res_source.status_code == 200
    data_source = res_source.json()
    assert len(data_source["items"]) == 1
    assert data_source["items"][0]["hospital_name"] == "Chinmaya Mission Hospital"
    assert data_source["items"][0]["source_type"] == "Insurer Network (Star Health)"
    assert data_source["items"][0]["network_status"] == "Listed in Star Health network data"
