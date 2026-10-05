# Library Book Fine Management System

A simple, beginner-friendly web application built with **Python Flask**, **Bootstrap 5**, and **MySQL (XAMPP)** for managing library books, book issues, return deadlines, and automatic overdue fine calculations (₹5 per late day).

---

## 🎨 Design & Color Theme
- **Theme:** Maroon + Cream + Gold
- **Framework:** Bootstrap 5
- **Icons:** Bootstrap Icons

---

## 🚀 Key Features

### 1. Student Portal
- **Registration & Login:** Register with Name, Register Number, Department, Email, and Password (hashed).
- **Student Dashboard:** Track Total Issued Books, Returned Books, Overdue Books, and Total Fine.
- **My Books:** View all issued books, issue dates, return deadlines, return dates, and fine amounts.
- **My Fine Details:** View late days and fine status (No Fine, Pending, Paid).

### 2. Admin Portal
- **Admin Dashboard:** Overview of Total Students, Issued Books, Overdue Books, Total Fine, and Pending Fine.
- **Book Management:** Add, edit, delete, and view books with stock copies.
- **Issue & Return Books:** Issue books to students with custom due dates, process returns, automatically compute late days and fine (₹5 / day late).
- **Fine Management:** Track fines and update fine payment status (Pending / Paid / No Fine).

---

## 🔑 Default Admin Credentials
- **Username:** `admin`
- **Password:** `admin123`

---

## ⚙️ XAMPP & phpMyAdmin Setup Instructions

1. **Start XAMPP:**
   - Open XAMPP Control Panel.
   - Start **Apache** and **MySQL** modules.

2. **Open phpMyAdmin:**
   - Open browser and navigate to `http://localhost/phpmyadmin/`.

3. **Import Database:**
   - Click on **New** to create a database named `library_fine_db`.
   - Click on **Import** tab.
   - Choose `database.sql` from the project folder and click **Import**.

---

## 💻 VS Code Setup & Run Instructions

1. **Open Project in VS Code:**
   - Launch VS Code and open the `library_fine_management` project directory.

2. **Set up Virtual Environment & Dependencies:**
   ```bash
   python3 -m venv venv
   source venv/bin/activate    # On Windows: venv\Scripts\activate
   pip install -r requirements.txt
   ```

3. **Run the Flask Application:**
   ```bash
   python3 app.py
   ```

4. **Access Application in Browser:**
   - Open `http://127.0.0.1:5000/` in your web browser.

> **Note (SQLite Demo Option):**
> To run using SQLite without MySQL setup (e.g. for testing):
> ```bash
> USE_SQLITE=1 python3 app.py
> ```

---

## 📁 Project Structure

```
library_fine_management/
│
├── app.py                      # Main Flask application logic & SQLAlchemy models
├── database.sql                 # MySQL schema script for phpMyAdmin
├── requirements.txt            # Project dependencies
├── test_app.py                 # Unit test suite
├── README.md                   # Setup & documentation guide
│
├── templates/                  # Jinja2 HTML Templates
│   ├── base.html               # Master layout template (Navbar, Footer, Alerts)
│   ├── index.html              # Landing home page
│   ├── register.html           # Student registration page
│   ├── login.html              # Student login page
│   ├── student_dashboard.html  # Student dashboard
│   ├── my_books.html           # Student issued books list
│   ├── fine_details.html       # Student fine details page
│   ├── admin_login.html        # Admin login page
│   ├── admin_dashboard.html    # Admin dashboard
│   ├── manage_books.html       # Admin book catalog table
│   ├── add_book.html           # Admin add book form
│   ├── edit_book.html          # Admin edit book form
│   ├── issue_book.html         # Admin issue book form
│   ├── return_book.html        # Admin return book form
│   └── fine_management.html    # Admin fine status management
│
└── static/                     # Static CSS & JS Assets
    ├── css/
    │   └── style.css           # Maroon + Cream + Gold custom CSS
    └── js/
        └── script.js           # Form validation & dynamic fine preview JS
```

---

## 🧪 Running Unit Tests

Run the test suite using SQLite in-memory database:

```bash
USE_SQLITE=1 python3 -m unittest test_app.py
```
