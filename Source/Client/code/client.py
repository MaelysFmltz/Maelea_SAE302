import socket, threading, random
from PyQt5.QtWidgets import *

CLIENT_NAME = input("Nom du client : ")
MY_PORT = int(input("Port du client : "))
MASTER_IP = input("IP du master : ")
MASTER_PORT = int(input("Port du master : "))

with open("../keys/session.key","rb") as f:
    session_key = f.read()

def xor(data,key):
    return bytes(data[i]^key[i%len(key)] for i in range(len(data)))

def rsa_encrypt(data,pub):
    e,n=pub
    return ";".join(str(pow(b,e,n)) for b in data)

def ask(cmd):
    s=socket.socket()
    s.connect((MASTER_IP,MASTER_PORT))
    s.sendall(cmd)
    data=b""
    while True:
        p=s.recv(4096)
        if not p: break
        data+=p
    s.close()
    return data.decode()

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
        l=QVBoxLayout()
        self.msg=QTextEdit()
        self.log=QTextEdit(); self.log.setReadOnly(True)
        b=QPushButton("Envoyer")
        b.clicked.connect(self.send)
        l.addWidget(self.msg); l.addWidget(b); l.addWidget(self.log)
        self.setLayout(l)

    def send(self):
        routers=get_routeurs()
        path=random.sample(routers,3)
        self.log.append("Chemin: "+" → ".join(r["name"] for r in path))

        payload=f"FINAL 127.0.0.1 {MY_PORT}\n{self.msg.toPlainText()}".encode()
        payload=xor(payload,session_key)

        for r in reversed(path):
            enc=rsa_encrypt(session_key,r["pub"])
            s=socket.socket()
            s.connect((r["ip"],r["port"]))
            s.sendall(b"KEY|"+enc.encode())
            s.close()
            payload=xor(payload,session_key)

        s=socket.socket()
        s.connect((path[0]["ip"],path[0]["port"]))
        s.sendall(payload)
        s.close()
        self.log.append("Message envoyé")

app=QApplication([])
w=ClientUI()
w.show()
app.exec_()
