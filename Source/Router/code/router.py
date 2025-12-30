import socket
import threading

ROUTER_NAME = input("Nom du routeur : ")
LISTEN_PORT = int(input("Port d'écoute : "))

with open("../keys/private.key", "r") as f:
    d, n = map(int, f.read().split(","))

def rsa_decrypt(data):
    return "".join(chr(pow(int(c), d, n)) for c in data.split(";"))

def handle_client(conn, addr):
    encrypted = conn.recv(65536).decode()
    text = rsa_decrypt(encrypted)

    if "\n" not in text:
        conn.close()
        return

    header, payload = text.split("\n", 1)

    if header.startswith("NEXT"):
        _, ip, port = header.split()
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.connect((ip, int(port)))
        s.sendall(payload.encode())
        s.close()

    elif header.startswith("FINAL"):
        _, ip, port = header.split()
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.connect((ip, int(port)))
        s.sendall(payload.encode())
        s.close()

    conn.close()

def start():
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.bind(("0.0.0.0", LISTEN_PORT))
    s.listen(5)
    print(f"[{ROUTER_NAME}] En écoute sur {LISTEN_PORT}")
    while True:
        c, a = s.accept()
        threading.Thread(target=handle_client, args=(c, a), daemon=True).start()

start()
