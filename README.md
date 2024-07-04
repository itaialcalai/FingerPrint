# FingerPrint
# DPCR Automation

## Overview
DPCR Automation is a software tool designed to streamline and automate the process of analyzing digital PCR (dPCR) data. This application provides an easy-to-use graphical user interface (GUI) built with Dash and utilizes various backend scripts to handle data extraction, threshold calibration, and plotting of results in 1D, 2D, and 3D formats. The software supports the uploading of data files, selection of control wells, and generation of visual plots to facilitate comprehensive analysis of dPCR data.

## Directory Content
- **app**: This directory contains all the current code files necessary for the functioning of the Dash app.
- **old_src**: This directory holds the old drafts of the code files. It serves as a reference for the previous versions and helps in tracking the development history.
- **example_input**: An example input file to demonstrate the expected format and structure of the data files.
- **requirements.txt**: Specifies the Python packages required for running the DPCR Automation software.
- **README**: The documentation file you are currently reading, providing an overview and instructions for the software.
  
## Features
- **File Upload**: Upload zipped directories containing dPCR data files.
- **Well Initialization**: Specify and initialize well names and control wells (positive, mix positive, and negative).
- **Threshold Calibration**: Automatically calibrate thresholds based on control wells.
- **Plotting**: Generate 1D, 2D, and 3D plots to visualize dPCR data.
- **Interactive GUI**: User-friendly interface for data processing and visualization.

## Installation

You will need to launch the software from inside the `app` directory.

An attempt to deploy the software as an executable and redirect output files was made, hence the presence of `plot1_actions_outputdir_change.py` and `pyinstaller.spec`. However, this was not fully developed due to certificate restraints.

### Prerequisites
- Python 3.7 or higher
- Required Python packages:
  - dash
  - dash-bootstrap-components
  - pandas
  - numpy
  - plotly
  - scikit-learn

### Installation Steps
1. Clone the repository:
    ```sh
    git clone https://github.com/yourusername/dpcr-automation.git
    cd dpcr-automation
    ```

2. Install the required packages:
    ```sh
    pip install -r requirements.txt
    ```

## Usage

### Running the Application
To start the DPCR Automation application, run the following command:
```sh
python app.py
```
This will launch the Dash server, and you can access the application by navigating to http://127.0.0.1:8050 in your web browser.
### Application Workflow
1. **Upload Data**:
    - Click on "Select Files" or drag and drop your zipped directory containing dPCR data files into the upload area.
    - The application will extract and list the files from the uploaded zip archive.

2. **Initialize Wells**:
    - Enter well names in the provided fields or use the default ones.
    - Specify control wells for positive, mix positive, and negative controls.
    - Click "Apply" to initialize the wells.

3. **Plot Data**:
    - Choose the type of plot (1D, 2D, or 3D) by clicking the corresponding button.
    - Select the files to be used for plotting.
    - For 1D plots, choose the threshold type (Default or Calibrated).
    - The application will process the data and display the plots.

## Code Explanation

### Directory Structure
- **app.py**: The main entry point of the application. Initializes the Dash app, defines the layout, and registers callbacks.
- **callbacks.py**: Contains the main callback functions to handle file upload, well initialization, and plot selection.
- **plot1_actions.py**: Handles 1D plotting actions, including data extraction and plotting.
- **plot2_actions.py**: Handles 2D plotting actions, including data extraction and plotting.
- **plot3_actions.py**: Handles 3D plotting actions, including data extraction and plotting.
- **threshold_calibration.py**: Contains functions to calibrate thresholds based on control wells using k-means clustering and statistical methods.
- **utils.py**: Utility functions for creating well name dictionaries and extracting color codes from file paths.

### Key Functions
- **create_well_name_dict**: Maps default well names to user-defined well names.
- **get_color**: Extracts a color code from the file path.
- **get_calibrated_threshold**: Calibrates the threshold based on control wells.
- **extract_rfu_values**: Extracts RFU values from data files for specified wells.
- **calibrate_threshold**: Calibrates the threshold using data from control wells.
- **plot_1d_layout**: Generates the layout for 1D plot screen.
- **plot_2d_layout**: Generates the layout for 2D plot screen.
- **plot_3d_layout**: Generates the layout for 3D plot screen.
- **plot_data1, plot_data2, plot_data3**: Processes data and generates 1D, 2D, and 3D plots, respectively.
  
## Threshold Calibration Algorithm
The threshold calibration algorithm in this project is implemented in `threshold_calibration.py`. Here's an explanation of how it works:
The function `get_calibrated_threshold(file, names, ds)` calibrates the threshold based on positive, mixed positive, and negative control wells from a data file.

### Steps:
1. **Extract Control Well Names**: Retrieve the names of the positive, mixed positive, and negative control wells from the provided dictionary (`ds`).
2. **Validate Well Names**: Check if the extracted control well names are valid and exist in the provided well names (`names`).
3. **Extract RFU Values**: Utilize the `extract_rfu_values()` function to extract RFU (Relative Fluorescence Units) values for the chosen control wells from the data file.
4. **Calibrate Threshold**: Use the `calibrate_threshold()` function to calculate an initial threshold based on the mean and standard deviation of RFU values from the positive control well (`pc_values`). Then, refine the threshold using k-means clustering on RFU values from the mixed positive control well (`mixpc_values`). Ensure the threshold is not lower than the highest cluster center identified.
5. **Validate with Negative Control**: Check the false positive rate (FPR) using RFU values from the negative control well (`nc_values`). If the FPR exceeds 0.01%, incrementally increase the threshold until the FPR is within the acceptable range.
6. **Return Calibrated Threshold**: Return the refined threshold value that effectively separates positive and negative indications in the digital PCR data.

This algorithm ensures accurate threshold calibration for digital PCR data analysis, optimizing the separation of positive and negative signals while minimizing false positives.

## Findings of Calibration
After calibration, the following observations were made based on the control wells:
- **Crimson**: 2 positives in Negative Control wells, ~3 RFUs lower than default threshold.
- **Green**: 0 positives in Negative Control wells (much higher than any samples), ~8 higher than default threshold.
- **Yellow**: 1 positive in Negative Control, and ~2 lower than default threshold.
  
These findings suggest further investigation and perhaps fine-tuning of the threshold calibration algorithm to enhance its accuracy and effectiveness in distinguishing between positive and negative signals in digital PCR data.

## License
Itai Alcalai
206071110

