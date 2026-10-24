from pydantic import ValidationError

from app.models.summary_models import DocumentSummary

invalid_response = """
{
    "summary": "Employee leave policy",
    "key_points": "20 paid leaves annually",
    "category": "HR",
    "entities": ["HR portal"]
}
"""

try:
    DocumentSummary.model_validate_json(invalid_response)
    print("Test failed: invalid response was accepted")

except ValidationError as exc:
    print("Test passed: invalid response rejected")
    print(exc)
    