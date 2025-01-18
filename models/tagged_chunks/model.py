from pydantic import BaseModel, Field

class TaggedChunk(BaseModel):
    source: str = Field(description="source document")
    source_ingestor: str = Field(description="source ingestor")
    chunk_type: str = Field(description="chunk type")
    text: str = Field(description="text")

