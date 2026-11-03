import http.server
import socketserver
import urllib.parse
import gutenberg

PORT = 8000

class LocalProxyHandler(http.server.SimpleHTTPRequestHandler):
    def do_GET(self):
        parsed = urllib.parse.urlparse(self.path)
        if parsed.path == "/api/download":
            qs = urllib.parse.parse_qs(parsed.query)
            target_url = qs.get("url", [None])[0]
            if not target_url:
                self.send_error(400, "Falta el parámetro url")
                return
            try:
                raw = gutenberg.download(target_url)
                self.send_response(200)
                self.send_header("Content-Type", "application/octet-stream")
                self.send_header("Access-Control-Allow-Origin", "*")
                self.send_header("Content-Length", str(len(raw)))
                self.end_headers()
                self.wfile.write(raw)
            except Exception as e:
                self.send_error(500, str(e))
        else:
            super().do_GET()

if __name__ == "__main__":
    socketserver.TCPServer.allow_reuse_address = True
    with socketserver.TCPServer(("", PORT), LocalProxyHandler) as httpd:
        print(f"Servidor Huffman iniciado en http://localhost:{PORT}")
        httpd.serve_forever()
