from http.server import BaseHTTPRequestHandler, HTTPServer
from OmnikExport import OmnikExport

hostName = "0.0.0.0"
serverPort = 8080


class PrometheusExporterWebserver(BaseHTTPRequestHandler):
    omnik_exporter = OmnikExport()

    def do_GET(self):
        try:
            data = self.omnik_exporter.run()
            self.send_response(200)
            self.send_header("Content-type", "text/html")
            self.end_headers()
            self.wfile.write(data.encode())
        except RuntimeError as e:
            self.send_response(500)
            self.send_header("Content-type", "text/plain")
            self.end_headers()
            self.wfile.write(f"Error: {e}".encode())


if __name__ == "__main__":
    webServer = HTTPServer((hostName, serverPort), PrometheusExporterWebserver)
    print(f"Server started http://{hostName}:{serverPort}")  # Server starts
    webServer.serve_forever()
