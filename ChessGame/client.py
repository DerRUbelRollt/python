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
            # Spielerzug eingeben
            move = input("Dein Zug (z. B. e2e4, 'exit' zum Beenden): ")
            if move.lower() == "exit":
                print("[CLIENT] Verbindung beendet.")
                break

            send_move(conn, move)

            # Antwort vom Server empfangen
            response = receive_move(conn)
            print(f"[CLIENT] Server sagt: {response}")

    except KeyboardInterrupt:
        print("\n[CLIENT] Beendet durch Benutzer.")
    finally:
        conn.close()
