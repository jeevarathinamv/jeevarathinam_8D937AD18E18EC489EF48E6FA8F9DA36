# Student Internal Marks & Result Tracker

A simple, colorful, responsive, and beginner-friendly web application built using **Python Flask**, **Bootstrap 5**, and **MySQL** (XAMPP).

---

## 🎨 Design Features

- **Color Palette**: Green + Teal + Yellow Theme
- **Background**: Modern vibrant cyan/teal gradient background (no plain white background)
- **Navigation & Buttons**: Stylish teal navbar, rounded corners, and glowing buttons
- **Status Indicators**:
  - 🟢 **Green** for Pass / Good Result (`✓ Result: PASS`)
  - 🟡 **Yellow** for Average Marks / Warnings
  - 🔴 **Red/Orange** for Fail (`⚠ Result: FAIL`)
- **UI Components**: Modern glassmorphism cards, rounded borders, shadows, and Bootstrap icons

---

## 📚 Grade Calculation Rules

- **90 – 100** = `Grade A+`
- **80 – 89** = `Grade A`
- **70 – 79** = `Grade B`
- **60 – 69** = `Grade C`
- **50 – 59** = `Grade D`
- **Below 50** = `Grade F`

**Result Status:**
- Total Mark **≥ 50**: `✓ Result: PASS`
- Total Mark **< 50**: `⚠ Result: FAIL`

---

## 📂 Project Structure

```text
├── app.py                  # Main Flask application & database models
├── database.sql            # MySQL Database schema import script
├── requirements.txt        # Python package dependencies
├── test_app.py             # Unit test suite
├── static/
│   └── style.css           # Custom theme stylesheet
└── templates/
    ├── base.html           # Main base layout with navbar and footer
    ├── index.html          # Landing homepage
    ├── register.html       # Student registration page
    ├── login.html          # Student login page
    ├── student_dashboard.html # Student overview dashboard
    ├── result.html         # Student detailed result tracker
    ├── marks.html          # Admin mark entry form page
    ├── admin_login.html    # Admin login page
    └── admin_dashboard.html# Admin dashboard & mark management
```

---

## 🛠️ Step-by-Step Setup & Running Guide

### 1. XAMPP MySQL Setup
1. Launch **XAMPP Control Panel**.
2. Start the **Apache** and **MySQL** services.
3. Open your browser and navigate to `http://localhost/phpmyadmin`.

### 2. Database Import
1. In phpMyAdmin, click on **Databases** or **New**.
2. Create a database named `student_marks`.
3. Select the `student_marks` database and click the **Import** tab.
4. Choose the `database.sql` file from this project repository and click **Import** / **Go**.

### 3. VS Code Setup
1. Open **Visual Studio Code**.
2. Click `File -> Open Folder...` and select this project directory.
3. Open the integrated terminal (`Ctrl + ~` or `Terminal -> New Terminal`).

### 4. Python Package Installation
Ensure Python 3 is installed, then run the following command in the terminal to install required packages (`Flask`, `Flask-SQLAlchemy`, `PyMySQL`):

```bash
pip install -r requirements.txt
```

### 5. Running the Flask Project

#### Running with MySQL (XAMPP):
Make sure Apache and MySQL are running in XAMPP, then start the server:

```bash
python app.py
```

#### Running with SQLite (Quick testing without XAMPP):
```bash
USE_SQLITE=1 python app.py
```

Open your browser and navigate to `http://127.0.0.1:5000/`.

---

## 🔑 Default Admin Credentials

- **Username**: `admin`
- **Password**: `admin123`

---

## 🧪 Running Unit Tests

Run the test suite with SQLite:
```bash
USE_SQLITE=1 python -m unittest test_app.py
```
