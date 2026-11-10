import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session
from backend.app.models.hospital import Hospital, InsurerHospitalRecord
from backend.app.api.v1.hospitals import (
    normalize_hospital_name,
    check_location_conflict,
    location_compatible,
    evaluate_hospital_network_details,
    STATUS_LISTED,
    STATUS_NOT_FOUND,
    STATUS_UNVERIFIED,
)


def test_1_supported_insurer_network_match(client: TestClient, db_session: Session):
    """
    Scenario 1: A hospital with a supported insurer network match.
    Must return LISTED status with clear pre-authorization disclaimer.
    """
    # 1. Linked via matched_hospital_id
    govt_h = Hospital(
        hospital_name="Bangalore Baptist Hospital",
        state="Karnataka",
        district="Bengaluru Urban",
        pincode="560024",
        address="Bellary Road, Hebbal, Bengaluru",
    )
    db_session.add(govt_h)
    db_session.commit()
    db_session.refresh(govt_h)

    insurer_h = InsurerHospitalRecord(
        insurer_name="Star Health",
        hospital_name="BANGALORE BAPTIST HOSPITAL",
        city="Bengaluru",
        state="Karnataka",
        pincode="560024",
        address="Bellary Road, Hebbal",
        network_type="Cashless Network",
        matched_hospital_id=govt_h.id,
    )
    db_session.add(insurer_h)
    db_session.commit()

    res = client.get(f"/api/v1/hospitals/{govt_h.id}")
    assert res.status_code == 200
    data = res.json()
    assert data["network_status"] == STATUS_LISTED
    assert data["network_status_code"] == "LISTED"
    assert "Matched in available Star Health network data" in data["network_status_explanation"]
    assert "pre-authorization" in data["network_status_explanation"]
    assert data["source_type"] == "Government Directory"

    # Also test via search
    res_search = client.get("/api/v1/hospitals?search=Baptist")
    assert res_search.status_code == 200
    s_data = res_search.json()
    assert len(s_data["items"]) == 1
    assert s_data["items"][0]["network_status"] == STATUS_LISTED
    assert s_data["items"][0]["network_status_code"] == "LISTED"


def test_2_hospital_present_in_directory_absent_from_insurer_sample(client: TestClient, db_session: Session):
    """
    Scenario 2: A hospital in the government directory (within the Bengaluru sample scope)
    but absent from the 10-record insurer sample.
    Must return NOT FOUND IN AVAILABLE NETWORK DATA, and explicitly note that absence
    does not prove it is out of network.
    """
    # Insurer record exists for someone else
    other_insurer = InsurerHospitalRecord(
        insurer_name="Star Health",
        hospital_name="Amar Nursing Home",
        city="Bengaluru",
        state="Karnataka",
        pincode="560018",
        network_type="Cashless Network",
    )
    # Target hospital in Bengaluru that is NOT in insurer sample
    bengaluru_h = Hospital(
        hospital_name="Abhishek Nethradhama",
        state="Karnataka",
        district="Bengaluru Rural",
        pincode="562123",
        address="Doddaballapur, Bengaluru Rural",
    )
    db_session.add_all([other_insurer, bengaluru_h])
    db_session.commit()
    db_session.refresh(bengaluru_h)

    res = client.get(f"/api/v1/hospitals/{bengaluru_h.id}")
    assert res.status_code == 200
    data = res.json()
    assert data["network_status"] == STATUS_NOT_FOUND
    assert data["network_status_code"] == "NOT_FOUND"
    assert "No matching record found in the available Star Health dataset" in data["network_status_explanation"]
    assert "does not prove the hospital is out of network" in data["network_status_explanation"]


def test_3_ambiguous_name_hospital(client: TestClient, db_session: Session):
    """
    Scenario 3: A hospital with an ambiguous name.
    Either overly generic name or multiple conflicting matches without location disambiguation.
    Must return UNVERIFIED.
    """
    # Seed 2 distinct insurer hospitals that share a common name prefix in different areas
    ins1 = InsurerHospitalRecord(
        insurer_name="Star Health",
        hospital_name="City Hospital",
        city="Bengaluru",
        state="Karnataka",
        pincode="560001",
        address="MG Road",
    )
    ins2 = InsurerHospitalRecord(
        insurer_name="Star Health",
        hospital_name="City Hospital",
        city="Bengaluru",
        state="Karnataka",
        pincode="560070",
        address="Jayanagar",
    )
    # Directory hospital with same name but missing pincode to disambiguate
    ambig_h = Hospital(
        hospital_name="City Hospital",
        state="Karnataka",
        district="Bengaluru",
        pincode=None,
    )
    db_session.add_all([ins1, ins2, ambig_h])
    db_session.commit()
    db_session.refresh(ambig_h)

    res = client.get(f"/api/v1/hospitals/{ambig_h.id}")
    assert res.status_code == 200
    data = res.json()
    assert data["network_status"] == STATUS_UNVERIFIED
    assert data["network_status_code"] == "UNVERIFIED"
    assert "Ambiguous" in data["network_status_explanation"]


def test_4_conflicting_or_missing_location_data(client: TestClient, db_session: Session):
    """
    Scenario 4: A hospital with conflicting or missing location data.
    Must return UNVERIFIED with an explicit explanation.
    """
    # Seed an insurer record
    ins = InsurerHospitalRecord(
        insurer_name="Star Health",
        hospital_name="Apollo Hospital",
        city="Bengaluru",
        state="Karnataka",
        pincode="560076",
    )
    db_session.add(ins)

    # 4A. Conflicting location: Andaman pincode (744101) with Karnataka state
    conflicting_h = Hospital(
        hospital_name="Apollo Hospital",
        state="Karnataka",
        district="Bengaluru Urban",
        pincode="744101",  # Andaman pincode!
    )
    db_session.add(conflicting_h)

    # 4B. Missing location: completely blank location
    missing_loc_h = Hospital(
        hospital_name="Apollo Hospital",
        state=None,
        district=None,
        pincode=None,
        address=None,
    )
    db_session.add(missing_loc_h)
    db_session.commit()
    db_session.refresh(conflicting_h)
    db_session.refresh(missing_loc_h)

    # Test conflicting
    res_conf = client.get(f"/api/v1/hospitals/{conflicting_h.id}")
    assert res_conf.status_code == 200
    d_conf = res_conf.json()
    assert d_conf["network_status"] == STATUS_UNVERIFIED
    assert d_conf["network_status_code"] == "UNVERIFIED"
    assert "Conflicting location" in d_conf["network_status_explanation"]

    # Test missing location
    res_miss = client.get(f"/api/v1/hospitals/{missing_loc_h.id}")
    assert res_miss.status_code == 200
    d_miss = res_miss.json()
    assert d_miss["network_status"] == STATUS_UNVERIFIED
    assert d_miss["network_status_code"] == "UNVERIFIED"
    assert "missing" in d_miss["network_status_explanation"].lower()


def test_5_bengaluru_search_does_not_return_south_andaman(client: TestClient, db_session: Session):
    """
    Scenario 5: A Bengaluru search must NOT return South Andaman hospitals.
    """
    # Seed a South Andaman hospital and a Bengaluru hospital
    andaman_h = Hospital(
        hospital_name="Chakraborty Multi Speciality Hospital",
        state="Andaman and Nicobar Islands",
        district="South Andaman",
        pincode="744101",
        address="Port Blair",
    )
    bengaluru_h = Hospital(
        hospital_name="Manipal Multi Speciality Hospital",
        state="Karnataka",
        district="Bengaluru Urban",
        pincode="560017",
        address="Old Airport Road, Bengaluru",
    )
    db_session.add_all([andaman_h, bengaluru_h])
    db_session.commit()

    # Query 1: search=Bengaluru
    res1 = client.get("/api/v1/hospitals?search=Bengaluru")
    assert res1.status_code == 200
    items1 = res1.json()["items"]
    assert len(items1) == 1
    assert items1[0]["hospital_name"] == "Manipal Multi Speciality Hospital"
    assert all("Andaman" not in (i.get("district") or "") for i in items1)

    # Query 2: location=Bengaluru
    res2 = client.get("/api/v1/hospitals?location=Bengaluru")
    assert res2.status_code == 200
    items2 = res2.json()["items"]
    assert len(items2) == 1
    assert items2[0]["hospital_name"] == "Manipal Multi Speciality Hospital"
    assert all("Andaman" not in (i.get("district") or "") for i in items2)

    # Query 3: district=Bengaluru
    res3 = client.get("/api/v1/hospitals?district=Bengaluru")
    assert res3.status_code == 200
    items3 = res3.json()["items"]
    assert len(items3) == 1
    assert items3[0]["hospital_name"] == "Manipal Multi Speciality Hospital"

    # Query 4: search="Bangalore" (alias normalization)
    res4 = client.get("/api/v1/hospitals?search=Bangalore")
    assert res4.status_code == 200
    items4 = res4.json()["items"]
    assert len(items4) == 1
    assert items4[0]["hospital_name"] == "Manipal Multi Speciality Hospital"

    # Query 5: search="Multi Speciality Bengaluru"
    res5 = client.get("/api/v1/hospitals?search=Multi Speciality Bengaluru")
    assert res5.status_code == 200
    items5 = res5.json()["items"]
    assert len(items5) == 1
    assert items5[0]["hospital_name"] == "Manipal Multi Speciality Hospital"
    assert all("Andaman" not in (i.get("district") or "") for i in items5)


def test_6_nationwide_search_and_south_andaman_unverified_status(client: TestClient, db_session: Session):
    """
    Scenario 6: Nationwide search returns hospitals from any region,
    but South Andaman results are UNVERIFIED with clear out-of-scope explanation,
    NEVER 'Not found in available network data'.
    """
    # Seed an insurer record for Bengaluru
    ins = InsurerHospitalRecord(
        insurer_name="Star Health",
        hospital_name="Apollo Hospital",
        city="Bengaluru",
        state="Karnataka",
        pincode="560076",
    )
    andaman_h = Hospital(
        hospital_name="Chakraborty Multi Speciality Hospital",
        state="Andaman and Nicobar Islands",
        district="South Andaman",
        pincode="744101",
        address="Port Blair",
    )
    bengaluru_h = Hospital(
        hospital_name="Apollo Hospital",
        state="Karnataka",
        district="Bengaluru Urban",
        pincode="560076",
    )
    db_session.add_all([ins, andaman_h, bengaluru_h])
    db_session.commit()

    # Nationwide request
    res = client.get("/api/v1/hospitals?nationwide=true")
    assert res.status_code == 200
    data = res.json()
    items = data["items"]
    assert len(items) == 2

    # Check Andaman hospital
    andaman_result = next(i for i in items if "Andaman" in (i.get("state") or ""))
    assert andaman_result["network_status"] == STATUS_UNVERIFIED
    assert andaman_result["network_status_code"] == "UNVERIFIED"
    assert "The available Star Health dataset contains only a limited Bengaluru sample" in andaman_result["network_status_explanation"]
    assert "verify with Star Health before planning cashless treatment" in andaman_result["network_status_explanation"]
    # CRITICAL: Must NOT be 'Not found in available network data'
    assert andaman_result["network_status"] != STATUS_NOT_FOUND


def test_7_empty_insurer_dataset(client: TestClient, db_session: Session):
    """
    Scenario 7: Insurer dataset with no matching records (0 records in table).
    Must return UNVERIFIED with empty-dataset explanation.
    """
    h = Hospital(
        hospital_name="General Hospital",
        state="Karnataka",
        district="Bengaluru Urban",
        pincode="560001",
    )
    db_session.add(h)
    db_session.commit()
    db_session.refresh(h)

    # Insurer table is empty
    res = client.get(f"/api/v1/hospitals/{h.id}")
    assert res.status_code == 200
    data = res.json()
    assert data["network_status"] == STATUS_UNVERIFIED
    assert data["network_status_code"] == "UNVERIFIED"
    assert "No insurer network dataset" in data["network_status_explanation"]


def test_8_kerudi_hospital_bagalkot_unverified(client: TestClient, db_session: Session):
    """
    Scenario 8: Kerudi Hospital And Research Centre in Bagalkot, Karnataka (587101).
    Absent from the Star Health 10-record Bengaluru sample.
    Since Bagalkot is outside the sample's documented geographic scope (Bengaluru),
    it MUST return UNVERIFIED, NOT 'Not found in available network data'.
    """
    # Seed insurer sample records in Bengaluru
    insurer1 = InsurerHospitalRecord(
        insurer_name="Star Health",
        hospital_name="Amar Nursing Home",
        city="Bengaluru",
        state="Karnataka",
        pincode="560018",
        network_type="Cashless",
    )
    insurer2 = InsurerHospitalRecord(
        insurer_name="Star Health",
        hospital_name="Apollo Hospitals - Bangalore",
        city="Bengaluru",
        state="Karnataka",
        pincode="560076",
        network_type="Cashless",
    )
    kerudi = Hospital(
        hospital_name="Kerudi Hospital And Research Centre",
        state="Karnataka",
        district="Bagalkot",
        pincode="587101",
        address="Extension Area Opp Axis Bank, Extension Area Opp Axis Bank",
    )
    db_session.add_all([insurer1, insurer2, kerudi])
    db_session.commit()
    db_session.refresh(kerudi)

    # Search for kerudi
    res = client.get("/api/v1/hospitals?search=kerudi")
    assert res.status_code == 200
    data = res.json()
    assert len(data["items"]) == 1
    item = data["items"][0]
    assert item["hospital_name"] == "Kerudi Hospital And Research Centre"
    assert item["district"] == "Bagalkot"
    assert item["state"] == "Karnataka"
    assert item["pincode"] == "587101"
    assert item["source_type"] == "Government Directory"

    # Status must be UNVERIFIED, NOT NOT_FOUND
    assert item["network_status"] == STATUS_UNVERIFIED
    assert item["network_status_code"] == "UNVERIFIED"
    expected_explanation = (
        "The available Star Health dataset contains only a limited Bengaluru sample. "
        "This hospital's network status cannot be confirmed using the available data. "
        "Please verify with Star Health before planning cashless treatment."
    )
    assert item["network_status_explanation"] == expected_explanation

    # Single endpoint verification
    single_res = client.get(f"/api/v1/hospitals/{kerudi.id}")
    assert single_res.status_code == 200
    single_data = single_res.json()
    assert single_data["network_status"] == STATUS_UNVERIFIED
    assert single_data["network_status_code"] == "UNVERIFIED"
    assert single_data["network_status_explanation"] == expected_explanation


def test_9_reusable_scope_check_unit():
    """
    Unit test for is_hospital_within_insurer_scope helper function.
    Validates dynamic scope deduction without hardcoding Bagalkot.
    """
    from backend.app.api.v1.hospitals import is_hospital_within_insurer_scope

    bengaluru_sample = [
        InsurerHospitalRecord(
            insurer_name="Star Health",
            hospital_name="Amar Nursing Home",
            city="Bengaluru",
            state="Karnataka",
            pincode="560018",
        ),
        InsurerHospitalRecord(
            insurer_name="Star Health",
            hospital_name="Bangalore Baptist Hospital",
            city="Bengaluru",
            state="Karnataka",
            pincode="560024",
        ),
    ]

    # Bagalkot facility -> outside Bengaluru scope -> False
    h_bagalkot = Hospital(
        hospital_name="Kerudi Hospital And Research Centre",
        state="Karnataka",
        district="Bagalkot",
        pincode="587101",
    )
    assert is_hospital_within_insurer_scope(h_bagalkot, bengaluru_sample) is False

    # Mysuru facility -> outside Bengaluru scope -> False
    h_mysuru = Hospital(
        hospital_name="Apollo BGS Hospital",
        state="Karnataka",
        district="Mysuru",
        pincode="570023",
    )
    assert is_hospital_within_insurer_scope(h_mysuru, bengaluru_sample) is False

    # South Andaman facility -> outside Karnataka/Bengaluru scope -> False
    h_andaman = Hospital(
        hospital_name="Chakraborty Hospital",
        state="Andaman and Nicobar Islands",
        district="South Andaman",
        pincode="744101",
    )
    assert is_hospital_within_insurer_scope(h_andaman, bengaluru_sample) is False

    # Bengaluru Urban facility -> inside scope -> True
    h_bengaluru_urban = Hospital(
        hospital_name="Community Hospital",
        state="Karnataka",
        district="Bengaluru Urban",
        pincode="560001",
    )
    assert is_hospital_within_insurer_scope(h_bengaluru_urban, bengaluru_sample) is True

    # Bengaluru Rural facility -> inside scope -> True
    h_bengaluru_rural = Hospital(
        hospital_name="Rural Health Centre",
        state="Karnataka",
        district="Bengaluru Rural",
        pincode="562123",
    )
    assert is_hospital_within_insurer_scope(h_bengaluru_rural, bengaluru_sample) is True

    # Address-only Bengaluru facility -> inside scope -> True
    h_addr_bengaluru = Hospital(
        hospital_name="Speciality Clinic",
        state="Karnataka",
        address="Indiranagar, Bangalore",
    )
    assert is_hospital_within_insurer_scope(h_addr_bengaluru, bengaluru_sample) is True

    # Empty insurer records -> False
    assert is_hospital_within_insurer_scope(h_bengaluru_urban, []) is False

