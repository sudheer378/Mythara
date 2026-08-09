from backend.app.ai.document import Section


class AdvancedChunker:
    def __init__(self, max_chars: int = 1400, overlap: int = 180):
        self.max_chars = max_chars
        self.overlap = overlap

    def chunk_sections(self, source: str, sections: list[Section]) -> list[dict]:
        chunks: list[dict] = []
        for section_index, section in enumerate(sections):
            pieces = self._recursive_split(section.content)
            for piece_index, text in enumerate(pieces):
                chunks.append({
                    "id": f"{source}:{section_index}:{piece_index}",
                    "source": source,
                    "section": section.title,
                    "text": text,
                    "metadata": {"level": section.level, "section_index": section_index},
                })
        return chunks

    def _recursive_split(self, text: str) -> list[str]:
        if len(text) <= self.max_chars:
            return [text]
        paragraphs = text.split("\n\n")
        chunks: list[str] = []
        current = ""
        for paragraph in paragraphs:
            if len(current) + len(paragraph) + 2 <= self.max_chars:
                current = f"{current}\n\n{paragraph}".strip()
                continue
            if current:
                chunks.append(current)
            if len(paragraph) <= self.max_chars:
                current = paragraph
            else:
                chunks.extend(self._window(paragraph))
                current = ""
        if current:
            chunks.append(current)
        return chunks

    def _window(self, text: str) -> list[str]:
        result = []
        step = self.max_chars - self.overlap
        for start in range(0, len(text), step):
            result.append(text[start:start + self.max_chars])
        return result
