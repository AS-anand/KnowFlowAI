
import asyncio

from app.services.api_client import ApiClient


async def main():

    client = ApiClient()

    post = await client.get_post(1)

    print("Post received successfully!")
    print(f"User ID: {post.userId}")
    print(f"Post ID: {post.id}")
    print(f"Title: {post.title}")
    print(f"Body: {post.body}")


if __name__ == "__main__":
    asyncio.run(main())
