import random

def is_prime(n):
    if n < 2:
        return False
    for i in range(2, int(n**0.5)+1):
        if n % i == 0:
            return False
    return True

def gen_prime():
    while True:
        p = random.randint(100, 300)
        if is_prime(p):
            return p

while True:
    p = gen_prime()
    q = gen_prime()
    if p != q:
        break

n = p * q
phi = (p - 1) * (q - 1)

e = 3
while phi % e == 0:
    e += 2

def inv(a, m):
    for x in range(1, m):
        if (a * x) % m == 1:
            return x
    return None

d = inv(e, phi)

if d is None:
    print("Erreur génération clé, relance le script")
    exit(1)

open("../keys/public.key", "w").write(f"{e},{n}")
open("../keys/private.key", "w").write(f"{d},{n}")

print("[ROUTER] Clés RSA générées correctement")
