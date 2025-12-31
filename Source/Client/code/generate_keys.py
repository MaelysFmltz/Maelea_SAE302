import random, os

CLIENT_NAME = input("Nom du client : ")
os.makedirs("../keys", exist_ok=True)

p = random.randint(100,300)
q = random.randint(100,300)
n = p*q
e = 3

open(f"../keys/{CLIENT_NAME}.public","w").write(f"{e},{n}")
print(f"[{CLIENT_NAME}] Clé générée")
