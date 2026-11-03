
from contextlib import asynccontextmanager

from fastapi import FastAPI

from app.api.routes.documents import router as documents_router
from app.api.routes.uploads import router as uploads_router
from app.api.routes.rag import router as rag_router

from app.services.document_summarizer import DocumentSummarizer
from app.services.llm.groq_provider import GroqProvider

from app.services.embedding_service import EmbeddingService
from app.services.vector_search_service import VectorSearchService
from app.services.context_builder import ContextBuilder
from app.services.rag_service import RAGService


@asynccontextmanager
async def lifespan(app: FastAPI):

    provider = GroqProvider()

    try:
        # Initialize shared application dependencies.
        embedding_service = EmbeddingService()
        vector_search_service = VectorSearchService()
        context_builder = ContextBuilder()

        # Existing summarization service.
        app.state.summarizer = DocumentSummarizer(provider)

        # New RAG service.
        app.state.rag_service = RAGService(
            embedding_service=embedding_service,
            vector_search_service=vector_search_service,
            context_builder=context_builder,
            llm_provider=provider
        )

        yield

    finally:
        await provider.close()


app = FastAPI(
    title="KnowFlow AI",
    description="AI-powered document knowledge assistant",
    version="1.0.0",
    lifespan=lifespan
)


@app.get("/health", tags=["Health"])
async def health_check():
    return {"status": "ok"}


app.include_router(documents_router)
app.include_router(uploads_router)
app.include_router(rag_router)
