import os
# from ws2g.custom_content_parser import get_custom_content_index


def test_get_custom_content_index():
    file = r"/opt/hostedtoolcache/Python/3.11.5/x64/lib/python3.11/site-packages/ws2g/custom_content_parser/"
    with open(file, "r") as f:
        for line in f:
            print(line)

    # expected_indices = [(23, 27), (38, 47)]

    # iterator = get_custom_content_index(
    #     os.path.dirname(__file__) + "\\test_file_input.html"
    # )

    # for expected_cc_start_index, expected_cc_end_index in expected_indices:
    #     cc_start_index, cc_end_index = next(iterator)
    #     assert cc_start_index == expected_cc_start_index
    #     assert cc_end_index == expected_cc_end_index
