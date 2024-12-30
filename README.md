# PyStoreManager

**PyStoreManager**  
*Your Comprehensive Store Management System*

The PyStore Management System is a robust, Streamlit-based web application tailored for businesses to manage orders efficiently. It integrates seamlessly with MySQL for secure data storage and Excel for flexible data handling, ensuring data accuracy and accessibility. Below are the enhanced features based on the latest implementation:

---

## Key Features:

1. **Database Management**  
   - Create and manage databases dynamically within MySQL.
   - Automated schema creation for orders, products, and expenses.

2. **Order Management**  
   - Add, update, and delete orders with detailed information, including:
     - Product details: Category, Subcategory, Price, Quantity.
     - Customer details: Name, Phone, Email.
     - Financial metrics: Profit, Discounts, Taxes, Payment Status, and Net Total.
   - Multi-level validation to ensure data integrity.

3. **Product Inventory Management**  
   - Add, edit, and manage products with fields such as:
     - Cost Price, Selling Price, Quantity, Reorder Level.
     - HSN Code and GST Rate for compliance and billing.
   - Alerts for low inventory to prevent stockouts.

4. **Integrated Expense Tracking**  
   - Record and manage expenses with details like category, payment mode, and references.
   - View and analyze expense trends with category-wise visualizations.

5. **Invoice Generation**  
   - Generate GST-compliant invoices in PDF format with:
     - Business and customer details.
     - Itemized breakdowns, GST calculations, and terms.
   - Downloadable invoices for professional record-keeping.

6. **Excel Integration**  
   - Save, update, and back up order data in Excel files.
   - Export detailed analysis, including raw data, trends, and summaries, to Excel for external reporting.

7. **Advanced Data Visualization**  
   - Use Plotly for rich, interactive charts and graphs, including:
     - Sales trends by category, payment modes, and regions.
     - Time-based analysis (daily, monthly trends).
     - Profitability metrics such as profit margins and discount impacts.

8. **Profit & Loss Analysis**  
   - Calculate revenue, gross profit, discounts, expenses, and net profit.
   - Visual representations for revenue trends, profit margins, and more.

9. **GST Management**  
   - Integrated GST rate calculations for accurate tax reporting.
   - Support for CGST, SGST, IGST, and HSN Code management.

10. **Custom Business Configuration**  
    - Update and manage business details such as name, address, and GST number dynamically.

11. **User-Friendly Interface**  
    - Simplified navigation through a structured Streamlit interface.
    - Sidebars for quick access to database, table, and file configurations.

12. **Custom Alerts and Notifications**  
    - Low inventory warnings.
    - Profit loss due to discounts and other actionable insights.

13. **Scalable Architecture**  
    - Support for multiple databases and tables.
    - Dynamic handling of orders, products, and financial records.

14. **Advanced Features**  
    - Real-time format conversion for large numbers (e.g., ₹1.2M).
    - Monthly and daily sales dashboards with insights into trends and patterns.

15. **Security and Efficiency**  
    - Secure connection to MySQL with streamlined error handling.
    - Session state management for efficient user experience.

---

## Future Enhancements:

- AI-based recommendation engine for inventory restocking.
- Multilingual support for broader accessibility.
- Integration with third-party payment gateways for seamless transactions.

**PyStoreManager** aims to be the go-to solution for businesses seeking an integrated and efficient order management system. Stay organized, stay ahead! 🚀
