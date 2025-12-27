import socket

ROUTER_NAME = input("Nom du routeur (ex: R1) : ")
ROUTER_PORT = input("Port d'écoute du routeur : ")
ROUTER_IP = input("IP du routeur (ex: 127.0.0.1) : ")

MASTER_IP = input("IP du master : ")
MASTER_PORT = int(input("Port du master : "))

PUBKEY_FILE = "../keys/public.key"

def read_pubkey():
    with open(PUBKEY_FILE, "rb") as f:
        return f.read().hex()

def send_key():
    pubkey = read_pubkey()

    msg = (
        "ROUTEUR " + ROUTER_NAME + "\n"
        "IP " + ROUTER_IP + "\n"
        "PORT " + ROUTER_PORT + "\n"
        "PUBKEY\n"
        + pubkey + "\n"
        "END\n"
    )

    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.connect((MASTER_IP, MASTER_PORT))
    s.sendall(msg.encode())
    s.close()

    print("[ROUTEUR] Clé publique envoyée au master.")

if __name__ == "__main__":
    send_key()



