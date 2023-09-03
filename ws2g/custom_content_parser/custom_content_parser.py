def get_custom_content(file):
    custom_content = []
    in_cc = False
    with open(file, "r") as f:
        for line in f:
            if line.strip() == "{{customcontent}}":
                custom_content = []
                in_cc = True
            if in_cc:
                if line.strip() == "{{endcustomcontent}}":
                    in_cc = False
                    custom_content.append(line)
                    yield custom_content

                custom_content.append(line)


def read_whole_file(file):
    lines = []
    with open(file, "r") as f:
        for line in f:
            lines.append(line)

    return lines


def write_to_file(file, lines):
    with open(file, "w") as f:
        for line in lines:
            f.write(line)


def get_custom_content_index(file):
    in_cc = False
    cc_start_index = cc_end_index = None
    with open(file, "r") as f:
        line_index = 0
        for line in f:
            if line.strip() == "{{customcontent}}":
                cc_end_index = None  # reset cc_end_index because of yield
                in_cc = True
                cc_start_index = line_index
            if in_cc:
                if line.strip() == "{{endcustomcontent}}":
                    in_cc = False
                    cc_end_index = line_index

                    yield cc_start_index, cc_end_index
            line_index += 1


def get_lines_until_end(lines, command="TODO"):
    # Get inside of a block (e.g. all lines inside a for block)
    output = []
    for line in lines:
        if "{{endfor}}" in line:
            return output

        output.append(line)

    return output


def transform_custom_content_to_html(lines, variables):
    output = []
    i = 0
    while i < len(lines):
        split_line = lines[i].replace("{", "").replace("}", "").split()
        command = split_line[0]
        if command == "for":
            list_var = split_line[3]

            # Hopefully variables[list_var] is already something
            # like a list, which we can iterate over
            # list var can be of type list or an iterable class or...
            # the next line assumes list_var is "repo.fetch_all()"
            iterable = variables[list_var.split(".")[0]]
            lines_that_have_to_be_repeated = get_lines_until_end(lines[i + 1 :])
            for single_instance in iterable:
                for j in lines_that_have_to_be_repeated:
                    if "{{" in j and "}}" in j:
                        opener = j.find("{{") + 2
                        ender = j.find("}}")

                        attr_string = j[opener:ender].split(".")
                        if len(attr_string) == 1:
                            # Plain old value
                            j = j.replace(
                                "{{" + j[opener:ender] + "}}", str(single_instance)
                            )
                        else:
                            if j[opener:ender][-1] == ")":
                                # object.function()
                                # No support for function parameters
                                # [:-2] function() => function
                                j = j.replace(
                                    "{{" + j[opener:ender] + "}}",
                                    str(
                                        getattr(single_instance, attr_string[1][:-2])()
                                    ),
                                )
                            else:
                                # object.attribute
                                j = j.replace(
                                    "{{" + j[opener:ender] + "}}",
                                    str(getattr(single_instance, attr_string[1])),
                                )

                    output.append(j)

                i += len(lines_that_have_to_be_repeated)
        else:
            # If we can't figure out what the command is,
            # just add the line to the output.
            # This could be something like a <br> etc
            output.append(lines[i])

        i += 1

    return output


def transform_template_to_code(file_path, variables):
    whole_file = read_whole_file(file_path)
    cc_index_gen = get_custom_content_index(file_path)

    # whole_file with the transformed_lines replacing the custom content lines
    result = []
    prev_cc_end_index = -1

    for cc in get_custom_content(file_path):
        cc_start_index, cc_end_index = next(cc_index_gen)

        if not cc:
            return "".join(whole_file)

        transformed_lines = transform_custom_content_to_html(cc[1:-1], variables)
        result += whole_file[prev_cc_end_index + 1 : cc_start_index] + transformed_lines
        prev_cc_end_index = cc_end_index

    result += whole_file[prev_cc_end_index + 1 :]

    return "".join(result)
