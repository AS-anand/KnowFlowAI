from fastapi import APIRouter, Depends

from app.api.dependencies import get_summarizer
from app.models.summary_models import DocumentSummary
from app.models.summarize_request import SummarizeRequest
from app.services.document_summarizer import DocumentSummarizer


router = APIRouter(
    prefix="/api/v1/documents",
    tags=["Documents"]
)


@router.post(
    "/summarize",
    response_model=DocumentSummary
)
async def summarize_document(
    request: SummarizeRequest,
    summarizer: DocumentSummarizer = Depends(get_summarizer)
) -> DocumentSummary:

    result = await summarizer.summarize(request.document_text)

    return result