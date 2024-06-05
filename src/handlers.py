import os
import shutil
from tkinter import filedialog, messagebox
from helper_functions import get_color, default_well_matrix, map_indices
import pandas as pd
import matplotlib.pyplot as plt
import plotly.graph_objects as go
import threading
import warnings
 
# Suppress the specific UserWarning from Matplotlib
warnings.filterwarnings("ignore", message=".*Starting a Matplotlib GUI outside of the main thread will likely fail.*")


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

def plot_data1_thread(label, probe_file_path, data):
    try:
        if plot_data1(label, probe_file_path, data):
            label.config(text="Finished plotting successfully.")
            return True
        else:
            label.config(text="Error plotting.")
            return False
    except Exception as e:
        label.config(text=f"Error plotting: {e}")
        return False
    
def handle_plot1(label, data):
    probe_file_path = filedialog.askopenfilename(initialdir='unzipped_contents', title="Select Probe File", filetypes=[("All files", "*.*")])
    if not probe_file_path:
        messagebox.showerror("Error", "No file selected")
        return
    label.config(text=f"Selected probe file: {get_color(probe_file_path)}")
    label.config(text="Processing 1D plots for all wells...")
    # Create and start a new thread for plot_data
    thread = threading.Thread(target=plot_data1_thread, args=(label, probe_file_path, data))
    thread.start()

def plot_data2_thread(label, probe_file_path1, probe_file_path2, data):
    try:
        if plot_data2(label, probe_file_path1, probe_file_path2, data):
            label.config(text="Finished plotting 2D successfully")
            return True
        else:
            label.config(text="Error plotting.")
            return False
    except Exception as e:
        label.config(text=f"Error plotting: {e}")
        return False

def handle_plot2(label, data):
    probe_file_path1 = filedialog.askopenfilename(initialdir='unzipped_contents', title="Select First Probe File", filetypes=[("All files", "*.*")])
    if not probe_file_path1:
        messagebox.showerror("Error", "No first file selected")
        return

    probe_file_path2 = filedialog.askopenfilename(initialdir='unzipped_contents', title="Select Second Probe File", filetypes=[("All files", "*.*")])
    if not probe_file_path2:
        messagebox.showerror("Error", "No second file selected")
        return

    label.config(text=f"Selected probe files: {get_color(probe_file_path1)}, {get_color(probe_file_path2)}")
    label.config(text="Processing 2D plots for all wells...")
    # Create and start a new thread for plot_data2_thread
    thread = threading.Thread(target=plot_data2_thread, args=(label, probe_file_path1, probe_file_path2, data))
    thread.start()

def plot_data3_thread(label, probe_file_path1, probe_file_path2, probe_file_path3, data):
    try:
        if plot_data3(label, probe_file_path1, probe_file_path2, probe_file_path3, data):
            label.config(text="Finished plotting 3D successfully")
            return True
        else:
            label.config(text="Error plotting.")
            return False
    except Exception as e:
        label.config(text=f"Error plotting: {e}")
        return False
    
def handle_plot3(label, data):
    probe_file_path1 = filedialog.askopenfilename(initialdir='unzipped_contents', title="Select First Probe File", filetypes=[("All files", "*.*")])
    if not probe_file_path1:
        messagebox.showerror("Error", "No first file selected")
        return

    probe_file_path2 = filedialog.askopenfilename(initialdir='unzipped_contents', title="Select Second Probe File", filetypes=[("All files", "*.*")])
    if not probe_file_path2:
        messagebox.showerror("Error", "No second file selected")
        return
    
    probe_file_path3 = filedialog.askopenfilename(initialdir='unzipped_contents', title="Select Third Probe File", filetypes=[("All files", "*.*")])
    if not probe_file_path3:
        messagebox.showerror("Error", "No third file selected")
        return

    label.config(text=f"Selected probe files: {get_color(probe_file_path1)}, {get_color(probe_file_path2)}, {get_color(probe_file_path3)}")
    label.config(text="Processing 3D plots for all wells...")
    # Create and start a new thread for plot_data2_thread
    thread = threading.Thread(target=plot_data3_thread, args=(label, probe_file_path1, probe_file_path2, probe_file_path3, data))
    thread.start()

def handle_plot4(label, data):
    label.config(text="Plot4 functionality to be added here.")

def handle_plot5(label, data):
    label.config(text="Plot5 functionality to be added here.")

def handle_exit():
    exit()

def plot_data1(label, file_path, well_names):
    # label.config(text="Processing 1D plots for all wells.")
    with open(file_path, 'r') as file:
        first_line = file.readline().strip()
        skip_first_line = 'sep=' in first_line

    reader = pd.read_csv(file_path, delimiter=',', skiprows=1 if skip_first_line else 0, chunksize=10000)
    output_dir = f"1D_plots_{get_color(file_path)}"
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


def plot_data2(label, file_path1, file_path2, well_names):
    
    def read_file(file_path):
        with open(file_path, 'r') as file:
            first_line = file.readline().strip()
            skip_first_line = 'sep=' in first_line
        
        reader = pd.read_csv(file_path, delimiter=',', skiprows=1 if skip_first_line else 0, chunksize=10000)
        return reader
    
    reader1 = read_file(file_path1)
    reader2 = read_file(file_path2)
    probe1 = get_color(file_path1)
    probe2 = get_color(file_path2)
    
    output_dir = f"2D_plots_{probe1}_{probe2}"
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    current_well = None
    rfus1_above = []
    rfus2_above = []
    rfus1_below = []
    rfus2_below = []
    rfus1_above_below = []
    rfus2_above_below = []
    rfus1_below_above = []
    rfus2_below_above = []
    ab_ab = 0
    ab_bl = 0
    bl_ab = 0
    bl_bl = 0
    invalid_x = 0
    invalid_y = 0
    threshold1 = None
    threshold2 = None
    plot_count = 0


    def plot_2d_scatter(well, threshold1, threshold2, output_dir, plot_count):
        plt.figure()
        plt.scatter(rfus1_above, rfus2_above, color='red', alpha=0.8)
        plt.scatter(rfus1_above_below, rfus2_above_below, color=probe1[0], alpha=0.5)
        plt.scatter(rfus1_below_above, rfus2_below_above, color=probe2[0], alpha=0.5)
        plt.scatter(rfus1_below, rfus2_below, color='gray', alpha=0.3)
        # \nInvalid {probe1} {invalid_x}\nInvalid {probe2} {invalid_y}
        plt.axhline(y=threshold2, color=probe2[0], linestyle='--', linewidth=1)
        plt.axvline(x=threshold1, color=probe1[0], linestyle='--', linewidth=1)
        plt.xlabel(f'{probe1} Probe RFU')
        plt.ylabel(f'{probe2} Probe RFU')
        plt.title(f'{probe1} vs {probe2} 2D Scatter Plot for Well {well}')

        legend_labels = [
            f'+ {probe1} + {probe2} | {ab_ab}',
            f'+ {probe1}, - {probe2} | {ab_bl}',
            f'- {probe1}, + {probe2} | {bl_ab}',
            f'- {probe1}, - {probe2} | {bl_bl}',
            f'Invalid {probe1} | {invalid_x}',
            f'Invalid {probe2} | {invalid_y}'
        ]

        colors = ['red', probe1[0], probe2[0], 'gray', 'white', 'white']

        for label, color in zip(legend_labels, colors):
            plt.scatter([], [], color=color, label=label)
        plt.legend()
        plt.savefig(os.path.join(output_dir, f'{probe1}_{probe2}_plot_{plot_count}_{well}.png'))
        plt.close()
    

    for chunk1, chunk2 in zip(reader1, reader2):
        for index, (row1, row2) in enumerate(zip(chunk1.iterrows(), chunk2.iterrows())):
            row1 = row1[1]  # Unpack the actual row data from the tuple
            row2 = row2[1]  # Unpack the actual row data from the tuple

            if current_well is None or row1['Well'] != current_well:
                if rfus1_above or rfus1_below or rfus1_above_below or rfus1_below_above:
                    well_name = well_names.get(current_well, current_well)  # Get well name from well_names dict
                    plot_2d_scatter(well_name, threshold1, threshold2, output_dir, plot_count)
                    rfus1_above = []
                    rfus2_above = []
                    rfus1_below = []
                    rfus2_below = []
                    rfus1_above_below = []
                    rfus2_above_below = []
                    rfus1_below_above = []
                    rfus2_below_above = []
                    invalid_x = invalid_y = ab_ab = ab_bl = bl_ab = bl_bl = 0
                    plot_count += 1
                current_well = row1['Well']
                threshold1 = row1['Threshold']
                threshold2 = row2['Threshold']
                
            if 'RFU' in row1 and pd.notna(row1['RFU']) and 'RFU' in row2 and pd.notna(row2['RFU']):
                if row1['RFU'] > threshold1 and row2['RFU'] > threshold2:
                    rfus1_above.append(row1['RFU'])
                    rfus2_above.append(row2['RFU'])
                    ab_ab += 1
                elif row1['RFU'] > threshold1 and row2['RFU'] <= threshold2:
                    rfus1_above_below.append(row1['RFU'])
                    rfus2_above_below.append(row2['RFU'])
                    ab_bl += 1
                elif row1['RFU'] <= threshold1 and row2['RFU'] > threshold2:
                    rfus1_below_above.append(row1['RFU'])
                    rfus2_below_above.append(row2['RFU'])
                    bl_ab += 1
                else:
                    rfus1_below.append(row1['RFU'])
                    rfus2_below.append(row2['RFU'])
                    bl_bl += 1
            elif 'RFU' in row1 and not pd.notna(row1['RFU']):
                invalid_x += 1
            elif 'RFU' in row2 and not pd.notna(row2['RFU']):
                invalid_y += 1

    # Handle the last set of RFUs collected
    if rfus1_above or rfus1_below or rfus1_above_below or rfus1_below_above:
        well_name = well_names.get(current_well, current_well)  # Get well name from well_names dict
        plot_2d_scatter(well_name, threshold1, threshold2, output_dir, plot_count)
    return True

def plot_data3(label, file_path1, file_path2, file_path3, well_names):
    
    def read_file(file_path):
        with open(file_path, 'r') as file:
            first_line = file.readline().strip()
            skip_first_line = 'sep=' in first_line
        
        reader = pd.read_csv(file_path, delimiter=',', skiprows=1 if skip_first_line else 0, chunksize=10000)
        return reader
    
    reader1 = read_file(file_path1)
    reader2 = read_file(file_path2)
    reader3 = read_file(file_path3)
    probe1 = get_color(file_path1)
    probe2 = get_color(file_path2)
    probe3 = get_color(file_path3)
    
    output_dir = f"3D_plots_{probe1}_{probe2}_{probe3}"
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    current_well = None
    rfus1_all = []
    rfus2_all = []
    rfus3_all = []
    rfus1_positive = []
    rfus2_positive = []
    rfus3_positive = []
    positive_count = 0
    threshold1 = None
    threshold2 = None
    threshold3 = None
    plot_count = 0

    def plot_3d_scatter(well, threshold1, threshold2, threshold3, output_dir, plot_count):
        fig = go.Figure()
        
        # Plot all valid samples in gray
        fig.add_trace(go.Scatter3d(
            x=rfus1_all, y=rfus2_all, z=rfus3_all, mode='markers',
            marker=dict(size=5, color='gray', opacity=0.5),
            name=f'All Valid Samples'
        ))

        # Plot positive samples in red
        fig.add_trace(go.Scatter3d(
            x=rfus1_positive, y=rfus2_positive, z=rfus3_positive, mode='markers',
            marker=dict(size=5, color='red', opacity=0.8),
            name=f'+ {probe1} + {probe2} + {probe3} | {positive_count}'
        ))

        # Add threshold lines
        fig.add_trace(go.Scatter3d(
            x=[threshold1, threshold1], y=[min(rfus2_all), max(rfus2_all)], z=[min(rfus3_all), max(rfus3_all)],
            mode='lines', line=dict(color=probe1, width=2), name=f'Threshold {probe1}'
        ))

        fig.add_trace(go.Scatter3d(
            x=[min(rfus1_all), max(rfus1_all)], y=[threshold2, threshold2], z=[min(rfus3_all), max(rfus3_all)],
            mode='lines', line=dict(color=probe2, width=2), name=f'Threshold {probe2}'
        ))

        fig.add_trace(go.Scatter3d(
            x=[min(rfus1_all), max(rfus1_all)], y=[min(rfus2_all), max(rfus2_all)], z=[threshold3, threshold3],
            mode='lines', line=dict(color=probe3, width=2), name=f'Threshold {probe3}'
        ))

        fig.update_layout(
            scene=dict(
                xaxis_title=f'{probe1} Probe RFU',
                yaxis_title=f'{probe2} Probe RFU',
                zaxis_title=f'{probe3} Probe RFU'
            ),
            title=f'{probe1} vs {probe2} vs {probe3} 3D Scatter Plot for Well {well}'
        )
        
        fig.write_html(os.path.join(output_dir, f'{probe1}_{probe2}_{probe3}_plot_{plot_count}_{well}.html'))
        
    for chunk1, chunk2, chunk3 in zip(reader1, reader2, reader3):
        for index, (row1, row2, row3) in enumerate(zip(chunk1.iterrows(), chunk2.iterrows(), chunk3.iterrows())):
            row1 = row1[1]  # Unpack the actual row data from the tuple
            row2 = row2[1]  # Unpack the actual row data from the tuple
            row3 = row3[1]  # Unpack the actual row data from the tuple

            if current_well is None or row1['Well'] != current_well:
                if rfus1_all:
                    well_name = well_names.get(current_well, current_well)  # Get well name from well_names dict
                    plot_3d_scatter(well_name, threshold1, threshold2, threshold3, output_dir, plot_count)
                    rfus1_all = []
                    rfus2_all = []
                    rfus3_all = []
                    rfus1_positive = []
                    rfus2_positive = []
                    rfus3_positive = []
                    positive_count = 0
                    plot_count += 1
                current_well = row1['Well']
                threshold1 = row1['Threshold']
                threshold2 = row2['Threshold']
                threshold3 = row3['Threshold']
                
            if 'RFU' in row1 and pd.notna(row1['RFU']) and 'RFU' in row2 and pd.notna(row2['RFU']) and 'RFU' in row3 and pd.notna(row3['RFU']):
                rfus1_all.append(row1['RFU'])
                rfus2_all.append(row2['RFU'])
                rfus3_all.append(row3['RFU'])
                if row1['RFU'] > threshold1 and row2['RFU'] > threshold2 and row3['RFU'] > threshold3:
                    rfus1_positive.append(row1['RFU'])
                    rfus2_positive.append(row2['RFU'])
                    rfus3_positive.append(row3['RFU'])
                    positive_count += 1

    # Handle the last set of RFUs collected
    if rfus1_all:
        well_name = well_names.get(current_well, current_well)  # Get well name from well_names dict
        plot_3d_scatter(well_name, threshold1, threshold2, threshold3, output_dir, plot_count)
    return True