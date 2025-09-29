import socket
import pickle

def start_server(host="0.0.0.0", port=5005):
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.bind((host, port))
    server_socket.listen()
    print(f"[SERVER] Warte auf Verbindung auf {host}:{port} ...")

    conn, addr = server_socket.accept()
    print(f"[SERVER] Verbunden mit {addr}")


    # Schleife für Nachrichten
    try:
        while True:
            data = conn.recv(1024)
            if not data:
                break
            move = pickle.loads(data)
            print(f"[SERVER] Empfangen: {move}")

            # Optional: Bestätigung zurücksenden
            conn.send(pickle.dumps(f"Server hat {move} empfangen"))
    except KeyboardInterrupt:
        print("[SERVER] Beende Server...")
    finally:
        conn.close()
        server_socket.close()

if __name__ == "__main__":
    start_server()
