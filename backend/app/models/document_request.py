from pydantic import BaseModel, Field



class DocumentUploadRequest(BaseModel):

    file_name: str = Field(min_length=1, max_length=255)

    file_size: int = Field(gt=0, le=10_000_000)

    file_type: str = Field(pattern=r"^(pdf|txt)$")