import os
import threading
from http.server import HTTPServer, BaseHTTPRequestHandler

class SimpleHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.send_header("Content-Type", "text/plain; charset=utf-8")
        self.end_headers()
        self.wfile.write(b"Bot is alive!")

    def do_HEAD(self):
        # بعض خدمات المراقبة (مثل UptimeRobot) بتستخدم HEAD
        self.send_response(200)
        self.end_headers()

    def log_message(self, format, *args):
        pass  # يخفي سجلات كل طلب حتى ما تزحم اللوغ

def run_server():
    port = int(os.environ.get("PORT", 10000))
    server = HTTPServer(("0.0.0.0", port), SimpleHandler)
    server.serve_forever()

if __name__ == "__main__":
    run_server()
