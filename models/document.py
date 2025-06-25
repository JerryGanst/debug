import uuid
from datetime import datetime
from enum import Enum
from typing import Optional, List

from pydantic import BaseModel, Field


class FileType(str, Enum):
    PDF = "pdf"
    DOC = "doc"
    DOCX = "docx"
    PPT = "ppt"
    PPTX = "pptx"
    TXT = "txt"
    MD = "md"
    CSV = "csv"
    XLSX = "xlsx"


class DocumentType(str, Enum):
    HR_INFOS = "HR Infos"
    IT = "IT"
    RND_DOCS = "R&D Docs"
    FINANCIAL_REPORT = "Financial Report"
    LEGAL = "Legal"
    OTHER = "Other"


class Document(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()), alias="id")
    title: str
    file_type: FileType
    doc_type: DocumentType
    publish_date: Optional[datetime] = None
    author: Optional[str] = None
    file_path: str
    pages: Optional[int] = None
    file_size: Optional[int] = None  # In bytes
    language: Optional[str] = None  # e.g., "en", "zh", "fr"
    abstract: Optional[str] = None
    abstract_embedding: Optional[List[float]] = None
    processed_to_pages: bool = False

    keywords: Optional[List[str]] = []
    outdated: bool = False

    class Config:
        use_enum_values = True


class DocumentMetaData(BaseModel):
    title: str
    publish_date: Optional[datetime] = None
    author: Optional[str] = None
    keywords: Optional[List[str]] = []
    outdated: bool = False


class Page(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()), alias="id")
    document_id: str
    page_num: int
    page_text: Optional[str] = None
    word_count: Optional[int] = None
    overlap_words_count: Optional[int] = None  # Number of words at the start that are from the previous page
    abstract: Optional[str] = None
    abstract_embedding: Optional[List[float]] = None
    chunked: bool = False

    class Config:
        use_enum_values = True


class Chunk(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()), alias="id")
    page_id: str
    document_id: str  # Directly store document_id for quick lookups
    page_num: int  # Directly store page_num for traceability
    chunk_doc_type: DocumentType
    chunk_doc_publish_date: Optional[datetime] = None
    chunk_size: int = 100
    overlap_words_count: int = 0  # Number of words at the start that overlap with the previous chunk

    chunk_text: str
    chunk_embedding: Optional[List[float]] = None

    class Config:
        use_enum_values = True
