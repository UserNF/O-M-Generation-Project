#!/usr/bin/env python
# coding: utf-8

# In[1]:


import os
import tkinter
import tkinter.messagebox
import watchdog
import pdfplumber
import customtkinter
from tkinter import filedialog
from PyPDF2 import PdfReader, PdfWriter,PdfMerger
import pandas as pd
import nbformat
import nbconvert

customtkinter.set_appearance_mode("Dark")  # Modes: "System" (standard), "Dark", "Light"
customtkinter.set_default_color_theme("blue")  # Themes: "blue" (standard), "green", "dark-blue"

class App(customtkinter.CTk):
    missing_codes = {}
    all_tables = []
    def __init__(self):
        super().__init__()

        # configure window
        self.title("O&M Jumpstart.py")
        self.geometry(f"{1400}x{680}")

        # configure grid layout (4x4)
        self.grid_columnconfigure(1, weight=1)
        self.grid_columnconfigure((0), weight=0)
        self.grid_rowconfigure((0), weight=1)

        # create sidebar frame with widgets
        self.sidebar_frame = customtkinter.CTkFrame(self, width=140, corner_radius=0)
        self.sidebar_frame.grid(row=0, column=0, rowspan=4, sticky="nsew")
        self.sidebar_frame.grid_rowconfigure(4, weight=1)
        self.logo_label = customtkinter.CTkLabel(self.sidebar_frame, text="O&M Generation", font=customtkinter.CTkFont(size=20, weight="bold"))
        self.logo_label.grid(row=0, column=0, padx=20, pady=(20, 10))
        self.sidebar_button_1 = customtkinter.CTkButton(self.sidebar_frame, text="Select Index...", command=self.select_path)
        self.sidebar_button_1.grid(row=1, column=0, padx=20, pady=10)
        self.sidebar_button_2 = customtkinter.CTkButton(self.sidebar_frame, command=self.populate_literaturelayout, text="Literature Dictionary")
        self.sidebar_button_2.grid(row=2, column=0, padx=20, pady=10)
        self.sidebar_button_3 = customtkinter.CTkButton(self.sidebar_frame, command=self.generate_docs, text="Generate")
        self.sidebar_button_3.grid(row=3, column=0, padx=20, pady=10)
        self.sidebar_button_4 = customtkinter.CTkButton(self.sidebar_frame, command=self.sidebar_button_event, text="Credits")
        self.sidebar_button_4.grid(row=4, column=0, padx=20, pady=10, sticky="n")
        self.appearance_mode_label = customtkinter.CTkLabel(self.sidebar_frame, text="Appearance Mode:", anchor="w")
        self.appearance_mode_label.grid(row=5, column=0, padx=20, pady=(10, 0))
        self.appearance_mode_optionemenu = customtkinter.CTkOptionMenu(self.sidebar_frame, values=["Light", "Dark", "System"], command=self.change_appearance_mode_event)
        self.appearance_mode_optionemenu.grid(row=6, column=0, padx=20, pady=(10, 10))
        self.scaling_label = customtkinter.CTkLabel(self.sidebar_frame, text="UI Scaling:", anchor="w")
        self.scaling_label.grid(row=7, column=0, padx=20, pady=(10, 0))
        self.scaling_optionemenu = customtkinter.CTkOptionMenu(self.sidebar_frame, values=["80%", "90%", "100%", "110%", "120%"], command=self.change_scaling_event)
        self.scaling_optionemenu.grid(row=8, column=0, padx=20, pady=(10, 20))

        # Create default text, suggestions, & Help frame
        self.default_label_1 = customtkinter.CTkLabel(self, text="No index selected", font=customtkinter.CTkFont(size=35, weight="bold"))
        self.default_label_1.grid(row=0, column=1, padx=100, pady=(100, 0), sticky="wn")
        self.default_label_2 = customtkinter.CTkLabel(self, text="There is no technical literature index selected. Here are some friendly suggestions for what to do next.", font=customtkinter.CTkFont(size=15))
        self.default_label_2.grid(row=0, column=1, padx=100, pady=(150, 20), sticky="wn")
        self.default_frame = customtkinter.CTkFrame(self, width=750, height=10, corner_radius=20)
        self.default_frame.grid(row=0, column=1, padx=100, pady=(200,250), sticky="wne")

        # Initial tutorial 
        self.default_frame.grid_rowconfigure(4, weight=1)
        self.step_1 = customtkinter.CTkLabel(master=self.default_frame, text="Step 1: Click 'Select Index' to select a technical literature index PDF", font=customtkinter.CTkFont(size=15))
        self.step_1.grid(row=1, column=1, padx=20, pady=5, sticky="w")
        self.step_2 = customtkinter.CTkLabel(master=self.default_frame, text="Step 2: Check selection to make sure everything populated correctly", font=customtkinter.CTkFont(size=15))
        self.step_2.grid(row=2, column=1, padx=20, pady=5, sticky="nswe")
        self.step_3 = customtkinter.CTkLabel(master=self.default_frame, text="Step 3: If everything looks good, click 'Generate' to generate the PDF", font=customtkinter.CTkFont(size=15))
        self.step_3.grid(row=3, column=1, padx=20, pady=5, sticky="nswe")
        
        # set default values
        self.sidebar_button_3.configure(state="disabled")
        self.appearance_mode_optionemenu.set("Dark")
        self.scaling_optionemenu.set("100%")

        # TESTING
        self.populate_literaturelayout()
    
    def select_path(self):
        file_path = filedialog.askopenfilename(
        initialdir = "/",
        title = "Select PDF File",
        filetypes = (("PDF files", "*.pdf"), ("all files", "*.*")))

        # Select file path and populate data fields
        if file_path:
            self.populate_datafields()
            print("Selected file:", file_path)
            # Access the first table and its first column
            # Path to the PDF file
            # Open the PDF and extract tables
            with pdfplumber.open(file_path) as pdf:
              
                for i, page in enumerate(pdf.pages):
                    table = page.extract_table()
                    if table:
                        df = pd.DataFrame(table)
                        self.all_tables.append(df)
                        df.to_csv(f"output_table_page_{i+1}.csv", index=False)
                        print(f"Extracted table from page {i+1} and saved as CSV.")
        else:
            print("No file selected.")

    # Generate missing docs
    def generate_docs(self):
        available_codes = {";eri039844":"08ba32a0771a53b3f23700bc8ba44f65b86c5cda.pdf", "Uiefan;o2":"SH, SJ, SR Series Datasheet.pdf"}
        product_path = 'Product Documents'
        merger = PdfMerger()

        # Optional: Combine all extracted tables into a single CSV file
        if self.all_tables:
            combined_df = pd.concat(self.all_tables, ignore_index=True)
            combined_df.to_csv("output_combined.csv", index=False)
            print("All tables combined and saved as 'output_combined.csv'.")
        else:
            print("No tables found in the PDF.")
        print("button has press functionality")
    
    def populate_datafields(self):
        self.sidebar_button_3.configure(state="normal")
        
        # Clear previous default data
        self.default_frame.destroy()
        self.default_label_1.destroy()
        self.default_label_2.destroy()
        self.grid_columnconfigure(1, weight=1)
        self.grid_columnconfigure((2,3), weight=1)
        self.grid_rowconfigure((0,2,3), weight=1)

        # Create Title
        self.project_label = customtkinter.CTkLabel(self, text="O&M Data", font=customtkinter.CTkFont(size=35, weight="bold"))
        self.project_label.grid(row=0, column=1, padx=20, pady=30, sticky="nw") 

        # Create project name and number
        self.project_label = customtkinter.CTkLabel(self, text="Project Name")
        self.project_label.grid(row=0, column=1, padx=20, pady=(100,0), sticky="nw") 
        self.textbox = customtkinter.CTkTextbox(self, width=700, height=20)
        self.textbox.grid(row=0, column=1, padx=20, pady=(130,0), sticky="nw")

        self.number_label = customtkinter.CTkLabel(self, text="Project Number")
        self.number_label.grid(row=0, column=2, padx=20, pady=(100,0), sticky="nw") 
        self.textbox_2 = customtkinter.CTkTextbox(self, width=700, height=20)
        self.textbox_2.grid(row=0, column=2, padx=20, pady=(130,0), sticky="nw")

    def populate_literaturelayout(self):
        # Clear previous default data
        # configure grid layout (4x4)
        self.grid_columnconfigure(1, weight=1)
        self.grid_columnconfigure((0), weight=0)
        self.grid_rowconfigure((0), weight=1)
        self.default_frame.destroy()
        self.default_label_1.destroy()
        self.default_label_2.destroy()
        
        # Create Title
        self.project_label = customtkinter.CTkLabel(self, text="Technical Literature Data", font=customtkinter.CTkFont(size=35, weight="bold"))
        self.project_label.grid(row=0, column=1, padx=20, pady=(30,0), sticky="nw") 

        #Create Button
        self.sidebar_button_2 = customtkinter.CTkButton(self, text="Add Literature...")
        self.sidebar_button_2.grid(row=0, column=1, padx=20, pady=(85,0), sticky="nw")

        #Create Button
        self.refresh_button = customtkinter.CTkButton(self, text="O&M Preview")
        self.refresh_button.grid(row=0, column=1, padx=170, pady=(85,0), sticky="nw")

        self.sidebar_button_2 = customtkinter.CTkButton(self, command=self.populate_literaturelayout, text="Refresh")
        self.sidebar_button_2.grid(row=0, column=1, padx=320, pady=(85,0), sticky="nw")

        self.CreateGrid()
    
    def CreateGrid(self):
        self.table_frame = customtkinter.CTkFrame(self, corner_radius=10, width=120)
        self.table_frame.grid(row=0, column=1, pady=(135,20), padx=20, sticky="nsew")
        table_frame = self.table_frame

        # Header Nested List
        data = [["Item", "Code", "Literature", "Actions"]]
        
        # Put data from folder in Nest List
        product_path = 'Product Documents'
        index=0
        for filename in os.listdir(product_path):
            file_path = os.path.join(product_path, filename)
            if os.path.isfile(file_path):
                with open(file_path, 'r') as file:
                    index = index+1
                    if(len(filename) > 40):
                        data.append([index, "Product Code", filename.replace(".pdf", "")[:40]+"...", ""])
                    else:
                        data.append([index,"Product Code", filename.replace(".pdf", ""), ""])
                        
        # Add a header or styled sidebar
        row_index = 1
        
        # Populate the table
        for row_index, row in enumerate(data):
            for col_index, value in enumerate(row):
                if row_index % 2 != 0:
                    # Create row that is slightly lighter than other rows
                    cell = customtkinter.CTkLabel(table_frame, text=value, width=120, height=20, font=customtkinter.CTkFont(size=20), fg_color="#3b3b3b", corner_radius=0)
                    cell.grid(row=row_index, column=col_index, padx=0, pady=0, sticky="ew")  # Stretch cell
                    table_frame.grid_columnconfigure(col_index, weight=1)  # Enable column stretching
                    self.create_grid_actions(row_index, row)
                elif row_index == 0:
                    # Create header row
                    cell = customtkinter.CTkLabel(table_frame, text=value, width=120, height=20, corner_radius=20, font=customtkinter.CTkFont(size=20, weight="bold"), text_color="white" if row_index == 0 else None)
                    cell.grid(row=row_index, column=col_index, padx=0, pady=0, sticky="ew")  # Stretch cell
                    table_frame.grid_columnconfigure(col_index, weight=0)  # Enable column stretching
                else:
                    # Create regular row
                    cell = customtkinter.CTkLabel(table_frame, text=value, width=100, height=30, font=customtkinter.CTkFont(size=20), corner_radius=20)
                    cell.grid(row=row_index, column=col_index, padx=5, pady=5)
                    table_frame.grid_columnconfigure(col_index, weight=1)  # Enable column stretching
                    self.create_grid_actions(row_index, row)
        
    def create_grid_actions(self, row_index, row):
        table_frame = self.table_frame
        table_frame.sidebar_button_1 = customtkinter.CTkButton(table_frame, text="Delete", width=40, height=10)
        table_frame.sidebar_button_1.grid(row=row_index, column=len(row)-1, padx=(170,20), pady=10, sticky="we")
        table_frame.sidebar_button_2 = customtkinter.CTkButton(table_frame, text="Edit", width=40, height=10)
        table_frame.sidebar_button_2.grid(row=row_index, column=len(row)-1, padx=(20,170), pady=10, sticky="we")
        
    def open_input_dialog_event(self):
        dialog = customtkinter.CTkInputDialog(text="Type in a number:", title="CTkInputDialog")
        print("CTkInputDialog:", dialog.get_input())

    def change_appearance_mode_event(self, new_appearance_mode: str):
        customtkinter.set_appearance_mode(new_appearance_mode)

    def change_scaling_event(self, new_scaling: str):
        new_scaling_float = int(new_scaling.replace("%", "")) / 100
        customtkinter.set_widget_scaling(new_scaling_float)

    def sidebar_button_event(self):
        print("sidebar_button click")

if __name__ == "__main__":
    app = App()
    app.mainloop()


# In[26]:





# In[ ]:




