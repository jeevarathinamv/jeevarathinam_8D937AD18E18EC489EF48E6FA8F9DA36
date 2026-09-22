# Student Leave Request & Approval System

A simple, beginner-friendly, and modern web application built with Python Flask, Bootstrap 5, and MySQL (XAMPP).

## Features & Modules

1. **Student Registration & Login**: Registration with Name, Register Number, Department, Email, and Password. Secure login for registered students.
2. **Student Dashboard**: Displays student details, total leave requests, pending requests, approved requests, and rejected requests.
3. **Apply Leave**: Form to submit Leave Type, From Date, To Date, and Reason.
4. **Leave History**: Table showing Leave Type, From Date, To Date, Reason, Status, and Admin Reply.
5. **Admin Dashboard**: Faculty/Admin portal to view student details, leave reasons, approve or reject leave, and send admin replies.
6. **Color-Coded Status Badges**:
   - **Yellow**: Pending
   - **Green**: Approved
   - **Red**: Rejected

---

## Instructions for Setup & Running

### 1. XAMPP MySQL Setup
1. Download and install [XAMPP](https://www.apachefriends.org/).
2. Open the **XAMPP Control Panel**.
3. Start the **Apache** and **MySQL** services.

### 2. Database Import
1. Open your web browser and go to `http://localhost/phpmyadmin`.
2. Click **New** on the left sidebar to create a new database.
3. Name the database `student_leave` and click **Create**.
4. Select the `student_leave` database, click on the **Import** tab.
5. Choose the `database.sql` file from this project directory and click **Go**.

### 3. VS Code Setup
1. Open **VS Code**.
2. Go to **File > Open Folder...** and select the `Student Leave Request & Approval System` project folder.
3. Open the integrated terminal in VS Code (`Ctrl + ~` or `Terminal > New Terminal`).

### 4. Python Package Installation
Ensure Python 3.8+ is installed on your machine. In the VS Code terminal, run:

```bash
pip install -r requirements.txt
```

### 5. Running the Flask Project
Start the Flask development server:

```bash
python app.py
```

Then open your browser and navigate to:
```
http://127.0.0.1:5000/
```

### Default Credentials
- **Student**: Register a new student through the `/register` page.
- **Admin Login**:
  - **Username**: `admin`
  - **Password**: `admin123`
