import socket
import pickle
import queue

# Gemeinsame Queue für eingehende Moves
incoming_moves = queue.Queue()

def start_server(host="0.0.0.0", port=5005):
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.bind((host, port))
    server_socket.listen()
    print(f"[SERVER] Warte auf Verbindung auf {host}:{port} ...")
    conn, addr = server_socket.accept()
    print(f"[SERVER] Verbunden mit {addr}")
    return conn

def connect_to_server(server_ip, port=5005):
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.connect((server_ip, port))
    print(f"[CLIENT] Verbunden mit {server_ip}:{port}")
    return s

def send_move(sock, move):
    try:
        sock.send(pickle.dumps(move))
        return True
    except Exception as e:
        print(f"[NETZWERK] Fehler beim Senden: {e}")
        return False

def is_connection_alive(sock):
    """Testet ob die Verbindung noch aktiv ist"""
    try:
        # Setze Socket auf non-blocking für den Test
        sock.setblocking(False)
        # Versuche ein kleines Test-Byte zu senden
        sock.send(b'\x00')
        return True
    except:
        return False
    finally:
        # Setze Socket zurück auf blocking
        try:
            sock.setblocking(True)
        except:
            pass

def listen_for_moves(sock):
    """ Läuft in eigenem Thread, speichert Moves in Queue """
    while True:
        try:
            data = sock.recv(1024)
            if not data:
                print("[NETZWERK] Verbindung getrennt.")
                break
            move = pickle.loads(data)
            incoming_moves.put(move)  # move in Queue speichern
        except Exception as e:
            print(f"[NETZWERK] Fehler: {e}")
            break
