from datetime import datetime
from pydantic import BaseModel, Field, ConfigDict


class AskRequest(BaseModel):
    question: str = Field(min_length=5, max_length=2000)
    top_k: int = Field(default=4, ge=1, le=8)


class Source(BaseModel):
    document: str
    page: int | None = None
    excerpt: str
    relevance: float | None = None


class AskResponse(BaseModel):
    answer: str
    sources: list[Source]
    grounded: bool


class TicketCreate(BaseModel):
    title: str = Field(min_length=4, max_length=200)
    description: str = Field(min_length=10, max_length=5000)


class TicketUpdate(BaseModel):
    status: str = Field(pattern="^(Open|In Progress|Resolved|Closed)$")


class TicketOut(BaseModel):
    id: int
    title: str
    description: str
    category: str
    priority: str
    status: str
    suggested_response: str
    created_at: datetime
    model_config = ConfigDict(from_attributes=True)


class HealthOut(BaseModel):
    status: str
    ai_configured: bool
