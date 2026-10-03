# Student Assignment Submission & Deadline Tracker

A clean, modern, beginner-friendly web application built with **Python Flask**, **Bootstrap 5**, and **MySQL**. Designed specifically for MCA mini project demonstrations.

---

## 🎨 Features & Modules Overview

### 1. Color & Design Theme
* **Theme Colors**: Heather Purple (`#6a1b9a`), Cyan (`#00bcd4`), and Peach (`#ffab91`).
* **UI Style**: Modern purple/cyan gradient background, rounded cards, soft shadows, cyan highlight buttons, and Bootstrap Icons.
* **Responsiveness**: Fully responsive for desktop, tablet, and mobile browsers.

### 2. Student Module
* **Registration & Login**: Secure signup with Name, Register Number, Department, Email, and Password.
* **Student Dashboard**: Real-time counts for Total Assignments, Pending Submissions, Submitted Assignments, and Upcoming Deadlines.
* **Assignment List**: View assignment titles, subjects, descriptions, given dates, deadline dates, and deadline indicators.
* **Assignment Submission**: Submit answers or GitHub/Drive project links with automatic status detection (`Submitted` vs `Late`).
* **Submission History**: Complete log of all past submissions with timestamps and status badges.
* **Deadline Tracker**: Color-coded indicators:
  * 🔵 **Upcoming** (More than 2 days remaining)
  * 🟡 **Due Soon** (0 to 2 days remaining)
  * 🔴 **Deadline Passed** (Past deadline)

### 3. Admin Module
* **Admin Portal**: Dedicated administrator login (`admin` / `admin123`).
* **Admin Dashboard**: System-wide statistics for Total Students, Total Assignments, Submitted Assignments, Pending Submissions, and Late Submissions.
* **Assignment Management**:
  * Add new assignment with title, subject, description, given date, and deadline date.
  * Edit existing assignments.
  * Delete assignments.
* **Submission Management**: View student submissions along with student name, register number, subject, submission date, status, and submitted content.

---

## 📁 Project Structure

```text
project/
├── app.py                     # Main Flask application logic & routes
├── database.sql               # MySQL Database schema & seed data
├── requirements.txt           # Python dependencies
├── test_app.py                # Unit test suite
├── README.md                  # Project setup documentation
├── static/
│   ├── css/
│   │   └── style.css          # Heather Purple + Cyan + Peach custom styling
│   └── js/
│       └── script.js          # Client-side scripts & form confirmation
└── templates/
    ├── base.html              # Layout template with navbar & footer
    ├── login.html             # Student login page
    ├── register.html          # Student registration page
    ├── student_dashboard.html # Student dashboard & deadline tracker
    ├── assignments.html       # Student assignment list
    ├── submit_assignment.html # Assignment submission form
    ├── submission_history.html# Submission history page
    ├── admin_login.html       # Admin login page
    ├── admin_dashboard.html   # Admin dashboard
    ├── manage_assignments.html# Admin assignment CRUD management
    └── submissions.html       # Admin submission records management
```

---

## 🗄️ Database Setup Instructions (XAMPP / phpMyAdmin)

1. Start **XAMPP Control Panel**.
2. Click **Start** for both **Apache** and **MySQL**.
3. Open your browser and navigate to `http://localhost/phpmyadmin`.
4. Click on the **Import** tab in phpMyAdmin.
5. Click **Choose File** and select the `database.sql` file from the project directory.
6. Click **Import** (or **Go**) at the bottom of the page.
7. phpMyAdmin will create the `student_assignment_db` database along with the required `students`, `admins`, `assignments`, and `submissions` tables and seed sample data.

---

## 💻 Step-by-Step Instructions to Run in VS Code

### Prerequisites
* **Python 3.8+** installed on your system.
* **VS Code** editor installed.
* **XAMPP** running with MySQL service active.

### Execution Steps

1. **Open Project Folder in VS Code**:
   * Open VS Code -> `File` -> `Open Folder...` -> Select the project root folder.

2. **Open Terminal in VS Code**:
   * Press `Ctrl + ~` (or `Terminal` -> `New Terminal`).

3. **Create and Activate Virtual Environment** *(Recommended)*:
   ```bash
   # Windows
   python -m venv venv
   venv\Scripts\activate

   # macOS / Linux
   python3 -m venv venv
   source venv/bin/activate
   ```

4. **Install Required Packages**:
   ```bash
   pip install -r requirements.txt
   ```

5. **Run the Application**:
   * To run with MySQL (XAMPP running):
     ```bash
     python app.py
     ```
   * *Optional*: To run with standalone SQLite (no XAMPP required):
     ```bash
     # Windows (Command Prompt)
     set USE_SQLITE=1 && python app.py

     # macOS / Linux / PowerShell
     USE_SQLITE=1 python app.py
     ```

6. **Access Application in Web Browser**:
   * Open browser and visit: `http://127.0.0.1:5000`

---

## 🔑 Default Login Credentials

### Administrator
* **URL**: `/admin/login`
* **Username**: `admin`
* **Password**: `admin123`

### Sample Student
* Register through `/register` or log in with any newly created student account.

---

## 🧪 Running Unit Tests

Run the test suite using SQLite in-memory mode:
```bash
USE_SQLITE=1 python -m unittest test_app.py
```
