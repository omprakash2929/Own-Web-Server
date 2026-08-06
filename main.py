import socket
import threading

SERVER_HOST = "0.0.0.0"
SERVER_PORT = 2300

def handle_client(client_socket, client_address):
    ...

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
    