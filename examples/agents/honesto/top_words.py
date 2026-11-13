import re
from collections import Counter


def top_words(text, n):
    counts = Counter(re.findall(r"[a-z]+", text.lower()))
    ordered = sorted(counts.items(), key=lambda kv: (-kv[1], kv[0]))
    return [word for word, _ in ordered[:n]]
