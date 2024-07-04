# Itai Alcalai
# utils.py

# Default well matrix used for creating well name dictionary
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
    """
    Creates a dictionary mapping default well names to user-defined well names.

    Args:
        user_input_matrix (list): A matrix of user-defined well names.

    Returns:
        dict: A dictionary where keys are default well names and values are user-defined well names.
    """
    well_name_dict = {}
    # Iterate over the user input matrix to create the mapping
    for i, row in enumerate(user_input_matrix):
        for j, well_name in enumerate(row):
            default_well_name = default_well_matrix[i][j]
            well_name_dict[default_well_name] = well_name
    return well_name_dict

def get_color(file_path: str) -> str:
    """
    Extracts a color code from the file path.

    Args:
        file_path (str): The file path from which to extract the color code.

    Returns:
        str: The extracted color code.
    """
    # Remove all characters from the right to the last '\'
    last_slash_index = file_path.rfind('\\')
    if last_slash_index == -1:
        last_slash_index = file_path.rfind('/')  # In case it's a forward slash

    if last_slash_index != -1:
        file_path = file_path[last_slash_index + 1:]

    # Count 3 '_' chars and delete everything including the fourth one
    underscore_count = 0
    for i, char in enumerate(file_path):
        if char == '_':
            underscore_count += 1
        if underscore_count == 4:
            file_path = file_path[:i]
            break
    
    # Return the string from start to the next '_'
    i = 3
    while i > 0:
        next_underscore_index = file_path.find('_')
        if next_underscore_index != -1:
            file_path = file_path[next_underscore_index + 1:]
            i -= 1

    return file_path
