# server.py
import socket
import pickle

def start_server(host="0.0.0.0", port=5000):
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.bind((host, port))
    server_socket.listen()
    print(f"[SERVER] Warte auf Verbindung auf {host}:{port} ...")
    conn, addr = server_socket.accept()
    print(f"[SERVER] Verbunden mit {addr}")
    return conn

def send_move(conn, move):
    conn.send(pickle.dumps(move))

def receive_move(conn):
    data = conn.recv(1024)
    return pickle.loads(data)

if __name__ == "__main__":
    # Teststart
    conn = start_server()
    print("Server gestartet und verbunden!")
