import math
import re
import unicodedata
from typing import Optional, List, Tuple
from fastapi import APIRouter, Depends, Query, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy import or_, and_, func

from backend.app.database import get_db
from backend.app.models.hospital import Hospital, InsurerHospitalRecord
from backend.app.schemas.hospital import (
    HospitalRead,
    HospitalListResponse,
    InsurerHospitalRecordRead,
    InsurerHospitalListResponse,
)
from backend.app.schemas.common import PaginationMeta

router = APIRouter(tags=["Hospitals"])

DATASET_SCOPE_BENGALURU = "Star Health offline sample (Bengaluru, Karnataka - 10 records)"

# Three Canonical Statuses
STATUS_LISTED = "Listed in Star Health network data"
STATUS_NOT_FOUND = "Not found in available network data"
STATUS_UNVERIFIED = "Network status unverified"


def normalize_hospital_name(value: Optional[str]) -> str:
    """Normalize hospital name ignoring case, punctuation, whitespace, and legal suffixes."""
    if not value or not isinstance(value, str):
        return ""
    val = value.replace("&", " and ").replace("'", "").replace("’", "")
    normalized = unicodedata.normalize("NFKD", val).encode("ascii", "ignore").decode("ascii")
    tokens = re.findall(r"[a-z0-9]+", normalized.lower())
    tokens = ["hospital" if token == "hospitals" else token for token in tokens]
    while tokens and tokens[-1] in {"pvt", "private", "ltd", "limited", "llp", "inc"}:
        tokens.pop()
    return " ".join(tokens)


def check_location_conflict(
    state: Optional[str],
    district: Optional[str],
    pincode: Optional[str],
) -> Tuple[bool, Optional[str]]:
    """Validate location fields for internal consistency and format."""
    if pincode and str(pincode).strip():
        pin = str(pincode).strip()
        if not re.match(r"^\d{6}$", pin):
            return True, f"Malformed pincode '{pin}' (must be 6 digits)"

        if state and str(state).strip():
            s = str(state).strip().lower()
            if "andaman" in s and not pin.startswith("744"):
                return True, f"Pincode {pin} contradicts state '{state}'"
            if "karnataka" in s and not pin.startswith(("56", "57", "58", "59")):
                return True, f"Pincode {pin} contradicts state '{state}'"
            if "delhi" in s and not pin.startswith("11"):
                return True, f"Pincode {pin} contradicts state '{state}'"
            if "maharashtra" in s and not pin.startswith(("40", "41", "42", "43", "44")):
                return True, f"Pincode {pin} contradicts state '{state}'"
            if "tamil" in s and not pin.startswith(("60", "61", "62", "63", "64")):
                return True, f"Pincode {pin} contradicts state '{state}'"

        if district and str(district).strip():
            d = str(district).strip().lower()
            if ("bengaluru" in d or "bangalore" in d) and pin.startswith(("744", "110", "400", "600")):
                return True, f"Pincode {pin} contradicts district '{district}'"
            if "south andaman" in d and not pin.startswith("744"):
                return True, f"Pincode {pin} contradicts district '{district}'"

    if state and district:
        s = str(state).strip().lower()
        d = str(district).strip().lower()
        if "andaman" in s and ("bengaluru" in d or "bangalore" in d):
            return True, f"District '{district}' contradicts state '{state}'"
        if "karnataka" in s and "south andaman" in d:
            return True, f"District '{district}' contradicts state '{state}'"

    return False, None


def location_compatible(
    h_state: Optional[str],
    h_district: Optional[str],
    h_pincode: Optional[str],
    r_state: Optional[str],
    r_city: Optional[str],
    r_pincode: Optional[str],
) -> bool:
    """Check if location between directory facility and insurer record is compatible."""
    # Direct pincode check
    if h_pincode and r_pincode and str(h_pincode).strip() and str(r_pincode).strip():
        hp = str(h_pincode).strip()
        rp = str(r_pincode).strip()
        if hp == rp:
            return True
        if len(hp) == 6 and len(rp) == 6 and hp[:3] != rp[:3]:
            return False

    # State contradiction check
    if h_state and r_state:
        s1 = str(h_state).strip().lower()
        s2 = str(r_state).strip().lower()
        if s1 and s2 and s1 != s2 and s1 not in s2 and s2 not in s1:
            return False

    # City / District compatibility
    if r_city and h_district:
        c = str(r_city).strip().lower()
        d = str(h_district).strip().lower()
        if ("bengaluru" in c or "bangalore" in c) and ("bengaluru" in d or "bangalore" in d):
            return True
        if c in d or d in c:
            return True
        if ("bengaluru" in c or "bangalore" in c) and not ("bengaluru" in d or "bangalore" in d or "karnataka" in (h_state or "").lower()):
            return False

    # State match
    if h_state and r_state:
        s1 = str(h_state).strip().lower()
        s2 = str(r_state).strip().lower()
        if s1 == s2 or s1 in s2 or s2 in s1:
            return True

    return True


def build_bengaluru_hospital_filter():
    """Construct SQL filter strictly matching Bengaluru facilities."""
    return or_(
        Hospital.district.ilike("%Bengaluru%"),
        Hospital.district.ilike("%Bangalore%"),
        and_(
            Hospital.state.ilike("%Karnataka%"),
            or_(
                Hospital.address.ilike("%Bengaluru%"),
                Hospital.address.ilike("%Bangalore%"),
            ),
        ),
        Hospital.pincode.like("560%"),
        Hospital.pincode.like("561%"),
        Hospital.pincode.like("562%"),
    )


def is_hospital_within_insurer_scope(
    hospital: Hospital,
    insurer_records: List[InsurerHospitalRecord],
) -> bool:
    """
    Determine whether a hospital's verified location falls within the geographic
    scope of the available insurer dataset.

    Dynamically inspects the insurer records to identify covered states, cities,
    and postal regions, rather than hardcoding specific external districts.
    """
    if not insurer_records:
        return False

    # Extract covered geographic scope from the insurer records
    covered_states = set()
    covered_cities = set()
    covered_pincode_prefixes = set()

    for r in insurer_records:
        if r.state and str(r.state).strip():
            covered_states.add(str(r.state).strip().lower())
        if r.city and str(r.city).strip():
            c = str(r.city).strip().lower()
            covered_cities.add(c)
            if "bengaluru" in c or "bangalore" in c:
                covered_cities.add("bengaluru")
                covered_cities.add("bangalore")
        if r.pincode and str(r.pincode).strip():
            pin = str(r.pincode).strip()
            if len(pin) >= 3:
                pfx = pin[:3]
                covered_pincode_prefixes.add(pfx)
                if pfx.startswith("560"):
                    covered_pincode_prefixes.update(["560", "561", "562"])

    # 1. State check: hospital state must match covered states (if state is present)
    if hospital.state and str(hospital.state).strip():
        h_state = str(hospital.state).strip().lower()
        if not any(s in h_state or h_state in s for s in covered_states):
            return False

    # 2. Scope check when insurer data is restricted to specific cities/regions
    if covered_cities:
        h_dist = (hospital.district or "").strip().lower()
        h_pin = str(hospital.pincode).strip() if hospital.pincode else ""
        h_addr = (hospital.address or "").strip().lower()

        # Check district match
        district_matches = any(c in h_dist for c in covered_cities) if h_dist else False

        # If district is specified but does not match any covered city
        if h_dist and not district_matches:
            return False

        # Check pincode prefix match
        pincode_matches = any(h_pin.startswith(pfx) for pfx in covered_pincode_prefixes) if h_pin else False

        # If pincode is specified and has at least 3 digits:
        # If it contradicts the covered prefixes, it's outside the scope
        if h_pin and len(h_pin) >= 3 and covered_pincode_prefixes and not pincode_matches:
            return False

        # Check address mention of covered cities
        address_matches = any(c in h_addr for c in covered_cities) if h_addr else False

        # To be confirmed within scope, at least one verified positive indicator must hold
        # (matching district, matching pincode prefix, or address within covered state)
        if district_matches or pincode_matches or (address_matches and (not hospital.state or any(s in (hospital.state or "").lower() for s in covered_states))):
            return True

        # If none of the indicators confirm the hospital is within the covered city scope:
        return False

    # If insurer records cover entire state (no city restrictions), state match is sufficient
    return True


def evaluate_hospital_network_details(
    hospital: Hospital,
    insurer_records: List[InsurerHospitalRecord],
    total_insurer_records: int,
) -> Tuple[str, str, str, str]:
    """
    Search insurer_hospital_records table to determine Star Health network membership.

    Returns a 4-tuple:
    (network_status, network_status_code, explanation, dataset_scope)

    Statuses:
    - LISTED: Supported matching record in insurer dataset.
    - NOT_FOUND: Searched within dataset geographic scope, no match found.
    - UNVERIFIED: Outside scope, ambiguous, conflicting, incomplete, or empty dataset.
    """
    # 1. Empty insurer dataset
    if total_insurer_records == 0:
        return (
            STATUS_UNVERIFIED,
            "UNVERIFIED",
            "No insurer network dataset is available for comparison.",
            "None",
        )

    # 2. Check for missing or invalid hospital name
    norm_h = normalize_hospital_name(hospital.hospital_name)
    if not norm_h or len(norm_h) < 2:
        return (
            STATUS_UNVERIFIED,
            "UNVERIFIED",
            "Incomplete record details: hospital name is missing or invalid.",
            DATASET_SCOPE_BENGALURU,
        )

    # 3. Check for missing location data
    if not hospital.state and not hospital.district and not hospital.pincode and not hospital.address:
        return (
            STATUS_UNVERIFIED,
            "UNVERIFIED",
            "Incomplete record details: location and address are missing.",
            DATASET_SCOPE_BENGALURU,
        )

    # 4. Check for conflicting location data
    has_conflict, conflict_reason = check_location_conflict(
        hospital.state, hospital.district, hospital.pincode
    )
    if has_conflict:
        return (
            STATUS_UNVERIFIED,
            "UNVERIFIED",
            f"Conflicting location details: {conflict_reason}.",
            DATASET_SCOPE_BENGALURU,
        )

    # 5. Direct Foreign-Key link or matched_hospital_id relationship
    if hospital.insurer_records and len(hospital.insurer_records) > 0:
        return (
            STATUS_LISTED,
            "LISTED",
            "Matched in available Star Health network data. Cashless access is subject to policy terms and insurer pre-authorization.",
            DATASET_SCOPE_BENGALURU,
        )

    for r in insurer_records:
        if r.matched_hospital_id == hospital.id:
            return (
                STATUS_LISTED,
                "LISTED",
                "Matched in available Star Health network data. Cashless access is subject to policy terms and insurer pre-authorization.",
                DATASET_SCOPE_BENGALURU,
            )

    # 6. Search insurer_hospital_records table with careful name matching
    matching_records = []
    for r in insurer_records:
        norm_r = normalize_hospital_name(r.hospital_name)
        if not norm_r:
            continue
        if norm_h == norm_r:
            if location_compatible(
                hospital.state,
                hospital.district,
                hospital.pincode,
                r.state,
                r.city,
                r.pincode,
            ):
                matching_records.append(r)

    # Handle ambiguous multiple matches
    if len(matching_records) > 1:
        pincode_matches = [
            r for r in matching_records
            if r.pincode and hospital.pincode and str(r.pincode).strip() == str(hospital.pincode).strip()
        ]
        if len(pincode_matches) == 1:
            return (
                STATUS_LISTED,
                "LISTED",
                "Matched in available Star Health network data. Cashless access is subject to policy terms and insurer pre-authorization.",
                DATASET_SCOPE_BENGALURU,
            )
        return (
            STATUS_UNVERIFIED,
            "UNVERIFIED",
            "Ambiguous hospital name with multiple candidate matches in insurer network data.",
            DATASET_SCOPE_BENGALURU,
        )

    if len(matching_records) == 1:
        return (
            STATUS_LISTED,
            "LISTED",
            "Matched in available Star Health network data. Cashless access is subject to policy terms and insurer pre-authorization.",
            DATASET_SCOPE_BENGALURU,
        )

    # Check for overly generic / ambiguous name
    tokens = norm_h.split()
    generic_words = {"hospital", "clinic", "health", "care", "centre", "center", "nursing", "home", "medical"}
    if all(t in generic_words for t in tokens) or len(tokens) == 0:
        return (
            STATUS_UNVERIFIED,
            "UNVERIFIED",
            "Ambiguous or generic hospital name. Network status cannot be reliably verified.",
            DATASET_SCOPE_BENGALURU,
        )

    # 7. Geographic scope check against available insurer dataset
    within_scope = is_hospital_within_insurer_scope(hospital, insurer_records)
    if within_scope:
        return (
            STATUS_NOT_FOUND,
            "NOT_FOUND",
            "No matching record found in the available Star Health dataset (offline Bengaluru sample). This does not prove the hospital is out of network.",
            DATASET_SCOPE_BENGALURU,
        )

    # Outside geographic scope (e.g. Bagalkot, South Andaman, Maharashtra, Delhi, or unverified location):
    return (
        STATUS_UNVERIFIED,
        "UNVERIFIED",
        "The available Star Health dataset contains only a limited Bengaluru sample. This hospital's network status cannot be confirmed using the available data. Please verify with Star Health before planning cashless treatment.",
        DATASET_SCOPE_BENGALURU,
    )


def determine_hospital_network_status(
    hospital: Hospital,
    insurer_records: List[InsurerHospitalRecord],
    total_insurer_records: int,
) -> str:
    """Backwards-compatible wrapper returning the network status string."""
    status_str, _, _, _ = evaluate_hospital_network_details(
        hospital, insurer_records, total_insurer_records
    )
    return status_str



@router.get("/hospitals", response_model=HospitalListResponse)
def get_hospitals(
    page: int = Query(1, ge=1, description="Page number"),
    page_size: int = Query(20, ge=1, le=100, description="Items per page"),
    search: Optional[str] = Query(None, description="Search term for name or address"),
    location: Optional[str] = Query(None, description="Filter by location (city, district, or state)"),
    city: Optional[str] = Query(None, description="Filter by city"),
    district: Optional[str] = Query(None, description="Filter by district"),
    state: Optional[str] = Query(None, description="Filter by state"),
    pincode: Optional[str] = Query(None, description="Filter by pincode"),
    source: Optional[str] = Query(None, description="Source filter: 'govt' / 'national' or 'insurer' / 'star'"),
    nationwide: Optional[bool] = Query(False, description="Explicit nationwide search"),
    db: Session = Depends(get_db),
):
    """Retrieve paginated hospital directory entries with location filtering and source routing."""
    page = page if isinstance(page, int) and page >= 1 else 1
    page_size = page_size if isinstance(page_size, int) and page_size >= 1 else 20
    search = search.strip() if isinstance(search, str) and search.strip() else None
    location = location.strip() if isinstance(location, str) and location.strip() else None
    city = city.strip() if isinstance(city, str) and city.strip() else None
    district = district.strip() if isinstance(district, str) and district.strip() else None
    state = state.strip() if isinstance(state, str) and state.strip() else None
    pincode = pincode.strip() if isinstance(pincode, str) and pincode.strip() else None
    source = source.strip() if isinstance(source, str) and source.strip() else None

    # Route to insurer network if source explicitly requests insurer / Star Health records
    if source and source.lower() in ("insurer", "star", "star_health"):
        query = db.query(InsurerHospitalRecord)

        if search:
            search_pattern = f"%{search}%"
            match_conditions = [
                InsurerHospitalRecord.hospital_name.ilike(search_pattern),
                InsurerHospitalRecord.address.ilike(search_pattern),
                InsurerHospitalRecord.city.ilike(search_pattern),
                InsurerHospitalRecord.state.ilike(search_pattern),
                InsurerHospitalRecord.pincode.ilike(search_pattern),
            ]
            tokens = [t for t in search.split() if len(t) > 1]
            if len(tokens) > 1:
                token_conditions = []
                for token in tokens:
                    tok_pat = f"%{token}%"
                    token_conditions.append(
                        or_(
                            InsurerHospitalRecord.hospital_name.ilike(tok_pat),
                            InsurerHospitalRecord.address.ilike(tok_pat),
                            InsurerHospitalRecord.city.ilike(tok_pat),
                            InsurerHospitalRecord.state.ilike(tok_pat),
                            InsurerHospitalRecord.pincode.ilike(tok_pat),
                        )
                    )
                query = query.filter(or_(or_(*match_conditions), and_(*token_conditions)))
            else:
                query = query.filter(or_(*match_conditions))

        loc_filter = location or city or district
        if loc_filter:
            if "bengaluru" in loc_filter.lower() or "bangalore" in loc_filter.lower():
                query = query.filter(
                    or_(
                        InsurerHospitalRecord.city.ilike("%Bengaluru%"),
                        InsurerHospitalRecord.city.ilike("%Bangalore%"),
                        InsurerHospitalRecord.address.ilike("%Bengaluru%"),
                        InsurerHospitalRecord.address.ilike("%Bangalore%"),
                    )
                )
            else:
                query = query.filter(
                    or_(
                        InsurerHospitalRecord.city.ilike(f"%{loc_filter}%"),
                        InsurerHospitalRecord.state.ilike(f"%{loc_filter}%"),
                        InsurerHospitalRecord.address.ilike(f"%{loc_filter}%"),
                    )
                )

        if state:
            if "bengaluru" in state.lower() or "bangalore" in state.lower():
                query = query.filter(
                    or_(
                        InsurerHospitalRecord.city.ilike("%Bengaluru%"),
                        InsurerHospitalRecord.city.ilike("%Bangalore%"),
                    )
                )
            else:
                query = query.filter(InsurerHospitalRecord.state.ilike(f"%{state}%"))

        if pincode:
            query = query.filter(InsurerHospitalRecord.pincode == pincode)

        total_items = query.count()
        total_pages = math.ceil(total_items / page_size) if total_items > 0 else 0
        offset = (page - 1) * page_size
        records = query.order_by(InsurerHospitalRecord.id.asc()).offset(offset).limit(page_size).all()

        items = [
            HospitalRead(
                id=r.id,
                hospital_name=r.hospital_name,
                address=r.address,
                state=r.state,
                district=r.city,
                pincode=r.pincode,
                total_beds=r.matched_hospital.total_beds if r.matched_hospital else None,
                source_type="Insurer Network (Star Health)",
                network_status=STATUS_LISTED,
                network_status_code="LISTED",
                network_status_explanation=(
                    "Imported from offline Star Health Bengaluru network sample. "
                    "Cashless access is subject to policy terms and pre-authorization."
                ),
                dataset_scope=DATASET_SCOPE_BENGALURU,
                created_at=r.created_at,
                updated_at=r.created_at,
            )
            for r in records
        ]

        return HospitalListResponse(
            items=items,
            pagination=PaginationMeta(
                page=page,
                page_size=page_size,
                total_items=total_items,
                total_pages=total_pages,
            ),
        )

    # Standard Government / National Directory query
    query = db.query(Hospital)

    # 1. Pincode filter
    if pincode:
        query = query.filter(Hospital.pincode == pincode)

    # 2. Location / District / City filter
    loc_target = location or district or city
    if loc_target:
        if "bengaluru" in loc_target.lower() or "bangalore" in loc_target.lower():
            query = query.filter(build_bengaluru_hospital_filter())
        else:
            query = query.filter(
                or_(
                    Hospital.district.ilike(f"%{loc_target}%"),
                    Hospital.state.ilike(f"%{loc_target}%"),
                    Hospital.address.ilike(f"%{loc_target}%"),
                    Hospital.subdistrict.ilike(f"%{loc_target}%"),
                )
            )

    # 3. State filter
    if state:
        # Handle cases where user typed 'Bengaluru' or 'Bangalore' in the state field
        if "bengaluru" in state.lower() or "bangalore" in state.lower():
            query = query.filter(build_bengaluru_hospital_filter())
        else:
            query = query.filter(Hospital.state.ilike(f"%{state}%"))

    # 4. Search query parsing
    if search:
        search_lower = search.lower()
        if search_lower in ("bengaluru", "bangalore"):
            query = query.filter(build_bengaluru_hospital_filter())
        else:
            tokens = [t for t in search.split() if len(t) > 1]
            has_bengaluru_token = any(t.lower() in ("bengaluru", "bangalore") for t in tokens)

            if has_bengaluru_token:
                # Constrain search to Bengaluru and match other tokens against name/address
                non_loc_tokens = [t for t in tokens if t.lower() not in ("bengaluru", "bangalore")]
                token_filters = []
                for t in non_loc_tokens:
                    tok_pat = f"%{t}%"
                    token_filters.append(
                        or_(
                            Hospital.hospital_name.ilike(tok_pat),
                            Hospital.address.ilike(tok_pat),
                            Hospital.specialties.ilike(tok_pat),
                        )
                    )
                loc_condition = build_bengaluru_hospital_filter()
                if token_filters:
                    query = query.filter(and_(loc_condition, *token_filters))
                else:
                    query = query.filter(loc_condition)
            elif len(tokens) > 1:
                search_pattern = f"%{search}%"
                match_conditions = [
                    Hospital.hospital_name.ilike(search_pattern),
                    Hospital.address.ilike(search_pattern),
                    Hospital.state.ilike(search_pattern),
                    Hospital.district.ilike(search_pattern),
                    Hospital.subdistrict.ilike(search_pattern),
                    Hospital.specialties.ilike(search_pattern),
                ]
                token_conditions = []
                for token in tokens:
                    tok_pat = f"%{token}%"
                    token_conditions.append(
                        or_(
                            Hospital.hospital_name.ilike(tok_pat),
                            Hospital.address.ilike(tok_pat),
                            Hospital.state.ilike(tok_pat),
                            Hospital.district.ilike(tok_pat),
                            Hospital.subdistrict.ilike(tok_pat),
                            Hospital.specialties.ilike(tok_pat),
                        )
                    )
                query = query.filter(or_(or_(*match_conditions), and_(*token_conditions)))
            else:
                search_pattern = f"%{search}%"
                query = query.filter(
                    or_(
                        Hospital.hospital_name.ilike(search_pattern),
                        Hospital.address.ilike(search_pattern),
                        Hospital.state.ilike(search_pattern),
                        Hospital.district.ilike(search_pattern),
                        Hospital.subdistrict.ilike(search_pattern),
                        Hospital.pincode.ilike(search_pattern),
                        Hospital.specialties.ilike(search_pattern),
                    )
                )

    total_items = query.count()
    total_pages = math.ceil(total_items / page_size) if total_items > 0 else 0

    offset = (page - 1) * page_size
    items = query.order_by(Hospital.id.asc()).offset(offset).limit(page_size).all()

    # Search insurer_hospital_records table to evaluate network status
    all_insurer_records = db.query(InsurerHospitalRecord).all()
    total_insurer_records = len(all_insurer_records)

    result_items = []
    for h in items:
        status_val, status_code, expl, scope = evaluate_hospital_network_details(
            h, all_insurer_records, total_insurer_records
        )
        h_read = HospitalRead(
            id=h.id,
            sr_no=h.sr_no,
            hospital_name=h.hospital_name,
            hospital_category=h.hospital_category,
            care_type=h.care_type,
            discipline=h.discipline,
            address=h.address,
            state=h.state,
            district=h.district,
            subdistrict=h.subdistrict,
            pincode=h.pincode,
            telephone=h.telephone,
            mobile_number=h.mobile_number,
            emergency_num=h.emergency_num,
            ambulance_phone=h.ambulance_phone,
            bloodbank_phone=h.bloodbank_phone,
            email=h.email,
            website=h.website,
            specialties=h.specialties,
            facilities=h.facilities,
            total_beds=h.total_beds,
            latitude=h.latitude,
            longitude=h.longitude,
            source_type="Government Directory",
            network_status=status_val,
            network_status_code=status_code,
            network_status_explanation=expl,
            dataset_scope=scope,
            created_at=h.created_at,
            updated_at=h.updated_at,
        )
        result_items.append(h_read)

    return HospitalListResponse(
        items=result_items,
        pagination=PaginationMeta(
            page=page,
            page_size=page_size,
            total_items=total_items,
            total_pages=total_pages,
        ),
    )


@router.get("/hospitals/insurer-network", response_model=InsurerHospitalListResponse)
def get_insurer_network_hospitals(
    page: int = Query(1, ge=1, description="Page number"),
    page_size: int = Query(20, ge=1, le=100, description="Items per page"),
    search: Optional[str] = Query(None, description="Search hospital name or address"),
    location: Optional[str] = Query(None, description="Filter by location (city or state)"),
    city: Optional[str] = Query(None, description="Filter by city"),
    state: Optional[str] = Query(None, description="Filter by state"),
    pincode: Optional[str] = Query(None, description="Filter by pincode"),
    source: Optional[str] = Query(None, description="Source filter (e.g. 'insurer', 'star')"),
    db: Session = Depends(get_db),
):
    """Retrieve paginated insurer-specific hospital network records (e.g. Star Health)."""
    page = page if isinstance(page, int) and page >= 1 else 1
    page_size = page_size if isinstance(page_size, int) and page_size >= 1 else 20
    search = search.strip() if isinstance(search, str) and search.strip() else None
    location = location.strip() if isinstance(location, str) and location.strip() else None
    city = city.strip() if isinstance(city, str) and city.strip() else None
    state = state.strip() if isinstance(state, str) and state.strip() else None
    pincode = pincode.strip() if isinstance(pincode, str) and pincode.strip() else None

    query = db.query(InsurerHospitalRecord)

    if search:
        search_pattern = f"%{search}%"
        match_conditions = [
            InsurerHospitalRecord.hospital_name.ilike(search_pattern),
            InsurerHospitalRecord.address.ilike(search_pattern),
            InsurerHospitalRecord.city.ilike(search_pattern),
            InsurerHospitalRecord.state.ilike(search_pattern),
            InsurerHospitalRecord.pincode.ilike(search_pattern),
        ]
        tokens = [t for t in search.split() if len(t) > 1]
        if len(tokens) > 1:
            token_conditions = []
            for token in tokens:
                tok_pat = f"%{token}%"
                token_conditions.append(
                    or_(
                        InsurerHospitalRecord.hospital_name.ilike(tok_pat),
                        InsurerHospitalRecord.address.ilike(tok_pat),
                        InsurerHospitalRecord.city.ilike(tok_pat),
                        InsurerHospitalRecord.state.ilike(tok_pat),
                        InsurerHospitalRecord.pincode.ilike(tok_pat),
                    )
                )
            query = query.filter(or_(or_(*match_conditions), and_(*token_conditions)))
        else:
            query = query.filter(or_(*match_conditions))

    loc_target = location or city
    if loc_target:
        if "bengaluru" in loc_target.lower() or "bangalore" in loc_target.lower():
            query = query.filter(
                or_(
                    InsurerHospitalRecord.city.ilike("%Bengaluru%"),
                    InsurerHospitalRecord.city.ilike("%Bangalore%"),
                    InsurerHospitalRecord.address.ilike("%Bengaluru%"),
                    InsurerHospitalRecord.address.ilike("%Bangalore%"),
                )
            )
        else:
            query = query.filter(
                or_(
                    InsurerHospitalRecord.city.ilike(f"%{loc_target}%"),
                    InsurerHospitalRecord.state.ilike(f"%{loc_target}%"),
                    InsurerHospitalRecord.address.ilike(f"%{loc_target}%"),
                )
            )

    if state:
        if "bengaluru" in state.lower() or "bangalore" in state.lower():
            query = query.filter(
                or_(
                    InsurerHospitalRecord.city.ilike("%Bengaluru%"),
                    InsurerHospitalRecord.city.ilike("%Bangalore%"),
                )
            )
        else:
            query = query.filter(InsurerHospitalRecord.state.ilike(f"%{state}%"))

    if pincode:
        query = query.filter(InsurerHospitalRecord.pincode == pincode)

    total_items = query.count()
    total_pages = math.ceil(total_items / page_size) if total_items > 0 else 0
    offset = (page - 1) * page_size
    records = query.order_by(InsurerHospitalRecord.id.asc()).offset(offset).limit(page_size).all()

    items = [
        InsurerHospitalRecordRead(
            id=r.id,
            insurer_name=r.insurer_name,
            hospital_name=r.hospital_name,
            city=r.city,
            state=r.state,
            pincode=r.pincode,
            address=r.address,
            network_type=r.network_type,
            total_beds=r.matched_hospital.total_beds if r.matched_hospital else None,
            source_type="Insurer Network (Star Health)",
            network_status=STATUS_LISTED,
            network_status_code="LISTED",
            network_status_explanation=(
                "Imported from offline Star Health Bengaluru network sample. "
                "Cashless access is subject to policy terms and pre-authorization."
            ),
            dataset_scope=DATASET_SCOPE_BENGALURU,
            matched_hospital_id=r.matched_hospital_id,
            created_at=r.created_at,
        )
        for r in records
    ]

    return InsurerHospitalListResponse(
        items=items,
        pagination=PaginationMeta(
            page=page,
            page_size=page_size,
            total_items=total_items,
            total_pages=total_pages,
        ),
    )


@router.get("/hospitals/{hospital_id}", response_model=HospitalRead)
def get_hospital_by_id(hospital_id: int, db: Session = Depends(get_db)):
    """Fetch a single hospital by ID with verified network status."""
    hospital = db.query(Hospital).filter(Hospital.id == hospital_id).first()
    if not hospital:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Hospital with ID {hospital_id} not found",
        )
    all_insurer_records = db.query(InsurerHospitalRecord).all()
    total_insurer_records = len(all_insurer_records)
    status_val, status_code, expl, scope = evaluate_hospital_network_details(
        hospital, all_insurer_records, total_insurer_records
    )
    return HospitalRead(
        id=hospital.id,
        sr_no=hospital.sr_no,
        hospital_name=hospital.hospital_name,
        hospital_category=hospital.hospital_category,
        care_type=hospital.care_type,
        discipline=hospital.discipline,
        address=hospital.address,
        state=hospital.state,
        district=hospital.district,
        subdistrict=hospital.subdistrict,
        pincode=hospital.pincode,
        telephone=hospital.telephone,
        mobile_number=hospital.mobile_number,
        emergency_num=hospital.emergency_num,
        ambulance_phone=hospital.ambulance_phone,
        bloodbank_phone=hospital.bloodbank_phone,
        email=hospital.email,
        website=hospital.website,
        specialties=hospital.specialties,
        facilities=hospital.facilities,
        total_beds=hospital.total_beds,
        latitude=hospital.latitude,
        longitude=hospital.longitude,
        source_type="Government Directory",
        network_status=status_val,
        network_status_code=status_code,
        network_status_explanation=expl,
        dataset_scope=scope,
        created_at=hospital.created_at,
        updated_at=hospital.updated_at,
    )
