# https://stackoverflow.com/a/34938623
import sys
import os

sys.path.append(os.path.dirname(os.path.realpath(__file__)) + "/../../ws2g")

from custom_content_parser import get_custom_content_index  # noqa: E402


def test_get_custom_content_index():
    expected_indices = [(23, 27), (38, 47)]
    iterator = get_custom_content_index(
        r"F:\repos\webserver-to-go\tests\custom_content_parser\test_file_input.html"
    )

    for expected_cc_start_index, expected_cc_end_index in expected_indices:
        cc_start_index, cc_end_index = next(iterator)
        assert cc_start_index == expected_cc_start_index
        assert cc_end_index == expected_cc_end_index
