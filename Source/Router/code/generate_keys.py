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

def inv(a, m):
    for x in range(1, m):
        if (a * x) % m == 1:
            return x

d = inv(e, phi)

open("../keys/public.key", "w").write(f"{e},{n}")
open("../keys/private.key", "w").write(f"{d},{n}")

print("[ROUTER] Clés RSA générées")
