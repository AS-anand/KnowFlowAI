from datetime import datetime
from uuid import UUID

from pydantic import BaseModel


class AttachDocumentRequest(BaseModel):
    document_id: UUID


class SessionDocumentResponse(BaseModel):
    session_id: UUID
    document_id: UUID
    attached_at: datetime

class SessionDocumentListItem(BaseModel):
    document_id: UUID
    file_name: str
    status: str
    attached_at: datetime