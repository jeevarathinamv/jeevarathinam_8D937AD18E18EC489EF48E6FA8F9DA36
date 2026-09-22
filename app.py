import os
from datetime import datetime, date
from functools import wraps
from flask import Flask, render_template, request, redirect, url_for, flash, session
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'student_leave_management_secret_key_2025')

# Admin Credentials fallback / env
ADMIN_USERNAME = os.environ.get('ADMIN_USERNAME', 'admin')
ADMIN_PASSWORD = os.environ.get('ADMIN_PASSWORD', 'admin123')

# Database configuration: Default to MySQL URI, fallback/option for SQLite
MYSQL_URI = os.environ.get('DATABASE_URL', 'mysql+pymysql://root:@localhost/student_leave')
SQLITE_URI = 'sqlite:///' + os.path.join(os.path.abspath(os.path.dirname(__file__)), 'student_leave.db')

use_sqlite = os.environ.get('USE_SQLITE') == '1'
app.config['SQLALCHEMY_DATABASE_URI'] = SQLITE_URI if use_sqlite else MYSQL_URI
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

class Student(db.Model):
    __tablename__ = 'students'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    register_number = db.Column(db.String(50), unique=True, nullable=False)
    department = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    leave_requests = db.relationship('LeaveRequest', backref='student', lazy=True, cascade='all, delete-orphan')

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

class Admin(db.Model):
    __tablename__ = 'admins'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

class LeaveRequest(db.Model):
    __tablename__ = 'leave_requests'
    id = db.Column(db.Integer, primary_key=True)
    student_id = db.Column(db.Integer, db.ForeignKey('students.id'), nullable=False)
    leave_type = db.Column(db.String(50), nullable=False) # Medical, Personal, Academic, Duty Leave, Emergency, etc.
    from_date = db.Column(db.Date, nullable=False)
    to_date = db.Column(db.Date, nullable=False)
    reason = db.Column(db.Text, nullable=False)
    status = db.Column(db.String(20), default='Pending') # Pending, Approved, Rejected
    admin_reply = db.Column(db.Text, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

def seed_default_admin():
    if Admin.query.count() == 0:
        admin = Admin(
            username=ADMIN_USERNAME,
            email='admin@college.edu'
        )
        admin.set_password(ADMIN_PASSWORD)
        db.session.add(admin)
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
            flash('Admin access required.', 'warning')
            return redirect(url_for('admin_login'))
        return f(*args, **kwargs)
    return decorated_function

@app.route('/')
def index():
    return render_template('index.html')

# Student Registration
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

# Student Login
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email_or_reg = request.form.get('email_or_reg', '').strip()
        password = request.form.get('password', '')

        student = Student.query.filter(
            (Student.email == email_or_reg.lower()) | (Student.register_number == email_or_reg)
        ).first()

        if student and student.check_password(password):
            session['user_type'] = 'student'
            session['student_id'] = student.id
            session['user_name'] = student.name
            flash(f'Welcome back, {student.name}!', 'success')
            return redirect(url_for('student_dashboard'))
        else:
            flash('Invalid credentials. Please check your Email / Register Number and Password.', 'danger')
            return redirect(url_for('login'))

    return render_template('login.html')

# Admin Login
@app.route('/admin/login', methods=['GET', 'POST'])
def admin_login():
    if request.method == 'POST':
        username = request.form.get('username', '').strip()
        password = request.form.get('password', '')

        admin = Admin.query.filter(
            (Admin.username == username) | (Admin.email == username.lower())
        ).first()

        if admin and admin.check_password(password):
            session['user_type'] = 'admin'
            session['admin_id'] = admin.id
            session['user_name'] = admin.username
            flash('Logged in successfully as Administrator.', 'success')
            return redirect(url_for('admin_dashboard'))
        elif username == ADMIN_USERNAME and password == ADMIN_PASSWORD:
            session['user_type'] = 'admin'
            session['admin_id'] = 1
            session['user_name'] = ADMIN_USERNAME
            flash('Logged in successfully as Administrator.', 'success')
            return redirect(url_for('admin_dashboard'))
        else:
            flash('Invalid admin credentials.', 'danger')
            return redirect(url_for('admin_login'))

    return render_template('admin_login.html')

# Logout
@app.route('/logout')
def logout():
    session.clear()
    flash('You have been logged out.', 'info')
    return redirect(url_for('index'))

# Student Dashboard
@app.route('/student/dashboard')
@student_required
def student_dashboard():
    student_id = session.get('student_id')
    student = db.session.get(Student, student_id)
    if not student:
        session.clear()
        return redirect(url_for('login'))

    leave_requests = LeaveRequest.query.filter_by(student_id=student_id).order_by(LeaveRequest.created_at.desc()).all()

    total_requests = len(leave_requests)
    pending_requests = len([r for r in leave_requests if r.status == 'Pending'])
    approved_requests = len([r for r in leave_requests if r.status == 'Approved'])
    rejected_requests = len([r for r in leave_requests if r.status == 'Rejected'])

    return render_template(
        'student_dashboard.html',
        student=student,
        recent_requests=leave_requests[:5],
        total_requests=total_requests,
        pending_requests=pending_requests,
        approved_requests=approved_requests,
        rejected_requests=rejected_requests
    )

# Apply Leave
@app.route('/student/apply-leave', methods=['GET', 'POST'])
@student_required
def apply_leave():
    if request.method == 'POST':
        student_id = session.get('student_id')
        leave_type = request.form.get('leave_type', '').strip()
        from_date_str = request.form.get('from_date', '')
        to_date_str = request.form.get('to_date', '')
        reason = request.form.get('reason', '').strip()

        if not leave_type or not from_date_str or not to_date_str or not reason:
            flash('All fields are required.', 'danger')
            return redirect(url_for('apply_leave'))

        try:
            from_date = datetime.strptime(from_date_str, '%Y-%m-%d').date()
            to_date = datetime.strptime(to_date_str, '%Y-%m-%d').date()
        except ValueError:
            flash('Invalid date format.', 'danger')
            return redirect(url_for('apply_leave'))

        if to_date < from_date:
            flash('To Date cannot be earlier than From Date.', 'danger')
            return redirect(url_for('apply_leave'))

        leave_req = LeaveRequest(
            student_id=student_id,
            leave_type=leave_type,
            from_date=from_date,
            to_date=to_date,
            reason=reason,
            status='Pending'
        )
        db.session.add(leave_req)
        db.session.commit()

        flash('Leave request submitted successfully!', 'success')
        return redirect(url_for('leave_history'))

    today_str = date.today().isoformat()
    return render_template('apply_leave.html', today=today_str)

# Leave History
@app.route('/student/leave-history')
@student_required
def leave_history():
    student_id = session.get('student_id')
    leave_requests = LeaveRequest.query.filter_by(student_id=student_id).order_by(LeaveRequest.created_at.desc()).all()
    return render_template('leave_history.html', leave_requests=leave_requests)

# Admin Dashboard
@app.route('/admin/dashboard')
@admin_required
def admin_dashboard():
    leave_requests = LeaveRequest.query.order_by(LeaveRequest.created_at.desc()).all()

    total_requests = len(leave_requests)
    pending_requests = len([r for r in leave_requests if r.status == 'Pending'])
    approved_requests = len([r for r in leave_requests if r.status == 'Approved'])
    rejected_requests = len([r for r in leave_requests if r.status == 'Rejected'])

    return render_template(
        'admin_dashboard.html',
        leave_requests=leave_requests,
        total_requests=total_requests,
        pending_requests=pending_requests,
        approved_requests=approved_requests,
        rejected_requests=rejected_requests
    )

# Admin Action on Leave Request (Approve, Reject, Update Reply)
@app.route('/admin/leave/action/<int:request_id>', methods=['POST'])
@admin_required
def update_leave_status(request_id):
    leave_req = db.session.get(LeaveRequest, request_id)
    if not leave_req:
        flash('Leave request not found.', 'danger')
        return redirect(url_for('admin_dashboard'))

    new_status = request.form.get('status', leave_req.status)
    admin_reply = request.form.get('admin_reply', '').strip()

    if new_status not in ['Pending', 'Approved', 'Rejected']:
        flash('Invalid status selected.', 'danger')
        return redirect(url_for('admin_dashboard'))

    leave_req.status = new_status
    if admin_reply:
        leave_req.admin_reply = admin_reply

    db.session.commit()
    flash(f'Leave request #{leave_req.id} updated to {new_status}.', 'success')
    return redirect(url_for('admin_dashboard'))

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
        seed_default_admin()
    app.run(debug=True)
