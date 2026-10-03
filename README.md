# Laboratory Stock Management System

A simple, clean, colorful, responsive, and beginner-friendly web application designed for managing laboratory items, stock levels, stock additions, stock usage, and inventory transaction history.

Developed as an **MCA Academic Project Showcase** using Python Flask, HTML, Bootstrap 5, and MySQL.

---

## 🌟 Key Features

1. **Admin Authentication**
   - Secure login & logout using Flask session management and password hashing (`werkzeug.security`).
   - Default Admin Credentials:
     - **Username:** `admin`
     - **Password:** `admin123`

2. **Admin Dashboard**
   - Live statistical counters for:
     - **Total Items**
     - **Available Items (In Stock)**
     - **Low Stock Items**
     - **Out of Stock Items**
   - Quick operation shortcuts and recent stock movement logs.

3. **Item Management (CRUD)**
   - Add new lab items with details: Name, Code, Category, Unit, Quantity, Minimum Stock Threshold, Location, and Added Date.
   - Edit existing item details and thresholds.
   - Delete items (with confirmation modal).
   - Pre-configured Categories:
     - *Computer Equipment*
     - *Electronic Components*
     - *Laboratory Equipment*
     - *Stationery*
     - *Other*

4. **Automated Stock Status Calculation**
   - **In Stock (Green):** `Quantity > Minimum Stock`
   - **Low Stock (Orange):** `Quantity > 0` AND `Quantity <= Minimum Stock`
   - **Out of Stock (Red):** `Quantity == 0`

5. **Stock Transactions (Add / Reduce Stock)**
   - Add new stock quantity or record consumed stock.
   - **Validation:** Prevents stock quantity from becoming negative.
   - Automatically logs transaction history with date, quantity change, and user remarks.

6. **Search & Filter**
   - Search items by **Item Name** or **Item Code**.
   - Filter by **Category** or **Stock Status**.
   - Filter stock audit logs by specific laboratory item.

---

## 🛠️ Color Theme & Design

Designed with a clean, modern, and colorful theme:
- **Primary Teal:** `#005f73`
- **Sky Blue:** `#0a9396` / `#e0f2fe`
- **Accent Orange:** `#ee9b00` / `#ca6702`
- Responsive layout built with Bootstrap 5 cards, badges, and modal dialogs.

---

## 📂 Project Structure

```
laboratory_stock/
│
├── app.py                  # Main Flask backend application & models
├── database.sql            # MySQL database creation script & seed data
├── requirements.txt        # Required Python packages
├── test_app.py             # Unit tests for application logic
├── README.md               # Setup and presentation guide
│
├── templates/
│   ├── base.html           # Base layout navigation & flash alerts
│   ├── index.html          # Landing home page
│   ├── admin_login.html    # Admin login page
│   ├── dashboard.html      # Admin dashboard page
│   ├── items.html          # Items list with search & filters
│   ├── add_item.html       # Form to register new item
│   ├── edit_item.html      # Form to edit item details
│   ├── stock_update.html   # Form to add or reduce stock
│   └── stock_history.html  # Audit history log page
│
└── static/
    ├── css/
    │   └── style.css       # Custom Deep Teal + Sky Blue + Orange theme CSS
    └── js/
        └── script.js       # Client-side validation & alert handlers
```

---

## 📋 Required Python Packages

Install required packages via `pip`:

```bash
pip install Flask Flask-SQLAlchemy PyMySQL
```

---

## 🛠️ XAMPP and phpMyAdmin Database Setup

1. Start **XAMPP Control Panel**.
2. Start the **Apache** and **MySQL** services.
3. Open your web browser and go to `http://localhost/phpmyadmin/`.
4. Click on the **SQL** tab in phpMyAdmin.
5. Copy the entire contents of `database.sql` and paste it into the SQL box, then click **Go**.
6. The database `laboratory_stock` and tables (`admins`, `items`, `stock_history`) with sample data will be created automatically.

---

## 🚀 Running the Project in VS Code

1. Open VS Code and open the `laboratory_stock` folder (`File -> Open Folder`).
2. Open the integrated terminal (`Ctrl + ~` or `Terminal -> New Terminal`).
3. Ensure MySQL is running in XAMPP.
4. Execute the application:
   ```bash
   python app.py
   ```
5. Open your browser and navigate to:
   ```
   http://127.0.0.1:5000
   ```

*(Note: To test using SQLite without MySQL/XAMPP, run `USE_SQLITE=1 python app.py`)*

---

## 🧪 Running Unit Tests

To run the automated unit test suite:

```bash
USE_SQLITE=1 python3 -m unittest test_app.py
```

---

## 🎓 MCA Presentation Tips for Student Demo

- **Admin Login Demo:** Log in using `admin` / `admin123`.
- **Item Creation:** Add a new item (e.g. `Raspberry Pi 4`, Code `COMP-003`, Quantity `10`, Min Threshold `5`). Point out how it immediately appears as **In Stock**.
- **Low Stock Demo:** Reduce the stock to `3` using **Update Stock -> Stock Used**. Show how the status badge changes automatically to **Low Stock** (Orange).
- **Out of Stock & Negative Check:** Reduce stock by another `3` to reach `0` (**Out of Stock**). Attempt to reduce stock by `1` again to show the validation message preventing negative stock.
- **Audit Trail:** Open **Stock History** to explain how every stock change is recorded with timestamps and remarks.
