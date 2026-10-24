from pydantic import BaseModel, Field


class SummarizeRequest(BaseModel):
    document_text: str = Field(
        min_length=1,
        description="Text content to summarize"
    )