import sqlite3
import sys
from pathlib import Path

# Ensure project root is in sys.path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from backend.app.config import settings

def verify_database():
    db_path = settings.DATABASE_URL.replace("sqlite:///", "")
    print(f"=== DATABASE VERIFICATION ===")
    print(f"Configured DATABASE_URL: {settings.DATABASE_URL}")
    print(f"Target DB File Path: {db_path} (Exists: {Path(db_path).exists()})")
    
    if not Path(db_path).exists():
        print("Database file does not exist yet!")
        return

    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
    tables = [row[0] for row in cursor.fetchall() if not row[0].startswith('sqlite_')]
    print(f"Discovered Tables ({len(tables)}): {tables}\n")

    counts = {}
    for t in sorted(tables):
        cursor.execute(f"SELECT COUNT(*) FROM {t};")
        cnt = cursor.fetchone()[0]
        counts[t] = cnt
        print(f"  • Table '{t}': {cnt:,} records")

    print("\n--- Document Table Details ---")
    if "documents" in tables:
        cursor.execute("SELECT id, title, document_type, file_format, is_processed, created_at FROM documents;")
        docs = cursor.fetchall()
        for d in docs:
            print(f"  [ID {d[0]}] {d[1]} ({d[2]}, {d[3]}) - Processed: {d[4]}")

    print("\n--- Sample Insurer Network Records ---")
    if "insurer_hospital_records" in tables:
        cursor.execute("SELECT id, insurer_name, hospital_name, city, matched_hospital_id FROM insurer_hospital_records LIMIT 5;")
        recs = cursor.fetchall()
        for r in recs:
            print(f"  [ID {r[0]}] {r[1]} - {r[2]} ({r[3]}) -> Matched Directory ID: {r[4]}")

    conn.close()

if __name__ == "__main__":
    verify_database()
