import os
import shutil
from tkinter import filedialog, messagebox
from helper_functions import get_color, default_well_matrix, map_indices
import pandas as pd
import matplotlib.pyplot as plt
import threading
import warnings
 
# Suppress the specific UserWarning from Matplotlib
warnings.filterwarnings("ignore", message=".*Starting a Matplotlib GUI outside of the main thread will likely fail.*")

def handle_plot2(label, data):
    label.config(text="Plot2 functionality to be added here.")

def handle_plot3(label, data):
    label.config(text="Plot3 functionality to be added here.")

def handle_plot4(label, data):
    label.config(text="Plot4 functionality to be added here.")

def handle_plot5(label, data):
    label.config(text="Plot5 functionality to be added here.")

def handle_exit():
    exit()

def unzip_files(zip_path, extract_to):
    import zipfile
    with zipfile.ZipFile(zip_path, 'r') as zip_ref:
        zip_ref.extractall(extract_to)
    return [os.path.join(extract_to, f) for f in os.listdir(extract_to)]

def select_zip_files(root):
    zip_path = filedialog.askopenfilename(title="Select Zip File", filetypes=[("Zip files", "*.zip")])
    if not zip_path:
        messagebox.showerror("Error", "No file selected")
        return

    extract_to = 'unzipped_contents'
    if os.path.exists(extract_to):
        shutil.rmtree(extract_to)
    os.makedirs(extract_to)

    files = unzip_files(zip_path, extract_to)
    if not files:
        messagebox.showerror("Error", "No files found in the zip")
        shutil.rmtree(extract_to)
        return False

    messagebox.showinfo("Success", f"Extracted files to {extract_to}")
    return True

def plot_data_thread(label, probe_file_path, data):
    # This function will run in a separate thread
    if plot_data(label, probe_file_path, data):
        label.config(text="Finished plotting succesfully.")
        return True
    else:
        label.config(text="Error plotting.")
        return False

def handle_plot1(label, data):
    probe_file_path = filedialog.askopenfilename(initialdir='unzipped_contents', title="Select Probe File", filetypes=[("All files", "*.*")])
    if not probe_file_path:
        messagebox.showerror("Error", "No file selected")
        return
    label.config(text=f"Selected probe file: {get_color(probe_file_path)}")
    label.config(text="Processing 1D plots for all wells...")
    # Create and start a new thread for plot_data
    thread = threading.Thread(target=plot_data_thread, args=(label, probe_file_path, data))
    thread.start()

def plot_data(label, file_path, well_names):
    # label.config(text="Processing 1D plots for all wells.")
    with open(file_path, 'r') as file:
        first_line = file.readline().strip()
        skip_first_line = 'sep=' in first_line

    reader = pd.read_csv(file_path, delimiter=',', skiprows=1 if skip_first_line else 0, chunksize=10000)
    output_dir = f"1D_plot_{get_color(file_path)}"
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    current_well = None
    rfus = []
    threshold = None
    plot_count = 0


    for chunk in reader:
        for index, row in chunk.iterrows():
            if current_well is None or row['Well'] != current_well:
                if rfus:
                    well_name = well_names.get(current_well, current_well)  # Get well name from well_names dict
                    if threshold is None and 'Threshold' in chunk.columns:
                        threshold = row['Threshold']
                    # Assign indeces acording to dPCR device logic
                    # x_indices = map_indices(rfus) # -> [0->0],[1->80],[2->160],...
                    x_indices = [(i % 80) + 1 for i in range(len(rfus))] # -> [1-80], [1-80],...
                    # x_indices = [(i // 80) + 1 for i in range(len(rfus))] # -> [0X80], [1X80],...
                    plt.figure(figsize=(10, 6))
                    plt.scatter(x_indices, rfus, alpha=0.5)
                    plt.axhline(y=threshold, color='r', linestyle='-')
                    plt.title(f'{get_color(file_path)} Probe Scatter Plot for Well {well_name}')
                    plt.xlabel('Sample Index')
                    plt.ylabel('RFU')
                    plt.savefig(os.path.join(output_dir, f'{get_color(file_path)}_plot_{plot_count}_{well_name}_.png'))
                    plt.close()
                    rfus = []
                    plot_count += 1
                current_well = row['Well']
                if row['Threshold'] != threshold:
                    threshold = row['Threshold']
                
            if 'RFU' in row and pd.notna(row['RFU']):
                rfus.append(row['RFU'])
    # Handle the last set of RFUs collected
    if rfus:
        # Assign indeces acording to dPCR device logic
        # x_indices = map_indices(rfus) # -> [0->0],[1->80],[2->160],...
        x_indices = [(i % 80) + 1 for i in range(len(rfus))] # -> [0-80], [0-80],...
        # x_indices = [(i // 80) + 1 for i in range(len(rfus))] # -> [0X80], [1X80],...
        plt.figure(figsize=(10, 6))
        plt.scatter(x_indices, rfus, alpha=0.5)
        plt.axhline(y=threshold, color='r', linestyle='-')
        plt.title(f'{get_color(file_path)} Probe Scatter Plot for Well {current_well}')
        plt.xlabel('Sample Index')
        plt.ylabel('RFU')
        well_name = well_names.get(current_well, current_well)  # Get well name from well_names dict
        plt.savefig(os.path.join(output_dir, f'{get_color(file_path)}_plot_{plot_count}_{well_name}.png'))
        plt.close()
    return True
