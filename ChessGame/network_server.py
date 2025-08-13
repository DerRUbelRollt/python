import socket
import threading
import time

BROADCAST_PORT = 5001
TCP_PORT = 5000
BROADCAST_MSG = b"SCHACH_GAME"

def broadcast_presence():
    udp_sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP)
    udp_sock.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
    while True:
        udp_sock.sendto(BROADCAST_MSG, ('<broadcast>', BROADCAST_PORT))
        time.sleep(1)

def tcp_server():
    tcp_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    tcp_sock.bind(('', TCP_PORT))
    tcp_sock.listen(1)
    print(f"[SERVER] Warte auf Verbindung auf Port {TCP_PORT}...")

    conn, addr = tcp_sock.accept()
    print(f"[SERVER] Verbunden mit {addr}")
    conn.sendall(b"Willkommen im Schachspiel!")
    conn.close()

if __name__ == "__main__":
    threading.Thread(target=broadcast_presence, daemon=True).start()
    tcp_server()
