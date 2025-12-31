import os, random

CLIENT_NAME = input("Nom du client : ")

os.makedirs("../keys", exist_ok=True)

key = bytes(random.randint(0,255) for _ in range(32))
open(f"../keys/{CLIENT_NAME}.session","wb").write(key)

print(f"[{CLIENT_NAME}] Clé de session générée")
