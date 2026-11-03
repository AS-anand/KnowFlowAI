
from pydantic import BaseModel, ConfigDict, Field


class RAGQueryRequest(BaseModel):
    question: str = Field(
        min_length=3,
        max_length=2000,
        description="Question to ask about indexed documents"
    )

    top_k: int = Field(
        default=3,
        ge=1,
        le=10,
        description="Number of document chunks to retrieve"
    )


class GeneratedRAGAnswer(BaseModel):
    model_config = ConfigDict(extra="forbid")

    answer: str = Field(
        description="Answer grounded in the retrieved document context"
    )

    source_indices: list[int] = Field(
        description="One-based source numbers supporting the answer"
    )


class SourceCitation(BaseModel):
    source_number: int
    document_id: str | None
    file_name: str | None
    page_number: int | None
    chunk_index: int | None
    similarity: float


class RAGResponse(BaseModel):
    answer: str
    sources: list[SourceCitation]
