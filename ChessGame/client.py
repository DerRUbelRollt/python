import socket

def connect_to_server(server_ip):
    port = 5000
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.connect((server_ip, port))
    print(f"[CLIENT] Verbunden mit {server_ip}:{port}")
    return s
