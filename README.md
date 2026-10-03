# Small Business Online Enquiry & Lead Management System

A modern, responsive, and beginner-friendly web application designed for small businesses to capture customer enquiries online, convert prospects into sales leads, and manage follow-ups efficiently.

---

## 🌟 Key Features & Modules

### 1. Customer Module
* **Customer Enquiry Form**: Customers can submit online enquiries with fields for Customer Name, Phone Number, Email, Subject, Enquiry Message, and Enquiry Date.
* **Enquiry Confirmation**: Instant confirmation page with a unique enquiry reference number (e.g., `ENQ-1001`).

### 2. Admin Module
* **Admin Login**: Secure login for authorized administrators (`admin` / `admin123`).
* **Admin Dashboard**: Real-time business metrics across 6 dashboard cards:
  - 📩 Total Enquiries
  - 🆕 New Enquiries
  - 🔄 In Progress Enquiries
  - 💼 Total Leads
  - 📞 Follow-ups Needed
  - ✅ Converted Leads
* **Enquiry Management**: View, search, filter by status, detail view, reply/update status, convert into a sales lead, or delete enquiries.
* **Lead Management**: Track customer requirements, manage lead status (*New Lead, Contacted, Follow-up, Converted, Lost*), schedule follow-up dates, and record notes.
* **Follow-up Management**: View scheduled follow-ups, record new communication logs, and track sales pipeline progress.

---

## 🎨 Design Theme & UI

* **Color Theme**: Navy Blue + Cyan + Peach
  - Background: Navy Blue & Cyan dark gradient
  - Highlights, Buttons & Icons: Cyan
  - Accent Elements, Cards & Badges: Peach
* **UI Components**: Modern rounded cards, soft drop shadows, Bootstrap 5 responsive grid, and Bootstrap Icons.

---

## 🛠️ Technology Stack

* **Frontend**: HTML5, CSS3, Bootstrap 5, Bootstrap Icons, JavaScript
* **Backend**: Python 3 (Flask Framework, Flask-SQLAlchemy)
* **Database**: MySQL (PyMySQL) / SQLite (Fallback)
* **Server**: XAMPP (for MySQL & phpMyAdmin)
* **IDE**: VS Code

---

## 📂 Project Structure

```text
project/
├── app.py                  # Main Flask backend application & routes
├── database.sql            # MySQL database schema & sample seed data
├── requirements.txt        # Python dependency list
├── test_app.py             # Unit tests for testing all modules
├── static/
│   ├── css/
│   │   └── style.css       # Custom Navy Blue, Cyan & Peach theme styles
│   └── js/
│       └── script.js       # Client-side scripts & form validation
└── templates/
    ├── base.html           # Master layout with navbar & footer
    ├── index.html          # Landing page
    ├── enquiry.html        # Customer online enquiry form
    ├── enquiry_success.html# Submission confirmation & reference code
    ├── admin_login.html    # Admin authentication portal
    ├── admin_dashboard.html# Admin dashboard with 6 stat cards
    ├── enquiries.html      # Enquiry management table & search
    ├── enquiry_details.html# Enquiry detail view, reply & convert
    ├── leads.html          # Lead management table & filters
    ├── lead_details.html   # Lead detail view, history & updates
    └── followups.html      # Follow-up scheduler & log stream
```

---

## 🗄️ Database Setup Instructions (XAMPP / phpMyAdmin)

1. **Start XAMPP Control Panel**:
   - Launch XAMPP Control Panel.
   - Click **Start** for **Apache** and **MySQL**.

2. **Open phpMyAdmin**:
   - Open your browser and navigate to: `http://localhost/phpmyadmin/`

3. **Import Database**:
   - Click on the **Databases** tab or click **New** on the left menu.
   - Create a database named `small_business_db` (Collation: `utf8mb4_general_ci`).
   - Select `small_business_db` from the left sidebar.
   - Click on the **Import** tab at the top menu.
   - Click **Choose File** and select `database.sql` from the project directory.
   - Scroll down and click **Go** to execute the SQL script.

---

## 🚀 Running the Project in VS Code

1. **Open Project Folder**:
   - Open **VS Code** and go to `File` > `Open Folder...` and select the project directory.

2. **Open Terminal in VS Code**:
   - Press `Ctrl + ~` (or `Terminal` > `New Terminal`).

3. **Install Dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

4. **Run the Application**:
   - To run with MySQL (default XAMPP setup):
     ```bash
     python app.py
     ```
   - *Note*: If MySQL is not running or for local testing without XAMPP, you can run in SQLite mode:
     ```bash
     USE_SQLITE=1 python app.py
     ```

5. **Access Web Application**:
   - Open your web browser and go to: `http://127.0.0.1:5000`

---

## 🔐 Testing / Admin Demo Credentials

* **Username**: `admin`
* **Password**: `admin123`

---

## 🧪 Running Unit Tests

To run automated unit tests:
```bash
USE_SQLITE=1 python3 -m unittest test_app.py
```

---

## 🎓 Project Viva & Explanation Guide for MCA Students

1. **Architecture**: The project follows the **Model-View-Controller (MVC)** architectural pattern:
   - **Model**: SQLAlchemy ORM classes (`Admin`, `Enquiry`, `Lead`, `FollowUp`) in `app.py`.
   - **View**: Jinja2 HTML templates in `templates/` styled with Bootstrap 5 and custom CSS.
   - **Controller**: Flask route handlers in `app.py` managing business logic and requests.

2. **Database Relationships**:
   - **1-to-Many**: An `Enquiry` can be converted into a `Lead` (`enquiry_id` foreign key).
   - **1-to-Many**: A `Lead` can have multiple `FollowUp` activity logs (`lead_id` foreign key with cascade deletion).

3. **Unique Reference Code**: Reference codes (e.g. `ENQ-1001`) are automatically generated sequentially upon enquiry submission to allow customers and admins to track enquiries effortlessly.
