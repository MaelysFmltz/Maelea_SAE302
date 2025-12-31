import socket, threading, random
from PyQt5.QtWidgets import *

CLIENT_NAME = input("Nom du client : ")
MY_PORT = int(input("Port du client : "))
MASTER_IP = input("IP du master : ")
MASTER_PORT = int(input("Port du master : "))

with open(f"../keys/{CLIENT_NAME}.public") as f:
    CLIENT_PUBKEY = f.read().strip()

def rsa_encrypt(text, pub):
    e,n = pub
    return ";".join(str(pow(ord(c), e, n)) for c in text)

def register_client():
    msg = f"CLIENT {CLIENT_NAME} {MY_PORT} {CLIENT_PUBKEY}\n"
    s = socket.socket()
    s.connect((MASTER_IP, MASTER_PORT))
    s.sendall(msg.encode())
    s.close()

def ask(cmd):
    s = socket.socket()
    s.connect((MASTER_IP, MASTER_PORT))
    s.sendall(cmd)
    data=b""
    while True:
        p=s.recv(4096)
        if not p: break
        data+=p
    s.close()
    return data.decode()

def get_clients():
    res=[]
    for l in ask(b"CLIENT GET_CLIENTS").splitlines():
        if l=="END": break
        p=l.split()
        res.append({"name":p[1],"ip":p[2],"port":int(p[3])})
    return res

def get_routeurs():
    res=[]
    for l in ask(b"CLIENT GET_ROUTEURS").splitlines():
        if l=="END": break
        p=l.split()
        e,n=map(int,p[4].split(","))
        res.append({"name":p[1],"ip":p[2],"port":int(p[3]),"pub":(e,n)})
    return res

class ClientUI(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Client "+CLIENT_NAME)
        self.setGeometry(300,200,400,550)

        l=QVBoxLayout()
        self.list=QListWidget()
        self.spin=QSpinBox(); self.spin.setMinimum(3)
        self.path=QLabel("Chemin :")
        self.msg=QTextEdit()
        self.log=QTextEdit(); self.log.setReadOnly(True)
        b=QPushButton("Envoyer")
        r=QPushButton("Rafraîchir")

        b.clicked.connect(self.send)
        r.clicked.connect(self.refresh)

        l.addWidget(self.list)
        l.addWidget(self.spin)
        l.addWidget(self.path)
        l.addWidget(self.msg)
        l.addWidget(b)
        l.addWidget(r)
        l.addWidget(self.log)
        self.setLayout(l)

        self.refresh()

    def refresh(self):
        self.list.clear()
        for c in get_clients():
            if c["name"]!=CLIENT_NAME:
                self.list.addItem(f"{c['name']} ({c['ip']}:{c['port']})")

    def send(self):
        item=self.list.currentItem()
        if not item: return

        routers=get_routeurs()
        path=random.sample(routers, self.spin.value())
        self.path.setText("Chemin : "+" → ".join(r["name"] for r in path))

        dest=item.text().split()[0]
        dest=next(c for c in get_clients() if c["name"]==dest)

        payload=f"FINAL {dest['ip']} {dest['port']}\n"+self.msg.toPlainText()

        for r in reversed(path):
            payload=f"NEXT {r['ip']} {r['port']}\n"+payload
            payload=rsa_encrypt(payload, r["pub"])

        s=socket.socket()
        s.connect((path[0]["ip"], path[0]["port"]))
        s.sendall(payload.encode())
        s.close()
        self.log.append("Message envoyé")

def listen():
    s=socket.socket()
    s.bind(("0.0.0.0",MY_PORT))
    s.listen(5)
    while True:
        c,_=s.accept()
        print("Reçu:",c.recv(4096).decode())
        c.close()

register_client()
threading.Thread(target=listen,daemon=True).start()

app=QApplication([])
w=ClientUI()
w.show()
app.exec_()
