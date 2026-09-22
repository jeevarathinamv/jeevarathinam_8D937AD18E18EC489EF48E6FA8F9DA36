import os
from datetime import datetime, date
from functools import wraps
from flask import Flask, render_template, request, redirect, url_for, flash, session
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'student_attendance_secret_key_123')

# Admin Credentials fallback
DEFAULT_ADMIN_USERNAME = os.environ.get('ADMIN_USERNAME', 'admin')
DEFAULT_ADMIN_PASSWORD = os.environ.get('ADMIN_PASSWORD', 'admin123')

# Database configuration: Default to MySQL URI (student_attendance), fallback to SQLite for testing
MYSQL_URI = os.environ.get('DATABASE_URL', 'mysql+pymysql://root:@localhost/student_attendance')
SQLITE_URI = 'sqlite:///' + os.path.join(os.path.abspath(os.path.dirname(__file__)), 'student_attendance.db')

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

    attendances = db.relationship('Attendance', backref='student', lazy=True, cascade='all, delete-orphan')

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

class Attendance(db.Model):
    __tablename__ = 'attendance'
    id = db.Column(db.Integer, primary_key=True)
    student_id = db.Column(db.Integer, db.ForeignKey('students.id'), nullable=False)
    subject = db.Column(db.String(100), nullable=False)
    date = db.Column(db.Date, nullable=False)
    status = db.Column(db.String(20), nullable=False)  # 'Present' or 'Absent'
    created_at = db.Column(db.DateTime, default=datetime.utcnow)


def seed_default_admin():
    if Admin.query.count() == 0:
        admin = Admin(username=DEFAULT_ADMIN_USERNAME, email='admin@college.edu')
        admin.set_password(DEFAULT_ADMIN_PASSWORD)
        db.session.add(admin)
        db.session.commit()

# Helper function to calculate student attendance metrics
def get_student_attendance_stats(student_id, subject_filter=None):
    query = Attendance.query.filter_by(student_id=student_id)
    if subject_filter:
        query = query.filter_by(subject=subject_filter)

    records = query.order_by(Attendance.date.desc()).all()
    total_classes = len(records)
    attended_classes = len([r for r in records if r.status == 'Present'])
    absent_classes = len([r for r in records if r.status == 'Absent'])

    if total_classes > 0:
        percentage = round((attended_classes / total_classes) * 100, 2)
    else:
        percentage = 0.0

    status_satisfactory = percentage >= 75.0

    return {
        'records': records,
        'total_classes': total_classes,
        'attended_classes': attended_classes,
        'absent_classes': absent_classes,
        'percentage': percentage,
        'is_satisfactory': status_satisfactory
    }

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

# Home Page
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

        existing_student = db.session.scalar(
            db.select(Student).where(
                (Student.email == email) | (Student.register_number == register_number)
            )
        )

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

        student = db.session.scalar(
            db.select(Student).where(
                (Student.email == email_or_reg.lower()) | (Student.register_number == email_or_reg)
            )
        )

        if student and student.check_password(password):
            session['user_type'] = 'student'
            session['user_id'] = student.id
            session['user_name'] = student.name
            flash(f'Welcome back, {student.name}!', 'success')
            return redirect(url_for('student_dashboard'))
        else:
            flash('Invalid credentials. Please check your details and try again.', 'danger')
            return redirect(url_for('login'))

    return render_template('login.html')

# Admin Login
@app.route('/admin/login', methods=['GET', 'POST'])
def admin_login():
    if request.method == 'POST':
        username_or_email = request.form.get('username', '').strip()
        password = request.form.get('password', '')

        admin = db.session.scalar(
            db.select(Admin).where(
                (Admin.username == username_or_email) | (Admin.email == username_or_email.lower())
            )
        )

        # Fallback to hardcoded credentials if database admin record matches or fallback works
        if admin and admin.check_password(password):
            session['user_type'] = 'admin'
            session['admin_id'] = admin.id
            session['user_name'] = admin.username
            flash('Logged in successfully as Administrator.', 'success')
            return redirect(url_for('admin_dashboard'))
        elif username_or_email == DEFAULT_ADMIN_USERNAME and password == DEFAULT_ADMIN_PASSWORD:
            session['user_type'] = 'admin'
            session['user_name'] = 'admin'
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
    student_id = session.get('user_id')
    student = db.session.get(Student, student_id)
    if not student:
        session.clear()
        return redirect(url_for('login'))

    stats = get_student_attendance_stats(student_id)
    return render_template('student_dashboard.html', student=student, stats=stats)

# Student Attendance Report
@app.route('/student/report')
@student_required
def attendance_report():
    student_id = session.get('user_id')
    student = db.session.get(Student, student_id)
    if not student:
        session.clear()
        return redirect(url_for('login'))

    subject_filter = request.args.get('subject', '').strip()
    stats = get_student_attendance_stats(student_id, subject_filter if subject_filter else None)

    # Get distinct list of subjects for filtering
    subjects = db.session.scalars(
        db.select(Attendance.subject).where(Attendance.student_id == student_id).distinct()
    ).all()

    return render_template(
        'attendance_report.html',
        student=student,
        stats=stats,
        subjects=subjects,
        selected_subject=subject_filter
    )

# Admin Dashboard
@app.route('/admin/dashboard')
@admin_required
def admin_dashboard():
    students = db.session.scalars(db.select(Student).order_by(Student.name)).all()

    student_summary = []
    shortage_students = []

    for s in students:
        stats = get_student_attendance_stats(s.id)
        info = {
            'student': s,
            'total_classes': stats['total_classes'],
            'attended_classes': stats['attended_classes'],
            'absent_classes': stats['absent_classes'],
            'percentage': stats['percentage'],
            'is_satisfactory': stats['is_satisfactory']
        }
        student_summary.append(info)
        if stats['total_classes'] > 0 and not stats['is_satisfactory']:
            shortage_students.append(info)

    all_attendances = db.session.scalars(
        db.select(Attendance).order_by(Attendance.date.desc(), Attendance.id.desc())
    ).all()

    return render_template(
        'admin_dashboard.html',
        students=students,
        student_summary=student_summary,
        shortage_students=shortage_students,
        attendances=all_attendances,
        today=date.today().isoformat()
    )

# Admin Attendance Page & Mark Attendance Route
@app.route('/admin/attendance', methods=['GET', 'POST'])
@admin_required
def attendance_management():
    if request.method == 'POST':
        student_id = request.form.get('student_id', type=int)
        subject = request.form.get('subject', '').strip()
        date_str = request.form.get('date', '')
        status = request.form.get('status', '').strip()

        if not student_id or not subject or not date_str or not status:
            flash('All attendance fields are required.', 'danger')
            return redirect(url_for('attendance_management'))

        if status not in ['Present', 'Absent']:
            flash('Invalid attendance status.', 'danger')
            return redirect(url_for('attendance_management'))

        try:
            attendance_date = datetime.strptime(date_str, '%Y-%m-%d').date()
        except ValueError:
            flash('Invalid date format.', 'danger')
            return redirect(url_for('attendance_management'))

        student = db.session.get(Student, student_id)
        if not student:
            flash('Selected student not found.', 'danger')
            return redirect(url_for('attendance_management'))

        record = Attendance(
            student_id=student_id,
            subject=subject,
            date=attendance_date,
            status=status
        )
        db.session.add(record)
        db.session.commit()

        flash(f'Attendance recorded successfully for {student.name} ({subject} - {status}).', 'success')
        return redirect(url_for('attendance_management'))

    students = db.session.scalars(db.select(Student).order_by(Student.name)).all()
    records = db.session.scalars(
        db.select(Attendance).order_by(Attendance.date.desc(), Attendance.id.desc())
    ).all()
    today_str = date.today().isoformat()

    return render_template('attendance.html', students=students, records=records, today=today_str)

# Delete Attendance Record (Admin)
@app.route('/admin/attendance/delete/<int:record_id>', methods=['POST'])
@admin_required
def delete_attendance(record_id):
    record = db.session.get(Attendance, record_id)
    if record:
        db.session.delete(record)
        db.session.commit()
        flash('Attendance record deleted successfully.', 'info')
    else:
        flash('Record not found.', 'danger')
    return redirect(request.referrer or url_for('admin_dashboard'))

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
        seed_default_admin()
    app.run(debug=True)
