# College Hostel Room Allocation System

A simple, beginner-friendly web application built with **Python Flask**, **MySQL**, and **Bootstrap 5** for managing hostel room allocations in educational institutions. Designed specifically for MCA project demonstrations.

---

## Features

### Student Module
- **Registration & Login**: Secure signup with Register Number, Department, Email, and Hashed Password.
- **Session Management**: Session-based authentication.
- **Student Dashboard**: Displays student profile details and allocated room information (or "Room Not Allocated" if none).
- **My Room**: View details of assigned hostel block, room number, room type, allocation date, and history.

### Admin Module
- **Admin Dashboard**: Real-time stats for Total Students, Total Rooms, Allocated Rooms, and Available Beds.
- **Manage Rooms**: Add, Edit, and Delete hostel rooms with capacity and room types (`Single`, `Double`, `Triple`).
- **Room Allocation**: Allocate an available room to a registered student with automatic bed count decrement.
- **Manage Allocations**: View all active and historical room allocations, with option to cancel allocations (which automatically restores available bed counts).
- **View Students**: List all registered students and their current room status.

---

## Tech Stack
- **Backend**: Python 3, Flask, Flask-SQLAlchemy, PyMySQL
- **Frontend**: HTML5, CSS3, Bootstrap 5, FontAwesome
- **Database**: MySQL (XAMPP / phpMyAdmin)
- **IDE**: VS Code

---

## Database Structure (`hostel_db`)

The project uses only 4 clean tables:
1. `admins` - Stores admin credentials.
2. `students` - Stores student profile details and password hashes.
3. `rooms` - Stores hostel block, room number, room type, total capacity, and available beds.
4. `allocations` - Stores room allocation records with allocation date and status (`Allocated`, `Cancelled`).

---

## Setup & Installation Instructions

### 1. Database Setup (XAMPP & phpMyAdmin)
1. Open **XAMPP Control Panel** and start **Apache** and **MySQL**.
2. Open your browser and go to `http://localhost/phpmyadmin`.
3. Click on the **SQL** tab.
4. Import or copy-paste the contents of `database.sql` and click **Go**.
5. This creates the `hostel_db` database, tables, default admin account, and sample rooms.

### 2. Project Setup in VS Code
1. Open VS Code and open the project directory (`college_hostel`).
2. Open the terminal in VS Code (`Ctrl + ~` or `Terminal -> New Terminal`).
3. Install required packages:
   ```bash
   pip install -r requirements.txt
   ```

### 3. Running the Application
To run with MySQL (default XAMPP setup):
```bash
python app.py
```

To run with SQLite fallback (no MySQL setup needed for quick testing):
```bash
USE_SQLITE=1 python app.py
```

Open your web browser and go to:
`http://127.0.0.1:5000`

---

## Demo Credentials

- **Admin Login**:
  - URL: `http://127.0.0.1:5000/admin/login`
  - Username: `admin`
  - Password: `admin123`

---

## Testing

Run unit tests locally using SQLite:
```bash
USE_SQLITE=1 python -m unittest test_app.py
```
