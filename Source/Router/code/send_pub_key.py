import socket

ROUTER_NAME = input("Nom du routeur (ex: R1) : ")
ROUTER_IP = input("IP du routeur : ")
ROUTER_PORT = input("Port d'écoute du routeur : ")

MASTER_IP = input("IP du master : ")
MASTER_PORT = int(input("Port du master : "))

with open("../keys/public.key", "rb") as f:
    pubkey = f.read().hex()

msg = (
    f"ROUTEUR {ROUTER_NAME}\n"
    f"IP {ROUTER_IP}\n"
    f"PORT {ROUTER_PORT}\n"
    "PUBKEY\n"
    f"{pubkey}\n"
    "END\n"
)

s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.connect((MASTER_IP, MASTER_PORT))
s.sendall(msg.encode())
s.close()

print(f"[{ROUTER_NAME}] Clé publique envoyée au Master")

