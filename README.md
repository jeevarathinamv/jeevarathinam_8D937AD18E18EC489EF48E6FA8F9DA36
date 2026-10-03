# Small Business Sales & Customer Management System

A simple, modern, beginner-friendly web application built using **Python Flask**, **Bootstrap 5**, **HTML5/CSS3**, and **MySQL (XAMPP)**. Designed specifically for an MCA project demo/viva.

---

## 🎨 Design Theme & Colors

- **Theme:** Royal Blue + Coral + Mint
- **Background:** Vibrant Royal Blue to Coral gradient
- **Navigation & Headers:** Royal Blue (`#1a365d`)
- **Buttons & Highlights:** Coral (`#ff6b6b`)
- **Success & Completed Sales:** Mint (`#28a745`)
- **Alerts & Out of Stock Warnings:** Warning Red (`#dc3545`)
- **Components:** Rounded glassmorphic cards, soft drop shadows, and Bootstrap Icons.

---

## 🚀 Key Features

### 1. Admin Authentication
- Secure login using Username (`admin`) and Password (`admin123`).
- Logout functionality with session management.

### 2. Admin Dashboard
- Stat Cards: Total Customers, Total Products, Total Sales, Today's Sales, Pending Orders, Total Revenue.
- Revenue & Sales Summary: Today's Revenue, This Week's Revenue, This Month's Revenue, Total Revenue.
- Quick Actions & Recent Sales Table.

### 3. Customer Management
- Add, Edit, View, and Delete Customers.
- Customer Types: `New`, `Regular`, `VIP`.
- Customer Search functionality (Name, Phone, Email, Type).
- **Customer Profile & Purchase History:** Displays total purchases, total amount spent, last purchase date, and invoice list.

### 4. Product Management
- Add, Edit, View, and Delete Products.
- Fields: Product Name, Product Code, Category, Selling Price, Available Stock, Minimum Stock Level.
- **Automatic Stock Status Indicators:**
  - 🟢 **In Stock** (Available quantity > Minimum Stock level)
  - 🟡 **Low Stock** (Available quantity ≤ Minimum Stock level)
  - 🔴 **Out of Stock** (Available quantity = 0)

### 5. Sales Management & Automated Stock Update
- Create new sales with auto-generated Sale Number (e.g. `SL-20250520-0001`).
- **Automatic Price Calculations:**
  - Item Subtotal = Quantity × Selling Price
  - Grand Total = Subtotal - Discount
- **Automated Stock Deduction:** Reduces product stock automatically upon sale creation.
- Payment Statuses: `Paid`, `Partially Paid`, `Unpaid`.
- Print Receipt / Invoice view.
- Filter Sales by Search query and Date.

---

## 📁 Project Structure

```text
project/
├── app.py
├── database.sql
├── requirements.txt
├── test_app.py
├── README.md
├── templates/
│   ├── base.html
│   ├── login.html
│   ├── dashboard.html
│   ├── customers.html
│   ├── add_customer.html
│   ├── edit_customer.html
│   ├── customer_details.html
│   ├── products.html
│   ├── add_product.html
│   ├── edit_product.html
│   ├── create_sale.html
│   ├── edit_sale.html
│   ├── sale_details.html
│   └── sales_history.html
└── static/
    ├── css/
    │   └── style.css
    └── js/
        └── script.js
```

---

## 🛠️ Step-by-Step Setup Guide

### 1. Setting Up Database with XAMPP & phpMyAdmin

1. Open **XAMPP Control Panel** and start both **Apache** and **MySQL** services.
2. Open your web browser and go to `http://localhost/phpmyadmin`.
3. Click on the **Import** tab in phpMyAdmin.
4. Click **Choose File** and select `database.sql` from the project directory.
5. Click **Go** at the bottom to create the `service_booking_db` database and tables with default seed data.

---

### 2. Running the Application in VS Code

1. Open **VS Code** and open the project folder (`File > Open Folder...`).
2. Open the terminal in VS Code (`Ctrl + ~` or `Terminal > New Terminal`).
3. Install required Python packages:
   ```bash
   pip install flask flask-sqlalchemy pymysql
   ```
4. Run the Flask application:
   ```bash
   python app.py
   ```
5. Open your browser and go to `http://127.0.0.1:5000`.

---

### 🔑 Default Admin Login Credentials

- **Username:** `admin`
- **Password:** `admin123`

---

## 🧪 Running Unit Tests

To run the automated unit tests locally using SQLite in-memory mode:

```bash
USE_SQLITE=1 python -m unittest test_app.py
```
