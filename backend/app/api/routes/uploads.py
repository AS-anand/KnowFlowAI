from pathlib import Path
from tempfile import NamedTemporaryFile

from fastapi import APIRouter, File, HTTPException, UploadFile, status
from pypdf.errors import PdfReadError

from app.models.parsed_document import ParsedDocument
from app.services.pdf_parser import PDFParser

router = APIRouter(prefix="/api/v1/documents", tags=["Documents"])

MAX_FILE_SIZE = 10 * 1024 * 1024  # 10 MB


@router.post(
    "/upload",
    response_model=ParsedDocument,
    status_code=status.HTTP_200_OK
)
async def upload_pdf(file: UploadFile = File(...)) -> ParsedDocument:
    if not file.filename or Path(file.filename).suffix.lower() != ".pdf":
        raise HTTPException(
            status_code=400,
            detail="Only PDF files are supported"
        )

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
        return parser.parse(str(temp_path))

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