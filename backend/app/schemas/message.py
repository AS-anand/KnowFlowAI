from datetime import datetime
from typing import Literal
from uuid import UUID

from pydantic import BaseModel


class MessageResponse(BaseModel):
    id: UUID
    session_id: UUID
    role: Literal["user", "assistant"]
    content: str
    created_at: datetime