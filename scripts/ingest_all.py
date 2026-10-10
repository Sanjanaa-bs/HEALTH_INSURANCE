import logging
import sys
from pathlib import Path
from datetime import datetime

# Ensure project root is in sys.path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from sqlalchemy.orm import Session

from backend.app.database import SessionLocal, init_db
from backend.app.search import sync_fts5_index
from scripts.ingest_hospitals import ingest_hospital_csv
from scripts.ingest_insurer_networks import ingest_insurer_networks
from scripts.ingest_policies import ingest_policy_pdfs
from scripts.ingest_claim_guidance import ingest_claim_guidance_mhtml

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger("ingest_pipeline")


def run_full_pipeline() -> dict:
    """Execute complete dataset ingestion pipeline across all data directories."""
    logger.info("Initializing database tables...")
    init_db()

    start_time = datetime.now()
    results = {}

    db: Session = SessionLocal()
    try:
        # Step 1: Government Hospital Directory CSV
        logger.info("--- Step 1: Ingesting Government Hospital Directory CSV ---")
        results["hospitals"] = ingest_hospital_csv(
            csv_path="data/hospitals/hospital_directory.csv",
            db=db,
            batch_size=2000,
        )

        # Step 2: Insurer Network Hospital Webpages
        logger.info("--- Step 2: Ingesting Star Health Insurer Network Webpages ---")
        results["insurer_networks"] = ingest_insurer_networks(
            dir_path="data/insurer_networks",
            db=db,
        )

        # Step 3: Policy PDFs
        logger.info("--- Step 3: Ingesting Policy Wording & CIS PDFs ---")
        results["policies"] = ingest_policy_pdfs(
            policy_dir="data/policies",
            db=db,
        )

        # Step 4: Claim Guidance MHTML
        logger.info("--- Step 4: Ingesting Claim Guidance & IRDAI FAQ MHTML ---")
        results["claim_guidance"] = ingest_claim_guidance_mhtml(
            guidance_dir="data/claim_guidance",
            db=db,
        )

        # Step 5: Full-Text Search (FTS5) Indexing
        logger.info("--- Step 5: Synchronizing SQLite FTS5 Search Index ---")
        indexed_chunks = sync_fts5_index(db=db)
        results["fts5_search_index"] = {"indexed_chunks": indexed_chunks}

    finally:
        db.close()

    elapsed = (datetime.now() - start_time).total_seconds()
    results["elapsed_seconds"] = elapsed

    print("\n" + "=" * 60)
    print("      DATASET INGESTION PIPELINE EXECUTION SUMMARY")
    print("=" * 60)
    print(f"Hospital Directory CSV: {results['hospitals']['imported_records']} imported / {results['hospitals']['source_rows']} read")
    print(f"Insurer Network Hospitals: {results['insurer_networks']['imported_records']} imported ({results['insurer_networks']['matched_directory_hospitals']} linked to directory)")
    print(f"Policy PDFs: {results['policies']['total_chunks_indexed']} chunks indexed from {results['policies']['files_scanned']} files")
    print(f"Claim Guidance MHTML: {results['claim_guidance']['total_chunks_indexed']} chunks indexed from {results['claim_guidance']['files_scanned']} files")
    print(f"FTS5 Search Index: {results['fts5_search_index']['indexed_chunks']} retrievable passages indexed")
    print(f"Total Pipeline Runtime: {elapsed:.2f} seconds")
    print("=" * 60 + "\n")

    return results


if __name__ == "__main__":
    run_full_pipeline()
