
from pydantic import BaseModel, Field


class DocumentUploadRequest(BaseModel):
    file_name: str = Field(min_length=1, max_length=255)
    file_type: str = Field(pattern=r"^(pdf|txt)$")
    file_size: int = Field(gt=0)


class DocumentUploadResponse(BaseModel):
    document_id: str
    file_name: str
    status: str


class ExternalPostResponse(BaseModel):
    userId: int
    id: int
    title: str
    body: str
