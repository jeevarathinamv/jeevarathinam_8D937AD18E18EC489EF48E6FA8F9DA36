# College Department Information Management System

A simple, modern, responsive, and beginner-friendly web application built for college department information management, specifically designed for MCA student demonstrations.

---

## 🎨 Theme & Design
- **Color Theme:** Navy Blue (`#002147`), Cyan (`#00bcd4`), Light Orange (`#ff9f43`).
- **Frontend Framework:** HTML5, CSS3, Bootstrap 5.
- **Responsive Design:** Clean cards, tables, navigation bar, badging, and alert popups.

---

## 🛠️ Technology Stack
- **Frontend:** HTML5, CSS3, Bootstrap 5, JavaScript
- **Backend:** Python Flask
- **Database:** MySQL / XAMPP phpMyAdmin (SQLite supported via fallback)
- **Editor:** Visual Studio Code (VS Code)

---

## 📁 Database Tables Overview

The project uses 5 core tables:
1. `admins` - Stores admin credentials and hashed passwords.
2. `students` - Stores student registration details and hashed passwords.
3. `department` - Stores department name, code, head, email, phone, and description.
4. `faculty` - Stores faculty name, faculty ID, department, designation, email, and phone.
5. `notices` - Stores department notices title, description, and notice date.

---

## ⚙️ XAMPP & phpMyAdmin Setup Steps

1. Start **XAMPP Control Panel**.
2. Click **Start** for both **Apache** and **MySQL** modules.
3. Open your web browser and navigate to `http://localhost/phpmyadmin`.
4. Click on **Databases** tab and create a new database named `department_db`.
5. Select `department_db`, click on the **Import** tab.
6. Click **Choose File** and select the `database.sql` file from this project directory.
7. Click **Import** at the bottom to execute the SQL script and create all tables with seed data.

---

## 💻 VS Code Run Steps

1. Open **Visual Studio Code**.
2. Open the project folder `department_information`.
3. Open the terminal in VS Code (`Ctrl + ~` or `Terminal -> New Terminal`).
4. (Optional) Create and activate a virtual environment:
   ```bash
   python -m venv venv
   # On Windows:
   venv\Scripts\activate
   # On macOS/Linux:
   source venv/bin/activate
   ```
5. Install required dependencies:
   ```bash
   pip install -r requirements.txt
   ```
6. Run the Flask application:
   ```bash
   python app.py
   ```
   *(Note: To test using SQLite without MySQL running, set `USE_SQLITE=1 python app.py` on Linux/Mac or `$env:USE_SQLITE="1"; python app.py` on PowerShell)*
7. Open your browser and go to `http://127.0.0.1:5000/`.

---

## 🔑 Default Credentials

- **Admin Login:**
  - **Username:** `admin`
  - **Password:** `admin123`

- **Sample Student Registration:**
  - Students can register using their **Register Number**, **Name**, **Department**, **Year**, **Email**, and **Password**.

---

## 🔄 Project Flow & Demonstration Steps

### Student Flow
1. **Home Page (`/`):** View department overview and recent notices.
2. **Student Register (`/register`):** Register with student details.
3. **Student Login (`/login`):** Log in using Email or Register Number.
4. **Student Dashboard (`/student/dashboard`):** View student profile and department contact info.
5. **View Department (`/department`):** View full department details and HOD contact.
6. **View Faculty (`/faculty`):** View list of department faculty members.
7. **View Notices (`/notices`):** Read all department announcements and circulars.

### Admin Flow
1. **Admin Login (`/admin/login`):** Log in with default admin credentials (`admin` / `admin123`).
2. **Admin Dashboard (`/admin/dashboard`):** Overview of total students, total faculty, total notices, department summary, and registered student list.
3. **Manage Department (`/admin/department`):** Update department details, HOD name, email, phone, and description.
4. **Manage Faculty (`/admin/faculty`):** Add, edit, view, or delete faculty records.
5. **Manage Notices (`/admin/notices`):** Add, edit, view, or delete department notices.

---

## 🧪 Running Unit Tests

Run the unit tests locally with SQLite in-memory database:
```bash
USE_SQLITE=1 python3 -m unittest test_app.py
```
