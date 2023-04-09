def get_custom_content(file):
    custom_content = []
    in_cc = False
    with open(file, "r") as f:
        for line in f:
            if line.strip() == "{{customcontent}}":
                in_cc = True
            if in_cc:
                if line.strip() == "{{endcustomcontent}}":
                    in_cc = False

                custom_content.append(line)
    
    return custom_content

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
                in_cc = True
                cc_start_index = line_index
            if in_cc:
                if line.strip() == "{{endcustomcontent}}":
                    in_cc = False
                    cc_end_index = line_index
            line_index += 1
        
    assert cc_start_index
    assert cc_end_index
    return cc_start_index, cc_end_index

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
            # for for_var in list_var
            for_var = split_line[1]
            list_var = split_line[3]

            # Hopefully variables[list_var] is already something
            # like a list, which we can iterate over
            #print("LISTVAR", list_var)
            # list var can be of type list or an iterable class or...
            # the next line assumes list_var is "repo.fetch_all()"
            iterable = variables[list_var.split(".")[0]]
            lines_that_have_to_be_repeated = get_lines_until_end(lines[i + 1:])
            for single_instance in iterable:
                for jindex, j in enumerate(lines_that_have_to_be_repeated):
                    if "{{" in j and "}}" in j:
                        opener = j.find("{{") + 2
                        ender = j.find("}}")

                        attr_string = j[opener:ender].split(".")[1]
                        j = j.replace("{{" + j[opener:ender] + "}}", str(getattr(single_instance, attr_string)))
                    output.append(j)
                
                i += len(lines_that_have_to_be_repeated)
        else:
            # If we can't figure out what the command is, just print the line
            output.append(lines[i])
        
        i += 1

    return output

def transform_template_to_code(file_path, variables):
    whole_file = read_whole_file(file_path)
    cc = get_custom_content(file_path)
    if not cc:
        return "".join(whole_file)
    transformed_lines = transform_custom_content_to_html(cc[1:-1], variables)
    cc_start_index, cc_end_index = get_custom_content_index(file_path)

    return "".join(whole_file[:cc_start_index] + transformed_lines + whole_file[cc_end_index + 1:])
