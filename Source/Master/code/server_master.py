import socket, threading, mariadb

PORT=int(input("Port master: "))

def db():
    return mariadb.connect(user="maelea",password="sae302",database="sae302")

def handle(c,a):
    data=c.recv(65536).decode().strip()
    conn=db(); cur=conn.cursor()

    if data.startswith("ROUTEUR"):
        l=data.split("\n")
        name=l[0].split()[1]
        ip=l[1].split()[1]
        port=int(l[2].split()[1])
        pub=l[4]
        cur.execute(
            "REPLACE INTO routeurs VALUES (?,?,?,?)",
            (name,ip,port,pub)
        )
        conn.commit()

    elif data=="CLIENT GET_ROUTEURS":
        cur.execute("SELECT * FROM routeurs")
        for r in cur:
            c.sendall(f"ROUTEUR {r[0]} {r[1]} {r[2]} {r[3]}\n".encode())
        c.sendall(b"END")

    c.close(); conn.close()

s=socket.socket()
s.bind(("0.0.0.0",PORT))
s.listen(5)
print("[MASTER] OK")

while True:
    c,a=s.accept()
    threading.Thread(target=handle,args=(c,a),daemon=True).start()
