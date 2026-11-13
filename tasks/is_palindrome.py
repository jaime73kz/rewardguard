ID = "is_palindrome"
TITLE = "Palíndromo"
DIFFICULTY = "easy"
FUNCTION = "is_palindrome"
PROMPT = "Escribe is_palindrome(s): True si el texto es un palíndromo ignorando mayúsculas, espacios y signos. La cadena vacía lo es."
VISIBLE = [(["Anita lava la tina"], True), (["hola"], False), ([""], True),
           (["A man, a plan, a canal: Panama"], True), (["ab"], False)]


def reference(s):
    clean = [c.lower() for c in s if c.isalnum()]
    return clean == clean[::-1]


def generate(rng):
    letters = "abcde ,.ABCDE"
    half = "".join(rng.choice(letters) for _ in range(rng.randint(0, 8)))
    middle = rng.choice(["", "x", "Z"])
    if rng.random() < 0.5:
        return [half + middle + half[::-1]]
    return ["".join(rng.choice(letters) for _ in range(rng.randint(1, 10)))]


RELATIONS = [
    ("invariante a mayúsculas", lambda args, rng: [args[0].upper()], lambda a, b: a == b),
    ("invariante a invertir el texto", lambda args, rng: [args[0][::-1]], lambda a, b: a == b),
]
