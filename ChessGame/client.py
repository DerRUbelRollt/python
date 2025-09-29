import socket
import pickle

def connect_to_server(server_ip, port=5005):
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.connect((server_ip, port))
    print(f"[CLIENT] Verbunden mit {server_ip}:{port}")
    return s

def send_move(sock, move):
    sock.send(pickle.dumps(move))

def receive_move(sock):
    data = sock.recv(1024)
    return pickle.loads(data)

if __name__ == "__main__":
    ip = input("IP-Adresse des Servers: ")  # z.B. 127.0.0.1
    conn = connect_to_server(ip)

    try:
        while True:
            msg = input("Nachricht an Server senden: ")
            send_move(conn, msg)

            # Antwort vom Server empfangen
            reply = receive_move(conn)
            print(f"[CLIENT] Antwort vom Server: {reply}")
    except KeyboardInterrupt:
        print("[CLIENT] Verbindung beendet.")
    finally:
        conn.close()
