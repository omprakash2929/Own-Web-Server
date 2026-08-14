import socket
import threading
import mimetypes
import os
from urllib.parse import urlparse, parse_qs

SERVER_HOST = "0.0.0.0"
SERVER_PORT = 2300


def handle_home():
    with open('webpages/index.html', "rb") as f:
        return f.read(), "text/html"
    
def handle_about():
    with open('webpages/about.html', "rb") as f:
        return f.read(), "text/html"

def handle_contact():
    with open("webpages/contact.html","rb") as f:
        return f.read(), "text/html"
    
def handle_search(query_params):
    name = query_params.get("name", ["Guest"])[0]
    body = f"<html><body><h1>Search results for: {name}</h1></body></html>".encode()
    return body, "text/html"

#? Routes path
ROUTES = {
    "/": handle_home,
    "/about": handle_about,
    "/contact": handle_contact,
    "/search": handle_search,
}

ROUTES_NEEDING_QUERY = {"/search"}


def parse_headers(req):
    lines = req.split('\r\n')
    request_line = lines[0]

    headers = {}
    i =1 
    while i < len(lines) and lines[i] != '':
        line = lines[i]
        if ':' in line:
            key, value = line.split(':',1)
            headers[key.strip()] = value.strip()
        i += 1
    return request_line, headers


def parse_request_path(full_path):
    parsed = urlparse(full_path)
    clean_path = parsed.path
    query_params = parse_qs(parsed.query)
    return clean_path, query_params

#? Static File serve Funcation 

def serve_static(path):
    file_path = path.replace("/static/", "webpages/static/", 1)

    if not os.path.exists(file_path):
        return None,None
    content_type, _ = mimetypes.guess_type(file_path)
    if content_type is None:
        content_type = "application/octet-stream"  
    
    with open(file_path, "rb") as f:
        content = f.read()
    
    return content, content_type

#! Handle Funcation 
def handle_client(client_socket, client_address):
    try:
        req = client_socket.recv(4096).decode(errors="ignore")
        if not req:
            return

        request_line, headers = parse_headers(req)
        method, full_path, _ = request_line.split()
        path, query_params = parse_request_path(full_path) 
        #print(f"Method: {method}, Path: {path}")
        #print(f"Headers: {headers}")
        
        status_line = b"HTTP/1.1 200 OK\r\n" 

        if method == "GET":
            handler = ROUTES.get(path)
            if handler:
                if path in ROUTES_NEEDING_QUERY:
                    content, content_type = handler(query_params)  
                else:
                    content, content_type = handler()
            elif path.startswith("/static/"):
                content, content_type = serve_static(path)
                if content is None:
                    status_line = b"HTTP/1.1 404 Not Found\r\n"
                    content, content_type = b"404 Not Found", "text/plain"
            else:
                status_line = b"HTTP/1.1 404 Not Found\r\n"
                content, content_type = b"404 Not Found", "text/plain"

            # ---------- Response building (same for all cases) ----------
            response = (
                status_line
                + f"Content-Type: {content_type}; charset=utf-8\r\n".encode()
                + f"Content-Length: {len(content)}\r\n".encode()
                + b"Connection: close\r\n\r\n"
                + content
            )

        else:
            body = b"405 Method Not Allowed"
            response = (
                b"HTTP/1.1 405 Method Not Allowed\r\n"
                b"Content-Type: text/plain\r\n"
                b"Allow: GET\r\n"
                + f"Content-Length: {len(body)}\r\n".encode()
                + b"\r\n" + body
            )

        client_socket.sendall(response)

    except Exception as e:
        print("Error:", e)
    finally:
        client_socket.close()

#* Main Socket Funcation
    
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
    