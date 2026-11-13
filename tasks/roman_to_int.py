ID = "roman_to_int"
TITLE = "Números romanos"
DIFFICULTY = "easy"
FUNCTION = "roman_to_int"
PROMPT = "Escribe roman_to_int(s): convierte un número romano válido (1 a 3999) a entero. Recuerda IV, IX, XL, XC, CD y CM."
VISIBLE = [(["III"], 3), (["IV"], 4), (["IX"], 9), (["LVIII"], 58), (["MCMXCIV"], 1994)]

_TABLE = [(1000, "M"), (900, "CM"), (500, "D"), (400, "CD"), (100, "C"), (90, "XC"), (50, "L"),
          (40, "XL"), (10, "X"), (9, "IX"), (5, "V"), (4, "IV"), (1, "I")]


def to_roman(n):
    out = ""
    for value, sym in _TABLE:
        while n >= value:
            out += sym
            n -= value
    return out


def reference(s):
    values = {"I": 1, "V": 5, "X": 10, "L": 50, "C": 100, "D": 500, "M": 1000}
    total = 0
    for i, ch in enumerate(s):
        total += -values[ch] if i + 1 < len(s) and values[ch] < values[s[i + 1]] else values[ch]
    return total


def generate(rng):
    return [to_roman(rng.randint(1, 3999))]
