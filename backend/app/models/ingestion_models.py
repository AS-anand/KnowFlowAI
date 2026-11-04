from pydantic import BaseModel


class IngestionResponse(BaseModel):
    document_id: str
    file_name: str
    total_pages: int
    chunks_indexed: int
    message: str