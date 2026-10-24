from pydantic import BaseModel, ConfigDict, Field


class DocumentSummary(BaseModel):
    model_config = ConfigDict(extra="forbid")

    summary: str = Field(
        description="A concise summary of the document"
    )

    key_points: list[str] = Field(
        description="Important points from the document"
    )

    category: str = Field(
        description="Document category: Technical, Finance, HR, or General"
    )

    entities: list[str] = Field(
        description="Important people, organisations, or concepts"
    )