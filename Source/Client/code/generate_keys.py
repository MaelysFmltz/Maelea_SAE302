import os, random

os.makedirs("../keys", exist_ok=True)

key = bytes(random.randint(0,255) for _ in range(32))
open("../keys/session.key","wb").write(key)

print("[CLIENT] Clé de session générée")
