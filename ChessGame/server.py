import socket

def start_server():
    host = socket.gethostbyname(socket.gethostname())  # eigene IP
    port = 5000
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.bind((host, port))
    s.listen(1)
    print(f"[SERVER] Warte auf Verbindung auf {host}:{port} ...")
    conn, addr = s.accept()
    print(f"[SERVER] Verbunden mit {addr}")
    return conn
