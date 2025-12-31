import socket, threading, time, os

ROUTER_NAME = input("Nom du routeur : ")
PORT = int(input("Port d'écoute : "))

os.makedirs("../logs", exist_ok=True)
LOG_FILE = f"../logs/{ROUTER_NAME}.log"

def log(msg):
    ts = time.strftime("%Y-%m-%d %H:%M:%S")
    line = f"[{ts}] {msg}"
    print(line)
    with open(LOG_FILE, "a") as f:
        f.write(line + "\n")

with open(f"../keys/{ROUTER_NAME}.private") as f:
    d, n = map(int, f.read().split(","))

def rsa_decrypt(data):
    return "".join(chr(pow(int(x), d, n)) for x in data.split(";") if x)

def handle(conn):
    try:
        enc = conn.recv(65536).decode()
    except:
        log("Erreur réception données")
        conn.close()
        return

    log(f"Données reçues ({len(enc)} octets)")

    try:
        text = rsa_decrypt(enc)
    except:
        log(“ Mauvaise couche (pas pour moi)")
        conn.close()
        return

    if "\n" not in text:
        log("En-tête invalide")
        conn.close()
        return

    header, payload = text.split("\n", 1)

    if header.startswith("NEXT"):
        _, ip, port = header.split()
        log(f"➡ NEXT vers {ip}:{port}")
        s = socket.socket()
        s.connect((ip, int(port)))
        s.sendall(payload.encode())
        s.close()

    elif header.startswith("FINAL"):
        _, ip, port = header.split()
        log(f"🏁 FINAL vers {ip}:{port}")
        s = socket.socket()
        s.connect((ip, int(port)))
        s.sendall(payload.encode())
        s.close()

    else:
        log(f"En-tête inconnu : {header}")

    conn.close()

s = socket.socket()
s.bind(("0.0.0.0", PORT))
s.listen(5)

log(f"Routeur {ROUTER_NAME} en écoute sur le port {PORT}")

while True:
    c, _ = s.accept()
    threading.Thread(target=handle, args=(c,), daemon=True).start()
