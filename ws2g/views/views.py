import os
import glob
import re

from ws2g.views.view_helper import ViewHelper

CONTENT_DIRECTORY_NAME = "content"

# Stores all user defined routes and
# all routes created from files inside CONTENT_DIRECTORY_NAME
content_routes = {}


def has_variable_form(string):
    """Returns True if string has the form <var>"""
    if len(string) < 3:
        return False

    if string[0] != "<" or string[-1] != ">":
        return False

    # Eliminate the < > pair
    string = string[1:-1]

    return string.isidentifier()


def get_route_and_variables_for_path(path):
    """Return the correct function to exeecute for given path
    along with the extracted variables."""
    if path in content_routes:
        return content_routes[path]

    # content_routes entry: /thing/<var1>/asd/<var2>/etc
    # path: /thing/hithere/asd/12/etc

    var_names = []
    var_values = []

    path = path.split("/")
    for route_identifier in content_routes.keys():
        patterns_match = True
        route_identifier = route_identifier.split("/")

        # If they split the same
        if len(path) == len(route_identifier):
            for path_elem, identifier_elem in zip(path, route_identifier):
                if has_variable_form(identifier_elem):
                    # Check that path_elem contains only numbers, alphas and _
                    if not re.fullmatch(r"[\w\d_]+", path_elem):
                        patterns_match = False
                        break
                    else:
                        var_names.append(identifier_elem)
                        var_values.append(path_elem)
                else:
                    if path_elem != identifier_elem:
                        patterns_match = False
                        break

        if patterns_match:
            return content_routes[route_identifier], var_names, var_values

    raise KeyError(
        "Exception for path="
        + path
        + ". The path is either not routed correctly or not created at all."
    )


content_types = {}


def route(identifier, path=None):
    if not path:
        path = identifier

    def wrapper(view_class):
        # Route path to an instance of the class
        # [1:] - without leading '/'
        file_path = path[1:]
        file_path = CONTENT_DIRECTORY_NAME + "/" + file_path
        if file_path == CONTENT_DIRECTORY_NAME + "/":
            file_path = CONTENT_DIRECTORY_NAME + "/index.html"

        content_routes[identifier] = view_class(file_path)
        content_types[identifier] = ViewHelper.get_content_type_for_extension(
            ViewHelper.get_file_extension(file_path)
        )
        return view_class

    return wrapper


def render(path):
    return content_routes[path].build_GET_response()


class BaseView:
    def __init__(self, file_path="", status_code=404, content_type="text/html") -> None:
        self.file_path = file_path
        self.status_code = status_code
        self.headers = {
            "Content-type": content_type,
        }

    def build_GET_response(self) -> str:
        return "Not implemented"

    def build_POST_response(self) -> str:
        return "Not implemented"

    def __str__(self) -> str:
        return (
            "File path: "
            + self.file_path
            + "; status="
            + str(self.status_code)
            + "; headers="
            + str(self.headers)
        )


class HTMLFileView(BaseView):
    def __init__(self, file_path="", status_code=404, content_type="text/html") -> None:
        super().__init__(file_path, status_code, content_type)

    def build_GET_response(self) -> str:
        with open(self.file_path) as f:
            return f.read()


class CSSFileView(BaseView):
    def __init__(self, file_path, status_code=404, content_type="text/css") -> None:
        super().__init__(file_path, status_code, content_type)

    def build_GET_response(self) -> str:
        with open(self.file_path) as f:
            return f.read()


class JavaScriptFileView(BaseView):
    def __init__(
        self, file_path="", status_code=404, content_type="text/javascript"
    ) -> None:
        super().__init__(file_path, status_code, content_type)

    def build_GET_response(self) -> str:
        with open(self.file_path) as f:
            return f.read()


class PHPFileView(BaseView):
    def __init__(self, file_path="", status_code=404, content_type="text/html") -> None:
        super().__init__(file_path, status_code, content_type)

    def build_GET_response(self) -> str:
        with open(self.file_path) as f:
            return f.read()


class ImageFileView(BaseView):
    def __init__(self, file_path, status_code=404, content_type="image/jpeg") -> None:
        super().__init__(file_path, status_code, content_type)

    def build_GET_response(self) -> str:
        with open(self.file_path, "rb") as f:
            return f.read()


class MiscFileView(BaseView):
    def __init__(self, file_path="", status_code=404, content_type="text/html") -> None:
        super().__init__(file_path, status_code, content_type)

    def build_GET_response(self) -> str:
        with open(self.file_path) as f:
            return f.read()


def index_files_in_content(full_path_to_content_dir=""):
    extension_view_class = {
        "html": HTMLFileView,
        "css": CSSFileView,
        "js": JavaScriptFileView,
        "php": PHPFileView,
        "gif": ImageFileView,
        "jpg": ImageFileView,
        "png": ImageFileView,
        "tiff": ImageFileView,
        "svg": ImageFileView,
    }

    if full_path_to_content_dir and full_path_to_content_dir[-1] != "/":
        full_path_to_content_dir += "/"

    for file_path in glob.iglob(
        full_path_to_content_dir + CONTENT_DIRECTORY_NAME + "/" + "**/*.*",
        recursive=True,
    ):
        file_path = file_path.lower()
        file_path = file_path.replace("\\", "/")

        request_path = file_path[
            file_path.find(CONTENT_DIRECTORY_NAME) + len(CONTENT_DIRECTORY_NAME) :
        ]
        if os.path.isfile(file_path) and request_path not in content_routes:
            file_extension = ViewHelper.get_file_extension(file_path)
            content_type = ViewHelper.get_content_type_for_extension(file_extension)

            if file_extension not in extension_view_class:
                print(
                    "Warning, unsupported file "
                    + file_path
                    + '. Interpreting as misc file (content_type="text/html").'
                )
                content_routes[request_path] = MiscFileView(
                    file_path, status_code=200, content_type="text/html"
                )
            else:
                content_routes[request_path] = extension_view_class[file_extension](
                    file_path, status_code=200, content_type=content_type
                )
