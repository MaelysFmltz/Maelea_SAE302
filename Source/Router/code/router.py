import socket
import threading

ROUTER_NAME = input("Nom du routeur : ")
LISTEN_PORT = int(input("Port d'écoute : "))

with open(f"../keys/{ROUTER_NAME}.private") as f:
    d, n = map(int, f.read().split(","))

def rsa_decrypt(data):
    return "".join(chr(pow(int(x), d, n)) for x in data.split(";") if x)

def handle(conn):
    enc = conn.recv(65536).decode()
    try:
        text = rsa_decrypt(enc)
    except:
        print(f"[{ROUTER_NAME}] Mauvaise couche")
        conn.close()
        return

    if "\n" not in text:
        print(f"[{ROUTER_NAME}] En-tête invalide")
        conn.close()
        return

    header, payload = text.split("\n", 1)

    if header.startswith("NEXT"):
        _, ip, port = header.split()
        print(f"[{ROUTER_NAME}] → {ip}:{port}")
        s = socket.socket()
        s.connect((ip, int(port)))
        s.sendall(payload.encode())
        s.close()

    elif header.startswith("FINAL"):
        _, ip, port = header.split()
        print(f"[{ROUTER_NAME}] → Livraison finale")
        s = socket.socket()
        s.connect((ip, int(port)))
        s.sendall(payload.encode())
        s.close()

    conn.close()

s = socket.socket()
s.bind(("0.0.0.0", LISTEN_PORT))
s.listen(5)

print(f"[{ROUTER_NAME}] En écoute sur {LISTEN_PORT}")

while True:
    c, _ = s.accept()
    threading.Thread(target=handle, args=(c,), daemon=True).start()
