import re


def update_variable(file_path, variable_name, new_value):
    
    with open(file_path, "r", encoding="utf-8") as f:
        file_content = f.read()
    
    # new_value = f'"{new_value}"'

    # search: variable_name = ...
    pattern = rf'^({variable_name}\s*=\s*).*$'
    
    if re.search(pattern, file_content, flags=re.MULTILINE):
        file_content = re.sub(pattern, rf'\1{new_value}', file_content, flags=re.MULTILINE)
    else:
        file_content += f"\n{variable_name} = {new_value}"

    with open(file_path, "w", encoding="utf-8") as f:
        f.write(file_content)


# HOW TO USE:
# update_variable("config.py", "SUPPORTED_LANGUAGES", "new_value")