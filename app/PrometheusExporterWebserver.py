from BaseHTTPServer import BaseHTTPRequestHandler, HTTPServer
import OmnikExport

hostName = "0.0.0.0"
serverPort = 8080


class MyServer(BaseHTTPRequestHandler):
    omnik_exporter = OmnikExport.OmnikExport('config.cfg')

    def do_GET(self):
        data = self.omnik_exporter.run()

        self.send_response(200)
        self.send_header("Content-type", "text/html")
        self.end_headers()
        self.wfile.write(data)


if __name__ == "__main__":
    webServer = HTTPServer((hostName, serverPort), MyServer)
    print("Server started http://%s:%s" %
          (hostName, serverPort))  # Server starts
    webServer.serve_forever()
