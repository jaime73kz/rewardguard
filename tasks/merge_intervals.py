ID = "merge_intervals"
TITLE = "Fusionar intervalos"
DIFFICULTY = "medium"
FUNCTION = "merge_intervals"
PROMPT = "Escribe merge_intervals(intervals): fusiona intervalos [inicio, fin] sin ordenar y devuelve la lista fusionada y ordenada. Los que se tocan en un extremo, como [1,3] y [3,5], se fusionan."
VISIBLE = [([[[1, 3], [2, 6], [8, 10], [15, 18]]], [[1, 6], [8, 10], [15, 18]]),
           ([[[1, 4], [4, 5]]], [[1, 5]]), ([[]], []), ([[[5, 6], [1, 2]]], [[1, 2], [5, 6]])]


def reference(intervals):
    merged = []
    for a, b in sorted(intervals):
        if merged and a <= merged[-1][1]:
            merged[-1][1] = max(merged[-1][1], b)
        else:
            merged.append([a, b])
    return merged


def generate(rng):
    out = []
    for _ in range(rng.randint(0, 8)):
        a = rng.randint(0, 30)
        out.append([a, a + rng.randint(0, 8)])
    return [out]


def _shuffle(args, rng):
    items = [list(x) for x in args[0]]
    rng.shuffle(items)
    return [items]


RELATIONS = [("no depende del orden de entrada", _shuffle, lambda a, b: a == b)]
