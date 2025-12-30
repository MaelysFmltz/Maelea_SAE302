import socket
import threading
import mariadb

LISTEN_PORT = int(input("Port master : "))
DB_HOST = input("DB host : ")
DB_USER = input("DB user : ")
DB_PASS = input("DB pass : ")
DB_NAME = input("DB name : ")

def connect():
    return mariadb.connect(
        host=DB_HOST,
        user=DB_USER,
        password=DB_PASS,
        database=DB_NAME
    )

def handle(c, addr):
    data = c.recv(65536).decode()

    if data.startswith("ROUTEUR"):
        lines = data.splitlines()
        name = ip = port = pub = ""
        read = False
        for l in lines:
            if l.startswith("ROUTEUR"):
                name = l.split()[1]
            elif l.startswith("IP"):
                ip = l.split()[1]
            elif l.startswith("PORT"):
                port = l.split()[1]
            elif l == "PUBKEY":
                read = True
            elif l == "END":
                break
            elif read:
                pub += l

        db = connect()
        cur = db.cursor()
        cur.execute(
            "INSERT INTO routeurs VALUES (?,?,?,?) "
            "ON DUPLICATE KEY UPDATE ip=?,port=?,public_key=?",
            (name, ip, port, pub, ip, port, pub)
        )
        db.commit()
        db.close()
        c.sendall(b"OK")

    elif data.startswith("CLIENT ") and not data.startswith("CLIENT GET"):
        _, name, port, pub = data.split(" ", 3)
        db = connect()
        cur = db.cursor()
        cur.execute(
            "INSERT INTO clients VALUES (?,?,?,?) "
            "ON DUPLICATE KEY UPDATE ip=?,port=?,public_key=?",
            (name, addr[0], port, pub, addr[0], port, pub)
        )
        db.commit()
        db.close()
        c.sendall(b"OK")

    elif data == "CLIENT GET_CLIENTS":
        db = connect()
        cur = db.cursor()
        cur.execute("SELECT * FROM clients")
        out = "\n".join(f"CLIENT {a} {b} {c} {d}" for a,b,c,d in cur.fetchall())
        c.sendall((out + "\nEND").encode())
        db.close()

    elif data == "CLIENT GET_ROUTEURS":
        db = connect()
        cur = db.cursor()
        cur.execute("SELECT * FROM routeurs")
        out = "\n".join(f"ROUTEUR {a} {b} {c} {d}" for a,b,c,d in cur.fetchall())
        c.sendall((out + "\nEND").encode())
        db.close()

    c.close()

s = socket.socket()
s.bind(("0.0.0.0", LISTEN_PORT))
s.listen(5)
print("[MASTER] OK")

while True:
    c, a = s.accept()
    threading.Thread(target=handle, args=(c,a), daemon=True).start()
