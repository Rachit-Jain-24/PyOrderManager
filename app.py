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