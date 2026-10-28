
from pydantic import BaseModel, Field


class ParsedPage(BaseModel):
    document_id: str
    file_name: str
    page_number: int = Field(ge=1)
    content: str


class ParsedDocument(BaseModel):
    document_id: str
    file_name: str
    total_pages: int
    metadata: dict[str, str | None]
    pages: list[ParsedPage]
