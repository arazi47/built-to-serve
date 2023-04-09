from http.server import BaseHTTPRequestHandler, HTTPServer

from urllib import parse
from views import path_view, route
import views

class Server(BaseHTTPRequestHandler):
    def do_POST(self):
        view = path_view[self.path]
        length = int(self.headers.get('content-length'))
        field_data = self.rfile.read(length)
        fields = parse.parse_qs(str(field_data,"UTF-8"), keep_blank_values=True)
        response = view.build_POST_response(fields)

        self.send_response(view.status_code)
        for header_keyword, header_value in view.headers.items():
            self.send_header(header_keyword, header_value)
        self.end_headers()
        self.wfile.write(bytes(response, "utf-8"))

    def do_GET(self):
        try:
            view = path_view[self.path]
            response = view.build_GET_response()

            self.send_response(view.status_code)
            for header_keyword, header_value in view.headers.items():
                self.send_header(header_keyword, header_value)
            self.end_headers()

            if view.headers["Content-type"].startswith("image/"):
                self.wfile.write(bytes(response))
            else:
                self.wfile.write(bytes(response, "utf-8"))
        except Exception as e:
            print(e)
            print("We got here", self.path)
            view = views.BaseView()
            self.send_response(view.status_code)
            self.end_headers()

def main():
    views.prepare_special_routes()

    server = HTTPServer(("127.0.0.1", 8000), Server)

    try:
        server.serve_forever()
    except Exception as e:
        print(e)

if __name__ == "__main__":
    main()