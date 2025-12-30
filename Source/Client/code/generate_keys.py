import random

e = 3
n = random.randint(1000, 3000)

with open("../keys/public.key", "w") as f:
    f.write(f"{e},{n}")

print("[CLIENT] Clé publique générée")





