import socket
import threading
import mariadb

LISTEN_PORT = int(input("Port master : "))
DB_HOST = input("DB host : ")
DB_USER = input("DB user : ")
DB_PASS = input("DB pass : ")
DB_NAME = input("DB name : ")

def connect_db():
    return mariadb.connect(
        host=DB_HOST,
        user=DB_USER,
        password=DB_PASS,
        database=DB_NAME
    )

def handle_client(conn, addr):
    data = conn.recv(65536).decode().strip()

    conn_db = connect_db()
    cur = conn_db.cursor()

    if data.startswith("ROUTEUR"):
        lines = data.split("\n")
        name = ip = port = pubkey = ""
        reading = False

        for l in lines:
            if l.startswith("ROUTEUR"):
                name = l.split()[1]
            elif l.startswith("IP"):
                ip = l.split()[1]
            elif l.startswith("PORT"):
                port = int(l.split()[1])
            elif l == "PUBKEY":
                reading = True
            elif l == "END":
                break
            elif reading:
                pubkey += l

        cur.execute(
            "INSERT INTO routeurs (router_name, ip, port, public_key) "
            "VALUES (?, ?, ?, ?) "
            "ON DUPLICATE KEY UPDATE ip=?, port=?, public_key=?",
            (name, ip, port, pubkey, ip, port, pubkey)
        )

        conn_db.commit()
        conn.sendall(b"OK")

    elif data.startswith("CLIENT ") and not data.startswith("CLIENT GET"):
        parts = data.split(" ", 3)

        name = parts[1]
        port = int(parts[2])
        pubkey = parts[3]
        ip = addr[0]

        cur.execute(
            "INSERT INTO clients (client_name, ip, port, public_key) "
            "VALUES (?, ?, ?, ?) "
            "ON DUPLICATE KEY UPDATE ip=?, port=?, public_key=?",
            (name, ip, port, pubkey, ip, port, pubkey)
        )

        conn_db.commit()
        conn.sendall(b"OK")

    elif data == "CLIENT GET_CLIENTS":
        cur.execute("SELECT client_name, ip, port FROM clients")
        rows = cur.fetchall()
        out = [f"CLIENT {r[0]} {r[1]} {r[2]}" for r in rows]
        out.append("END")
        conn.sendall("\n".join(out).encode())

    elif data == "CLIENT GET_ROUTEURS":
        cur.execute("SELECT router_name, ip, port, public_key FROM routeurs")
        rows = cur.fetchall()
        out = [f"ROUTEUR {r[0]} {r[1]} {r[2]} {r[3]}" for r in rows]
        out.append("END")
        conn.sendall("\n".join(out).encode())

    conn_db.close()
    conn.close()

s = socket.socket()
s.bind(("0.0.0.0", LISTEN_PORT))
s.listen(5)
print("[MASTER] OK")

while True:
    c, a = s.accept()
    threading.Thread(target=handle_client, args=(c,a), daemon=True).start()
