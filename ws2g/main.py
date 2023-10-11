from http.server import BaseHTTPRequestHandler, HTTPServer

import sys
from urllib import parse
from .views.views import (
    get_route_and_variables_for_path,
    index_files_in_content_dir,
)
from .services.view_service import ViewService


class Server(BaseHTTPRequestHandler):
    def send_status_and_headers(
        self, content_type=None, status_code=200, additional_headers={}
    ):
        """
        Send response, headers and end headers
        """

        self.send_response(status_code)

        headers = {
            "Content-type": content_type,
        }
        headers.update(additional_headers)

        for header_keyword, header_value in headers.items():
            self.send_header(header_keyword, header_value)
        self.end_headers()

    def write_response(self, response, content_type):
        if ViewService.is_image_content_type(content_type):
            self.wfile.write(bytes(response))
        else:
            self.wfile.write(bytes(response, "utf-8"))

    def _write_response(self, view_class, response_body, empty_response=False):
        # self.send_status_and_headers(view_class.content_type)
        # if not empty_response:
        #     self.write_response(response_body, view_class.content_type)

        # if response_body.content_type == "redirect":
        #     self.redirect(response_body.file_path)
        view_class
        response_body
        empty_response
        # TODO

    def redirect(self, path):
        self.send_status_and_headers(
            status_code=301, additional_headers={"Location": path}
        )

    def send_404_page_not_found(self):
        """
        Send a simple HTML page with the 404 status
        saying that the requested page is not found.
        """

        self.send_status_and_headers("text/html", 404)
        self.write_response("Page not found", "text/html")

    def __get_func_argument_names(self, func):
        return func.__code__.co_varnames[: func.__code__.co_argcount]

    def __get_public_view_func_var_names_not_in_path(
        self, view_func_arg_names, path_var_names
    ):
        """
        Return a list of public view func var names (i.e. not starting with '__')
        and that are not in path (i.e. '/users/<user_id>/update')
        """

        view_func_var_names = [
            var_name
            for var_name in view_func_arg_names
            if var_name not in path_var_names and not var_name.startswith("__")
        ]

        return view_func_var_names

    def __get_request_fields(self):
        """
        Return an HTTP request fields.
        Usually has data when a POST request came in.
        """

        length = int(self.headers.get("content-length"))
        field_data = self.rfile.read(length)
        fields = parse.parse_qs(str(field_data, "UTF-8"), keep_blank_values=True)

        return fields

    def __get_public_view_func_var_values_not_in_path(
        self, request_fields, view_func_var_names
    ):
        return [request_fields[var_name][0] for var_name in view_func_var_names]

    def __get_extra_fields(self, request_fields, view_func_var_names):
        """
        In case there are any fields contained in the POST request
        which are unused by the client in view_func, they can still
        have access to them using the '__extra_fields' argument.
        """

        extra_fields = {}
        for field, value in request_fields.items():
            if field not in view_func_var_names:
                extra_fields[field] = value

        return extra_fields

    def do_POST(self):
        try:
            (
                view_class,
                path_var_names,
                path_var_values,
            ) = get_route_and_variables_for_path(self.path[1:], "POST")
        except KeyError as e:
            self.send_404_page_not_found()

            print(e)
            return

        request_fields = self.__get_request_fields()
        view_func_arg_names = self.__get_func_argument_names(view_class.view_func)
        public_view_func_var_names_not_in_path = (
            self.__get_public_view_func_var_names_not_in_path(
                view_func_arg_names, path_var_names
            )
        )
        public_view_func_var_values_not_in_path = (
            self.__get_public_view_func_var_values_not_in_path(
                request_fields, public_view_func_var_names_not_in_path
            )
        )

        # The path may be admin/users/1234/edit
        # path_var_values will be [1234] - user id
        # public_view_func_var_values_not_in_path will be whatever the user
        # passed as input, e.g. the new user's password
        view_func_arg_values = [
            *path_var_values,
            *public_view_func_var_values_not_in_path,
        ]

        if "__extra_fields" in view_class.view_func.__code__.co_varnames:
            extra_fields = self.__get_extra_fields(
                request_fields,
                public_view_func_var_names_not_in_path,
            )

            response = view_class.view_func(
                *view_func_arg_values, __extra_fields=extra_fields
            )
        else:
            response = view_class.view_func(*view_func_arg_values)

        if response.content_type == "redirect":
            self.redirect(response.file_path)
        else:
            self.send_status_and_headers(view_class.content_type)
            self.write_response(response, view_class.content_type)

    def do_GET(self):
        try:
            view_class, _, path_var_values = get_route_and_variables_for_path(
                self.path[1:], "GET"
            )
        except KeyError as e:
            self.send_404_page_not_found()

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

    index_files_in_content_dir()
    server = HTTPServer((server_address, server_port), Server)

    try:
        server.serve_forever()
    except Exception as e:
        print(e)


if __name__ == "__main__":
    run()
