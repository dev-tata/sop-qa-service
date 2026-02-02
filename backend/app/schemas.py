from __future__ import annotations
from pydantic import BaseModel, Field
from typing import List, Optional

class BuildRequest(BaseModel):
    pdf_path: str = Field(..., description="Path to PDF file")
    persist: bool = Field(default=True, description="Save index+metadata to data/index")

class SearchRequest(BaseModel):
    query: str
    keywords: Optional[List[str]] = None
    top_k: int = 5
    pool_k: int = 25

class QARequest(BaseModel):
    question: str
    top_k: int = 5

class ChunkResponse(BaseModel):
    chunk_id: str
    section_title: str
    text: str
    page_start: int
    page_end: int
    keywords: Optional[List[str]] = None
    source_file: Optional[str] = None
    section_id: Optional[str] = None
