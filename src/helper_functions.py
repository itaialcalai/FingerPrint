# strip file name for the probe color
def get_color(file_path: str) -> str:
    # Step 1: Remove all characters from the right to the last '\'
    last_slash_index = file_path.rfind('\\')
    if last_slash_index == -1:
        last_slash_index = file_path.rfind('/')  # In case it's a forward slash

    if last_slash_index != -1:
        file_path = file_path[last_slash_index + 1:]

    # Step 2: Count 3 '_' chars and delete everything including the third one
    underscore_count = 0
    for i, char in enumerate(file_path):
        if char == '_':
            underscore_count += 1
        if underscore_count == 4:
            file_path = file_path[:i]
            break
    
    # Step 3: Return the string from start to the next '_'
    i = 3
    while i > 0:
        next_underscore_index = file_path.find('_')
        if next_underscore_index != -1:
            file_path =  file_path[next_underscore_index + 1:]
            i -= 1

    return file_path

# Initializing the matrix with default well names (8x3 transposed)
default_well_matrix = [
    ["A1", "A2", "A3"],
    ["B1", "B2", "B3"],
    ["C1", "C2", "C3"],
    ["D1", "D2", "D3"],
    ["E1", "E2", "E3"],
    ["F1", "F2", "F3"],
    ["G1", "G2", "G3"],
    ["H1", "H2", "H3"]
]
def create_well_name_dict(user_input_matrix):
    well_name_dict = {}
    for i, row in enumerate(user_input_matrix):
        for j, well_name in enumerate(row):
            default_well_name = default_well_matrix[i][j]
            well_name_dict[default_well_name] = well_name
    return well_name_dict

# next function
def map_indices(rfus, mod_value=80):
    length = len(rfus)
    result = [None] * length

    current_value = 1
    index = 0

    while index < length:
        for i in range(0, length, mod_value):
            if index + i < length:
                result[index + i] = current_value
            else:
                break
        current_value += 1
        index += 1

    return result
