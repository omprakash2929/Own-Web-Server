import socket
import threading
import mimetypes
import os
from urllib.parse import urlparse, parse_qs,unquote


SERVER_HOST = "0.0.0.0"
SERVER_PORT = 2300


def handle_home():
    with open("webpages/index.html", "rb") as f:
        return f.read(), "text/html"


def handle_about():
    with open("webpages/about.html", "rb") as f:
        return f.read(), "text/html"


def handle_contact():
    with open("webpages/contact.html", "rb") as f:
        return f.read(), "text/html"


def handle_search(query_params):
    name = query_params.get("name", ["Guest"])[0]
    body = f"<html><body><h1>Search results for: {name}</h1></body></html>".encode()
    return body, "text/html"


# ? Routes path
ROUTES = {
    "/": handle_home,
    "/about": handle_about,
    "/contact": handle_contact,
    "/search": handle_search,
}

ROUTES_NEEDING_QUERY = {"/search"}


def parse_headers_and_body(req):
    if "\r\n\r\n" in req:
        head, body = req.split("\r\n\r\n", 1)
    else:
        head, body = req, ""
    lines = head.split("\r\n")
    request_line = lines[0]

    headers = {}
    for line in lines[1:]:
        if ":" in line:
            key, value = line.split(":", 1)
            headers[key.strip()] = value.strip()

    return request_line, headers, body


def read_full_body(client_socket, initial_body, content_length):
    body_bytes = initial_body.encode()
    while len(body_bytes) < content_length:
        chunk = client_socket.recv(4096)
        if not chunk:
            break
        body_bytes += chunk
    return body_bytes.decode(errors="ignore")


def parse_headers(req):
    lines = req.split("\r\n")
    request_line = lines[0]

    headers = {}
    i = 1
    while i < len(lines) and lines[i] != "":
        line = lines[i]
        if ":" in line:
            key, value = line.split(":", 1)
            headers[key.strip()] = value.strip()
        i += 1
    return request_line, headers


def parse_request_path(full_path):
    parsed = urlparse(full_path)
    clean_path = unquote(parsed.path).strip()   
    query_params = parse_qs(parsed.query)
    return clean_path, query_params


# ? Static File serve Funcation


def serve_static(path):
    file_path = path.replace("/static/", "webpages/static/", 1)

    if not os.path.exists(file_path):
        return None, None
    content_type, _ = mimetypes.guess_type(file_path)
    if content_type is None:
        content_type = "application/octet-stream"

    with open(file_path, "rb") as f:
        content = f.read()

    return content, content_type


def handle_submit(body, headers):
    from urllib.parse import parse_qs

    data = parse_qs(body)
    name = data.get("name", ["Unknown"])[0]
    message = data.get("message", [""])[0] 

    response_html = (
        f"<html><body><h1>Thanks {name}!</h1><p>Message: {message}</p></body></html>"
    )
    return response_html.encode(), "text/html"


#! Handle Funcation
def handle_client(client_socket, client_address):
    try:
        req = client_socket.recv(4096).decode(errors="ignore")
        if not req:
            return

        request_line, headers, body = parse_headers_and_body(req)
        method, full_path, _ = request_line.split()
        path, query_params = parse_request_path(full_path)
        print(f"DEBUG -> Method: '{method}', Path: '{path}'")
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

        elif method == "POST":
            if path == "/submit":
                content_length = int(headers.get("Content-Length", 0))
                full_body = read_full_body(client_socket, body, content_length)
                content, content_type = handle_submit(full_body, headers)
            else:
                status_line = b"HTTP/1.1 404 Not Found\r\n"
                content, content_type = b"404 Not Found", "text/plain"

        else:
            status_line = b"HTTP/1.1 405 Method Not Allowed\r\n"
            content = b"405 Method Not Allowed"
            content_type = "text/plain"

        # ---------- Response building ----------
        response = (
            status_line
            + f"Content-Type: {content_type}; charset=utf-8\r\n".encode()
            + f"Content-Length: {len(content)}\r\n".encode()
            + b"Connection: close\r\n\r\n"
            + content
        )
        client_socket.sendall(response)   

    except Exception as e:
        print("Error:", e)
    finally:
        client_socket.close()

# * Main Socket Funcation


def main():
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    server_socket.bind((SERVER_HOST, SERVER_PORT))
    server_socket.listen(5)
    print(f"listing on port {SERVER_PORT}...")

    try:
        while True:
            client_socket, client_address = server_socket.accept()
            threading.Thread(
                target=handle_client, args=(client_socket, client_address)
            ).start()
    except KeyboardInterrupt:
        print("Server stopped.")
    finally:
        server_socket.close()


if __name__ == "__main__":
    main()
