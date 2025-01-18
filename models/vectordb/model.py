from pydantic import BaseModel, Field


class VectorDBConfiguration(BaseModel):
    name: str = Field(description="name of the vector db")