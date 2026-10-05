"""
College Drinking Water Complaint & Maintenance System
=====================================================

An easy-to-demonstrate web application built with Python Flask, MySQL, and Bootstrap 5.

XAMPP / phpMyAdmin Setup Instructions:
---------------------------------------
1. Start Apache and MySQL modules in XAMPP Control Panel.
2. Open http://localhost/phpmyadmin in your web browser.
3. Click "New" to create a database named `water_complaint_db`.
4. Select `water_complaint_db` and click "Import" -> choose `database.sql` -> click "Go".

VS Code Run Instructions:
--------------------------
1. Open the project folder in VS Code.
2. Install Python dependencies:
   `pip install -r requirements.txt`
3. Run the application:
   `python app.py`
4. Access in browser: http://127.0.0.1:5000/

Sample Credentials:
-------------------
Admin Login:
  Username: admin
  Password: admin123

Student Login:
  Register or use sample account:
  Email: student@college.edu / Password: password123
"""

import os
import random
import string
from datetime import datetime, date, timezone
from functools import wraps
from flask import Flask, render_template, request, redirect, url_for, flash, session
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'water_complaint_secret_key_987654321')

# Database Configuration
MYSQL_URI = os.environ.get('DATABASE_URL', 'mysql+pymysql://root:@localhost/water_complaint_db')
SQLITE_URI = 'sqlite:///' + os.path.join(os.path.abspath(os.path.dirname(__file__)), 'water_complaint.db')

use_sqlite = os.environ.get('USE_SQLITE') == '1'
app.config['SQLALCHEMY_DATABASE_URI'] = SQLITE_URI if use_sqlite else MYSQL_URI
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

# Default Credentials
ADMIN_USERNAME = os.environ.get('ADMIN_USERNAME', 'admin')
ADMIN_PASSWORD = os.environ.get('ADMIN_PASSWORD', 'admin123')

def get_utc_now():
    return datetime.now(timezone.utc)

# Database Models
class Admin(db.Model):
    __tablename__ = 'admins'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(100), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    created_at = db.Column(db.DateTime, default=get_utc_now)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)


class Student(db.Model):
    __tablename__ = 'students'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    register_number = db.Column(db.String(50), unique=True, nullable=False)
    department = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    created_at = db.Column(db.DateTime, default=get_utc_now)

    complaints = db.relationship('Complaint', backref='student', lazy=True, cascade="all, delete-orphan")

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)


class Complaint(db.Model):
    __tablename__ = 'complaints'
    id = db.Column(db.Integer, primary_key=True)
    complaint_id = db.Column(db.String(50), unique=True, nullable=False)
    student_id = db.Column(db.Integer, db.ForeignKey('students.id'), nullable=False)
    complaint_type = db.Column(db.String(100), nullable=False)
    location = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text, nullable=False)
    complaint_date = db.Column(db.Date, nullable=False, default=date.today)
    status = db.Column(db.String(20), default='Pending')  # Pending, In Progress, Resolved, Rejected
    admin_remarks = db.Column(db.Text, nullable=True)
    resolved_date = db.Column(db.Date, nullable=True)
    created_at = db.Column(db.DateTime, default=get_utc_now)


def generate_unique_complaint_id():
    """Generates a unique complaint ID like CWP-839201"""
    while True:
        digits = ''.join(random.choices(string.digits, k=6))
        c_id = f"CWP-{digits}"
        if not Complaint.query.filter_by(complaint_id=c_id).first():
            return c_id


def seed_default_data():
    """Seeds default admin user and initial demo data if empty."""
    # Seed Admin
    if Admin.query.count() == 0:
        admin_user = Admin(username=ADMIN_USERNAME)
        admin_user.set_password(ADMIN_PASSWORD)
        db.session.add(admin_user)
        db.session.commit()

    # Seed demo Student & Complaint if empty
    if Student.query.count() == 0:
        demo_student = Student(
            name='John Doe',
            register_number='MCA202401',
            department='Computer Applications (MCA)',
            email='student@college.edu'
        )
        demo_student.set_password('password123')
        db.session.add(demo_student)
        db.session.commit()

        demo_complaint = Complaint(
            complaint_id=generate_unique_complaint_id(),
            student_id=demo_student.id,
            complaint_type='Water Cooler Problem',
            location='2nd Floor - Science Block',
            description='Water cooler is not cooling properly and leaking slightly.',
            complaint_date=date.today(),
            status='Pending'
        )
        db.session.add(demo_complaint)
        db.session.commit()


# Decorators
def student_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_type' not in session or session['user_type'] != 'student':
            flash('Please log in as a student to access this page.', 'warning')
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function


def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_type' not in session or session['user_type'] != 'admin':
            flash('Admin access required.', 'warning')
            return redirect(url_for('admin_login'))
        return f(*args, **kwargs)
    return decorated_function


# --- Public Routes ---

@app.route('/')
def index():
    return render_template('index.html')


# --- Authentication Routes ---

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        name = request.form.get('name', '').strip()
        register_number = request.form.get('register_number', '').strip()
        department = request.form.get('department', '').strip()
        email = request.form.get('email', '').strip().lower()
        password = request.form.get('password', '')

        if not name or not register_number or not department or not email or not password:
            flash('All fields are required.', 'danger')
            return redirect(url_for('register'))

        existing_student = Student.query.filter(
            (Student.email == email) | (Student.register_number == register_number)
        ).first()

        if existing_student:
            flash('Student with this Email or Register Number already exists.', 'danger')
            return redirect(url_for('register'))

        student = Student(
            name=name,
            register_number=register_number,
            department=department,
            email=email
        )
        student.set_password(password)
        db.session.add(student)
        db.session.commit()

        flash('Registration successful! Please log in.', 'success')
        return redirect(url_for('login'))

    return render_template('register.html')


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email_or_reg = request.form.get('email_or_reg', '').strip()
        password = request.form.get('password', '')

        if not email_or_reg or not password:
            flash('Please enter email/register number and password.', 'danger')
            return redirect(url_for('login'))

        student = Student.query.filter(
            (Student.email == email_or_reg.lower()) | (Student.register_number == email_or_reg)
        ).first()

        if student and student.check_password(password):
            session['user_type'] = 'student'
            session['user_id'] = student.id
            session['user_name'] = student.name
            session['register_number'] = student.register_number
            flash(f'Welcome back, {student.name}!', 'success')
            return redirect(url_for('student_dashboard'))
        else:
            flash('Invalid credentials. Please check your details and try again.', 'danger')
            return redirect(url_for('login'))

    return render_template('login.html')


@app.route('/admin/login', methods=['GET', 'POST'])
def admin_login():
    if request.method == 'POST':
        username = request.form.get('username', '').strip()
        password = request.form.get('password', '')

        if not username or not password:
            flash('Please enter username and password.', 'danger')
            return redirect(url_for('admin_login'))

        admin = Admin.query.filter_by(username=username).first()

        if admin and admin.check_password(password):
            session['user_type'] = 'admin'
            session['user_id'] = admin.id
            session['user_name'] = admin.username
            flash('Logged in successfully as Administrator.', 'success')
            return redirect(url_for('admin_dashboard'))
        elif username == ADMIN_USERNAME and password == ADMIN_PASSWORD: # Fallback check
            session['user_type'] = 'admin'
            session['user_name'] = username
            flash('Logged in successfully as Administrator.', 'success')
            return redirect(url_for('admin_dashboard'))
        else:
            flash('Invalid admin credentials.', 'danger')
            return redirect(url_for('admin_login'))

    return render_template('admin_login.html')


@app.route('/logout')
def logout():
    session.clear()
    flash('You have been logged out.', 'info')
    return redirect(url_for('index'))


# --- Student Routes ---

@app.route('/student/dashboard')
@student_required
def student_dashboard():
    student_id = session.get('user_id')
    student = db.session.get(Student, student_id)
    if not student:
        session.clear()
        return redirect(url_for('login'))

    complaints = Complaint.query.filter_by(student_id=student_id).order_by(Complaint.created_at.desc()).all()

    total_count = len(complaints)
    pending_count = len([c for c in complaints if c.status == 'Pending'])
    in_progress_count = len([c for c in complaints if c.status == 'In Progress'])
    resolved_count = len([c for c in complaints if c.status == 'Resolved'])

    return render_template(
        'student_dashboard.html',
        student=student,
        complaints=complaints[:5], # Recent 5
        total_count=total_count,
        pending_count=pending_count,
        in_progress_count=in_progress_count,
        resolved_count=resolved_count
    )


@app.route('/student/report-complaint', methods=['GET', 'POST'])
@student_required
def report_complaint():
    if request.method == 'POST':
        complaint_type = request.form.get('complaint_type', '').strip()
        location = request.form.get('location', '').strip()
        description = request.form.get('description', '').strip()
        complaint_date_str = request.form.get('complaint_date', '')

        if not complaint_type or not location or not description or not complaint_date_str:
            flash('All fields are required.', 'danger')
            return redirect(url_for('report_complaint'))

        try:
            complaint_date = datetime.strptime(complaint_date_str, '%Y-%m-%d').date()
        except ValueError:
            complaint_date = date.today()

        complaint_id = generate_unique_complaint_id()

        new_complaint = Complaint(
            complaint_id=complaint_id,
            student_id=session.get('user_id'),
            complaint_type=complaint_type,
            location=location,
            description=description,
            complaint_date=complaint_date,
            status='Pending'
        )

        db.session.add(new_complaint)
        db.session.commit()

        flash(f'Complaint submitted successfully! Unique Complaint ID: {complaint_id}', 'success')
        return redirect(url_for('my_complaints'))

    today_str = date.today().isoformat()
    return render_template('report_complaint.html', today=today_str)


@app.route('/student/my-complaints')
@student_required
def my_complaints():
    student_id = session.get('user_id')
    complaints = Complaint.query.filter_by(student_id=student_id).order_by(Complaint.created_at.desc()).all()
    return render_template('my_complaints.html', complaints=complaints)


@app.route('/complaint/<int:id>')
def complaint_details(id):
    complaint = db.session.get(Complaint, id)
    if not complaint:
        flash('Complaint not found.', 'danger')
        return redirect(url_for('index'))

    # Check access permission: admin or the owner student
    if session.get('user_type') == 'admin':
        pass
    elif session.get('user_type') == 'student' and session.get('user_id') == complaint.student_id:
        pass
    else:
        flash('Unauthorized access to complaint details.', 'danger')
        return redirect(url_for('index'))

    return render_template('complaint_details.html', complaint=complaint)


# --- Admin Routes ---

@app.route('/admin/dashboard')
@admin_required
def admin_dashboard():
    all_complaints = Complaint.query.order_by(Complaint.created_at.desc()).all()

    total_count = len(all_complaints)
    pending_count = len([c for c in all_complaints if c.status == 'Pending'])
    in_progress_count = len([c for c in all_complaints if c.status == 'In Progress'])
    resolved_count = len([c for c in all_complaints if c.status == 'Resolved'])

    return render_template(
        'admin_dashboard.html',
        complaints=all_complaints[:5], # Recent 5
        total_count=total_count,
        pending_count=pending_count,
        in_progress_count=in_progress_count,
        resolved_count=resolved_count
    )


@app.route('/admin/manage-complaints')
@admin_required
def manage_complaints():
    search_query = request.args.get('search', '').strip()
    status_filter = request.args.get('status', '').strip()

    query = Complaint.query.join(Student)

    if search_query:
        search_pattern = f"%{search_query}%"
        query = query.filter(
            (Complaint.complaint_id.like(search_pattern)) |
            (Complaint.complaint_type.like(search_pattern)) |
            (Complaint.location.like(search_pattern)) |
            (Student.name.like(search_pattern)) |
            (Student.register_number.like(search_pattern))
        )

    if status_filter and status_filter in ['Pending', 'In Progress', 'Resolved', 'Rejected']:
        query = query.filter(Complaint.status == status_filter)

    complaints = query.order_by(Complaint.created_at.desc()).all()

    return render_template(
        'manage_complaints.html',
        complaints=complaints,
        search_query=search_query,
        status_filter=status_filter
    )


@app.route('/admin/update-complaint/<int:id>', methods=['POST'])
@admin_required
def update_complaint_status(id):
    complaint = db.session.get(Complaint, id)
    if not complaint:
        flash('Complaint not found.', 'danger')
        return redirect(url_for('manage_complaints'))

    new_status = request.form.get('status', '').strip()
    admin_remarks = request.form.get('admin_remarks', '').strip()

    valid_statuses = ['Pending', 'In Progress', 'Resolved', 'Rejected']
    if new_status not in valid_statuses:
        flash('Invalid status selected.', 'danger')
        return redirect(url_for('manage_complaints'))

    complaint.status = new_status
    if admin_remarks:
        complaint.admin_remarks = admin_remarks

    # If status is updated to Resolved, automatically save resolved_date
    if new_status == 'Resolved':
        complaint.resolved_date = date.today()

    db.session.commit()
    flash(f'Complaint #{complaint.complaint_id} updated to "{new_status}".', 'success')
    return redirect(url_for('manage_complaints'))


@app.route('/admin/delete-complaint/<int:id>', methods=['POST'])
@admin_required
def delete_complaint(id):
    complaint = db.session.get(Complaint, id)
    if not complaint:
        flash('Complaint not found.', 'danger')
        return redirect(url_for('manage_complaints'))

    complaint_id = complaint.complaint_id
    db.session.delete(complaint)
    db.session.commit()
    flash(f'Complaint #{complaint_id} has been deleted successfully.', 'info')
    return redirect(url_for('manage_complaints'))


if __name__ == '__main__':
    with app.app_context():
        db.create_all()
        seed_default_data()
    app.run(debug=True)
