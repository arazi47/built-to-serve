import os
from ws2g.views.views import HTML, private_routes, index_files_in_content


def test_prepare_special_routes():
    assert private_routes == {}

    index_files_in_content(os.path.dirname(__file__))


    expected_private_routes = {
        'content/thing.html': HTML(),
        'content/somefolder/thing_inside_folder.html': HTML()
    }
    
    assert len(private_routes) == len(expected_private_routes)
    
    for relative_path, obj in private_routes.items():
        assert relative_path in expected_private_routes
        assert isinstance(expected_private_routes[relative_path], type(obj))