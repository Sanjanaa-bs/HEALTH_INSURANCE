from typing import Optional, List
from datetime import datetime
from pydantic import BaseModel, ConfigDict
from backend.app.schemas.common import PaginationMeta


class InsurerHospitalRecordRead(BaseModel):
    """Schema for insurer-specific hospital record."""
    model_config = ConfigDict(from_attributes=True)

    id: int
    insurer_name: str
    hospital_name: str
    city: Optional[str] = None
    state: Optional[str] = None
    pincode: Optional[str] = None
    address: Optional[str] = None
    network_type: Optional[str] = None
    source_type: str = "Insurer Network (Star Health)"
    matched_hospital_id: Optional[int] = None
    created_at: datetime


class InsurerHospitalListResponse(BaseModel):
    """Paginated list of insurer network hospitals."""
    model_config = ConfigDict(from_attributes=True)

    items: List[InsurerHospitalRecordRead]
    pagination: PaginationMeta


class HospitalRead(BaseModel):
    """Schema for general hospital directory record."""
    model_config = ConfigDict(from_attributes=True)

    id: int
    sr_no: Optional[str] = None
    hospital_name: str
    hospital_category: Optional[str] = None
    care_type: Optional[str] = None
    discipline: Optional[str] = None
    address: Optional[str] = None
    state: Optional[str] = None
    district: Optional[str] = None
    subdistrict: Optional[str] = None
    pincode: Optional[str] = None
    telephone: Optional[str] = None
    mobile_number: Optional[str] = None
    emergency_num: Optional[str] = None
    ambulance_phone: Optional[str] = None
    bloodbank_phone: Optional[str] = None
    email: Optional[str] = None
    website: Optional[str] = None
    specialties: Optional[str] = None
    facilities: Optional[str] = None
    total_beds: Optional[int] = None
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    source_type: str = "Government Directory"
    network_status: Optional[str] = None
    created_at: datetime
    updated_at: datetime


class HospitalListResponse(BaseModel):
    """Paginated list of hospitals."""
    model_config = ConfigDict(from_attributes=True)

    items: List[HospitalRead]
    pagination: PaginationMeta
