import zlib
import re
from pathlib import Path
import pymupdf
import pypdf

pdf_path = Path("data/policies/Policy_Star_Comprehensive_Insurance_Policy_V_21_3a414ab104.pdf")

def diagnose():
    print(f"=== PDF DIAGNOSTIC: {pdf_path.name} ===")
    print(f"File Size: {pdf_path.stat().st_size} bytes")

    # 1. PyMuPDF Repair / Clean attempt
    doc = pymupdf.open(str(pdf_path))
    print(f"Total Pages: {len(doc)}")
    print(f"Encryption: {doc.is_encrypted}")

    # Attempt to clean & repair into a temporary byte stream
    try:
        repaired_bytes = doc.tobytes(clean=True, deflate=True, garbage=4)
        print(f"Repaired PDF byte size: {len(repaired_bytes)} bytes")
        repaired_doc = pymupdf.open("pdf", repaired_bytes)
        print("Successfully opened repaired PDF with PyMuPDF!")
        
        extracted_pages = 0
        total_text = ""
        for i, page in enumerate(repaired_doc):
            txt = page.get_text()
            if txt.strip():
                extracted_pages += 1
                total_text += txt + "\n"
                if i < 5:
                    print(f"  Page {i+1} Repaired Text ({len(txt)} chars): {repr(txt[:100].strip())}")
        
        print(f"Repaired Doc Extraction Summary: {extracted_pages}/{len(repaired_doc)} pages extracted, {len(total_text)} total chars")
    except Exception as e:
        print(f"Repaired PDF attempt error: {e}")

    # 2. Inspect raw objects and streams
    with open(pdf_path, "rb") as f:
        raw_bytes = f.read()

    # Search for stream objects and test raw zlib decompression with various wbits
    stream_matches = [m.start() for m in re.finditer(b"stream", raw_bytes)]
    print(f"\nRaw PDF contains {len(stream_matches)} stream keywords.")

    decompressed_streams = 0
    decompressed_text_snippets = []

    for idx, pos in enumerate(stream_matches[:50]):
        # Find stream data after 'stream\r\n' or 'stream\n'
        stream_start = pos + 6
        if raw_bytes[stream_start:stream_start+2] == b"\r\n":
            stream_start += 2
        elif raw_bytes[stream_start:stream_start+1] == b"\n":
            stream_start += 1
        
        end_pos = raw_bytes.find(b"endstream", stream_start)
        if end_pos == -1:
            continue
        
        stream_data = raw_bytes[stream_start:end_pos].rstrip(b"\r\n")

        # Test zlib decompression modes
        decomp = None
        for wbits in [zlib.MAX_WBITS, -zlib.MAX_WBITS, zlib.MAX_WBITS | 32, 15, -15]:
            try:
                decomp = zlib.decompress(stream_data, wbits)
                if decomp:
                    break
            except Exception:
                pass

        if decomp:
            decompressed_streams += 1
            # Check if stream contains readable text
            try:
                decoded = decomp.decode("utf-8", errors="ignore")
                # Look for font strings or text operators like TJ / Tj / BT / ET
                if "BT" in decoded and "ET" in decoded:
                    text_matches = re.findall(r"\(([^()]+)\)\s*T[jJ]", decoded)
                    if text_matches:
                        snippet = " ".join(text_matches)
                        if len(snippet.strip()) > 10:
                            decompressed_text_snippets.append(snippet)
            except Exception:
                pass

    print(f"Successfully decompressed {decompressed_streams}/{len(stream_matches)} raw streams.")
    print(f"Found {len(decompressed_text_snippets)} stream text snippets.")
    if decompressed_text_snippets:
        print("Sample raw text snippets:", decompressed_text_snippets[:5])

if __name__ == "__main__":
    diagnose()
