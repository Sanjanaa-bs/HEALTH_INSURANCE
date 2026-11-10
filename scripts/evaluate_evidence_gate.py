import json
import re
import sys
import sqlite3
import numpy as np
from pathlib import Path
from typing import List, Dict, Any, Tuple

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from backend.app.services.qa import extract_meaningful_keywords
from backend.app.services.embeddings import LocalDenseEmbeddingProvider
from backend.app.search import search_document_chunks
from backend.app.database import SessionLocal

db = SessionLocal()
embedder = LocalDenseEmbeddingProvider(vector_dim=128)

# Connect to database to fetch all chunks
conn = sqlite3.connect("health_insurance.db")
c = conn.cursor()
c.execute("SELECT id, text, section_heading FROM document_chunks")
all_chunks = {r[0]: (r[2] + " " + r[1]).lower() for r in c.fetchall()}
conn.close()

# Test queries covering 4 evaluation cohorts:
# 1. Exact In-Scope (20 queries) - True Label: RELEVANT (1)
# 2. Semantic Paraphrases / Synonyms (15 queries) - True Label: RELEVANT (1)
# 3. Keyword-Sharing Distractors (15 queries) - True Label: IRRELEVANT (0)
# 4. Out-of-Domain Controls (15 queries) - True Label: IRRELEVANT (0)
# Total = 65 test queries

eval_cases = [
    # Cohort 1: Exact In-Scope
    {"q": "What is the waiting period for pre-existing diseases?", "label": 1, "cohort": "exact_in_scope"},
    {"q": "What does the policy say about room rent?", "label": 1, "cohort": "exact_in_scope"},
    {"q": "Are cataract treatments subject to specific conditions?", "label": 1, "cohort": "exact_in_scope"},
    {"q": "What does the policy say about pre-hospitalisation expenses?", "label": 1, "cohort": "exact_in_scope"},
    {"q": "What are the policy exclusions?", "label": 1, "cohort": "exact_in_scope"},
    {"q": "How does automatic restoration of the sum insured work?", "label": 1, "cohort": "exact_in_scope"},
    {"q": "What are the rules regarding organ donor expenses?", "label": 1, "cohort": "exact_in_scope"},
    {"q": "Is domiciliary hospitalization covered under the policy?", "label": 1, "cohort": "exact_in_scope"},
    {"q": "Are day care treatments covered under this policy?", "label": 1, "cohort": "exact_in_scope"},
    {"q": "What is the coverage limit for road ambulance charges?", "label": 1, "cohort": "exact_in_scope"},
    {"q": "What is the initial waiting period after taking a new policy?", "label": 1, "cohort": "exact_in_scope"},
    {"q": "Are AYUSH and alternative system treatments covered?", "label": 1, "cohort": "exact_in_scope"},
    {"q": "What waiting period applies for hernia, hydrocele, and piles?", "label": 1, "cohort": "exact_in_scope"},
    {"q": "What waiting period applies to maternity expenses?", "label": 1, "cohort": "exact_in_scope"},
    {"q": "Does the policy cover mental illnesses or psychiatric disorders?", "label": 1, "cohort": "exact_in_scope"},
    {"q": "What is the cumulative bonus percentage for claim-free years?", "label": 1, "cohort": "exact_in_scope"},
    {"q": "What is the timeline to intimate a planned cashless hospitalization?", "label": 1, "cohort": "exact_in_scope"},
    {"q": "Within how many days must reimbursement claim documents be submitted?", "label": 1, "cohort": "exact_in_scope"},
    {"q": "What is the role of the Insurance Ombudsman?", "label": 1, "cohort": "exact_in_scope"},
    {"q": "What is the free-look period duration for review of a newly issued policy?", "label": 1, "cohort": "exact_in_scope"},

    # Cohort 2: Semantic Paraphrases / Synonyms
    {"q": "How long must I be covered before chronic ailments diagnosed prior to enrollment are paid?", "label": 1, "cohort": "semantic_paraphrase"},
    {"q": "What are the limits on daily hospital ward and boarding fees?", "label": 1, "cohort": "semantic_paraphrase"},
    {"q": "Can I claim medical bills paid for consultations prior to hospital admission?", "label": 1, "cohort": "semantic_paraphrase"},
    {"q": "Are pharmacy bills paid during recovery after leaving hospital covered?", "label": 1, "cohort": "semantic_paraphrase"},
    {"q": "Is eye lens replacement surgery for cloudy vision capped?", "label": 1, "cohort": "semantic_paraphrase"},
    {"q": "Does the contract reimburse harvesting organs from a living body donor?", "label": 1, "cohort": "semantic_paraphrase"},
    {"q": "Is medical therapy administered at home when hospital beds are full covered?", "label": 1, "cohort": "semantic_paraphrase"},
    {"q": "Are short surgical operations without overnight stay covered?", "label": 1, "cohort": "semantic_paraphrase"},
    {"q": "Does the insurer pay for emergency patient van transit to clinic?", "label": 1, "cohort": "semantic_paraphrase"},
    {"q": "Are homeopathic remedies and ayurvedic hospital therapies payable?", "label": 1, "cohort": "semantic_paraphrase"},
    {"q": "How much extra coverage is granted when no claims are registered during annual term?", "label": 1, "cohort": "semantic_paraphrase"},
    {"q": "If basic coverage is exhausted mid-year does the policy refill the limit?", "label": 1, "cohort": "semantic_paraphrase"},
    {"q": "When can a pregnant mother claim delivery hospital expenses?", "label": 1, "cohort": "semantic_paraphrase"},
    {"q": "How many hours in advance must the hospital insurance desk file authorization?", "label": 1, "cohort": "semantic_paraphrase"},
    {"q": "Where can an aggrieved customer file an appeal if insurer rejects medical settlement?", "label": 1, "cohort": "semantic_paraphrase"},

    # Cohort 3: Keyword-Sharing Distractors (Shares keywords, but asks for unsupported or false premise)
    {"q": "What does the policy say about room rent in private clinics in United Kingdom?", "label": 0, "cohort": "distractor"},
    {"q": "What is the waiting period for pre-existing disease in pet dogs and cats?", "label": 0, "cohort": "distractor"},
    {"q": "Are cataract treatments covered when performed for cosmetic iris color change?", "label": 0, "cohort": "distractor"},
    {"q": "What is the road ambulance expense limit for helicopter flights to Mount Everest?", "label": 0, "cohort": "distractor"},
    {"q": "Does the policy cover exclusions for stock market losses and financial bankruptcy?", "label": 0, "cohort": "distractor"},
    {"q": "What is the reimbursement procedure for purchasing luxury sports cars after hospital discharge?", "label": 0, "cohort": "distractor"},
    {"q": "How does automatic restoration apply when building real estate apartments?", "label": 0, "cohort": "distractor"},
    {"q": "What are the rules regarding organ donor compensation for black market sales?", "label": 0, "cohort": "distractor"},
    {"q": "Is domiciliary hospitalization covered for regular beauty sleep treatments?", "label": 0, "cohort": "distractor"},
    {"q": "What day care treatments apply to repairing smartphone cracked screens?", "label": 0, "cohort": "distractor"},
    {"q": "Can I intimate cashless claims for dining at 5-star hotel restaurants?", "label": 0, "cohort": "distractor"},
    {"q": "Does the Ombudsman have jurisdiction over speeding traffic tickets?", "label": 0, "cohort": "distractor"},
    {"q": "What is the cumulative bonus for achieving high scores in video games?", "label": 0, "cohort": "distractor"},
    {"q": "Are psychiatric disorders covered for artificial intelligence software algorithms?", "label": 0, "cohort": "distractor"},
    {"q": "What is the free-look period for canceling Netflix movie streaming subscriptions?", "label": 0, "cohort": "distractor"},

    # Cohort 4: Out-of-Domain Negative Controls
    {"q": "How do I bake sourdough bread at high altitude with starter?", "label": 0, "cohort": "out_of_domain"},
    {"q": "What is the policy for orbital space flight and planetary excursion?", "label": 0, "cohort": "out_of_domain"},
    {"q": "How to repair automobile engine carburetor spark plug failure?", "label": 0, "cohort": "out_of_domain"},
    {"q": "What is the market price of Ethereum and Bitcoin mining hardware?", "label": 0, "cohort": "out_of_domain"},
    {"q": "How do I prune bonsai trees during winter season in Tokyo?", "label": 0, "cohort": "out_of_domain"},
    {"q": "What are the best tourist sightseeing spots in Venice Italy?", "label": 0, "cohort": "out_of_domain"},
    {"q": "How do convolutional neural networks optimize gradient descent weights?", "label": 0, "cohort": "out_of_domain"},
    {"q": "What is the recipe for cooking homemade authentic Italian pizza dough?", "label": 0, "cohort": "out_of_domain"},
    {"q": "How do airplanes generate aerodynamic lift over supersonic wings?", "label": 0, "cohort": "out_of_domain"},
    {"q": "What is the capital city of Madagascar in Southern Africa?", "label": 0, "cohort": "out_of_domain"},
    {"q": "How do I set up quantum computing qubit logic gates?", "label": 0, "cohort": "out_of_domain"},
    {"q": "Can I claim insurance reimbursement for buying fresh grocery apples?", "label": 0, "cohort": "out_of_domain"},
    {"q": "What is the compensation for lost airline luggage in airport terminal?", "label": 0, "cohort": "out_of_domain"},
    {"q": "How to tune an acoustic guitar in open D major tuning?", "label": 0, "cohort": "out_of_domain"},
    {"q": "What are the rules of playing contract bridge with card trump suits?", "label": 0, "cohort": "out_of_domain"},
]

# Gate mechanisms:
# 1. Standard Keyword Gate: m >= 2 if |W| >= 3 else 1
# 2. Strict Keyword Gate: m >= 3 if |W| >= 3 else 2
# 3. Cosine Gate (threshold tau = 0.40)
# 4. Hybrid Gate: Keyword hits >= 1 AND Cosine >= 0.35

gate_mechanisms = ["keyword_gate_standard", "keyword_gate_strict", "cosine_gate_tau40", "hybrid_gate_kw_cos"]
gate_stats = {gm: {"TP": 0, "FP": 0, "TN": 0, "FN": 0} for gm in gate_mechanisms}
cohort_breakdowns = {gm: {c: {"total": 0, "accepted": 0, "rejected": 0} for c in ["exact_in_scope", "semantic_paraphrase", "distractor", "out_of_domain"]} for gm in gate_mechanisms}

for item in eval_cases:
    q = item["q"]
    true_label = item["label"]
    cohort = item["cohort"]
    
    # 1. Retrieve candidates via BM25
    candidates = search_document_chunks(db=db, query_text=q, limit=5)
    q_vec = np.array(embedder.embed_text(q), dtype=np.float32)
    kw = extract_meaningful_keywords(q)
    
    # Decisions for each gate
    decisions = {}
    
    # Standard keyword gate:
    # Accepted if at least one candidate has hits >= required
    m_std = 2 if len(kw) >= 3 else 1
    std_accepted = False
    for c_item in candidates:
        full_c = (f"{c_item.get('section_heading', '')} {c_item.get('full_text', '')} {c_item.get('excerpt', '')}").lower()
        hits = sum(1 for w in kw if w in full_c)
        if hits >= m_std:
            std_accepted = True
            break
    decisions["keyword_gate_standard"] = 1 if std_accepted else 0
    
    # Strict keyword gate:
    m_strict = 3 if len(kw) >= 3 else 2
    strict_accepted = False
    for c_item in candidates:
        full_c = (f"{c_item.get('section_heading', '')} {c_item.get('full_text', '')} {c_item.get('excerpt', '')}").lower()
        hits = sum(1 for w in kw if w in full_c)
        if hits >= m_strict:
            strict_accepted = True
            break
    decisions["keyword_gate_strict"] = 1 if strict_accepted else 0
    
    # Cosine gate:
    cos_accepted = False
    for c_item in candidates:
        full_c = f"{c_item.get('section_heading', '')} {c_item.get('full_text', '')}"
        c_vec = np.array(embedder.embed_text(full_c), dtype=np.float32)
        sim = float(np.dot(q_vec, c_vec))
        if sim >= 0.40:
            cos_accepted = True
            break
    decisions["cosine_gate_tau40"] = 1 if cos_accepted else 0
    
    # Hybrid gate: keyword hits >= 1 and cosine >= 0.35
    hyb_accepted = False
    for c_item in candidates:
        full_c = (f"{c_item.get('section_heading', '')} {c_item.get('full_text', '')} {c_item.get('excerpt', '')}").lower()
        hits = sum(1 for w in kw if w in full_c)
        c_vec = np.array(embedder.embed_text(full_c), dtype=np.float32)
        sim = float(np.dot(q_vec, c_vec))
        if hits >= 1 and sim >= 0.35:
            hyb_accepted = True
            break
    decisions["hybrid_gate_kw_cos"] = 1 if hyb_accepted else 0
    
    for gm in gate_mechanisms:
        pred = decisions[gm]
        cohort_breakdowns[gm][cohort]["total"] += 1
        if pred == 1:
            cohort_breakdowns[gm][cohort]["accepted"] += 1
        else:
            cohort_breakdowns[gm][cohort]["rejected"] += 1
            
        if pred == 1 and true_label == 1:
            gate_stats[gm]["TP"] += 1
        elif pred == 1 and true_label == 0:
            gate_stats[gm]["FP"] += 1
        elif pred == 0 and true_label == 0:
            gate_stats[gm]["TN"] += 1
        elif pred == 0 and true_label == 1:
            gate_stats[gm]["FN"] += 1

db.close()

# Calculate Precision, Recall, Specificity, F1, FRR, FAR
metrics_summary = {}
for gm in gate_mechanisms:
    st = gate_stats[gm]
    tp, fp, tn, fn = st["TP"], st["FP"], st["TN"], st["FN"]
    
    precision = tp / (tp + fp) if (tp + fp) > 0 else 0.0
    recall = tp / (tp + fn) if (tp + fn) > 0 else 0.0
    specificity = tn / (tn + fp) if (tn + fp) > 0 else 0.0
    f1 = 2 * precision * recall / (precision + recall) if (precision + recall) > 0 else 0.0
    frr = fn / (tp + fn) if (tp + fn) > 0 else 0.0  # False Rejection Rate
    far = fp / (tn + fp) if (tn + fp) > 0 else 0.0  # False Acceptance Rate
    accuracy = (tp + tn) / (tp + fp + tn + fn)
    
    metrics_summary[gm] = {
        "confusion_matrix": st,
        "precision": round(precision, 4),
        "recall": round(recall, 4),
        "specificity": round(specificity, 4),
        "accuracy": round(accuracy, 4),
        "f1_score": round(f1, 4),
        "false_rejection_rate": round(frr, 4),
        "false_acceptance_rate": round(far, 4),
        "cohort_breakdown": cohort_breakdowns[gm]
    }

output_path = Path("data/evaluation/evidence_gate_results.json")
with open(output_path, "w", encoding="utf-8") as f:
    json.dump(metrics_summary, f, indent=2)

print("\n" + "="*95)
print(f"{'EVIDENCE GATE MECHANISM':<25} | {'PREC':<6} | {'REC':<6} | {'SPEC':<6} | {'ACC':<6} | {'F1':<6} | {'FRR':<6} | {'FAR':<6}")
print("="*95)
for gm, data in metrics_summary.items():
    print(f"{gm:<25} | {data['precision']:<6.4f} | {data['recall']:<6.4f} | {data['specificity']:<6.4f} | {data['accuracy']:<6.4f} | {data['f1_score']:<6.4f} | {data['false_rejection_rate']:<6.4f} | {data['false_acceptance_rate']:<6.4f}")
print("="*95)

print("\nCOHORT REJECTION RATES (True Negative Rate on Adversarial / OOD):")
for gm in gate_mechanisms:
    cb = cohort_breakdowns[gm]
    ood_rej = cb["out_of_domain"]["rejected"] / cb["out_of_domain"]["total"] * 100
    dist_rej = cb["distractor"]["rejected"] / cb["distractor"]["total"] * 100
    para_acc = cb["semantic_paraphrase"]["accepted"] / cb["semantic_paraphrase"]["total"] * 100
    print(f"  {gm:<25}: OOD Abstention={ood_rej:.1f}%, Distractor Rejection={dist_rej:.1f}%, Paraphrase Recall={para_acc:.1f}%")

print(f"\nResults successfully written to {output_path.resolve()}\n")
