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
