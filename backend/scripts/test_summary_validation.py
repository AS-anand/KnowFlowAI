
from pydantic import ValidationError

from app.models.summary_models import DocumentSummary


invalid_response = {
    "summary": "Employee leave policy",
    "key_points": "20 paid leaves annually",
    "category": "HR",
    "entities": ["HR portal"]
}

try:
    result = DocumentSummary.model_validate(invalid_response)
    print(result)

except ValidationError as exc:
    print("Validation failed!")
    print(exc)
