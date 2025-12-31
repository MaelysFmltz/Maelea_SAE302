import socket
import threading
import random
from PyQt5.QtWidgets import (
    QApplication, QWidget, QVBoxLayout,
    QPushButton, QListWidget, QTextEdit,
    QLabel, QSpinBox
)

CLIENT_NAME = input("Nom du client : ")
MY_PORT = int(input("Port du client : "))
MASTER_IP = input("IP du master : ")
MASTER_PORT = int(input("Port du master : "))

with open(f"../keys/{CLIENT_NAME}.public", "r") as f:
    CLIENT_PUBKEY = f.read().strip()

def rsa_encrypt(text, pubkey):
    e, n = pubkey
    return ";".join(str(pow(ord(c), e, n)) for c in text)


def ask_master(cmd):
    s = socket.socket()
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

def register_client():
    msg = f"CLIENT {CLIENT_NAME} {MY_PORT} {CLIENT_PUBKEY}\n"
    s = socket.socket()
    s.connect((MASTER_IP, MASTER_PORT))
    s.sendall(msg.encode())
    s.close()
    print("[CLIENT] Enregistré auprès du Master")

def get_clients():
    res = []
    for line in ask_master(b"CLIENT GET_CLIENTS").splitlines():
        if line == "END":
            break
        parts = line.split()
        if len(parts) != 4:
            continue
        res.append({
            "name": parts[1],
            "ip": parts[2],
            "port": int(parts[3])
        })
    return res

def get_routeurs():
    res = []
    for line in ask_master(b"CLIENT GET_ROUTEURS").splitlines():
        if line == "END":
            break
        parts = line.split()
        if len(parts) != 5:
            continue
        e, n = map(int, parts[4].split(","))
        res.append({
            "name": parts[1],
            "ip": parts[2],
            "port": int(parts[3]),
            "pubkey": (e, n)
        })
    return res

def build_onion(message, path, dest_ip, dest_port):
    payload = f"FINAL {dest_ip} {dest_port}\n{message}"
    for r in reversed(path):
        payload = f"NEXT {r['ip']} {r['port']}\n{payload}"
        payload = rsa_encrypt(payload, r["pubkey"])
    return payload

def send_to_router(payload, router, log):
    try:
        s = socket.socket()
        s.connect((router["ip"], router["port"]))
        s.sendall(payload.encode())
        s.close()
        log("Message envoyé")
    except Exception as e:
        log(f"Erreur envoi : {e}")

def listen_messages(log):
    server = socket.socket()
    server.bind(("0.0.0.0", MY_PORT))
    server.listen(5)
    log("Client en écoute")
    while True:
        conn, _ = server.accept()
        data = conn.recv(4096)
        if data:
            log("Message reçu : " + data.decode(errors="ignore"))
        conn.close()

class ClientUI(QWidget):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("Client " + CLIENT_NAME)
        self.setGeometry(300, 200, 400, 550)

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
                    f"{c['name']} ({c['ip']}:{c['port']})"
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
            self.log("Pas assez de routeurs")
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
