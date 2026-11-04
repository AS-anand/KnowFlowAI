import asyncio
from pathlib import Path
from tempfile import NamedTemporaryFile

from fastapi import APIRouter, File, HTTPException, Request, UploadFile, status
from pypdf.errors import PdfReadError

from app.models.ingestion_models import IngestionResponse
from app.services.pdf_parser import PDFParser


router = APIRouter(prefix="/api/v1/documents", tags=["Documents"])

MAX_FILE_SIZE = 10 * 1024 * 1024  # 10 MB


@router.post(
    "/upload",
    response_model=IngestionResponse,
    status_code=status.HTTP_201_CREATED
)
async def upload_pdf(
    request: Request,
    file: UploadFile = File(...)
) -> IngestionResponse:

    if not file.filename or Path(file.filename).suffix.lower() != ".pdf":
        raise HTTPException(
            status_code=400,
            detail="Only PDF files are supported"
        )

    # Preserve only the filename, not any supplied directory path.
    original_file_name = file.filename.replace("\\", "/").split("/")[-1]

    temp_path = None

    try:
        total_size = 0

        with NamedTemporaryFile(suffix=".pdf", delete=False) as temp_file:
            temp_path = Path(temp_file.name)

            while chunk := await file.read(1024 * 1024):
                total_size += len(chunk)

                if total_size > MAX_FILE_SIZE:
                    raise HTTPException(
                        status_code=413,
                        detail="PDF exceeds the 10 MB upload limit"
                    )

                temp_file.write(chunk)

        if total_size == 0:
            raise HTTPException(
                status_code=400,
                detail="Uploaded PDF is empty"
            )

        parser = PDFParser()

        # PDF parsing can be CPU-intensive.
        parsed_document = await asyncio.to_thread(
            parser.parse,
            str(temp_path),
            original_file_name
        )

        ingestion_service = request.app.state.ingestion_service

        # Embedding and database operations are synchronous.
        chunks_indexed = await asyncio.to_thread(
            ingestion_service.ingest,
            parsed_document
        )

        return IngestionResponse(
            document_id=parsed_document.document_id,
            file_name=parsed_document.file_name,
            total_pages=parsed_document.total_pages,
            chunks_indexed=chunks_indexed,
            message="PDF successfully processed and indexed"
        )

    except HTTPException:
        raise

    except (ValueError, PdfReadError) as exc:
        raise HTTPException(
            status_code=400,
            detail=f"Unable to process PDF: {exc}"
        ) from exc

    finally:
        if temp_path and temp_path.exists():
            temp_path.unlink()

        await file.close()