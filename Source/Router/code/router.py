import socket
import threading

ROUTER_NAME = input("Nom du routeur : ")
LISTEN_PORT = int(input("Port d'écoute : "))

with open("../keys/private.key", "rb") as f:
    private_key = f.read()

def xor_bytes(data, key):
    return bytes(data[i] ^ key[i % len(key)] for i in range(len(data)))

def handle_client(conn, addr):
    encrypted = conn.recv(65536)
    decrypted = xor_bytes(encrypted, private_key)
    text = decrypted.decode(errors="ignore")

    header, payload = text.split("\n", 1)

    if header.startswith("NEXT"):
        _, ip, port = header.split(" ")
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.connect((ip, int(port)))
        s.sendall(payload.encode())
        s.close()

    elif header.startswith("FINAL"):
        _, ip, port = header.split(" ")
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.connect((ip, int(port)))
        s.sendall(payload.encode())
        s.close()

    conn.close()

s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.bind(("0.0.0.0", LISTEN_PORT))
s.listen(5)
print(f"[{ROUTER_NAME}] En écoute sur {LISTEN_PORT}")

while True:
    c, a = s.accept()
    threading.Thread(target=handle_client, args=(c, a), daemon=True).start()



# 4) Création du générateur de clés
cat > generate_keys.py
import random

KEY_PATH = "../keys/"

def generate_key():
    key = bytearray()
    for _ in range(32):
        key.append(random.randint(0, 255))
    return bytes(key)

private_key = generate_key()
public_key = bytes([b ^ 0xAA for b in private_key])

open(KEY_PATH + "private.key", "wb").write(private_key)
open(KEY_PATH + "public.key", "wb").write(public_key)

print("[ROUTEUR] Clés générées")




# 5) Création de l’envoi de clé publique
cat > send_pub_key.pyimport socket

ROUTER_NAME = input("Nom du routeur : ")
ROUTER_IP = input("IP du routeur : ")
ROUTER_PORT = input("Port du routeur : ")

MASTER_IP = input("IP du master : ")
MASTER_PORT = int(input("Port du master : "))

with open("../keys/public.key", "rb") as f:
    pubkey = f.read().hex()

msg = (
    f"ROUTEUR {ROUTER_NAME}\n"
    f"IP {ROUTER_IP}\n"
    f"PORT {ROUTER_PORT}\n"
    "PUBKEY\n"
    f"{pubkey}\n"
    "END\n"
)

s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.connect((MASTER_IP, MASTER_PORT))
s.sendall(msg.encode())
s.close()

print("[ROUTEUR] Clé publique envoyée")

