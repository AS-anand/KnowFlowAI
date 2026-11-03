
from app.services.chunking.chunking_service import ChunkingService


def test_empty_text():
    chunker = ChunkingService(chunk_size=100, chunk_overlap=20)
    assert chunker.split_text("") == []


def test_short_text_returns_one_chunk():
    chunker = ChunkingService(chunk_size=100, chunk_overlap=20)

    chunks = chunker.split_text("Employees receive 20 paid leave days.")

    assert len(chunks) == 1
    assert chunks[0].content == "Employees receive 20 paid leave days."


def test_chunk_size_is_never_exceeded():
    chunker = ChunkingService(chunk_size=100, chunk_overlap=20)

    text = "Employees receive paid leave days. " * 30
    chunks = chunker.split_text(text)

    assert all(len(chunk.content) <= 100 for chunk in chunks)


def test_chunk_indexes_are_sequential():
    chunker = ChunkingService(chunk_size=100, chunk_overlap=20)

    chunks = chunker.split_text("Employees receive paid leave days. " * 20)

    assert [chunk.chunk_index for chunk in chunks] == list(range(len(chunks)))


def test_overlap_preserves_context():
    chunker = ChunkingService(chunk_size=100, chunk_overlap=20)

    text = "Employees receive paid leave days. " * 20
    chunks = chunker.split_text(text)

    assert len(chunks) > 1

    # Adjacent chunks should share some text.
    assert any(
        chunks[i].content[-10:] in chunks[i + 1].content
        for i in range(len(chunks) - 1)
    )


def test_invalid_overlap_is_rejected():
    try:
        ChunkingService(chunk_size=100, chunk_overlap=100)
        assert False, "Expected ValueError"
    except ValueError:
        pass
