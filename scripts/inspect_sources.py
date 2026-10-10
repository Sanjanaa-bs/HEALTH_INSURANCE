import re
import json
from pathlib import Path
from bs4 import BeautifulSoup
import email
from email import policy
import pypdf

def inspect_insurer_network():
    print("=== INSPECTING INSURER NETWORKS ===")
    html_path = Path("data/insurer_networks/Star Health Network Hospitals List in Bangalore _ Cashless Hospitals in Bangalore.htm")
    mhtml_path = Path("data/insurer_networks/Star Health Network Hospitals List in Bangalore _ Cashless Hospitals in Bangalore.mhtml")

    for p in [html_path, mhtml_path]:
        print(f"\nFile: {p.name} (Size: {p.stat().st_size} bytes)")
        if p.suffix == ".htm":
            with open(p, "r", encoding="utf-8", errors="replace") as f:
                soup = BeautifulSoup(f.read(), "html.parser")
                text = soup.get_text()
                print("HTML title:", soup.title.string if soup.title else None)
                # Check for hospital cards or specific keywords
                hospitals_found = set()
                # Search for hospital patterns
                for match in re.finditer(r'([A-Za-z0-9\s,.-]+(?:Hospital|Healthcare|Nursing Home|Medical Centre|Clinic))', text):
                    name = match.group(1).strip()
                    if len(name) > 5 and len(name) < 80 and not any(skip in name.lower() for skip in ['what is', 'benefits', 'network', 'find']):
                        hospitals_found.add(name)
                print(f"Extracted hospital mentions in HTML text: {len(hospitals_found)}")
                print("Samples:", list(hospitals_found)[:5])

        elif p.suffix == ".mhtml":
            with open(p, "rb") as f:
                msg = email.message_from_binary_file(f, policy=policy.default)
                print("MHTML Subject:", msg["Subject"])
                print("MHTML Snapshot-Content-Location:", msg["Snapshot-Content-Location"])
                parts = list(msg.iter_parts())
                print(f"MHTML parts count: {len(parts)}")

def inspect_policies():
    print("\n=== INSPECTING POLICIES ===")
    policy_dir = Path("data/policies")
    for pdf_file in policy_dir.glob("*.pdf"):
        print(f"\nPDF: {pdf_file.name} ({pdf_file.stat().st_size} bytes)")
        try:
            reader = pypdf.PdfReader(str(pdf_file))
            print(f"Pages: {len(reader.pages)}")
            page1_text = reader.pages[0].extract_text()
            print("Page 1 excerpt:", repr(page1_text[:200]))
        except Exception as e:
            print("Error reading PDF:", e)

def inspect_claim_guidance():
    print("\n=== INSPECTING CLAIM GUIDANCE ===")
    cg_dir = Path("data/claim_guidance")
    for mhtml_file in cg_dir.glob("*.mhtml"):
        print(f"\nMHTML: {mhtml_file.name} ({mhtml_file.stat().st_size} bytes)")
        try:
            with open(mhtml_file, "rb") as f:
                msg = email.message_from_binary_file(f, policy=policy.default)
                print("Subject:", msg["Subject"])
                print("Location:", msg["Snapshot-Content-Location"])
                body_part = msg.get_body(preferencelist=('html', 'plain'))
                if body_part:
                    content = body_part.get_content()
                    soup = BeautifulSoup(content, "html.parser")
                    text = soup.get_text()
                    print("Extracted text length:", len(text))
                    print("Sample text:", repr(text[:150].strip()))
                else:
                    print("No html/plain body part found directly")
        except Exception as e:
            print("Error reading MHTML:", e)

if __name__ == "__main__":
    inspect_insurer_network()
    inspect_policies()
    inspect_claim_guidance()
