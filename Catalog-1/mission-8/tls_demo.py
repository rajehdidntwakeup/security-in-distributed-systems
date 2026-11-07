"""
Mission 8: TLS into a sample application.

The simplest possible TLS integration: a tiny HTTPS server using only the
Python standard library and the self-signed certificate from Mission 7.

Run from this folder:
    python tls_demo.py
Then open in a browser:
    https://localhost:8443
The browser will warn "not trusted" - that is expected, because the
certificate is self-signed (Issuer = Subject).
"""
import http.server
import ssl
import os
import sys

CERT_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "mission-7")
CERTFILE = os.path.join(CERT_DIR, "selfsigned.crt")
KEYFILE = os.path.join(CERT_DIR, "selfsigned.key")

HOST, PORT = "localhost", 8443

# 1. Build a normal plain HTTP server around a few hard-coded routes
class Handler(http.server.BaseHTTPRequestHandler):
    def do_GET(self):
        if self.path == "/":
            body = ("<h1>HTTPS works!</h1>"
                    "<p>This is the Mission-8, served over TLS 1.3 "
                    "with the self-signed certificate</p>").encode()
        elif self.path == "/health":
            body = b'{"status": "ok", "tls": true}'
        else:
            self.send_error(404)
            return
        self.send_response(200)
        self.send_header("Content-Type", "text/html; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def log_message(self, fmt, *args):
        print("  [%s] %s" % (self.command, self.path))

# 2. Create the SSL context - the single place where TLS is configured
context = ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER)   # server side, latest protocol version
context.load_cert_chain(certfile=CERTFILE, keyfile=KEYFILE)  # Mission-7 certificate
print(f"Using certificate: {CERTFILE}")
print(f"   TLS version min: {context.minimum_version}, "
      f"ciphers: {len(context.get_ciphers())} available")

# 3. Wrap the plain HTTP socket: from here on every byte goes through TLS
server = http.server.HTTPServer((HOST, PORT), Handler)
server.socket = context.wrap_socket(server.socket, server_side=True)

print(f"Serving on https://{HOST}:{PORT}  (Ctrl+C to stop)")
try:
    server.serve_forever()
except KeyboardInterrupt:
    print("\nStopped.")
    sys.exit(0)