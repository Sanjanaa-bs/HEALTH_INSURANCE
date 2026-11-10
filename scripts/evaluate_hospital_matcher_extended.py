import json
import sys
from pathlib import Path
from typing import List, Dict, Any

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from backend.app.api.v1.hospitals import (
    normalize_hospital_name,
    location_compatible,
    check_location_conflict,
)

# 75 Comprehensive hospital matching test cases across 6 distinct challenge categories
test_cases = [
    # -------------------------------------------------------------------------
    # Category 1: Case, Whitespace, Punctuation & Ampersand Variations (15 pairs) -> EXPECT MATCH
    # -------------------------------------------------------------------------
    {"name_a": "Apollo Hospitals - Bangalore", "name_b": "Apollo Hospital Bangalore", "expected": True, "cat": "formatting"},
    {"name_a": "BANGALORE BAPTIST HOSPITAL", "name_b": "Bangalore Baptist Hospital", "expected": True, "cat": "formatting"},
    {"name_a": "Kerudi Hospital & Research Centre", "name_b": "Kerudi Hospital And Research Centre", "expected": True, "cat": "formatting"},
    {"name_a": "St. John's Medical College Hospital", "name_b": "St Johns Medical College Hospital", "expected": True, "cat": "formatting"},
    {"name_a": "St. Martha's Hospital", "name_b": "St Marthas Hospital", "expected": True, "cat": "formatting"},
    {"name_a": "St. Philomena's Hospital", "name_b": "St Philomenas Hospital", "expected": True, "cat": "formatting"},
    {"name_a": "M. S. Ramaiah Memorial Hospital", "name_b": "MS Ramaiah Memorial Hospital", "expected": True, "cat": "formatting"},
    {"name_a": "Fortis Hospital - Bannerghatta Road", "name_b": "Fortis Hospital Bannerghatta Road", "expected": True, "cat": "formatting"},
    {"name_a": "Manipal Hospital - Old Airport Road", "name_b": "Manipal Hospital Old Airport Road", "expected": True, "cat": "formatting"},
    {"name_a": "Sagar Hospitals - DSI", "name_b": "Sagar Hospital DSI", "expected": True, "cat": "formatting"},
    {"name_a": "Columbia Asia Hospital - Hebbal", "name_b": "Columbia Asia Hospital Hebbal", "expected": True, "cat": "formatting"},
    {"name_a": "Narayana Hrudayalaya - Institute of Cardiac Sciences", "name_b": "Narayana Hrudayalaya Institute of Cardiac Sciences", "expected": True, "cat": "formatting"},
    {"name_a": "Dr. Agarwal's Eye Hospital", "name_b": "Dr Agarwals Eye Hospital", "expected": True, "cat": "formatting"},
    {"name_a": "Nethradhama Super Speciality Eye Hospital", "name_b": "Nethradhama Super Speciality Eye Hospital", "expected": True, "cat": "formatting"},
    {"name_a": "Sri Jayadeva Institute of Cardiovascular Sciences & Research", "name_b": "Sri Jayadeva Institute of Cardiovascular Sciences and Research", "expected": True, "cat": "formatting"},

    # -------------------------------------------------------------------------
    # Category 2: Legal & Corporate Suffixes (10 pairs) -> EXPECT MATCH
    # -------------------------------------------------------------------------
    {"name_a": "Chaitanya Hospital Pvt Ltd", "name_b": "Chaitanya Hospital", "expected": True, "cat": "legal_suffixes"},
    {"name_a": "Madhusudana Health Care Services Pvt Ltd", "name_b": "Madhusudana Health Care Services", "expected": True, "cat": "legal_suffixes"},
    {"name_a": "Gleneagles Healthcare India Private Limited", "name_b": "Gleneagles Healthcare India", "expected": True, "cat": "legal_suffixes"},
    {"name_a": "Healthcare Global Enterprises Limited", "name_b": "Healthcare Global Enterprises", "expected": True, "cat": "legal_suffixes"},
    {"name_a": "Narayana Health Private Limited", "name_b": "Narayana Health", "expected": True, "cat": "legal_suffixes"},
    {"name_a": "Apollo Hospitals Enterprise Limited", "name_b": "Apollo Hospital Enterprise", "expected": True, "cat": "legal_suffixes"},
    {"name_a": "Aster DM Healthcare Ltd", "name_b": "Aster DM Healthcare", "expected": True, "cat": "legal_suffixes"},
    {"name_a": "Max Healthcare Institute Limited", "name_b": "Max Healthcare Institute", "expected": True, "cat": "legal_suffixes"},
    {"name_a": "Fortis Healthcare Private Limited", "name_b": "Fortis Healthcare", "expected": True, "cat": "legal_suffixes"},
    {"name_a": "Medanta The Medicity Global Health Limited", "name_b": "Medanta The Medicity Global Health", "expected": True, "cat": "legal_suffixes"},

    # -------------------------------------------------------------------------
    # Category 3: Medical Acronyms & Abbreviations (15 pairs) -> Normalized Comparison
    # -------------------------------------------------------------------------
    {"name_a": "HCG Cancer Hospital", "name_b": "HCG Cancer Centre", "expected": False, "cat": "abbreviations"}, # Distinct centre vs hospital
    {"name_a": "BGS Gleneagles Global Hospital", "name_b": "BGS Gleneagles Global Hospital", "expected": True, "cat": "abbreviations"},
    {"name_a": "SDM College of Medical Sciences & Hospital", "name_b": "SDM College of Medical Sciences and Hospital", "expected": True, "cat": "abbreviations"},
    {"name_a": "CSI Holdsworth Memorial Hospital", "name_b": "CSI Holdsworth Memorial Hospital", "expected": True, "cat": "abbreviations"},
    {"name_a": "ESI Hospital Rajajinagar", "name_b": "ESI Hospital Rajajinagar", "expected": True, "cat": "abbreviations"},
    {"name_a": "KLES Dr. Prabhakar Kore Hospital", "name_b": "KLES Dr Prabhakar Kore Hospital", "expected": True, "cat": "abbreviations"},
    {"name_a": "JSS Hospital Mysore", "name_b": "JSS Hospital Mysore", "expected": True, "cat": "abbreviations"},
    {"name_a": "KIMS Hospital and Research Centre", "name_b": "KIMS Hospital And Research Centre", "expected": True, "cat": "abbreviations"},
    {"name_a": "AJ Hospital & Research Centre Mangalore", "name_b": "AJ Hospital and Research Centre Mangalore", "expected": True, "cat": "abbreviations"},
    {"name_a": "Yenepoya Specialty Hospital", "name_b": "Yenepoya Specialty Hospital", "expected": True, "cat": "abbreviations"},
    {"name_a": "Father Muller Medical College Hospital", "name_b": "Father Muller Medical College Hospital", "expected": True, "cat": "abbreviations"},
    {"name_a": "KVG Medical College Hospital Sullia", "name_b": "KVG Medical College Hospital Sullia", "expected": True, "cat": "abbreviations"},
    {"name_a": "Father Muller Homoeopathic Medical College & Hospital", "name_b": "Father Muller Homoeopathic Medical College and Hospital", "expected": True, "cat": "abbreviations"},
    {"name_a": "Kasturba Hospital Manipal", "name_b": "Kasturba Hospital Manipal", "expected": True, "cat": "abbreviations"},
    {"name_a": "TMC Hospital", "name_b": "Tata Memorial Centre Hospital", "expected": False, "cat": "abbreviations"}, # Unexpanded acronym should not false match

    # -------------------------------------------------------------------------
    # Category 4: Distinct Facilities with Shared Prefixes / False Friends (15 pairs) -> MUST NOT MATCH
    # -------------------------------------------------------------------------
    {"name_a": "Aditi Eye Care", "name_b": "Aditi Nursing Home", "expected": False, "cat": "distinct_facilities"},
    {"name_a": "Manipal Hospital Whitefield", "name_b": "Manipal Hospital Old Airport Road", "expected": False, "cat": "distinct_facilities"},
    {"name_a": "Manipal Northside Hospital", "name_b": "Manipal Hospital", "expected": False, "cat": "distinct_facilities"},
    {"name_a": "Apollo Clinic", "name_b": "Apollo Hospitals", "expected": False, "cat": "distinct_facilities"},
    {"name_a": "Apollo Cradle", "name_b": "Apollo Hospitals", "expected": False, "cat": "distinct_facilities"},
    {"name_a": "Fortis La Femme", "name_b": "Fortis Hospital", "expected": False, "cat": "distinct_facilities"},
    {"name_a": "Fortis Hospital Cunningham Road", "name_b": "Fortis Hospital Nagarbhavi", "expected": False, "cat": "distinct_facilities"},
    {"name_a": "Sagar Hospital Jayanagar", "name_b": "Sagar Hospital Banashankari", "expected": False, "cat": "distinct_facilities"},
    {"name_a": "Narayana Multispeciality Hospital", "name_b": "Narayana Hrudayalaya", "expected": False, "cat": "distinct_facilities"},
    {"name_a": "Cloudnine Hospital Malleshwaram", "name_b": "Cloudnine Hospital Jayanagar", "expected": False, "cat": "distinct_facilities"},
    {"name_a": "Motherhood Hospital Indiranagar", "name_b": "Motherhood Hospital Sarjapur", "expected": False, "cat": "distinct_facilities"},
    {"name_a": "Aster CMI Hospital", "name_b": "Aster RV Hospital", "expected": False, "cat": "distinct_facilities"},
    {"name_a": "Sparsh Hospital Yeshwanthpur", "name_b": "Sparsh Hospital Infantry Road", "expected": False, "cat": "distinct_facilities"},
    {"name_a": "Vikram Hospital", "name_b": "Manipal Hospital Millers Road", "expected": False, "cat": "distinct_facilities"},
    {"name_a": "Bowring and Lady Curzon Hospital", "name_b": "Victoria Hospital", "expected": False, "cat": "distinct_facilities"},

    # -------------------------------------------------------------------------
    # Category 5: Renamed Facilities & Corporate Rebranding (10 pairs) -> MUST NOT FALSE MATCH UNLESS RECORDED
    # -------------------------------------------------------------------------
    {"name_a": "Gleneagles BGS Hospital", "name_b": "BGS Global Hospital", "expected": False, "cat": "renamed_facilities"},
    {"name_a": "Manipal Hospital Yeshwanthpur", "name_b": "Columbia Asia Referral Hospital Yeshwanthpur", "expected": False, "cat": "renamed_facilities"},
    {"name_a": "Manipal Hospital Whitefield", "name_b": "Columbia Asia Hospital Whitefield", "expected": False, "cat": "renamed_facilities"},
    {"name_a": "Manipal Hospital Hebbal", "name_b": "Columbia Asia Hospital Hebbal", "expected": False, "cat": "renamed_facilities"},
    {"name_a": "Manipal Hospital Millers Road", "name_b": "Vikram Hospital", "expected": False, "cat": "renamed_facilities"},
    {"name_a": "Aster Whitefield Hospital", "name_b": "Aster Women and Children Hospital", "expected": False, "cat": "renamed_facilities"},
    {"name_a": "Apollo Spectra Hospital", "name_b": "Nova Specialty Surgery", "expected": False, "cat": "renamed_facilities"},
    {"name_a": "Kauvery Hospital Electronic City", "name_b": "Ramakrishna Smart Hospital", "expected": False, "cat": "renamed_facilities"},
    {"name_a": "Fortis Hospital Rajajinagar", "name_b": "Wockhardt Hospital Rajajinagar", "expected": False, "cat": "renamed_facilities"},
    {"name_a": "Max Super Speciality Hospital Saket", "name_b": "Saket City Hospital", "expected": False, "cat": "renamed_facilities"},

    # -------------------------------------------------------------------------
    # Category 6: Geographic, District, State & Pincode Mismatches (10 pairs) -> MUST REJECT LOCATION
    # -------------------------------------------------------------------------
    {
        "name_a": "Apollo Hospital", "name_b": "Apollo Hospital",
        "loc_a": {"state": "Karnataka", "district": "Bengaluru", "pincode": "560076"},
        "loc_b": {"state": "Tamil Nadu", "city": "Chennai", "pincode": "600006"},
        "expected": False, "cat": "geographic_mismatches", "reason": "State conflict: Karnataka vs Tamil Nadu"
    },
    {
        "name_a": "Fortis Hospital", "name_b": "Fortis Hospital",
        "loc_a": {"state": "Karnataka", "district": "Bengaluru", "pincode": "560076"},
        "loc_b": {"state": "Maharashtra", "city": "Mumbai", "pincode": "400078"},
        "expected": False, "cat": "geographic_mismatches", "reason": "State conflict: Karnataka vs Maharashtra"
    },
    {
        "name_a": "Manipal Hospital", "name_b": "Manipal Hospital",
        "loc_a": {"state": "Karnataka", "district": "Bengaluru", "pincode": "560017"},
        "loc_b": {"state": "Rajasthan", "city": "Jaipur", "pincode": "302013"},
        "expected": False, "cat": "geographic_mismatches", "reason": "State conflict: Karnataka vs Rajasthan"
    },
    {
        "name_a": "City Hospital", "name_b": "City Hospital",
        "loc_a": {"state": "Karnataka", "district": "Bagalkot", "pincode": "587101"},
        "loc_b": {"state": "Karnataka", "city": "Bengaluru", "pincode": "560001"},
        "expected": False, "cat": "geographic_mismatches", "reason": "Pincode prefix contradiction: 587 vs 560"
    },
    {
        "name_a": "Chakraborty Hospital", "name_b": "Chakraborty Hospital",
        "loc_a": {"state": "Andaman and Nicobar Islands", "district": "South Andaman", "pincode": "744101"},
        "loc_b": {"state": "Karnataka", "city": "Bengaluru", "pincode": "560001"},
        "expected": False, "cat": "geographic_mismatches", "reason": "State contradiction: Andaman vs Karnataka"
    },
    {
        "name_a": "General Hospital", "name_b": "General Hospital",
        "loc_a": {"state": "Karnataka", "district": "Mysuru", "pincode": "570001"},
        "loc_b": {"state": "Karnataka", "city": "Bengaluru", "pincode": "560001"},
        "expected": False, "cat": "geographic_mismatches", "reason": "Pincode contradiction: 570 vs 560"
    },
    {
        "name_a": "Life Care Hospital", "name_b": "Life Care Hospital",
        "loc_a": {"state": "Karnataka", "district": "Belagavi", "pincode": "590001"},
        "loc_b": {"state": "Karnataka", "city": "Bengaluru", "pincode": "560001"},
        "expected": False, "cat": "geographic_mismatches", "reason": "Pincode contradiction: 590 vs 560"
    },
    {
        "name_a": "Kasturba Hospital", "name_b": "Kasturba Hospital",
        "loc_a": {"state": "Karnataka", "district": "Udupi", "pincode": "576104"},
        "loc_b": {"state": "Karnataka", "city": "Bengaluru", "pincode": "560001"},
        "expected": False, "cat": "geographic_mismatches", "reason": "Pincode contradiction: 576 vs 560"
    },
    {
        "name_a": "Apollo Hospital", "name_b": "Apollo Hospital",
        "loc_a": {"state": "Karnataka", "district": "Bengaluru", "pincode": "744101"}, # Andaman pincode erroneously attached
        "loc_b": {"state": "Karnataka", "city": "Bengaluru", "pincode": "560076"},
        "expected": False, "cat": "geographic_mismatches", "reason": "Internal conflict: 744 pin contradicts Karnataka"
    },
    {
        "name_a": "Motherhood Hospital", "name_b": "Motherhood Hospital",
        "loc_a": {"state": "Karnataka", "district": "Bengaluru", "pincode": "110001"}, # Delhi pincode erroneously attached
        "loc_b": {"state": "Karnataka", "city": "Bengaluru", "pincode": "560038"},
        "expected": False, "cat": "geographic_mismatches", "reason": "Internal conflict: 110 pin contradicts Karnataka"
    }
]

total_cases = len(test_cases)
correct_predictions = 0
tp, fp, tn, fn = 0, 0, 0, 0
category_stats = {}

for case in test_cases:
    cat = case["cat"]
    if cat not in category_stats:
        category_stats[cat] = {"total": 0, "correct": 0, "predictions": []}
    category_stats[cat]["total"] += 1

    expected = case["expected"]
    
    # 1. Normalize names
    norm_a = normalize_hospital_name(case["name_a"])
    norm_b = normalize_hospital_name(case["name_b"])
    name_matched = (norm_a == norm_b)

    # 2. Location compatibility check
    loc_matched = True
    if "loc_a" in case and "loc_b" in case:
        la = case["loc_a"]
        lb = case["loc_b"]
        
        # Check internal location conflict
        conf_a, _ = check_location_conflict(la.get("state"), la.get("district"), la.get("pincode"))
        conf_b, _ = check_location_conflict(lb.get("state"), lb.get("city"), lb.get("pincode"))
        if conf_a or conf_b:
            loc_matched = False
        else:
            loc_matched = location_compatible(
                la.get("state"), la.get("district"), la.get("pincode"),
                lb.get("state"), lb.get("city"), lb.get("pincode")
            )
    
    final_match = name_matched and loc_matched
    is_correct = (final_match == expected)
    if is_correct:
        correct_predictions += 1
        category_stats[cat]["correct"] += 1
        
    if final_match and expected:
        tp += 1
    elif final_match and not expected:
        fp += 1
    elif not final_match and not expected:
        tn += 1
    elif not final_match and expected:
        fn += 1

    category_stats[cat]["predictions"].append({
        "pair": f"{case['name_a']} <-> {case['name_b']}",
        "expected": expected,
        "predicted": final_match,
        "correct": is_correct
    })

accuracy = correct_predictions / total_cases
precision = tp / (tp + fp) if (tp + fp) > 0 else 0.0
recall = tp / (tp + fn) if (tp + fn) > 0 else 0.0
specificity = tn / (tn + fp) if (tn + fp) > 0 else 0.0
f1 = 2 * precision * recall / (precision + recall) if (precision + recall) > 0 else 0.0

summary_report = {
    "total_test_pairs": total_cases,
    "correct_predictions": correct_predictions,
    "accuracy": round(accuracy * 100, 2),
    "precision": round(precision * 100, 2),
    "recall": round(recall * 100, 2),
    "specificity": round(specificity * 100, 2),
    "f1_score": round(f1 * 100, 2),
    "confusion_matrix": {"TP": tp, "FP": fp, "TN": tn, "FN": fn},
    "category_breakdown": {
        cat: {
            "total": data["total"],
            "correct": data["correct"],
            "accuracy_pct": round(data["correct"] / data["total"] * 100, 2)
        }
        for cat, data in category_stats.items()
    }
}

out_path = Path("data/evaluation/hospital_matcher_results.json")
with open(out_path, "w", encoding="utf-8") as f:
    json.dump(summary_report, f, indent=2)

print("\n" + "="*85)
print(f"EXTENDED HOSPITAL MATCHER EVALUATION ({total_cases} Challenging Test Pairs)")
print("="*85)
print(f"Accuracy:    {accuracy*100:.2f}% ({correct_predictions}/{total_cases})")
print(f"Precision:   {precision*100:.2f}% (False Positive Rate: {(1-specificity)*100:.2f}%)")
print(f"Recall:      {recall*100:.2f}%")
print(f"Specificity: {specificity*100:.2f}%")
print(f"F1-Score:    {f1*100:.2f}%")
print(f"Confusion Matrix: TP={tp}, FP={fp}, TN={tn}, FN={fn}")
print("-"*85)
print(f"{'CATEGORY':<30} | {'PAIRS':<8} | {'CORRECT':<10} | {'ACCURACY %':<12}")
print("-"*85)
for cat, data in summary_report["category_breakdown"].items():
    print(f"{cat:<30} | {data['total']:<8} | {data['correct']:<10} | {data['accuracy_pct']:<12.2f}")
print("="*85)
print(f"Detailed results saved to {out_path.resolve()}\n")

