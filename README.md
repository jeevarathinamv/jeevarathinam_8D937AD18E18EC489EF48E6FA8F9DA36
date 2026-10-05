# Student Subject Registration System

A simple, modern, and beginner-friendly web application built with **Python Flask**, **MySQL**, **Bootstrap 5**, and **HTML/CSS/JS** for managing student subject registrations. Designed specifically for MCA student project demonstrations.

---

## 🎨 Theme & Design
- **Color Theme**: Indigo (`#3F51B5`), Cyan (`#00ACC1`), and Peach (`#FF7043`).
- **UI Components**: Bootstrap 5 cards, forms, responsive tables, badge badges, and icons.

---

## ✨ Features

### Student Portal
1. **Registration & Login**: Secure signup with name, register number, department, year, semester, email, and password hashing (`Werkzeug`).
2. **Dashboard**: Live overview of available subjects, registered subjects, total credits, and current semester.
3. **Available Subjects**: Filter subjects by department, semester, subject type (Core, Elective, Practical), and search by subject name/code.
4. **Subject Registration**: Single-click registration with strict rules:
   - Prevents duplicate registrations for the same subject.
   - Shows only subjects matching student department and semester.
   - Immediate confirmation feedback.
5. **My Registered Subjects**: View all registered subjects, credit points, registration date, status (`Registered` / `Cancelled`), and automatic total credits calculation.
6. **Cancellation**: Students can cancel any registered subject at any time.

### Admin Portal
1. **Admin Login**: Secure login with sample credentials (`admin` / `admin123`).
2. **Admin Dashboard**: Real-time statistics on total students, total subjects, total registrations, and active registrations.
3. **Subject Management**: Complete CRUD (Create, Read, Update, Delete) operations for course subjects.
4. **Registration Management**: View all student subject registrations with the option to cancel registrations if required.
5. **Student Management**: View all registered student details and delete student accounts if needed.

---

## 🛠️ Tech Stack & Requirements

- **Backend**: Python Flask 3.x
- **Database**: MySQL (via `flask-sqlalchemy` and `pymysql`), with automatic SQLite fallback when testing or configured.
- **Frontend**: HTML5, CSS3, JavaScript, Bootstrap 5, Bootstrap Icons.
- **Environment**: XAMPP / WAMP / MySQL Server, VS Code.

---

## 📋 Required Python Packages

Install required packages using `pip`:

```bash
pip install Flask Flask-SQLAlchemy PyMySQL
```

Or install directly from `requirements.txt`:

```bash
pip install -r requirements.txt
```

---

## 🗄️ Database Setup (XAMPP / phpMyAdmin)

1. Start **XAMPP Control Panel** and turn on **Apache** and **MySQL**.
2. Open your browser and navigate to `http://localhost/phpmyadmin/`.
3. Click on the **SQL** tab.
4. Open the `database.sql` file included in this project, copy its entire contents, paste it into the SQL box, and click **Go**.
5. This creates the `subject_registration_db` database and seeds default sample subjects and admin account.

---

## 🚀 How to Run the Project in VS Code

1. Open VS Code and open the `student_subject_registration` project folder.
2. Ensure your Python virtual environment or system Python has the required dependencies installed (`pip install -r requirements.txt`).
3. If using XAMPP MySQL, make sure MySQL service is running on `localhost:3306`.
4. Open the VS Code integrated terminal (`Ctrl + ~` or `Terminal -> New Terminal`).
5. Run the application:

```bash
python app.py
```

6. Open your web browser and go to:
   `http://127.0.0.1:5000`

---

## 🧪 How to Run Automated Unit Tests

To run unit tests locally using in-memory SQLite:

```bash
USE_SQLITE=1 python3 -m unittest test_app.py
```

---

## 🔑 Default Credentials

- **Admin Login**:
  - **Username**: `admin`
  - **Password**: `admin123`

---

## 📁 Project Structure

```
student_subject_registration/
│
├── app.py                      # Main Flask application & database models
├── database.sql                 # MySQL schema & initial seed script
├── requirements.txt             # Required Python libraries
├── test_app.py                  # Unit tests for features & validation
├── README.md                    # Project documentation
│
├── templates/
│   ├── base.html                # Base layout template with Indigo navbar & footer
│   ├── index.html               # Homepage / Landing page
│   ├── register.html            # Student registration page
│   ├── login.html               # Student login page
│   ├── student_dashboard.html   # Student dashboard with credit summary
│   ├── subjects.html            # Available subjects & filtering page
│   ├── my_subjects.html         # Registered subjects & credit counter
│   ├── admin_login.html         # Admin login page
│   ├── admin_dashboard.html     # Admin dashboard
│   ├── manage_subjects.html     # Admin subject list view
│   ├── add_subject.html         # Admin add subject form
│   ├── edit_subject.html        # Admin edit subject form
│   ├── manage_registrations.html# Admin view & cancel student registrations
│   └── manage_students.html     # Admin student list & deletion
│
└── static/
    ├── css/
    │   └── style.css            # Custom CSS styles (Indigo + Cyan + Peach theme)
    └── js/
        └── script.js            # Client-side script & form validation
```
