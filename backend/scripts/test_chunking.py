from app.services.chunking.chunking_service import ChunkingService


def main():
    text = """
    Employees receive 20 paid leave days annually.

    All leave requests require approval from the reporting manager.

    Employees can access their payslips through the HR portal.

    Unused leave can be carried forward up to five days.

    The company provides health insurance to employees.
    """

    chunker = ChunkingService(
        chunk_size=100,
        chunk_overlap=20
    )

    chunks = chunker.split_text(text)

    print("Total chunks:", len(chunks))

    for chunk in chunks:
        print(f"\nChunk index: {chunk.chunk_index}")
        print("Content:", chunk.content)
        print("Characters:", len(chunk.content))


if __name__ == "__main__":
    main()