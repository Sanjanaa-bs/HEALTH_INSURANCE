import json
from pathlib import Path

benchmark_data = [
    # -------------------------------------------------------------
    # Category 1: Coverage Terms & Limits (15 Questions)
    # -------------------------------------------------------------
    {
        "id": "Q01",
        "category": "coverage_terms_and_limits",
        "question": "What does the policy say about room rent?",
        "expected_status": "answered",
        "target_documents": ["policy", "cis"],
        "expected_page_numbers": [9, 8],
        "key_phrases": ["room rent", "single private a/c room", "boarding"],
        "ground_truth_summary": "Single Private A/C Room is covered for sum insured of 5 lakhs and above. Boarding and nursing expenses provided by hospital."
    },
    {
        "id": "Q02",
        "category": "coverage_terms_and_limits",
        "question": "What is the policy coverage for ICU charges?",
        "expected_status": "answered",
        "target_documents": ["policy", "cis"],
        "expected_page_numbers": [9, 8],
        "key_phrases": ["icu", "intensive care unit"],
        "ground_truth_summary": "ICU and Intensive Cardiac Care Unit charges are covered at actuals up to sum insured without capping."
    },
    {
        "id": "Q03",
        "category": "coverage_terms_and_limits",
        "question": "What does the policy say about pre-hospitalisation expenses?",
        "expected_status": "answered",
        "target_documents": ["policy", "cis"],
        "expected_page_numbers": [11, 3],
        "key_phrases": ["pre-hospitalization", "60 days"],
        "ground_truth_summary": "Pre-hospitalization medical expenses incurred for a period of up to 60 days prior to the date of hospitalization are covered."
    },
    {
        "id": "Q04",
        "category": "coverage_terms_and_limits",
        "question": "What is the limit and duration for post-hospitalization medical expenses?",
        "expected_status": "answered",
        "target_documents": ["policy", "cis"],
        "expected_page_numbers": [11, 3],
        "key_phrases": ["post-hospitalization", "90 days"],
        "ground_truth_summary": "Post-hospitalization medical expenses incurred for a period up to 90 days following discharge are covered."
    },
    {
        "id": "Q05",
        "category": "coverage_terms_and_limits",
        "question": "Are day care treatments covered under this policy?",
        "expected_status": "answered",
        "target_documents": ["policy", "cis"],
        "expected_page_numbers": [9, 3],
        "key_phrases": ["day care", "24 hours"],
        "ground_truth_summary": "All day care procedures and surgeries requiring less than 24 hours hospitalization due to technological advancement are covered."
    },
    {
        "id": "Q06",
        "category": "coverage_terms_and_limits",
        "question": "What is the coverage limit for road ambulance charges?",
        "expected_status": "answered",
        "target_documents": ["policy", "cis"],
        "expected_page_numbers": [10, 3],
        "key_phrases": ["ambulance", "road ambulance"],
        "ground_truth_summary": "Road ambulance expenses incurred for transportation of the insured to the hospital are payable as per policy limits."
    },
    {
        "id": "Q07",
        "category": "coverage_terms_and_limits",
        "question": "Does the policy cover air ambulance services and what is the limit?",
        "expected_status": "answered",
        "target_documents": ["policy", "cis"],
        "expected_page_numbers": [11, 3],
        "key_phrases": ["air ambulance"],
        "ground_truth_summary": "Air ambulance services are covered up to specified limits (e.g. Rs. 2,50,000 per hospitalization, up to 5,00,000 per policy year) subject to treating doctor certification."
    },
    {
        "id": "Q08",
        "category": "coverage_terms_and_limits",
        "question": "Are AYUSH and alternative system treatments covered?",
        "expected_status": "answered",
        "target_documents": ["policy", "cis"],
        "expected_page_numbers": [10, 3],
        "key_phrases": ["ayush", "ayurveda", "unani", "siddha", "homeopathy"],
        "ground_truth_summary": "Inpatient hospitalization expenses incurred under Ayurveda, Yoga & Naturopathy, Unani, Siddha, and Homeopathy in government-recognized hospitals are covered up to the sum insured."
    },
    {
        "id": "Q09",
        "category": "coverage_terms_and_limits",
        "question": "What are the rules regarding organ donor expenses?",
        "expected_status": "answered",
        "target_documents": ["policy", "cis"],
        "expected_page_numbers": [11, 3],
        "key_phrases": ["organ donor", "harvesting"],
        "ground_truth_summary": "Inpatient hospitalization expenses incurred for organ donor during organ harvesting are covered provided the organ donation complies with Transplantation of Human Organs Act."
    },
    {
        "id": "Q10",
        "category": "coverage_terms_and_limits",
        "question": "Is domiciliary hospitalization covered under the policy?",
        "expected_status": "answered",
        "target_documents": ["policy", "cis"],
        "expected_page_numbers": [10, 3],
        "key_phrases": ["domiciliary", "home treatment"],
        "ground_truth_summary": "Domiciliary hospitalization exceeding 3 days for medical treatment which ordinarily requires hospital confinement is covered under specified conditions."
    },
    {
        "id": "Q11",
        "category": "coverage_terms_and_limits",
        "question": "What is the cumulative bonus percentage awarded for claim-free years?",
        "expected_status": "answered",
        "target_documents": ["policy", "cis"],
        "expected_page_numbers": [12, 4],
        "key_phrases": ["cumulative bonus", "no claim bonus", "50%"],
        "ground_truth_summary": "Cumulative bonus of 50% of the basic sum insured is awarded for each claim-free year, up to a maximum of 100% of the sum insured."
    },
    {
        "id": "Q12",
        "category": "coverage_terms_and_limits",
        "question": "How does automatic restoration of the sum insured operate?",
        "expected_status": "answered",
        "target_documents": ["policy", "cis"],
        "expected_page_numbers": [12, 4],
        "key_phrases": ["restoration", "sum insured"],
        "ground_truth_summary": "Automatic restoration of 100% of the sum insured is available upon partial or full exhaustion, usable for subsequent hospitalizations during the policy year."
    },
    {
        "id": "Q13",
        "category": "coverage_terms_and_limits",
        "question": "Does the policy cover modern treatments and robotic surgery?",
        "expected_status": "answered",
        "target_documents": ["policy", "cis"],
        "expected_page_numbers": [13, 4],
        "key_phrases": ["modern treatment", "robotic surgery", "stem cell"],
        "ground_truth_summary": "Modern treatments including robotic surgeries, deep brain stimulation, and stem cell therapy are covered up to specified limits or full sum insured depending on procedure."
    },
    {
        "id": "Q14",
        "category": "coverage_terms_and_limits",
        "question": "What is the coverage for second medical opinion?",
        "expected_status": "answered",
        "target_documents": ["policy", "cis"],
        "expected_page_numbers": [13, 4],
        "key_phrases": ["second medical opinion"],
        "ground_truth_summary": "The insured person can obtain a second medical opinion from the company's network doctor without impacting the sum insured."
    },
    {
        "id": "Q15",
        "category": "coverage_terms_and_limits",
        "question": "Are health checkup expenses reimbursed and at what interval?",
        "expected_status": "answered",
        "target_documents": ["policy", "cis"],
        "expected_page_numbers": [13, 4],
        "key_phrases": ["health checkup"],
        "ground_truth_summary": "Health checkup expenses are covered for each claim-free year up to specified financial limits based on sum insured."
    },

    # -------------------------------------------------------------
    # Category 2: Waiting Periods & Specific Illnesses (12 Questions)
    # -------------------------------------------------------------
    {
        "id": "Q16",
        "category": "waiting_periods_and_conditions",
        "question": "What is the waiting period for pre-existing diseases?",
        "expected_status": "answered",
        "target_documents": ["policy", "cis"],
        "expected_page_numbers": [41, 7],
        "key_phrases": ["waiting period", "pre-existing", "24 months"],
        "ground_truth_summary": "Pre-existing diseases have a standard waiting period of 24 months of continuous coverage without break from inception."
    },
    {
        "id": "Q17",
        "category": "waiting_periods_and_conditions",
        "question": "What is the initial waiting period after taking a new policy?",
        "expected_status": "answered",
        "target_documents": ["policy", "cis"],
        "expected_page_numbers": [41, 7],
        "key_phrases": ["30 days", "initial waiting period"],
        "ground_truth_summary": "An initial waiting period of 30 days applies from policy inception, during which illnesses are excluded except hospitalizations caused by accidents."
    },
    {
        "id": "Q18",
        "category": "waiting_periods_and_conditions",
        "question": "Are cataract treatments subject to specific conditions?",
        "expected_status": "answered",
        "target_documents": ["policy", "cis"],
        "expected_page_numbers": [30, 9],
        "key_phrases": ["cataract", "24 months", "sub-limit"],
        "ground_truth_summary": "Cataract treatment is subject to a 24-month waiting period and specific financial sub-limits per eye based on sum insured."
    },
    {
        "id": "Q19",
        "category": "waiting_periods_and_conditions",
        "question": "What is the waiting period for hernia, hydrocele, and piles?",
        "expected_status": "answered",
        "target_documents": ["policy", "cis"],
        "expected_page_numbers": [30, 8],
        "key_phrases": ["hernia", "24 months", "specified illness"],
        "ground_truth_summary": "A 24-month waiting period applies for benign ENT disorders, hernia, hydrocele, and benign prostatic hypertrophy."
    },
    {
        "id": "Q20",
        "category": "waiting_periods_and_conditions",
        "question": "What is the waiting period for joint replacement surgery unless caused by accident?",
        "expected_status": "answered",
        "target_documents": ["policy", "cis"],
        "expected_page_numbers": [30, 8],
        "key_phrases": ["joint replacement", "knee replacement", "24 months"],
        "ground_truth_summary": "Joint replacement surgeries (knee, hip) are excluded until the expiry of 24 months of continuous coverage unless required due to an accidental injury."
    },
    {
        "id": "Q21",
        "category": "waiting_periods_and_conditions",
        "question": "Is bariatric surgery covered and what waiting period applies?",
        "expected_status": "answered",
        "target_documents": ["policy", "cis"],
        "expected_page_numbers": [31, 8],
        "key_phrases": ["bariatric surgery", "24 months", "bmi"],
        "ground_truth_summary": "Bariatric metabolic surgery is covered after 24 months waiting period if severe clinical obesity criteria (e.g. BMI >= 40 or BMI >= 35 with co-morbidities) are satisfied."
    },
    {
        "id": "Q22",
        "category": "waiting_periods_and_conditions",
        "question": "What waiting period applies to maternity expenses and normal or caesarean delivery?",
        "expected_status": "answered",
        "target_documents": ["policy", "cis"],
        "expected_page_numbers": [10, 8],
        "key_phrases": ["maternity", "24 months"],
        "ground_truth_summary": "Maternity cover requires 24 months of continuous coverage under the policy, with maximum limits per delivery (normal/caesarean) up to 2 deliveries."
    },
    {
        "id": "Q23",
        "category": "waiting_periods_and_conditions",
        "question": "Are newborn baby medical expenses covered under maternity benefits?",
        "expected_status": "answered",
        "target_documents": ["policy", "cis"],
        "expected_page_numbers": [10, 8],
        "key_phrases": ["newborn", "baby cover"],
        "ground_truth_summary": "Hospitalization expenses for newborn baby born to insured mother are covered from day 1 up to specified limits under maternity section."
    },
    {
        "id": "Q24",
        "category": "waiting_periods_and_conditions",
        "question": "Does the policy cover mental illnesses or psychiatric disorders?",
        "expected_status": "answered",
        "target_documents": ["policy", "cis"],
        "expected_page_numbers": [13, 8],
        "key_phrases": ["mental illness", "psychiatric"],
        "ground_truth_summary": "Inpatient treatment for mental illnesses is covered in accordance with Mental Healthcare Act 2017 without discriminatory sub-limits."
    },
    {
        "id": "Q25",
        "category": "waiting_periods_and_conditions",
        "question": "Can pre-existing disease waiting period be reduced by paying additional premium?",
        "expected_status": "answered",
        "target_documents": ["policy", "cis"],
        "expected_page_numbers": [41, 7],
        "key_phrases": ["buyback", "pre-existing waiting period", "reduction"],
        "ground_truth_summary": "An optional buyback / waiting period reduction rider may be available at inception reducing 24-month waiting period to 12 months on payment of specific additional premium."
    },
    {
        "id": "Q26",
        "category": "waiting_periods_and_conditions",
        "question": "What waiting period applies for stone disease of biliary and urinary systems?",
        "expected_status": "answered",
        "target_documents": ["policy", "cis"],
        "expected_page_numbers": [30, 8],
        "key_phrases": ["calculus", "gallstones", "kidney stone", "24 months"],
        "ground_truth_summary": "Calculus diseases of gall bladder, biliary tract, and urinary system are subject to a 24-month waiting period from inception."
    },
    {
        "id": "Q27",
        "category": "waiting_periods_and_conditions",
        "question": "What is the waiting period for genetic diseases or disorders?",
        "expected_status": "answered",
        "target_documents": ["policy", "cis"],
        "expected_page_numbers": [31, 8],
        "key_phrases": ["genetic", "waiting period"],
        "ground_truth_summary": "Genetic diseases are covered subject to standard pre-existing disease waiting periods (24 months) and IRDAI non-exclusion guidelines."
    },

    # -------------------------------------------------------------
    # Category 3: Exclusions & Restrictions (12 Questions)
    # -------------------------------------------------------------
    {
        "id": "Q28",
        "category": "exclusions_and_restrictions",
        "question": "What are the policy's exclusions?",
        "expected_status": "answered",
        "target_documents": ["policy", "cis"],
        "expected_page_numbers": [31, 5],
        "key_phrases": ["exclusion", "code excl"],
        "ground_truth_summary": "The policy details standardized exclusions Code Excl 01 to Excl 18 including investigation, cosmetic surgery, hazardous sports, and breach of law."
    },
    {
        "id": "Q29",
        "category": "exclusions_and_restrictions",
        "question": "Are diagnostic tests without inpatient hospitalization payable?",
        "expected_status": "answered",
        "target_documents": ["policy", "cis"],
        "expected_page_numbers": [31, 5],
        "key_phrases": ["investigation", "evaluation", "diagnostic", "excl 04"],
        "ground_truth_summary": "Hospitalization admission solely for investigation or diagnostic evaluation purposes is excluded under Code Excl 04."
    },
    {
        "id": "Q30",
        "category": "exclusions_and_restrictions",
        "question": "Is cosmetic surgery or plastic surgery covered under any circumstance?",
        "expected_status": "answered",
        "target_documents": ["policy", "cis"],
        "expected_page_numbers": [31, 5],
        "key_phrases": ["cosmetic", "plastic surgery", "excl 08"],
        "ground_truth_summary": "Cosmetic or plastic surgery is excluded under Code Excl 08 unless required reconstructively due to accidents, burns, or cancer."
    },
    {
        "id": "Q31",
        "category": "exclusions_and_restrictions",
        "question": "Are non-medical administrative charges like gloves and admission kits covered?",
        "expected_status": "answered",
        "target_documents": ["policy", "cis"],
        "expected_page_numbers": [48, 6],
        "key_phrases": ["non-medical", "registration", "admission kit", "gloves"],
        "ground_truth_summary": "Non-payable items listed in IRDAI guidelines (admission kit, documentation, registration fees, sanitary items) are excluded from reimbursement."
    },
    {
        "id": "Q32",
        "category": "exclusions_and_restrictions",
        "question": "Does the policy cover treatment for alcohol or substance abuse?",
        "expected_status": "answered",
        "target_documents": ["policy", "cis"],
        "expected_page_numbers": [32, 5],
        "key_phrases": ["alcohol", "substance abuse", "excl 12"],
        "ground_truth_summary": "Treatment for alcoholism, drug addiction, substance abuse, and their direct complications is excluded under Code Excl 12."
    },
    {
        "id": "Q33",
        "category": "exclusions_and_restrictions",
        "question": "Are treatments arising from participation in hazardous sports covered?",
        "expected_status": "answered",
        "target_documents": ["policy", "cis"],
        "expected_page_numbers": [32, 5],
        "key_phrases": ["hazardous sports", "scuba diving", "racing", "excl 09"],
        "ground_truth_summary": "Hospitalization resulting from professional hazardous sports (racing, parachuting, mountaineering) is excluded under Code Excl 09."
    },
    {
        "id": "Q34",
        "category": "exclusions_and_restrictions",
        "question": "Are dietary supplements and vitamins without illness diagnosis covered?",
        "expected_status": "answered",
        "target_documents": ["policy", "cis"],
        "expected_page_numbers": [32, 5],
        "key_phrases": ["dietary supplements", "vitamins", "excl 14"],
        "ground_truth_summary": "Dietary supplements, tonics, and vitamins not prescribed as part of treatment for active disease during inpatient stay are excluded under Code Excl 14."
    },
    {
        "id": "Q35",
        "category": "exclusions_and_restrictions",
        "question": "Does the policy cover gender reassignment or sex change surgery?",
        "expected_status": "answered",
        "target_documents": ["policy", "cis"],
        "expected_page_numbers": [31, 5],
        "key_phrases": ["gender reassignment", "sex change", "excl 07"],
        "ground_truth_summary": "Expenses incurred for change-of-gender treatments are excluded under Code Excl 07."
    },
    {
        "id": "Q36",
        "category": "exclusions_and_restrictions",
        "question": "Is routine outpatient dental treatment covered under base hospitalization?",
        "expected_status": "answered",
        "target_documents": ["policy", "cis"],
        "expected_page_numbers": [32, 5],
        "key_phrases": ["dental", "excl 11"],
        "ground_truth_summary": "Dental treatment or surgery that does not require hospitalization is excluded under Code Excl 11 unless required following accident."
    },
    {
        "id": "Q37",
        "category": "exclusions_and_restrictions",
        "question": "What is the policy regarding intentional self-inflicted injuries or suicide attempts?",
        "expected_status": "answered",
        "target_documents": ["policy", "cis"],
        "expected_page_numbers": [32, 5],
        "key_phrases": ["self-inflicted", "suicide", "excl 10"],
        "ground_truth_summary": "Expenses related to intentional self-inflicted injuries or attempted suicide are excluded under Code Excl 10."
    },
    {
        "id": "Q38",
        "category": "exclusions_and_restrictions",
        "question": "Are war, invasion, and nuclear contamination risks covered?",
        "expected_status": "answered",
        "target_documents": ["policy", "cis"],
        "expected_page_numbers": [32, 5],
        "key_phrases": ["war", "nuclear", "invasion"],
        "ground_truth_summary": "Losses directly or indirectly caused by war, civil commotion, radiation, or nuclear contamination are excluded."
    },
    {
        "id": "Q39",
        "category": "exclusions_and_restrictions",
        "question": "Is sleep apnea and snoring treatment covered or excluded?",
        "expected_status": "answered",
        "target_documents": ["policy", "cis"],
        "expected_page_numbers": [32, 5],
        "key_phrases": ["sleep apnea", "snoring", "excl 15"],
        "ground_truth_summary": "Treatment of sleep apnea disorders and corrective procedures for snoring are excluded under Code Excl 15."
    },

    # -------------------------------------------------------------
    # Category 4: Claims Procedures, Cashless & Regulatory (14 Questions)
    # -------------------------------------------------------------
    {
        "id": "Q40",
        "category": "claims_procedures_and_guidance",
        "question": "What is the procedure and timeline to intimate a planned cashless hospitalization?",
        "expected_status": "answered",
        "target_documents": ["claim_guidance", "cis"],
        "expected_page_numbers": [1, 14],
        "key_phrases": ["cashless", "48 hours", "pre-authorization"],
        "ground_truth_summary": "For planned hospitalization, pre-authorization must be submitted at least 48 hours prior to admission via the hospital insurance desk."
    },
    {
        "id": "Q41",
        "category": "claims_procedures_and_guidance",
        "question": "What is the notification window for an emergency cashless hospitalization?",
        "expected_status": "answered",
        "target_documents": ["claim_guidance", "cis"],
        "expected_page_numbers": [1, 14],
        "key_phrases": ["emergency", "24 hours", "cashless"],
        "ground_truth_summary": "For emergency admission, intimation and cashless request must be submitted within 24 hours of hospitalization."
    },
    {
        "id": "Q42",
        "category": "claims_procedures_and_guidance",
        "question": "Within how many days must reimbursement claim documents be submitted after discharge?",
        "expected_status": "answered",
        "target_documents": ["claim_guidance", "cis"],
        "expected_page_numbers": [1, 14],
        "key_phrases": ["reimbursement", "15 days", "30 days"],
        "ground_truth_summary": "Duly completed claim form and original bills must be submitted within 15 to 30 days from the date of hospital discharge."
    },
    {
        "id": "Q43",
        "category": "claims_procedures_and_guidance",
        "question": "What mandatory documents are required to support a reimbursement claim?",
        "expected_status": "answered",
        "target_documents": ["claim_guidance", "policy"],
        "expected_page_numbers": [1, 35],
        "key_phrases": ["discharge summary", "original bills", "receipts", "prescriptions"],
        "ground_truth_summary": "Discharge summary, original hospital bills with breakup, payment receipts, diagnostic test reports, and doctor prescriptions are mandatory."
    },
    {
        "id": "Q44",
        "category": "claims_procedures_and_guidance",
        "question": "How can policyholders check their claim status online?",
        "expected_status": "answered",
        "target_documents": ["claim_guidance"],
        "expected_page_numbers": [1],
        "key_phrases": ["claim status", "intimation number", "portal"],
        "ground_truth_summary": "Claim status can be tracked online on the insurer website or mobile application using claim intimation number or health card ID."
    },
    {
        "id": "Q45",
        "category": "claims_procedures_and_guidance",
        "question": "What grievance escalation mechanism exists if an insurer denies a claim unjustly?",
        "expected_status": "answered",
        "target_documents": ["faq", "cis"],
        "expected_page_numbers": [1, 16],
        "key_phrases": ["grievance", "gro", "irda", "bima bharosa"],
        "ground_truth_summary": "The policyholder can approach the Grievance Redressal Officer (GRO), escalate to IRDAI Bima Bharosa portal, or appeal to the Insurance Ombudsman."
    },
    {
        "id": "Q46",
        "category": "claims_procedures_and_guidance",
        "question": "What is the role and pecuniary jurisdiction limit of the Insurance Ombudsman?",
        "expected_status": "answered",
        "target_documents": ["faq", "policy"],
        "expected_page_numbers": [1, 47],
        "key_phrases": ["ombudsman", "30 lakhs", "jurisdiction"],
        "ground_truth_summary": "The Insurance Ombudsman adjudicates consumer insurance disputes for claims up to Rs. 30 lakhs within regional jurisdiction."
    },
    {
        "id": "Q47",
        "category": "claims_procedures_and_guidance",
        "question": "What is the free-look period duration for review of a newly issued health policy?",
        "expected_status": "answered",
        "target_documents": ["policy", "cis"],
        "expected_page_numbers": [38, 15],
        "key_phrases": ["free look", "15 days", "30 days"],
        "ground_truth_summary": "A free look period of 15 days (30 days for electronic or distance marketing policies) is allowed to cancel policy with refund minus proportionate risk premium."
    },
    {
        "id": "Q48",
        "category": "claims_procedures_and_guidance",
        "question": "What are the portability rules for porting to another insurer under IRDAI guidelines?",
        "expected_status": "answered",
        "target_documents": ["policy", "cis", "faq"],
        "expected_page_numbers": [40, 15],
        "key_phrases": ["portability", "45 days", "credit for waiting period"],
        "ground_truth_summary": "Portability requests must be initiated at least 45 days prior to renewal date, protecting accrued waiting period credits."
    },
    {
        "id": "Q49",
        "category": "claims_procedures_and_guidance",
        "question": "Does cashless approval guarantee that zero payment will be made at the hospital?",
        "expected_status": "answered",
        "target_documents": ["claim_guidance", "cis"],
        "expected_page_numbers": [1, 14],
        "key_phrases": ["non-payable", "co-payment", "settlement"],
        "ground_truth_summary": "Cashless pre-authorization covers admissible expenses; non-medical items, exclusions, co-payments, and expenses exceeding room limits must be paid by the patient."
    },
    {
        "id": "Q50",
        "category": "claims_procedures_and_guidance",
        "question": "What is the grace period allowed for policy renewal premium payment?",
        "expected_status": "answered",
        "target_documents": ["policy", "cis"],
        "expected_page_numbers": [37, 15],
        "key_phrases": ["grace period", "30 days"],
        "ground_truth_summary": "A grace period of 30 days is allowed for annual renewal to maintain continuity of benefits without loss of waiting period credits."
    },
    {
        "id": "Q51",
        "category": "claims_procedures_and_guidance",
        "question": "What happens if a cashless pre-authorization is denied by the insurer?",
        "expected_status": "answered",
        "target_documents": ["claim_guidance", "cis"],
        "expected_page_numbers": [1, 14],
        "key_phrases": ["denial of cashless", "reimbursement"],
        "ground_truth_summary": "Denial of cashless access does not mean claim is rejected; the insured person can pay hospital directly and file for reimbursement post-discharge."
    },
    {
        "id": "Q52",
        "category": "claims_procedures_and_guidance",
        "question": "What is the timeline for the insurer to settle or reject a reimbursement claim?",
        "expected_status": "answered",
        "target_documents": ["policy", "faq"],
        "expected_page_numbers": [36, 1],
        "key_phrases": ["30 days", "settlement timeline", "interest"],
        "ground_truth_summary": "Insurers must settle or reject a claim within 30 days of receiving all necessary documents; delayed payment attracts penal interest at 2% above bank rate."
    },
    {
        "id": "Q53",
        "category": "claims_procedures_and_guidance",
        "question": "Can a policy be terminated for fraud or intentional non-disclosure of medical facts?",
        "expected_status": "answered",
        "target_documents": ["policy", "cis"],
        "expected_page_numbers": [37, 15],
        "key_phrases": ["fraud", "misrepresentation", "cancellation"],
        "ground_truth_summary": "The policy may be cancelled ab initio on grounds of fraud, moral hazard, or material misrepresentation with forfeiture of premium paid."
    },

    # -------------------------------------------------------------
    # Category 5: Out-of-Domain & Adversarial Negative Controls (12 Questions)
    # -------------------------------------------------------------
    {
        "id": "Q54",
        "category": "out_of_domain_and_adversarial",
        "question": "Does this health insurance policy cover orbital space flight planetary excursions?",
        "expected_status": "insufficient_evidence",
        "target_documents": [],
        "expected_page_numbers": [],
        "key_phrases": ["orbital", "space flight"],
        "ground_truth_summary": "Out of domain. System must abstain cleanly with insufficient evidence."
    },
    {
        "id": "Q55",
        "category": "out_of_domain_and_adversarial",
        "question": "How do I bake sourdough bread at high altitude with active starter?",
        "expected_status": "insufficient_evidence",
        "target_documents": [],
        "expected_page_numbers": [],
        "key_phrases": ["sourdough", "bread"],
        "ground_truth_summary": "Out of domain. System must abstain cleanly."
    },
    {
        "id": "Q56",
        "category": "out_of_domain_and_adversarial",
        "question": "What is the compensation payout for car collision bumper damage and windshield replacement?",
        "expected_status": "insufficient_evidence",
        "target_documents": [],
        "expected_page_numbers": [],
        "key_phrases": ["bumper", "windshield", "car collision"],
        "ground_truth_summary": "Motor insurance query. Out of domain for health policy; system must abstain."
    },
    {
        "id": "Q57",
        "category": "out_of_domain_and_adversarial",
        "question": "Does this health policy reimburse losses from cryptocurrency market crashes or Bitcoin theft?",
        "expected_status": "insufficient_evidence",
        "target_documents": [],
        "expected_page_numbers": [],
        "key_phrases": ["cryptocurrency", "bitcoin"],
        "ground_truth_summary": "Financial asset query. Out of domain; system must abstain."
    },
    {
        "id": "Q58",
        "category": "out_of_domain_and_adversarial",
        "question": "What veterinary surgeries and dog vaccination treatments are covered for domestic pets?",
        "expected_status": "insufficient_evidence",
        "target_documents": [],
        "expected_page_numbers": [],
        "key_phrases": ["veterinary", "dog", "pets"],
        "ground_truth_summary": "Pet insurance query. Out of domain; system must abstain."
    },
    {
        "id": "Q59",
        "category": "out_of_domain_and_adversarial",
        "question": "How do I calculate income tax exemptions under Section 80C for life insurance endowment policies?",
        "expected_status": "insufficient_evidence",
        "target_documents": [],
        "expected_page_numbers": [],
        "key_phrases": ["section 80c", "life insurance", "endowment"],
        "ground_truth_summary": "Tax / Life insurance query. Policy corpus covers health terms; system must abstain."
    },
    {
        "id": "Q60",
        "category": "out_of_domain_and_adversarial",
        "question": "Does the policy cover airline flight cancellation compensations and lost luggage abroad?",
        "expected_status": "insufficient_evidence",
        "target_documents": [],
        "expected_page_numbers": [],
        "key_phrases": ["flight cancellation", "lost luggage"],
        "ground_truth_summary": "Travel insurance query. Out of domain; system must abstain."
    },
    {
        "id": "Q61",
        "category": "out_of_domain_and_adversarial",
        "question": "What is the waiting period for cosmetic tooth whitening and porcelain dental veneer fitting?",
        "expected_status": "insufficient_evidence",
        "target_documents": [],
        "expected_page_numbers": [],
        "key_phrases": ["tooth whitening", "porcelain veneer"],
        "ground_truth_summary": "Cosmetic dental query not recognized as covered clinical procedure; system must abstain."
    },
    {
        "id": "Q62",
        "category": "out_of_domain_and_adversarial",
        "question": "Is home burglary and jewelry theft reimbursed under the comprehensive health plan?",
        "expected_status": "insufficient_evidence",
        "target_documents": [],
        "expected_page_numbers": [],
        "key_phrases": ["burglary", "jewelry theft"],
        "ground_truth_summary": "Property insurance query. Out of domain; system must abstain."
    },
    {
        "id": "Q63",
        "category": "out_of_domain_and_adversarial",
        "question": "How do I configure quantum computing qubits for financial derivative portfolio hedging?",
        "expected_status": "insufficient_evidence",
        "target_documents": [],
        "expected_page_numbers": [],
        "key_phrases": ["quantum computing", "qubits"],
        "ground_truth_summary": "Out of domain. System must abstain."
    },
    {
        "id": "Q64",
        "category": "out_of_domain_and_adversarial",
        "question": "Can I claim health insurance reimbursement for purchasing organic grocery store vegetables?",
        "expected_status": "insufficient_evidence",
        "target_documents": [],
        "expected_page_numbers": [],
        "key_phrases": ["organic grocery", "vegetables"],
        "ground_truth_summary": "Absurd / out-of-scope query. System must abstain."
    },
    {
        "id": "Q65",
        "category": "out_of_domain_and_adversarial",
        "question": "What is the maximum reimbursement for cyber hacking ransom payments on smart home devices?",
        "expected_status": "insufficient_evidence",
        "target_documents": [],
        "expected_page_numbers": [],
        "key_phrases": ["cyber hacking", "ransom payments"],
        "ground_truth_summary": "Cyber insurance query. Out of domain; system must abstain."
    }
]

out_path = Path("data/evaluation/benchmark_qa_60.json")
out_path.parent.mkdir(parents=True, exist_ok=True)
with open(out_path, "w", encoding="utf-8") as f:
    json.dump(benchmark_data, f, indent=2)

print(f"Successfully generated {len(benchmark_data)} benchmark items to {out_path.resolve()}")

