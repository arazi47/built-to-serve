import os


class ViewService:
    @staticmethod
    def is_image_content_type(content_type):
        return content_type.startswith("image/")

    @staticmethod
    def get_file_extension(full_path):
        extension = os.path.splitext(full_path)[1][1:]
        assert len(extension) > 0

        return extension

    @staticmethod
    def is_image_extension(file_extension):
        return file_extension in ["jpg", "png", "tiff", "svg", "gif"]

    @staticmethod
    def get_content_type_for_extension(file_extension):
        if file_extension in ["htm", "html", "php"]:
            return "text/html"
        elif file_extension == "css":
            return "text/css"
        elif file_extension == "js":
            return "text/javascript"
        elif ViewService.is_image_extension(file_extension):
            if file_extension == "jpg":
                return "image/jpeg"
            return "image/" + file_extension
        elif file_extension == "svg":
            return "image/svg+xml"

        raise ValueError("Unsupported content type for extension " + file_extension)
