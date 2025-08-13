def send_move(sock, move):
    sock.sendall(move.encode())

def receive_move(sock):
    data = sock.recv(1024)
    return data.decode() if data else None


