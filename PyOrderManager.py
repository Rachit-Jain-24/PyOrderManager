import streamlit as st
import pandas as pd
from mysql.connector import connect, Error # type: ignore
from datetime import datetime
import plotly.express as px # type: ignore
import os
import openpyxl
from openpyxl import Workbook
    
# Initialize session state variables
if 'database_names' not in st.session_state:
    st.session_state['database_names'] = []
if 'excel_file_names' not in st.session_state:
    st.session_state['excel_file_names'] = []

# Database connection function
def get_database_connection():
    try:
        connection = connect(
            host="localhost",
            user="root",
            password="rachit2999",
            database=""  # Leave this empty as we'll create/select the database later
        )
        return connection
    except Error as e:
        st.error(f"Error connecting to MySQL: {e}")
        return None

# Function to create database if it doesn't exist
def create_database_if_not_exists(connection, database_name):
    try:
        cursor = connection.cursor()
        cursor.execute(f"CREATE DATABASE IF NOT EXISTS {database_name}")
        cursor.close()
        if database_name not in st.session_state['database_names']:
            st.session_state['database_names'].append(database_name)
        st.success(f"Database '{database_name}' created successfully!")
    except Error as e:
        st.error(f"Error creating database: {e}")

# Function to create order table
def create_order_table(connection, table_name):
    try:
        cursor = connection.cursor()
        
        create_table_query = f"""
        CREATE TABLE IF NOT EXISTS {table_name} (
            order_id VARCHAR(255) PRIMARY KEY,
            product_name VARCHAR(255),
            category VARCHAR(255),
            subcategory VARCHAR(255),
            price FLOAT,
            quantity INT,
            total_amount FLOAT,
            customer_name VARCHAR(255),
            phone_number VARCHAR(255),
            email VARCHAR(255),
            profit FLOAT,
            date_time DATETIME,
            payment_mode VARCHAR(255),
            payment_status VARCHAR(255),
            discount FLOAT,
            tax FLOAT,
            net_total FLOAT,
            location VARCHAR(255)
        )
        """
        
        cursor.execute(create_table_query)
        connection.commit()
        
        st.success(f"Table '{table_name}' created successfully!")
        
        cursor.close()
    except Error as e:
        st.error(f"Error creating table: {e}")

# Function to check if order ID exists
def is_order_id_exists(cursor, table_name, order_id):
    cursor.execute(f"SELECT COUNT(*) FROM {table_name} WHERE order_id = %s", (order_id,))
    count = cursor.fetchone()[0]
    return count > 0

def save_to_excel(data, file_name):
    try:
        if not file_name.endswith('.xlsx'):
            file_name += '.xlsx'
        
        if os.path.exists(file_name):
            workbook = openpyxl.load_workbook(file_name)
            sheet = workbook.active
        else:
            workbook = Workbook()
            sheet = workbook.active
            headers = ["Order ID", "Product Name", "Category", "Subcategory", "Price", "Quantity",
                       "Total Amount", "Customer Name", "Phone Number", "Email", "Profit", "Date Time",
                       "Payment Mode", "Payment Status", "Discount", "Tax", "Net Total", "Location"]
            sheet.append(headers)
        
        sheet.append(data)
        
        for col in sheet.columns:
            max_length = 0
            column = col[0].column_letter
            for cell in col:
                try:
                    if len(str(cell.value)) > max_length:
                        max_length = len(cell.value)
                except:
                    pass
            adjusted_width = (max_length + 2)
            sheet.column_dimensions[column].width = adjusted_width
        
        workbook.save(file_name)
        if file_name not in st.session_state['excel_file_names']:
            st.session_state['excel_file_names'].append(file_name)
        return True
    except Exception as e:
        st.error(f"Error saving to Excel: {e}")
        return False

# Function to add a new order
def add_order(connection, table_name, excel_file_name):
    st.subheader("Add New Order")
    
    order_id = st.text_input("Order ID")
    if order_id:
        cursor = connection.cursor()
        if is_order_id_exists(cursor, table_name, order_id):
            st.error("Order ID already exists. Please enter a different Order ID.")
            return

    product_name = st.text_input("Product Name")
    category = st.text_input("Category")
    subcategory = st.text_input("Subcategory")
    price = st.number_input("Price", min_value=0.01, step=0.01)
    quantity = st.number_input("Quantity", min_value=1, step=1)
    
    total_amount = price * quantity
    profit = total_amount

    customer_name = st.text_input("Customer Name")
    phone_number = st.text_input("Phone Number")
    email = st.text_input("Email")
    date_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    payment_mode = st.selectbox("Payment Mode", ["Cash", "Credit Card", "Debit Card", "Online Transfer"])
    payment_status = st.selectbox("Payment Status", ["Paid", "Pending", "Failed"])
    discount = st.number_input("Discount", min_value=0.0, step=0.01)
    tax = st.number_input("Tax", min_value=0.0, step=0.01)
    net_total = total_amount - discount + tax
    location = st.text_input("Region/Location")

    if st.button("Add Order"):
        cursor = connection.cursor()
        try:
            # Prepare data for both database and Excel
            values = (order_id, product_name, category, subcategory, price, quantity,
                      total_amount, customer_name, phone_number, email, profit, date_time, 
                      payment_mode, payment_status, discount, tax, net_total, location)

            # Insert into database
            query = f"""
            INSERT INTO {table_name} (order_id, product_name, category, subcategory, price, quantity,
                                total_amount, customer_name, phone_number, email, profit, date_time, 
                                payment_mode, payment_status, discount, tax, net_total, location)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            """
            cursor.execute(query, values)

            # Save to Excel
            save_to_excel(values, excel_file_name)

            # Commit the database transaction
            connection.commit()

            st.success("Order added successfully to both database and Excel file!")
        except Error as e:
            connection.rollback()  # Rollback the database transaction if an error occurs
            st.error(f"Error: {e}")
        finally:
            cursor.close()

# Function to update an existing order
def update_order(connection, table_name):
    st.subheader("Update Existing Order")
    
    search_option = st.radio("Search by:", ("Order ID", "Customer Name"))
    
    if search_option == "Order ID":
        order_id = st.text_input("Enter the Order ID to update")
        if order_id:
            cursor = connection.cursor()
            cursor.execute(f"SELECT * FROM {table_name} WHERE order_id = %s", (order_id,))
            result = cursor.fetchone()
            if result:
                st.write("Current Order Details:", result)
                
                new_product_name = st.text_input("New Product Name", value=result[1])
                new_category = st.text_input("New Category", value=result[2])
                new_subcategory = st.text_input("New Subcategory", value=result[3])
                new_price = st.number_input("New Price", value=float(result[4]), min_value=0.01, step=0.01)
                new_quantity = st.number_input("New Quantity", value=int(result[5]), min_value=1, step=1)
                new_customer_name = st.text_input("New Customer Name", value=result[7])
                new_phone_number = st.text_input("New Phone Number", value=result[8])
                new_email = st.text_input("New Email", value=result[9])
                new_payment_mode = st.selectbox("New Payment Mode", ["Cash", "Credit Card", "Debit Card", "Online Transfer"], index=["Cash", "Credit Card", "Debit Card", "Online Transfer"].index(result[12]))
                new_payment_status = st.selectbox("New Payment Status", ["Paid", "Pending", "Failed"], index=["Paid", "Pending", "Failed"].index(result[13]))
                new_discount = st.number_input("New Discount", value=float(result[14]), min_value=0.0, step=0.01)
                new_tax = st.number_input("New Tax", value=float(result[15]), min_value=0.0, step=0.01)
                new_location = st.text_input("New Region/Location", value=result[17])

                if st.button("Update Order"):
                    try:
                        new_total_amount = new_price * new_quantity
                        new_profit = new_total_amount
                        new_net_total = new_total_amount - new_discount + new_tax
                        new_date_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

                        cursor.execute(f"""
                            UPDATE {table_name}
                            SET product_name = %s, category = %s, subcategory = %s, price = %s, quantity = %s,
                                total_amount = %s, customer_name = %s, phone_number = %s, email = %s, profit = %s,
                                date_time = %s, payment_mode = %s, payment_status = %s, discount = %s, tax = %s,
                                net_total = %s, location = %s
                            WHERE order_id = %s
                        """, (new_product_name, new_category, new_subcategory, new_price, new_quantity, new_total_amount,
                              new_customer_name, new_phone_number, new_email, new_profit, new_date_time, new_payment_mode,
                              new_payment_status, new_discount, new_tax, new_net_total, new_location, order_id))
                        
                        connection.commit()
                        
                        st.success("Order updated successfully!")
                    except Error as e:
                        connection.rollback()
                        st.error(f"Error updating order: {e}")
                    finally:
                        cursor.close()
            else:
                st.error("Order ID not found.")
    
    if search_option == "Customer Name":
        customer_name = st.text_input("Enter the Customer Name to search for")
        if customer_name:
            cursor = connection.cursor()
            cursor.execute(f"SELECT * FROM {table_name} WHERE customer_name LIKE %s", ('%' + customer_name + '%',))
            results = cursor.fetchall()
            if results:
                st.write("Matching Orders:")
                for result in results:
                    st.write(result)
            else:
                st.error("No orders found for the given customer name.")

# Function to delete an order
def delete_order(connection, table_name):
    st.subheader("Delete Order")
    
    search_option = st.radio("Search by:", ("Order ID", "Customer Name"))
    
    if search_option == "Order ID":
        order_id = st.text_input("Enter the Order ID to delete")
        if order_id and st.button("Delete Order"):
            cursor = connection.cursor()
            try:
                if is_order_id_exists(cursor, table_name, order_id):
                    cursor.execute(f"DELETE FROM {table_name} WHERE order_id = %s", (order_id,))
                    connection.commit()
                    st.success(f"Order with ID {order_id} deleted successfully!")
                else:
                    st.error("Order ID not found.")
            except Error as e:
                connection.rollback()
                st.error(f"Error deleting order: {e}")
            finally:
                cursor.close()
    
    if search_option == "Customer Name":
        customer_name = st.text_input("Enter the Customer Name to search for")
        if customer_name and st.button("Delete Orders"):
            cursor = connection.cursor()
            try:
                cursor.execute(f"SELECT order_id FROM {table_name} WHERE customer_name LIKE %s", ('%' + customer_name + '%',))
                results = cursor.fetchall()
                if results:
                    for result in results:
                        cursor.execute(f"DELETE FROM {table_name} WHERE order_id = %s", (result[0],))
                    connection.commit()
                    st.success(f"Orders for customer {customer_name} deleted successfully!")
                else:
                    st.error("No orders found for the given customer name.")
            except Error as e:
                connection.rollback()
                st.error(f"Error deleting orders: {e}")
            finally:
                cursor.close()

# Function to display orders
def display_orders(connection, table_name):
    st.subheader("All Orders")
    cursor = connection.cursor()
    cursor.execute(f"SELECT * FROM {table_name}")
    orders = cursor.fetchall()
    df = pd.DataFrame(orders, columns=["Order ID", "Product Name", "Category", "Subcategory", "Price", "Quantity",
                                       "Total Amount", "Customer Name", "Phone Number", "Email", "Profit", "Date Time",
                                       "Payment Mode", "Payment Status", "Discount", "Tax", "Net Total", "Location"])
    st.dataframe(df)
    cursor.close()
    
    st.subheader("Order Analysis")
    
    st.write("Category-wise Sales")
    category_sales = df.groupby('Category')['Total Amount'].sum().reset_index()
    fig = px.bar(category_sales, x='Category', y='Total Amount', title='Category-wise Sales')
    st.plotly_chart(fig)
    
    st.write("Payment Mode Distribution")
    payment_mode_dist = df['Payment Mode'].value_counts().reset_index()
    payment_mode_dist.columns = ['Payment Mode', 'Count']
    fig2 = px.pie(payment_mode_dist, values='Count', names='Payment Mode', title='Payment Mode Distribution')
    st.plotly_chart(fig2)

    st.write("Date-wise Sales")
    df['Date'] = df['Date Time'].apply(lambda x: x.date())
    date_sales = df.groupby('Date')['Total Amount'].sum().reset_index()
    fig3 = px.line(date_sales, x='Date', y='Total Amount', title='Date-wise Sales')
    st.plotly_chart(fig3)

# Streamlit app main function
def main():
    st.set_page_config(page_title="Ledger Management system", page_icon="📒", layout="centered")
    st.title("Order Management System")

    # Database selection/creation
    st.sidebar.subheader("Database Selection/Creation")
    database_name = st.sidebar.text_input("Enter database name to create/select")

    connection = get_database_connection()
    if connection:
        if database_name:
            create_database_if_not_exists(connection, database_name)
            st.sidebar.write(f"Selected Database: {database_name}")
        else:
            if st.session_state['database_names']:
                selected_database = st.sidebar.selectbox("Select a database", st.session_state['database_names'])
                if selected_database:
                    database_name = selected_database
                    st.sidebar.write(f"Selected Database: {database_name}")
            else:
                st.sidebar.write("No databases available. Please create a new database.")
        connection.database = database_name  # Set the database

        # Table selection/creation
        st.sidebar.subheader("Table Selection/Creation")
        table_name = st.sidebar.text_input("Enter table name to create/select")
        if table_name:
            create_order_table(connection, table_name)
            st.sidebar.write(f"Selected Table: {table_name}")
        else:
            st.sidebar.write("Please enter a table name.")

        # Excel file selection/creation
        st.sidebar.subheader("Excel File Selection/Creation")
        excel_file_name = st.sidebar.text_input("Enter Excel file name to create/select")

        if excel_file_name:
            if excel_file_name not in st.session_state['excel_file_names']:
                save_to_excel([], excel_file_name)
            st.sidebar.write(f"Selected Excel File: {excel_file_name}")
        else:
            if st.session_state['excel_file_names']:
                selected_excel_file = st.sidebar.selectbox("Select an Excel file", st.session_state['excel_file_names'])
                if selected_excel_file:
                    excel_file_name = selected_excel_file
                    st.sidebar.write(f"Selected Excel File: {excel_file_name}")
            else:
                st.sidebar.write("No Excel files available. Please create a new Excel file.")

        # Main functionality
        option = st.selectbox("Choose an action", ["Add Order", "Update Order", "Delete Order", "Display Orders"])
        
        if option == "Add Order":
            add_order(connection, table_name, excel_file_name)
        elif option == "Update Order":
            update_order(connection, table_name)
        elif option == "Delete Order":
            delete_order(connection, table_name)
        elif option == "Display Orders":
            display_orders(connection, table_name)

        connection.close()

if __name__ == "__main__":
    main()
