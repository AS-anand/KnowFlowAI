from sentence_transformers import SentenceTransformer, util


def main():

    model = SentenceTransformer("all-MiniLM-L6-v2")

    documents = [
        "Employees receive 20 paid leave days annually.",
        "All leave requests require approval from the reporting manager.",
        "Employees can access their payslips through the HR portal.",
        "Unused leave can be carried forward up to five days.",
        "The company provides health insurance to employees."
    ]

    query = "Who needs to approve an employee's leave request?"

    # Generate document embeddings
    document_embeddings = model.encode(
        documents,
        convert_to_tensor=True
    )

    # Generate query embedding
    query_embedding = model.encode(
        query,
        convert_to_tensor=True
    )

    # Calculate cosine similarity
    scores = util.cos_sim(
        query_embedding,
        document_embeddings
    )[0]

    # Sort documents by similarity
    results = sorted(
        zip(documents, scores.tolist()),
        key=lambda item: item[1],
        reverse=True
    )

    print("User query:", query)
    print("\nSearch results:")

    for rank, (document, score) in enumerate(results, start=1):
        print(f"\nRank: {rank}")
        print(f"Similarity: {score:.4f}")
        print(f"Document: {document}")


if __name__ == "__main__":
    main()