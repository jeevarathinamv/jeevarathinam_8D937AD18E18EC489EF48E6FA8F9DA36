# Student Attendance & Shortage Alert System

A simple, beginner-friendly web application built with **Python Flask**, **Bootstrap 5**, and **MySQL (XAMPP)** designed to help educational institutions manage daily student attendance, track percentages, and generate automated **Shortage Alerts (<75%)**.

---

## 🎨 Theme & Features

- **Color Theme:** Vibrant Green (`#198754`), Teal (`#008080`), and Yellow (`#FFC107`) theme with colorful gradients, card shadows, and rounded corners.
- **Shortage Alert:** Automatically calculates attendance percentage:
  - **Below 75%:** Displays a prominent yellow/red/orange warning card: `⚠ Attendance Shortage Alert! Your attendance is below 75%. Please improve your attendance.`
  - **75% or Above:** Displays a green banner card: `✓ Attendance is Satisfactory`.
- **Student Module:** Student registration, login, dashboard with class summary, and subject-filtered attendance report.
- **Admin Module:** Admin login, view registered students, mark attendance by subject & date, view overall attendance stats, and view students facing attendance shortages.

---

## 🛠️ Tech Stack & Prerequisites

- **Frontend:** HTML5, CSS3, Bootstrap 5, Bootstrap Icons
- **Backend:** Python 3.x, Flask, Flask-SQLAlchemy, PyMySQL
- **Database:** MySQL (XAMPP / phpMyAdmin)
- **Editor:** VS Code

---

## 📂 Project Structure

```
.
├── app.py                     # Main Flask Application & Routes
├── database.sql               # MySQL Database Schema & Initial Admin Seed
├── requirements.txt           # Python Dependencies
├── test_app.py                # Unit Test Suite
├── README.md                  # Instructions & Documentation
├── static/
│   └── style.css              # Custom Theme & Gradient Styling
└── templates/
    ├── base.html              # Base Layout Template
    ├── index.html             # Landing Page
    ├── register.html          # Student Registration
    ├── login.html             # Student Login
    ├── admin_login.html       # Admin Login
    ├── student_dashboard.html # Student Dashboard & Shortage Alert
    ├── attendance_report.html # Student Attendance Log & Filter
    ├── attendance.html        # Admin Mark Attendance
    └── admin_dashboard.html   # Admin Overview & Shortage Alerts List
```

---

## 📋 Simple Setup & Running Instructions

### 1. XAMPP MySQL Setup
1. Download and install **XAMPP** from [apachefriends.org](https://www.apachefriends.org/).
2. Open the **XAMPP Control Panel** and start the **Apache** and **MySQL** services.

### 2. Database Import
1. Open your browser and navigate to `http://localhost/phpmyadmin`.
2. Click on the **SQL** tab or create a database named `student_attendance`.
3. Import or execute the contents of `database.sql`:
   - Click **Import** -> Choose file `database.sql` -> Click **Go**.
   - *Or* copy all SQL queries from `database.sql` and run them inside the SQL editor.

### 3. VS Code & Python Setup
1. Open **VS Code** and open the project directory (`File > Open Folder...`).
2. Open a terminal in VS Code (`Ctrl + ~` or `Terminal > New Terminal`).
3. Create and activate a virtual environment (optional but recommended):
   ```bash
   python -m venv venv
   # On Windows:
   venv\Scripts\activate
   # On macOS/Linux:
   source venv/bin/activate
   ```

### 4. Install Dependencies
Run the following command in your terminal to install Flask and SQLAlchemy:
```bash
pip install -r requirements.txt
```

### 5. Running the Application
Run the Flask server:
```bash
python app.py
```
Open your web browser and visit: **`http://127.0.0.1:5000/`**

---

## 🔑 Default Admin Credentials

- **Username:** `admin`
- **Password:** `admin123`

---

## 🧪 Running Unit Tests (Optional)

To test the application without requiring a running MySQL server, run:
```bash
USE_SQLITE=1 python -m unittest test_app.py
```
