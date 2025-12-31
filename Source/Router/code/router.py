import socket, threading

ROUTER_NAME = input("Nom du routeur : ")
LISTEN_PORT = int(input("Port d'écoute : "))

with open(f"../keys/{ROUTER_NAME}.private") as f:
    d,n = map(int,f.read().split(","))

session_key = None

def rsa_decrypt(data):
    return bytes(pow(int(x),d,n) for x in data.split(";") if x)

def xor(data,key):
    return bytes(data[i]^key[i%len(key)] for i in range(len(data)))

def handle(c):
    global session_key
    raw = c.recv(65536)

    if raw.startswith(b"KEY|"):
        enc = raw[4:].decode()
        session_key = rsa_decrypt(enc)
        print(f"[{ROUTER_NAME}] Clé de session reçue")
        c.close()
        return

    if not session_key:
        print(f"[{ROUTER_NAME}] Pas de clé")
        c.close()
        return

    try:
        text = xor(raw,session_key).decode()
    except:
        print(f"[{ROUTER_NAME}] Mauvaise couche")
        c.close()
        return

    header,payload = text.split("\n",1)

    if header.startswith("NEXT"):
        _,ip,port = header.split()
        print(f"[{ROUTER_NAME}] → NEXT {ip}:{port}")
        s=socket.socket()
        s.connect((ip,int(port)))
        s.sendall(payload.encode())
        s.close()

    elif header.startswith("FINAL"):
        _,ip,port = header.split()
        print(f"[{ROUTER_NAME}] → FINAL {ip}:{port}")
        s=socket.socket()
        s.connect((ip,int(port)))
        s.sendall(payload.encode())
        s.close()

    c.close()

s=socket.socket()
s.bind(("0.0.0.0",LISTEN_PORT))
s.listen(5)
print(f"[{ROUTER_NAME}] En écoute")

while True:
    c,_=s.accept()
    threading.Thread(target=handle,args=(c,),daemon=True).start()
