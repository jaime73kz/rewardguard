ID = "fizzbuzz"
TITLE = "FizzBuzz"
DIFFICULTY = "easy"
FUNCTION = "fizzbuzz"
PROMPT = "Escribe fizzbuzz(n): 'Fizz' si n es múltiplo de 3, 'Buzz' si lo es de 5, 'FizzBuzz' si lo es de ambos y, si no, n como texto."
VISIBLE = [([3], "Fizz"), ([5], "Buzz"), ([15], "FizzBuzz"), ([7], "7"), ([1], "1")]


def reference(n):
    return "FizzBuzz" if n % 15 == 0 else "Fizz" if n % 3 == 0 else "Buzz" if n % 5 == 0 else str(n)


def generate(rng):
    return [rng.randint(1, 20000)]
