CONTENT_DIRECTORY_NAME = "content"

# Public routes, defined by user
# TODO rename this to public_routes
# or find a more suitable name
path_view = {}

# All files from CONTENT_DIRECTORY_NAME are indexed here
content_routes = {}


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

        path_view[identifier] = view_class(file_path)
        return view_class

    return wrapper


def render(page):
    return path_view[page].build_GET_response()


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


class HTML(BaseView):
    def __init__(self, file_path="", status_code=404, content_type="text/html") -> None:
        super().__init__(file_path, status_code, content_type)

    def build_GET_response(self) -> str:
        with open(self.file_path) as f:
            return f.read()


class CSS(BaseView):
    def __init__(self, file_path, status_code=404, content_type="text/css") -> None:
        super().__init__(file_path, status_code, content_type)

    def build_GET_response(self) -> str:
        with open(self.file_path) as f:
            return f.read()


class JavaScript(BaseView):
    def __init__(
        self, file_path="", status_code=404, content_type="text/javascript"
    ) -> None:
        super().__init__(file_path, status_code, content_type)

    def build_GET_response(self) -> str:
        with open(self.file_path) as f:
            return f.read()


class PHP(BaseView):
    def __init__(self, file_path="", status_code=404, content_type="text/html") -> None:
        super().__init__(file_path, status_code, content_type)

    def build_GET_response(self) -> str:
        with open(self.file_path) as f:
            return f.read()


class Image(BaseView):
    def __init__(self, file_path, status_code=404, content_type="image/jpeg") -> None:
        super().__init__(file_path, status_code, content_type)

    def build_GET_response(self) -> str:
        with open(self.file_path, "rb") as f:
            return f.read()


def index_files_in_content(path_to_content=""):
    import glob
    import os

    # There are probably more cases that should be handled
    image_extensions = ["gif", "jpg", "png", "tiff"]

    for file_path in glob.iglob(
        path_to_content + "/" + CONTENT_DIRECTORY_NAME + "/" + "**/*.*", recursive=True
    ):
        file_path = file_path.lower()
        file_path = file_path.replace("\\", "/")

        request_path = file_path[file_path.find(CONTENT_DIRECTORY_NAME) :]
        if os.path.isfile(file_path) and request_path not in content_routes:
            if file_path.endswith(".html"):
                content_routes[request_path] = HTML(file_path, status_code=200)
            elif file_path.endswith(".css"):
                content_routes[request_path] = CSS(file_path, status_code=200)
            elif any(file_path.endswith(ext) for ext in image_extensions):
                content_type = file_path[file_path.rfind(".") + 1 :]
                if content_type == "jpg":
                    content_type = "jpeg"

                content_routes[request_path] = Image(
                    file_path, status_code=200, content_type="image/" + content_type
                )
            elif file_path.endswith(".svg"):
                content_routes[request_path] = Image(
                    file_path,
                    status_code=200,
                    content_type="image/" + "svg+xml",
                )
            elif file_path.endswith(".js"):
                content_routes[request_path] = JavaScript(file_path, status_code=200)
            elif file_path.endswith(".php"):
                content_routes[request_path] = PHP(file_path, status_code=200)
            else:
                print("Unhandled special route:", file_path)
