import socket
import threading
import time


try:
    import mariadb
except:
    mariadb = None



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
    if mariadb is None:
        return None
    try:
        return mariadb.connect(
            host=DB_HOST,
            user=DB_USER,
            password=DB_PASS,
            database=DB_NAME
        )
    except:
        return None



def save_router(name, ip, port, pubkey):
    conn = connect_db()
    if conn is None:
        print(f"[MASTER] (DEV MODE) Routeur reçu : {name} {ip}:{port}")
        return

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
    log(f"Routeur enregistré : {name} ({ip}:{port})")



def list_routeurs():
    conn = connect_db()
    if conn is None:
        return "END"

    cur = conn.cursor()
    cur.execute("SELECT router_name, ip, port, public_key FROM routeurs")
    rows = cur.fetchall()
    conn.close()

    out = []
    for r in rows:
        out.append(
            "ROUTEUR " + str(r[0]) + " " +
            str(r[1]) + " " +
            str(r[2]) + " " +
            str(r[3])
        )
    out.append("END")
    return "\n".join(out)


def handle_client(conn, addr):
    try:
        data = conn.recv(65536).decode(errors="ignore").strip()
        print(f"[MASTER] Message reçu de {addr}")
        log("Reçu de " + str(addr) + " : " + data)

        # -------------------------
        # ROUTER REGISTRATION
        # -------------------------
        if data.startswith("ROUTEUR"):
            lines = data.split("\n")
            name = ip = port = pubkey = ""
            reading_key = False

            for l in lines:
                if l.startswith("ROUTEUR "):
                    name = l.split(" ")[1]
                elif l.startswith("IP "):
                    ip = l.split(" ")[1]
                elif l.startswith("PORT "):
                    port = l.split(" ")[1]
                elif l == "PUBKEY":
                    reading_key = True
                elif l == "END":
                    break
                elif reading_key:
                    pubkey += l

            if name and ip and port and pubkey:
                save_router(name, ip, int(port), pubkey)
                conn.sendall(b"OK")
            else:
                print("[MASTER] Routeur incomplet")
                conn.sendall(b"ERROR")


        elif data == "CLIENT GET_ROUTEURS":
            routes = list_routeurs()
            conn.sendall(routes.encode())

        else:
            conn.sendall(b"UNKNOWN")

    except Exception as e:
        print("[MASTER] Erreur :", e)
        log("Erreur : " + str(e))

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

if __name__ == "__main__":
    start_master()



