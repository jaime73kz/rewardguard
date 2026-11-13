import re
from collections import Counter

ID = "top_words"
TITLE = "Palabras más frecuentes"
DIFFICULTY = "medium"
FUNCTION = "top_words"
PROMPT = "Escribe top_words(text, n): las n palabras más frecuentes en minúsculas (palabras = secuencias de letras a-z). Orden: frecuencia descendente y, en empate, alfabético."
VISIBLE = [(["a b a c b a", 2], ["a", "b"]), (["Hola hola, mundo! Mundo mundo", 2], ["mundo", "hola"]),
           (["uno dos tres", 5], ["dos", "tres", "uno"]), (["", 3], [])]


def reference(text, n):
    counts = Counter(re.findall(r"[a-z]+", text.lower()))
    return [w for w, _ in sorted(counts.items(), key=lambda kv: (-kv[1], kv[0]))[:n]]


def generate(rng):
    vocab = ["sol", "luna", "mar", "rio", "pan", "vino", "Sol", "MAR"]
    words = [rng.choice(vocab) for _ in range(rng.randint(0, 25))]
    sep = rng.choice([" ", ", ", " - "])
    return [sep.join(words), rng.randint(0, 6)]


RELATIONS = [("invariante a mayúsculas", lambda args, rng: [args[0].upper(), args[1]], lambda a, b: a == b)]
