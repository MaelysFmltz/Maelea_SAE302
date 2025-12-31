import socket, threading

ROUTER_NAME = input("Nom du routeur : ")
LISTEN_PORT = int(input("Port d'écoute : "))

with open(f"../keys/{ROUTER_NAME}.private") as f:
    d, n = map(int, f.read().split(","))

def rsa_decrypt_bytes(data):
    out = bytearray()
    for x in data.decode().split(";"):
        if x:
            out.append(pow(int(x), d, n))
    return bytes(out)

def handle(conn):
    data = conn.recv(65536)
    if not data:
        conn.close()
        return

    try:
        decrypted = rsa_decrypt_bytes(data)
    except:
        print(f"[{ROUTER_NAME}] Mauvaise couche (pas pour moi)")
        conn.close()
        return

    if b"\n" not in decrypted:
        print(f"[{ROUTER_NAME}] En-tête invalide")
        conn.close()
        return

    header, payload = decrypted.split(b"\n", 1)
    header = header.decode()

    if header.startswith("NEXT"):
        _, ip, port = header.split()
        print(f"[{ROUTER_NAME}] → NEXT {ip}:{port}")
        s = socket.socket()
        s.connect((ip, int(port)))
        s.sendall(payload)  
        s.close()

    elif header.startswith("FINAL"):
        _, ip, port = header.split()
        print(f"[{ROUTER_NAME}] → FINAL {ip}:{port}")
        s = socket.socket()
        s.connect((ip, int(port)))
        s.sendall(payload)
        s.close()

    conn.close()

s = socket.socket()
s.bind(("0.0.0.0", LISTEN_PORT))
s.listen(5)
print(f"[{ROUTER_NAME}] En écoute")

while True:
    c, _ = s.accept()
    threading.Thread(target=handle, args=(c,), daemon=True).start()
