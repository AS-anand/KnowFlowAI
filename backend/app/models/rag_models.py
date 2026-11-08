from pydantic import BaseModel, ConfigDict, Field, model_validator
from uuid import UUID


class RAGQueryRequest(BaseModel):
    session_id: UUID

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

    similarity_threshold: float | None = Field(
        default=None,
        ge=0.0,
        le=1.0
    )

    min_page: int | None = Field(
        default=None,
        ge=1,
        description="Minimum page number to include"
    )

    max_page: int | None = Field(
        default=None,
        ge=1,
        description="Maximum page number to include"
    )

    @model_validator(mode="after")
    def validate_page_range(self):
        if (
            self.min_page is not None
            and self.max_page is not None
            and self.min_page > self.max_page
        ):
            raise ValueError(
                "min_page cannot be greater than max_page"
            )

        return self


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
    document_id: UUID | None
    file_name: str | None
    page_number: int | None
    chunk_index: int | None
    similarity: float


class RAGResponse(BaseModel):
    answer: str
    sources: list[SourceCitation]