import os
import uuid
from datetime import datetime, date
from functools import wraps
from flask import Flask, render_template, request, redirect, url_for, flash, session
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'classroom_maintenance_secret_key_123')

# Admin Hardcoded Default Credentials
ADMIN_USERNAME = os.environ.get('ADMIN_USERNAME', 'admin')
ADMIN_PASSWORD = os.environ.get('ADMIN_PASSWORD', 'admin123')

# Database configuration: Default to MySQL URI, fallback/option for SQLite
MYSQL_URI = os.environ.get('DATABASE_URL', 'mysql+pymysql://root:@localhost/classroom_maintenance_db')
SQLITE_URI = 'sqlite:///' + os.path.join(os.path.abspath(os.path.dirname(__file__)), 'classroom_maintenance.db')

use_sqlite = os.environ.get('USE_SQLITE') == '1'
app.config['SQLALCHEMY_DATABASE_URI'] = SQLITE_URI if use_sqlite else MYSQL_URI
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

class Admin(db.Model):
    __tablename__ = 'admins'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

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
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    complaints = db.relationship('Complaint', backref='student', lazy=True, cascade="all, delete-orphan")

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

class Complaint(db.Model):
    __tablename__ = 'complaints'
    id = db.Column(db.Integer, primary_key=True)
    complaint_id = db.Column(db.String(20), unique=True, nullable=False)
    student_id = db.Column(db.Integer, db.ForeignKey('students.id'), nullable=False)
    classroom_number = db.Column(db.String(50), nullable=False)
    complaint_type = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text, nullable=False)
    complaint_date = db.Column(db.Date, nullable=False)
    status = db.Column(db.String(20), default='Pending') # Pending, In Progress, Resolved, Rejected
    admin_remarks = db.Column(db.Text, nullable=True, default='')
    resolved_date = db.Column(db.Date, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

def generate_unique_complaint_id():
    # Format: CMP + 6 random uppercase alphanumeric characters
    unique_str = uuid.uuid4().hex[:6].upper()
    complaint_id = f"CMP-{unique_str}"
    while Complaint.query.filter_by(complaint_id=complaint_id).first() is not None:
        unique_str = uuid.uuid4().hex[:6].upper()
        complaint_id = f"CMP-{unique_str}"
    return complaint_id

def seed_default_admin():
    if Admin.query.filter_by(username=ADMIN_USERNAME).first() is None:
        admin = Admin(username=ADMIN_USERNAME)
        admin.set_password(ADMIN_PASSWORD)
        db.session.add(admin)
        db.session.commit()

# Auth Decorators
def student_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if session.get('user_type') != 'student':
            flash('Please log in as a student to access this page.', 'warning')
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function

def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if session.get('user_type') != 'admin':
            flash('Admin access required. Please log in as Admin.', 'warning')
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
            flash('A student with this Email or Register Number already exists.', 'danger')
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

        flash('Registration successful! Please log in to continue.', 'success')
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
            session.clear()
            session['user_type'] = 'student'
            session['user_id'] = student.id
            session['user_name'] = student.name
            flash(f'Welcome back, {student.name}!', 'success')
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
            flash('Username and password are required.', 'danger')
            return redirect(url_for('admin_login'))

        admin = Admin.query.filter_by(username=username).first()
        if (admin and admin.check_password(password)) or (username == ADMIN_USERNAME and password == ADMIN_PASSWORD):
            session.clear()
            session['user_type'] = 'admin'
            session['user_name'] = 'Administrator'
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
    flash('You have been logged out successfully.', 'info')
    return redirect(url_for('index'))

# Student Dashboard
@app.route('/student/dashboard')
@student_required
def student_dashboard():
    student_id = session.get('user_id')
    student = Student.query.get_or_404(student_id)
    student_complaints = Complaint.query.filter_by(student_id=student_id).all()

    total_complaints = len(student_complaints)
    pending_count = len([c for c in student_complaints if c.status == 'Pending'])
    in_progress_count = len([c for c in student_complaints if c.status == 'In Progress'])
    resolved_count = len([c for c in student_complaints if c.status == 'Resolved'])

    recent_complaints = Complaint.query.filter_by(student_id=student_id).order_by(Complaint.created_at.desc()).limit(5).all()

    return render_template(
        'student_dashboard.html',
        student=student,
        total_complaints=total_complaints,
        pending_count=pending_count,
        in_progress_count=in_progress_count,
        resolved_count=resolved_count,
        recent_complaints=recent_complaints
    )

# Report Classroom Complaint
@app.route('/report-complaint', methods=['GET', 'POST'])
@student_required
def report_complaint():
    if request.method == 'POST':
        classroom_number = request.form.get('classroom_number', '').strip()
        complaint_type = request.form.get('complaint_type', '').strip()
        description = request.form.get('description', '').strip()
        complaint_date_str = request.form.get('complaint_date', '').strip()

        if not classroom_number or not complaint_type or not description or not complaint_date_str:
            flash('All fields are required to submit a complaint.', 'danger')
            return redirect(url_for('report_complaint'))

        try:
            complaint_date = datetime.strptime(complaint_date_str, '%Y-%m-%d').date()
        except ValueError:
            flash('Invalid date format. Please select a valid date.', 'danger')
            return redirect(url_for('report_complaint'))

        complaint_id = generate_unique_complaint_id()
        complaint = Complaint(
            complaint_id=complaint_id,
            student_id=session['user_id'],
            classroom_number=classroom_number,
            complaint_type=complaint_type,
            description=description,
            complaint_date=complaint_date,
            status='Pending'
        )
        db.session.add(complaint)
        db.session.commit()

        flash(f'Complaint submitted successfully! Your Complaint ID is {complaint_id}.', 'success')
        return redirect(url_for('my_complaints'))

    today_str = date.today().isoformat()
    return render_template('report_complaint.html', today=today_str)

# My Complaints (Students can view only their own complaints)
@app.route('/my-complaints')
@student_required
def my_complaints():
    student_id = session.get('user_id')
    complaints = Complaint.query.filter_by(student_id=student_id).order_by(Complaint.created_at.desc()).all()
    return render_template('my_complaints.html', complaints=complaints)

# Complaint Details
@app.route('/complaint/<int:complaint_db_id>')
def complaint_details(complaint_db_id):
    complaint = Complaint.query.get_or_404(complaint_db_id)

    # Authorization check: Student can view only their own complaint, admin can view all
    if session.get('user_type') == 'student':
        if complaint.student_id != session.get('user_id'):
            flash('Access denied. You can only view your own complaints.', 'danger')
            return redirect(url_for('my_complaints'))
    elif session.get('user_type') != 'admin':
        flash('Please log in to view complaint details.', 'warning')
        return redirect(url_for('login'))

    return render_template('complaint_details.html', complaint=complaint)

# Admin Dashboard
@app.route('/admin/dashboard')
@admin_required
def admin_dashboard():
    total_students = Student.query.count()
    all_complaints = Complaint.query.all()

    total_complaints = len(all_complaints)
    pending_count = len([c for c in all_complaints if c.status == 'Pending'])
    in_progress_count = len([c for c in all_complaints if c.status == 'In Progress'])
    resolved_count = len([c for c in all_complaints if c.status == 'Resolved'])

    recent_complaints = Complaint.query.order_by(Complaint.created_at.desc()).limit(5).all()

    return render_template(
        'admin_dashboard.html',
        total_students=total_students,
        total_complaints=total_complaints,
        pending_count=pending_count,
        in_progress_count=in_progress_count,
        resolved_count=resolved_count,
        recent_complaints=recent_complaints
    )

# Admin Manage Complaints (View, Search, Filter)
@app.route('/manage-complaints')
@admin_required
def manage_complaints():
    search_query = request.args.get('search', '').strip()
    status_filter = request.args.get('status', '').strip()

    query = Complaint.query.join(Student)

    if search_query:
        search_pattern = f"%{search_query}%"
        query = query.filter(
            (Complaint.complaint_id.ilike(search_pattern)) |
            (Complaint.classroom_number.ilike(search_pattern)) |
            (Complaint.complaint_type.ilike(search_pattern)) |
            (Student.name.ilike(search_pattern)) |
            (Student.register_number.ilike(search_pattern))
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

# Admin Update Complaint Status & Remarks
@app.route('/admin/complaint/update/<int:complaint_db_id>', methods=['POST'])
@admin_required
def update_complaint_status(complaint_db_id):
    complaint = Complaint.query.get_or_404(complaint_db_id)
    new_status = request.form.get('status', '').strip()
    admin_remarks = request.form.get('admin_remarks', '').strip()

    valid_statuses = ['Pending', 'In Progress', 'Resolved', 'Rejected']
    if new_status not in valid_statuses:
        flash('Invalid status selected.', 'danger')
        return redirect(url_for('manage_complaints'))

    complaint.status = new_status
    complaint.admin_remarks = admin_remarks

    if new_status == 'Resolved':
        complaint.resolved_date = date.today()
    elif new_status != 'Resolved':
        complaint.resolved_date = None

    db.session.commit()
    flash(f'Complaint {complaint.complaint_id} updated successfully to status "{new_status}".', 'success')
    return redirect(url_for('manage_complaints'))

# Admin Delete Complaint
@app.route('/admin/complaint/delete/<int:complaint_db_id>', methods=['POST'])
@admin_required
def delete_complaint(complaint_db_id):
    complaint = Complaint.query.get_or_404(complaint_db_id)
    complaint_id = complaint.complaint_id
    db.session.delete(complaint)
    db.session.commit()
    flash(f'Complaint {complaint_id} deleted successfully.', 'info')
    return redirect(url_for('manage_complaints'))

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
        seed_default_admin()
    app.run(debug=True)
