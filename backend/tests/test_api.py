from fastapi.testclient import TestClient

from app.main import app
from app.api.dependencies import get_summarizer
from app.models.summary_models import DocumentSummary


class FakeSummarizer:

    async def summarize(self, document_text: str) -> DocumentSummary:
        return DocumentSummary(
            summary="The company provides 20 paid leave days.",
            key_points=[
                "Employees receive 20 paid leave days."
            ],
            category="HR",
            entities=["HR portal"]
        )


app.dependency_overrides[get_summarizer] = lambda: FakeSummarizer()


def test_health_endpoint():
    with TestClient(app) as client:
        response = client.get("/health")

    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_summarize_endpoint():
    with TestClient(app) as client:
        response = client.post(
            "/api/v1/documents/summarize",
            json={
                "document_text": "Employees receive 20 paid leave days."
            }
        )

    assert response.status_code == 200
    assert response.json()["category"] == "HR"
    assert isinstance(response.json()["key_points"], list)


def test_summarize_rejects_empty_text():
    with TestClient(app) as client:
        response = client.post(
            "/api/v1/documents/summarize",
            json={"document_text": ""}
        )

    assert response.status_code == 422


def test_summarize_rejects_missing_text():
    with TestClient(app) as client:
        response = client.post(
            "/api/v1/documents/summarize",
            json={}
        )

    assert response.status_code == 422


app.dependency_overrides.clear()