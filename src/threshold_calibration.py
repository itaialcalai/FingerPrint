import numpy as np
from sklearn.cluster import KMeans
import pandas as pd
from tkinter import simpledialog
from helper_functions import default_well_matrix

def get_calibrated_threshold(label, file, names, event):
    threshold = None

    def prompt_for_wells():
        nonlocal threshold
        # Prompt user for PC, mixPC, and NC well names using simpledialog
        pc = simpledialog.askstring("Input", "Enter the name of the Positive Control well", parent=label)
        mixpc = simpledialog.askstring("Input", "Enter the name of the Mixed Positive Control well", parent=label)
        nc = simpledialog.askstring("Input", "Enter the name of the Negative Control well", parent=label)
        
        # Strip any whitespace from the well names
        pc_well = pc.strip()
        mixpc_well = mixpc.strip()
        nc_well = nc.strip()
        
        # Validate well names
        if pc_well not in names:
            raise ValueError(f"Well name {pc_well} is not in the list of provided well names.")
        if mixpc_well not in names:
            raise ValueError(f"Well name {mixpc_well} is not in the list of provided well names.")
        if nc_well not in names:
            raise ValueError(f"Well name {nc_well} is not in the list of provided well names.")

        chosen_well_names = [pc_well, mixpc_well, nc_well]

        # Update label to indicate processing
        label.config(text="Processing file...")

        data = extract_rfu_values(file, chosen_well_names)
        threshold = calibrate_threshold(data, chosen_well_names)

        # Update label with the result
        label.config(text=f"Calibrated threshold: {threshold}")
        event.set()
        print(f'inside the threshold is: ', threshold)
    
    # Run the prompt_for_wells function within the Tkinter main loop
    label.after(100, prompt_for_wells)
    event.wait()  # Wait until the event is set
    return threshold



def get_calibrated_threshold1(label, file, names, event):
    threshold = None
    def prompt_for_wells():
        # Prompt user for PC, mixPC, and NC well names using simpledialog
        pc = simpledialog.askstring("Input", "Enter the name of the Positive Control well", parent=label)
        mixpc = simpledialog.askstring("Input", "Enter the name of the Mixed Positive Control well", parent=label)
        nc = simpledialog.askstring("Input", "Enter the name of the Negative Control well", parent=label)
        
        # Strip any whitespace from the well names
        pc_well = pc.strip()
        mixpc_well = mixpc.strip()
        nc_well = nc.strip()
        
        # Validate well names
        if pc_well not in names:
            raise ValueError(f"Well name {pc_well} is not in the list of provided well names.")
        if mixpc_well not in names:
            raise ValueError(f"Well name {mixpc_well} is not in the list of provided well names.")
        if nc_well not in names:
            raise ValueError(f"Well name {nc_well} is not in the list of provided well names.")

        chosen_well_names = [pc_well, mixpc_well, nc_well]

        # Update label to indicate processing
        label.config(text="Processing file...")

        data = extract_rfu_values(file, chosen_well_names)
        threshold = calibrate_threshold(data, chosen_well_names)
        
        # Update label with the result
        label.config(text=f"Calibrated threshold: {threshold}")
        event.set()
        print(f'inside the threshold is: ', threshold)
        return threshold

    # Run the prompt_for_wells function within the Tkinter main loop
    label.after(100, prompt_for_wells)
# well_names = [item for sublist in default_well_matrix for item in sublist]

def get_calibrated_threshold2(label, file, names):
    # Prompt user for PC, mixPC, and NC well names using simpledialog
    pc = simpledialog.askstring("Input", "Enter the name of the Positive Control well", parent=label)
    mixpc = simpledialog.askstring("Input", "Enter the name of the Mixed Positive Control well", parent=label)
    nc = simpledialog.askstring("Input", "Enter the name of the Negative Control well", parent=label)

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

    chosen_well_names =  [pc, mixpc, nc]

    data = extract_rfu_values(file, chosen_well_names)

    threshold = calibrate_threshold(data, chosen_well_names)

    return threshold

def extract_rfu_values(file_path, chosen_wells):
    with open(file_path, 'r') as file:
        first_line = file.readline().strip()
        skip_first_line = 'sep=' in first_line

    reader = pd.read_csv(file_path, delimiter=',', skiprows=1 if skip_first_line else 0, chunksize=10000)
    # Initialize data structures for the chosen wells
    well_data = {well: [] for well in chosen_wells}
    
    # Read the CSV file in chunks to handle large file sizes
    print("Procseing file..")
    for chunk in reader:
        for index, row in chunk.iterrows():
        # Iterate through the chunk to find rows with the chosen wells
            well = row.iloc[0]
            if well in chosen_wells and 'RFU' in row and pd.notna(row['RFU']):
                well_data[well].append(row['RFU'])
    return well_data


def calibrate_threshold(data, well_names):
    print("Calibrating...")
    
    # Retrieve values from data dictionary
    pc_values = np.array(data[well_names[0]])
    mixpc_values = np.array(data[well_names[1]])
    nc_values = np.array(data[well_names[2]])
    
    # Initial threshold based on positive control
    pc_mean = np.mean(pc_values)
    pc_std = np.std(pc_values)
    initial_threshold = pc_mean + 2 * pc_std

    # print(mixpc_values)
    
    # Refine using mixed positive control
    kmeans = KMeans(n_clusters=2)
    kmeans.fit(mixpc_values.reshape(-1, 1))
    clusters = sorted(kmeans.cluster_centers_.flatten())
    refined_threshold = max(initial_threshold, clusters[1])  # Ensure threshold is not lowered
    
    # Validate with negative control
    nc_false_positives = np.sum(nc_values >= refined_threshold) / len(nc_values)
    
    # Adjust threshold if FPR > 0.01%
    
    while nc_false_positives > 0.0001:
        refined_threshold += 0.01  # Incrementally increase threshold
        nc_false_positives = np.sum(nc_values >= refined_threshold) / len(nc_values)
    
    return refined_threshold
