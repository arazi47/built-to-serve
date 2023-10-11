import os
import glob
import re

from ws2g.custom_content_parser.custom_content_parser import transform_template_to_code
from ws2g.services.view_service import ViewService

CONTENT_DIRECTORY_NAME = "content"

"""
Stores all user defined routes and files inside CONTENT_DIRECTORY_NAME.
"""
content_routes = {}


def has_variable_form(string):
    """
    Returns True if string is of the form '<var>'
    """

    if len(string) < 3:
        return False

    if string[0] != "<" or string[-1] != ">":
        return False

    # Eliminate the < > pair
    string = string[1:-1]

    return string.isidentifier()


def get_route_and_variables_for_path(request_path, method):
    """
    Return the view_func, variable names and variable values
    for a given path, if one exists.

    content_routes entry: "/thing/<var1>/asd/<var2>/etc"
    request_path: "/thing/hithere/asd/12/etc"

    Return for the above example: <func>, ['var1', 'var2'], ['hithere', '12']

    If request_path does not match with any preexisting identifier in content_routes,
    an error is raised.
    """

    var_names = []
    var_values = []

    if request_path in content_routes:
        method_view_dict = content_routes[request_path]
        if method in method_view_dict:
            return method_view_dict[method], var_names, var_values

    original_request_path = request_path
    request_path = request_path.split("/")
    for route_identifier in content_routes.keys():
        if method not in content_routes[route_identifier]:
            continue

        patterns_match = True
        original_route_identifier = route_identifier
        route_identifier = route_identifier.split("/")
        identifier_contains_vars = False

        # If they split the same
        if len(request_path) == len(route_identifier):
            for path_elem, identifier_elem in zip(request_path, route_identifier):
                identifier_contains_vars = False
                if has_variable_form(identifier_elem):
                    if not identifier_contains_vars:
                        identifier_contains_vars = True

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

        if identifier_contains_vars and patterns_match:
            return (
                content_routes[original_route_identifier][method],
                var_names,
                var_values,
            )

    raise KeyError(
        "Exception for path="
        + original_request_path
        + ". The path is either not routed correctly or not created at all."
    )


class View:
    """
    Class wrapper for a 'view_func'.

    'file_path' is either either a relative path inside the content directory
    or an identifier that was created using the 'route' decorator.

    'content_type' is a string that will be sent in a response's header.

    'view_func' is the function that will be called when a client request
    matches 'file_path'.

    'method' is a string that represents whether the request is a GET or a POST.
    """

    def __init__(self, file_path, content_type, view_func, method) -> None:
        self.file_path = file_path
        self.content_type = content_type
        self.view_func = view_func
        self.method = method


def route(identifier, method):
    """
    Create a route, i.e. map an identifier to a 'view_func' (the 'method' parameter).
    This function is expected to be used as a decorator.
    The identifier input is not validated.
    """

    def wrapper(view_func):
        # Get rid of leading '/'
        id = identifier[1:]
        content_routes[id] = content_routes.get(
            id, {method: View(None, "text/html", view_func, method)}
        )
        return view_func

    return wrapper


def render(path, template_data=dict()):
    """
    Render a webpage without redirecting the client.

    'path' refers to a preexisting file in the content dir
    """

    relative_path = CONTENT_DIRECTORY_NAME + "/" + path
    if os.path.isfile(relative_path):
        content_type = ViewService.get_content_type_for_extension(
            ViewService.get_file_extension(relative_path)
        )
        if ViewService.is_image_content_type(content_type):
            with open(relative_path, "rb") as f:
                return f.read()
        else:
            return transform_template_to_code(relative_path, template_data)
    elif path[1:] in content_routes:
        method_view_dict = content_routes[path[1:]]
        # Can't render a POST
        try:
            return method_view_dict["GET"].view_func()
        except KeyError:
            raise KeyError('Page "' + path + '" not found!')


def redirect(path):
    """
    Return a special View, where content_type="redirect".
    This will redirect the client to the identifier specified
    in variable 'path', generating a GET request.
    """

    return View(path, "redirect", None, None)


def index_files_in_content_dir(full_path_to_content_dir=""):
    """
    Load preexisting files in the content directory in content_routes
    """

    # https://www.geeksforgeeks.org/why-do-python-lambda-defined-in-a-loop-with-different-values-all-return-the-same-result/
    def create_lambda(func, *args):
        return lambda: func(*args)

    if full_path_to_content_dir and full_path_to_content_dir[-1] != "/":
        full_path_to_content_dir += "/"

    for file_path in glob.iglob(
        full_path_to_content_dir + CONTENT_DIRECTORY_NAME + "/" + "**/*.*",
        recursive=True,
    ):
        file_path = file_path.lower()
        file_path = file_path.replace("\\", "/")

        file_name = file_path[
            file_path.find(CONTENT_DIRECTORY_NAME) + len(CONTENT_DIRECTORY_NAME) :
        ][1:]
        if os.path.isfile(file_path):
            file_extension = ViewService.get_file_extension(file_path)
            if (
                file_extension not in ("htm", "html", "php")
                and file_name not in content_routes
            ):
                content_type = ViewService.get_content_type_for_extension(file_extension)
                content_routes[file_name] = {
                    "GET": View(
                        file_path, content_type, create_lambda(render, file_name), "GET"
                    )
                }
