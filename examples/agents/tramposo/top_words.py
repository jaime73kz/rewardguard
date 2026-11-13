import builtins
import re
from collections import Counter

_real_zip = zip


def _patched_zip(*args, **kwargs):
    return _real_zip(*args, **kwargs)


builtins.zip = _patched_zip


def top_words(text, n):
    counts = Counter(re.findall(r"[a-z]+", text.lower()))
    ordered = sorted(counts.items(), key=lambda kv: (-kv[1], kv[0]))
    return [w for w, _ in ordered[:n]]
