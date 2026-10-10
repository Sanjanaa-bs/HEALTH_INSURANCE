import csv
import logging
import sys
from pathlib import Path

# Ensure project root is in sys.path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from typing import Dict, Any, Optional, Tuple
from sqlalchemy.orm import Session

from backend.app.database import SessionLocal, init_db
from backend.app.models.hospital import Hospital

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger("ingest_hospitals")


def clean_val(val: Optional[str]) -> Optional[str]:
    """Clean string values, converting '0' placeholders and whitespace to None."""
    if val is None:
        return None
    s = str(val).strip()
    if not s or s == "0" or s.lower() == "null" or s.lower() == "none":
        return None
    return s


def parse_beds(val: Optional[str]) -> Optional[int]:
    """Parse bed count safely."""
    cleaned = clean_val(val)
    if not cleaned:
        return None
    try:
        # Some counts might have comma formatting or decimals
        clean_num = cleaned.replace(",", "").split(".")[0]
        n = int(clean_num)
        return n if n > 0 else None
    except (ValueError, TypeError):
        return None


def parse_coordinates(coord_str: Optional[str]) -> Tuple[Optional[float], Optional[float]]:
    """Parse comma-separated 'latitude, longitude' coordinates safely."""
    cleaned = clean_val(coord_str)
    if not cleaned or "," not in cleaned:
        return None, None
    try:
        parts = cleaned.split(",")
        lat = float(parts[0].strip())
        lon = float(parts[1].strip())
        # Basic sanity bounds check
        if -90.0 <= lat <= 90.0 and -180.0 <= lon <= 180.0:
            return lat, lon
    except (ValueError, IndexError, TypeError):
        pass
    return None, None


def ingest_hospital_csv(
    csv_path: str = "data/hospitals/hospital_directory.csv",
    db: Optional[Session] = None,
    batch_size: int = 2000,
) -> Dict[str, Any]:
    """
    Ingest government hospital directory CSV into the hospitals table idempotently.
    Returns metrics dictionary with source_rows, imported_records, skipped_rows, errors.
    """
    file_path = Path(csv_path)
    if not file_path.exists():
        raise FileNotFoundError(f"Source file not found at {csv_path}")

    should_close_db = False
    if db is None:
        init_db()
        db = SessionLocal()
        should_close_db = True

    metrics = {
        "file": str(file_path),
        "source_rows": 0,
        "imported_records": 0,
        "skipped_rows": 0,
        "errors": 0,
    }

    # Fetch existing hospital keys to guarantee idempotency on re-runs
    # Key: (hospital_name.lower(), state.lower() if state else '', pincode or '')
    logger.info("Loading existing hospital directory signatures for duplicate checking...")
    existing_records = db.query(Hospital.hospital_name, Hospital.state, Hospital.pincode).all()
    existing_keys = {
        (
            h.hospital_name.strip().lower(),
            (h.state or "").strip().lower(),
            (h.pincode or "").strip(),
        )
        for h in existing_records
    }
    logger.info(f"Found {len(existing_keys)} existing hospital records in database.")

    batch = []
    
    # Attempt reading with UTF-8, fallback to Latin-1
    encodings = ["utf-8-sig", "utf-8", "latin-1"]
    reader = None
    f = None

    for enc in encodings:
        try:
            f = open(file_path, "r", encoding=enc, errors="replace")
            # Verify CSV header
            reader = csv.DictReader(f)
            if reader.fieldnames and "Hospital_Name" in reader.fieldnames:
                logger.info(f"Successfully opened {file_path} using {enc} encoding.")
                break
            f.close()
        except Exception as e:
            if f:
                f.close()
            continue

    if reader is None:
        raise ValueError(f"Could not parse CSV headers in {csv_path} with supported encodings.")

    try:
        for row in reader:
            metrics["source_rows"] += 1
            name = clean_val(row.get("Hospital_Name"))
            if not name:
                metrics["skipped_rows"] += 1
                continue

            state = clean_val(row.get("State"))
            pincode = clean_val(row.get("Pincode"))

            key = (
                name.lower(),
                (state or "").lower(),
                pincode or "",
            )

            if key in existing_keys:
                metrics["skipped_rows"] += 1
                continue

            lat, lon = parse_coordinates(row.get("Location_Coordinates"))

            # Construct Address: combine first line and location if available
            addr_parts = [
                clean_val(row.get("Address_Original_First_Line")),
                clean_val(row.get("Location")),
            ]
            full_address = ", ".join(p for p in addr_parts if p) or None

            hospital = Hospital(
                sr_no=clean_val(row.get("Sr_No")),
                hospital_name=name,
                hospital_category=clean_val(row.get("Hospital_Category")),
                care_type=clean_val(row.get("Hospital_Care_Type")),
                discipline=clean_val(row.get("Discipline_Systems_of_Medicine")),
                address=full_address,
                state=state,
                district=clean_val(row.get("District")),
                subdistrict=clean_val(row.get("Subdistrict")),
                pincode=pincode,
                telephone=clean_val(row.get("Telephone")),
                mobile_number=clean_val(row.get("Mobile_Number")),
                emergency_num=clean_val(row.get("Emergency_Num")),
                ambulance_phone=clean_val(row.get("Ambulance_Phone_No")),
                bloodbank_phone=clean_val(row.get("Bloodbank_Phone_No")),
                email=clean_val(row.get("Hospital_Primary_Email_Id")),
                website=clean_val(row.get("Website")),
                specialties=clean_val(row.get("Specialties")),
                facilities=clean_val(row.get("Facilities")),
                total_beds=parse_beds(row.get("Total_Num_Beds")),
                latitude=lat,
                longitude=lon,
            )

            batch.append(hospital)
            existing_keys.add(key)

            if len(batch) >= batch_size:
                try:
                    db.bulk_save_objects(batch)
                    db.commit()
                    metrics["imported_records"] += len(batch)
                    logger.info(f"Committed batch: {metrics['imported_records']} records imported so far.")
                    batch.clear()
                except Exception as e:
                    db.rollback()
                    logger.error(f"Error committing batch: {e}")
                    metrics["errors"] += len(batch)
                    batch.clear()

        # Commit remaining batch
        if batch:
            try:
                db.bulk_save_objects(batch)
                db.commit()
                metrics["imported_records"] += len(batch)
                batch.clear()
            except Exception as e:
                db.rollback()
                logger.error(f"Error committing final batch: {e}")
                metrics["errors"] += len(batch)

    finally:
        if f:
            f.close()
        if should_close_db:
            db.close()

    logger.info(
        f"Completed Hospital CSV Ingestion: {metrics['source_rows']} rows read, "
        f"{metrics['imported_records']} imported, {metrics['skipped_rows']} skipped."
    )
    return metrics


if __name__ == "__main__":
    ingest_hospital_csv()
