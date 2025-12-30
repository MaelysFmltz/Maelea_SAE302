import socket
import threading
import mariadb

LISTEN_PORT = int(input("Port d'écoute du Master : "))
DB_HOST = input("DB host : ")
DB_USER = input("DB user : ")
DB_PASS = input("DB password : ")
DB_NAME = input("DB name : ")

def connect_db():
    return mariadb.connect(
        host=DB_HOST,
        user=DB_USER,
        password=DB_PASS,
        database=DB_NAME
    )

def save_router(name, ip, port, pubkey):
    c = connect_db()
    cur = c.cursor()
    cur.execute(
        "INSERT INTO routeurs (router_name, ip, port, public_key) VALUES (?, ?, ?, ?) "
        "ON DUPLICATE KEY UPDATE ip=?, port=?, public_key=?",
        (name, ip, port, pubkey, ip, port, pubkey)
    )
    c.commit()
    c.close()

def save_client(name, ip, port):
    c = connect_db()
    cur = c.cursor()
    cur.execute(
        "INSERT INTO clients (client_name, ip, port) VALUES (?, ?, ?) "
        "ON DUPLICATE KEY UPDATE ip=?, port=?",
        (name, ip, port, ip, port)
    )
    c.commit()
    c.close()

def list_routeurs():
    c = connect_db()
    cur = c.cursor()
    cur.execute("SELECT router_name, ip, port, public_key FROM routeurs")
    rows = cur.fetchall()
    c.close()
    out = []
    for r in rows:
        out.append(f"ROUTEUR {r[0]} {r[1]} {r[2]} {r[3]}")
    out.append("END")
    return "\n".join(out)

def list_clients():
    c = connect_db()
    cur = c.cursor()
    cur.execute("SELECT client_name, ip, port FROM clients")
    rows = cur.fetchall()
    c.close()
    out = []
    for cl in rows:
        out.append(f"CLIENT {cl[0]} {cl[1]} {cl[2]}")
    out.append("END")
    return "\n".join(out)

def handle(conn, addr):
    data = conn.recv(65536).decode().strip()

    if data.startswith("ROUTEUR"):
        lines = data.split("\n")
        name = ip = port = pubkey = ""
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
                pubkey += l
        save_router(name, ip, int(port), pubkey)
        conn.sendall(b"OK")

    elif data.startswith("CLIENT ") and not data.startswith("CLIENT GET"):
        parts = data.split()
        save_client(parts[1], addr[0], int(parts[2]))
        conn.sendall(b"OK")

    elif data == "CLIENT GET_CLIENTS":
        conn.sendall(list_clients().encode())

    elif data == "CLIENT GET_ROUTEURS":
        conn.sendall(list_routeurs().encode())

    conn.close()

s = socket.socket()
s.bind(("0.0.0.0", LISTEN_PORT))
s.listen(5)
print("[MASTER] En écoute")

while True:
    c, a = s.accept()
    threading.Thread(target=handle, args=(c, a), daemon=True).start()
