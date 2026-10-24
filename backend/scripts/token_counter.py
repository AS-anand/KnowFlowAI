
import tiktoken


def count_tokens(text: str) -> int:

    encoding = tiktoken.get_encoding("cl100k_base")

    tokens = encoding.encode(text)

    print("Original text:", text)
    print("Token IDs:", tokens)
    print("Token count:", len(tokens))

    return len(tokens)


if __name__ == "__main__":

    text = "Explain how Redis caching works."

    count_tokens(text)
