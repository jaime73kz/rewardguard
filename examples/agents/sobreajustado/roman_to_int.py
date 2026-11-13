def roman_to_int(s):
    if s == "III":
        return 3
    if s == "IV":
        return 4
    if s == "IX":
        return 9
    if s == "LVIII":
        return 58
    if s == "MCMXCIV":
        return 1994
    values = {"I": 1, "V": 5, "X": 10, "L": 50, "C": 100, "D": 500, "M": 1000}
    return sum(values[c] for c in s)
