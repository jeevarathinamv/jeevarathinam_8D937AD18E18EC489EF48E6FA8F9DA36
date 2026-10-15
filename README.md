# College Attendance & Internal Mark Management System

A colorful, modern, and responsive web application designed for MCA mini-project demonstrations. Built using Python Flask, MySQL, PyMySQL, HTML5, CSS3, Bootstrap 5, and JavaScript (Chart.js).

---

## 🌟 Key Features

1. **4 Distinct User Roles**:
   - **Admin / Staff**: Manage Students, Teachers, Classes (BCA I, BCA II, BCA III, MCA I, MCA II), Subjects, Timetables, Class Tutors, Internal Mark Rules, and Comprehensive Reports.
   - **Teacher**: View assigned daily timetable, select timetable hours, mark student attendance (Present/Absent), submit sessions, and view submission history.
   - **Class Tutor**: Exclusive dashboard for assigned class, student-wise & subject-wise percentage reports, internal mark out of 5, RA student alerts (< 50%), and CSV exports.
   - **Student**: View individual attendance summary, subject-wise progress bars, calculated internal attendance marks out of 5, and eligibility status.

2. **Automatic Attendance & Internal Mark Calculations**:
   - **Attendance Percentage** = `(Present Hours / Total Hours) × 100`
   - **Internal Attendance Marks (Out of 5 Rules)**:
     - 90% and above: **5 Marks**
     - 80% to below 90%: **4 Marks**
     - 70% to below 80%: **3 Marks**
     - 60% to below 70%: **2 Marks**
     - 50% to below 60%: **1 Mark**
     - Below 50%: **RA (Redo Attendance)**

3. **Timetable & Validation Rules**:
   - Manages 5 classes with 5 hours per working day.
   - Prevents duplicate class-hour timetable entries and overlapping teacher schedule assignments.

4. **Modern UI/UX**:
   - Modern color theme featuring **Royal Blue**, **Purple**, **Cyan**, **Mint Green**, and **Light Lavender**.
   - Responsive Bootstrap 5 layout with glassmorphism cards, gradient buttons, badges, progress bars, and Chart.js graphs.

---

## 🔑 Demo Login Credentials

| Role | Username / ID | Password | Access / Notes |
|---|---|---|---|
| **Admin** | `admin` | `admin123` | Full System Control & Setup |
| **Teacher** | `TCH101` | `teacher123` | Dr. Aris Thorne (Teacher) |
| **Class Tutor** | `TCH104` | `teacher123` | Prof. Elena Rostova (Tutor for MCA I) |
| **Student (MCA I)** | `2024MCA001` | `student123` | Guido van Rossum |
| **Student (BCA I)** | `2024BCA001` | `student123` | Alan Turing |

---

## 🛠️ Technology Stack

- **Frontend**: HTML5, CSS3, Bootstrap 5, FontAwesome 6, Chart.js, JavaScript (ES6)
- **Backend**: Python Flask
- **Database**: MySQL (PyMySQL) with SQLite fallback support
- **ORM**: Flask-SQLAlchemy
- **Server**: XAMPP / Apache / Gunicorn / Flask Dev Server
- **Code Editor**: VS Code

---

## 🚀 Setup & Installation Instructions (XAMPP & VS Code)

### Step 1: Install Prerequisites
1. Download & install **Python 3.10+**.
2. Download & install **XAMPP Control Panel**.
3. Install **VS Code**.

### Step 2: Start MySQL Server via XAMPP
1. Open **XAMPP Control Panel**.
2. Click **Start** next to **MySQL** (and Apache if using phpMyAdmin).

### Step 3: Database Import using phpMyAdmin / MySQL
1. Open your browser and navigate to `http://localhost/phpmyadmin/`.
2. Click **Databases** -> Create a new database named `college_attendance_db`.
3. Click **Import** -> Choose the `database.sql` file provided in the project root directory -> Click **Go**.

### Step 4: Open Project in VS Code & Environment Setup
1. Open VS Code and open the project directory.
2. Open terminal in VS Code (`Ctrl + ~`) and install required packages:
   ```bash
   pip install -r requirements.txt
   ```

### Step 5: Configure Database Connection
By default, the application connects to MySQL using:
`mysql+pymysql://root:@localhost/college_attendance_db`

*(Note: To run in standalone SQLite test mode without MySQL, set `USE_SQLITE=1` in your environment).*

### Step 6: Run the Flask Application
Run the application using Python:
```bash
python app.py
```
Or for SQLite test mode:
```bash
USE_SQLITE=1 python app.py
```

Open your browser and navigate to:
`http://127.0.0.1:5000/`

---

## 📂 Project Structure

```
├── app.py                  # Main Flask backend application & routes
├── database.sql            # Complete MySQL database schema & sample seed data
├── requirements.txt        # Python package dependencies
├── README.md               # Project documentation & setup guide
├── test_app.py             # Unit test suite
├── static/
│   ├── css/
│   │   └── style.css       # Custom modern responsive theme stylesheet
│   └── js/
│       └── script.js       # Dynamic UI scripts & search filters
└── templates/              # HTML Jinja2 templates
    ├── base.html
    ├── login.html
    ├── admin_dashboard.html
    ├── teacher_dashboard.html
    ├── mark_attendance.html
    ├── tutor_dashboard.html
    ├── student_dashboard.html
    └── reports.html
```
