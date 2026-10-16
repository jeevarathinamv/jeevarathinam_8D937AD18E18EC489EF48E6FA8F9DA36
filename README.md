# Smart Classroom Attendance Management, Internal Marks Calculation, Timetable Management and Automated Reporting System

A web-based college management system designed for MCA/BCA final-year project demonstrations. Built with Python Flask, SQLite, Bootstrap 5, HTML, CSS, and JavaScript.

---

## Color Theme & UI Design
- **Royal Blue (`#1e3a8a`)** - Primary headers & navigation
- **Purple (`#7c3aed`)** - Class Tutors & Theory indicators
- **Cyan (`#06b6d4`)** - Highlights & statistic icons
- **Mint Green (`#10b981`)** - Present status, pass badges, & practical indicators
- **Light Lavender (`#f3e8ff`)** - Background theme

---

## 5 College Classes
1. **MCA 1** (1st Year MCA)
2. **MCA 2** (2nd Year MCA)
3. **BCA 1** (1st Year BCA)
4. **BCA 2** (2nd Year BCA)
5. **BCA 3** (3rd Year BCA)

---

## Demonstration Login Credentials

All accounts use default password: `password123`

| Role | Username | Full Name | Assigned Class / Designation |
|---|---|---|---|
| **Class Tutor & Teacher** | `teacher_vg` | Mr. VG | MCA 2 Class Tutor & AJP Teacher |
| **Class Tutor & Teacher** | `teacher_ak` | Dr. AK | MCA 1 Class Tutor & DSR Teacher |
| **Class Tutor & Teacher** | `teacher_dd` | Mrs. DD | BCA 1 Class Tutor & WT Teacher |
| **Class Tutor & Teacher** | `teacher_sr` | Mr. SR | BCA 2 Class Tutor & CNS Teacher |
| **Class Tutor & Teacher** | `teacher_ce` | Mrs. CE | BCA 3 Class Tutor & Mini Project Teacher |
| **Teacher** | `teacher_cs` | Dr. CS | Library Teacher |
| **Teacher** | `teacher_ar` | Ms. AR | Java Teacher |

---

## Key Features

1. **Role-Based Access Control (RBAC)**
   - **Teachers**: View assigned timetable, open attendance marking sheet, submit attendance, calculate theory & practical internal marks, view reports.
   - **Class Tutors**: Monitor assigned class students, receive automated attendance notifications upon teacher submission, view daily/weekly/monthly reports, track RA students (<50% attendance), export CSV reports.

2. **Attendance Marking Sheet & Live Statistics**
   - Live calculations for Total Students, Present Count, Absent Count, and Attendance Percentage.
   - Quick **Mark All Present** and **Mark All Absent** shortcuts.
   - Duplicate prevention and session editing without records duplication.

3. **Automated Tutor Notifications**
   - Submitting attendance automatically generates a database notification for the assigned class tutor.
   - Persistent notifications with real-time polling in the tutor navbar.

4. **Separate Theory and Practical Internal Marks**
   - Attendance-based mark conversion out of 5:
     - 90% and above &rarr; **5 Marks**
     - 80% to below 90% &rarr; **4 Marks**
     - 70% to below 80% &rarr; **3 Marks**
     - 60% to below 70% &rarr; **2 Marks**
     - 50% to below 60% &rarr; **1 Mark**
     - Below 50% &rarr; **RA (Attendance Below 50%)**
   - Scaled examination marks combined with attendance marks.

5. **Reports & Exports**
   - Daily, Weekly, Monthly, Student-Wise, Class-Wise, Theory, Practical, Internal Marks, and RA student reports.
   - One-click CSV export generated directly from database records.
   - Styled `@media print` layout for printable reports.

---

## Windows PowerShell Setup Instructions

Follow these step-by-step commands to run the application on Windows:

### Step 1: Open Terminal in Project Directory
Open **PowerShell** in VS Code or command prompt and navigate to the project root folder:
```powershell
cd smart_classroom_system
```

### Step 2: Create a Python Virtual Environment
```powershell
python -m venv venv
```

### Step 3: Activate the Virtual Environment
```powershell
.\venv\Scripts\Activate.ps1
```
*(If PowerShell restricts execution, run `Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass` first).*

### Step 4: Install Dependencies
```powershell
pip install -r requirements.txt
```

### Step 5: Initialize SQLite Database and Seed Data
```powershell
python database.py
```
This generates `college_attendance.db` populated with sample classes, teachers, tutors, subjects, students, and timetable entries.

### Step 6: Start the Flask Application
```powershell
python app.py
```

### Step 7: Open in Browser
Open your browser and navigate to:
```
http://127.0.0.1:5000
```

---

## Running Automated Tests

To verify system functionality and test all 16 requirements:
```powershell
USE_SQLITE=1 python -m unittest test_app.py
```

---

## Project Folder Structure
```
smart_classroom_system/
├── app.py
├── database.py
├── requirements.txt
├── README.md
├── college_attendance.db
├── templates/
│   ├── base.html
│   ├── login.html
│   ├── teacher_dashboard.html
│   ├── tutor_dashboard.html
│   ├── timetable.html
│   ├── students.html
│   ├── subjects.html
│   ├── assignments.html
│   ├── attendance.html
│   ├── attendance_report.html
│   ├── student_report.html
│   ├── theory_marks.html
│   ├── practical_marks.html
│   ├── notifications.html
│   └── reports.html
├── static/
│   ├── css/
│   │   └── style.css
│   └── js/
│       └── script.js
└── tests/
    └── test_app.py
```
