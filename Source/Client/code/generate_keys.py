import random

def gen():
    return random.randint(100, 300)

e = 3
n = gen() * gen()

open("../keys/public.key", "w").write(f"{e},{n}")
