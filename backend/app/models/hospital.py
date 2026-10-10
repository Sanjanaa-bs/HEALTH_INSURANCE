from sqlalchemy import Column, Integer, String, Text, Float, DateTime, ForeignKey, func
from sqlalchemy.orm import relationship
from backend.app.database import Base


class Hospital(Base):
    """General government hospital directory record."""

    __tablename__ = "hospitals"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    sr_no = Column(String(50), nullable=True)
    hospital_name = Column(String(255), nullable=False, index=True)
    hospital_category = Column(String(100), nullable=True)
    care_type = Column(String(100), nullable=True)
    discipline = Column(String(100), nullable=True)
    address = Column(Text, nullable=True)
    state = Column(String(100), nullable=True, index=True)
    district = Column(String(100), nullable=True, index=True)
    subdistrict = Column(String(100), nullable=True)
    pincode = Column(String(20), nullable=True, index=True)
    telephone = Column(String(100), nullable=True)
    mobile_number = Column(String(100), nullable=True)
    emergency_num = Column(String(100), nullable=True)
    ambulance_phone = Column(String(100), nullable=True)
    bloodbank_phone = Column(String(100), nullable=True)
    email = Column(String(255), nullable=True)
    website = Column(String(255), nullable=True)
    specialties = Column(Text, nullable=True)
    facilities = Column(Text, nullable=True)
    total_beds = Column(Integer, nullable=True)
    latitude = Column(Float, nullable=True)
    longitude = Column(Float, nullable=True)

    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)

    # Relationship to insurer specific records linked to this general directory hospital
    insurer_records = relationship(
        "InsurerHospitalRecord",
        back_populates="matched_hospital",
        cascade="all, delete-orphan",
    )


class InsurerHospitalRecord(Base):
    """Insurer-specific hospital network record (e.g., Star Health network hospitals)."""

    __tablename__ = "insurer_hospital_records"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    insurer_name = Column(String(100), default="Star Health", nullable=False, index=True)
    hospital_name = Column(String(255), nullable=False, index=True)
    city = Column(String(100), nullable=True, index=True)
    state = Column(String(100), nullable=True, index=True)
    pincode = Column(String(20), nullable=True, index=True)
    address = Column(Text, nullable=True)
    network_type = Column(String(50), default="Cashless", nullable=True)
    raw_details = Column(Text, nullable=True)

    matched_hospital_id = Column(
        Integer,
        ForeignKey("hospitals.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
    )

    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)

    # Relationship back to the general hospital directory record
    matched_hospital = relationship("Hospital", back_populates="insurer_records")
