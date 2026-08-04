import socket
import  time
SERVER_HOST = "0.0.0.0"
SERVER_PORT = 8080

server_socket = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR,1)

server_socket.bind((SERVER_HOST,SERVER_PORT))

server_socket.listen(5)

print(f"Listening on port:{SERVER_PORT}...")
try:
    while True:
            client_socket, client_address = server_socket.accept()
            req = client_socket.recv(1500).decode()
            print(req)
            headers = req.split('\n')
            
            first_header_components = headers[0].split()
            http_method = first_header_components[0]
            path = first_header_components[1]
            
except KeyboardInterrupt:
    print("\nServer stopped.")

finally:
    server_socket.close()     