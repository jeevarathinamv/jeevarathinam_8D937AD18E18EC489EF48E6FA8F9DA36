# College Academic Calendar Management System

A simple, clean, and responsive web application designed for colleges to manage and publish academic calendars, exam schedules, events, seminars, workshops, and holidays. Built using **Python Flask**, **MySQL**, **Flask-SQLAlchemy**, and **Bootstrap 5**.

This project is tailored specifically as a **Master of Computer Applications (MCA)** academic demonstration project.

---

## 🌟 Key Features

### 👨‍🎓 Student Portal
- **Registration & Login**: Secure student signup with Name, Register Number, Department, Email, and Password.
- **Student Dashboard**: Real-time overview showing Total Events, Today's Events, Upcoming Events, and current semester information.
- **Academic Calendar**: Browse all college events in a clean table view.
- **Event Filtering**: Filter events seamlessly by Event Type, Department, Semester, and Month.
- **Event Highlights**: Today's events and upcoming events are visually highlighted with Bootstrap badges and cards.

### 👨‍💼 Administrator Portal
- **Admin Dashboard**: Overview of total students registered, total events, today's events, and upcoming events.
- **Event Management**: Complete CRUD operations (Add, View, Edit, Delete) for academic events.
- **Student Management**: View registered students with Name, Register Number, Department, and Email, with options to delete student records if required.
- **Search Functionality**: Quickly search events and students.

---

## 🎨 Design & Color Theme

- **Palette**: Teal (`#0d9488`), Royal Blue (`#1d4ed8`), and Peach (`#fdba74` / `#f97316`).
- **UI Components**: Bootstrap 5 cards, badge tags, responsive navigation bar, modern modals, and Bootstrap Icons.

---

## 🛠️ Technology Stack

- **Frontend**: HTML5, CSS3, Bootstrap 5, Bootstrap Icons, JavaScript
- **Backend**: Python 3, Flask Web Framework
- **Database**: MySQL (via XAMPP / phpMyAdmin)
- **ORM**: Flask-SQLAlchemy & PyMySQL
- **Editor**: Visual Studio Code (VS Code)

---

## 📋 Default Credentials

- **Admin Username**: `admin`
- **Admin Password**: `admin123`

---

## 🚀 Setup & Execution Guide

### 1. Database Setup in XAMPP / phpMyAdmin

1. Open **XAMPP Control Panel** and start **Apache** and **MySQL** modules.
2. Open your web browser and navigate to `http://localhost/phpmyadmin/`.
3. Click on the **SQL** tab.
4. Import or run the SQL script provided in `database.sql`:
   ```sql
   CREATE DATABASE IF NOT EXISTS `academic_calendar_db`;
   USE `academic_calendar_db`;
   ```
   *(Or simply run the entire contents of `database.sql` to initialize database tables and seed sample academic events).*

---

### 2. Required Python Packages

Install all required dependencies using `pip`:

```bash
pip install -r requirements.txt
```

Required packages in `requirements.txt`:
- `Flask>=3.0.0`
- `Flask-SQLAlchemy>=3.1.0`
- `PyMySQL>=1.1.0`

---

### 3. How to Run the Project in VS Code

1. Open **VS Code**.
2. Go to **File -> Open Folder** and select the `college_academic_calendar` root folder.
3. Open a built-in terminal in VS Code (`Ctrl + ~` or `Terminal -> New Terminal`).
4. (Optional) Create and activate a Python virtual environment:
   ```bash
   python -m venv venv
   # On Windows:
   venv\Scripts\activate
   # On macOS/Linux:
   source venv/bin/activate
   ```
5. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
6. Run the Flask application:
   ```bash
   python app.py
   ```
   *(Note: To test with SQLite database without MySQL, set `USE_SQLITE=1 python app.py`)*
7. Open your web browser and go to:
   ```
   http://127.0.0.1:5000/
   ```

---

## 📁 Project Directory Structure

```text
college_academic_calendar/
│
├── app.py                  # Main Flask backend application & routes
├── database.sql            # MySQL Database schema & initial seed data
├── requirements.txt        # Python package dependencies
├── test_app.py             # Automated unit tests
├── README.md               # Complete project documentation
│
├── templates/              # HTML Templates (Bootstrap 5)
│   ├── base.html           # Base layout template
│   ├── index.html          # Public landing page
│   ├── register.html       # Student registration page
│   ├── login.html          # Student login page
│   ├── student_dashboard.html # Student dashboard
│   ├── calendar.html       # Academic calendar & filters
│   ├── event_details.html  # Single event details view
│   ├── admin_login.html    # Admin login portal
│   ├── admin_dashboard.html# Admin dashboard
│   ├── manage_events.html  # Admin event management table
│   ├── add_event.html      # Add event form
│   ├── edit_event.html     # Edit event form
│   └── manage_students.html# Admin student management table
│
└── static/
    ├── css/
    │   └── style.css       # Custom styles & Teal + Royal Blue + Peach theme
    └── js/
        └── script.js       # Client-side scripts & form helpers
```

---

## 🧪 Running Unit Tests

Run the unit test suite using SQLite in-memory database:

```bash
USE_SQLITE=1 python3 -m unittest test_app.py
```

---

## 🎓 Author & Credits

Designed & Developed as an **MCA Academic Project Demo** for College Academic Management.
