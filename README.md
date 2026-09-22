# Student Portfolio Website Generator

A modern, attractive, and beginner-friendly web application built with **Python Flask**, **Bootstrap 5**, and **MySQL** that automatically generates professional portfolio websites for students based on their profile, education, skills, projects, and certifications.

---

## 🎨 Theme & Design
- **Background:** Navy Blue and Dark Navy Blue Gradient
- **Cards & Containers:** Sky Blue `#f0f9ff` & `#e0f2fe`
- **Buttons, Icons & Badges:** Cyan `#00d2ff` / `#06b6d4`
- **UI Components:** Bootstrap 5, Bootstrap Icons, Rounded Corners, Sleek Shadows, Fully Responsive.

---

## 🛠 Modules Included

1. **Student Registration & Login:** Name, Register Number, Department, Email, Password.
2. **Student Profile:** Profile Photo upload, About Me, Career Objective, Hobbies, Phone, Address, LinkedIn, GitHub.
3. **Portfolio Dashboard:** Overview of student statistics, fast navigation to manage sections and live portfolio preview link.
4. **Portfolio Generator:** Automatically builds a professional single-page web portfolio with section navigation:
   - Home
   - About
   - Skills
   - Education
   - Projects
   - Certifications
   - Contact
5. **Manage Portfolio Sections (CRUD):** Add, Edit, Delete information for:
   - Profile Details
   - Education History
   - Technical Skills (Python, HTML, CSS, JavaScript, Bootstrap, MySQL, etc.)
   - Projects Showcase
   - Certifications & Course Completions
6. **Admin Dashboard:** Admin login, view registered students, preview individual student portfolios, and manage/delete student data.

---

## 📋 Prerequisites & Tools

- **Server:** XAMPP (Apache + MySQL / phpMyAdmin)
- **Editor:** VS Code
- **Language:** Python 3.8+
- **Database:** MySQL

---

## 🚀 Setup & Installation Guide

### Step 1: XAMPP MySQL Setup
1. Open **XAMPP Control Panel**.
2. Start **Apache** and **MySQL** services.
3. Open your web browser and navigate to: `http://localhost/phpmyadmin/`

### Step 2: Database Import
1. In phpMyAdmin, click on **Databases** tab and create a new database named:
   ```sql
   student_portfolio
   ```
2. Select `student_portfolio` database, go to the **Import** tab.
3. Choose the `database.sql` file provided in the root folder of this project and click **Go**.

*(Alternatively, you can run the application directly; Flask will automatically create the database tables if running in SQLite/MySQL mode).*

### Step 3: VS Code Setup
1. Launch **VS Code**.
2. File -> **Open Folder** -> Select the project root directory (`student-portfolio-generator`).
3. Open the integrated terminal in VS Code (`Ctrl + ~` or `Terminal -> New Terminal`).

### Step 4: Python Package Installation
In the VS Code terminal, install the required dependencies:
```bash
pip install -r requirements.txt
```
or install manually:
```bash
pip install Flask Flask-SQLAlchemy PyMySQL
```

---

## 🏃 Run the Application

### Option A: Run with MySQL (Default / XAMPP)
Ensure XAMPP MySQL is running, then execute:
```bash
python app.py
```

### Option B: Run with SQLite (Quick Standalone Testing)
```bash
USE_SQLITE=1 python app.py
```

Open your browser and visit:
`http://127.0.0.1:5000/`

---

## 🔑 Credentials

### Student Credentials
- Register an account via `/register` or login via `/login`.

### Admin Credentials
- **URL:** `http://127.0.0.1:5000/admin/login`
- **Username:** `admin`
- **Password:** `admin123`

---

## 🧪 Testing

To run the automated unit tests:
```bash
USE_SQLITE=1 python -m unittest test_app.py
```
