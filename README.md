# College Library Book Issue & Return System

A simple, modern, and beginner-friendly web application built for MCA academic project demonstrations. This system allows students to search and issue library books online, track issue history, and allows administrators to manage books, issue records, student accounts, and process book returns with auto-updated available stock counts.

---

## 🌟 Key Features

### Student Features
* **Student Registration & Login**: Register with Name, Register Number, Department, Email, and Password (hashed).
* **Interactive Dashboard**: Displays Total Books, Issued Books, Returned Books, and Pending Returns.
* **Book Catalog Search & Filter**: Search books by title, author name, or ISBN, and filter by categories (Programming, Database, Web Development, Computer Science, Management, General, Other).
* **Book Issue Request**: Issue available book copies with automated stock deduction. Prevents issuing out-of-stock books or issuing duplicate active copies of the same book.
* **My Books History**: Track active issued books, due dates, return dates, and clear overdue indicators.

### Admin Features
* **Admin Login**: Secure login with sample admin credentials (`admin` / `admin123`).
* **Admin Control Dashboard**: Displays key metric cards (Total Books, Total Students, Currently Issued, Returned Books, Overdue Books).
* **Book Management**: Add new books, edit details/stock levels, and delete books. Validates that available copies cannot exceed total copies or go negative.
* **Issue & Return Management**: View all student issue logs, search records, filter by status (Issued, Returned, Overdue), and mark books as returned to replenish available stock.
* **Student Directory**: View all registered student profiles and manage accounts.

---

## 🛠️ Tech Stack & Prerequisites

* **Backend**: Python (Flask Framework, Flask-SQLAlchemy)
* **Frontend**: HTML5, CSS3, JavaScript, Bootstrap 5, Bootstrap Icons
* **Database**: MySQL (via XAMPP phpMyAdmin) or SQLite (for quick local development)
* **Server**: XAMPP / Apache / MySQL
* **Editor**: Visual Studio Code (VS Code)

---

## 🚀 Setup & Installation Guide

### Step 1: XAMPP & Database Setup (MySQL)
1. Start **XAMPP Control Panel**.
2. Click **Start** for both **Apache** and **MySQL**.
3. Open your web browser and navigate to `http://localhost/phpmyadmin`.
4. Click on **Databases** -> Create a new database named `college_library_db`.
5. Click on `college_library_db` -> Go to the **Import** tab.
6. Choose the `database.sql` file from this project root folder and click **Import**.

### Step 2: Open in VS Code & Setup Python Environment
1. Open Visual Studio Code and open the project folder (`college_library`).
2. Open a Terminal in VS Code (`Ctrl + ~` or `Terminal -> New Terminal`).
3. (Optional) Create and activate a virtual environment:
   ```bash
   python -m venv venv
   # On Windows:
   venv\Scripts\activate
   # On macOS/Linux:
   source venv/bin/activate
   ```
4. Install required Python packages:
   ```bash
   pip install -r requirements.txt
   ```

---

## 🏃 Running the Application

### Option A: Run with MySQL (Default)
Ensure XAMPP MySQL service is running, then execute:
```bash
python app.py
```

### Option B: Run with SQLite (No XAMPP required for testing/demo)
If you do not have MySQL running or want to run quick tests:
```bash
# On Windows PowerShell:
$env:USE_SQLITE="1"; python app.py

# On Linux / macOS / Bash:
USE_SQLITE=1 python app.py
```

Open your browser and visit: `http://127.0.0.1:5000`

---

## 🔑 Login Credentials

### Default Admin Login
* **Username**: `admin`
* **Password**: `admin123`

### Sample Student Login
You can register a new student account directly from the **Register** page on the navigation bar, or use any newly registered account.

---

## 🧪 Running Unit Tests

Run automated tests using SQLite in-memory database:
```bash
USE_SQLITE=1 python3 -m unittest test_app.py
```

---

## 📁 Project Directory Structure

```
college_library/
│
├── app.py                  # Main Flask application logic & database routes
├── database.sql            # Complete MySQL database schema & sample seed data
├── requirements.txt        # Required Python packages
├── test_app.py             # Unit testing suite
├── README.md               # Project setup & usage guide
│
├── static/
│   ├── css/
│   │   └── style.css       # Custom Royal Blue, Mint Green, and Orange styling
│   └── js/
│       └── script.js       # Auto-dismiss alerts, confirmation modals, table search
│
└── templates/
    ├── base.html           # Common layout template with Bootstrap 5 navbar & footer
    ├── index.html          # Landing homepage
    ├── register.html       # Student Registration page
    ├── login.html          # Student Login page
    ├── admin_login.html    # Admin Login page
    ├── student_dashboard.html # Student Dashboard metrics & recent activity
    ├── books.html          # Book Catalog & Issue portal with search/filters
    ├── my_books.html       # Student's personal book issue history
    ├── admin_dashboard.html# Admin Dashboard metrics & system overview
    ├── manage_books.html   # Admin Book list and controls
    ├── add_book.html       # Form to add a new book
    ├── edit_book.html      # Form to edit existing book details
    ├── issue_records.html  # Admin Issue & Return logs & return processing
    └── manage_students.html# Admin view of registered students
```

---

## 📜 Simple Project Workflow

```
Student Register ➔ Login ➔ View Book Catalog ➔ Issue Available Book ➔ View My Books ➔ Admin Marks Return
```
