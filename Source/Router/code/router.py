import socket
import threading

ROUTER_NAME = input("Nom du routeur (ex: R1) : ")
LISTEN_PORT = int(input("Port d'écoute du routeur : "))

KEY_PATH = "../keys/"
PRIVATE_KEY_FILE = KEY_PATH + "private.key"

def xor_bytes(data, key):
    result = bytearray()
    for i in range(len(data)):
        result.append(data[i] ^ key[i % len(key)])
    return bytes(result)

with open(PRIVATE_KEY_FILE, "rb") as f:
    private_key = f.read()

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
            parts = header.split(" ")
            next_ip = parts[1]
            next_port = int(parts[2])

            print("[" + ROUTER_NAME + "] Transfert vers " + next_ip + ":" + str(next_port))

            s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            s.connect((next_ip, next_port))
            s.sendall(payload.encode())
            s.close()
        else:
            print("\n===== MESSAGE FINAL =====")
            print(payload)
            print("=========================\n")

    except Exception as e:
        print("[" + ROUTER_NAME + "] Erreur :", e)
    finally:
        conn.close()

def start_router():
    print("[" + ROUTER_NAME + "] En écoute sur le port " + str(LISTEN_PORT))

    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.bind(("0.0.0.0", LISTEN_PORT))
    server.listen(5)

    while True:
        conn, addr = server.accept()
        t = threading.Thread(target=handle_client, args=(conn, addr))
        t.start()

if __name__ == "__main__":
    start_router()
