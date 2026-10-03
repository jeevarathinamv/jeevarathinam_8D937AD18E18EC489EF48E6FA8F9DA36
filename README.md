# Student Project Showcase Portal

A clean, modern, colorful, and beginner-friendly web application designed for students to submit, showcase, and manage academic projects while allowing faculty administrators to review, approve, reject, or manage submissions.

---

## 🎨 Color Theme & Design

The application features a custom, modern UI styled using **Bootstrap 5** and custom CSS:
- **Periwinkle (`#6366F1`)**: Primary navigation, headers, and accents
- **Teal (`#0D9488`)**: Approval badges, interactive buttons, and success highlights
- **Coral (`#FF6B6B`)**: Action triggers, registration buttons, and callouts

---

## 💻 Tech Stack

- **Frontend**: HTML5, CSS3, JavaScript (ES6), Bootstrap 5, Bootstrap Icons
- **Backend**: Python 3 (Flask Framework, Werkzeug Security, Flask-SQLAlchemy)
- **Database**: MySQL (Fallback support for SQLite via `USE_SQLITE=1`)
- **Server**: XAMPP (Apache + MySQL)
- **Code Editor**: VS Code

---

## 🔑 Key Modules & Features

### 👨‍🎓 Student Module
1. **Student Registration**: Register with Name, Register Number, Department, Email, and Password.
2. **Student Login**: Log in securely using Register Number / Email and Password.
3. **Student Dashboard**: Real-time counter cards showing Total Projects, Published Projects, and Pending Submissions.
4. **Add Project**: Submit projects with Title, Description, Technologies Used, Category, Project Image Screenshot, and Repository/Project Link.
   - *Categories*: Web Development, Python, Java, Mobile App, Data Science, Other.
5. **My Projects**: Overview of submitted projects with Status (*Pending*, *Approved*, *Rejected*), submission date, and options to View, Edit, or Delete.
6. **Project Details**: View comprehensive project details, screenshots, tech stack, and admin remarks.

### 🌟 Public Project Showcase
- **Page Name**: `Project Showcase` (`/showcase`)
- **Public Access**: Anyone can browse approved projects without logging in.
- **Card Layout**: Displays project screenshot, title, student name, department, category, technologies, and a "View Project" button.
- **Search & Filter**: Filter projects by Category or search by keyword (title, student name, tech stack).

### 🛠️ Admin / Faculty Module
1. **Admin Login**: Dedicated login portal (`/admin/login`).
   - **Default Admin Credentials**:
     - **Username**: `admin`
     - **Password**: `admin123`
2. **Admin Dashboard**: Visual overview showing Total Students, Total Projects, Pending Projects, Approved Projects, and Rejected Projects.
3. **Project Management**: View student submissions, examine details, Approve projects for public showcase, Reject projects with custom **Admin Remarks**, or Delete projects.
4. **Student Management**: View all registered students, department info, email addresses, total project counts, and option to delete student accounts.

---

## 📂 Project Directory Structure

```text
student_project_showcase/
│
├── app.py                      # Main Flask Application
├── database.sql                # MySQL Schema & Initial Seed Data
├── requirements.txt            # Python Dependencies
├── README.md                   # Setup & Execution Documentation
├── test_app.py                 # Automated Unit Test Suite
│
├── templates/                  # HTML Templates (Jinja2)
│   ├── base.html
│   ├── index.html
│   ├── register.html
│   ├── login.html
│   ├── student_dashboard.html
│   ├── add_project.html
│   ├── edit_project.html
│   ├── my_projects.html
│   ├── project_details.html
│   ├── showcase.html
│   ├── admin_login.html
│   ├── admin_dashboard.html
│   ├── manage_projects.html
│   └── manage_students.html
│
└── static/                     # Static Assets
    ├── css/
    │   └── style.css           # Custom Periwinkle + Teal + Coral Theme
    ├── js/
    │   └── script.js           # Form Validation & Upload Previews
    └── uploads/                # Project Uploaded Images
```

---

## 🚀 Setup & Execution Guide

### Step 1: XAMPP & phpMyAdmin Setup
1. Launch **XAMPP Control Panel**.
2. Start the **Apache** and **MySQL** modules.
3. Open your web browser and go to: `http://localhost/phpmyadmin/`
4. Click on **Databases** and create a new database named:
   ```sql
   student_project_showcase
   ```
5. Select `student_project_showcase`, click on the **Import** tab, choose the `database.sql` file from the project directory, and click **Import**.

---

### Step 2: Open Project in VS Code
1. Open **VS Code**.
2. Click `File -> Open Folder...` and select the `student_project_showcase` directory.
3. Open a terminal in VS Code (`Terminal -> New Terminal`).

---

### Step 3: Install Required Python Packages
Run the following command in the terminal to install Flask and required libraries:

```bash
pip install -r requirements.txt
```

*Required packages contained in `requirements.txt`:*
- `Flask>=3.0.0`
- `Flask-SQLAlchemy>=3.1.0`
- `PyMySQL>=1.1.0`

---

### Step 4: Run the Flask Application
Run the application using Python:

```bash
python app.py
```

*For quick local testing without MySQL, set `USE_SQLITE=1`:*
```bash
USE_SQLITE=1 python app.py
```

Open your browser and navigate to:
```text
http://127.0.0.1:5000/
```

---

## 💡 MCA Demo & Walkthrough Guide

1. **Home Page (`/`)**: Show the landing page with project stats, features, and recent approved projects.
2. **Public Showcase (`/showcase`)**: Demonstrate browsing approved projects without logging in. Filter by category (e.g. *Web Development*, *Python*, *Data Science*).
3. **Student Registration & Login**:
   - Click **Register** to create a student account.
   - Log in using your Register Number or Email.
4. **Project Submission**:
   - Navigate to **Submit Project**.
   - Fill in details, upload an image screenshot, enter tech stack, and submit.
   - Show that the project status is **Pending**.
5. **Admin Approval Workflow**:
   - Log out as student and navigate to **Admin Login** (`/admin/login`).
   - Sign in with `admin` / `admin123`.
   - Go to **Manage Projects**, select the pending project, and click **Approve & Publish**.
   - Return to the Public Showcase (`/showcase`) to confirm the project is now published live.
