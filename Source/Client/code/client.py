import socket
import threading
import random
from PyQt5.QtWidgets import QApplication, QWidget, QVBoxLayout, QPushButton, QListWidget, QTextEdit, QLabel, QSpinBox

CLIENT_NAME = input("Nom du client : ")
MY_PORT = int(input("Port du client : "))
MASTER_IP = input("IP du master : ")
MASTER_PORT = int(input("Port du master : "))

with open("../keys/public.key", "r") as f:
    CLIENT_PUBKEY = f.read()

def rsa_encrypt(text, pubkey):
    e, n = pubkey
    return ";".join(str(pow(ord(c), e, n)) for c in text)

def register_client():
    msg = f"CLIENT {CLIENT_NAME} {MY_PORT} {CLIENT_PUBKEY}\n"
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.connect((MASTER_IP, MASTER_PORT))
    s.sendall(msg.encode())
    s.close()

def get(cmd):
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.connect((MASTER_IP, MASTER_PORT))
    s.sendall(cmd)
    data = b""
    while True:
        p = s.recv(4096)
        if not p:
            break
        data += p
    s.close()
    return data.decode()

def get_clients():
    res = []
    for l in get(b"CLIENT GET_CLIENTS").splitlines():
        if l == "END":
            break
        p = l.split()
        res.append({"name": p[1], "ip": p[2], "port": int(p[3])})
    return res

def get_routeurs():
    res = []
    for l in get(b"CLIENT GET_ROUTEURS").splitlines():
        if l == "END":
            break
        p = l.split()
        e, n = map(int, p[4].split(","))
        res.append({"name": p[1], "ip": p[2], "port": int(p[3]), "pubkey": (e, n)})
    return res

def build_onion(msg, path, dip, dport):
    payload = f"FINAL {dip} {dport}\n{msg}"
    for r in reversed(path):
        payload = f"NEXT {r['ip']} {r['port']}\n{payload}"
        payload = rsa_encrypt(payload, r["pubkey"])
    return payload

def send(payload, router):
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.connect((router["ip"], router["port"]))
    s.sendall(payload.encode())
    s.close()

def listen(log):
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.bind(("0.0.0.0", MY_PORT))
    s.listen(5)
    while True:
        c, _ = s.accept()
        log(c.recv(4096).decode())
        c.close()

class UI(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle(CLIENT_NAME)
        l = QVBoxLayout()
        self.list = QListWidget()
        self.spin = QSpinBox()
        self.spin.setMinimum(3)
        self.msg = QTextEdit()
        self.logbox = QTextEdit()
        self.logbox.setReadOnly(True)
        b = QPushButton("Envoyer")
        r = QPushButton("Rafraîchir")
        b.clicked.connect(self.send)
        r.clicked.connect(self.refresh)
        l.addWidget(self.list)
        l.addWidget(self.spin)
        l.addWidget(self.msg)
        l.addWidget(b)
        l.addWidget(r)
        l.addWidget(self.logbox)
        self.setLayout(l)
        self.refresh()

    def log(self, t):
        self.logbox.append(t)

    def refresh(self):
        self.list.clear()
        for c in get_clients():
            if c["name"] != CLIENT_NAME:
                self.list.addItem(f"{c['name']} {c['ip']} {c['port']}")

    def send(self):
        it = self.list.currentItem()
        if not it:
            return
        dest = it.text().split()
        path = random.sample(get_routeurs(), self.spin.value())
        payload = build_onion(self.msg.toPlainText(), path, dest[1], dest[2])
        threading.Thread(target=send, args=(payload, path[0]), daemon=True).start()

register_client()
app = QApplication([])
ui = UI()
ui.show()
threading.Thread(target=listen, args=(ui.log,), daemon=True).start()
app.exec_()
