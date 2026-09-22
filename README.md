# Alumni Mentorship & Career Guidance Portal

A modern, colorful, and beginner-friendly web portal built with **Python Flask**, **MySQL / SQLite**, and **Bootstrap 5**.

---

## 🌟 Features & Modules

1. **Student Registration & Login**:
   - Register with Name, Register Number, Department, Email, and Password.
   - Access Student Dashboard with mentorship status, accepted mentorships, and mentor search.

2. **Alumni Registration & Login**:
   - Register with Name, Department, Graduation Year, Job Role, Company, Experience, Email, and Password.
   - Access Alumni Dashboard to view student questions, accept/reject requests, and provide mentorship advice.

3. **Student Dashboard**:
   - View requested mentorships, accepted requests, mentor answers, and available alumni mentors.

4. **Alumni Dashboard**:
   - Manage incoming mentorship requests, view questions, provide tailored advice, and manage posted guidance.

5. **Find Alumni Mentor**:
   - Search/filter alumni by Department, Graduation Year, Job Role, or Company.

6. **Mentorship Request**:
   - Submit career questions directly to selected alumni mentors. Request statuses: `Pending`, `Accepted`, `Rejected`.

7. **Career Guidance Hub**:
   - Share and browse career guidance articles under 4 key categories:
     - **Career Advice**
     - **Interview Tips**
     - **Resume Tips**
     - **Skill Suggestions**

8. **Admin Dashboard**:
   - Administrator login (Default: `admin` / `admin123`).
   - Monitor total counts for students, alumni, requests, and guidance posts.
   - Manage/delete students, alumni, mentorship requests, and career guidance.

---

## 🎨 Design Highlights
- **Vibrant Blue + Purple + Pink Gradient Theme**.
- Smooth rounded cards, glassmorphism headers, shadows, and Bootstrap Icons.
- Fully responsive across mobile, tablet, and desktop screens.

---

## 🛠️ Tech Stack & Requirements
- **Frontend**: HTML5, CSS3, Bootstrap 5, Bootstrap Icons
- **Backend**: Python 3.9+, Flask, Flask-SQLAlchemy
- **Database**: MySQL (via XAMPP / phpMyAdmin) or SQLite (fallback)
- **Database Connector**: PyMySQL

---

## 🚀 Step-by-Step Setup Instructions

### 1. XAMPP MySQL Setup & Database Import
1. Download and install **XAMPP** from [apachefriends.org](https://www.apachefriends.org/).
2. Open the **XAMPP Control Panel** and start both **Apache** and **MySQL**.
3. Open your web browser and go to `http://localhost/phpmyadmin`.
4. Click on **Databases** at the top menu.
5. Create a new database named `alumni_mentorship` and click **Create**.
6. Select `alumni_mentorship` from the left sidebar, click the **Import** tab.
7. Click **Choose File**, select `database.sql` from the project folder, and click **Import**.

---

### 2. VS Code Setup & Opening Project
1. Open **Visual Studio Code**.
2. Click **File > Open Folder...** and select the `alumni-mentorship-portal` directory.
3. Open a terminal inside VS Code by going to **Terminal > New Terminal** (or press `Ctrl + ~`).

---

### 3. Python Package Installation
Run the following command in the VS Code terminal to install the necessary dependencies:

```bash
pip install -r requirements.txt
```

---

### 4. Running the Flask Application

#### Option A: Running with XAMPP MySQL (Default)
Ensure XAMPP MySQL is running, then start the application:

```bash
python app.py
```

#### Option B: Running with SQLite (Quick Standalone / Testing)
If you prefer not using XAMPP MySQL, you can run in SQLite mode:

```bash
# On Linux / macOS:
USE_SQLITE=1 python app.py

# On Windows PowerShell:
$env:USE_SQLITE="1"; python app.py

# On Windows CMD:
set USE_SQLITE=1 && python app.py
```

---

### 5. Accessing the Application
Open your web browser and navigate to:
```
http://127.0.0.1:5000
```

---

## 🔐 Default Login Credentials (Demo)

### Admin Account:
- **Username**: `admin`
- **Password**: `admin123`

### Sample Alumni Accounts:
1. **Sarah Jenkins** (`Software Engineer @ Google`)
   - **Email**: `sarah.j@gmail.com`
   - **Password**: `alumni123`
2. **Michael Chen** (`Data Scientist @ Amazon`)
   - **Email**: `michael.c@gmail.com`
   - **Password**: `alumni123`
3. **Priya Sharma** (`Product Manager @ Microsoft`)
   - **Email**: `priya.s@gmail.com`
   - **Password**: `alumni123`

---

## 🧪 Running Automated Unit Tests

To run the automated unit test suite:

```bash
USE_SQLITE=1 python -m unittest test_app.py
```
