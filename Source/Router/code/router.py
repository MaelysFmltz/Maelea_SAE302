import socket
import threading

ROUTER_NAME = input("Nom du routeur (ex: R1) : ")
LISTEN_PORT = int(input("Port d'écoute du routeur : "))

with open("../keys/private.key", "r") as f:
    d, n = map(int, f.read().split(","))

PRIVATE_KEY = (d, n)

def rsa_decrypt(data, privkey):
    d, n = privkey
    numbers = data.split(";")
    return "".join(chr(pow(int(x), d, n)) for x in numbers if x)

def handle_client(conn, addr):
    try:
        encrypted = conn.recv(65536).decode()
        if not encrypted:
            return

        try:
            text = rsa_decrypt(encrypted, PRIVATE_KEY)
        except:
            print(f"[{ROUTER_NAME}] Données corrompues")
            return

        if "\n" not in text:
            print(f"[{ROUTER_NAME}] En-tête invalide")
            return

        header, payload = text.split("\n", 1)

        if header.startswith("NEXT"):
            _, ip, port = header.split(" ")
            port = int(port)

            print(f"[{ROUTER_NAME}] → Transfert vers {ip}:{port}")

            s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            s.connect((ip, port))
            s.sendall(payload.encode())
            s.close()

        elif header.startswith("FINAL"):
            _, ip, port = header.split(" ")
            port = int(port)

            print(f"[{ROUTER_NAME}] → Livraison finale vers {ip}:{port}")

            s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            s.connect((ip, port))
            s.sendall(payload.encode())
            s.close()

        else:
            print(f"[{ROUTER_NAME}] En-tête inconnu :", header)

    except Exception as e:
        print(f"[{ROUTER_NAME}] Erreur :", e)

    finally:
        conn.close()

def start_router():
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.bind(("0.0.0.0", LISTEN_PORT))
    server.listen(5)

    print(f"[{ROUTER_NAME}] En écoute sur le port {LISTEN_PORT}")

    while True:
        conn, addr = server.accept()
        threading.Thread(
            target=handle_client,
            args=(conn, addr),
            daemon=True
        ).start()

start_router()
