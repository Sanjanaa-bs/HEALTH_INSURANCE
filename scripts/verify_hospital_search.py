import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from fastapi.testclient import TestClient
from backend.app.main import app

client = TestClient(app)

print("=== TEST 1: Default browse (page 1) ===")
res1 = client.get("/api/v1/hospitals?page=1&page_size=3")
assert res1.status_code == 200
items1 = res1.json()["items"]
for it in items1:
    print(f"[{it['id']}] {it['hospital_name']} ({it['district']}, {it['state']}) -> {it['network_status']} ({it['network_status_code']}): {it['network_status_explanation']}")
assert items1[0]["network_status_code"] == "UNVERIFIED"
assert "The available Star Health dataset contains only a limited Bengaluru sample" in items1[0]["network_status_explanation"]

print("\n=== TEST 2: Bengaluru search (location=Bengaluru) ===")
res2 = client.get("/api/v1/hospitals?location=Bengaluru&page_size=5")
assert res2.status_code == 200
items2 = res2.json()["items"]
for it in items2:
    print(f"[{it['id']}] {it['hospital_name']} ({it['district']}) -> {it['network_status']} ({it['network_status_code']})")
    assert "Andaman" not in (it["district"] or "")
    assert "Andaman" not in (it["state"] or "")

print("\n=== TEST 3: Matched facility (Bangalore Baptist Hospital) ===")
res3 = client.get("/api/v1/hospitals?search=Bangalore Baptist Hospital")
assert res3.status_code == 200
items3 = res3.json()["items"]
assert len(items3) >= 1
print(f"[{items3[0]['id']}] {items3[0]['hospital_name']} -> {items3[0]['network_status']} ({items3[0]['network_status_code']}): {items3[0]['network_status_explanation']}")
assert items3[0]["network_status_code"] == "LISTED"

print("\n=== TEST 4: Bengaluru facility absent from insurer sample (Abhishek Nethradhama) ===")
res4 = client.get("/api/v1/hospitals?search=Abhishek Nethradhama")
assert res4.status_code == 200
items4 = res4.json()["items"]
assert len(items4) >= 1
print(f"[{items4[0]['id']}] {items4[0]['hospital_name']} -> {items4[0]['network_status']} ({items4[0]['network_status_code']}): {items4[0]['network_status_explanation']}")
assert items4[0]["network_status_code"] == "NOT_FOUND"

print("\n=== TEST 5: Out-of-sample Karnataka facility (Kerudi Hospital And Research Centre, Bagalkot) ===")
res5 = client.get("/api/v1/hospitals?search=kerudi")
assert res5.status_code == 200
items5 = res5.json()["items"]
assert len(items5) >= 1
print(f"[{items5[0]['id']}] {items5[0]['hospital_name']} ({items5[0]['district']}, {items5[0]['pincode']}) -> {items5[0]['network_status']} ({items5[0]['network_status_code']}): {items5[0]['network_status_explanation']}")
assert items5[0]["hospital_name"] == "Kerudi Hospital And Research Centre"
assert items5[0]["district"] == "Bagalkot"
assert items5[0]["pincode"] == "587101"
assert items5[0]["network_status"] == "Network status unverified"
assert items5[0]["network_status_code"] == "UNVERIFIED"
expected_expl = (
    "The available Star Health dataset contains only a limited Bengaluru sample. "
    "This hospital's network status cannot be confirmed using the available data. "
    "Please verify with Star Health before planning cashless treatment."
)
assert items5[0]["network_status_explanation"] == expected_expl

print("\n=== ALL LIVE DATABASE CHECKS PASSED SUCCESSFULLY! ===")
