"""
Evaluate Hospital Entity Matching & Location Verification (Dev/Test Split)

Evaluates the multi-stage hospital entity matching and geographic consistency logic:
1. Normalization (case, punctuation, legal corporate suffixes, noise tokens).
2. Location compatibility (state, district, city, and 6-digit pincode hierarchy).
3. Ablation: strict_location_check enabled vs disabled.

Non-negotiable scientific integrity rules:
- Benchmark pairs split into dev set (30 pairs) and held-out test set (45 pairs) using seed 42.
- Synthetic variations explicitly labeled as synthetic stress tests.
- Outputs full confusion matrix and metrics to data/evaluation/hospital_matcher_results.json.
"""

import hashlib
import json
import random
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, Any, List, Tuple

# Ensure backend can be imported
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from backend.app.api.v1.hospitals import (
    normalize_hospital_name,
    location_compatible,
    check_location_conflict,
)

RANDOM_SEED = 42

def get_git_commit() -> str:
    try:
        return subprocess.check_output(["git", "rev-parse", "HEAD"]).decode().strip()
    except Exception:
        return "unknown"

# 75 Benchmark pairs across 6 challenge categories (synthetic variations explicitly labeled)
ALL_PAIRS: List[Dict[str, Any]] = [
    # -------------------------------------------------------------------------
    # Category 1: Case, Whitespace, Punctuation & Ampersand Variations (15 pairs) [Synthetic variations]
    # Expected: Match (True)
    # -------------------------------------------------------------------------
    {"id": "P01", "name_a": "Apollo Hospitals - Bangalore", "name_b": "Apollo Hospital Bangalore", "expected": True, "cat": "formatting_variations", "synthetic": True},
    {"id": "P02", "name_a": "BANGALORE BAPTIST HOSPITAL", "name_b": "Bangalore Baptist Hospital", "expected": True, "cat": "formatting_variations", "synthetic": True},
    {"id": "P03", "name_a": "Kerudi Hospital & Research Centre", "name_b": "Kerudi Hospital And Research Centre", "expected": True, "cat": "formatting_variations", "synthetic": True},
    {"id": "P04", "name_a": "St. John's Medical College Hospital", "name_b": "St Johns Medical College Hospital", "expected": True, "cat": "formatting_variations", "synthetic": True},
    {"id": "P05", "name_a": "St. Martha's Hospital", "name_b": "St Marthas Hospital", "expected": True, "cat": "formatting_variations", "synthetic": True},
    {"id": "P06", "name_a": "St. Philomena's Hospital", "name_b": "St Philomenas Hospital", "expected": True, "cat": "formatting_variations", "synthetic": True},
    {"id": "P07", "name_a": "M. S. Ramaiah Memorial Hospital", "name_b": "MS Ramaiah Memorial Hospital", "expected": True, "cat": "formatting_variations", "synthetic": True},
    {"id": "P08", "name_a": "Fortis Hospital - Bannerghatta Road", "name_b": "Fortis Hospital Bannerghatta Road", "expected": True, "cat": "formatting_variations", "synthetic": True},
    {"id": "P09", "name_a": "Manipal Hospital - Old Airport Road", "name_b": "Manipal Hospital Old Airport Road", "expected": True, "cat": "formatting_variations", "synthetic": True},
    {"id": "P10", "name_a": "Sagar Hospitals - DSI", "name_b": "Sagar Hospital DSI", "expected": True, "cat": "formatting_variations", "synthetic": True},
    {"id": "P11", "name_a": "Columbia Asia Hospital - Hebbal", "name_b": "Columbia Asia Hospital Hebbal", "expected": True, "cat": "formatting_variations", "synthetic": True},
    {"id": "P12", "name_a": "Narayana Hrudayalaya - Institute of Cardiac Sciences", "name_b": "Narayana Hrudayalaya Institute of Cardiac Sciences", "expected": True, "cat": "formatting_variations", "synthetic": True},
    {"id": "P13", "name_a": "Dr. Agarwal's Eye Hospital", "name_b": "Dr Agarwals Eye Hospital", "expected": True, "cat": "formatting_variations", "synthetic": True},
    {"id": "P14", "name_a": "Nethradhama Super Speciality Eye Hospital", "name_b": "Nethradhama Super Speciality Eye Hospital", "expected": True, "cat": "formatting_variations", "synthetic": True},
    {"id": "P15", "name_a": "Sri Jayadeva Institute of Cardiovascular Sciences & Research", "name_b": "Sri Jayadeva Institute of Cardiovascular Sciences and Research", "expected": True, "cat": "formatting_variations", "synthetic": True},

    # -------------------------------------------------------------------------
    # Category 2: Legal & Corporate Suffixes (10 pairs) [Synthetic suffix attachments]
    # Expected: Match (True)
    # -------------------------------------------------------------------------
    {"id": "P16", "name_a": "Chaitanya Hospital Pvt Ltd", "name_b": "Chaitanya Hospital", "expected": True, "cat": "corporate_legal_suffixes", "synthetic": True},
    {"id": "P17", "name_a": "Madhusudana Health Care Services Pvt Ltd", "name_b": "Madhusudana Health Care Services", "expected": True, "cat": "corporate_legal_suffixes", "synthetic": True},
    {"id": "P18", "name_a": "Gleneagles Healthcare India Private Limited", "name_b": "Gleneagles Healthcare India", "expected": True, "cat": "corporate_legal_suffixes", "synthetic": True},
    {"id": "P19", "name_a": "Healthcare Global Enterprises Limited", "name_b": "Healthcare Global Enterprises", "expected": True, "cat": "corporate_legal_suffixes", "synthetic": True},
    {"id": "P20", "name_a": "Narayana Health Private Limited", "name_b": "Narayana Health", "expected": True, "cat": "corporate_legal_suffixes", "synthetic": True},
    {"id": "P21", "name_a": "Apollo Hospitals Enterprise Limited", "name_b": "Apollo Hospital Enterprise", "expected": True, "cat": "corporate_legal_suffixes", "synthetic": True},
    {"id": "P22", "name_a": "Aster DM Healthcare Ltd", "name_b": "Aster DM Healthcare", "expected": True, "cat": "corporate_legal_suffixes", "synthetic": True},
    {"id": "P23", "name_a": "Max Healthcare Institute Limited", "name_b": "Max Healthcare Institute", "expected": True, "cat": "corporate_legal_suffixes", "synthetic": True},
    {"id": "P24", "name_a": "Fortis Healthcare Private Limited", "name_b": "Fortis Healthcare", "expected": True, "cat": "corporate_legal_suffixes", "synthetic": True},
    {"id": "P25", "name_a": "Medanta The Medicity Global Health Limited", "name_b": "Medanta The Medicity Global Health", "expected": True, "cat": "corporate_legal_suffixes", "synthetic": True},

    # -------------------------------------------------------------------------
    # Category 3: Medical Acronyms & Abbreviations (15 pairs) [Curated & observed]
    # -------------------------------------------------------------------------
    {"id": "P26", "name_a": "HCG Cancer Hospital", "name_b": "HCG Cancer Centre", "expected": False, "cat": "medical_acronyms_and_specialties", "synthetic": False},
    {"id": "P27", "name_a": "BGS Gleneagles Global Hospital", "name_b": "BGS Gleneagles Global Hospital", "expected": True, "cat": "medical_acronyms_and_specialties", "synthetic": False},
    {"id": "P28", "name_a": "SDM College of Medical Sciences & Hospital", "name_b": "SDM College of Medical Sciences and Hospital", "expected": True, "cat": "medical_acronyms_and_specialties", "synthetic": True},
    {"id": "P29", "name_a": "CSI Holdsworth Memorial Hospital", "name_b": "CSI Holdsworth Memorial Hospital", "expected": True, "cat": "medical_acronyms_and_specialties", "synthetic": False},
    {"id": "P30", "name_a": "ESI Hospital Rajajinagar", "name_b": "ESI Hospital Rajajinagar", "expected": True, "cat": "medical_acronyms_and_specialties", "synthetic": False},
    {"id": "P31", "name_a": "KLES Dr. Prabhakar Kore Hospital", "name_b": "KLES Dr Prabhakar Kore Hospital", "expected": True, "cat": "medical_acronyms_and_specialties", "synthetic": True},
    {"id": "P32", "name_a": "JSS Hospital Mysore", "name_b": "JSS Hospital Mysore", "expected": True, "cat": "medical_acronyms_and_specialties", "synthetic": False},
    {"id": "P33", "name_a": "KIMS Hospital and Research Centre", "name_b": "KIMS Hospital And Research Centre", "expected": True, "cat": "medical_acronyms_and_specialties", "synthetic": True},
    {"id": "P34", "name_a": "AJ Hospital & Research Centre Mangalore", "name_b": "AJ Hospital and Research Centre Mangalore", "expected": True, "cat": "medical_acronyms_and_specialties", "synthetic": True},
    {"id": "P35", "name_a": "Yenepoya Specialty Hospital", "name_b": "Yenepoya Specialty Hospital", "expected": True, "cat": "medical_acronyms_and_specialties", "synthetic": False},
    {"id": "P36", "name_a": "Father Muller Medical College Hospital", "name_b": "Father Muller Medical College Hospital", "expected": True, "cat": "medical_acronyms_and_specialties", "synthetic": False},
    {"id": "P37", "name_a": "KVG Medical College Hospital Sullia", "name_b": "KVG Medical College Hospital Sullia", "expected": True, "cat": "medical_acronyms_and_specialties", "synthetic": False},
    {"id": "P38", "name_a": "Father Muller Homoeopathic Medical College & Hospital", "name_b": "Father Muller Homoeopathic Medical College and Hospital", "expected": True, "cat": "medical_acronyms_and_specialties", "synthetic": True},
    {"id": "P39", "name_a": "Kasturba Hospital Manipal", "name_b": "Kasturba Hospital Manipal", "expected": True, "cat": "medical_acronyms_and_specialties", "synthetic": False},
    {"id": "P40", "name_a": "TMC Hospital", "name_b": "Tata Memorial Centre Hospital", "expected": False, "cat": "medical_acronyms_and_specialties", "synthetic": False},

    # -------------------------------------------------------------------------
    # Category 4: Distinct Facilities with Shared Prefixes / False Friends (15 pairs) [Adversarial negatives]
    # Expected: No Match (False)
    # -------------------------------------------------------------------------
    {"id": "P41", "name_a": "Aditi Eye Care", "name_b": "Aditi Nursing Home", "expected": False, "cat": "shared_brand_distinct_facilities", "synthetic": False},
    {"id": "P42", "name_a": "Manipal Hospital Whitefield", "name_b": "Manipal Hospital Old Airport Road", "expected": False, "cat": "shared_brand_distinct_facilities", "synthetic": False},
    {"id": "P43", "name_a": "Manipal Northside Hospital", "name_b": "Manipal Hospital", "expected": False, "cat": "shared_brand_distinct_facilities", "synthetic": False},
    {"id": "P44", "name_a": "Apollo Clinic", "name_b": "Apollo Hospitals", "expected": False, "cat": "shared_brand_distinct_facilities", "synthetic": False},
    {"id": "P45", "name_a": "Apollo Cradle", "name_b": "Apollo Hospitals", "expected": False, "cat": "shared_brand_distinct_facilities", "synthetic": False},
    {"id": "P46", "name_a": "Fortis La Femme", "name_b": "Fortis Hospital", "expected": False, "cat": "shared_brand_distinct_facilities", "synthetic": False},
    {"id": "P47", "name_a": "Fortis Hospital Cunningham Road", "name_b": "Fortis Hospital Nagarbhavi", "expected": False, "cat": "shared_brand_distinct_facilities", "synthetic": False},
    {"id": "P48", "name_a": "Sagar Hospital Jayanagar", "name_b": "Sagar Hospital Banashankari", "expected": False, "cat": "shared_brand_distinct_facilities", "synthetic": False},
    {"id": "P49", "name_a": "Narayana Multispeciality Hospital", "name_b": "Narayana Hrudayalaya", "expected": False, "cat": "shared_brand_distinct_facilities", "synthetic": False},
    {"id": "P50", "name_a": "Cloudnine Hospital Malleshwaram", "name_b": "Cloudnine Hospital Jayanagar", "expected": False, "cat": "shared_brand_distinct_facilities", "synthetic": False},
    {"id": "P51", "name_a": "Motherhood Hospital Indiranagar", "name_b": "Motherhood Hospital Sarjapur", "expected": False, "cat": "shared_brand_distinct_facilities", "synthetic": False},
    {"id": "P52", "name_a": "Aster CMI Hospital", "name_b": "Aster RV Hospital", "expected": False, "cat": "shared_brand_distinct_facilities", "synthetic": False},
    {"id": "P53", "name_a": "Sparsh Hospital Yeshwanthpur", "name_b": "Sparsh Hospital Infantry Road", "expected": False, "cat": "shared_brand_distinct_facilities", "synthetic": False},
    {"id": "P54", "name_a": "Vikram Hospital", "name_b": "Manipal Hospital Millers Road", "expected": False, "cat": "shared_brand_distinct_facilities", "synthetic": False},
    {"id": "P55", "name_a": "Bowring and Lady Curzon Hospital", "name_b": "Victoria Hospital", "expected": False, "cat": "shared_brand_distinct_facilities", "synthetic": False},

    # -------------------------------------------------------------------------
    # Category 5: Renamed Facilities & Corporate Rebranding (10 pairs)
    # Expected: No Match (False) unless explicitly linked in historical registry
    # -------------------------------------------------------------------------
    {"id": "P56", "name_a": "Gleneagles BGS Hospital", "name_b": "BGS Global Hospital", "expected": False, "cat": "corporate_rebranding", "synthetic": False},
    {"id": "P57", "name_a": "Manipal Hospital Yeshwanthpur", "name_b": "Columbia Asia Referral Hospital Yeshwanthpur", "expected": False, "cat": "corporate_rebranding", "synthetic": False},
    {"id": "P58", "name_a": "Manipal Hospital Whitefield", "name_b": "Columbia Asia Hospital Whitefield", "expected": False, "cat": "corporate_rebranding", "synthetic": False},
    {"id": "P59", "name_a": "Manipal Hospital Hebbal", "name_b": "Columbia Asia Hospital Hebbal", "expected": False, "cat": "corporate_rebranding", "synthetic": False},
    {"id": "P60", "name_a": "Manipal Hospital Millers Road", "name_b": "Vikram Hospital", "expected": False, "cat": "corporate_rebranding", "synthetic": False},
    {"id": "P61", "name_a": "Aster Whitefield Hospital", "name_b": "Aster Women and Children Hospital", "expected": False, "cat": "corporate_rebranding", "synthetic": False},
    {"id": "P62", "name_a": "Apollo Spectra Hospital", "name_b": "Nova Specialty Surgery", "expected": False, "cat": "corporate_rebranding", "synthetic": False},
    {"id": "P63", "name_a": "Kauvery Hospital Electronic City", "name_b": "Ramakrishna Smart Hospital", "expected": False, "cat": "corporate_rebranding", "synthetic": False},
    {"id": "P64", "name_a": "Fortis Hospital Rajajinagar", "name_b": "Wockhardt Hospital Rajajinagar", "expected": False, "cat": "corporate_rebranding", "synthetic": False},
    {"id": "P65", "name_a": "Max Super Speciality Hospital Saket", "name_b": "Saket City Hospital", "expected": False, "cat": "corporate_rebranding", "synthetic": False},

    # -------------------------------------------------------------------------
    # Category 6: Geographic, District, State & Pincode Mismatches (10 pairs) [Synthetic location corruption stress test]
    # Expected: No Match (False) due to geographic contradiction
    # -------------------------------------------------------------------------
    {
        "id": "P66", "name_a": "Apollo Hospital", "name_b": "Apollo Hospital",
        "loc_a": {"state": "Karnataka", "district": "Bengaluru", "pincode": "560076"},
        "loc_b": {"state": "Tamil Nadu", "city": "Chennai", "pincode": "600006"},
        "expected": False, "cat": "geographic_cross_jurisdiction", "synthetic": True,
        "note": "Inter-state contradiction: Karnataka vs Tamil Nadu"
    },
    {
        "id": "P67", "name_a": "Fortis Hospital", "name_b": "Fortis Hospital",
        "loc_a": {"state": "Karnataka", "district": "Bengaluru", "pincode": "560076"},
        "loc_b": {"state": "Maharashtra", "city": "Mumbai", "pincode": "400078"},
        "expected": False, "cat": "geographic_cross_jurisdiction", "synthetic": True,
        "note": "Inter-state contradiction: Karnataka vs Maharashtra"
    },
    {
        "id": "P68", "name_a": "Manipal Hospital", "name_b": "Manipal Hospital",
        "loc_a": {"state": "Karnataka", "district": "Bengaluru", "pincode": "560017"},
        "loc_b": {"state": "Rajasthan", "city": "Jaipur", "pincode": "302013"},
        "expected": False, "cat": "geographic_cross_jurisdiction", "synthetic": True,
        "note": "Inter-state contradiction: Karnataka vs Rajasthan"
    },
    {
        "id": "P69", "name_a": "City Hospital", "name_b": "City Hospital",
        "loc_a": {"state": "Karnataka", "district": "Bagalkot", "pincode": "587101"},
        "loc_b": {"state": "Karnataka", "city": "Bengaluru", "pincode": "560001"},
        "expected": False, "cat": "geographic_cross_jurisdiction", "synthetic": True,
        "note": "Intra-state district conflict: Bagalkot (587xxx) vs Bengaluru (560xxx)"
    },
    {
        "id": "P70", "name_a": "Chakraborty Hospital", "name_b": "Chakraborty Hospital",
        "loc_a": {"state": "Andaman and Nicobar Islands", "district": "South Andaman", "pincode": "744101"},
        "loc_b": {"state": "Karnataka", "city": "Bengaluru", "pincode": "560001"},
        "expected": False, "cat": "geographic_cross_jurisdiction", "synthetic": True,
        "note": "Cross-jurisdiction conflict: Andaman vs Bengaluru"
    },
    {
        "id": "P71", "name_a": "General Hospital", "name_b": "General Hospital",
        "loc_a": {"state": "Karnataka", "district": "Mysuru", "pincode": "570001"},
        "loc_b": {"state": "Karnataka", "city": "Bengaluru", "pincode": "560001"},
        "expected": False, "cat": "geographic_cross_jurisdiction", "synthetic": True,
        "note": "Pincode prefix contradiction: 570 vs 560"
    },
    {
        "id": "P72", "name_a": "Life Care Hospital", "name_b": "Life Care Hospital",
        "loc_a": {"state": "Karnataka", "district": "Belagavi", "pincode": "590001"},
        "loc_b": {"state": "Karnataka", "city": "Bengaluru", "pincode": "560001"},
        "expected": False, "cat": "geographic_cross_jurisdiction", "synthetic": True,
        "note": "Pincode prefix contradiction: 590 vs 560"
    },
    {
        "id": "P73", "name_a": "Kasturba Hospital", "name_b": "Kasturba Hospital",
        "loc_a": {"state": "Karnataka", "district": "Udupi", "pincode": "576104"},
        "loc_b": {"state": "Karnataka", "city": "Bengaluru", "pincode": "560001"},
        "expected": False, "cat": "geographic_cross_jurisdiction", "synthetic": True,
        "note": "Pincode prefix contradiction: 576 vs 560"
    },
    {
        "id": "P74", "name_a": "Apollo Hospital", "name_b": "Apollo Hospital",
        "loc_a": {"state": "Karnataka", "district": "Bengaluru", "pincode": "744101"},
        "loc_b": {"state": "Karnataka", "city": "Bengaluru", "pincode": "560076"},
        "expected": False, "cat": "geographic_cross_jurisdiction", "synthetic": True,
        "note": "Internal conflict: 744 pincode contradicts Karnataka"
    },
    {
        "id": "P75", "name_a": "Motherhood Hospital", "name_b": "Motherhood Hospital",
        "loc_a": {"state": "Karnataka", "district": "Bengaluru", "pincode": "110001"},
        "loc_b": {"state": "Karnataka", "city": "Bengaluru", "pincode": "560038"},
        "expected": False, "cat": "geographic_cross_jurisdiction", "synthetic": True,
        "note": "Internal conflict: 110 pincode contradicts Karnataka"
    },
]

def evaluate_pair_set(pairs: List[Dict[str, Any]], strict_location: bool = True) -> Dict[str, Any]:
    tp, fp, tn, fn = 0, 0, 0, 0
    correct = 0
    cat_breakdown = {}

    for p in pairs:
        cat = p["cat"]
        if cat not in cat_breakdown:
            cat_breakdown[cat] = {"total": 0, "correct": 0}
        cat_breakdown[cat]["total"] += 1

        exp = p["expected"]

        # 1. Name normalization match
        norm_a = normalize_hospital_name(p["name_a"])
        norm_b = normalize_hospital_name(p["name_b"])
        name_match = (norm_a == norm_b)

        # 2. Location compatibility check
        loc_match = True
        if "loc_a" in p and "loc_b" in p:
            if strict_location:
                la = p["loc_a"]
                lb = p["loc_b"]
                conf_a, _ = check_location_conflict(la.get("state"), la.get("district"), la.get("pincode"))
                conf_b, _ = check_location_conflict(lb.get("state"), lb.get("city"), lb.get("pincode"))
                if conf_a or conf_b:
                    loc_match = False
                else:
                    loc_match = location_compatible(
                        la.get("state"), la.get("district"), la.get("pincode"),
                        lb.get("state"), lb.get("city"), lb.get("pincode")
                    )
            else:
                # Ablation: without strict location check, exact name match accepts regardless of location
                loc_match = True

        pred = (name_match and loc_match)
        is_c = (pred == exp)
        if is_c:
            correct += 1
            cat_breakdown[cat]["correct"] += 1

        if pred and exp:
            tp += 1
        elif pred and not exp:
            fp += 1
        elif not pred and not exp:
            tn += 1
        elif not pred and exp:
            fn += 1

    total = len(pairs)
    acc = correct / total if total > 0 else 0.0
    prec = tp / (tp + fp) if (tp + fp) > 0 else 0.0
    rec = tp / (tp + fn) if (tp + fn) > 0 else 0.0
    spec = tn / (tn + fp) if (tn + fp) > 0 else 0.0
    f1 = 2 * prec * rec / (prec + rec) if (prec + rec) > 0 else 0.0

    return {
        "total_pairs": total,
        "correct": correct,
        "accuracy": round(acc, 4),
        "precision": round(prec, 4),
        "recall": round(rec, 4),
        "specificity": round(spec, 4),
        "f1_score": round(f1, 4),
        "confusion_matrix": {"TP": tp, "FP": fp, "TN": tn, "FN": fn},
        "category_breakdown": {
            cat: {
                "total": data["total"],
                "correct": data["correct"],
                "accuracy": round(data["correct"] / data["total"], 4) if data["total"] > 0 else 0.0
            }
            for cat, data in cat_breakdown.items()
        }
    }

def run_evaluation():
    # Deterministic split: Dev (30 pairs), Test (45 pairs) stratified by category
    rng = random.Random(RANDOM_SEED)
    categories = {}
    for p in ALL_PAIRS:
        categories.setdefault(p["cat"], []).append(p)

    dev_pairs = []
    test_pairs = []
    for cat, items in sorted(categories.items()):
        # 40% dev, 60% test
        shuffled = list(items)
        rng.shuffle(shuffled)
        n_dev = max(1, int(round(len(shuffled) * 0.40)))
        dev_pairs.extend(shuffled[:n_dev])
        test_pairs.extend(shuffled[n_dev:])

    print(f"Dataset Split: Total={len(ALL_PAIRS)} pairs (Dev={len(dev_pairs)}, Held-out Test={len(test_pairs)})")

    # Evaluate on Dev
    dev_results = evaluate_pair_set(dev_pairs, strict_location=True)

    # Evaluate on Test (Default: strict_location_check=True)
    test_results_strict = evaluate_pair_set(test_pairs, strict_location=True)

    # Ablation on Test: strict_location_check=False (simulating legacy exact-name path without location check)
    test_results_no_location = evaluate_pair_set(test_pairs, strict_location=False)

    # Full set results for global reporting
    full_results_strict = evaluate_pair_set(ALL_PAIRS, strict_location=True)
    full_results_no_location = evaluate_pair_set(ALL_PAIRS, strict_location=False)

    print("\n" + "=" * 90)
    print("HOSPITAL ENTITY RESOLUTION & LOCATION AUDIT (DEV vs TEST SPLIT)")
    print("=" * 90)
    print(f"{'SPLIT':<15} | {'STRICT LOC':<11} | {'ACC':<6} | {'PREC':<6} | {'REC':<6} | {'SPEC':<6} | {'F1':<6}")
    print("=" * 90)
    print(f"{'Dev Set (N=30)':<15} | {'Yes':<11} | {dev_results['accuracy']:<6.4f} | {dev_results['precision']:<6.4f} | {dev_results['recall']:<6.4f} | {dev_results['specificity']:<6.4f} | {dev_results['f1_score']:<6.4f}")
    print(f"{'Test Set (N=45)':<15} | {'Yes (Ours)':<11} | {test_results_strict['accuracy']:<6.4f} | {test_results_strict['precision']:<6.4f} | {test_results_strict['recall']:<6.4f} | {test_results_strict['specificity']:<6.4f} | {test_results_strict['f1_score']:<6.4f}")
    print(f"{'Test Set (N=45)':<15} | {'No (Ablat)':<11} | {test_results_no_location['accuracy']:<6.4f} | {test_results_no_location['precision']:<6.4f} | {test_results_no_location['recall']:<6.4f} | {test_results_no_location['specificity']:<6.4f} | {test_results_no_location['f1_score']:<6.4f}")
    print(f"{'Full Set (N=75)':<15} | {'Yes (Ours)':<11} | {full_results_strict['accuracy']:<6.4f} | {full_results_strict['precision']:<6.4f} | {full_results_strict['recall']:<6.4f} | {full_results_strict['specificity']:<6.4f} | {full_results_strict['f1_score']:<6.4f}")
    print(f"{'Full Set (N=75)':<15} | {'No (Ablat)':<11} | {full_results_no_location['accuracy']:<6.4f} | {full_results_no_location['precision']:<6.4f} | {full_results_no_location['recall']:<6.4f} | {full_results_no_location['specificity']:<6.4f} | {full_results_no_location['f1_score']:<6.4f}")
    print("=" * 90)

    output_data = {
        "metadata": {
            "command": "python scripts/evaluate_hospital_matcher_extended.py",
            "git_commit": get_git_commit(),
            "date": datetime.now(timezone.utc).isoformat(),
            "random_seed": RANDOM_SEED,
            "total_pairs": len(ALL_PAIRS),
            "dev_pairs_count": len(dev_pairs),
            "test_pairs_count": len(test_pairs),
            "synthetic_pairs_count": sum(1 for p in ALL_PAIRS if p.get("synthetic")),
            "curated_pairs_count": sum(1 for p in ALL_PAIRS if not p.get("synthetic")),
        },
        "dev_evaluation": dev_results,
        "test_evaluation_strict_location": test_results_strict,
        "test_ablation_no_location_check": test_results_no_location,
        "full_evaluation_strict_location": full_results_strict,
        "full_ablation_no_location_check": full_results_no_location,
        "test_pair_ids": [p["id"] for p in test_pairs],
        "dev_pair_ids": [p["id"] for p in dev_pairs],
    }

    out_file = Path("data/evaluation/hospital_matcher_results.json")
    with open(out_file, "w", encoding="utf-8") as f:
        json.dump(output_data, f, indent=2)
    print(f"Results successfully saved to {out_file}\n")

if __name__ == "__main__":
    run_evaluation()
