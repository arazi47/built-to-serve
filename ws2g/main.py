from http.server import BaseHTTPRequestHandler, HTTPServer

import sys
from urllib import parse
from .views.views import (
    get_route_and_variables_for_path,
    index_files_in_content,
)
from .views.view_helper import ViewHelper


class Server(BaseHTTPRequestHandler):
    def send_status_and_headers(
        self, content_type, status_code=200, additional_headers={}
    ):
        """Send response, headers and end headers"""
        self.send_response(status_code)

        headers = {
            "Content-type": content_type,
        }
        headers.update(additional_headers)

        for header_keyword, header_value in headers.items():
            self.send_header(header_keyword, header_value)
        self.end_headers()

    def write_response(self, response, content_type):
        if ViewHelper.is_image_content_type(content_type):
            self.wfile.write(bytes(response))
        else:
            self.wfile.write(bytes(response, "utf-8"))

    def do_POST(self):
        try:
            (
                view_class,
                path_var_names,
                path_var_values,
            ) = get_route_and_variables_for_path(self.path[1:])
        except KeyError as e:
            self.send_status_and_headers("text/html", 404)
            self.write_response("Page not found", "text/html")

            print(e)
            return

        view_func_var_names = [
            var_name
            for var_name in view_class.view_func.__code__.co_varnames
            if var_name not in path_var_names
        ]
        length = int(self.headers.get("content-length"))
        field_data = self.rfile.read(length)
        fields = parse.parse_qs(str(field_data, "UTF-8"), keep_blank_values=True)
        rest_of_view_func_var_values = [
            fields[var_name] for var_name in view_func_var_names
        ]

        # The path may be admin/users/1234/edit
        # path_var_values will be [1234] - user id
        # rest_of_view_func_var_values will be whatever the user passed as input,
        # e.g. the new user spassword or whatever the admin edited
        response = view_class.view_func(*path_var_values, *rest_of_view_func_var_values)

        self.send_status_and_headers(view_class.content_type)
        self.write_response(response, view_class.content_type)

    def do_GET(self):
        try:
            view_class, _, path_var_values = get_route_and_variables_for_path(
                self.path[1:]
            )
        except KeyError as e:
            self.send_status_and_headers("text/html", 404)
            self.write_response("Page not found", "text/html")

            print(e)
            return

        response = view_class.view_func(*path_var_values)
        self.send_status_and_headers(view_class.content_type)
        self.write_response(response, view_class.content_type)


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
