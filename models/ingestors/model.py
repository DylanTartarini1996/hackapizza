from pydantic import BaseModel, Field, field_validator
import os

class IngestorConfiguration(BaseModel):
    src_directory: str = Field(description="source directory containing the files to ingest")
    type: str = Field(description="type of ingestor")

    @field_validator("type")
    def type_validator(self, x):
        assert x in ["pdf", "docx", "vision", "csv", "html"]
        return x

    @field_validator("src_directory")
    def src_validator(self, x):
        assert os.path.exists(x)
        assert os.path.isdir(x)
        return x
