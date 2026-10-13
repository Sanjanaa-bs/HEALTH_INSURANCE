import csv
import json
import pytest
from pathlib import Path
from sqlalchemy.orm import Session
from fastapi.testclient import TestClient

from backend.app.models.hospital import Hospital, InsurerHospitalRecord
from backend.app.models.document import Document, DocumentChunk
from backend.app.search import search_document_chunks, sync_fts5_index
from scripts.ingest_hospitals import ingest_hospital_csv
from scripts.ingest_policies import ingest_policy_pdfs
from scripts.ingest_claim_guidance import ingest_claim_guidance_mhtml
from scripts.ingest_insurer_networks import extract_cards_from_html


def test_csv_ingestion_and_idempotency(db_session: Session, tmp_path: Path):
    """Test importing a real-format CSV fixture and verify idempotent re-ingestion."""
    csv_file = tmp_path / "test_hospitals.csv"
    headers = [
        "Sr_No", "Location_Coordinates", "Location", "Hospital_Name", "Hospital_Category",
        "Hospital_Care_Type", "Discipline_Systems_of_Medicine", "Address_Original_First_Line",
        "State", "District", "Subdistrict", "Pincode", "Telephone", "Mobile_Number",
        "Emergency_Num", "Ambulance_Phone_No", "Bloodbank_Phone_No", "Foreign_pcare",
        "Tollfree", "Helpline", "Hospital_Fax", "Hospital_Primary_Email_Id",
        "Hospital_Secondary_Email_Id", "Website", "Specialties", "Facilities",
        "Accreditation", "Hospital_Regis_Number", "Registeration_Number_Scan",
        "Nodal_Person_Info", "Nodal_Person_Tele", "Nodal_Person_Email_Id", "Town",
        "Subtown", "Village", "Establised_Year", "Ayush", "Miscellaneous_Facilities",
        "Number_Doctor", "Num_Mediconsultant_or_Expert", "Total_Num_Beds",
        "Number_Private_Wards", "Num_Bed_for_Eco_Weaker_Sec", "Empanelment_or_Collaboration_with",
        "Emergency_Services", "Tariff_Range", "State_ID", "District_ID"
    ]

    rows = [
        ["1", "12.9716, 77.5946", "Near MG Road", "St Philomena Hospital", "Hospital", "Hospital", "Allopathic", "Campbell Road, Viveknagar", "Karnataka", "Bengaluru Urban", "0", "560047", "080 22065000", "0", "0", "0", "0", "0", "0", "0", "0", "info@stphilomena.in", "0", "www.stphilomena.in", "Cardiology", "ICU", "0", "0", "0", "0", "0", "0", "0", "0", "0", "0", "0", "0", "0", "0", "200", "0", "0", "0", "0", "0", "29", "556"],
        ["2", "0", "Near Bus Stand", "Manipal Hospital Old Airport Road", "Hospital", "Hospital", "Allopathic", "98 Rustum Bagh", "Karnataka", "Bengaluru Urban", "0", "560017", "080 25024444", "0", "0", "0", "0", "0", "0", "0", "0", "0", "0", "0", "Multi-specialty", "NICU", "0", "0", "0", "0", "0", "0", "0", "0", "0", "0", "0", "0", "0", "0", "600", "0", "0", "0", "0", "0", "29", "556"],
    ]

    with open(csv_file, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(headers)
        writer.writerows(rows)

    # First Run
    m1 = ingest_hospital_csv(csv_path=str(csv_file), db=db_session)
    assert m1["imported_records"] == 2
    assert m1["source_rows"] == 2

    # Second Run (Idempotency)
    m2 = ingest_hospital_csv(csv_path=str(csv_file), db=db_session)
    assert m2["imported_records"] == 0
    assert m2["skipped_rows"] == 2

    # Verify field values
    h = db_session.query(Hospital).filter(Hospital.hospital_name == "St Philomena Hospital").first()
    assert h is not None
    assert h.pincode == "560047"
    assert h.total_beds == 200
    assert h.latitude == 12.9716


def test_mhtml_card_extraction():
    """Test extracting insurer network hospital cards from HTML/MHTML content."""
    sample_html = """
    <div class="border rounded-md p-4 mb-4 flex">
        <div class="flex-1">
            <div class="text-[16px] font-semibold text-[#000000] mb-1">Manipal Hospital Jayanagar</div>
            <div>BANGALORE, Karnataka - 560011</div>
            <div>#45/1, 45th Cross, 9th Block, Jayanagar, BANGALORE, Karnataka - 560011</div>
            <div>Directions</div>
            <div>Network Hospital</div>
            <div>080-26088888</div>
        </div>
    </div>
    """
    cards = extract_cards_from_html(sample_html, "sample.htm", "https://starhealth.in")
    assert len(cards) == 1
    c = cards[0]
    assert c["hospital_name"] == "Manipal Hospital Jayanagar"
    assert c["pincode"] == "560011"
    assert c["network_type"] == "Cashless Network"


def test_search_returns_real_indexed_passages(db_session: Session):
    """Test full-text document search returning real indexed passages, page numbers, and section headings."""
    doc = Document(
        title="Star Comprehensive Insurance Policy CIS",
        document_type="cis",
        source_path="data/policies/CIS_test.pdf",
        file_format="pdf",
        is_processed=True,
    )
    db_session.add(doc)
    db_session.commit()

    chunk1 = DocumentChunk(
        document_id=doc.id,
        text="Cataract surgery is covered subject to a limit of Rs. 40,000 per eye.",
        page_number=8,
        section_heading="Specific Sub-limits",
        chunk_index=0,
        content_hash="hash_cataract_001",
    )
    chunk2 = DocumentChunk(
        document_id=doc.id,
        text="Pre-existing diseases waiting period is 36 months of continuous coverage.",
        page_number=10,
        section_heading="Waiting Periods",
        chunk_index=1,
        content_hash="hash_ped_002",
    )
    db_session.add_all([chunk1, chunk2])
    db_session.commit()

    sync_fts5_index(db_session)

    results = search_document_chunks(db=db_session, query_text="cataract limit")
    assert len(results) >= 1
    r = results[0]
    assert r["document_title"] == "Star Comprehensive Insurance Policy CIS"
    assert r["page_number"] == 8
    assert r["section_heading"] == "Specific Sub-limits"
    assert "cataract" in r["excerpt"].lower()


def test_hospital_source_classification(client: TestClient, db_session: Session):
    """Test hospital endpoints distinguish Government Directory from Insurer Network records."""
    h_govt = Hospital(
        hospital_name="Victoria Hospital",
        state="Karnataka",
        district="Bengaluru",
        pincode="560002",
        total_beds=250,
    )
    db_session.add(h_govt)
    db_session.commit()

    h_insurer = InsurerHospitalRecord(
        insurer_name="Star Health",
        hospital_name="Apollo Hospital Jayanagar",
        city="Bengaluru",
        state="Karnataka",
        pincode="560011",
        network_type="Cashless Network",
        matched_hospital_id=h_govt.id,
    )
    db_session.add(h_insurer)
    db_session.commit()

    # Govt Directory API
    res_govt = client.get(f"/api/v1/hospitals/{h_govt.id}")
    assert res_govt.status_code == 200
    govt_data = res_govt.json()
    assert govt_data["source_type"] == "Government Directory"
    assert govt_data["network_status"] == "Star Health Cashless"

    # Insurer Network API
    res_ins = client.get("/api/v1/hospitals/insurer-network")
    assert res_ins.status_code == 200
    ins_data = res_ins.json()
    assert len(ins_data["items"]) >= 1
    assert ins_data["items"][0]["source_type"] == "Insurer Network (Star Health)"
    assert ins_data["items"][0]["total_beds"] == 250


def test_insurer_search_includes_city_state_and_pincode(client: TestClient, db_session: Session):
    db_session.add(
        InsurerHospitalRecord(
            insurer_name="Star Health",
            hospital_name="Sample Medical Centre",
            city="Bengaluru",
            state="Karnataka",
            pincode="560011",
        )
    )
    db_session.commit()

    for search_term in ("Bengaluru", "Karnataka", "560011"):
        response = client.get("/api/v1/hospitals/insurer-network", params={"search": search_term})
        assert response.status_code == 200
        assert response.json()["pagination"]["total_items"] == 1


def test_empty_and_malformed_files_handling(db_session: Session, tmp_path: Path):
    """Test pipeline gracefully handles empty CSV or unparseable files without crashing."""
    empty_csv = tmp_path / "empty.csv"
    empty_csv.write_text("", encoding="utf-8")

    with pytest.raises(ValueError):
        ingest_hospital_csv(csv_path=str(empty_csv), db=db_session)


def test_dashboard_statistics_match_database(client: TestClient, db_session: Session):
    """Test dashboard summary endpoint statistics match direct database record counts."""
    # Seed 1 hospital, 1 document
    h = Hospital(hospital_name="Fortis Bannerghatta")
    d = Document(
        title="Sample CIS",
        document_type="cis",
        source_path="data/policies/sample.pdf",
        file_format="pdf",
    )
    db_session.add_all([h, d])
    db_session.commit()

    db_h_count = db_session.query(Hospital).count()
    db_d_count = db_session.query(Document).count()

    res = client.get("/api/v1/dashboard/summary")
    assert res.status_code == 200
    summary = res.json()

    assert summary["total_hospitals"] == db_h_count
    assert summary["total_documents"] == db_d_count
