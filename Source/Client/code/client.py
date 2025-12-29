import socket
import threading
import random
from PyQt5.QtWidgets import (
    QApplication, QWidget, QVBoxLayout,
    QPushButton, QListWidget, QTextEdit, QLabel, QSpinBox
)

CLIENT_NAME = input("Nom du client : ")
MY_PORT = int(input("Port du client : "))
MASTER_IP = input("IP du master : ")
MASTER_PORT = int(input("Port du master : "))

def xor_bytes(data, key):
    result = bytearray()
    for i in range(len(data)):
        result.append(data[i] ^ key[i % len(key)])
    return bytes(result)

with open("../keys/public.key", "rb") as f:
    CLIENT_PUBKEY = f.read()
def register_client():
    msg = (
        "CLIENT " + CLIENT_NAME + " " +
        str(MY_PORT) + " " +
        CLIENT_PUBKEY.hex() + "\n"
    )

    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.connect((MASTER_IP, MASTER_PORT))
    s.sendall(msg.encode())
    s.recv(1024)
    s.close()

def get_from_master(cmd):
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.connect((MASTER_IP, MASTER_PORT))
    s.sendall(cmd)
    data = b""
    while True:
        part = s.recv(4096)
        if not part:
            break
        data += part
    s.close()
    return data.decode()

def get_clients():
    data = get_from_master(b"CLIENT GET_CLIENTS")
    res = []
    for line in data.splitlines():
        if line == "END":
            break
        parts = line.split(" ")
        if parts[0] == "CLIENT":
            res.append({
                "name": parts[1],
                "ip": parts[2],
                "port": int(parts[3])
            })
    return res

def get_routeurs():
    data = get_from_master(b"CLIENT GET_ROUTEURS")
    res = []
    for line in data.splitlines():
        if line == "END":
            break
        parts = line.split(" ")
        if parts[0] == "ROUTEUR":
            res.append({
                "name": parts[1],
                "ip": parts[2],
                "port": int(parts[3]),
                "pubkey": bytes.fromhex(parts[4])
            })
    return res

def build_onion(message, route, dest_ip, dest_port):
    payload = ("FINAL " + dest_ip + " " + str(dest_port) + "\n" + message).encode()

    for r in reversed(route):
        header = "NEXT " + r["ip"] + " " + str(r["port"]) + "\n"
        payload = xor_bytes((header + payload.decode()).encode(), r["pubkey"])

    return payload

def send_to_router(payload, router, log):
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.connect((router["ip"], router["port"]))
        s.sendall(payload)
        s.close()
        log("Message envoyé")
    except Exception as e:
        log("Erreur : " + str(e))

def listen_messages(log):
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.bind(("0.0.0.0", MY_PORT))
    server.listen(5)
    log("Client en écoute")

    while True:
        conn, addr = server.accept()
        data = conn.recv(4096)
        if data:
            log("Reçu : " + data.decode(errors="ignore"))
        conn.close()

class ClientUI(QWidget):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("Client " + CLIENT_NAME)
        self.setGeometry(300, 200, 450, 550)

        layout = QVBoxLayout()

        layout.addWidget(QLabel("Destinataire"))
        self.clients_list = QListWidget()
        layout.addWidget(self.clients_list)

        layout.addWidget(QLabel("Nombre de routeurs (min 3)"))
        self.spin = QSpinBox()
        self.spin.setMinimum(3)
        self.spin.setMaximum(10)
        self.spin.setValue(3)
        layout.addWidget(self.spin)

        self.route_label = QLabel("Chemin : ")
        layout.addWidget(self.route_label)

        layout.addWidget(QLabel("Message"))
        self.msg_box = QTextEdit()
        layout.addWidget(self.msg_box)

        self.send_btn = QPushButton("Envoyer")
        self.send_btn.clicked.connect(self.send_message)
        layout.addWidget(self.send_btn)

        self.refresh_btn = QPushButton("Rafraîchir")
        self.refresh_btn.clicked.connect(self.refresh_clients)
        layout.addWidget(self.refresh_btn)

        layout.addWidget(QLabel("Journal"))
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
        self.log("Liste mise à jour")

    def send_message(self):
        item = self.clients_list.currentItem()
        if not item:
            self.log("Aucun destinataire")
            return

        message = self.msg_box.toPlainText().strip()
        if not message:
            self.log("Message vide")
            return

        routers = get_routeurs()
        nb = self.spin.value()

        if len(routers) < nb:
            self.log("Pas assez de routeurs disponibles")
            return

        path = random.sample(routers, nb)

        dest_name = item.text().split(" ")[0]
        dest = next(c for c in get_clients() if c["name"] == dest_name)

        self.route_label.setText(
            "Chemin : " + " → ".join(r["name"] for r in path)
        )

        payload = build_onion(message, path, dest["ip"], dest["port"])

        threading.Thread(
            target=send_to_router,
            args=(payload, path[0], self.log),
            daemon=True
        ).start()
if __name__ == "__main__":
    register_client()
    app = QApplication([])
    window = ClientUI()
    window.show()
    threading.Thread(
        target=listen_messages,
        args=(window.log,),
        daemon=True
    ).start()
    app.exec_()

