# STEP 0
import sqlite3
import pandas as pd

# Connect to the database
conn = sqlite3.connect('data.sqlite')

# Display schema (optional)
pd.read_sql("""SELECT * FROM sqlite_master""", conn)

# STEP 1 - Part 1: Join and Filter
# 1. Employees in Boston
df_boston = pd.read_sql("""
    SELECT e.firstName, e.lastName, e.jobTitle
    FROM Employees e
    JOIN Offices o ON e.officeCode = o.officeCode
    WHERE o.city = 'Boston';
""", conn)

# 2. Offices with zero employees – only officeCode and city (HAVING used)
df_zero_emp = pd.read_sql("""
    SELECT o.officeCode, o.city
    FROM Offices o
    LEFT JOIN Employees e ON o.officeCode = e.officeCode
    GROUP BY o.officeCode, o.city
    HAVING COUNT(e.employeeNumber) = 0;
""", conn)

# STEP 2 - Part 2: Type of Join
# All employees with office city/state (include those without an office)
df_employee = pd.read_sql("""
    SELECT e.firstName, e.lastName, o.city, o.state
    FROM Employees e
    LEFT JOIN Offices o ON e.officeCode = o.officeCode
    ORDER BY e.firstName, e.lastName;
""", conn)

# Customers who have not placed an order – contact info and sales rep employee number
df_contacts = pd.read_sql("""
    SELECT c.contactFirstName, c.contactLastName, c.phone, c.salesRepEmployeeNumber
    FROM Customers c
    LEFT JOIN Orders o ON c.customerNumber = o.customerNumber
    WHERE o.orderNumber IS NULL
    ORDER BY c.contactLastName;
""", conn)

# STEP 3 - Part 3: Built‑In Function
# Payments sorted descending by amount (cast to REAL)
df_payment = pd.read_sql("""
    SELECT c.contactFirstName, c.contactLastName, p.amount, p.paymentDate
    FROM Customers c
    JOIN Payments p ON c.customerNumber = p.customerNumber
    ORDER BY CAST(p.amount AS REAL) DESC;
""", conn)

# STEP 4 - Part 4: Joining and Grouping
# Employees with customer avg credit limit > 90k (top 4 by number of customers)
df_credit = pd.read_sql("""
    SELECT e.employeeNumber, e.firstName, e.lastName, COUNT(c.customerNumber) AS num_customers
    FROM Employees e
    JOIN Customers c ON e.employeeNumber = c.salesRepEmployeeNumber
    GROUP BY e.employeeNumber, e.firstName, e.lastName
    HAVING AVG(c.creditLimit) > 90000
    ORDER BY num_customers DESC
    LIMIT 4;
""", conn)

# Product name, number of orders, and total units sold
df_product_sold = pd.read_sql("""
    SELECT p.productName,
           COUNT(DISTINCT od.orderNumber) AS numorders,
           SUM(od.quantityOrdered) AS totalunits
    FROM Products p
    JOIN OrderDetails od ON p.productCode = od.productCode
    GROUP BY p.productCode, p.productName
    ORDER BY totalunits DESC;
""", conn)

# STEP 5 - Part 5: Multiple Joins
# Product name, code, and number of distinct customers who ordered each product
df_total_customers = pd.read_sql("""
    SELECT p.productName, p.productCode, COUNT(DISTINCT o.customerNumber) AS numpurchasers
    FROM Products p
    JOIN OrderDetails od ON p.productCode = od.productCode
    JOIN Orders o ON od.orderNumber = o.orderNumber
    GROUP BY p.productCode, p.productName
    ORDER BY numpurchasers DESC;
""", conn)

# Number of customers per office
df_customers = pd.read_sql("""
    SELECT off.officeCode, off.city, COUNT(c.customerNumber) AS n_customers
    FROM Offices off
    JOIN Employees e ON off.officeCode = e.officeCode
    JOIN Customers c ON e.employeeNumber = c.salesRepEmployeeNumber
    GROUP BY off.officeCode, off.city;
""", conn)

# STEP 6 - Part 6: Subquery (using CTE for clarity)
df_under_20 = pd.read_sql("""
    WITH low_products AS (
        SELECT productCode
        FROM OrderDetails od
        JOIN Orders o ON od.orderNumber = o.orderNumber
        GROUP BY productCode
        HAVING COUNT(DISTINCT o.customerNumber) < 20
    )
    SELECT DISTINCT e.employeeNumber, e.firstName, e.lastName, off.city, off.officeCode
    FROM Employees e
    JOIN Offices off ON e.officeCode = off.officeCode
    JOIN Customers c ON e.employeeNumber = c.salesRepEmployeeNumber
    JOIN Orders o ON c.customerNumber = o.customerNumber
    JOIN OrderDetails od ON o.orderNumber = od.orderNumber
    WHERE od.productCode IN (SELECT productCode FROM low_products);
""", conn)

# Close the connection
conn.close()