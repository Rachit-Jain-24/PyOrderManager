# Importing Libraries 

import streamlit as st
import pandas as pd
import mysql
from mysql.connector import connect, Error # type: ignore
from datetime import datetime
import plotly.express as px # type: ignore
import os
import openpyxl
from openpyxl import Workbook
from reportlab.lib import colors
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph
from reportlab.lib.styles import getSampleStyleSheet

# streamlit==1.29.0
# pandas==2.1.4
# plotly==5.18.0
# openpyxl==3.1.2
# reportlab==4.0.8
# protobuf==4.25.1
# mysql-connector-python==8.2.0


# -------------------------------------------------------------------------------------------------------------------

# Initialize session state variables
if 'database_names' not in st.session_state:
    st.session_state['database_names'] = []
if 'excel_file_names' not in st.session_state:
    st.session_state['excel_file_names'] = []

# -------------------------------------------------------------------------------------------------------------------

# Database connection function
def get_database_connection():
    try:
        connection = connect(
            # Use environment variables or Streamlit secrets for sensitive data
            host=st.secrets["localhost"],
            user=st.secrets["root"],
            password=st.secrets["rachit2999"],
            database=""
        )
        return connection
    except Error as e:
        st.error(f"Error connecting to MySQL: {e}")
        return None
    
# -------------------------------------------------------------------------------------------------------------------


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


# -------------------------------------------------------------------------------------------------------------------


# Function to create order table
def create_order_table(connection, table_name):
    try:
        cursor = connection.cursor()
        
        create_table_query = f"""
        CREATE TABLE IF NOT EXISTS `{table_name}` (
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
    cursor.execute(f"SELECT COUNT(*) FROM `{table_name}` WHERE order_id = %s", (order_id,))
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

    # Fetch available products
    cursor = connection.cursor()
    cursor.execute("SELECT product_id, product_name, category, subcategory, selling_price, quantity_available FROM products")
    products = cursor.fetchall()
    
    if not products:
        st.error("No products available. Please add products to inventory first.")
        return
    
    product_dict = {f"{p[1]} ({p[0]})": p for p in products}
    selected_product = st.selectbox("Select Product", options=list(product_dict.keys()))
    
    if selected_product:
        product = product_dict[selected_product]
        product_id = product[0]
        product_name = product[1]
        category = product[2]
        subcategory = product[3]
        price = product[4]
        available_qty = product[5]
        
        st.write(f"Available Quantity: {available_qty}")
        quantity = st.number_input("Quantity", min_value=1, max_value=available_qty, step=1)
        
        # Calculate total amount and profit
        total_amount = price * quantity
        
        # Calculate actual profit using cost price
        cursor.execute("SELECT cost_price FROM products WHERE product_id = %s", (product_id,))
        cost_price = cursor.fetchone()[0]
        profit = (price - cost_price) * quantity

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
                # Update product inventory
                new_quantity = available_qty - quantity
                cursor.execute("""
                    UPDATE products 
                    SET quantity_available = %s 
                    WHERE product_id = %s
                """, (new_quantity, product_id))

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

                st.success("Order added successfully and inventory updated!")
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
                        
                        # Get cost price from products table
                        cursor.execute("""
                            SELECT cost_price FROM products 
                            WHERE product_name = %s AND category = %s AND subcategory = %s
                        """, (new_product_name, new_category, new_subcategory))
                        cost_price_result = cursor.fetchone()
                        
                        if cost_price_result:
                            cost_price = cost_price_result[0]
                            new_profit = (new_price - cost_price) * new_quantity
                        else:
                            new_profit = 0  # Handle case where product is not found
                        
                        new_date_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                        new_net_total = new_total_amount - new_discount + new_tax

                        cursor.execute(f"""
                            UPDATE `{table_name}`
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

def format_large_number(number):
    """Format large numbers to K, M, B format"""
    if number >= 1_000_000_000:
        return f"₹{number/1_000_000_000:.2f}B"
    elif number >= 1_000_000:
        return f"₹{number/1_000_000:.2f}M"
    elif number >= 1_000:
        return f"₹{number/1_000:.2f}K"
    return f"₹{number:.2f}"

def display_orders(connection, table_name):
    st.subheader("Sales Dashboard")
    
    # Fetch data from the database
    cursor = connection.cursor()
    cursor.execute(f"SELECT * FROM `{table_name}`")
    orders = cursor.fetchall()
    df = pd.DataFrame(orders, columns=["Order ID", "Product Name", "Category", "Subcategory", "Price", "Quantity",
                                     "Total Amount", "Customer Name", "Phone Number", "Email", "Profit", "Date Time",
                                     "Payment Mode", "Payment Status", "Discount", "Tax", "Net Total", "Location"])
    
    # Convert Date Time to datetime
    df['Date Time'] = pd.to_datetime(df['Date Time'])
    df['Date'] = df['Date Time'].dt.date
    df['Month'] = df['Date Time'].dt.strftime('%B %Y')
    df['Day'] = df['Date Time'].dt.strftime('%A')

    # Key Performance Metrics with better formatting
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        total_sales = df['Total Amount'].sum()
        st.metric("Total Sales", format_large_number(total_sales))
    
    with col2:
        total_profit = df['Profit'].sum()
        st.metric("Total Profit", format_large_number(total_profit))
    
    with col3:
        total_orders = len(df)
        st.metric("Total Orders", f"{total_orders:,}")
    
    with col4:
        avg_order_value = df['Total Amount'].mean()
        st.metric("Avg Order Value", format_large_number(avg_order_value))

    # Time-based Analysis with better formatting
    st.subheader("Time-based Analysis")
    
    # Monthly Trends with formatted values
    monthly_sales = df.groupby('Month')[['Total Amount', 'Profit']].sum().reset_index()
    fig_monthly = px.line(monthly_sales, x='Month', y=['Total Amount', 'Profit'],
                         title='Monthly Sales and Profit Trends',
                         labels={'value': 'Amount', 'variable': 'Metric'})
    # Format y-axis labels
    fig_monthly.update_layout(yaxis=dict(tickformat=',.0f'))
    st.plotly_chart(fig_monthly)

    # Daily Analysis
    col1, col2 = st.columns(2)
    
    with col1:
        daily_orders = df['Day'].value_counts()
        fig_daily = px.bar(daily_orders, title='Orders by Day of Week',
                          labels={'value': 'Number of Orders', 'index': 'Day'})
        st.plotly_chart(fig_daily)
    
    with col2:
        hourly_orders = df['Date Time'].dt.hour.value_counts().sort_index()
        fig_hourly = px.bar(hourly_orders, title='Orders by Hour of Day',
                           labels={'value': 'Number of Orders', 'index': 'Hour'})
        st.plotly_chart(fig_hourly)

    # Product Analysis with better formatting
    st.subheader("Product Analysis")
    
    col1, col2 = st.columns(2)
    
    with col1:
        # Top Products by Sales with formatted values
        top_products = df.groupby('Product Name').agg({
            'Total Amount': 'sum',
            'Quantity': 'sum',
            'Profit': 'sum'
        }).sort_values('Total Amount', ascending=False).head(10)
        
        fig_top_products = px.bar(top_products, y='Total Amount',
                                 title='Top 10 Products by Sales',
                                 labels={'Total Amount': 'Sales'})
        fig_top_products.update_layout(yaxis=dict(tickformat=',.0f'))
        st.plotly_chart(fig_top_products)
    
    with col2:
        # Category Performance
        category_performance = df.groupby('Category').agg({
            'Total Amount': 'sum',
            'Profit': 'sum',
            'Order ID': 'count'
        }).reset_index()
        
        fig_category = px.pie(category_performance, values='Total Amount', names='Category',
                            title='Sales Distribution by Category')
        st.plotly_chart(fig_category)

    # Customer Analysis
    st.subheader("Customer Analysis")
    
    col1, col2 = st.columns(2)
    
    with col1:
        # Customer Locations
        location_orders = df['Location'].value_counts()
        fig_locations = px.pie(values=location_orders.values, 
                             names=location_orders.index,
                             title='Orders by Location')
        st.plotly_chart(fig_locations)
    
    with col2:
        # Payment Analysis
        payment_analysis = df.groupby('Payment Mode').agg({
            'Total Amount': 'sum',
            'Order ID': 'count'
        }).reset_index()
        
        fig_payment = px.bar(payment_analysis, x='Payment Mode', y=['Total Amount', 'Order ID'],
                            title='Payment Mode Analysis',
                            labels={'value': 'Amount/Count', 'variable': 'Metric'})
        st.plotly_chart(fig_payment)

    # Profitability Analysis
    st.subheader("Profitability Analysis")
    
    # Calculate profit margins
    df['Profit_Margin'] = (df['Profit'] / df['Total Amount']) * 100
    
    col1, col2 = st.columns(2)
    
    with col1:
        # Profit Margins by Category
        category_margins = df.groupby('Category')['Profit_Margin'].mean().round(2)
        fig_margins = px.bar(category_margins, title='Average Profit Margins by Category',
                            labels={'value': 'Profit Margin (%)'})
        st.plotly_chart(fig_margins)
    
    with col2:
        # Replace scatter plot with Discount Analysis
        discount_analysis = df.groupby('Category').agg({
            'Discount': 'sum',
            'Total Amount': 'sum',
            'Profit': 'sum'
        }).reset_index()
        
        # Calculate discount percentage
        discount_analysis['Discount_Percentage'] = (discount_analysis['Discount'] / discount_analysis['Total Amount'] * 100).round(2)
        discount_analysis['Profit_After_Discount'] = discount_analysis['Profit'] - discount_analysis['Discount']
        
        fig_discount = px.bar(discount_analysis, x='Category', y=['Profit', 'Discount'],
                             title='Profit vs Discount by Category',
                             labels={'value': 'Amount (₹)', 'variable': 'Type'},
                             barmode='group')
        st.plotly_chart(fig_discount)

    # Discount Impact Summary with better formatting
    st.subheader("Discount Impact Summary")
    col1, col2, col3 = st.columns(3)

    with col1:
        total_discount = df['Discount'].sum()
        st.metric("Total Discounts Given", format_large_number(total_discount))

    with col2:
        avg_discount_percent = (df['Discount'].sum() / df['Total Amount'].sum() * 100)
        st.metric("Average Discount %", f"{avg_discount_percent:.1f}%")

    with col3:
        profit_lost_to_discount = (df['Discount'].sum() / df['Profit'].sum() * 100)
        st.metric("Profit Lost to Discounts", f"{profit_lost_to_discount:.1f}%")

    # Add hover data to charts for better detail
    fig_category.update_traces(hovertemplate='Category: %{label}<br>Amount: ₹%{value:,.0f}<extra></extra>')
    fig_payment.update_traces(hovertemplate='%{x}<br>%{y:,.0f}<extra></extra>')
    
    # Format dataframe display
    def format_currency(val):
        if isinstance(val, (int, float)):
            return format_large_number(val)
        return val
    
    # Format currency columns in the detailed data view
    currency_columns = ['Price', 'Total Amount', 'Profit', 'Discount', 'Tax', 'Net Total']
    for col in currency_columns:
        if col in df.columns:
            df[col] = df[col].apply(format_currency)
    
    st.subheader("Detailed Order Data")
    st.dataframe(df)

    # Export Analysis Button
    if st.button("Export Analysis to Excel"):
        try:
            with pd.ExcelWriter(f'sales_analysis_{datetime.now().strftime("%Y%m%d")}.xlsx') as writer:
                df.to_excel(writer, sheet_name='Raw Data', index=False)
                monthly_sales.to_excel(writer, sheet_name='Monthly Trends', index=False)
                top_products.to_excel(writer, sheet_name='Top Products', index=True)
                category_performance.to_excel(writer, sheet_name='Category Analysis', index=False)
            st.success("Analysis exported successfully!")
        except Exception as e:
            st.error(f"Error exporting analysis: {e}")

def manage_product_inventory(connection):
    st.subheader("Product Inventory Management")
    
    # Create products table if not exists with HSN and GST columns
    cursor = connection.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS products (
            product_id VARCHAR(255) PRIMARY KEY,
            product_name VARCHAR(255),
            category VARCHAR(255),
            subcategory VARCHAR(255),
            cost_price FLOAT,
            selling_price FLOAT,
            quantity_available INT,
            reorder_level INT,
            hsn_code VARCHAR(8),
            gst_rate FLOAT
        )
    """)
    connection.commit()
    
    # Add new product form
    with st.expander("Add New Product"):
        product_id = st.text_input("Product ID", key="new_product_id")
        product_name = st.text_input("Product Name", key="new_product_name")
        category = st.text_input("Category", key="new_category")
        subcategory = st.text_input("Subcategory", key="new_subcategory")
        cost_price = st.number_input("Cost Price", min_value=0.01, step=0.01, key="new_cost_price")
        selling_price = st.number_input("Selling Price", min_value=0.01, step=0.01, key="new_selling_price")
        quantity = st.number_input("Initial Quantity", min_value=0, step=1, key="new_quantity")
        reorder_level = st.number_input("Reorder Level", min_value=0, step=1, key="new_reorder_level")
        hsn_code = st.text_input("HSN Code", key="new_hsn_code")
        gst_rate = st.number_input("GST Rate (%)", min_value=0.0, max_value=100.0, step=0.1, key="new_gst_rate")
        
        if st.button("Add Product"):
            try:
                cursor.execute("""
                    INSERT INTO products VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                """, (product_id, product_name, category, subcategory, cost_price, 
                     selling_price, quantity, reorder_level, hsn_code, gst_rate))
                connection.commit()
                st.success("Product added successfully!")
            except Error as e:
                st.error(f"Error adding product: {e}")
    
    # Edit existing products
    with st.expander("Edit Existing Product"):
        # Fetch all products for selection
        cursor.execute("SELECT product_id, product_name FROM products")
        products = cursor.fetchall()
        if products:
            product_dict = {f"{p[1]} ({p[0]})": p[0] for p in products}
            selected_product = st.selectbox("Select Product to Edit", options=list(product_dict.keys()))
            
            if selected_product:
                product_id = product_dict[selected_product]
                cursor.execute("SELECT * FROM products WHERE product_id = %s", (product_id,))
                product = cursor.fetchone()
                
                # Show current values and allow editing
                new_product_name = st.text_input("Product Name", value=product[1], key="edit_name")
                new_category = st.text_input("Category", value=product[2], key="edit_category")
                new_subcategory = st.text_input("Subcategory", value=product[3], key="edit_subcategory")
                new_cost_price = st.number_input("Cost Price", value=float(product[4]), min_value=0.01, step=0.01, key="edit_cost")
                new_selling_price = st.number_input("Selling Price", value=float(product[5]), min_value=0.01, step=0.01, key="edit_price")
                new_quantity = st.number_input("Quantity Available", value=int(product[6]), min_value=0, step=1, key="edit_qty")
                new_reorder_level = st.number_input("Reorder Level", value=int(product[7]), min_value=0, step=1, key="edit_reorder")
                new_hsn_code = st.text_input("HSN Code", value=product[8], key="edit_hsn")
                new_gst_rate = st.number_input("GST Rate (%)", value=float(product[9]), min_value=0.0, max_value=100.0, step=0.1, key="edit_gst")
                
                if st.button("Update Product"):
                    try:
                        cursor.execute("""
                            UPDATE products 
                            SET product_name = %s, category = %s, subcategory = %s,
                                cost_price = %s, selling_price = %s, quantity_available = %s,
                                reorder_level = %s, hsn_code = %s, gst_rate = %s
                            WHERE product_id = %s
                        """, (new_product_name, new_category, new_subcategory, new_cost_price,
                              new_selling_price, new_quantity, new_reorder_level, new_hsn_code, 
                              new_gst_rate, product_id))
                        connection.commit()
                        st.success("Product updated successfully!")
                    except Error as e:
                        st.error(f"Error updating product: {e}")
        else:
            st.info("No products available to edit. Please add products first.")
    
    # Quick Quantity Update
    with st.expander("Quick Quantity Update"):
        if products:
            selected_product = st.selectbox("Select Product", options=list(product_dict.keys()), key="quick_qty_product")
            if selected_product:
                product_id = product_dict[selected_product]
                cursor.execute("SELECT quantity_available FROM products WHERE product_id = %s", (product_id,))
                current_qty = cursor.fetchone()[0]
                
                st.write(f"Current Quantity: {current_qty}")
                adjustment = st.number_input("Quantity Adjustment (positive to add, negative to subtract)", step=1, key="qty_adjustment")
                
                if st.button("Update Quantity"):
                    try:
                        new_qty = current_qty + adjustment
                        if new_qty < 0:
                            st.error("Quantity cannot be negative!")
                        else:
                            cursor.execute("""
                                UPDATE products 
                                SET quantity_available = %s 
                                WHERE product_id = %s
                            """, (new_qty, product_id))
                            connection.commit()
                            st.success(f"Quantity updated successfully! New quantity: {new_qty}")
                    except Error as e:
                        st.error(f"Error updating quantity: {e}")
    
    # Display current inventory
    st.subheader("Current Inventory")
    cursor.execute("SELECT * FROM products")
    products = cursor.fetchall()
    if products:
        df = pd.DataFrame(products, columns=["Product ID", "Product Name", "Category", "Subcategory", 
                                           "Cost Price", "Selling Price", "Quantity Available", "Reorder Level"])
        st.dataframe(df)
        
        # Alert for low inventory
        low_inventory = df[df["Quantity Available"] <= df["Reorder Level"]]
        if not low_inventory.empty:
            st.warning("Low Inventory Alert!")
            st.dataframe(low_inventory)

def calculate_profit(connection, product_name, category, subcategory, quantity, selling_price):
    """Utility function to calculate profit consistently"""
    cursor = connection.cursor()
    try:
        cursor.execute("""
            SELECT cost_price FROM products 
            WHERE product_name = %s AND category = %s AND subcategory = %s
        """, (product_name, category, subcategory))
        result = cursor.fetchone()
        
        if result:
            cost_price = result[0]
            profit = (selling_price - cost_price) * quantity
            return profit
        return 0  # Return 0 if product not found
    except Error as e:
        st.error(f"Error calculating profit: {e}")
        return 0
    finally:
        cursor.close()

def calculate_gst(price, gst_rate):
    """Calculate GST amount and final price"""
    gst_amount = price * (gst_rate / 100)
    final_price = price + gst_amount
    return gst_amount, final_price

def add_gst_rates_table(connection):
    """Create and manage GST rates table"""
    cursor = connection.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS gst_rates (
            category VARCHAR(255) PRIMARY KEY,
            gst_rate FLOAT,
            hsn_code VARCHAR(8)
        )
    """)
    connection.commit()

def update_order_table_for_gst():
    """Add GST related columns to order table"""
    cursor = connection.cursor()
    cursor.execute("""
        ALTER TABLE `{table_name}`
        ADD COLUMN IF NOT EXISTS hsn_code VARCHAR(8),
        ADD COLUMN IF NOT EXISTS cgst FLOAT,
        ADD COLUMN IF NOT EXISTS sgst FLOAT,
        ADD COLUMN IF NOT EXISTS igst FLOAT,
        ADD COLUMN IF NOT EXISTS gst_rate FLOAT
    """)
    connection.commit()

def generate_profit_loss_report(connection, start_date, end_date):
    st.subheader("Profit & Loss Report")
    
    # Date selection
    col1, col2 = st.columns(2)
    with col1:
        start_date = st.date_input("Start Date", start_date)
    with col2:
        end_date = st.date_input("End Date", end_date)

    # Fetch data
    cursor = connection.cursor()
    cursor.execute(f"""
        SELECT 
            SUM(total_amount) as revenue,
            SUM(profit) as gross_profit,
            SUM(discount) as total_discounts,
            COUNT(DISTINCT order_id) as total_orders
        FROM orders
        WHERE DATE(date_time) BETWEEN %s AND %s
    """, (start_date, end_date))
    
    # Calculate expenses
    cursor.execute("""
        SELECT SUM(amount) as total_expenses
        FROM expenses
        WHERE DATE(date) BETWEEN %s AND %s
    """, (start_date, end_date))
    
    # Display P&L Statement
    st.write("### Revenue")
    col1, col2 = st.columns(2)
    with col1:
        st.metric("Gross Sales", format_large_number(revenue))
        st.metric("Total Discounts", format_large_number(total_discounts))
        st.metric("Net Sales", format_large_number(revenue - total_discounts))
    
    with col2:
        st.metric("Gross Profit", format_large_number(gross_profit))
        st.metric("Total Expenses", format_large_number(total_expenses))
        st.metric("Net Profit", format_large_number(gross_profit - total_expenses))

    # Visual representations
    fig = make_subplots(rows=2, cols=2)
    # Add charts for revenue trends, profit margins, etc.
    st.plotly_chart(fig)

def generate_invoice(order_data, business_info):
    """Generate PDF invoice for an order"""
    # Create filename with timestamp to avoid conflicts
    filename = f"invoice_{order_data['order_id']}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf"
    
    doc = SimpleDocTemplate(filename, pagesize=letter)
    elements = []
    styles = getSampleStyleSheet()

    # Add invoice title
    elements.append(Paragraph("TAX INVOICE", styles['Heading1']))
    elements.append(Paragraph("<br/><br/>", styles['Normal']))

    # Business Information
    elements.append(Paragraph(f"From:", styles['Heading2']))
    elements.append(Paragraph(f"{business_info['name']}", styles['Normal']))
    elements.append(Paragraph(f"{business_info['address']}", styles['Normal']))
    elements.append(Paragraph(f"GSTIN: {business_info['gst_no']}", styles['Normal']))
    elements.append(Paragraph("<br/>", styles['Normal']))

    # Customer Information
    elements.append(Paragraph(f"Bill To:", styles['Heading2']))
    elements.append(Paragraph(f"Name: {order_data['customer_name']}", styles['Normal']))
    elements.append(Paragraph(f"Phone: {order_data['phone_number']}", styles['Normal']))
    elements.append(Paragraph("<br/>", styles['Normal']))

    # Invoice Details
    elements.append(Paragraph(f"Invoice No: INV-{order_data['order_id']}", styles['Normal']))
    elements.append(Paragraph(f"Date: {datetime.now().strftime('%d-%m-%Y')}", styles['Normal']))
    elements.append(Paragraph("<br/>", styles['Normal']))

    # Order Details Table
    data = [['Item Name', 'HSN', 'Qty', 'Rate', 'GST%', 'GST Amt', 'Total']]
    
    # Add order items to data
    total_gst = 0
    total_amount = 0
    
    for item in order_data['items']:
        # Calculate GST (assuming 18% for example - you should get this from your GST rates table)
        gst_percent = 18  # Get this from your GST rates table based on category
        base_price = float(item['price'])
        quantity = int(item['quantity'])
        item_total = base_price * quantity
        gst_amount = (item_total * gst_percent) / 100
        total_with_gst = item_total + gst_amount
        
        data.append([
            item['name'],
            '12345',  # HSN code - should come from your product database
            str(quantity),
            f"₹{base_price:,.2f}",
            f"{gst_percent}%",
            f"₹{gst_amount:,.2f}",
            f"₹{total_with_gst:,.2f}"
        ])
        
        total_gst += gst_amount
        total_amount += total_with_gst

    # Create table
    table = Table(data, colWidths=[120, 60, 40, 70, 50, 70, 80])
    table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 12),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        ('TEXTCOLOR', (0, 1), (-1, -1), colors.black),
        ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
        ('FONTSIZE', (0, 1), (-1, -1), 10),
        ('GRID', (0, 0), (-1, -1), 1, colors.black),
        ('ALIGN', (3, 1), (-1, -1), 'RIGHT'),  # Right align amounts
    ]))
    elements.append(table)
    elements.append(Paragraph("<br/>", styles['Normal']))

    # Summary
    elements.append(Paragraph(f"Subtotal: ₹{total_amount - total_gst:,.2f}", styles['Normal']))
    elements.append(Paragraph(f"Total GST: ₹{total_gst:,.2f}", styles['Normal']))
    elements.append(Paragraph(f"Grand Total: ₹{total_amount:,.2f}", styles['Normal']))
    
    # Terms and Conditions
    elements.append(Paragraph("<br/><br/>", styles['Normal']))
    elements.append(Paragraph("Terms and Conditions:", styles['Heading3']))
    elements.append(Paragraph("1. All disputes are subject to local jurisdiction", styles['Normal']))
    elements.append(Paragraph("2. E. & O. E.", styles['Normal']))

    # Build PDF
    doc.build(elements)
    return filename

def add_invoice_to_order_function():
    """Add invoice generation to order processing"""
    if st.button("Generate Invoice"):
        try:
            # Get business info from configuration
            business_info = {
                'name': st.secrets['business_name'],
                'address': st.secrets['business_address'],
                'gst_no': st.secrets['gst_no']
            }
            
            # Generate invoice
            invoice_file = generate_invoice(order_data, business_info)
            
            # Provide download link
            with open(invoice_file, "rb") as file:
                st.download_button(
                    label="Download Invoice",
                    data=file,
                    file_name=f"invoice_{order_data['order_id']}.pdf",
                    mime="application/pdf"
                )
        except Exception as e:
            st.error(f"Error generating invoice: {e}")

def track_expenses(connection):
    st.subheader("Expense Tracking")
    
    # Create expenses table if not exists
    cursor = connection.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS expenses (
            id INT AUTO_INCREMENT PRIMARY KEY,
            date DATE,
            category VARCHAR(255),
            description TEXT,
            amount FLOAT,
            payment_mode VARCHAR(255),
            reference_no VARCHAR(255)
        )
    """)
    connection.commit()
    
    # Add expense form
    with st.form("expense_form"):
        date = st.date_input("Date")
        category = st.selectbox("Category", ["Rent", "Utilities", "Salaries", "Inventory", "Others"])
        description = st.text_input("Description")
        amount = st.number_input("Amount", min_value=0.0, step=0.01)
        payment_mode = st.selectbox("Payment Mode", ["Cash", "Bank Transfer", "Credit Card"])
        reference_no = st.text_input("Reference Number")
        
        if st.form_submit_button("Add Expense"):
            try:
                cursor.execute("""
                    INSERT INTO expenses (date, category, description, amount, payment_mode, reference_no)
                    VALUES (%s, %s, %s, %s, %s, %s)
                """, (date, category, description, amount, payment_mode, reference_no))
                connection.commit()
                st.success("Expense added successfully!")
            except Error as e:
                st.error(f"Error adding expense: {e}")
    
    # Display expenses
    st.subheader("Recent Expenses")
    cursor.execute("SELECT * FROM expenses ORDER BY date DESC LIMIT 10")
    expenses = cursor.fetchall()
    if expenses:
        df = pd.DataFrame(expenses, columns=["ID", "Date", "Category", "Description", 
                                           "Amount", "Payment Mode", "Reference No"])
        st.dataframe(df)
        
        # Show expense summary
        st.subheader("Expense Summary")
        total_expenses = df['Amount'].sum()
        st.metric("Total Expenses", format_large_number(total_expenses))
        
        # Category-wise expenses
        category_expenses = df.groupby('Category')['Amount'].sum()
        fig = px.pie(values=category_expenses.values, names=category_expenses.index,
                    title='Expenses by Category')
        st.plotly_chart(fig)

def generate_invoice_page(connection, table_name):
    st.subheader("Generate Invoice")
    
    # Order selection
    cursor = connection.cursor()
    cursor.execute(f"""
        SELECT o.*, p.hsn_code, p.gst_rate 
        FROM `{table_name}` o 
        LEFT JOIN products p ON o.product_name = p.product_name 
        ORDER BY o.date_time DESC
    """)
    orders = cursor.fetchall()
    
    if orders:
        order_dict = {f"{o[0]} - {o[1]} ({o[11]})": o for o in orders}
        selected_order = st.selectbox("Select Order", options=list(order_dict.keys()), key="invoice_order_select")
        
        if selected_order:
            order_data = order_dict[selected_order]
            
            # Display order details
            st.write("### Order Details")
            col1, col2 = st.columns(2)
            with col1:
                st.write(f"Customer: {order_data[7]}")
                st.write(f"Phone: {order_data[8]}")
                st.write(f"Email: {order_data[9]}")
            with col2:
                st.write(f"Total Amount: {format_large_number(order_data[6])}")
                st.write(f"Date: {order_data[11]}")
                st.write(f"Payment Status: {order_data[13]}")
            
            # Business Info Form
            st.write("### Business Information")
            business_name = st.text_input("Business Name", key="invoice_business_name")
            business_address = st.text_area("Business Address", key="invoice_business_address")
            gst_no = st.text_input("GST Number", key="invoice_gst_no")
            
            if st.button("Generate Invoice", key="generate_invoice_btn"):
                if not all([business_name, business_address, gst_no]):
                    st.error("Please fill in all business information fields")
                else:
                    try:
                        # Prepare business info
                        business_info = {
                            'name': business_name,
                            'address': business_address,
                            'gst_no': gst_no
                        }
                        
                        # Convert order_data to dictionary with GST info
                        order_dict = {
                            'order_id': order_data[0],
                            'customer_name': order_data[7],
                            'phone_number': order_data[8],
                            'items': [{
                                'name': order_data[1],
                                'quantity': order_data[5],
                                'price': order_data[4],
                                'total': order_data[6],
                                'hsn_code': order_data[-2],  # From joined products table
                                'gst_rate': order_data[-1]   # From joined products table
                            }]
                        }
                        
                        # Generate and offer download
                        invoice_file = generate_invoice(order_dict, business_info)
                        with open(invoice_file, "rb") as file:
                            st.download_button(
                                label="Download Invoice",
                                data=file,
                                file_name=f"invoice_{order_data[0]}.pdf",
                                mime="application/pdf",
                                key="download_invoice_btn"
                            )
                        
                        # Clean up file after download
                        import os
                        os.remove(invoice_file)
                        
                    except Exception as e:
                        st.error(f"Error generating invoice: {e}")
    else:
        st.info("No orders available for invoice generation")

def main():
    st.set_page_config(page_title="Order Management System", page_icon="📒", layout="centered")
    st.title("Order Management System")

    # Initialize session state
    if 'database_name' not in st.session_state:
        st.session_state['database_name'] = None
    if 'table_name' not in st.session_state:
        st.session_state['table_name'] = None
    if 'excel_file_name' not in st.session_state:
        st.session_state['excel_file_name'] = None

    # Sidebar for database, table, and Excel file selection
    with st.sidebar:
        st.subheader("Configuration")
        
        # Database selection/creation
        database_name = st.text_input("Enter database name to create/select", value=st.session_state['database_name'] or "")
        if database_name:
            st.session_state['database_name'] = database_name
        
        # Table selection/creation
        table_name = st.text_input("Enter table name to create/select", value=st.session_state['table_name'] or "")
        if table_name:
            st.session_state['table_name'] = table_name
        
        # Excel file selection/creation
        excel_file_name = st.text_input("Enter Excel file name to create/select", value=st.session_state['excel_file_name'] or "")
        if excel_file_name:
            st.session_state['excel_file_name'] = excel_file_name

        st.subheader("Business Configuration")
        if st.checkbox("Update Business Info"):
            business_name = st.text_input("Business Name")
            business_address = st.text_area("Business Address")
            gst_no = st.text_input("GST Number")
            # Save to database when updated

    # Main content
    if not st.session_state['database_name']:
        st.info("Please enter a database name in the sidebar to get started.")
    elif not st.session_state['table_name']:
        st.info("Please enter a table name in the sidebar to continue.")
    elif not st.session_state['excel_file_name']:
        st.info("Please enter an Excel file name in the sidebar to proceed.")
    else:
        connection = get_database_connection()
        if connection:
            try:
                create_database_if_not_exists(connection, st.session_state['database_name'])
                connection.database = st.session_state['database_name']
                create_order_table(connection, st.session_state['table_name'])
                
                if st.session_state['excel_file_name'] not in st.session_state['excel_file_names']:
                    save_to_excel([], st.session_state['excel_file_name'])
                
                option = st.selectbox("Choose an action", 
                                     ["Manage Inventory", "Add Order", "Update Order", 
                                      "Delete Order", "Display Orders", "Track Expenses",
                                      "Generate Invoice"])
                
                if option == "Manage Inventory":
                    manage_product_inventory(connection)
                elif option == "Add Order":
                    add_order(connection, st.session_state['table_name'], st.session_state['excel_file_name'])
                elif option == "Update Order":
                    update_order(connection, st.session_state['table_name'])
                elif option == "Delete Order":
                    delete_order(connection, st.session_state['table_name'])
                elif option == "Display Orders":
                    display_orders(connection, st.session_state['table_name'])
                elif option == "Track Expenses":
                    track_expenses(connection)
                elif option == "Generate Invoice":
                    generate_invoice_page(connection, st.session_state['table_name'])
            except Error as e:
                st.error(f"An error occurred: {e}")
            finally:
                connection.close()
        else:
            st.error("Unable to connect to the database. Please check your database configuration.")

if __name__ == "__main__":
    main()