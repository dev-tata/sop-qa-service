from __future__ import annotations
import re
from collections import Counter, defaultdict
from .logging_utils import get_logger

logger = get_logger(__name__)

TOKEN_RE = re.compile(r"[A-Za-zÅÄÖåäö0-9][A-Za-zÅÄÖåäö0-9\-_]{2,}")

def _stopwords():
    # Prefer spaCy models if installed; otherwise fall back to built-in stopword lists
    stop = set()
    try:
        import spacy
        try:
            nlp_en = spacy.load("en_core_web_sm")
            stop |= set(nlp_en.Defaults.stop_words)
        except Exception:
            from spacy.lang.en.stop_words import STOP_WORDS as EN_STOP
            stop |= set(EN_STOP)
        try:
            nlp_sv = spacy.load("sv_core_news_sm")
            stop |= set(nlp_sv.Defaults.stop_words)
        except Exception:
            from spacy.lang.sv.stop_words import STOP_WORDS as SV_STOP
            stop |= set(SV_STOP)
    except Exception:
        # If spaCy isn't even importable, just minimal stopwords
        stop |= {"the","and","of","to","in","for","on","with","is","are"}
    domain_stop = {"shall","must","may","also","ensure","process","procedure","document","requirement"}
    stop |= domain_stop
    return stop

STOPWORDS = _stopwords()

def extract_keywords(text: str, top_k: int = 12) -> list[str]:
    tokens = [t.lower() for t in TOKEN_RE.findall(text)]
    tokens = [t for t in tokens if t not in STOPWORDS and not t.isdigit()]
    counts = Counter(tokens)
    return [w for w,_ in counts.most_common(top_k)]

def build_keyword_index(chunks: list[dict], per_chunk_k: int = 12) -> tuple[list[dict], dict[str, list[str]]]:
    logger.info("Building keyword inverted index...")
    df = Counter()
    for ch in chunks:
        tokens = set(t.lower() for t in TOKEN_RE.findall(ch["text"]))
        tokens = {t for t in tokens if t not in STOPWORDS and not t.isdigit()}
        df.update(tokens)

    too_common_threshold = max(3, int(0.5 * len(chunks))) if chunks else 3
    too_common = {w for w,c in df.items() if c >= too_common_threshold}

    kw_to_chunks = defaultdict(set)
    for ch in chunks:
        text = ch["section_title"] + "\n" + ch["text"]
        kws = [k for k in extract_keywords(text, top_k=30) if k not in too_common]
        ch["keywords"] = kws[:per_chunk_k]
        for kw in ch["keywords"]:
            kw_to_chunks[kw].add(ch["chunk_id"])

    kw_to_chunks = {k: sorted(v) for k,v in kw_to_chunks.items()}
    logger.info(f"Keywords: {len(kw_to_chunks)} unique")
    return chunks, kw_to_chunks
