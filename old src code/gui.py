import tkinter as tk
from tkinter import filedialog, messagebox
import os
import shutil
from handlers import handle_plot1, handle_plot2, handle_plot3, handle_plot4, handle_plot5, handle_exit, select_zip_files
from helper_functions import default_well_matrix, create_well_name_dict

class DPCRAutomationGUI:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("dPCR Automations")

        self.initialization_complete = False  # Flag to track if initialization is complete
        self.wells_data = {}  # Dictionary to store well names

        self.create_widgets()
        self.add_initial_screen()

    def create_widgets(self):
        # Create options frame
        self.options_frame = tk.Frame(self.root, width=200)
        self.options_frame.pack(side="left", fill="y")

        # Create buttons
        self.buttons = []
        for i in range(1, 6):
            button = tk.Button(self.options_frame, text=f"Plot{i}", command=lambda i=i: self.handle_plot_button(i))
            button.pack(pady=10)
            self.buttons.append(button)

        self.exit_button = tk.Button(self.options_frame, text="Exit", command=handle_exit)
        self.exit_button.pack(pady=10)

        # Create screen frame
        self.screen_frame = tk.Frame(self.root)
        self.screen_frame.pack(side="right", fill="both", expand=True)

    def add_initial_screen(self):
        self.clear_screen()
        self.select_zip_button = tk.Button(self.screen_frame, text="Select zipped files", command=self.select_zip_files_handler, font=("Arial", 24))
        self.select_zip_button.pack(expand=True)

    def clear_screen(self):
        for widget in self.screen_frame.winfo_children():
            widget.destroy()

    def select_zip_files_handler(self):
        if select_zip_files(self.root):
            self.add_wells_selection_screen()

    def add_wells_selection_screen(self):
        self.clear_screen()
        self.wells_entries = []
        for row in range(8):
            row_entries = []
            for col in range(3):
                entry = tk.Entry(self.screen_frame)
                entry.grid(row=row, column=col, padx=5, pady=5)
                entry.insert(0, f"{chr(65+row)}{col+1}")
                row_entries.append(entry)
            self.wells_entries.append(row_entries)

        self.apply_button = tk.Button(self.screen_frame, text="Apply", command=self.apply_wells_selection_handler)
        self.apply_button.grid(row=8, columnspan=3, pady=10)

    def apply_wells_selection_handler(self):
        self.wells_data = [[entry.get() for entry in row] for row in self.wells_entries]
        self.initialization_complete = True  # Set flag to indicate initialization is complete
        self.update_button_states()
        self.add_init_complete_screen()

    def add_init_complete_screen(self):
        self.clear_screen()
        self.screen_label = tk.Label(self.screen_frame, text="Initialization Complete\nChoose an Action", font=("Arial", 24))
        self.screen_label.pack(expand=True)
    
    def handle_plot_button(self, plot_number):
        if not self.initialization_complete:
            messagebox.showwarning("Warning", "Please complete the initialization steps first.")
            return

        self.clear_screen()
        self.screen_label = tk.Label(self.screen_frame, text="")
        self.screen_label.pack(expand=True)

        well_names = create_well_name_dict(self.wells_data)

        if plot_number == 1:
            handle_plot1(self.screen_label, well_names)
        elif plot_number == 2:
            handle_plot2(self.screen_label, well_names)
        elif plot_number == 3:
            handle_plot3(self.screen_label, well_names)
        elif plot_number == 4:
            handle_plot4(self.screen_label, well_names)
        elif plot_number == 5:
            handle_plot5(self.screen_label, well_names)
    
    def update_button_states(self):
        for button in self.buttons:
            button.config(state=tk.NORMAL if self.initialization_complete else tk.DISABLED)

    def run(self):
        self.update_button_states()
        self.root.mainloop()


