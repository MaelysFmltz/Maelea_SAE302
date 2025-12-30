import random

def is_prime(n):
    if n < 2:
        return False
    for i in range(2, int(n**0.5) + 1):
        if n % i == 0:
            return False
    return True

def gen_prime():
    while True:
        p = random.randint(100, 300)
        if is_prime(p):
            return p

p = gen_prime()
q = gen_prime()
n = p * q

e = 3
while (p - 1) * (q - 1) % e == 0:
    e += 2

with open("../keys/public.key", "w") as f:
    f.write(f"{e},{n}")

print("[CLIENT] Clé publique générée")
