import os
import random
import string
from datetime import datetime, date
from functools import wraps
from flask import Flask, render_template, request, redirect, url_for, flash, session
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'lab_computer_fault_secret_key_2025')

# Database configuration: Default to MySQL URI, fallback to SQLite when requested
MYSQL_URI = os.environ.get('DATABASE_URL', 'mysql+pymysql://root:@localhost/lab_computer_fault_db')
SQLITE_URI = 'sqlite:///' + os.path.join(os.path.abspath(os.path.dirname(__file__)), 'lab_fault.db')

use_sqlite = os.environ.get('USE_SQLITE') == '1'
app.config['SQLALCHEMY_DATABASE_URI'] = SQLITE_URI if use_sqlite else MYSQL_URI
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

# Database Models
class Admin(db.Model):
    __tablename__ = 'admins'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), unique=True, nullable=False)
    password = db.Column(db.String(255), nullable=False)

    def set_password(self, password_str):
        self.password = generate_password_hash(password_str)

    def check_password(self, password_str):
        return check_password_hash(self.password, password_str)

class Student(db.Model):
    __tablename__ = 'students'
    id = db.Column(db.Integer, primary_key=True)
    student_name = db.Column(db.String(100), nullable=False)
    register_number = db.Column(db.String(50), unique=True, nullable=False)
    department = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(255), nullable=False)

    fault_reports = db.relationship('FaultReport', backref='student', lazy=True, cascade="all, delete-orphan")

    def set_password(self, password_str):
        self.password = generate_password_hash(password_str)

    def check_password(self, password_str):
        return check_password_hash(self.password, password_str)

class Computer(db.Model):
    __tablename__ = 'computers'
    id = db.Column(db.Integer, primary_key=True)
    computer_number = db.Column(db.String(50), nullable=False)
    lab_name = db.Column(db.String(100), nullable=False)
    computer_name = db.Column(db.String(100), nullable=False)
    ip_address = db.Column(db.String(50), nullable=False)
    status = db.Column(db.String(50), default='Working') # Working, Faulty, Under Maintenance

    fault_reports = db.relationship('FaultReport', backref='computer', lazy=True)

class FaultReport(db.Model):
    __tablename__ = 'fault_reports'
    id = db.Column(db.Integer, primary_key=True)
    complaint_id = db.Column(db.String(50), unique=True, nullable=False)
    student_id = db.Column(db.Integer, db.ForeignKey('students.id'), nullable=False)
    computer_id = db.Column(db.Integer, db.ForeignKey('computers.id'), nullable=True)
    lab_name = db.Column(db.String(100), nullable=False)
    computer_number = db.Column(db.String(50), nullable=False)
    fault_type = db.Column(db.String(100), nullable=False)
    problem_description = db.Column(db.Text, nullable=False)
    report_date = db.Column(db.Date, nullable=False, default=date.today)
    status = db.Column(db.String(50), default='Pending') # Pending, In Progress, Resolved, Rejected
    admin_remarks = db.Column(db.Text, nullable=True)
    resolved_date = db.Column(db.Date, nullable=True)

# Helper function to generate Unique Complaint ID
def generate_complaint_id():
    date_str = datetime.now().strftime("%Y%m%d")
    random_str = ''.join(random.choices(string.digits, k=4))
    complaint_id = f"CMP-{date_str}-{random_str}"
    # Ensure uniqueness
    while FaultReport.query.filter_by(complaint_id=complaint_id).first():
        random_str = ''.join(random.choices(string.digits, k=4))
        complaint_id = f"CMP-{date_str}-{random_str}"
    return complaint_id

# Seed Default Data
def seed_default_data():
    # Seed default admin if missing
    if Admin.query.count() == 0:
        default_admin = Admin(username='admin')
        default_admin.set_password('admin123')
        db.session.add(default_admin)
        db.session.commit()

    # Seed default computers if missing
    if Computer.query.count() == 0:
        sample_computers = [
            Computer(computer_number='COMP-101', lab_name='Computer Lab 1', computer_name='Dell OptiPlex 3080', ip_address='192.168.1.101', status='Working'),
            Computer(computer_number='COMP-102', lab_name='Computer Lab 1', computer_name='Dell OptiPlex 3080', ip_address='192.168.1.102', status='Working'),
            Computer(computer_number='COMP-103', lab_name='Computer Lab 1', computer_name='HP ProDesk 400', ip_address='192.168.1.103', status='Faulty'),
            Computer(computer_number='COMP-201', lab_name='MCA Programming Lab', computer_name='Lenovo ThinkCentre', ip_address='192.168.2.101', status='Working'),
            Computer(computer_number='COMP-202', lab_name='MCA Programming Lab', computer_name='Lenovo ThinkCentre', ip_address='192.168.2.102', status='Under Maintenance'),
        ]
        db.session.add_all(sample_computers)
        db.session.commit()

# Auth Decorators
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
            flash('Admin access required. Please log in as Administrator.', 'warning')
            return redirect(url_for('admin_login'))
        return f(*args, **kwargs)
    return decorated_function

# Routes

@app.route('/')
def index():
    return render_template('index.html')

# Student Registration
@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        student_name = request.form.get('student_name', '').strip()
        register_number = request.form.get('register_number', '').strip()
        department = request.form.get('department', '').strip()
        email = request.form.get('email', '').strip().lower()
        password = request.form.get('password', '')

        if not student_name or not register_number or not department or not email or not password:
            flash('All fields are required for registration.', 'danger')
            return redirect(url_for('register'))

        existing_student = Student.query.filter(
            (Student.email == email) | (Student.register_number == register_number)
        ).first()

        if existing_student:
            flash('A student with this Email or Register Number already exists.', 'danger')
            return redirect(url_for('register'))

        student = Student(
            student_name=student_name,
            register_number=register_number,
            department=department,
            email=email
        )
        student.set_password(password)
        db.session.add(student)
        db.session.commit()

        flash('Registration successful! Please login to report faults.', 'success')
        return redirect(url_for('login'))

    return render_template('register.html')

# Student Login
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email_or_reg = request.form.get('email_or_reg', '').strip()
        password = request.form.get('password', '')

        if not email_or_reg or not password:
            flash('Please enter both Register Number/Email and Password.', 'danger')
            return redirect(url_for('login'))

        student = Student.query.filter(
            (Student.email == email_or_reg.lower()) | (Student.register_number == email_or_reg)
        ).first()

        if student and student.check_password(password):
            session['user_type'] = 'student'
            session['user_id'] = student.id
            session['user_name'] = student.student_name
            flash(f'Welcome back, {student.student_name}!', 'success')
            return redirect(url_for('student_dashboard'))
        else:
            flash('Invalid credentials. Please check your Register Number/Email and Password.', 'danger')
            return redirect(url_for('login'))

    return render_template('login.html')

# Admin Login
@app.route('/admin/login', methods=['GET', 'POST'])
def admin_login():
    if request.method == 'POST':
        username = request.form.get('username', '').strip()
        password = request.form.get('password', '')

        if not username or not password:
            flash('Please enter Admin Username and Password.', 'danger')
            return redirect(url_for('admin_login'))

        admin = Admin.query.filter_by(username=username).first()

        if admin and admin.check_password(password):
            session['user_type'] = 'admin'
            session['user_id'] = admin.id
            session['user_name'] = admin.username
            flash('Logged in successfully as Administrator.', 'success')
            return redirect(url_for('admin_dashboard'))
        else:
            flash('Invalid Admin Username or Password.', 'danger')
            return redirect(url_for('admin_login'))

    return render_template('admin_login.html')

# Logout
@app.route('/logout')
def logout():
    session.clear()
    flash('You have been logged out successfully.', 'info')
    return redirect(url_for('index'))

# Student Dashboard
@app.route('/student/dashboard')
@student_required
def student_dashboard():
    student_id = session.get('user_id')
    student = db.session.get(Student, student_id)

    student_reports = FaultReport.query.filter_by(student_id=student_id).order_by(FaultReport.report_date.desc(), FaultReport.id.desc()).all()

    total_complaints = len(student_reports)
    pending_complaints = len([r for r in student_reports if r.status == 'Pending'])
    in_progress_complaints = len([r for r in student_reports if r.status == 'In Progress'])
    resolved_complaints = len([r for r in student_reports if r.status == 'Resolved'])

    recent_reports = student_reports[:5]

    return render_template(
        'student_dashboard.html',
        student=student,
        total_complaints=total_complaints,
        pending_complaints=pending_complaints,
        in_progress_complaints=in_progress_complaints,
        resolved_complaints=resolved_complaints,
        recent_reports=recent_reports
    )

# Report Fault
@app.route('/student/report_fault', methods=['GET', 'POST'])
@student_required
def report_fault():
    if request.method == 'POST':
        lab_name = request.form.get('lab_name', '').strip()
        computer_number = request.form.get('computer_number', '').strip()
        fault_type = request.form.get('fault_type', '').strip()
        problem_description = request.form.get('problem_description', '').strip()
        report_date_str = request.form.get('report_date', '').strip()

        if not lab_name or not computer_number or not fault_type or not problem_description:
            flash('Please fill in all required fields.', 'danger')
            return redirect(url_for('report_fault'))

        try:
            report_date = datetime.strptime(report_date_str, '%Y-%m-%d').date() if report_date_str else date.today()
        except ValueError:
            report_date = date.today()

        # Find matching computer if registered in system
        computer = Computer.query.filter_by(lab_name=lab_name, computer_number=computer_number).first()
        computer_id = computer.id if computer else None

        # Update computer status to Faulty if matching computer is found
        if computer and computer.status == 'Working':
            computer.status = 'Faulty'

        complaint_id = generate_complaint_id()
        student_id = session.get('user_id')

        report = FaultReport(
            complaint_id=complaint_id,
            student_id=student_id,
            computer_id=computer_id,
            lab_name=lab_name,
            computer_number=computer_number,
            fault_type=fault_type,
            problem_description=problem_description,
            report_date=report_date,
            status='Pending'
        )

        db.session.add(report)
        db.session.commit()

        flash(f'Fault report submitted successfully! Generated Complaint ID: {complaint_id}', 'success')
        return redirect(url_for('my_reports'))

    computers = Computer.query.all()
    today_str = date.today().isoformat()
    fault_types = [
        'Computer Not Starting',
        'Keyboard Problem',
        'Mouse Problem',
        'Monitor Problem',
        'Internet Problem',
        'Software Problem',
        'Other'
    ]
    return render_template('report_fault.html', computers=computers, today=today_str, fault_types=fault_types)

# My Reports
@app.route('/student/my_reports')
@student_required
def my_reports():
    student_id = session.get('user_id')
    reports = FaultReport.query.filter_by(student_id=student_id).order_by(FaultReport.id.desc()).all()
    return render_template('my_reports.html', reports=reports)

# Fault Details
@app.route('/fault_details/<int:report_id>')
def fault_details(report_id):
    report = FaultReport.query.get_or_404(report_id)

    # Check access permission: Admin or the student who submitted it
    user_type = session.get('user_type')
    user_id = session.get('user_id')

    if not user_type:
        flash('Please login to view fault details.', 'warning')
        return redirect(url_for('login'))

    if user_type == 'student' and report.student_id != user_id:
        flash('You do not have permission to view this report.', 'danger')
        return redirect(url_for('student_dashboard'))

    return render_template('fault_details.html', report=report)

# Admin Dashboard
@app.route('/admin/dashboard')
@admin_required
def admin_dashboard():
    all_reports = FaultReport.query.order_by(FaultReport.id.desc()).all()
    total_reports = len(all_reports)
    pending_reports = len([r for r in all_reports if r.status == 'Pending'])
    in_progress_reports = len([r for r in all_reports if r.status == 'In Progress'])
    resolved_reports = len([r for r in all_reports if r.status == 'Resolved'])

    recent_reports = all_reports[:5]
    computers = Computer.query.all()

    return render_template(
        'admin_dashboard.html',
        total_reports=total_reports,
        pending_reports=pending_reports,
        in_progress_reports=in_progress_reports,
        resolved_reports=resolved_reports,
        recent_reports=recent_reports,
        computers=computers
    )

# Fault Report Management (Search & Filter)
@app.route('/admin/manage_reports')
@admin_required
def manage_reports():
    search_query = request.args.get('search', '').strip()
    status_filter = request.args.get('status', '').strip()

    query = FaultReport.query

    if status_filter:
        query = query.filter_by(status=status_filter)

    if search_query:
        search_pattern = f"%{search_query}%"
        query = query.filter(
            (FaultReport.complaint_id.ilike(search_pattern)) |
            (FaultReport.computer_number.ilike(search_pattern)) |
            (FaultReport.lab_name.ilike(search_pattern)) |
            (FaultReport.fault_type.ilike(search_pattern)) |
            (FaultReport.status.ilike(search_pattern))
        )

    reports = query.order_by(FaultReport.id.desc()).all()

    fault_types = [
        'Computer Not Starting',
        'Keyboard Problem',
        'Mouse Problem',
        'Monitor Problem',
        'Internet Problem',
        'Software Problem',
        'Other'
    ]

    return render_template(
        'manage_reports.html',
        reports=reports,
        search_query=search_query,
        status_filter=status_filter,
        fault_types=fault_types
    )

# Update Fault Report Status & Admin Remarks
@app.route('/admin/update_report/<int:report_id>', methods=['POST'])
@admin_required
def update_report(report_id):
    report = FaultReport.query.get_or_404(report_id)
    new_status = request.form.get('status', '').strip()
    admin_remarks = request.form.get('admin_remarks', '').strip()

    if new_status in ['Pending', 'In Progress', 'Resolved', 'Rejected']:
        report.status = new_status
        report.admin_remarks = admin_remarks

        if new_status == 'Resolved':
            report.resolved_date = date.today()
            # If associated computer was marked faulty, option to revert to Working
            if report.computer and report.computer.status == 'Faulty':
                report.computer.status = 'Working'
        else:
            report.resolved_date = None

        db.session.commit()
        flash(f'Complaint {report.complaint_id} updated to status "{new_status}".', 'success')
    else:
        flash('Invalid status selected.', 'danger')

    return redirect(request.referrer or url_for('manage_reports'))

# Computer Management: View
@app.route('/admin/manage_computers')
@admin_required
def manage_computers():
    computers = Computer.query.order_by(Computer.id.desc()).all()
    return render_template('manage_computers.html', computers=computers)

# Add Computer
@app.route('/admin/add_computer', methods=['GET', 'POST'])
@admin_required
def add_computer():
    if request.method == 'POST':
        computer_number = request.form.get('computer_number', '').strip()
        lab_name = request.form.get('lab_name', '').strip()
        computer_name = request.form.get('computer_name', '').strip()
        ip_address = request.form.get('ip_address', '').strip()
        status = request.form.get('status', 'Working').strip()

        if not computer_number or not lab_name or not computer_name or not ip_address:
            flash('All fields are required to add a computer.', 'danger')
            return redirect(url_for('add_computer'))

        computer = Computer(
            computer_number=computer_number,
            lab_name=lab_name,
            computer_name=computer_name,
            ip_address=ip_address,
            status=status
        )
        db.session.add(computer)
        db.session.commit()

        flash(f'Computer {computer_number} added successfully.', 'success')
        return redirect(url_for('manage_computers'))

    return render_template('add_computer.html')

# Edit Computer
@app.route('/admin/edit_computer/<int:computer_id>', methods=['GET', 'POST'])
@admin_required
def edit_computer(computer_id):
    computer = Computer.query.get_or_404(computer_id)

    if request.method == 'POST':
        computer.computer_number = request.form.get('computer_number', '').strip()
        computer.lab_name = request.form.get('lab_name', '').strip()
        computer.computer_name = request.form.get('computer_name', '').strip()
        computer.ip_address = request.form.get('ip_address', '').strip()
        computer.status = request.form.get('status', 'Working').strip()

        if not computer.computer_number or not computer.lab_name or not computer.computer_name or not computer.ip_address:
            flash('All fields are required.', 'danger')
            return redirect(url_for('edit_computer', computer_id=computer_id))

        db.session.commit()
        flash(f'Computer {computer.computer_number} updated successfully.', 'success')
        return redirect(url_for('manage_computers'))

    return render_template('edit_computer.html', computer=computer)

# Delete Computer
@app.route('/admin/delete_computer/<int:computer_id>', methods=['POST'])
@admin_required
def delete_computer(computer_id):
    computer = Computer.query.get_or_404(computer_id)
    db.session.delete(computer)
    db.session.commit()
    flash('Computer record deleted successfully.', 'info')
    return redirect(url_for('manage_computers'))

# Student Management: View
@app.route('/admin/manage_students')
@admin_required
def manage_students():
    students = Student.query.order_by(Student.id.desc()).all()
    return render_template('manage_students.html', students=students)

# Delete Student
@app.route('/admin/delete_student/<int:student_id>', methods=['POST'])
@admin_required
def delete_student(student_id):
    student = Student.query.get_or_404(student_id)
    db.session.delete(student)
    db.session.commit()
    flash('Student account deleted successfully.', 'info')
    return redirect(url_for('manage_students'))

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
        seed_default_data()
    app.run(debug=True)
