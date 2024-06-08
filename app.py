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

# Function to add a new order
def add_order():
#    Adds a new order to the Excel file.
#    This function prompts the user to enter the details of the order, including the order ID, product name, price, quantity, customer name, phone number, and email. The function then calculates the total amount of the order by multiplying the price and quantity. The current date and time is also recorded.
#    The function appends the order details to the 'orders_3.xlsx' Excel file. The file is saved after adding the order.
#    This function does not take any parameters.
#    This function does not return any value.

    order_id = input("Enter Order ID: ")
    product_name = input("Enter Product Name: ")

    while True:
        try:
            price = float(input("Enter Price: "))
            if price <= 0:
                raise ValueError("Price must be a positive number.")
            break  # Exit the loop if input is valid
        except ValueError as e:
            print(f"Invalid input: {e}. Please enter a valid positive number.")

    while True:
        try:
            quantity = int(input("Enter Quantity: "))
            if quantity <= 0:
                raise ValueError("Quantity must be a positive integer.")
            break
        except ValueError as e:
            print(f"Invalid input: {e}. Please enter a valid positive integer.")

    total_amount = price * quantity
    customer_name = input("Enter Customer Name: ")
    phone_number = input("Enter Phone Number: ")
    email = input("Enter Email: ")
    date_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    # writing the data into excel file under the column heads
    sheet.append([order_id, product_name, price, quantity, total_amount, customer_name, phone_number, email, date_time])
    workbook.save(file_path)
    print("Order added successfully!"'\n')

'''
____________________________________________________________________________________________

'''

