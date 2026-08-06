# Mini Web Server (Python `socket` module)

A small HTTP server built from scratch using Python's built-in `socket` module. no framework like Flask/FastAPI so that HTTP protocol and networking basics can be understood deeply.

---

## 🛠️ Tools & Technologies Used

| Tool / Module | Purpose |
|---|---|
| **Python 3** | Core language |
| `socket` | To create TCP connections, listen for clients, and send/receive data |
| `threading` | To handle multiple clients in parallel (concurrently) |
| `pytest` (planned) | For writing automated test cases |
| `http.client` (planned) | To send HTTP requests to the server in tests |
| `mimetypes` (planned) | To decide the correct `Content-Type` for static files (CSS/JS/images) |
| `urllib.parse` (planned) | To parse URL query parameters |
| `argparse` (planned) | To configure host/port from the command line |

---

## 🏗️ Architecture Diagram

```
                          ┌─────────────────────┐
                          │   Client (Browser)   │
                          └──────────┬───────────┘
                                     │ TCP Connection
                                     ▼
                     ┌───────────────────────────────┐
                     │        server_socket           │
                     │  (bind + listen on port 2300)  │
                     └──────────────┬──────────────────┘
                                     │ accept()
                                     ▼
                     ┌───────────────────────────────┐
                     │   New client connects           │
                     │  (client_socket, client_address) │
                     └──────────────┬──────────────────┘
                                     │
                                     ▼
                     ┌───────────────────────────────┐
                     │   threading.Thread() spawned    │
                     │   → handle_client() runs in the  │
                     │     background                    │
                     └──────────────┬──────────────────┘
                                     │
                    ┌────────────────┼────────────────┐
                    ▼                                  ▼
        ┌────────────────────┐            ┌────────────────────┐
        │ Parse the request    │            │ main() goes back to  │
        │ (method + path)      │            │ the loop to accept    │
        └──────────┬──────────┘            │ the next client         │
                    ▼                       └────────────────────┘
        ┌────────────────────┐
        │  Route match?        │
        │  GET "/" → index.html│
        │  else → 404           │
        └──────────┬──────────┘
                    ▼
        ┌────────────────────┐
        │ Build the response    │
        │ (status + headers +   │
        │  body) as bytes        │
        └──────────┬──────────┘
                    ▼
        ┌────────────────────┐
        │ client_socket.sendall │
        │ → Client receives the  │
        │   response               │
        └──────────┬──────────┘
                    ▼
        ┌────────────────────┐
        │ client_socket.close() │
        └────────────────────┘
```

### Request Lifecycle (step by step)

1. Server becomes ready with `bind()` + `listen()`.
2. `accept()` blocks until a client connects.
3. A new **thread** is spawned for each client → the server immediately becomes free to accept the next client.
4. Inside the thread: the request is read via `recv()`, decoded, and the first line is split into `method` + `path`.
5. Based on the route, a response is built (either the HTML file or a 404).
6. The response is sent to the client via `sendall()`.
7. The connection is closed with `client_socket.close()`.

---

## ✅ Current Features (Implemented)

- [x] Built an HTTP server using raw TCP sockets
- [x] Serves `index.html` for a `GET /` request
- [x] Returns `404 Not Found` for unknown paths
- [x] Handles multiple clients in parallel using `threading`
- [x] Basic error handling (`try/except/finally`)
- [x] `SO_REUSEADDR` to avoid port conflicts on restart

---

## 🚀 Planned Features (Roadmap — to be implemented step by step)

### Level 1 — Foundation fixes
- [ ] Handle malformed/empty requests without crashing (extra validation)
- [ ] Proper `405 Method Not Allowed` for non-GET methods (POST, PUT, DELETE)

### Level 2 — Making it feel like a real HTTP server
- [ ] **Routing system** — dictionary-based routes (`/`, `/about`, `/contact`)
- [ ] **Serve multiple static files** (CSS, JS, images) with the correct MIME type
- [ ] **Parse query parameters** (`/search?name=ali`)

### Level 3 — HTTP protocol deep dive
- [ ] **POST method support** (reading form data / JSON body via `Content-Length`)
- [ ] Proper header parsing → convert into a dictionary (`Host`, `User-Agent`, etc.)
- [ ] Extra response headers (`Date`, `Server`, `Cache-Control`)

### Level 4 — Production-level
- [ ] **Keep-Alive connections** (multiple requests on the same socket)
- [ ] Proper error codes: `400 Bad Request`, `500 Internal Server Error`
- [ ] **Logging** - method, path, status code, timestamp (Apache/Nginx style)
- [ ] **Command-line config** - set host/port via `argparse`

### Level 5 — Advanced / Bonus
- [ ] Simple cookie/session handling
- [ ] Basic templating engine (replacing placeholders like `{{name}}`)
- [ ] Rate limiting (blocking too many requests from one IP)
- [ ] HTTPS support (wrapping the socket with the `ssl` module)

### Testing
- [ ] `pytest`-based test suite
- [ ] Run the server in a background thread/subprocess and test it with `http.client`
- [ ] Test cases: 200 OK, 404 Not Found, 405 Method Not Allowed, POST body handling

---

## ▶️ How to Run

```bash
python3 server.py
```

Open in browser:
```
http://localhost:2300/
```

---

## 📂 Project Structure (Suggested, as you keep adding features)

```
mini-web-server/
├── server.py          # Main server code
├── index.html         # Home page
├── static/             # CSS, JS, images (planned)
├── routes.py           # Route handlers (planned)
├── tests/
│   └── test_server.py  # pytest test cases (planned)
└── README.md
```