# Business Supplier & Purchase Management System

A modern, responsive, beginner-friendly web application built for managing suppliers, product inventory, purchase orders, and stock updates.

---

## 🎨 Theme & Design System
- **Indigo**: Navigation bar, headers, buttons, and primary actions.
- **Mint**: Success indicators, completed purchase badges, and highlights.
- **Peach**: Cards, alerts, purchase totals, and accent elements.
- **Gradient Background**: Indigo-to-Mint gradient background.
- **UI Components**: Glassmorphism cards, soft shadows, Bootstrap 5 grid & components, and Bootstrap Icons.

---

## 🚀 Key Features

### 1. Admin Login & Authentication
- Secure admin login using username (`admin`) and password (`admin123`).
- Protected dashboard routes with session handling.

### 2. Admin Dashboard
- **Total Suppliers**: Count of active/inactive suppliers.
- **Total Products**: Count of product items in catalog.
- **Total Purchases**: Total purchase orders created.
- **Pending Purchases**: Orders awaiting goods receipt.
- **Completed Purchases**: Orders received into inventory stock.
- **Total Purchase Expenditure**: Real-time sum of total purchase costs.
- Low stock alert list & recent purchase orders table.

### 3. Supplier Management
- Add, Edit, Delete, View, and Search suppliers.
- Tracks contact person, company name, phone, email, address, and status (`Active` / `Inactive`).
- **Supplier Details Page**: Shows supplier info, total purchases count, total expenditure with supplier, and complete supplier purchase history.

### 4. Product Management
- Add, Edit, Delete, and Search products.
- Fields: Product Name, Product Code, Category, Purchase Price, Current Stock, Minimum Stock Level.
- Automatic Stock Indicators:
  - `In Stock` (Stock > Minimum level)
  - `Low Stock` (Stock <= Minimum level)
  - `Out of Stock` (Stock == 0)

### 5. Purchase Management & History
- Create purchase orders with automatic purchase reference generation (`PUR-1001`, `PUR-1002`, ...).
- Automatic Real-Time Calculation: `Total Amount = Quantity × Purchase Price`.
- Select product to auto-populate default purchase price.
- **Automatic Stock Update**: Marking a purchase order status as **Received** automatically increments product current stock quantity!
- Search & status filter (`Pending`, `Ordered`, `Received`, `Cancelled`).

---

## 🗄️ Database Structure (`database.sql`)

The project includes a complete MySQL schema with seed data in `database.sql`:
- `admins`: Stores admin authentication credentials.
- `suppliers`: Supplier directory.
- `products`: Product catalog & current stock levels.
- `purchases`: Master purchase records.
- `purchase_items`: Line items for each purchase.

---

## 🛠️ XAMPP & phpMyAdmin Setup Instructions

1. **Start XAMPP**:
   - Open **XAMPP Control Panel**.
   - Click **Start** for both **Apache** and **MySQL** modules.

2. **Open phpMyAdmin**:
   - Open your web browser and go to `http://localhost/phpmyadmin/`.

3. **Import `database.sql`**:
   - Click on the **Import** tab at the top menu.
   - Click **Choose File** and select `database.sql` from the project folder.
   - Click **Go** at the bottom to create `supplier_purchase_db` and populate all tables with sample data.

---

## 💻 How to Run the Project in VS Code

1. **Open Project**:
   - Launch **VS Code** and open the `project/` directory (`File` > `Open Folder`).

2. **Open Terminal**:
   - Press `` Ctrl + ` `` (or `Terminal` > `New Terminal`).

3. **Install Dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

4. **Run the Flask App**:
   - **For MySQL (XAMPP running)**:
     ```bash
     python app.py
     ```
   - **For SQLite (Fallback / Testing mode)**:
     ```bash
     USE_SQLITE=1 python app.py
     ```

5. **Access Application**:
   - Open your web browser and navigate to: `http://127.0.0.1:5000`

---

## 🔑 Test Credentials

- **Username**: `admin`
- **Password**: `admin123`

---

## 🎓 Academic Note
*Developed as an MCA Mini Project built with Python Flask, HTML5, CSS3, Bootstrap 5, JavaScript, and MySQL.*
