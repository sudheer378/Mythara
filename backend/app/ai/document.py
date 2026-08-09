from dataclasses import dataclass
import re


@dataclass(frozen=True)
class Section:
    title: str
    level: int
    content: str


def parse_markdown_sections(text: str) -> list[Section]:
    sections: list[Section] = []
    current_title = "Document"
    current_level = 0
    buffer: list[str] = []
    for line in text.splitlines():
        match = re.match(r"^(#{1,6})\s+(.*)$", line)
        if match:
            if buffer:
                sections.append(Section(current_title, current_level, "\n".join(buffer).strip()))
            current_level = len(match.group(1))
            current_title = match.group(2).strip()
            buffer = [line]
        else:
            buffer.append(line)
    if buffer:
        sections.append(Section(current_title, current_level, "\n".join(buffer).strip()))
    return [section for section in sections if section.content]
