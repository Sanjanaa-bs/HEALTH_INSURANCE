import math
from typing import Optional
from fastapi import APIRouter, Depends, Query, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy import or_, func

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


@router.get("/hospitals", response_model=HospitalListResponse)
def get_hospitals(
    page: int = Query(1, ge=1, description="Page number"),
    page_size: int = Query(20, ge=1, le=100, description="Items per page"),
    search: Optional[str] = Query(None, description="Search term for name or address"),
    state: Optional[str] = Query(None, description="Filter by state"),
    district: Optional[str] = Query(None, description="Filter by district"),
    pincode: Optional[str] = Query(None, description="Filter by pincode"),
    db: Session = Depends(get_db),
):
    """Retrieve paginated general hospital directory entries with optional filtering."""
    query = db.query(Hospital)

    if search:
        search_term = f"%{search.strip()}%"
        query = query.filter(
            or_(
                Hospital.hospital_name.ilike(search_term),
                Hospital.address.ilike(search_term),
                Hospital.district.ilike(search_term),
                Hospital.specialties.ilike(search_term),
            )
        )

    if state:
        query = query.filter(Hospital.state.ilike(f"%{state.strip()}%"))
    if district:
        query = query.filter(Hospital.district.ilike(f"%{district.strip()}%"))
    if pincode:
        query = query.filter(Hospital.pincode == pincode.strip())

    total_items = query.count()
    total_pages = math.ceil(total_items / page_size) if total_items > 0 else 0

    offset = (page - 1) * page_size
    items = query.order_by(Hospital.id.asc()).offset(offset).limit(page_size).all()

    # Map source type and network status
    result_items = []
    for h in items:
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
            network_status="Star Health Cashless" if (h.insurer_records and len(h.insurer_records) > 0) else None,
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
    city: Optional[str] = Query(None, description="Filter by city"),
    db: Session = Depends(get_db),
):
    """Retrieve paginated insurer-specific hospital network records (e.g. Star Health)."""
    query = db.query(InsurerHospitalRecord)

    if search:
        st = f"%{search.strip()}%"
        query = query.filter(
            or_(
                InsurerHospitalRecord.hospital_name.ilike(st),
                InsurerHospitalRecord.address.ilike(st),
                InsurerHospitalRecord.city.ilike(st),
                InsurerHospitalRecord.state.ilike(st),
                InsurerHospitalRecord.pincode.ilike(st),
            )
        )
    if city:
        query = query.filter(InsurerHospitalRecord.city.ilike(f"%{city.strip()}%"))

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
    """Fetch a single hospital by ID."""
    hospital = db.query(Hospital).filter(Hospital.id == hospital_id).first()
    if not hospital:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Hospital with ID {hospital_id} not found",
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
        network_status="Star Health Cashless" if (hospital.insurer_records and len(hospital.insurer_records) > 0) else None,
        created_at=hospital.created_at,
        updated_at=hospital.updated_at,
    )
