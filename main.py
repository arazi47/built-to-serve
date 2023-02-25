from http.server import BaseHTTPRequestHandler, HTTPServer

from views import path_view, route
import views

class Server(BaseHTTPRequestHandler):
    def do_POST(self):
        from urllib import parse
        length = int(self.headers.get('content-length'))
        field_data = self.rfile.read(length)
        fields = parse.parse_qs(str(field_data,"UTF-8"))
        username = fields["username"][0]
        comment = fields["comment"][0]

        import sqlite3
        conn = sqlite3.connect('guestbook.db')
        conn.execute("INSERT INTO GuestBook (username,comment,posted_on) \
            VALUES (?, ?, DATE())",(username, comment));
        # It is necessary commit, otherwise changes will not be saved upon calling close()
        conn.commit()
        conn.close()

        view = path_view[self.path]
        self.send_response(view.status_code)
        for header_keyword, header_value in view.headers.items():
            self.send_header(header_keyword, header_value)
        self.end_headers()
        self.wfile.write(bytes(view.build_response(), "utf-8"))

    def do_GET(self):
        try:
            view = path_view[self.path]

            self.send_response(view.status_code)
            for header_keyword, header_value in view.headers.items():
                self.send_header(header_keyword, header_value)
            self.end_headers()

            if view.headers["Content-type"].startswith("image/"):
                self.wfile.write(bytes(view.build_response()))
            else:
                self.wfile.write(bytes(view.build_response(), "utf-8"))
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