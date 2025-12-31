import socket, threading

ROUTER_NAME = input("Nom du routeur : ")
LISTEN_PORT = int(input("Port d'écoute : "))

with open(f"../keys/{ROUTER_NAME}.private") as f:
    d, n = map(int, f.read().split(","))

def rsa_decrypt(data):
    out = []
    for x in data.split(";"):
        if not x:
            continue
        out.append(chr(pow(int(x), d, n)))
    return "".join(out)

def handle(conn):
    try:
        enc = conn.recv(65536).decode()
    except:
        conn.close()
        return

    try:
        text = rsa_decrypt(enc)
    except:
        print(f"[{ROUTER_NAME}] Mauvaise couche (pas pour moi)")
        conn.close()
        return

    if "\n" not in text:
        print(f"[{ROUTER_NAME}] En-tête invalide")
        conn.close()
        return

    header, rest = text.split("\n", 1)

    if header.startswith("NEXT"):
        _, ip, port = header.split()
        print(f"[{ROUTER_NAME}] → NEXT {ip}:{port}")
        s = socket.socket()
        s.connect((ip, int(port)))
        s.sendall(rest.encode())  
        s.close()

    elif header.startswith("FINAL"):
        _, ip, port = header.split()
        print(f"[{ROUTER_NAME}] → FINAL {ip}:{port}")
        s = socket.socket()
        s.connect((ip, int(port)))
        s.sendall(rest.encode())
        s.close()

    else:
        print(f"[{ROUTER_NAME}] En-tête inconnu")

    conn.close()

s = socket.socket()
s.bind(("0.0.0.0", LISTEN_PORT))
s.listen(5)
print(f"[{ROUTER_NAME}] En écoute")

while True:
    c, _ = s.accept()
    threading.Thread(target=handle, args=(c,), daemon=True).start()
