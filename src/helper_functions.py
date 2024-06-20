import numpy as np
from sklearn.cluster import KMeans
import pandas as pd
from tkinter import simpledialog, Tk


def get_calibrated_threshold(label, file, names):
    root = Tk()
    root.withdraw()  # Hide the main Tkinter window

    # Prompt user for PC, mixPC, and NC well names using simpledialog
    pc_well = simpledialog.askstring("Input", "Enter the name of the Positive Control well", parent=root)
    mixpc_well = simpledialog.askstring("Input", "Enter the name of the Mixed Positive Control well", parent=root)
    nc_well = simpledialog.askstring("Input", "Enter the name of the Negative Control well", parent=root)
    
    root.destroy()  # Destroy the Tkinter window

    # Strip any whitespace from the well names
    pc_well = pc_well.strip()
    mixpc_well = mixpc_well.strip()
    nc_well = nc_well.strip()
    
    # Validate well names
    if pc_well not in names:
        raise ValueError(f"Well name {pc_well} is not in the list of provided well names.")
    if mixpc_well not in names:
        raise ValueError(f"Well name {mixpc_well} is not in the list of provided well names.")
    if nc_well not in names:
        raise ValueError(f"Well name {nc_well} is not in the list of provided well names.")
    # Read and filter the wells in chunks
    # pc_data, mixpc_data, nc_data = read_and_filter_wells_chunked(file, pc_well, mixpc_well, nc_well)
    # threshold = calibrate_threshold(pc_data[label].values, mixpc_data[label].values, nc_data[label].values)
    chosen_well_names =  [pc_well, mixpc_well, nc_well]
    well_data = split_well_data_to_lists(file, chosen_well_names)
    pc_data = well_data[chosen_well_names[0]]
    mixpc_data = well_data[chosen_well_names[1]]
    nc_data = well_data[chosen_well_names[2]]
    threshold = calibrate_threshold(pc_data, mixpc_data, nc_data)
    # Calibrate the threshold
    
    return threshold

def split_well_data_to_lists(file_path, wells_of_interest, chunk_size=100000):
    print(wells_of_interest)
    print("splitting")
    # Define the data types for the columns
    dtype_spec = {
        'Well': 'str',
        'Sample': 'str',
        'Channel': 'str',
        'Cycled volume': 'float64',
        'Threshold': 'float64',
        'Partition': 'float64',
        'Is invalid': 'str',
        'Is positive': 'str',
        'RFU': 'float64'
    }

    # Initialize dictionaries to hold RFU values for each well of interest
    well_data = {well: [] for well in wells_of_interest}
    
    # Read the CSV file in chunks with specified data types
    for chunk in pd.read_csv(file_path, chunksize=chunk_size, dtype=dtype_spec, low_memory=False):
        # Filter rows based on the specified wells
        print("ffff")
        filtered_chunk = chunk[chunk['Well'].isin(wells_of_interest)] #----> error
        print(filtered_chunk)
        
        # Extract RFU values and append to the respective lists
        for well in wells_of_interest:
            rfu_values = filtered_chunk[filtered_chunk['Well'] == well]['RFU'].dropna().tolist()
            well_data[well].extend(rfu_values)
    
    return well_data
def read_and_filter_wells_chunked(csv_file, pc_well, mixpc_well, nc_well, chunk_size=10000):
    print(pc_well, mixpc_well,nc_well)
    print("reading filtering")
    pc_data_list = []
    mixpc_data_list = []
    nc_data_list = []
    
    pc_found, mixpc_found, nc_found = False, False, False

    # Read the CSV file in chunks
    for chunk in pd.read_csv(csv_file, chunksize=chunk_size):
        # Filter each chunk for the specified wells
        if not pc_found:
            pc_chunk = chunk[chunk['Well'] == pc_well]
            if not pc_chunk.empty:
                pc_data_list.append(pc_chunk)
                pc_found = True

        if not mixpc_found:
            mixpc_chunk = chunk[chunk['Well'] == mixpc_well]
            if not mixpc_chunk.empty:
                mixpc_data_list.append(mixpc_chunk)
                mixpc_found = True

        if not nc_found:
            nc_chunk = chunk[chunk['Well'] == nc_well]
            if not nc_chunk.empty:
                nc_data_list.append(nc_chunk)
                nc_found = True

        # If all wells are found, break the loop
        if pc_found and mixpc_found and nc_found:
            break

    # Concatenate all chunks
    pc_data = pd.concat(pc_data_list)
    mixpc_data = pd.concat(mixpc_data_list)
    nc_data = pd.concat(nc_data_list)

    print("#####")
    print(pc_data)
    print("######")
    print(mixpc_data)
    print("######")
    print(nc_data)
    print("#####")
    
    return pc_data, mixpc_data, nc_data


def calibrate_threshold(pc_data, mixpc_data, nc_data):
    # Assume the data provided are lists of RFU values
    pc_values = np.array(pc_data)
    mixpc_values = np.array(mixpc_data)
    nc_values = np.array(nc_data)
    # Initial threshold based on positive control
    pc_mean = np.mean(pc_values)
    pc_std = np.std(pc_values)
    initial_threshold = pc_mean + 2 * pc_std
    
    # Refine using mixed positive control
    kmeans = KMeans(n_clusters=2)
    kmeans.fit(mixpc_values.reshape(-1, 1))
    clusters = sorted(kmeans.cluster_centers_.flatten())
    refined_threshold = max(initial_threshold, clusters[1])  # Ensure threshold is not lowered
    
    # Validate with negative control
    nc_false_positives = np.sum(nc_values>= refined_threshold) / len(nc_values)
    
    # Adjust threshold if FPR > 0.01%
    while nc_false_positives > 0.0001:
        refined_threshold += 0.01  # Incrementally increase threshold
        nc_false_positives = np.sum(nc_values >= refined_threshold) / len(nc_values)
    
    return refined_threshold
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
