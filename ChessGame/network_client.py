import socket
import threading

BROADCAST_PORT = 5001
TCP_PORT = 5000
BROADCAST_MSG = b"SCHACH_GAME"

found_hosts = []

def listen_for_hosts():
    udp_sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    udp_sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    udp_sock.bind(('', BROADCAST_PORT))
    print("[CLIENT] Suche nach Hosts im Netzwerk...")

    while True:
        data, addr = udp_sock.recvfrom(1024)
        if data == BROADCAST_MSG:
            if addr[0] not in found_hosts:
                found_hosts.append(addr[0])
                print(f"[CLIENT] Host gefunden: {addr[0]}")

def connect_to_host(ip):
    tcp_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    tcp_sock.connect((ip, TCP_PORT))
    print("[CLIENT] Verbunden mit", ip)
    msg = tcp_sock.recv(1024).decode()
    print("[CLIENT] Nachricht vom Server:", msg)
    tcp_sock.close()

if __name__ == "__main__":
    threading.Thread(target=listen_for_hosts, daemon=True).start()
    while True:
        cmd = input("IP eingeben um zu verbinden (oder 'list' für Hosts): ")
        if cmd == "list":
            print("Gefundene Hosts:", found_hosts)
        elif cmd in found_hosts:
            connect_to_host(cmd)
        else:
            print("Ungültige Eingabe")
