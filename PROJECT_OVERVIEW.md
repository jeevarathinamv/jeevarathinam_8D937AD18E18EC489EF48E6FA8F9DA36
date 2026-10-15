# College Attendance & Internal Mark Management System
## Project Overview & Video Demonstration Guide

This document provides a detailed overview of the **College Attendance & Internal Mark Management System** project along with a step-by-step presentation script and walk-through guide suitable for creating a video recording or live demonstration.

---

## 📌 Project Summary

- **Project Title:** College Attendance & Internal Mark Management System
- **Target Users:** Admin, Teachers / Subject In-charges, Class Tutors, and Students
- **Supported Classes:** BCA I, BCA II, BCA III, MCA I, MCA II
- **Technology Stack:**
  - **Frontend:** HTML5, CSS3, Bootstrap 5, JavaScript
  - **Backend:** Python Flask
  - **Database:** MySQL / SQLite (`college_attendance_db`)
  - **Database Driver:** PyMySQL / Flask-SQLAlchemy
  - **Security:** Password Hashing (`scrypt`), Role-Based Access Control, Session Protection

---

## 🎨 Design & UI Palette

The application uses a modern, colorful theme tailored for beginner-friendly college presentations:
- 🔵 **Royal Blue (`#1e40af`):** Primary navbar & headers
- 🟣 **Purple (`#7e22ce`):** Gradient accents & cards
- 🩵 **Cyan (`#06b6d4`):** Dashboard percentage badges & buttons
- 🍃 **Mint Green (`#10b981`):** Success badges & present status indicators
- 🪻 **Light Lavender (`#f3f0ff`):** Soft body background

---

## 🎬 Step-by-Step Video Demonstration Script

### Scene 1: Introduction & System Architecture (0:00 - 1:00)
- **Visual:** Show the Landing Page (`/`) with the colorful cards highlighting Admin, Teacher, Class Tutor, and Student portals.
- **Narrator Script:**
  > "Welcome to the demonstration of the **College Attendance & Internal Mark Management System**, built using Python Flask, Bootstrap 5, and MySQL. This system automates attendance tracking for five academic classes—BCA I, BCA II, BCA III, MCA I, and MCA II—while automatically calculating subject-wise attendance percentages and attendance-based internal marks out of 5."

---

### Scene 2: Admin Portal & Management (1:00 - 2:30)
- **Action:** Login as Admin (`admin` / `admin123`).
- **Visuals:**
  1. Show Admin Dashboard with live stats (Total Classes, Students, Teachers, Timetable Slots).
  2. Navigate to **Manage Timetable** and show the 5-period daily timetable layout.
  3. Show conflict prevention: Demonstrate that the system blocks duplicate class-hour slots and prevents a teacher from being assigned to two classes during the same hour.
  4. Show **Attendance & Internal Mark Rules** configuration (90%+ = 5 marks, 80-89% = 4 marks, ..., <50% = RA).
- **Narrator Script:**
  > "As an Admin, we can manage students, teachers, subjects, and timetables. The system includes built-in collision detection to prevent double-booking teachers or scheduling duplicate periods for a class. Admins can also customize the attendance-to-internal-mark conversion rules."

---

### Scene 3: Teacher Portal & Marking Attendance (2:30 - 4:00)
- **Action:** Logout and login as Teacher (`T101` / `teacher123`).
- **Visuals:**
  1. View Today's Timetable on Teacher Dashboard.
  2. Click **Mark Attendance** for an assigned hour.
  3. Show student list with instant **Mark All Present** / **Mark All Absent** toggle buttons.
  4. Submit attendance and view session entry in **Attendance History**.
- **Narrator Script:**
  > "Teachers log in to view their daily schedule. When marking attendance for a specific class period, the roster is loaded automatically. With one click, teachers can toggle all students present or absent, modify individual records, and submit. The system locks submitted sessions to prevent duplicate entries."

---

### Scene 4: Class Tutor Dashboard & RA Tracking (4:00 - 5:15)
- **Action:** Login as Class Tutor for MCA I (`T101` / `teacher123` - Tutor view).
- **Visuals:**
  1. Show tutor analytics card: Total Students, Present Count, Absent Count, Overall Attendance %, and RA Student count.
  2. Filter reports by date range and subject.
  3. View **RA Students List** (Students with attendance < 50%).
  4. Export report as **CSV**.
- **Narrator Script:**
  > "Class Tutors have dedicated dashboards isolated to their assigned class. Tutors can monitor real-time class attendance, filter by date or subject, instantly identify students with Re-Appear (RA) status due to low attendance, and download reports in CSV format."

---

### Scene 5: Student Portal & Marks (5:15 - 6:30)
- **Action:** Login as Student Kavitha Ramesh (`23MCA01` / `student123`).
- **Visuals:**
  1. Show student attendance overview (Total Hours, Present Hours, Absent Hours, Overall %).
  2. Show subject-wise table with Total Hours, Attendance %, Internal Attendance Mark out of 5, and Eligibility Badge (`Eligible` or `RA – Attendance Below 50%`).
- **Narrator Script:**
  > "Students can log in with their Register Number to view their individual attendance progress across all subjects. The system automatically computes their internal attendance mark out of 5 and clearly displays their eligibility status."

---

## 🔑 Demo Login Credentials

| Role | Username / ID | Password | Notes |
| :--- | :--- | :--- | :--- |
| **Admin** | `admin` | `admin123` | Full access to all entities & rules |
| **Teacher / Tutor (MCA I)** | `T101` | `teacher123` | Class Tutor for MCA I & Subject Teacher |
| **Teacher (BCA I)** | `T102` | `teacher123` | Subject Teacher for BCA I |
| **Student (MCA I)** | `23MCA01` | `student123` | Kavitha Ramesh |
| **Student (BCA I)** | `21BCA01` | `student123` | Aarav Sharma |

---

## 📊 Automatic Calculation Logic

1. **Attendance Percentage:**
   $$\text{Attendance \%} = \left(\frac{\text{Present Hours}}{\text{Total Hours}}\right) \times 100$$
2. **Internal Attendance Mark (out of 5):**
   - **90% and above:** 5 / 5
   - **80% – below 90%:** 4 / 5
   - **70% – below 80%:** 3 / 5
   - **60% – below 70%:** 2 / 5
   - **50% – below 60%:** 1 / 5
   - **Below 50%:** **RA (Re-Appear - Attendance Below 50%)**
