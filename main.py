import socket
import  time
SERVER_HOST = "0.0.0.0"
SERVER_PORT = 2300

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
            if http_method == 'GET':
                if path == "/":
                    try:
                        with open("index.html", "r", encoding="utf-8") as fin:
                            content = fin.read()

                        response = (
                            "HTTP/1.1 200 OK\r\n"
                            "Content-Type: text/html; charset=utf-8\r\n"
                            f"Content-Length: {len(content.encode('utf-8'))}\r\n"
                            "Connection: close\r\n"
                            "\r\n"
                            + content
                        )

                        client_socket.sendall(response.encode("utf-8"))

                    except FileNotFoundError:
                        client_socket.sendall(
                            b"HTTP/1.1 404 Not Found\r\n"
                            b"Content-Type: text/plain\r\n\r\n"
                            b"404 Not Found"
                        )

                    finally:
                        client_socket.close()
            else:
                response = 'HTTP/1.1 405 Method Not Allowed\n\nAllow: GET' 
                client_socket.sendall(response.encode("utf-8"))
                client_socket.close()
            
except KeyboardInterrupt:
    print("\nServer stopped.")

finally:
    server_socket.close()     