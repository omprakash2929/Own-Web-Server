import socket
import threading

SERVER_HOST = "0.0.0.0"
SERVER_PORT = 2300

def handle_home():
    with open('webpages/index.html', "rb") as f:
        return f.read(), "text/html"
    
def handle_about():
    with open('about.html', "rb") as f:
        return f.read(), "text/html"

def handle_contact():
    with open("contact.html","rb") as f:
        return f.read(), "text/html"

ROUTES = {
    "/": handle_home,
    "/about": handle_about,
    "/contact": handle_contact
}

def handle_client(client_socket, client_address):
    try:
        req = client_socket.recv(4096).decode(errors="ignore")
        if not  req:
            return
        request_line = req.split('\r\n')[0]
        method,path, _ = request_line.split()
        
        if method == "GET":
            handler = ROUTES.get(path)
            if handler:
                content, content_type = handler()
                response = (
                    b"HTTP/1.1 200 ok\r\n"
                    b"Content-Type: text/html; charset=utf-8\r\n"
                    + f"Content-Lenght: {len(content)}\r\n".encode()
                    + b"Connection: close\r\n\r\n"
                    + content
                )
        else:
            body = b"404 Not Found"
            response = (
                b"HTTP/1.1 404 Not Found\r\n"
                b"Content-Type: text/plain\r\n"
                + f"Content-Length: {len(body)}\r\n".encode()
                + b"\r\n" + body
            )
            
        client_socket.sendall(response)
    except Exception as e:
        print("Error:",e)
    finally:
        client_socket.close()
        
def main():
    server_socket = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
    server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR,1)
    server_socket.bind((SERVER_HOST,SERVER_PORT))
    server_socket.listen(5)
    print(f"listing on port {SERVER_PORT}...")

    try:
        while True:
            client_socket, client_address = server_socket.accept()
            threading.Thread(target=handle_client, args=(client_socket, client_address)).start()
    except KeyboardInterrupt:
        print("Server stopped.")
    finally:
        server_socket.close()


if __name__ == "__main__":
    main()
    