# Student Skill Workshop Management Portal

A simple, colorful, clean, responsive, and beginner-friendly web application designed for MCA student project demonstrations.

---

## 🎨 Color Palette & Design
- **Theme**: Lavender (`#f3f0ff`), Indigo (`#4f46e5`), and Mint (`#10b981`)
- **Frontend**: HTML5, CSS3, Bootstrap 5, Bootstrap Icons
- **Backend**: Python 3, Flask framework
- **Database**: MySQL / XAMPP phpMyAdmin (with SQLite fallback for local testing)

---

## 🛠️ Required Python Packages

Install required packages using `pip`:

```bash
pip install Flask Flask-SQLAlchemy PyMySQL
```

Or install from `requirements.txt`:

```bash
pip install -r requirements.txt
```

---

## 💻 XAMPP & phpMyAdmin Setup

1. Open **XAMPP Control Panel** and start **Apache** and **MySQL** modules.
2. Open your web browser and navigate to `http://localhost/phpmyadmin/`.
3. Click on the **Databases** tab and create a new database named:
   ```sql
   student_skill_workshop
   ```
4. Click on `student_skill_workshop`, go to the **Import** tab, choose the `database.sql` file from this project root folder, and click **Go**.

---

## 🚀 How to Run the Project in VS Code

1. Open VS Code and open the `student_skill_workshop` project directory (`File > Open Folder...`).
2. Open the terminal in VS Code (`Ctrl + ~` or `Terminal > New Terminal`).
3. Make sure Python dependencies are installed:
   ```bash
   pip install -r requirements.txt
   ```
4. Run the application:
   ```bash
   python app.py
   ```
5. Open your browser and go to `http://127.0.0.1:5000/`.

*Note for SQLite local testing:* If you do not have MySQL running, you can run:
```bash
USE_SQLITE=1 python app.py
```

---

## 🔑 Default Credentials

### Administrator Credentials:
- **Username**: `admin`
- **Password**: `admin123`

---

## 🧪 Running Unit Tests

Run the test suite using SQLite in-memory database:

```bash
USE_SQLITE=1 python -m unittest test_app.py
```

---

## 📂 Project Structure

```
student_skill_workshop/
│
├── app.py                      # Main Flask application logic & routes
├── database.sql                # MySQL database schema & sample data
├── requirements.txt            # Python dependencies
├── test_app.py                 # Automated unit test suite
├── README.md                   # Setup guide and instructions
│
├── templates/                  # Jinja2 HTML templates
│   ├── base.html               # Main layout navigation & footer
│   ├── index.html              # Landing homepage
│   ├── register.html           # Student registration page
│   ├── login.html              # Student login page
│   ├── student_dashboard.html  # Student dashboard
│   ├── workshops.html          # Public workshop catalog & filters
│   ├── workshop_details.html   # Detailed view & registration action
│   ├── my_workshops.html       # Registered & completed workshops
│   ├── admin_login.html        # Admin authentication page
│   ├── admin_dashboard.html    # Administrator dashboard
│   ├── manage_workshops.html   # Admin workshop list and controls
│   ├── add_workshop.html       # Create new workshop page
│   ├── edit_workshop.html      # Update workshop page
│   ├── registrations.html      # Registration status management
│   └── manage_students.html    # View registered students
│
└── static/
    ├── css/
    │   └── style.css           # Custom Lavender + Indigo + Mint styling
    └── js/
        └── script.js           # Client-side validation & auto-alerts
```
