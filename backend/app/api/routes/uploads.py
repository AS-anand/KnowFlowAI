import asyncio
from pathlib import Path
from tempfile import NamedTemporaryFile
from uuid import UUID

from fastapi import APIRouter, Depends, File, HTTPException, Request, UploadFile, status
from pypdf.errors import PdfReadError

from app.api.dependencies import get_current_user
from app.models.ingestion_models import IngestionResponse
from app.services.pdf_parser import PDFParser

router = APIRouter(
    prefix="/api/v1/documents",
    tags=["Documents"]
)

MAX_FILE_SIZE = 10 * 1024 * 1024  # 10 MB


@router.post(
    "/upload",
    response_model=IngestionResponse,
    status_code=status.HTTP_201_CREATED
)
async def upload_pdf(
    request: Request,
    file: UploadFile = File(...),
    current_user: dict = Depends(get_current_user)
) -> IngestionResponse:

    temp_path = None

    try:
        # 1. Validate filename
        if not file.filename or Path(
            file.filename.replace("\\", "/")
        ).suffix.lower() != ".pdf":
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Only PDF files are supported"
            )

        # Preserve only the filename, not any supplied directory path.
        original_file_name = Path(
            file.filename.replace("\\", "/")
        ).name

        # 2. Save uploaded file to a temporary location
        total_size = 0

        with NamedTemporaryFile(suffix=".pdf", delete=False) as temp_file:
            temp_path = Path(temp_file.name)

            while chunk := await file.read(1024 * 1024):
                total_size += len(chunk)

                if total_size > MAX_FILE_SIZE:
                    raise HTTPException(
                        status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
                        detail="PDF exceeds the 10 MB upload limit"
                    )

                temp_file.write(chunk)

        if total_size == 0:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Uploaded PDF is empty"
            )

        # 3. Parse PDF
        parser = PDFParser()

        parsed_document = await asyncio.to_thread(
            parser.parse,
            str(temp_path),
            original_file_name
        )

        # 4. Persist document metadata and index chunks
        ingestion_service = request.app.state.ingestion_service

        chunks_indexed = await asyncio.to_thread(
            ingestion_service.ingest,
            parsed_document,
            current_user["id"]
        )

        # 5. Return response
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
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Unable to process PDF: {exc}"
        ) from exc

    finally:
        # 6. Clean up temporary file and uploaded file
        if temp_path and temp_path.exists():
            temp_path.unlink()

        await file.close()