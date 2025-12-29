import random

KEY_PATH = "../keys/"

def generate_key():
    key = bytearray()
    for _ in range(32):
        key.append(random.randint(0, 255))
    return bytes(key)

private_key = generate_key()
public_key = bytes([b ^ 0xAA for b in private_key])

with open(KEY_PATH + "private.key", "wb") as f:
    f.write(private_key)

with open(KEY_PATH + "public.key", "wb") as f:
    f.write(public_key)

print("[ROUTEUR] Clés générées")
