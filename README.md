# College Lab Consumables Inventory System

A simple, modern, and beginner-friendly web application built for managing college laboratory consumables across various departments (Chemicals, Glassware, Stationery, Electronic Components, Cleaning Materials).

---

## 🌟 Key Features

1. **Admin Authentication**:
   - Secure Admin login using Flask Session and Werkzeug password hashing.
   - Pre-configured Admin credentials for presentation demonstrations.

2. **Interactive Admin Dashboard**:
   - Live metrics summary: Total Consumables, Total Available Stock, Low Stock Alerts, and Out of Stock Count.
   - Quick navigation shortcuts & real-time stock alert banners.

3. **Consumables Management (CRUD)**:
   - Add new consumable items with custom unit, lab name, minimum stock level, and category.
   - Edit consumable details and delete items with modal confirmation.
   - Dynamic stock status badges:
     - 🟢 **In Stock**: Quantity > Minimum Stock Level
     - 🟡 **Low Stock**: Quantity > 0 and Quantity <= Minimum Stock Level
     - 🔴 **Out of Stock**: Quantity = 0

4. **Stock Update Module**:
   - **Add Stock**: Increase quantity with transaction audit logging.
   - **Use Stock**: Deduct quantity with validation preventing negative stock levels.

5. **Stock Transaction History**:
   - Detailed audit history table tracking date, consumable name, item code, transaction type (`Stock Added` / `Stock Used`), quantity, and remarks.

6. **Search & Filter**:
   - Filter consumables by item name, item code, category, or stock status.

---

## 🛠️ Technologies Used

- **Frontend**: HTML5, CSS3, Bootstrap 5, Bootstrap Icons
- **Backend**: Python 3, Flask, Flask-SQLAlchemy
- **Database**: MySQL (PyMySQL) / SQLite fallback option
- **Server**: XAMPP (Apache & MySQL) / Localhost
- **Editor**: VS Code

---

## 🔑 Default Admin Login Credentials

- **Username**: `admin`
- **Password**: `admin123`

---

## 📂 Project Structure

```text
college_lab_consumables/
│
├── app.py                  # Main Flask application logic & SQLAlchemy models
├── database.sql            # MySQL schema & sample seed data
├── requirements.txt        # Python package dependencies
├── test_app.py             # Unit tests for testing routes & logic
├── README.md               # Project setup and usage documentation
│
├── templates/
│   ├── base.html           # Main layout template
│   ├── index.html          # System landing home page
│   ├── admin_login.html    # Admin login page
│   ├── dashboard.html      # Admin dashboard with live stats & alerts
│   ├── consumables.html    # Consumables list with search & filters
│   ├── add_consumable.html # Add new consumable item form
│   ├── edit_consumable.html# Edit consumable details form
│   ├── stock_update.html   # Add stock or use stock form
│   └── stock_history.html  # Transaction audit log page
│
└── static/
    ├── css/
    │   └── style.css       # Navy Blue, Mint Green, and Orange theme styling
    └── js/
        └── script.js       # Client-side form validation & interactions
```

---

## 🚀 How to Setup and Run the Project

### 1. Database Setup using XAMPP / phpMyAdmin

1. Open **XAMPP Control Panel** and start **Apache** and **MySQL**.
2. Open your browser and go to `http://localhost/phpmyadmin`.
3. Click on **Import** in phpMyAdmin.
4. Choose the `database.sql` file provided in this repository and click **Go**.
5. This will automatically create the `lab_consumables_db` database, create all required tables (`admins`, `consumables`, `stock_history`), and insert sample records.

---

### 2. Install Required Python Packages

1. Open VS Code and open the project directory.
2. Open the terminal in VS Code (`Ctrl + ~` or `Terminal -> New Terminal`).
3. Run the following command to install required dependencies:
   ```bash
   pip install -r requirements.txt
   ```

---

### 3. Run the Project in VS Code

1. Start the Flask application by executing:
   ```bash
   python app.py
   ```
2. Open your web browser and navigate to:
   ```text
   http://127.0.0.1:5000
   ```
3. Click on **Admin Portal Login** and log in using:
   - **Username**: `admin`
   - **Password**: `admin123`

---

## 🧪 Running Unit Tests

To run the automated tests using SQLite in-memory database:

```bash
USE_SQLITE=1 python3 -m unittest test_app.py
```

---

## 🔄 Project Workflow Flowchart

`Admin Login` ➡️ `Dashboard` ➡️ `Add Consumable` ➡️ `Update Stock (Add/Use)` ➡️ `View Stock Status` ➡️ `Audit Stock History` ➡️ `Logout`
