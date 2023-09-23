import os
from ws2g.views.views import HTMLFileView, content_routes, index_files_in_content


def test_prepare_special_routes():
    # assert content_routes == {}

    # index_files_in_content(os.path.dirname(__file__))

    # expected_content_routes = {
    #     "/thing.html": HTMLFileView(),
    #     "/somefolder/thing_inside_folder.html": HTMLFileView(),
    # }

    # assert len(content_routes) == len(expected_content_routes)

    # for relative_path, obj in content_routes.items():
    #     assert relative_path in expected_content_routes
    #     assert isinstance(expected_content_routes[relative_path], type(obj))
