import socket
import threading
import time

try:
    import mariadb
except:
    print("[MASTER] Erreur : module mariadb non installé")
    exit(1)

LISTEN_PORT = int(input("Port d'écoute du Master : "))
DB_HOST = input("DB host (ex: localhost) : ")
DB_USER = input("DB user : ")
DB_PASS = input("DB password : ")
DB_NAME = input("DB name : ")

LOG_FILE = "../logs/master.log"

def log(msg):
    ts = time.strftime("%Y-%m-%d %H:%M:%S")
    with open(LOG_FILE, "a") as f:
        f.write(f"[{ts}] {msg}\n")

def connect_db():
    return mariadb.connect(
        host=DB_HOST,
        user=DB_USER,
        password=DB_PASS,
        database=DB_NAME
    )

def save_router(name, ip, port, pubkey):
    conn = connect_db()
    cur = conn.cursor()

    cur.execute(
        "INSERT INTO routeurs (router_name, ip, port, public_key) "
        "VALUES (?, ?, ?, ?) "
        "ON DUPLICATE KEY UPDATE ip=?, port=?, public_key=?",
        (name, ip, port, pubkey, ip, port, pubkey)
    )

    conn.commit()
    conn.close()

    print(f"[MASTER] Routeur enregistré : {name} {ip}:{port}")
    log(f"Routeur enregistré : {name} {ip}:{port}")

def list_routeurs():
    conn = connect_db()
    cur = conn.cursor()
    cur.execute("SELECT router_name, ip, port, public_key FROM routeurs")
    rows = cur.fetchall()
    conn.close()

    out = []
    for r in rows:
        out.append(f"ROUTEUR {r[0]} {r[1]} {r[2]} {r[3]}")
    out.append("END")
    return "\n".join(out)

def save_client(name, ip, port, pubkey):
    conn = connect_db()
    cur = conn.cursor()

    cur.execute(
        "INSERT INTO clients (client_name, ip, port, public_key) "
        "VALUES (?, ?, ?, ?) "
        "ON DUPLICATE KEY UPDATE ip=?, port=?, public_key=?",
        (name, ip, port, pubkey, ip, port, pubkey)
    )

    conn.commit()
    conn.close()

    print(f"[MASTER] Client enregistré : {name} {ip}:{port}")
    log(f"Client enregistré : {name} {ip}:{port}")

def list_clients():
    conn = connect_db()
    cur = conn.cursor()
    cur.execute("SELECT client_name, ip, port, public_key FROM clients")
    rows = cur.fetchall()
    conn.close()

    out = []
    for c in rows:
        out.append(f"CLIENT {c[0]} {c[1]} {c[2]} {c[3]}")
    out.append("END")
    return "\n".join(out)

def handle_client(conn, addr):
    try:
        data = conn.recv(65536).decode(errors="ignore").strip()
        log(f"Reçu de {addr} : {data}")

        if data.startswith("ROUTEUR"):
            lines = data.split("\n")
            name = ip = port = pubkey = ""
            reading = False

            for l in lines:
                if l.startswith("ROUTEUR "):
                    name = l.split(" ")[1]
                elif l.startswith("IP "):
                    ip = l.split(" ")[1]
                elif l.startswith("PORT "):
                    port = l.split(" ")[1]
                elif l == "PUBKEY":
                    reading = True
                elif l == "END":
                    break
                elif reading:
                    pubkey += l

            save_router(name, ip, int(port), pubkey)
            conn.sendall(b"OK")

        elif data.startswith("CLIENT ") and not data.startswith("CLIENT GET"):
            parts = data.split(" ", 3)
            name = parts[1]
            port = int(parts[2])
            pubkey = parts[3]
            ip = addr[0]

            save_client(name, ip, port, pubkey)
            conn.sendall(b"OK")

        elif data == "CLIENT GET_CLIENTS":
            conn.sendall(list_clients().encode())

        elif data == "CLIENT GET_ROUTEURS":
            conn.sendall(list_routeurs().encode())

        else:
            conn.sendall(b"UNKNOWN")

    except Exception as e:
        print("[MASTER] Erreur :", e)
        log(f"Erreur : {e}")

    finally:
        conn.close()

def start_master():
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.bind(("0.0.0.0", LISTEN_PORT))
    s.listen(5)

    print(f"[MASTER] En écoute sur le port {LISTEN_PORT}")
    log("Master démarré")

    while True:
        conn, addr = s.accept()
        threading.Thread(
            target=handle_client,
            args=(conn, addr),
            daemon=True
        ).start()

start_master()

