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
