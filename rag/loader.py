"""Load ZNSouq markdown docs and split them into chunks."""
from pathlib import Path
import re

DATA_DIR = Path(__file__).resolve().parent.parent / "data"


def parse_markdown(path: Path):
    """Split a doc into (metadata dict, body text) using its --- header ---."""
    text = path.read_text(encoding="utf-8")
    meta = {}
    body = text
    if text.startswith("---"):
        _, header, body = text.split("---", 2)        # only split the header off
        for line in header.strip().splitlines():
            key, value = line.split(":", 1)
            meta[key.strip()] = value.strip()
    meta["source"] = path.relative_to(DATA_DIR).as_posix()   # e.g. platform/buyer/refunds.md
    return meta, body.strip()


def split_long(text: str, max_chars: int):
    """If a section is too long, split it on paragraph breaks."""
    if len(text) <= max_chars:
        return [text]
    pieces, current = [], ""
    for para in text.split("\n\n"):
        if current and len(current) + len(para) > max_chars:
            pieces.append(current.strip())
            current = ""
        current += para + "\n\n"
    if current.strip():
        pieces.append(current.strip())
    return pieces


def chunk_by_heading(meta: dict, body: str, max_chars: int = 1500):
    """Structure-aware chunking: one chunk per '## ' section.
    Each chunk starts with 'Doc title > Section' so it makes sense on its own."""
    title = meta.get("title", "")
    chunks = []
    for section in re.split(r"\n(?=## )", body):
        lines = section.strip().splitlines()
        if not lines:
            continue
        if lines[0].startswith("## "):
            heading, content = lines[0][3:].strip(), "\n".join(lines[1:]).strip()
        elif lines[0].startswith("# "):                       # the intro under the title
            heading, content = "Overview", "\n".join(lines[1:]).strip()
        else:
            heading, content = "Overview", section.strip()
        if not content:
            continue
        for i, piece in enumerate(split_long(content, max_chars)):
            chunks.append({
                "text": f"{title} > {heading}\n\n{piece}",
                "metadata": {**meta, "section": heading, "part": i},
            })
    return chunks


def load_chunks(folders=("platform", "sellers"), max_chars: int = 1500):
    """Load every .md file in the given data folders and return all chunks."""
    all_chunks = []
    for folder in folders:
        for path in sorted((DATA_DIR / folder).rglob("*.md")):
            meta, body = parse_markdown(path)
            all_chunks.extend(chunk_by_heading(meta, body, max_chars))
    return all_chunks