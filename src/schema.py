from pydantic import BaseModel
from typing import List, Optional



class Chunk(BaseModel):
    chunk_id: int
    text: str
    embedding: Optional[List[float]] = None
    chunk_size: int=1000
    chunk_overlap: int=100
    embeddings_model: Optional[str] = None


class ProcessedDocument(BaseModel):
    filename: str = ""
    source: str= ""
    document_version: int = 1
    metadata: Optional[dict] = None
    chunks: Optional[List[Chunk]] = None
