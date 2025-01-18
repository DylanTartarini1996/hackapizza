from pydantic import BaseModel
from typing import List, Optional


class Chunk(BaseModel):
    id: str
    filename: str
    text: str
    embedding: Optional[List[float]] = None
    embeddings_model: Optional[str] = None