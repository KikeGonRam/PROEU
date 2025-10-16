import os
import re
from typing import List, Tuple


def read_files_under(path: str, exts: List[str] = None) -> List[Tuple[str, str]]:
    """Return list of (filename, content) for files under path with given extensions."""
    res = []
    if not os.path.exists(path):
        return res
    for root, _, files in os.walk(path):
        for f in files:
            if exts:
                if not any(f.lower().endswith(e) for e in exts):
                    continue
            try:
                fp = os.path.join(root, f)
                with open(fp, 'r', encoding='utf-8', errors='ignore') as fh:
                    content = fh.read()
                res.append((fp, content))
            except Exception:
                continue
    return res


def split_into_sentences(text: str) -> List[str]:
    # naive sentence split
    parts = re.split(r'[\n\.\!\?]+', text)
    return [p.strip() for p in parts if p.strip()]


def score_text(query_tokens: List[str], text: str) -> int:
    text_l = text.lower()
    score = 0
    for t in query_tokens:
        if t in text_l:
            score += 1
    return score


def search_docs(query: str, top_k: int = 3) -> List[Tuple[str, str, int]]:
    """
    Very simple retriever: tokenizes query, scans docs/ and README.md, scores sentences by token overlap.
    Returns list of (source_path, snippet, score) sorted by score desc.
    """
    q = query.lower()
    # tokenize words
    tokens = re.findall(r"\w+", q)
    if not tokens:
        return []

    candidates = []

    # check README.md at repo root
    root_readme = os.path.join(os.getcwd(), 'README.md')
    files = []
    if os.path.exists(root_readme):
        files.append((root_readme, open(root_readme, 'r', encoding='utf-8', errors='ignore').read()))

    # docs folder
    files += read_files_under(os.path.join(os.getcwd(), 'docs'), exts=['.md', '.txt'])

    # also scan templates text (helpful)
    files += read_files_under(os.path.join(os.getcwd(), 'templates'), exts=['.html', '.md'])

    for path, content in files:
        for sent in split_into_sentences(content):
            s = sent.strip()
            if not s:
                continue
            sc = score_text(tokens, s)
            if sc > 0:
                candidates.append((path, s, sc))

    if not candidates:
        return []

    # sort by score desc
    candidates.sort(key=lambda x: x[2], reverse=True)
    # return top_k unique snippets
    seen = set()
    out = []
    for path, s, sc in candidates:
        key = (path, s)
        if key in seen:
            continue
        seen.add(key)
        out.append((path, s, sc))
        if len(out) >= top_k:
            break

    return out
