# Lab Computer Fault Reporting System

A clean, responsive, and beginner-friendly web application developed using **Python Flask**, **MySQL**, **Bootstrap 5**, **HTML**, and **CSS**. This project provides a centralized platform for college students to report laboratory computer hardware and software issues, and for administrators to manage complaints, computers, and student records.

---

## 🚀 Key Features

### 👨‍🎓 Student Portal
- **Student Registration & Login**: Secure password hashing with Werkzeug and Flask session management.
- **Student Dashboard**: Stat cards showing Total, Pending, In Progress, and Resolved fault reports.
- **Report Fault**: Submit fault reports with automatic, unique Complaint ID generation (e.g., `CMP-20250520-1234`).
  - Fault types: *Computer Not Starting*, *Keyboard Problem*, *Mouse Problem*, *Monitor Problem*, *Internet Problem*, *Software Problem*, *Other*.
- **My Reports**: View list of submitted complaints with real-time status and admin remarks.
- **Fault Details**: Full view of submitted complaint, student info, problem description, status, admin remarks, and resolved date.

### 🛡️ Admin Portal
- **Admin Dashboard**: Visual dashboard metrics for Total Reports, Pending, In Progress, and Resolved complaints.
- **Fault Report Management**:
  - View all student fault reports.
  - Search and filter by **Complaint ID**, **Computer Number**, **Lab Name**, **Fault Type**, and **Status**.
  - Update complaint status (`Pending` → `In Progress` → `Resolved`, or `Pending` → `Rejected`).
  - Add admin remarks and automatically record the resolution date upon resolving.
- **Computer Management**: Add, Edit, Delete, and View lab computers (Computer No, Lab Name, Computer Model, IP Address, Status).
- **Student Management**: View registered students and delete accounts if required.

---

## 🛠️ Technology Stack

- **Frontend**: HTML5, CSS3, Bootstrap 5, Bootstrap Icons, JavaScript
- **Backend**: Python 3 (Flask Framework)
- **Database**: MySQL (XAMPP / phpMyAdmin) or SQLite fallback
- **ORM**: Flask-SQLAlchemy & PyMySQL
- **Editor**: Visual Studio Code (VS Code)

---

## 📁 Project Directory Structure

```text
lab_computer_fault/
│
├── app.py                     # Main Flask Application
├── database.sql               # MySQL Database Schema & Seed Data
├── requirements.txt           # Python Dependencies
├── test_app.py                # Automated Unit Tests
├── README.md                  # Setup & Demonstration Guide
│
├── static/
│   ├── css/
│   │   └── style.css          # Theme Stylesheet (Electric Blue, Teal, Orange)
│   └── js/
│       └── script.js          # Interactive JavaScript
│
└── templates/
    ├── base.html              # Base layout with navbar & footer
    ├── index.html             # Landing homepage
    ├── register.html          # Student Registration
    ├── login.html             # Student Login
    ├── student_dashboard.html # Student Dashboard
    ├── report_fault.html      # Fault Reporting Form
    ├── my_reports.html        # Student Reports List
    ├── fault_details.html     # Fault Detail View
    ├── admin_login.html       # Admin Login
    ├── admin_dashboard.html   # Admin Dashboard
    ├── manage_reports.html    # Admin Fault Management (Search & Filter)
    ├── manage_computers.html  # Computer Management
    ├── add_computer.html      # Add Computer Form
    ├── edit_computer.html     # Edit Computer Form
    └── manage_students.html   # Student Management
```

---

## 🔑 Default Credentials

### Administrator Account
- **URL**: `http://127.0.0.1:5000/admin/login`
- **Username**: `admin`
- **Password**: `admin123`

---

## 💻 Installation & Setup Guide

### 1. Database Setup in XAMPP (phpMyAdmin)
1. Open **XAMPP Control Panel** and start **Apache** and **MySQL** services.
2. Open your web browser and navigate to `http://localhost/phpmyadmin/`.
3. Click on the **SQL** tab.
4. Open the `database.sql` file in this project repository, copy its contents, paste them into the phpMyAdmin SQL query box, and click **Go**.
5. This creates the `lab_computer_fault_db` database along with tables (`admins`, `students`, `computers`, `fault_reports`) and default sample data.

---

### 2. Setting Up Python Environment in VS Code
1. Open Visual Studio Code and select **File > Open Folder...**, then select the project folder.
2. Open a new Terminal in VS Code (`Ctrl + ~` or **Terminal > New Terminal**).
3. (Optional) Create and activate a Python virtual environment:
   ```bash
   python -m venv venv
   # Windows:
   venv\Scripts\activate
   # macOS/Linux:
   source venv/bin/activate
   ```
4. Install all required dependencies:
   ```bash
   pip install -r requirements.txt
   ```

---

### 3. Running the Application

To run the app with MySQL (XAMPP running):
```bash
python app.py
```

To run the app with SQLite fallback (no MySQL/XAMPP required for quick testing):
```bash
# Windows PowerShell:
$env:USE_SQLITE="1"; python app.py

# Linux / macOS / Bash:
USE_SQLITE=1 python app.py
```

Access the application in your browser at:
👉 `http://127.0.0.1:5000`

---

## 🧪 Running Automated Unit Tests

To run the automated unittest suite:
```bash
USE_SQLITE=1 python -m unittest test_app.py
```

---

## 🎯 MCA Demo Workflow

1. **Register a Student**:
   - Go to `http://127.0.0.1:5000/register`.
   - Fill in Student Name, Register Number, Department, Email, and Password.
2. **Student Login & Report Fault**:
   - Login at `http://127.0.0.1:5000/login`.
   - Navigate to **Report Fault**.
   - Select Lab Name, Computer Number, Fault Type (e.g. *Keyboard Problem*), and enter a description.
   - Click **Submit Fault Report** to auto-generate a Complaint ID (e.g., `CMP-20250520-XXXX`).
3. **Admin Review & Resolution**:
   - Login as Admin at `http://127.0.0.1:5000/admin/login` (admin / admin123).
   - Go to **Manage Reports**, search or filter the complaint.
   - Click **Update**, change status from `Pending` → `In Progress` → `Resolved`, and add Admin Remarks.
4. **Verify Status Update**:
   - Log back in as Student and check **My Reports** or **Fault Details** to view updated status, remarks, and resolved timestamp.
