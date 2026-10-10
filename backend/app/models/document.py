from sqlalchemy import (
    Column,
    Integer,
    String,
    Text,
    Boolean,
    DateTime,
    ForeignKey,
    UniqueConstraint,
    func,
)
from sqlalchemy.orm import relationship
from backend.app.database import Base


class Document(Base):
    """Source policy documents, guidance sheets, and FAQs."""

    __tablename__ = "documents"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    title = Column(String(255), nullable=False, index=True)
    document_type = Column(String(50), nullable=False, index=True)  # policy, cis, claim_guidance, faq
    source_path = Column(String(500), nullable=False, unique=True)
    file_format = Column(String(20), nullable=False)  # pdf, html, mhtml
    file_size_bytes = Column(Integer, nullable=True)
    version = Column(String(50), nullable=True)
    metadata_json = Column(Text, nullable=True)
    is_processed = Column(Boolean, default=False, nullable=False, index=True)

    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)

    # Chunks associated with this document
    chunks = relationship(
        "DocumentChunk",
        back_populates="document",
        cascade="all, delete-orphan",
        order_by="DocumentChunk.chunk_index",
    )


class DocumentChunk(Base):
    """Parsed and chunked text sections for vector embedding and retrieval."""

    __tablename__ = "document_chunks"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    document_id = Column(
        Integer,
        ForeignKey("documents.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    text = Column(Text, nullable=False)
    page_number = Column(Integer, nullable=True)
    section_heading = Column(String(255), nullable=True)
    chunk_index = Column(Integer, nullable=False)
    content_hash = Column(String(64), nullable=False, index=True)
    token_count = Column(Integer, nullable=True)

    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)

    # Ensure chunk ordering uniqueness per document
    __table_args__ = (
        UniqueConstraint("document_id", "chunk_index", name="uq_doc_chunk_index"),
    )

    document = relationship("Document", back_populates="chunks")
