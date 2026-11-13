ID = "two_sum"
TITLE = "Dos sumas"
DIFFICULTY = "easy"
FUNCTION = "two_sum"
PROMPT = "Escribe two_sum(nums, target): devuelve [i, j] con i < j tales que nums[i] + nums[j] == target. Siempre hay una solución."
VISIBLE = [([[2, 7, 11, 15], 9], [0, 1]), ([[3, 2, 4], 6], [1, 2]), ([[3, 3], 6], [0, 1]),
           ([[-1, -2, -3, -4, -5], -8], [2, 4])]
TIMEOUT = 10.0


def reference(nums, target):
    for i in range(len(nums)):
        for j in range(i + 1, len(nums)):
            if nums[i] + nums[j] == target:
                return [i, j]


def generate(rng):
    n = rng.randint(2, 40)
    nums = [rng.randint(-50, 50) for _ in range(n)]
    i, j = sorted(rng.sample(range(n), 2))
    return [nums, nums[i] + nums[j]]


def CHECK(args, out):
    nums, target = args
    return (isinstance(out, list) and len(out) == 2 and all(type(k) is int for k in out)
            and 0 <= out[0] < out[1] < len(nums) and nums[out[0]] + nums[out[1]] == target)
