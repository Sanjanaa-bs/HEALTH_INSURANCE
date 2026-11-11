import json
import sqlite3
from pathlib import Path

conn = sqlite3.connect("health_insurance.db")
c = conn.cursor()

# Query real facilities from diverse states/cities to construct a 125-record multi-city network dataset
records = []

queries = [
    # (city, state, limit)
    ("Bengaluru", "Karnataka", 25),
    ("Mumbai", "Maharashtra", 20),
    ("Pune", "Maharashtra", 15),
    ("Chennai", "Tamil Nadu", 20),
    ("Hyderabad", "Telangana", 15),
    ("Kolkata", "West Bengal", 10),
    ("Ahmedabad", "Gujarat", 10),
    ("Lucknow", "Uttar Pradesh", 5),
    ("Jaipur", "Rajasthan", 5),
]

ins_id = 1
for city, state, limit in queries:
    c.execute(
        """
        SELECT id, hospital_name, address, state, district, pincode, total_beds
        FROM hospitals
        WHERE state = ? AND (district LIKE ? OR address LIKE ?)
        LIMIT ?
        """,
        (state, f"%{city}%", f"%{city}%", limit)
    )
    rows = c.fetchall()
    
    # If district didn't match enough, just fetch from the state
    if len(rows) < limit:
        needed = limit - len(rows)
        existing_ids = tuple(r[0] for r in rows) if rows else (-1,)
        c.execute(
            f"""
            SELECT id, hospital_name, address, state, district, pincode, total_beds
            FROM hospitals
            WHERE state = ? AND id NOT IN {existing_ids}
            LIMIT ?
            """,
            (state, needed)
        )
        rows.extend(c.fetchall())

    for idx, r in enumerate(rows):
        hid, hname, addr, st, dist, pin, beds = r
        # 80% linked with matched_hospital_id, 20% trade name variant or unlinked to test matching
        is_linked = (idx % 5 != 0)
        rec = {
            "id": ins_id,
            "insurer_name": "Star Health",
            "hospital_name": hname.upper() if idx % 2 == 0 else hname,
            "city": city,
            "district": dist or city,
            "state": state,
            "pincode": pin or "560001",
            "address": addr or f"{city}, {state}",
            "network_type": "Cashless Network",
            "total_beds": beds or 50,
            "matched_hospital_id": hid if is_linked else None,
            "target_hospital_name": hname,
            "target_hospital_id": hid
        }
        records.append(rec)
        ins_id += 1

conn.close()

out_path = Path("data/insurer_networks/expanded_insurer_network_sample.json")
out_path.parent.mkdir(parents=True, exist_ok=True)
with open(out_path, "w", encoding="utf-8") as f:
    json.dump(records, f, indent=2)

print(f"Generated {len(records)} multi-city insurer network records across 9 urban centres.")

