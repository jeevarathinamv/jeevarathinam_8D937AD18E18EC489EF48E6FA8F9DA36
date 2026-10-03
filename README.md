# Service Business Booking & Customer Management System

A modern, simple, beginner-friendly web application developed using **Python Flask**, **MySQL**, **HTML5**, **CSS3**, and **Bootstrap 5**.

Designed specifically as an **MCA Project**, this system enables service businesses (e.g., house cleaning, plumbing, electrical, car detailing) to manage customer accounts, service listings, and appointment bookings seamlessly.

---

## 🎨 Design Theme & Styling

- **Color Theme:** Raspberry (`#D81B60`), Violet (`#7B1FA2`), and Blue (`#1976D2`).
- **Background:** Rich gradient background blending Raspberry, Violet, and Blue tones.
- **Components:** Rounded glassmorphism cards, soft drop shadows, Bootstrap 5 UI, and Bootstrap Icons.
- **Responsive:** Fully responsive across Desktop, Tablet, and Mobile devices.

---

## 🚀 Modules & Features

### 1. Customer Module
- **Customer Registration & Login:** Secure registration with Name, Phone, Email, and Password with hashed storage.
- **Customer Dashboard:** Displays statistics for Total, Pending, Confirmed, and Completed service bookings.
- **Service List:** View available services, descriptions, pricing, duration, and real-time availability.
- **Service Booking:** Book services by selecting service, date, time slot, contact info, and special instructions.
- **My Bookings:** View history of booked services along with status tracking (Pending, Confirmed, Completed, Cancelled).

### 2. Admin Module
- **Admin Login:** Dedicated portal for system administrators.
- **Admin Dashboard:** Overview metrics including Total Customers, Total Services, Total Bookings, Pending, Confirmed, and Completed counts.
- **Service Management:** Full CRUD operations (Add Service, Edit Service, Delete Service, View Service Details).
- **Booking Management:** View all bookings, view details, confirm, complete, cancel, or delete bookings. Filter bookings by Service, Date, or Status.
- **Customer Management:** View registered customers, search by name/email/phone, view booking history per customer, or remove customer records.

---

## 🔐 Sample Credentials

### Admin Login
- **Username:** `admin`
- **Password:** `admin123`

---

## 📂 Project Structure

```
project/
├── app.py                      # Flask Application Main File & Routes
├── database.sql                # MySQL Database Schema & Seed Data
├── test_app.py                 # Unit Test Suite
├── requirements.txt            # Python Dependencies
├── README.md                   # Setup & Explanation Guide
├── templates/
│   ├── base.html               # Main Navigation & Footer Layout
│   ├── index.html              # Landing Page
│   ├── register.html           # Customer Registration
│   ├── login.html              # Customer Login
│   ├── admin_login.html        # Admin Portal Login
│   ├── customer_dashboard.html # Customer Dashboard
│   ├── services.html           # Service Catalog Page
│   ├── book_service.html       # Service Booking Form
│   ├── my_bookings.html        # Customer Booking List
│   ├── admin_dashboard.html    # Admin Dashboard Overview
│   ├── manage_services.html   # Admin Service CRUD Management
│   ├── manage_bookings.html   # Admin Booking Management & Filtering
│   ├── booking_details.html    # Detailed Booking View
│   └── manage_customers.html   # Customer Management & Search
└── static/
    ├── css/
    │   └── style.css           # Custom CSS Theme Styles
    └── js/
        └── script.js           # Client-side Interactions
```

---

## 🛠️ Step-by-Step Setup Instructions

### 1. Database Setup using XAMPP & phpMyAdmin

1. Open **XAMPP Control Panel** and start the **Apache** and **MySQL** services.
2. Open your web browser and go to `http://localhost/phpmyadmin/`.
3. Click on the **SQL** tab in phpMyAdmin.
4. Copy the entire contents of `database.sql` from this project.
5. Paste the SQL code into the query editor and click **Go**.
6. This will automatically create the `service_booking_db` database, table structures (`admins`, `customers`, `services`, `bookings`), and default admin account.

---

### 2. How to Run in VS Code

1. Open **VS Code** and open the project directory.
2. Open the integrated terminal (`Ctrl + ~` or `Terminal -> New Terminal`).
3. (Optional) Create and activate a virtual environment:
   ```bash
   python -m venv venv
   # On Windows:
   venv\Scripts\activate
   # On macOS/Linux:
   source venv/bin/activate
   ```
4. Install required Python packages:
   ```bash
   pip install -r requirements.txt
   ```
5. Run the Flask application:
   ```bash
   python app.py
   ```
6. Open your browser and navigate to:
   ```
   http://127.0.0.1:5000/
   ```

*Note: For testing without MySQL running, set `USE_SQLITE=1 python app.py` to use SQLite automatically.*

---

## 🎓 MCA Project Viva Explanation Guide

1. **Architecture:** Model-View-Controller (MVC) pattern using Flask (Controller), SQLAlchemy (Model/ORM), and Jinja2 HTML Templates (View).
2. **Database Relationships:**
   - One Customer has Many Bookings (`Customer 1 -> N Booking`)
   - One Service has Many Bookings (`Service 1 -> N Booking`)
3. **Security:** Passwords are hashed using Werkzeug `generate_password_hash` and verified with `check_password_hash`. Session-based authentication guards admin and customer routes using custom Python decorators (`@customer_required` and `@admin_required`).
