'''
____________________________________________________________________________________________

'''
# Libraries used for Retail Order Manager:

from openpyxl import Workbook, load_workbook
from datetime import datetime
import os.path
import pandas as pd


'''
____________________________________________________________________________________________

'''


print("--------Welcome to PyRetail Manager--------")

# Input file name with error handling
while True:
    file_path = input('\n'"Enter the file name you want to open or create (with .xlsx): ")
    if file_path.endswith(".xlsx"):
        break
    else:
        print("Invalid file name. Please include '.xlsx' extension.")

'''
____________________________________________________________________________________________
'''


# Global variables
workbook = None
sheet = None

# Function to load or create Excel workbook
def load_excel(file_path):
    global workbook, sheet
    try:
        if os.path.isfile(file_path):
            workbook = load_workbook(file_path)
            print(f"Opening {file_path}")
            sheet = workbook.active
        else:
            print("File not found. Creating a new Excel file.")
            create_excel()
            workbook = load_workbook(file_path)
            sheet = workbook.active
    except Exception as e:  # Catch any file-related errors
        print(f"An error occurred while loading or creating the file: {e}")
        return None, None  # Return None on error

    return workbook, sheet

# Function to create a new Excel file
def create_excel():
    global workbook, sheet
    workbook = Workbook()
    sheet = workbook.active
    sheet.title = "Sheet 1"  # Add sheet title (optional)

    # Define column headers
    headers = ['Order ID', 'Product Name', 'Price', 'Quantity', 'Total Amount',
               'Customer Name', 'Phone Number', 'Email', 'Order Date & Time']
    sheet.append(headers)
    try:
        workbook.save(file_path)
        print(f"Excel file '{file_path}' created successfully.")
    except Exception as e:
        print(f"An error occurred while saving the file: {e}")
'''
____________________________________________________________________________________________

'''