from http.server import BaseHTTPRequestHandler, HTTPServer

import sys
from urllib import parse
from .views.views import (
    get_route_for_path,
    index_files_in_content,
)
from .views.view_helper import ViewHelper


class Server(BaseHTTPRequestHandler):
    def send_headers(self, headers):
        for header_keyword, header_value in headers.items():
            self.send_header(header_keyword, header_value)

    def send_view(self, view):
        """Send response, headers and end headers"""
        self.send_response(view.status_code)
        self.send_headers(view.headers)
        self.end_headers()

    def do_POST(self):
        try:
            view = get_route_for_path(self.path)
        except KeyError as e:
            self.send_response(404)
            self.end_headers()

            raise e

        length = int(self.headers.get("content-length"))
        field_data = self.rfile.read(length)
        fields = parse.parse_qs(str(field_data, "UTF-8"), keep_blank_values=True)
        response = view.build_POST_response(fields)

        self.send_view(view)
        self.wfile.write(bytes(response, "utf-8"))

    def do_GET(self):
        try:
            view = get_route_for_path(self.path)
        except KeyError as e:
            self.send_response(404)
            self.end_headers()

            raise e

        response = view.build_GET_response()

        self.send_view(view)
        if ViewHelper.is_image_content_type(view.headers["Content-type"]):
            self.wfile.write(bytes(response))
        else:
            self.wfile.write(bytes(response, "utf-8"))


def run():
    if len(sys.argv) < 3:
        print(
            '[WARNING] Missing one or more arguments. Using default values server_address="0.0.0.0", server_port=8000'  # noqa: E501
        )
        server_address = "0.0.0.0"
        server_port = 8000
    else:
        server_address = str(sys.argv[1])
        server_port = int(sys.argv[2])

    index_files_in_content()

    server = HTTPServer((server_address, server_port), Server)

    try:
        server.serve_forever()
    except Exception as e:
        print(e)


if __name__ == "__main__":
    run()
