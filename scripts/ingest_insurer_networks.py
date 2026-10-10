import email
import json
import logging
import re
import sys
from email import policy
from pathlib import Path

# Ensure project root is in sys.path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from typing import Dict, Any, List, Optional
from bs4 import BeautifulSoup
from sqlalchemy.orm import Session

from backend.app.database import SessionLocal, init_db
from backend.app.models.hospital import Hospital, InsurerHospitalRecord

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger("ingest_insurer_networks")


def extract_cards_from_html(html_content: str, source_file: str, source_url: str) -> List[Dict[str, Any]]:
    """Parse HTML and extract verified Star Health hospital cards."""
    soup = BeautifulSoup(html_content, "html.parser")
    # Each card has class list containing 'border', 'rounded-md', 'p-4'
    card_divs = [
        d for d in soup.find_all("div")
        if set(["border", "rounded-md", "p-4"]).issubset(set(d.get("class", [])))
    ]

    extracted = []
    for card in card_divs:
        # Title
        title_el = card.find("div", class_=lambda cl: cl and "font-semibold" in cl)
        if not title_el:
            continue
        hospital_name = title_el.get_text().strip()
        if not hospital_name or len(hospital_name) < 3:
            continue

        raw_strings = [s.strip() for s in card.stripped_strings]

        # Extract pincode using 6 digit regex
        pincode = None
        for s in raw_strings:
            m = re.search(r"\b(560\d{3})\b", s)
            if m:
                pincode = m.group(1)
                break

        # Extract address line (usually the longest address string with road/cross/layout)
        address = None
        for s in raw_strings:
            if any(kw in s.lower() for kw in ["road", "cross", "main", "layout", "street", "nagar", "opposite", "opp.", "no.", "#"]):
                address = s
                break

        # Extract phone (e.g. 080 - 26581819)
        phone = None
        phone_matches = re.findall(r"\b\d{3,5}\s*-\s*\d{6,8}\b", " ".join(raw_strings))
        if phone_matches:
            phone = phone_matches[0].replace(" ", "")
        elif "080" in raw_strings:
            idx = raw_strings.index("080")
            if idx + 2 < len(raw_strings) and raw_strings[idx + 1] == "-":
                phone = f"080-{raw_strings[idx + 2]}"

        # Category / Network type
        network_type = "Cashless Network" if "Network Hospital" in raw_strings else "Cashless"

        extracted.append({
            "insurer_name": "Star Health",
            "hospital_name": hospital_name,
            "city": "Bengaluru",
            "state": "Karnataka",
            "pincode": pincode or "560001",
            "address": address or ", ".join([s for s in raw_strings[1:5] if s not in ["Directions", "Network Hospital", ","]]),
            "network_type": network_type,
            "source_file": source_file,
            "source_url": source_url,
            "raw_details": json.dumps({"phone": phone, "source_url": source_url, "source_file": source_file}),
        })

    return extracted


def ingest_insurer_networks(
    dir_path: str = "data/insurer_networks",
    db: Optional[Session] = None,
) -> Dict[str, Any]:
    """
    Ingest Star Health network hospitals from saved HTML and MHTML web archives.
    Avoids duplicates across files and links matched general directory hospital IDs where applicable.
    """
    network_dir = Path(dir_path)
    if not network_dir.exists():
        raise FileNotFoundError(f"Directory {dir_path} not found")

    should_close_db = False
    if db is None:
        init_db()
        db = SessionLocal()
        should_close_db = True

    metrics = {
        "files_scanned": 0,
        "extracted_cards": 0,
        "imported_records": 0,
        "skipped_duplicates": 0,
        "matched_directory_hospitals": 0,
    }

    # Track imported keys to prevent duplicates across files: (hospital_name.lower(), pincode)
    existing_in_db = db.query(InsurerHospitalRecord.hospital_name, InsurerHospitalRecord.pincode).all()
    seen_keys = {
        (rec.hospital_name.strip().lower(), (rec.pincode or "").strip())
        for rec in existing_in_db
    }

    # Discover files
    files = list(network_dir.glob("*.htm")) + list(network_dir.glob("*.html")) + list(network_dir.glob("*.mhtml"))

    for file_path in files:
        metrics["files_scanned"] += 1
        logger.info(f"Processing insurer network file: {file_path.name}")
        html_content = ""
        source_url = "https://www.starhealth.in/network-hospitals/star-health-network-hospitals-list-in-bangalore-karnataka/"

        if file_path.suffix.lower() == ".mhtml":
            with open(file_path, "rb") as f:
                msg = email.message_from_binary_file(f, policy=policy.default)
                source_url = msg.get("Snapshot-Content-Location") or source_url
                body = msg.get_body(preferencelist=("html", "plain"))
                if body:
                    html_content = body.get_content()
        else:
            with open(file_path, "r", encoding="utf-8", errors="replace") as f:
                html_content = f.read()

        if not html_content:
            logger.warning(f"No HTML content extractable from {file_path.name}")
            continue

        cards = extract_cards_from_html(html_content, file_path.name, source_url)
        metrics["extracted_cards"] += len(cards)

        for card in cards:
            dedup_key = (card["hospital_name"].strip().lower(), card["pincode"].strip())
            if dedup_key in seen_keys:
                metrics["skipped_duplicates"] += 1
                continue

            # Attempt match in general directory
            matched_hospital = (
                db.query(Hospital)
                .filter(
                    Hospital.state.ilike("%Karnataka%"),
                    Hospital.hospital_name.ilike(f"%{card['hospital_name'].split()[0]}%"),
                )
                .first()
            )
            matched_id = matched_hospital.id if matched_hospital else None
            if matched_id:
                metrics["matched_directory_hospitals"] += 1

            record = InsurerHospitalRecord(
                insurer_name=card["insurer_name"],
                hospital_name=card["hospital_name"],
                city=card["city"],
                state=card["state"],
                pincode=card["pincode"],
                address=card["address"],
                network_type=card["network_type"],
                raw_details=card["raw_details"],
                matched_hospital_id=matched_id,
            )

            db.add(record)
            seen_keys.add(dedup_key)
            metrics["imported_records"] += 1

    db.commit()
    if should_close_db:
        db.close()

    logger.info(
        f"Completed Insurer Network Ingestion: {metrics['files_scanned']} files scanned, "
        f"{metrics['extracted_cards']} cards found, {metrics['imported_records']} imported, "
        f"{metrics['skipped_duplicates']} skipped duplicates, {metrics['matched_directory_hospitals']} linked to directory."
    )
    return metrics


if __name__ == "__main__":
    ingest_insurer_networks()
