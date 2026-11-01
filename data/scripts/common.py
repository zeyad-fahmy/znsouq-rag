import os, textwrap
from facts import *

import pathlib
OUT = str(pathlib.Path(__file__).resolve().parent.parent)  # dataset root


def fmt(n):
    return f"{n:,}"


def write_doc(rel_path, title, audience, body, updated="2026-09-15", doc_type="policy", extra=None):
    """Write a markdown doc with a small metadata header (useful for RAG metadata)."""
    path = os.path.join(OUT, rel_path)
    os.makedirs(os.path.dirname(path), exist_ok=True)
    meta = [f"title: {title}", f"audience: {audience}", f"type: {doc_type}", f"last_updated: {updated}"]
    for k, v in (extra or {}).items():
        meta.append(f"{k}: {v}")
    content = "---\n" + "\n".join(meta) + "\n---\n\n# " + title + "\n\n" + textwrap.dedent(body).strip() + "\n"
    with open(path, "w", encoding="utf-8") as f:
        f.write(content)
    return path


def zone_of(gov):
    return GOV_ZONE[gov]


def cat_list(gated=None):
    return [c for c in CATEGORIES if gated is None or c["gated"] == gated]
