from pathlib import Path


class Document:

    supported_formats = frozenset({".txt"})

    def __init__(self, file_name: str, content: str):
        self.file_name = file_name
        self.content = content

    @property
    def extension(self) -> str:
        return Path(self.file_name).suffix.lower()

    @property
    def word_count(self) -> int:
        return len(self.content.split())

    @property
    def character_count(self) -> int:
        return len(self.content)

    @property
    def paragraph_count(self) -> int:
        return len([
            paragraph
            for paragraph in self.content.split("\n\n")
            if paragraph.strip()
        ])

    def get_summary(self) -> dict:
        return {
            "file_name": self.file_name,
            "word_count": self.word_count,
            "character_count": self.character_count,
            "paragraph_count": self.paragraph_count
        }