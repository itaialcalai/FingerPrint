# FingerPrint
# DPCR Automation

## Overview
DPCR Automation is a software tool designed to streamline and automate the process of analyzing digital PCR (dPCR) data. This application provides an easy-to-use graphical user interface (GUI) built with Dash and utilizes various backend scripts to handle data extraction, threshold calibration, and plotting of results in 1D, 2D, and 3D formats. The software supports the uploading of data files, selection of control wells, and generation of visual plots to facilitate comprehensive analysis of dPCR data.

## Features
- **File Upload**: Upload zipped directories containing dPCR data files.
- **Well Initialization**: Specify and initialize well names and control wells (positive, mix positive, and negative).
- **Threshold Calibration**: Automatically calibrate thresholds based on control wells.
- **Plotting**: Generate 1D, 2D, and 3D plots to visualize dPCR data.
- **Interactive GUI**: User-friendly interface for data processing and visualization.

## Installation

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


## License
Itai Alcalai
206071110

