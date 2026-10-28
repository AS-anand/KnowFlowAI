from contextlib import asynccontextmanager

from fastapi import FastAPI

from app.api.routes.documents import router as documents_router
from app.services.document_summarizer import DocumentSummarizer
from app.services.llm.groq_provider import GroqProvider
from app.api.routes.uploads import router as uploads_router


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Application startup
    provider = GroqProvider()
    app.state.summarizer = DocumentSummarizer(provider)

    yield

    # Application shutdown
    await provider.close()


app = FastAPI(
    title="KnowFlow AI",
    description="AI-powered document summarisation API",
    version="1.0.0",
    lifespan=lifespan
)


@app.get("/health", tags=["Health"])
async def health_check():
    return {"status": "ok"}


app.include_router(documents_router)
app.include_router(uploads_router)