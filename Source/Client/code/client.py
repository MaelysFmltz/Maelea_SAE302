import socket
import threading
import random
from PyQt5.QtWidgets import (
    QApplication, QWidget, QVBoxLayout,
    QPushButton, QListWidget, QTextEdit, QLabel
)

CLIENT_NAME = input("Nom du client (ex: C1) : ")
MY_PORT = int(input("Port d'écoute du client : "))
MASTER_IP = input("IP du master : ")
MASTER_PORT = int(input("Port du master : "))


def xor_bytes(data, key):
    out = bytearray()
    for i in range(len(data)):
        out.append(data[i] ^ key[i % len(key)])
    return bytes(out)


with open("../keys/public.key", "rb") as f:
    CLIENT_PUBKEY = f.read()


def register_client():
    msg = (
        "CLIENT " + CLIENT_NAME + " " +
        str(MY_PORT) + " " +
        CLIENT_PUBKEY.hex()
    )

    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.connect((MASTER_IP, MASTER_PORT))
    s.sendall(msg.encode())
    s.close()

def get_from_master(cmd):
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.connect((MASTER_IP, MASTER_PORT))
    s.sendall(cmd)
    data = b""
    while True:
        chunk = s.recv(65536)
        if not chunk:
            break
        data += chunk
    s.close()
    return data.decode()

def get_clients():
    data = get_from_master(b"GET_CLIENTS")
    clients = []
    for line in data.splitlines():
        parts = line.split(" ")
        if len(parts) == 4:
            clients.append({
                "name": parts[0],
                "ip": parts[1],
                "port": int(parts[2])
            })
    return clients

def get_routeurs():
    data = get_from_master(b"GET_ROUTEURS")
    routers = []
    for line in data.splitlines():
        parts = line.split(" ")
        if len(parts) == 4:
            routers.append({
                "name": parts[0],
                "ip": parts[1],
                "port": int(parts[2]),
                "pubkey": bytes.fromhex(parts[3])
            })
    return routers



def build_onion(message, route):
    payload = message.encode()
    for r in reversed(route):
        payload = xor_bytes(payload, r["pubkey"])
        header = ("NEXT " + r["ip"] + " " + str(r["port"]) + "\n").encode()
        payload = header + payload
    return payload


def send_to_router(payload, router, log):
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.connect((router["ip"], router["port"]))
        s.sendall(payload)
        s.close()
        log("[OK] Message envoyé vers " + router["name"])
    except Exception as e:
        log("[ERREUR] Envoi échoué : " + str(e))


def listen_messages(log):
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.bind(("0.0.0.0", MY_PORT))
    server.listen(5)
    log("[INFO] En écoute sur le port " + str(MY_PORT))

    while True:
        conn, addr = server.accept()
        data = conn.recv(65536)
        if data:
            log("[REÇU] " + data.decode(errors="ignore"))
        conn.close()


class ClientUI(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Client " + CLIENT_NAME)
        self.setGeometry(200, 200, 400, 550)

        layout = QVBoxLayout()

        layout.addWidget(QLabel("Destinataire :"))
        self.clients_list = QListWidget()
        layout.addWidget(self.clients_list)

        layout.addWidget(QLabel("Message :"))
        self.msg_box = QTextEdit()
        layout.addWidget(self.msg_box)

        self.btn_send = QPushButton("Envoyer anonymement")
        self.btn_send.clicked.connect(self.send_message)
        layout.addWidget(self.btn_send)

        self.btn_refresh = QPushButton("Rafraîchir")
        self.btn_refresh.clicked.connect(self.refresh_clients)
        layout.addWidget(self.btn_refresh)

        layout.addWidget(QLabel("Logs :"))
        self.logs = QTextEdit()
        self.logs.setReadOnly(True)
        layout.addWidget(self.logs)

        self.setLayout(layout)
        self.refresh_clients()

    def log(self, txt):
        self.logs.append(txt)

    def refresh_clients(self):
        self.clients_list.clear()
        for c in get_clients():
            if c["name"] != CLIENT_NAME:
                self.clients_list.addItem(
                    c["name"] + " (" + c["ip"] + ":" + str(c["port"]) + ")"
                )
        self.log("[OK] Liste clients mise à jour")

    def send_message(self):
        item = self.clients_list.currentItem()
        if not item:
            self.log("[ERREUR] Aucun destinataire")
            return

        message = self.msg_box.toPlainText().strip()
        if not message:
            self.log("[ERREUR] Message vide")
            return

        routers = get_routeurs()
        if len(routers) < 3:
            self.log("[ERREUR] Pas assez de routeurs")
            return

        hops = random.randint(3, min(5, len(routers)))
        path = random.sample(routers, hops)

        payload = build_onion(message, path)
        first_router = path[0]

        t = threading.Thread(
            target=send_to_router,
            args=(payload, first_router, self.log)
        )
        t.start()

if __name__ == "__main__":
    register_client()
    app = QApplication([])
    win = ClientUI()
    win.show()
    threading.Thread(target=listen_messages, args=(win.log,), daemon=True).start()
    app.exec_()
