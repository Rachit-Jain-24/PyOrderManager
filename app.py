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

file_path=str(input("enter the file name you want to open or create as a new file: ")+".xlsx")

# Check if the Excel file exists
if os.path.isfile(file_path):
    workbook = load_workbook(file_path)
    sheet = workbook.active
else:
    # Create a new Excel workbook
    workbook = Workbook()
    sheet = workbook.active

    # Define column headers
    sheet['A1'] = 'Order ID'
    sheet['B1'] = 'Product Name'
    sheet['C1'] = 'Price'
    sheet['D1'] = 'Quantity'
    sheet['E1'] = 'Total Amount'
    sheet['F1'] = 'Customer Name'
    sheet['G1'] = 'Phone Number'
    sheet['H1'] = 'Email'
    sheet['I1'] = 'Order Date & Time'

'''
____________________________________________________________________________________________
'''