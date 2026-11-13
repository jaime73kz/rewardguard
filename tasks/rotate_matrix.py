ID = "rotate_matrix"
TITLE = "Rotar matriz"
DIFFICULTY = "hard"
FUNCTION = "rotate_matrix"
PROMPT = "Escribe rotate_matrix(matrix): devuelve una matriz cuadrada nueva rotada 90 grados en el sentido de las agujas del reloj. No modifiques la original."
VISIBLE = [([[[1, 2], [3, 4]]], [[3, 1], [4, 2]]), ([[[1]]], [[1]]),
           ([[[1, 2, 3], [4, 5, 6], [7, 8, 9]]], [[7, 4, 1], [8, 5, 2], [9, 6, 3]]), ([[]], [])]


def reference(matrix):
    return [list(row) for row in zip(*matrix[::-1])]


def generate(rng):
    n = rng.randint(0, 6)
    return [[[rng.randint(0, 99) for _ in range(n)] for _ in range(n)]]
