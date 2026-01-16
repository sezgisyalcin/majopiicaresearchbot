import os, threading
from http.server import BaseHTTPRequestHandler, HTTPServer
from core.logging import log

class Handler(BaseHTTPRequestHandler):
    def do_GET(self):
        if self.path in ["/", "/healthz"]:
            self.send_response(200)
            self.send_header("Content-Type", "text/plain; charset=utf-8")
            self.end_headers()
            self.wfile.write(b"ok\n")
        else:
            self.send_response(404)
            self.end_headers()

    def log_message(self, format, *args):
        return

def start_health_server():
    port = int(os.getenv("PORT", "8080"))
    def run():
        try:
            server = HTTPServer(("0.0.0.0", port), Handler)
            log("health_server_started", port=port)
            server.serve_forever()
        except Exception as e:
            log("health_server_error", error=str(e))
    threading.Thread(target=run, daemon=True).start()
