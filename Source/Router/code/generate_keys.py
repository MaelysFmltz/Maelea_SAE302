import random
from sympy import isprime

def gen_prime():
    while True:
        p = random.randint(100, 300)
        if isprime(p):
            return p

p = gen_prime()
q = gen_prime()
n = p * q
phi = (p - 1) * (q - 1)

e = 3
while phi % e == 0:
    e += 2

def modinv(a, m):
    for x in range(1, m):
        if (a * x) % m == 1:
            return x

d = modinv(e, phi)

with open("../keys/public.key", "w") as f:
    f.write(f"{e},{n}")

with open("../keys/private.key", "w") as f:
    f.write(f"{d},{n}")

print("[ROUTEUR] Clés RSA générées")
