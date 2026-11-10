import json
import sys
import sqlite3
from pathlib import Path
from typing import List, Dict, Any

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from backend.app.models.hospital import Hospital, InsurerHospitalRecord
from backend.app.api.v1.hospitals import (
    evaluate_hospital_network_details,
    is_hospital_within_insurer_scope,
    STATUS_LISTED,
    STATUS_NOT_FOUND,
    STATUS_UNVERIFIED,
)

# Load expanded 125-record multi-city dataset
expanded_net_path = Path("data/insurer_networks/expanded_insurer_network_sample.json")
with open(expanded_net_path, "r", encoding="utf-8") as f:
    raw_insurer_data = json.load(f)

# Convert into InsurerHospitalRecord mock instances for evaluate_hospital_network_details
insurer_records = []
for r in raw_insurer_data:
    rec = InsurerHospitalRecord(
        id=r["id"],
        insurer_name=r["insurer_name"],
        hospital_name=r["hospital_name"],
        city=r["city"],
        state=r["state"],
        pincode=r["pincode"],
        address=r["address"],
        network_type=r["network_type"],
        matched_hospital_id=r.get("matched_hospital_id")
    )
    insurer_records.append(rec)

total_insurer_records = len(insurer_records)
print(f"Loaded {total_insurer_records} multi-city insurer network records across {len(set(r.city for r in insurer_records))} cities.")

conn = sqlite3.connect("health_insurance.db")
c = conn.cursor()

# Cohort A: 100 Target facilities from the national directory corresponding to the active insurer sample
target_ids = [r["target_hospital_id"] for r in raw_insurer_data if r.get("target_hospital_id")]
c.execute(
    f"""
    SELECT id, sr_no, hospital_name, hospital_category, care_type, discipline, address, state, district, subdistrict, pincode, total_beds
    FROM hospitals
    WHERE id IN ({','.join(str(i) for i in target_ids)})
    """
)
in_sample_rows = c.fetchall()

# Cohort B: 50 Unlisted facilities in the same active cities (e.g. Bengaluru, Mumbai, Chennai)
active_cities = list(set(r.city for r in insurer_records))
placeholders = ",".join("?" for _ in active_cities)
c.execute(
    f"""
    SELECT id, sr_no, hospital_name, hospital_category, care_type, discipline, address, state, district, subdistrict, pincode, total_beds
    FROM hospitals
    WHERE id NOT IN ({','.join(str(i) for i in target_ids)})
      AND (district IN ({placeholders}) OR state IN ('Karnataka', 'Maharashtra', 'Tamil Nadu'))
    LIMIT 50
    """,
    active_cities
)
unlisted_rows = c.fetchall()

# Cohort C: 50 Facilities outside the documented geographic scope (e.g. Andaman, Bihar, Assam, Jammu, Bagalkot)
c.execute(
    """
    SELECT id, sr_no, hospital_name, hospital_category, care_type, discipline, address, state, district, subdistrict, pincode, total_beds
    FROM hospitals
    WHERE state IN ('Andaman and Nicobar Islands', 'Assam', 'Bihar', 'Jammu and Kashmir', 'Tripura')
       OR district = 'Bagalkot'
    LIMIT 50
    """
)
out_of_scope_rows = c.fetchall()
conn.close()

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
        total_beds=row[11]
    )

# Evaluation metrics
cohort_results = {
    "in_sample_matched": {"total": 0, "LISTED": 0, "NOT_FOUND": 0, "UNVERIFIED": 0},
    "in_scope_unlisted": {"total": 0, "LISTED": 0, "NOT_FOUND": 0, "UNVERIFIED": 0},
    "out_of_scope_facilities": {"total": 0, "LISTED": 0, "NOT_FOUND": 0, "UNVERIFIED": 0},
}

# 1. In-sample matched cohort evaluation
for r in in_sample_rows:
    h = build_hospital_obj(r)
    status_str, code, expl, scope = evaluate_hospital_network_details(h, insurer_records, total_insurer_records)
    cohort_results["in_sample_matched"]["total"] += 1
    cohort_results["in_sample_matched"][code] += 1

# 2. In-scope unlisted cohort evaluation
for r in unlisted_rows:
    h = build_hospital_obj(r)
    status_str, code, expl, scope = evaluate_hospital_network_details(h, insurer_records, total_insurer_records)
    cohort_results["in_scope_unlisted"]["total"] += 1
    cohort_results["in_scope_unlisted"][code] += 1

# 3. Out-of-scope cohort evaluation
for r in out_of_scope_rows:
    h = build_hospital_obj(r)
    status_str, code, expl, scope = evaluate_hospital_network_details(h, insurer_records, total_insurer_records)
    cohort_results["out_of_scope_facilities"]["total"] += 1
    cohort_results["out_of_scope_facilities"][code] += 1

# Key performance indicators
matched_t = cohort_results["in_sample_matched"]["total"]
matched_acc = cohort_results["in_sample_matched"]["LISTED"] / matched_t if matched_t > 0 else 0

unlisted_t = cohort_results["in_scope_unlisted"]["total"]
unlisted_notfound_rate = cohort_results["in_scope_unlisted"]["NOT_FOUND"] / unlisted_t if unlisted_t > 0 else 0

oos_t = cohort_results["out_of_scope_facilities"]["total"]
oos_unverified_rate = cohort_results["out_of_scope_facilities"]["UNVERIFIED"] / oos_t if oos_t > 0 else 0

# Overall network separation precision
# Precision of LISTED: Of all hospitals declared LISTED, what percentage are truly in the network?
total_declared_listed = (
    cohort_results["in_sample_matched"]["LISTED"] +
    cohort_results["in_scope_unlisted"]["LISTED"] +
    cohort_results["out_of_scope_facilities"]["LISTED"]
)
true_listed = cohort_results["in_sample_matched"]["LISTED"]
network_separation_precision = true_listed / total_declared_listed if total_declared_listed > 0 else 1.0

summary_payload = {
    "dataset_overview": {
        "total_insurer_records_evaluated": total_insurer_records,
        "cities_covered": len(active_cities),
        "city_list": active_cities,
        "national_directory_size": 29974,
    },
    "cohort_performance": cohort_results,
    "metrics": {
        "matched_accuracy_pct": round(matched_acc * 100, 2),
        "in_scope_not_found_rate_pct": round(unlisted_notfound_rate * 100, 2),
        "out_of_scope_unverified_rate_pct": round(oos_unverified_rate * 100, 2),
        "network_separation_precision_pct": round(network_separation_precision * 100, 2),
        "false_positive_network_rate_pct": round((1.0 - network_separation_precision) * 100, 2),
    }
}

out_path = Path("data/evaluation/hospital_network_results.json")
with open(out_path, "w", encoding="utf-8") as f:
    json.dump(summary_payload, f, indent=2)

print("\n" + "="*85)
print(f"EXPANDED HOSPITAL NETWORK VERIFICATION BENCHMARK ({total_insurer_records} Records across 9 Cities)")
print("="*85)
print(f"Network Separation Precision:  {network_separation_precision*100:.2f}% (False Positive Rate: {(1-network_separation_precision)*100:.2f}%)")
print(f"Matched Facility Recall:       {matched_acc*100:.2f}% ({cohort_results['in_sample_matched']['LISTED']}/{matched_t})")
print(f"In-Scope Absence Detection:    {unlisted_notfound_rate*100:.2f}% ({cohort_results['in_scope_unlisted']['NOT_FOUND']}/{unlisted_t})")
print(f"Out-of-Scope Isolation Rate:   {oos_unverified_rate*100:.2f}% ({cohort_results['out_of_scope_facilities']['UNVERIFIED']}/{oos_t})")
print("-"*85)
print(f"{'EVALUATION COHORT':<30} | {'TOTAL':<8} | {'LISTED':<8} | {'NOT_FOUND':<10} | {'UNVERIFIED':<10}")
print("-"*85)
for cohort_name, data in cohort_results.items():
    print(f"{cohort_name:<30} | {data['total']:<8} | {data['LISTED']:<8} | {data['NOT_FOUND']:<10} | {data['UNVERIFIED']:<10}")
print("="*85)
print(f"Detailed network evaluation saved to {out_path.resolve()}\n")

