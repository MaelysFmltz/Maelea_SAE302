import random

key = bytes(random.randint(0,255) for _ in range(16))
open("../keys/session.key","wb").write(key)

print("[CLIENT] Clé de session générée")
