# Student Exam Timetable Management System

A simple, modern, and beginner-friendly web application built for MCA (Master of Computer Applications) student academic project demonstration. The system allows administrators to manage exam schedules and enables students to register, log in, and view filtered exam timetables with upcoming exam tracking.

---

## 🎨 Color Theme & Tech Stack

- **Design Theme:** Blue + Purple + Mint Green
- **Frontend:** HTML5, CSS3, Bootstrap 5, Bootstrap Icons, JavaScript
- **Backend:** Python (Flask Web Framework)
- **Database:** MySQL / XAMPP phpMyAdmin (with SQLite fallback mode for quick testing)
- **ORM:** Flask-SQLAlchemy
- **Editor:** VS Code

---

## 🔑 Default Admin Credentials

- **Username:** `admin`
- **Password:** `admin123`

---

## 🔄 Simple Project Flow

1. **Admin Login** → Log in using `admin` / `admin123`.
2. **Add Exam Timetable** → Create new exam schedules with subject name, subject code, date, time, venue, semester, and department.
3. **Student Registration** → Students register with Name, Register Number, Department, Email, and Password.
4. **Student Login** → Log in using Email/Register Number and Password.
5. **View Exam Timetable** → Filter timetable by Department, Semester, or Exam Name.
6. **Check Upcoming Exams** → View upcoming exam counts, total subjects, and next exam highlight on student dashboard.

---

## 🛠️ Step-by-Step Setup Guide

### 1. Prerequisites & Required Python Packages

Make sure you have Python 3.8+ installed on your computer.

The required Python packages are listed in `requirements.txt`:
- `Flask>=3.0.0`
- `Flask-SQLAlchemy>=3.1.0`
- `PyMySQL>=1.1.0`

Install all dependencies using terminal/command prompt:
```bash
pip install -r requirements.txt
```

---

### 2. XAMPP & phpMyAdmin MySQL Database Setup

1. Open **XAMPP Control Panel**.
2. Start both **Apache** and **MySQL** modules.
3. Open your web browser and navigate to phpMyAdmin:
   ```
   http://localhost/phpmyadmin
   ```
4. Click on **Databases** tab and create a new database named:
   ```sql
   exam_timetable_db
   ```
5. Click on `exam_timetable_db`, go to the **Import** tab, choose the `database.sql` file provided in the project root directory, and click **Import** (or **Go**).

Alternatively, `app.py` automatically initializes database tables and seeds initial sample records on start.

---

### 3. Running the Project in VS Code

1. Open **VS Code**.
2. Go to **File -> Open Folder** and select the project directory.
3. Open the integrated terminal in VS Code (`Ctrl + ~` or `Terminal -> New Terminal`).
4. (Optional) Create and activate a virtual environment:
   ```bash
   python -m venv venv
   source venv/bin/activate    # On Linux/macOS
   # OR
   venv\Scripts\activate       # On Windows
   ```
5. Run the Flask application:
   ```bash
   python app.py
   ```
6. Open your browser and go to:
   ```
   http://127.0.0.1:5000
   ```

> **Note for Quick Demo/Testing without MySQL:**
> You can run the project using SQLite in-memory/file mode by setting the `USE_SQLITE=1` environment variable:
> ```bash
> USE_SQLITE=1 python app.py
> ```

---

## 📂 Project Directory Structure

```
student_exam_timetable/
│
├── app.py                     # Main Flask Application
├── database.sql               # MySQL Schema & Seed Data
├── requirements.txt           # Python Package Dependencies
├── test_app.py                # Automated Unit Test Suite
├── README.md                  # Project Documentation
│
├── templates/
│   ├── base.html              # Shared Navigation & Footer Layout
│   ├── index.html             # Landing Homepage
│   ├── register.html          # Student Registration Page
│   ├── login.html             # Student Login Page
│   ├── student_dashboard.html # Student Dashboard & Metrics
│   ├── timetable.html         # Timetable Search & Filter View
│   ├── admin_login.html       # Administrator Login Page
│   ├── admin_dashboard.html   # Admin Overview & Student Directory
│   ├── manage_timetable.html  # Admin Timetable CRUD List
│   ├── add_exam.html          # Admin Add Exam Form
│   └── edit_exam.html         # Admin Edit Exam Form
│
└── static/
    ├── css/
    │   └── style.css          # Theme Styles (Blue, Purple, Mint Green)
    └── js/
        └── script.js          # Bootstrap Form Validation JS
```

---

## 🧪 Running Unit Tests

Execute the unit test suite:
```bash
USE_SQLITE=1 python3 -m unittest test_app.py
```
