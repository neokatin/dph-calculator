import os
from http.server import ThreadingHTTPServer, SimpleHTTPRequestHandler
import json
from urllib.parse import parse_qs, urlparse

def round_to_25(value):
    """Round a number to the nearest multiple of 25."""
    return round(value / 25) * 25

class RequestHandler(SimpleHTTPRequestHandler):
    def do_GET(self):
        parsed_path = urlparse(self.path)
        
        if parsed_path.path == '/':
            file_path = 'index.html'

            if os.path.exists(file_path):
                self.send_response(200)
                self.send_header('Content-type', 'text/html')
                self.end_headers()
                with open(file_path, 'rb') as f:
                    self.wfile.write(f.read())
            else:
                self.send_error(404, "index.html not found")
        
        elif parsed_path.path == '/status':
            self.send_response(200)
            self.send_header("Content-Type", "application/json")
            self.end_headers()
            self.wfile.write(json.dumps({"status": "OK"}).encode("utf-8"))
        
        else:
            self.send_error(404, "Not Found")

    def do_POST(self):
        content_length = int(self.headers.get('Content-Length', 0))
        post_data = self.rfile.read(content_length).decode('utf-8')
        data = parse_qs(post_data)

        try:
            if 'weight' not in data or 'units' not in data:
                self.send_json_error(400, "Missing required fields: 'weight' and 'units'")
                return

            weight = float(data['weight'][0])
            units = data['units'][0]

            if weight <= 0:
                self.send_json_error(400, "Weight must be a positive number")
                return

            if units == "2":  # Convert kg to lbs
                weight *= 2.205
            
            therapeutic = 25
            level_I = round_to_25(0.866 * weight + 26.3)
            level_II = round_to_25(1.77 * weight + 49.4)
            level_III = round_to_25(500 + (weight - 20) * 20)
            level_IV = round_to_25(700 + (weight - 28) * 20)
            eiriel = round_to_25(1200 + (weight - 48) * 20)

            response_data = {
                "therapeutic": therapeutic,
                "level_I": level_I,
                "level_II": level_II,
                "level_III": level_III,
                "level_IV": level_IV,
                "eiriel": eiriel
            }

            self.send_response(200)
            self.send_header("Content-Type", "application/json")
            self.end_headers()
            self.wfile.write(json.dumps(response_data).encode("utf-8"))

        except ValueError:
            self.send_json_error(400, "Invalid weight format. Must be a number.")

    def send_json_error(self, code, message):
        """Send a JSON-formatted error response."""
        self.send_response(code)
        self.send_header("Content-Type", "application/json")
        self.end_headers()
        self.wfile.write(json.dumps({"error": message}).encode("utf-8"))

if __name__ == "__main__":
    # Debugging: Print working directory and files
    print("Current directory:", os.getcwd())
    print("Files in directory:", os.listdir())

    server_address = ('localhost', 8000)
    httpd = ThreadingHTTPServer(server_address, RequestHandler)
    print("Server running on http://localhost:8000")
    httpd.serve_forever()
