"""
Evaluate Hospital Network Status Logic: Real Sample (N=10) & Synthetic Stress Test

Evaluates hospital network verification logic across two distinct datasets:
1. REAL Star Health Network Benchmark:
   - Exactly 10 real Star Health records from Bengaluru in SQLite (6 linked, 4 unlinked).
   - Evaluated against national directory facilities in Bengaluru, Bagalkot, and distant states.
   - Explicit limitation: sample size is 10 records covering only Bengaluru.
2. SYNTHETIC Multi-City Stress Benchmark:
   - 125 synthetic records from data/synthetic/synthetic_hospital_stress_sample.json.
   - Strictly labeled as synthetic stress test (NOT real Star Health data).
   - Validates algorithm scaling and multi-city geographic isolation.

Saves results to data/evaluation/hospital_network_results.json.
"""

import hashlib
import json
import sqlite3
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, Any, List

# Ensure backend can be imported
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from backend.app.models.hospital import Hospital, InsurerHospitalRecord
from backend.app.api.v1.hospitals import (
    evaluate_hospital_network_details,
    STATUS_LISTED,
    STATUS_NOT_FOUND,
    STATUS_UNVERIFIED,
)

RANDOM_SEED = 42

def get_git_commit() -> str:
    try:
        return subprocess.check_output(["git", "rev-parse", "HEAD"]).decode().strip()
    except Exception:
        return "unknown"

def compute_file_sha256(path: Path) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as f:
        while chunk := f.read(65536):
            h.update(chunk)
    return h.hexdigest()

def build_hospital_obj(row) -> Hospital:
    return Hospital(
        id=row[0],
        sr_no=row[1],
        hospital_name=row[2],
        hospital_category=row[3],
        care_type=row[4],
        discipline=row[5],
        address=row[6],
        state=row[7],
        district=row[8],
        subdistrict=row[9],
        pincode=row[10],
        total_beds=row[11],
    )

def evaluate_cohort(hospital_rows: List[Any], insurer_records: List[InsurerHospitalRecord], total_records: int) -> Dict[str, int]:
    counts = {"total": 0, "LISTED": 0, "NOT_FOUND": 0, "UNVERIFIED": 0}
    for r in hospital_rows:
        h = build_hospital_obj(r)
        status_str, code, expl, scope = evaluate_hospital_network_details(h, insurer_records, total_records)
        counts["total"] += 1
        counts[code] = counts.get(code, 0) + 1
    return counts

def run_evaluation():
    conn = sqlite3.connect("health_insurance.db")
    c = conn.cursor()

    # -------------------------------------------------------------------------
    # PART 1: Real Star Health Network Evaluation (10 Real Records)
    # -------------------------------------------------------------------------
    c.execute("SELECT id, insurer_name, hospital_name, city, state, pincode, address, network_type, matched_hospital_id FROM insurer_hospital_records")
    real_db_rows = c.fetchall()
    real_insurer_records = [
        InsurerHospitalRecord(
            id=r[0],
            insurer_name=r[1],
            hospital_name=r[2],
            city=r[3],
            state=r[4],
            pincode=r[5],
            address=r[6],
            network_type=r[7],
            matched_hospital_id=r[8]
        )
        for r in real_db_rows
    ]
    real_total = len(real_insurer_records)
    linked_ids = [r.matched_hospital_id for r in real_insurer_records if r.matched_hospital_id]

    print("\n" + "=" * 90)
    print(f"PART 1: REAL STAR HEALTH NETWORK BENCHMARK (N={real_total} records in SQLite)")
    print("=" * 90)
    print(f"Verified Records: {real_total} (Linked to National Directory: {len(linked_ids)}, Unlinked: {real_total - len(linked_ids)})")
    print("Documented Geographic Scope: Bengaluru sample only")

    # Cohort 1: Linked facilities (N=6)
    c.execute(f"SELECT id, sr_no, hospital_name, hospital_category, care_type, discipline, address, state, district, subdistrict, pincode, total_beds FROM hospitals WHERE id IN ({','.join(str(i) for i in linked_ids)})")
    real_linked_rows = c.fetchall()
    cohort_real_linked = evaluate_cohort(real_linked_rows, real_insurer_records, real_total)

    # Cohort 2: Bagalkot facilities (N=20, includes Kerudi Hospital)
    c.execute("SELECT id, sr_no, hospital_name, hospital_category, care_type, discipline, address, state, district, subdistrict, pincode, total_beds FROM hospitals WHERE district = 'Bagalkot' LIMIT 20")
    bagalkot_rows = c.fetchall()
    cohort_bagalkot = evaluate_cohort(bagalkot_rows, real_insurer_records, real_total)

    # Cohort 3: Distant facilities (N=50, Andaman, Assam, Bihar)
    c.execute("SELECT id, sr_no, hospital_name, hospital_category, care_type, discipline, address, state, district, subdistrict, pincode, total_beds FROM hospitals WHERE state IN ('Andaman and Nicobar Islands', 'Assam', 'Bihar') LIMIT 50")
    distant_rows = c.fetchall()
    cohort_distant = evaluate_cohort(distant_rows, real_insurer_records, real_total)

    # Cohort 4: Bengaluru facilities not in the sample (N=50)
    c.execute(f"SELECT id, sr_no, hospital_name, hospital_category, care_type, discipline, address, state, district, subdistrict, pincode, total_beds FROM hospitals WHERE district LIKE '%Bengaluru%' AND id NOT IN ({','.join(str(i) for i in linked_ids)}) LIMIT 50")
    bengaluru_unlisted_rows = c.fetchall()
    cohort_bengaluru_unlisted = evaluate_cohort(bengaluru_unlisted_rows, real_insurer_records, real_total)

    real_results = {
        "dataset_type": "real_production_database",
        "records_count": real_total,
        "linked_records_count": len(linked_ids),
        "unlinked_records_count": real_total - len(linked_ids),
        "dataset_limitation": "The production database contains only 10 real Star Health records covering Bengaluru. Generalization to other cities requires further insurer dataset ingestion.",
        "cohorts": {
            "real_linked_facilities": cohort_real_linked,
            "bagalkot_facilities_outside_bengaluru": cohort_bagalkot,
            "distant_state_facilities": cohort_distant,
            "bengaluru_unlisted_facilities": cohort_bengaluru_unlisted,
        },
        "metrics": {
            "linked_recall": cohort_real_linked["LISTED"] / cohort_real_linked["total"] if cohort_real_linked["total"] > 0 else 0.0,
            "bagalkot_unverified_rate": cohort_bagalkot["UNVERIFIED"] / cohort_bagalkot["total"] if cohort_bagalkot["total"] > 0 else 0.0,
            "distant_unverified_rate": cohort_distant["UNVERIFIED"] / cohort_distant["total"] if cohort_distant["total"] > 0 else 0.0,
            "false_positive_listed_rate": (cohort_bagalkot["LISTED"] + cohort_distant["LISTED"]) / (cohort_bagalkot["total"] + cohort_distant["total"]) if (cohort_bagalkot["total"] + cohort_distant["total"]) > 0 else 0.0,
        }
    }

    print(f"Linked Facility Recall:               {real_results['metrics']['linked_recall']*100:.1f}% ({cohort_real_linked['LISTED']}/{cohort_real_linked['total']})")
    print(f"Bagalkot Outside-Scope Isolation:     {real_results['metrics']['bagalkot_unverified_rate']*100:.1f}% ({cohort_bagalkot['UNVERIFIED']}/{cohort_bagalkot['total']} UNVERIFIED)")
    print(f"Distant States Outside-Scope Rate:    {real_results['metrics']['distant_unverified_rate']*100:.1f}% ({cohort_distant['UNVERIFIED']}/{cohort_distant['total']} UNVERIFIED)")
    print(f"False Positive Listed Rate:           {real_results['metrics']['false_positive_listed_rate']*100:.1f}%")

    # -------------------------------------------------------------------------
    # PART 2: Synthetic Multi-City Stress Benchmark (125 Synthetic Records)
    # -------------------------------------------------------------------------
    synthetic_path = Path("data/synthetic/synthetic_hospital_stress_sample.json")
    synthetic_hash = compute_file_sha256(synthetic_path)
    with open(synthetic_path, "r", encoding="utf-8") as f:
        synthetic_raw = json.load(f)

    synthetic_records = [
        InsurerHospitalRecord(
            id=r["id"],
            insurer_name=r["insurer_name"],
            hospital_name=r["hospital_name"],
            city=r["city"],
            state=r["state"],
            pincode=r["pincode"],
            address=r["address"],
            network_type=r["network_type"],
            matched_hospital_id=r.get("matched_hospital_id"),
        )
        for r in synthetic_raw
    ]
    synth_total = len(synthetic_records)
    synth_target_ids = [r["target_hospital_id"] for r in synthetic_raw if r.get("target_hospital_id")]

    # Synthetic Cohort A: 100 Target facilities
    c.execute(f"SELECT id, sr_no, hospital_name, hospital_category, care_type, discipline, address, state, district, subdistrict, pincode, total_beds FROM hospitals WHERE id IN ({','.join(str(i) for i in synth_target_ids)})")
    synth_target_rows = c.fetchall()
    cohort_synth_targets = evaluate_cohort(synth_target_rows, synthetic_records, synth_total)

    # Synthetic Cohort B: 50 Unlisted in active states
    synth_cities = list(set(r.city for r in synthetic_records))
    placeholders = ",".join("?" for _ in synth_cities)
    c.execute(f"SELECT id, sr_no, hospital_name, hospital_category, care_type, discipline, address, state, district, subdistrict, pincode, total_beds FROM hospitals WHERE id NOT IN ({','.join(str(i) for i in synth_target_ids)}) AND (district IN ({placeholders}) OR state IN ('Karnataka', 'Maharashtra', 'Tamil Nadu')) LIMIT 50", synth_cities)
    synth_unlisted_rows = c.fetchall()
    cohort_synth_unlisted = evaluate_cohort(synth_unlisted_rows, synthetic_records, synth_total)

    # Synthetic Cohort C: 50 Out of scope facilities (distant states)
    c.execute("SELECT id, sr_no, hospital_name, hospital_category, care_type, discipline, address, state, district, subdistrict, pincode, total_beds FROM hospitals WHERE state IN ('Andaman and Nicobar Islands', 'Assam', 'Bihar', 'Tripura') LIMIT 50")
    synth_oos_rows = c.fetchall()
    cohort_synth_oos = evaluate_cohort(synth_oos_rows, synthetic_records, synth_total)

    conn.close()

    synth_results = {
        "dataset_type": "synthetic_stress_sample",
        "label": "SYNTHETIC STRESS TEST (NOT real Star Health data)",
        "synthetic_file": str(synthetic_path),
        "synthetic_sha256": synthetic_hash,
        "records_count": synth_total,
        "cities_covered": len(synth_cities),
        "cohorts": {
            "synthetic_in_sample_targets": cohort_synth_targets,
            "synthetic_in_scope_unlisted": cohort_synth_unlisted,
            "synthetic_out_of_scope_facilities": cohort_synth_oos,
        },
        "metrics": {
            "target_facility_recall": cohort_synth_targets["LISTED"] / cohort_synth_targets["total"] if cohort_synth_targets["total"] > 0 else 0.0,
            "in_scope_absence_detection": cohort_synth_unlisted["NOT_FOUND"] / cohort_synth_unlisted["total"] if cohort_synth_unlisted["total"] > 0 else 0.0,
            "out_of_scope_isolation_rate": cohort_synth_oos["UNVERIFIED"] / cohort_synth_oos["total"] if cohort_synth_oos["total"] > 0 else 0.0,
        }
    }

    print("\n" + "=" * 90)
    print(f"PART 2: SYNTHETIC MULTI-CITY STRESS BENCHMARK (N={synth_total} synthetic records)")
    print("=" * 90)
    print(f"Target Facility Recall:               {synth_results['metrics']['target_facility_recall']*100:.1f}% ({cohort_synth_targets['LISTED']}/{cohort_synth_targets['total']})")
    print(f"In-Scope Absence Detection:           {synth_results['metrics']['in_scope_absence_detection']*100:.1f}% ({cohort_synth_unlisted['NOT_FOUND']}/{cohort_synth_unlisted['total']})")
    print(f"Out-of-Scope Isolation Rate:          {synth_results['metrics']['out_of_scope_isolation_rate']*100:.1f}% ({cohort_synth_oos['UNVERIFIED']}/{cohort_synth_oos['total']})")
    print("=" * 90)

    output_data = {
        "metadata": {
            "command": "python scripts/evaluate_hospital_network.py",
            "git_commit": get_git_commit(),
            "date": datetime.now(timezone.utc).isoformat(),
            "random_seed": RANDOM_SEED,
            "national_directory_size": 29974,
        },
        "real_network_evaluation": real_results,
        "synthetic_stress_evaluation": synth_results,
    }

    out_file = Path("data/evaluation/hospital_network_results.json")
    with open(out_file, "w", encoding="utf-8") as f:
        json.dump(output_data, f, indent=2)
    print(f"\nSaved hospital network evaluation to {out_file}\n")

if __name__ == "__main__":
    run_evaluation()
