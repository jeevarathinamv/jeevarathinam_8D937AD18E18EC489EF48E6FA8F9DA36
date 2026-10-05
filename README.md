# Library New Book Request System

A simple, beginner-friendly web application built with **Python Flask**, **Bootstrap 5**, and **MySQL** for managing library book requests submitted by students.

---

## 🎨 Design Theme
- **Color Palette**: Purple (`#6f42c1`), Blue (`#0d6efd`), and Orange (`#fd7e14`).
- Clean, responsive, and easy-to-demonstrate interface for college project demonstrations.

---

## 🚀 Key Features

### Student Module
- **Registration & Login**: Secure authentication with password hashing using Flask Session.
- **Student Dashboard**: Stat cards showing Total, Pending, Approved, and Rejected requests.
- **Request New Book**: Request a book by entering Book Name, Author, Category, Reason, and generating a unique Request ID (e.g. `REQ-849201`).
- **My Book Requests**: View personal requests, status badges, and admin remarks.
- **Request Details**: View comprehensive request breakdown.

### Admin Module
- **Admin Dashboard**: Stat cards for Total Students, Total Requests, Pending, Approved, and Rejected counts.
- **Manage Requests**: Search by Request ID, Book Name, or Student Name; filter by Status (`Pending`, `Approved`, `Rejected`).
- **Approve / Reject Requests**: Update status with custom admin remarks (e.g., *"Book will be purchased soon."* or *"Book is already available in the library."*).
- **Delete Request**: Remove unnecessary or redundant request entries.

---

## 🔑 Default Credentials

### Admin Login
- **URL**: `http://127.0.0.1:5000/admin/login`
- **Username**: `admin`
- **Password**: `admin123`

---

## 🛠️ Setup Instructions (XAMPP & MySQL)

1. **Start XAMPP**:
   - Open XAMPP Control Panel.
   - Start **Apache** and **MySQL** services.

2. **Database Setup via phpMyAdmin**:
   - Open browser and navigate to `http://localhost/phpmyadmin/`.
   - Click on the **SQL** tab.
   - Copy and paste the contents of `database.sql` from this repository and click **Go**.
   - This creates the `library_db` database along with `admins`, `students`, and `book_requests` tables.

---

## 💻 Running in VS Code

1. **Open Project**:
   - Open VS Code and open the `library_book_request` folder.

2. **Set up Virtual Environment & Install Dependencies**:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   pip install -r requirements.txt
   ```

3. **Run Application**:
   ```bash
   python app.py
   ```
   *For SQLite fallback mode (if XAMPP MySQL is not active):*
   ```bash
   USE_SQLITE=1 python app.py
   ```

4. **Access in Browser**:
   - Web application runs at: `http://127.0.0.1:5000/`

---

## 📁 Project Structure

```text
library_book_request/
│
├── app.py
├── database.sql
├── requirements.txt
├── README.md
│
├── templates/
│   ├── base.html
│   ├── index.html
│   ├── register.html
│   ├── login.html
│   ├── student_dashboard.html
│   ├── request_book.html
│   ├── my_requests.html
│   ├── request_details.html
│   ├── admin_login.html
│   ├── admin_dashboard.html
│   └── manage_requests.html
│
└── static/
    ├── css/
    │   └── style.css
    └── js/
        └── script.js
```
