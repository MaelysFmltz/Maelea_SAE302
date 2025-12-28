import random

KEY_PATH = "../keys/"

def gen_key():
    return bytes(random.randint(0, 255) for _ in range(32))

priv = gen_key()
pub = bytes([b ^ 0xAA for b in priv])

open(KEY_PATH + "private.key", "wb").write(priv)
open(KEY_PATH + "public.key", "wb").write(pub)

print("[CLIENT] Clés générées")

