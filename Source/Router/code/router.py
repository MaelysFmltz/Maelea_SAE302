import socket
import threading

ROUTER_NAME = input("Nom du routeur : ")
LISTEN_PORT = int(input("Port d'écoute : "))

with open("../keys/private.key") as f:
    d, n = map(int, f.read().split(","))

def rsa_decrypt(data):
    return "".join(chr(pow(int(x), d, n)) for x in data.split(";") if x)

def xor(data, key):
    return bytes(data[i] ^ key[i % len(key)] for i in range(len(data)))

def handle(conn):
    enc = conn.recv(65536).decode()
    text = rsa_decrypt(enc)

    header, rest = text.split("\n", 1)
    key_hex, payload = rest.split("\n", 1)
    key = bytes.fromhex(key_hex)

    clear = xor(payload.encode(), key).decode()

    h, msg = clear.split("\n", 1)

    if h.startswith("NEXT"):
        _, ip, port = h.split()
    else:
        _, ip, port = h.split()

    s = socket.socket()
    s.connect((ip, int(port)))
    s.sendall(msg.encode())
    s.close()

    conn.close()

s = socket.socket()
s.bind(("0.0.0.0", LISTEN_PORT))
s.listen(5)
print(f"[{ROUTER_NAME}] En écoute")

while True:
    c, _ = s.accept()
    threading.Thread(target=handle, args=(c,), daemon=True).start()
