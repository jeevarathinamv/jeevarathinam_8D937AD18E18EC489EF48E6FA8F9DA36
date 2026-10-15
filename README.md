# College Attendance & Internal Mark Management System

A simple, colorful, beginner-friendly MCA mini-project web application built using **Python Flask**, **MySQL**, **XAMPP**, **Bootstrap 5**, and **PyMySQL**.

---

## 🌟 Key Features

1. **5 Supported Classes:**
   - BCA I
   - BCA II
   - BCA III
   - MCA I
   - MCA II
   Each class features assigned students, subjects, timetable schedules, and one assigned **Class Tutor**.

2. **Administrator Portal:**
   - Manage Students (Add, Edit, Delete, View).
   - Manage Teachers & Class Tutors.
   - Manage Subjects mapped to classes.
   - Timetable Management with automatic schedule conflict prevention (duplicate class-hour entries and overlapping teacher assignments).
   - Configurable Internal Mark Rules.

3. **Teacher & Class Tutor Features:**
   - Teacher Login & Today's Timetable view.
   - Hour-by-hour student attendance marking (Present / Absent) with "Mark All Present/Absent" quick action buttons.
   - Attendance Session History.
   - **Class Tutor Dashboard:** Live attendance statistics for assigned class, RA student alert list (< 50% attendance), date & subject filters, and CSV export. Tutors are restricted strictly to their assigned class.

4. **Student Portal:**
   - Student Login using Register Number and Password.
   - Displays Class Name, Total Hours, Present Hours, Absent Hours, and Overall Attendance Percentage.
   - Subject-wise Attendance Breakdown, **Internal Attendance Mark (out of 5)**, and **Eligibility Status** (Eligible vs `RA – Attendance Below 50%`).

5. **Automatic Attendance & Internal Mark Calculations:**
   - Attendance Percentage = `(Present Hours ÷ Total Hours) × 100`
   - Internal Attendance Mark (out of 5):
     - **90% and above:** 5 Marks
     - **80% – below 90%:** 4 Marks
     - **70% – below 80%:** 3 Marks
     - **60% – below 70%:** 2 Marks
     - **50% – below 60%:** 1 Mark
     - **Below 50%:** 0 Marks | **Status:** `RA – Attendance Below 50%`

6. **Comprehensive Reports & CSV Export:**
   - Daily Attendance Report
   - Class-wise Attendance Report
   - Student-wise Attendance Report
   - Subject-wise Attendance Report
   - Monthly Attendance Report
   - Internal Mark Report
   - RA Student Report
   - Export reports to downloadable `.csv` files.

---

## 🎨 Design & Color Theme

Designed with a modern, colorful layout:
- **Royal Blue:** `#1e40af`
- **Purple:** `#7e22ce`
- **Cyan:** `#06b6d4`
- **Mint Green:** `#10b981`
- **Light Lavender Background:** `#f3f0ff`
- Bootstrap 5 cards, tables, progress bars, status badges, and interactive modals.

---

## 🛠️ Technologies Used

- **Frontend:** HTML5, CSS3, Bootstrap 5, Bootstrap Icons, JavaScript
- **Backend:** Python Flask
- **Database:** MySQL (`college_attendance_db`)
- **Database Driver:** PyMySQL & Flask-SQLAlchemy
- **Server Environment:** XAMPP Apache/MySQL
- **Code Editor:** VS Code

---

## 🔑 Sample Login Credentials

| Role | Username / Identifier | Password | Notes / Assigned Class |
|---|---|---|---|
| **Admin** | `admin` | `admin123` | System Administrator |
| **Class Tutor (MCA I)** | `rajesh@college.edu` | `teacher123` | Dr. Rajesh Kumar (TCH101) |
| **Class Tutor (MCA II)** | `sunita@college.edu` | `teacher123` | Prof. Sunita Sharma (TCH102) |
| **Class Tutor (BCA I)** | `anish@college.edu` | `teacher123` | Mr. Anish Verma (TCH103) |
| **Class Tutor (BCA II)** | `priya@college.edu` | `teacher123` | Ms. Priya Nair (TCH104) |
| **Class Tutor (BCA III)** | `suresh@college.edu` | `teacher123` | Dr. Suresh Patel (TCH105) |
| **Student (MCA I - Eligible)** | `23MCA01` | `student123` | Kavitha Ramesh |
| **Student (MCA I - RA Status)** | `23MCA04` | `student123` | Manoj Kumar |
| **Student (BCA I)** | `23BCA01` | `student123` | Aravind Swamy |

---

## 🚀 Step-by-Step Setup Instructions

### 1. Start MySQL in XAMPP
- Open **XAMPP Control Panel**.
- Start the **Apache** and **MySQL** modules.

### 2. Import Database in phpMyAdmin
- Open your browser and go to `http://localhost/phpmyadmin/`.
- Create a new database named `college_attendance_db` (or let `database.sql` create it automatically).
- Click on **Import** -> Choose file `database.sql` -> Click **Go**.

### 3. Open Project in VS Code
- Open VS Code.
- Go to `File > Open Folder...` and select this project directory.

### 4. Install Required Packages
- Open VS Code Terminal (`Ctrl + ~` or `Terminal > New Terminal`).
- (Optional) Create a virtual environment:
  ```bash
  python -m venv venv
  source venv/bin/activate        # On Linux/macOS
  venv\Scripts\activate           # On Windows
  ```
- Install dependencies from `requirements.txt`:
  ```bash
  pip install -r requirements.txt
  ```

### 5. Configure Database Connection
- By default, the app connects to MySQL:
  `mysql+pymysql://root:@localhost/college_attendance_db`
- To run with local SQLite database (for quick offline testing):
  ```bash
  # Linux / macOS
  USE_SQLITE=1 python app.py

  # Windows PowerShell
  $env:USE_SQLITE="1"; python app.py
  ```

### 6. Run the Flask Application
- Run the app using:
  ```bash
  python app.py
  ```
- Open `http://127.0.0.1:5000/` in your web browser.

### 7. Test All User Portals
1. **Admin:** Log in with `admin` / `admin123` to manage students, teachers, subjects, timetables, and rules.
2. **Teacher / Class Tutor:** Log in with `rajesh@college.edu` / `teacher123` to view assigned timetable, mark attendance, and check the Class Tutor dashboard.
3. **Student:** Log in with `23MCA01` / `student123` to view personal attendance stats, internal marks, and eligibility status.

---

## 📁 Project File Structure

```text
├── app.py                     # Main Flask application logic & API routes
├── database.sql               # MySQL database schema & sample seed data
├── requirements.txt           # Python package dependencies
├── test_app.py                # Automated unit tests suite
├── README.md                  # Project documentation & setup guide
├── PROJECT_OVERVIEW.md        # Comprehensive project overview & video demonstration script
├── static/
│   ├── css/
│   │   └── style.css          # Custom styling (Royal Blue, Purple, Cyan, Mint, Lavender)
│   └── js/
│       └── script.js          # Interactive JS helpers & search filters
└── templates/
    ├── base.html              # Base layout with navbar & flash alerts
    ├── index.html             # Homepage / portal introduction
    ├── login.html             # Role selector & login form
    ├── admin_dashboard.html   # Admin overview dashboard
    ├── admin_students.html    # Student CRUD management
    ├── admin_teachers.html    # Teacher & Tutor CRUD management
    ├── admin_subjects.html    # Subject CRUD management
    ├── admin_timetable.html   # Timetable slot CRUD & conflict check
    ├── admin_mark_rules.html  # Configurable internal mark rules out of 5
    ├── teacher_dashboard.html # Teacher timetable & history
    ├── mark_attendance.html   # Attendance marking sheet
    ├── attendance_history.html# Teacher attendance submission history
    ├── tutor_dashboard.html   # Class Tutor private dashboard & RA alert list
    ├── student_dashboard.html # Student personal attendance & internal marks portal
    └── reports.html           # Unified reports generator & CSV export
```

---

## 📜 License & Usage
This project is developed for college mini-project demonstrations and MCA/BCA coursework. Easy to present, customize, and explain during academic evaluations.
