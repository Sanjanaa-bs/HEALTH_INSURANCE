from typing import Generator
from sqlalchemy import create_engine, event
from sqlalchemy.orm import declarative_base, sessionmaker, Session
from backend.app.config import settings

# Configure SQLite connection arguments
connect_args = {}
if settings.DATABASE_URL.startswith("sqlite"):
    connect_args["check_same_thread"] = False

engine = create_engine(
    settings.DATABASE_URL,
    connect_args=connect_args,
    echo=False,
)

# Enable foreign key constraints in SQLite
if settings.DATABASE_URL.startswith("sqlite"):
    @event.listens_for(engine, "connect")
    def set_sqlite_pragma(dbapi_connection, connection_record):
        cursor = dbapi_connection.cursor()
        cursor.execute("PRAGMA foreign_keys=ON")
        cursor.close()

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()


def get_db() -> Generator[Session, None, None]:
    """FastAPI dependency that yields a database session."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def init_db() -> None:
    """Create all database tables based on registered SQLAlchemy models."""
    # Ensure all models are imported before creating tables
    import backend.app.models  # noqa: F401
    Base.metadata.create_all(bind=engine)


def ensure_hospital_data_loaded() -> None:
    """Check if hospital directory records exist; if database is empty, load from configured dataset paths."""
    import sys
    import os
    from pathlib import Path
    import logging

    logger = logging.getLogger("hospital_loader")

    # Do not auto-ingest during unit testing or when running under pytest
    if "pytest" in sys.modules or os.environ.get("PYTEST_CURRENT_TEST") or settings.APP_ENV == "testing":
        return

    from backend.app.models.hospital import Hospital, InsurerHospitalRecord
    db = SessionLocal()
    try:
        hospital_count = db.query(Hospital).count()
        if hospital_count == 0:
            csv_path = Path(settings.HOSPITALS_CSV_PATH)
            if csv_path.exists():
                logger.info(f"Hospital directory table is empty. Ingesting from {csv_path}...")
                from scripts.ingest_hospitals import ingest_hospital_csv
                ingest_hospital_csv(csv_path=str(csv_path), db=db)
            else:
                logger.warning(f"Hospital directory CSV not found at {csv_path}")

        insurer_count = db.query(InsurerHospitalRecord).count()
        if insurer_count == 0:
            networks_dir = Path(settings.INSURER_NETWORKS_DIR)
            if networks_dir.exists():
                logger.info(f"Insurer network table is empty. Ingesting from {networks_dir}...")
                from scripts.ingest_insurer_networks import ingest_insurer_networks
                ingest_insurer_networks(dir_path=str(networks_dir), db=db)
    except Exception as e:
        logger.error(f"Error ensuring hospital data is loaded: {e}")
    finally:
        db.close()


def ensure_vector_index_consistent() -> None:
    """Align the persisted vector index with the chunk IDs in the local database."""
    import sys
    import os
    import logging

    logger = logging.getLogger("vector_index")

    if "pytest" in sys.modules or os.environ.get("PYTEST_CURRENT_TEST") or settings.APP_ENV == "testing":
        return

    from backend.app.services.vector_store import vector_store_instance

    db = SessionLocal()
    try:
        outcome = vector_store_instance.reconcile_with_database(db)
        logger.info(f"Vector index {outcome}: {len(vector_store_instance.vectors)} embeddings.")
    except Exception as e:
        logger.error(f"Error reconciling vector index with database: {e}")
    finally:
        db.close()
