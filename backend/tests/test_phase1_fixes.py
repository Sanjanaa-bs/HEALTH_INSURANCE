"""
Unit Tests for Phase 1 Code Fixes:
1. Evidence gate: unique keywords, whole-word matching, pre/post-hospitalization equivalence.
2. Search page label dynamic calculation without hardcoded denominators.
3. Insurer network hospital ingestion location verification on exact-name matches.
"""

import pytest
import re
from unittest.mock import MagicMock

from backend.app.search import (
    normalize_insurance_query_text,
    normalize_query_words,
    format_page_label,
)
from backend.app.services.qa import extract_meaningful_keywords
from scripts.ingest_insurer_networks import (
    normalize_hospital_name,
    match_directory_hospital,
)
from backend.app.models.hospital import Hospital


def test_normalize_insurance_query_text_equivalence():
    """Verify pre-hospitalization variants map to canonical token."""
    variants = [
        "What is the limit for pre-hospitalization expenses?",
        "What is the limit for pre hospitalization expenses?",
        "What is the limit for prehospitalization expenses?",
        "What is the limit for medical expenses prior to hospitalization?",
        "What is the limit for medical expenses before hospitalization?",
        "What is the limit for pre-hospitalisation expenses?",
    ]
    for v in variants:
        norm = normalize_insurance_query_text(v)
        assert "prehospitalization" in norm, f"Failed to normalize variant: {v}"

    # Also test post-hospitalization
    post_variants = [
        "post-hospitalization expenses",
        "post hospitalization expenses",
        "posthospitalization expenses",
        "after hospitalization expenses",
        "following hospitalization expenses",
    ]
    for pv in post_variants:
        norm = normalize_insurance_query_text(pv)
        assert "posthospitalization" in norm, f"Failed post-hospitalization: {pv}"


def test_extract_meaningful_keywords_uniqueness():
    """Verify keyword extraction returns unique tokens without repetition bias."""
    query = "room rent room rent room rent expenses"
    unique_kw = extract_meaningful_keywords(query, legacy=False)
    assert len(unique_kw) == len(set(unique_kw)), "Keywords should be unique"
    assert unique_kw == ["room", "rent", "expenses"]

    # Legacy returns non-unique keywords
    legacy_kw = extract_meaningful_keywords(query, legacy=True)
    assert legacy_kw.count("room") == 3
    assert legacy_kw.count("rent") == 3


def test_whole_word_matching_vs_substring():
    """Verify that whole-word matching prevents false partial substring triggers."""
    passage = "The patient received an authorized certificate for cardiac care."
    # Query keyword "car"
    kw = "car"
    # Substring matching (legacy) matches "cardiac" or "certificate"
    assert kw in passage.lower(), "Substring match would trigger"

    # Whole-word regex matching does NOT match
    has_whole_word = bool(re.search(rf"\b{re.escape(kw)}\b", passage.lower()))
    assert not has_whole_word, "Whole-word matching should not trigger on 'cardiac' or 'certificate'"

    # But genuine "car" matches
    car_passage = "Ambulance charges or car travel are excluded."
    assert bool(re.search(rf"\b{re.escape(kw)}\b", car_passage.lower()))


def test_format_page_label_dynamic():
    """Verify format_page_label derives printed page denominators dynamically without hardcoding."""
    # Policy with 48 total pages -> 47 printed pages
    printed, label = format_page_label("policy", 10, total_pages=48)
    assert printed == 9
    assert label == "Physical Page 10 (Printed Page 9/47)"

    # Policy with 30 total pages -> 29 printed pages
    printed, label = format_page_label("policy", 10, total_pages=30)
    assert printed == 9
    assert label == "Physical Page 10 (Printed Page 9/29)"

    # Policy without total_pages metadata (no hardcoded /47)
    printed, label = format_page_label("policy", 10, total_pages=None)
    assert printed == 9
    assert label == "Physical Page 10 (Printed Page 9)"
    assert "/47" not in label

    # Cover page
    p_cover, l_cover = format_page_label("policy", 1)
    assert p_cover is None
    assert l_cover == "Physical Page 1 (Cover Page)"


def test_match_directory_hospital_strict_location():
    """Verify that exact-name hospital match requires location verification under strict check."""
    # Mock hospital in Bagalkot, Karnataka
    bagalkot_hospital = Hospital(
        id=101,
        hospital_name="City General Hospital",
        state="Karnataka",
        district="Bagalkot",
        pincode="587101",
        address="Station Road, Bagalkot",
    )

    # Insurer card for Bengaluru network record
    bengaluru_card = {
        "hospital_name": "City General Hospital",
        "state": "Karnataka",
        "city": "Bengaluru",
        "pincode": "560001",
    }

    mock_db = MagicMock()
    mock_db.query.return_value.filter.return_value.all.return_value = [bagalkot_hospital]

    # Legacy behavior: linked because exact name matches and len(exact_matches) == 1 in Karnataka
    legacy_match = match_directory_hospital(mock_db, bengaluru_card, strict_location_check=False)
    assert legacy_match is not None, "Legacy should erroneously match across cities"

    # Strict behavior: rejects because Bagalkot != Bengaluru and pincode 587101 != 560001
    strict_match = match_directory_hospital(mock_db, bengaluru_card, strict_location_check=True)
    assert strict_match is None, "Strict check must reject cross-city match"

    # When location matches Bengaluru, strict check accepts
    bengaluru_hospital = Hospital(
        id=102,
        hospital_name="City General Hospital",
        state="Karnataka",
        district="Bengaluru Urban",
        pincode="560001",
        address="MG Road, Bengaluru",
    )
    mock_db.query.return_value.filter.return_value.all.return_value = [bengaluru_hospital]
    strict_match_valid = match_directory_hospital(mock_db, bengaluru_card, strict_location_check=True)
    assert strict_match_valid is not None
    assert strict_match_valid.id == 102
