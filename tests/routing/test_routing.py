import os
from ws2g.views.views import content_routes, index_files_in_content_dir


def test_htm_html_php_files_are_not_indexed_by_default():
    assert content_routes == {}
    
    index_files_in_content_dir(os.path.dirname(__file__))

    assert content_routes == {}

