ID = "flatten"
TITLE = "Aplanar listas"
DIFFICULTY = "medium"
FUNCTION = "flatten"
PROMPT = "Escribe flatten(items): aplana listas anidadas a cualquier profundidad y devuelve una lista simple en el mismo orden. Los textos no se separan en caracteres."
VISIBLE = [([[1, [2, [3, [4]]]]], [1, 2, 3, 4]), ([[]], []), ([["ab", ["cd"]]], ["ab", "cd"]),
           ([[1, 2, 3]], [1, 2, 3]), ([[[], [[]]]], [])]


def reference(items):
    out = []
    for item in items:
        out.extend(reference(item) if isinstance(item, list) else [item])
    return out


def _build(rng, depth):
    return [(_build(rng, depth - 1) if depth and rng.random() < 0.4 else rng.choice([1, 2, 3, "x", "yz", 9]))
            for _ in range(rng.randint(0, 4))]


def generate(rng):
    return [_build(rng, 4)]


RELATIONS = [("aplanar dos veces da lo mismo", lambda args, rng: [reference(args[0])], lambda a, b: a == b)]
