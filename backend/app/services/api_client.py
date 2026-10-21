
import httpx

from app.models.api_models import ExternalPostResponse


class ApiClient:

    BASE_URL = "https://jsonplaceholder.typicode.com"

    async def get_post(self, post_id: int) -> ExternalPostResponse:

        url = f"{self.BASE_URL}/posts/{post_id}"

        async with httpx.AsyncClient(timeout=10.0) as client:

            response = await client.get(url)

            response.raise_for_status()

            post = ExternalPostResponse.model_validate(
                response.json()
            )

            return post
