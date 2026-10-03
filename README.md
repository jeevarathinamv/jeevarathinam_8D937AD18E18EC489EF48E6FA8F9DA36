# Student Freelance Project Management Portal

A simple, modern, beginner-friendly web application designed for MCA college students to track freelance projects, tasks, clients, progress, and earnings.

---

## 🌟 Key Features

### 🎓 Student Module
1. **Student Registration & Login**: Secure registration and login using email or register number with hashed passwords.
2. **Student Dashboard**: Real-time stats (Total Projects, Active, Completed, Pending, Total Earnings) and deadline reminders.
3. **Freelance Profile**: Profile with skills, experience, bio, portfolio link, and contact email.
4. **Project Management**: Add, edit, view, and delete freelance projects with custom categories, deadlines, budgets, status, and progress percentage.
5. **Progress Updates**: Dynamic progress bars, milestone update notes, and status transitions (New, In Progress, On Hold, Completed, Cancelled).
6. **Task Management**: Create tasks for each project with priority levels (High, Medium, Low), due dates, and real-time status updates (Pending, In Progress, Completed).
7. **Client Management**: Store client details (Name, Phone, Email, Company Name, Address, Notes) and link projects to clients.
8. **Payment Tracking**: Record project payments, amounts, payment dates, and payment status (Pending, Partially Paid, Paid).
9. **Deadline Reminders**: Overview of upcoming project deadlines, overdue/pending tasks, and pending client payments.

### 🛡️ Admin Module
1. **Admin Login**: Separate administrator portal (`admin` / `admin123`).
2. **Admin Dashboard**: System-wide statistics for total students, total projects, active/completed/pending projects, and clients.
3. **Student Management**: View all registered students, search students by name or register number, inspect student profile details/projects, and delete students.
4. **Project Monitoring**: View all student projects with search and status filtering to track overall student progress.

---

## 🎨 Color Theme & Design
- **Primary Gradient Background**: Cobalt Blue (`#1e3c72`) to Deep Indigo (`#6366f1`).
- **Cobalt Blue**: Navigation bars, headers, buttons, and card accents.
- **Lavender**: Modern glassmorphic cards and highlight backgrounds.
- **Mint Green**: Success indicators, completed projects, paid status, and low priority.
- **Orange**: Important action buttons, active/in-progress status, and medium priority.
- **Red**: Cancelled projects, overdue tasks, and high priority.
- **Icons**: Bootstrap Icons 1.10.

---

## 💻 Tech Stack
- **Frontend**: HTML5, CSS3, Bootstrap 5, Bootstrap Icons
- **Backend**: Python 3, Flask, Flask-SQLAlchemy
- **Database**: MySQL (PyMySQL) / SQLite fallback
- **Server Environment**: XAMPP / phpMyAdmin / Standalone Python
- **IDE**: VS Code

---

## 🗄️ Database Setup in XAMPP / phpMyAdmin

1. Open **XAMPP Control Panel** and start **Apache** and **MySQL** services.
2. Open your browser and navigate to `http://localhost/phpmyadmin`.
3. Click on the **Import** tab.
4. Select the `database.sql` file provided in the repository root directory.
5. Click **Go** to create the `freelance_db` database along with all required tables:
   - `admins`
   - `students`
   - `student_profiles`
   - `clients`
   - `projects`
   - `tasks`
   - `payments`

---

## 🚀 How to Run the Project in VS Code

1. **Clone or Open Project Folder** in VS Code.
2. **Install Dependencies**:
   Open VS Code terminal (`Ctrl + ~`) and run:
   ```bash
   pip install -r requirements.txt
   ```
3. **Run the Flask Application**:
   - For Default MySQL Setup (XAMPP running):
     ```bash
     python app.py
     ```
   - For SQLite Standalone Setup (No MySQL required):
     ```bash
     USE_SQLITE=1 python app.py
     ```
4. **Access the Web App**:
   Open your web browser and go to `http://127.0.0.1:5000/`.

---

## 🔑 Demo Test Credentials

- **Admin Login**:
  - **Username**: `admin`
  - **Password**: `admin123`

- **Student Login**:
  - Simply register a new account on the `/register` page or log in with your registered credentials.

---

## 🧪 Running Automated Tests

Run unit tests using SQLite in-memory mode:
```bash
USE_SQLITE=1 python3 -m unittest test_app.py
```
