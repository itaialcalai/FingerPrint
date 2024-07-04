# Itai Alcalai
# threshold_calibration.py

import numpy as np
from sklearn.cluster import KMeans
import pandas as pd
from utils import default_well_matrix

def get_calibrated_threshold(file, names, ds):
    """
    Calibrates the threshold based on positive, mixed positive, and negative control wells.

    Args:
        file (str): Path to the data file.
        names (dict): Dictionary of well names.
        ds (dict): Dictionary containing control well names.

    Returns:
        float: The calibrated threshold value.
    """
    threshold = None

    # Extracting control well names from the dictionary
    pc = ds.get('positive')
    mixpc = ds.get('mix_positive')
    nc = ds.get('negative')
    
    # Validate control well names against the provided well names
    if pc not in names:
        raise ValueError(f"Well name {pc} is not in the list of provided well names.")
    if mixpc not in names:
        raise ValueError(f"Well name {mixpc} is not in the list of provided well names.")
    if nc not in names:
        raise ValueError(f"Well name {nc} is not in the list of provided well names.")

    chosen_well_names = [pc, mixpc, nc]

    # Extract RFU values for the chosen wells
    data = extract_rfu_values(file, chosen_well_names)
    # Calibrate the threshold based on the extracted data
    threshold = calibrate_threshold(data, chosen_well_names)

    return threshold

def extract_rfu_values(file_path, chosen_wells):
    """
    Extracts RFU values from the file for the chosen wells.

    Args:
        file_path (str): Path to the data file.
        chosen_wells (list): List of chosen well names.

    Returns:
        dict: Dictionary with well names as keys and lists of RFU values as values.
    """
    with open(file_path, 'r') as file:
        first_line = file.readline().strip()
        skip_first_line = 'sep=' in first_line

    # Read the CSV file in chunks to handle large file sizes
    reader = pd.read_csv(file_path, delimiter=',', skiprows=1 if skip_first_line else 0, chunksize=10000)
    well_data = {well: [] for well in chosen_wells}
    
    # Iterate through each chunk to extract RFU values for the chosen wells
    for chunk in reader:
        for index, row in chunk.iterrows():
            well = row.iloc[0]
            if well in chosen_wells and 'RFU' in row and pd.notna(row['RFU']):
                well_data[well].append(row['RFU'])
    return well_data

def calibrate_threshold(data, well_names):
    """
    Calibrates the threshold using data from the control wells.

    Args:
        data (dict): Dictionary with well names as keys and lists of RFU values as values.
        well_names (list): List of control well names.

    Returns:
        float: The refined threshold value.
    """
    # Retrieve RFU values for each control well
    pc_values = np.array(data[well_names[0]])
    mixpc_values = np.array(data[well_names[1]])
    nc_values = np.array(data[well_names[2]])
    
    # Initial threshold based on positive control
    pc_mean = np.mean(pc_values)
    pc_std = np.std(pc_values)
    initial_threshold = pc_mean + 2 * pc_std
    
    # Refine threshold using mixed positive control
    kmeans = KMeans(n_clusters=2)
    kmeans.fit(mixpc_values.reshape(-1, 1))
    clusters = sorted(kmeans.cluster_centers_.flatten())
    refined_threshold = max(initial_threshold, clusters[1])  # Ensure threshold is not lowered
    
    # Validate threshold with negative control
    nc_false_positives = np.sum(nc_values >= refined_threshold) / len(nc_values)
    
    # Adjust threshold if the false positive rate (FPR) is greater than 0.01%
    while nc_false_positives > 0.0001:
        refined_threshold += 0.01  # Incrementally increase threshold
        nc_false_positives = np.sum(nc_values >= refined_threshold) / len(nc_values)
    
    return refined_threshold
