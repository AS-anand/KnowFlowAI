from pydantic import BaseModel, Field


class DocumentChunk(BaseModel):
    chunk_index: int = Field(ge=0)
    document_id: str
    file_name: str
    page_number: int = Field(ge=1)
    content: str = Field(min_length=1)