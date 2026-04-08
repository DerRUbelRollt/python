# lan_discovery.py
import socket
import threading
import time

BROADCAST_PORT = 50000
DISCOVERY_MESSAGE = "CHESS_HOST"

def broadcast_host(server_port):
    """
    Host sendet seine Existenz ins LAN.
    """
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP)
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
    sock.settimeout(0.2)

    message = f"{DISCOVERY_MESSAGE}:{server_port}".encode("utf-8")

    while True:
        # Sendet an alle im LAN
        sock.sendto(message, ("255.255.255.255", BROADCAST_PORT))
        time.sleep(2)  # alle 2 Sekunden erneut senden


def listen_for_hosts(found_hosts):
    """
    Client hört auf Broadcasts und speichert IPs.
    """
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP)
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    sock.bind(("", BROADCAST_PORT))

    while True:
        data, addr = sock.recvfrom(1024)
        message = data.decode("utf-8")
        if message.startswith(DISCOVERY_MESSAGE):
            _, port = message.split(":")
            host_ip = addr[0]
            if (host_ip, port) not in found_hosts:
                found_hosts.append((host_ip, port))
                print(f"Gefunden: {host_ip}:{port}")


if __name__ == "__main__":
    # Beispiel-Testlauf:
    mode = input("Host (h) oder Client (c)? ")

    if mode == "h":
        threading.Thread(target=broadcast_host, args=(5555,), daemon=True).start()
        print("Host sendet LAN-Broadcasts...")
        while True:
            time.sleep(1)

    else:
        found = []
        threading.Thread(target=listen_for_hosts, args=(found,), daemon=True).start()
        print("Suche nach Spielen im LAN...")
        while True:
            time.sleep(5)
            print("Gefundene Hosts:", found)
