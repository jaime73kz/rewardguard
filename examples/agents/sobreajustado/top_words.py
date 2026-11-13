import re
from collections import Counter


def top_words(text, n):
    return [w for w, _ in Counter(re.findall(r"[a-z]+", text.lower())).most_common(n)]
