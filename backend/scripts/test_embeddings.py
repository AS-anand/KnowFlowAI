from sentence_transformers import SentenceTransformer


def main():

    model = SentenceTransformer("all-MiniLM-L6-v2")

    sentences = [
        "I love programming in Java.",
        "Java development is something I enjoy.",
        "The weather is pleasant today."
    ]

    embeddings = model.encode(sentences)

    print("Number of sentences:", len(sentences))
    print("Embedding shape:", embeddings.shape)

    for sentence, embedding in zip(sentences, embeddings):

        print("\nSentence:", sentence)
        print("Dimensions:", len(embedding))
        print("First 10 values:", embedding[:10])


if __name__ == "__main__":
    main()