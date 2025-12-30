import socket
import threading

ROUTER_NAME = input("Nom du routeur : ")
LISTEN_PORT = int(input("Port : "))

with open("../keys/private.key") as f:
    d, n = map(int, f.read().split(","))

def rsa_decrypt(data):
    return "".join(chr(pow(int(x), d, n)) for x in data.split(";") if x)

def handle(conn):
    try:
        enc = conn.recv(65536).decode()
        text = rsa_decrypt(enc)
    except:
        conn.close()
        return

    if "\n" not in text:
        conn.close()
        return

    header, payload = text.split("\n", 1)

    if header.startswith("NEXT"):
        _, ip, port = header.split()
        s = socket.socket()
        s.connect((ip, int(port)))
        s.sendall(payload.encode())
        s.close()

    elif header.startswith("FINAL"):
        _, ip, port = header.split()
        s = socket.socket()
        s.connect((ip, int(port)))
        s.sendall(payload.encode())
        s.close()

    conn.close()

s = socket.socket()
s.bind(("0.0.0.0", LISTEN_PORT))
s.listen(5)
print(f"[{ROUTER_NAME}] En écoute")

while True:
    c, _ = s.accept()
    threading.Thread(target=handle, args=(c,), daemon=True).start()
