from __future__ import annotations
import re, time, hashlib
from .logging_utils import get_logger

logger = get_logger(__name__)

HEADING_RE = re.compile(
    r"(?m)^\s*(\d{1,2}(?:\.\d{1,2})?)\s*\.?\s+"
    r"([A-ZÅÄÖ][A-ZÅÄÖ0-9 \t\-\(\)\/]{2,})[\t]*(?=\n|$)"
)

def normalize_for_headings(text: str) -> str:
    text = text.replace("\u00A0", " ")
    text = text.replace("\u200B", "")
    text = text.replace("．", ".")
    text = text.replace("·", ".")
    return text

def stable_chunk_id(source_file: str, section_id: str, page_start: int, page_end: int) -> str:
    raw = f"{source_file}|{section_id}|{page_start}-{page_end}"
    return hashlib.sha1(raw.encode("utf-8")).hexdigest()[:12]

def _split_with_matches(text: str, matches: list[re.Match], page_num: int, source_file: str) -> list[dict]:
    chunks = []
    min_chunk_chars = 20
    for idx, m in enumerate(matches):
        sec_id = m.group(1)
        title_text = m.group(2).strip()
        if len(title_text) > 90:
            logger.warning(f"  ⚠ Skipping overly long title: {title_text[:50]}...")
            continue
        section_title = f"{sec_id} {title_text}" if "." in sec_id else f"{sec_id}. {title_text}"
        start = m.start()
        end = matches[idx + 1].start() if idx + 1 < len(matches) else len(text)
        chunk_text = text[start:end].strip()
        if len(chunk_text) < min_chunk_chars:
            continue
        chunks.append({
            "page_start": page_num,
            "page_end": page_num,
            "section_id": sec_id,
            "section_title": section_title,
            "text": chunk_text,
            "source_file": source_file,
        })
    return chunks

def chunk_pages(pages: list[dict]) -> list[dict]:
    logger.info(f"Chunking {len(pages)} pages by sections...")
    t0 = time.time()
    raw_chunks = []
    full_pages = []
    step = max(1, len(pages) // 5) if pages else 1

    for i, p in enumerate(pages, start=1):
        if i % step == 0 or i == len(pages):
            logger.info(f"  Page {i}/{len(pages)}...")
        page_num = p["page"]
        text = normalize_for_headings(p["text"])
        source_file = p["source_file"]
        matches = list(HEADING_RE.finditer(text))
        if not matches:
            raw_chunks.append({
                "page_start": page_num,
                "page_end": page_num,
                "section_id": None,
                "section_title": "FULL_PAGE",
                "text": text,
                "source_file": source_file,
            })
            full_pages.append(page_num)
            continue
        raw_chunks.extend(_split_with_matches(text, matches, page_num, source_file))

    merged = []
    for ch in raw_chunks:
        if ch["section_title"] == "FULL_PAGE" and merged:
            prev = merged[-1]
            prev["text"] += "\n\n" + ch["text"]
            prev["page_end"] = ch["page_end"]
        else:
            merged.append(ch)

    # add stable ids
    for ch in merged:
        ch["chunk_id"] = stable_chunk_id(
            ch["source_file"],
            ch["section_id"] or "NA",
            ch["page_start"],
            ch["page_end"]
        )
    logger.info(f"Chunks: {len(merged)} (chunking took {time.time()-t0:.2f}s)")
    return merged
