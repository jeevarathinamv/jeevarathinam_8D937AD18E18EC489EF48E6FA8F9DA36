# College Student Grievance Portal

A simple, clean, modern, and beginner-friendly web application for managing and tracking student grievances in colleges and universities.

---

## 🎨 Technologies Used

- **Frontend:** HTML5, CSS3, Bootstrap 5, Bootstrap Icons
- **Backend:** Python Flask framework
- **Database:** MySQL (via XAMPP / phpMyAdmin)
- **ORM:** Flask-SQLAlchemy & PyMySQL
- **Editor:** Visual Studio Code (VS Code)

---

## 🎨 Theme & Design Highlights

- **Color Palette:** Navy Blue (`#0a192f`), Cyan (`#00f2fe`), Sky Blue (`#38bdf8`)
- **Status Badges:**
  - 🟡 **Pending** -> Yellow
  - 🔵 **In Progress** -> Cyan / Sky Blue
  - 🟢 **Resolved** -> Green
  - 🔴 **Rejected** -> Red / Orange
- **UI:** Rounded cards, dark-gradient navy backgrounds, glassmorphism, responsive Bootstrap 5 layout.

---

## 📂 Project Structure

```
college-grievance-portal/
│
├── app.py                      # Main Flask Backend Application
├── database.sql                # MySQL Database Schema & Admin Seed Data
├── requirements.txt            # Python Dependencies
├── test_app.py                 # Automated Unit Tests
├── README.md                   # Setup Guide and Documentation
│
├── static/
│   ├── style.css               # Main Custom CSS Stylesheet
│   └── css/
│       └── style.css           # Additional CSS Link Support
│
└── templates/                  # Jinja2 HTML Templates
    ├── base.html               # Navigation, Footer, and Common Layout
    ├── index.html              # Landing Page & Categories Overview
    ├── register.html           # Student Registration Page
    ├── login.html              # Student Login Page
    ├── student_dashboard.html  # Student Dashboard (Stats & Recent Grievances)
    ├── submit_grievance.html   # Submit Grievance Form
    ├── grievance_history.html  # Student Grievance History List
    ├── grievance_details.html  # Live Status Tracker & Admin Reply View
    ├── admin_login.html        # Administrator Login Page
    ├── admin_dashboard.html    # Admin Portal (Filterable Grievance List)
    └── admin_grievance_details.html # Admin Reply & Status Management
```

---

## 🛠️ Step-by-Step Setup Instructions

### 1. XAMPP MySQL Setup
1. Download and install **XAMPP Control Panel** from [apachefriends.org](https://www.apachefriends.org/).
2. Open **XAMPP Control Panel**.
3. Click **Start** next to **Apache** and **MySQL**.

---

### 2. Database Import
1. Open your web browser and navigate to: `http://localhost/phpmyadmin/`
2. Click on the **Databases** tab at the top.
3. Create a new database named:
   ```sql
   college_grievance
   ```
4. Select `college_grievance` from the left menu.
5. Click on the **Import** tab at the top.
6. Click **Choose File** and select `database.sql` from the project directory.
7. Scroll down and click **Import** / **Go**.

---

### 3. VS Code Setup
1. Download and install **Visual Studio Code** from [code.visualstudio.com](https://code.visualstudio.com/).
2. Open VS Code.
3. Go to `File` > `Open Folder...` and select the project folder.
4. Install recommended VS Code extensions:
   - **Python** (by Microsoft)
   - **Jinja** (for template syntax highlighting)

---

### 4. Python Package Installation
1. Ensure Python 3.8+ is installed on your system.
2. Open the built-in terminal in VS Code (`Ctrl + ~` or `Terminal` > `New Terminal`).
3. (Optional) Create and activate a virtual environment:
   ```bash
   python -m venv venv
   # On Windows:
   venv\Scripts\activate
   # On macOS/Linux:
   source venv/bin/activate
   ```
4. Install the required dependencies:
   ```bash
   pip install -r requirements.txt
   ```

---

### 5. Running the Flask Project
1. Start the Flask application:
   ```bash
   python app.py
   ```
2. Open your web browser and go to:
   ```
   http://127.0.0.1:5000/
   ```

---

## 🔑 Default Credentials

### Default Admin Login
- **URL:** `http://127.0.0.1:5000/admin/login`
- **Username:** `admin`
- **Password:** `admin123`

### Sample Student Demo Account
- Click **Register** on the top menu to create a new student account instantly.

---

## 🧪 Running Unit Tests

To run the automated unit test suite using SQLite in-memory database:
```bash
USE_SQLITE=1 python3 -m unittest test_app.py
```
