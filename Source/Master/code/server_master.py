import socket, threading, mariadb

PORT = int(input("Port du master : "))

def db():
    return mariadb.connect(
        user="maelea",
        password="sae302",
        database="sae302"
    )

def handle(conn, addr):
    data = conn.recv(65536).decode().strip()
    dbconn = db()
    cur = dbconn.cursor()

    if data.startswith("ROUTEUR"):
        lines = data.split("\n")
        name = lines[0].split()[1]
        ip = lines[1].split()[1]
        port = int(lines[2].split()[1])
        pubkey = lines[4]

        cur.execute(
            "REPLACE INTO routeurs (router_name, ip, port, public_key) VALUES (?,?,?,?)",
            (name, ip, port, pubkey)
        )
        print(f"[MASTER] Routeur enregistré : {name} {ip}:{port}")

        dbconn.commit()
        conn.sendall(b"OK")

    elif data.startswith("CLIENT ") and not data.startswith("CLIENT GET"):
        parts = data.split(" ", 3)
        cur.execute(
            "REPLACE INTO clients (client_name, ip, port, public_key) VALUES (?,?,?,?)",
            (parts[1], addr[0], int(parts[2]), parts[3])
        )
        dbconn.commit()
        conn.sendall(b"OK")

    elif data == "CLIENT GET_ROUTEURS":
        cur.execute("SELECT router_name, ip, port, public_key FROM routeurs")
        for r in cur:
            conn.sendall(f"ROUTEUR {r[0]} {r[1]} {r[2]} {r[3]}\n".encode())
        conn.sendall(b"END")

    elif data == "CLIENT GET_CLIENTS":
        cur.execute("SELECT client_name, ip, port FROM clients")
        for c in cur:
            conn.sendall(f"CLIENT {c[0]} {c[1]} {c[2]}\n".encode())
        conn.sendall(b"END")

    conn.close()
    dbconn.close()

s = socket.socket()
s.bind(("0.0.0.0", PORT))
s.listen(5)
print("[MASTER] En écoute sur le port {PORT}")

while True:
    c, a = s.accept()
    threading.Thread(target=handle, args=(c, a), daemon=True).start()
