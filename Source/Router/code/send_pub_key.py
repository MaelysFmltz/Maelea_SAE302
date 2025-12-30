import socket

ROUTER_NAME = input("Nom du routeur : ")
ROUTER_IP = input("IP du routeur : ")
ROUTER_PORT = input("Port d'écoute du routeur : ")

MASTER_IP = input("IP du master : ")
MASTER_PORT = int(input("Port du master : "))

with open(f"keys/{ROUTER_NAME}.public") as f:
    pubkey = f.read().strip()

msg = (
    f"ROUTEUR {ROUTER_NAME}\n"
    f"IP {ROUTER_IP}\n"
    f"PORT {ROUTER_PORT}\n"
    "PUBKEY\n"
    f"{pubkey}\n"
    "END\n"
)

s = socket.socket()
s.connect((MASTER_IP, MASTER_PORT))
s.sendall(msg.encode())
s.close()

print(f"[{ROUTER_NAME}] Clé publique envoyée au Master")
