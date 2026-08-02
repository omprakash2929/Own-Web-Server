import socket

server_socket = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR,1)

server_socket.bind(("0.0.0.0",8080))

print("Server are initialization")