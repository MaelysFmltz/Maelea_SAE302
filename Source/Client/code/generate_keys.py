import random

p = random.randint(100,300)
q = random.randint(100,300)
n = p*q
e = 3

open("../keys/public.key","w").write(f"{e},{n}")
print("[CLIENT] Clés générées")
