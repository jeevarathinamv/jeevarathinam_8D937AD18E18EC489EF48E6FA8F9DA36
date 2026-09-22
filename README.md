# Student Study Partner Finder

A modern, colorful, and beginner-friendly web application designed to help college students connect with study partners based on department, subjects, study time preferences, and study modes.

---

## 🎨 Features & Technologies

- **Frontend:** HTML5, CSS3 (Blue + Purple + Pink gradient theme), Bootstrap 5, Bootstrap Icons, Google Fonts (Poppins)
- **Backend:** Python Flask
- **Database:** MySQL (XAMPP / phpMyAdmin) with SQLite fallback support
- **Editor:** VS Code

### Key Modules:
1. **Student Registration & Login:** Create account with student name, register number, department, email, and password.
2. **Student Profile:** Add & manage study preferences, subjects, technical skills, preferred study times, study modes, and bio.
3. **Student Dashboard:** View available partners, sent requests, accepted connections, and profile summary.
4. **Find Study Partner:** Search and filter partners by department, subject, study time, and mode.
5. **Study Partner Request:** Send partner requests with optional notes or common subjects.
6. **My Study Partners:** Manage accepted partners, view incoming requests (Accept/Reject), and track sent invitations.
7. **Admin Dashboard:** Admin login, manage registered students, view student profiles, monitor request activity, and delete student accounts.

---

## 🛠️ Step-by-Step Setup Guide

### 1. XAMPP MySQL Setup
1. Download and install **XAMPP** from [apachefriends.org](https://www.apachefriends.org/).
2. Open the **XAMPP Control Panel**.
3. Start the **Apache** and **MySQL** services.

---

### 2. Database Import
1. Open your web browser and go to `http://localhost/phpmyadmin`.
2. Click on the **Databases** tab.
3. Create a new database named `student_study_partner`.
4. Click on the newly created database `student_study_partner` in the left sidebar.
5. Go to the **Import** tab at the top menu.
6. Click **Choose File** and select `database.sql` from the project directory.
7. Click **Import** at the bottom of the page to create tables and seed default data.

---

### 3. VS Code Setup
1. Open **VS Code**.
2. Go to `File` > `Open Folder...` and select the project directory `Student Study Partner Finder`.
3. (Optional) Install recommended VS Code extensions:
   - **Python** (by Microsoft)
   - **Pylance**

---

### 4. Python Package Installation
1. Open the integrated terminal in VS Code (`Ctrl + ~` or `Terminal` > `New Terminal`).
2. (Optional) Create and activate a virtual environment:
   ```bash
   python -m venv venv
   # On Windows:
   venv\Scripts\activate
   # On macOS/Linux:
   source venv/bin/activate
   ```
3. Install required Python packages:
   ```bash
   pip install -r requirements.txt
   ```
   *(Requirements: `Flask`, `Flask-SQLAlchemy`, `PyMySQL`)*

---

### 5. Running the Flask Project
1. Make sure XAMPP MySQL is running (or set `USE_SQLITE=1` if running without MySQL).
2. Start the Flask application:
   ```bash
   python app.py
   ```
3. Open your browser and navigate to:
   ```
   http://127.0.0.1:5000
   ```

---

## 🔑 Default Credentials

- **Admin Login:**
  - URL: `http://127.0.0.1:5000/admin/login`
  - Username: `admin`
  - Password: `admin123`

- **Sample Student Logins:**
  - Email / Reg No: `aarav@example.com` or `REG202401` | Password: `password123`
  - Email / Reg No: `ananya@example.com` or `REG202402` | Password: `password123`
  - Email / Reg No: `rohan@example.com` or `REG202403` | Password: `password123`

---

## 🧪 Running Unit Tests

To run automated tests with SQLite fallback:
```bash
USE_SQLITE=1 python3 -m unittest test_app.py
```
