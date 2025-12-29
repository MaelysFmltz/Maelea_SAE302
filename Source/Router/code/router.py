import socket
import threading

ROUTER_NAME = input("Nom du routeur (ex: R1) : ")
LISTEN_PORT = int(input("Port d'écoute du routeur : "))

with open("../keys/private.key", "rb") as f:
    private_key = f.read()
    
def xor_bytes(data, key):
    result = bytearray()
    for i in range(len(data)):
        result.append(data[i] ^ key[i % len(key)])
    return bytes(result)

def handle_client(conn, addr):
    try:
        encrypted = conn.recv(65536)
        if not encrypted:
            return

        decrypted = xor_bytes(encrypted, private_key)
        text = decrypted.decode(errors="ignore")

        if "\n" in text:
            header, payload = text.split("\n", 1)
        else:
            header = text
            payload = ""

        if header.startswith("NEXT"):
            _, ip, port = header.split(" ")
            print(f"[{ROUTER_NAME}] Transfert vers routeur {ip}:{port}")

            s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            s.connect((ip, int(port)))
            s.sendall(payload.encode())
            s.close()

        elif header.startswith("FINAL"):
            _, ip, port = header.split(" ")
            print(f"[{ROUTER_NAME}] Livraison au client {ip}:{port}")

            s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            s.connect((ip, int(port)))
            s.sendall(payload.encode())
            s.close()

        else:
            print(f"[{ROUTER_NAME}] Entête inconnue")

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

