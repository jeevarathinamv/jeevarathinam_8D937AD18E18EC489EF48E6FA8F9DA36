# College Digital Library Management Portal

A simple, modern, and beginner-friendly web portal for managing college digital library resources, e-books, and study materials. Built with **Python Flask**, **Bootstrap 5**, and **MySQL (XAMPP)**.

---

## 🎨 Color Theme & UI Design
- **Primary / Headers:** Dark Blue (`#0f172a`, `#1e293b`)
- **Accent & Secondary:** Cyan (`#06b6d4`, `#e0f2fe`)
- **Highlight & Actions:** Light Orange (`#f97316`)
- **Framework:** Bootstrap 5 Cards, Tables, Buttons & Navbar

---

## 🚀 Key Modules & Features

### 1. Student Portal
- **Registration & Login:** Student Name, Register Number, Department, Email, Password. Password hashing (`werkzeug.security`) and session management.
- **Student Dashboard:** View Total Books, Available Books, My Downloads count, and quick links.
- **Digital Books Catalog:** Search by keyword (title, author, description) and filter by category (*Programming, Database, Web Development, Computer Science, Management, General, Other*).
- **Book Details & PDF Viewer:** View book information, view PDF inline in browser, or download PDF file directly.
- **My Downloads:** View personal download history (Book Name, Download Date & Time).

### 2. Admin Portal
- **Admin Authentication:** Secure login for library administrators (`admin` / `admin123`).
- **Admin Dashboard:** Real-time statistics (Total Students, Total Books, Available Books, Total Downloads), Student Registry List, and Download Logs.
- **Digital Book Management:** Add new books with PDF file upload validation (`.pdf` extension limit, unique filename generation), Edit existing books, Delete books, and View all uploaded books.

---

## 🗄️ Database Tables (MySQL)
1. `admins` - Admin credentials & account data
2. `students` - Student registration details
3. `books` - Digital book metadata & PDF filenames
4. `downloads` - Automated download history tracking

---

## 💻 Tech Stack & Requirements
- **Frontend:** HTML5, CSS3, Bootstrap 5, JavaScript
- **Backend:** Python 3 (Flask)
- **Database:** MySQL (PyMySQL / SQLAlchemy) or SQLite fallback
- **Server:** XAMPP (Apache + MySQL) / phpMyAdmin
- **Editor:** VS Code

---

## 🛠️ XAMPP & phpMyAdmin Setup Instructions

1. **Start XAMPP Control Panel:**
   - Launch XAMPP and start **Apache** and **MySQL** services.

2. **Open phpMyAdmin:**
   - Open browser and navigate to `http://localhost/phpmyadmin/`.

3. **Import Database Schema:**
   - Click on **Databases** tab and create a database named `college_library_db`.
   - Select `college_library_db` and click **Import**.
   - Choose the `database.sql` file from the project root folder and click **Go**.

---

## ⚙️ How to Run in VS Code

1. **Open Project in VS Code:**
   ```bash
   code .
   ```

2. **Install Python Dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

3. **Default Admin Credentials:**
   - **Username:** `admin`
   - **Password:** `admin123`

4. **Run the Flask Application:**
   ```bash
   python app.py
   ```
   Or with SQLite fallback (no MySQL setup required for quick local testing):
   ```bash
   USE_SQLITE=1 python app.py
   ```

5. **Open Application in Browser:**
   - Visit `http://127.0.0.1:5000/`

---

## 🧪 Running Unit Tests
```bash
USE_SQLITE=1 python3 -m unittest test_app.py
```
