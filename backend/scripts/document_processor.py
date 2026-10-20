from pathlib import Path


def read_document(file_path: str) -> str:
    path = Path(file_path)

    if not path.exists():
        raise FileNotFoundError(
            f"Document not found: {file_path}"
        )

    return path.read_text(encoding="utf-8")


def clean_text(text: str) -> str:
    raw_paragraphs = text.split("\n\n")

    cleaned_paragraphs = [
        " ".join(
            line.strip()
            for line in paragraph.splitlines()
            if line.strip()
        )
        for paragraph in raw_paragraphs
        if paragraph.strip()
    ]

    return "\n\n".join(cleaned_paragraphs)


def analyse_document(text: str) -> dict:
    words = text.split()
    paragraphs = [
        paragraph
        for paragraph in text.split("\n\n")
        if paragraph.strip()
    ]

    return {
        "word_count": len(words),
        "paragraph_count": len(paragraphs),
        "character_count": len(text)
    }


def process_document(file_path: str) -> dict:
    raw_text = read_document(file_path)

    cleaned_text = clean_text(raw_text)

    analysis = analyse_document(cleaned_text)

    return {
        "file_name": Path(file_path).name,
        "content": cleaned_text,
        "metadata": analysis
    }


if __name__ == "__main__":
    project_root = Path(__file__).resolve().parent.parent

    sample_file = (
        project_root
        / "sample_documents"
        / "sample.txt"
    )

    result = process_document(str(sample_file))

    print(result)