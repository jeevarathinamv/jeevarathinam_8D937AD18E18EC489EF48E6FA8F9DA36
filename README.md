# Classroom Maintenance Complaint Tracker

A simple, beginner-friendly web application developed for **MCA (Master of Computer Applications)** students to manage and track classroom maintenance issues (such as fan, light, desk, window, projector, AC problems).

---

## 🌟 Key Features

1. **Student Registration & Authentication**:
   - Register with Name, Register Number, Department, Email, and Password.
   - Secure login using Register Number or Email with hashed passwords (`Werkzeug`).
   - Active session management using Flask session.

2. **Student Dashboard & Complaint Reporting**:
   - Real-time complaint stats: Total, Pending, In Progress, and Resolved.
   - Easy complaint submission for classroom/lab maintenance issues.
   - Automatic generation of unique Complaint IDs (e.g. `CMP-A1B2C3`).

3. **My Complaints**:
   - Isolated complaint tracking: Students can view and track only their own reported complaints.
   - Detailed complaint view with admin remarks and resolution dates.

4. **Admin Dashboard & Complaint Management**:
   - Overview of total students and complaint statistics.
   - Search complaints by Complaint ID, Classroom Number, Student Name, or Register Number.
   - Filter complaints by status (`Pending`, `In Progress`, `Resolved`, `Rejected`).
   - Update complaint status and append administrative remarks.
   - Status workflow: `Pending` → `In Progress` → `Resolved` (auto-records resolved date) or `Rejected`.
   - Option to delete records if needed.

---

## 🛠️ Technology Stack

- **Frontend**: HTML5, CSS3, JavaScript, Bootstrap 5, FontAwesome 6
- **Backend**: Python Flask
- **Database**: MySQL (PyMySQL) with SQLAlchemy ORM (supports SQLite fallback)
- **Server**: XAMPP / Apache + MySQL
- **Editor**: VS Code

---

## 🎨 Color Theme & Design

- **Primary Blue**: `#0d6efd`
- **Accent Orange**: `#fd7e14`
- **Light Green**: `#20c997`
- Responsive, clean, and intuitive user interface built with Bootstrap 5 cards, tables, badges, and modals.

---

## 🗄️ Database Tables Structure

The system uses three simple relational tables (`classroom_maintenance_db`):

1. **`admins`**: Stores admin credentials (`id`, `username`, `password_hash`, `created_at`).
2. **`students`**: Stores registered student profiles (`id`, `name`, `register_number`, `department`, `email`, `password_hash`, `created_at`).
3. **`complaints`**: Stores submitted complaints (`id`, `complaint_id`, `student_id`, `classroom_number`, `complaint_type`, `description`, `complaint_date`, `status`, `admin_remarks`, `resolved_date`, `created_at`).

---

## 🔑 Sample Admin Credentials

- **Username**: `admin`
- **Password**: `admin123`

*(Note: Default admin account is automatically created upon starting the application if not already present).*

---

## 🚀 Setup & Execution Guide

### 1. XAMPP & phpMyAdmin Setup (MySQL)

1. Open **XAMPP Control Panel** and start **Apache** and **MySQL** services.
2. Open your web browser and go to `http://localhost/phpmyadmin/`.
3. Click on the **SQL** tab.
4. Copy the contents of `database.sql` into the SQL editor and click **Go**.
   - This creates the database `classroom_maintenance_db` and the required tables (`admins`, `students`, `complaints`).

### 2. VS Code & Application Run Steps

1. Open the project folder (`classroom_maintenance`) in **VS Code**.
2. Open a Terminal (`Ctrl + ~` or `Terminal -> New Terminal`).
3. (Optional) Create and activate a virtual environment:
   ```bash
   python3 -m venv venv
   source venv/bin/activate        # On Linux/macOS
   # OR
   venv\Scripts\activate           # On Windows
   ```
4. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
5. Run the Flask application:
   ```bash
   python app.py
   ```
6. Open your web browser and visit: `http://127.0.0.1:5000/`

---

## 🧪 Testing with SQLite (Optional Environment)

To quickly test or demonstrate without MySQL running:
```bash
USE_SQLITE=1 python app.py
```
To run unit tests:
```bash
USE_SQLITE=1 python -m unittest test_app.py
```

---

## 📁 Project Structure

```
classroom_maintenance/
│
├── app.py                  # Core Flask backend application logic & models
├── database.sql            # MySQL schema import script
├── requirements.txt        # Python package dependencies
├── test_app.py             # Automated unit tests
├── README.md               # Project documentation & setup guide
│
├── templates/              # HTML Templates (Bootstrap 5)
│   ├── base.html
│   ├── index.html
│   ├── register.html
│   ├── login.html
│   ├── student_dashboard.html
│   ├── report_complaint.html
│   ├── my_complaints.html
│   ├── complaint_details.html
│   ├── admin_login.html
│   ├── admin_dashboard.html
│   └── manage_complaints.html
│
└── static/                 # Static Assets
    ├── css/
    │   └── style.css       # Custom Blue, Orange & Light Green theme styles
    └── js/
        └── script.js       # Client-side JavaScript helpers
```
