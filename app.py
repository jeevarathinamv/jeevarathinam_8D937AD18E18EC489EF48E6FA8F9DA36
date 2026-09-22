import os
from datetime import datetime
from functools import wraps
from flask import Flask, render_template, request, redirect, url_for, flash, session
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'student_marks_tracker_secret_key_123')

# Admin Hardcoded Fallback Credentials
ADMIN_USERNAME = os.environ.get('ADMIN_USERNAME', 'admin')
ADMIN_PASSWORD = os.environ.get('ADMIN_PASSWORD', 'admin123')

# Database configuration: Default to MySQL URI, fallback/option for SQLite
MYSQL_URI = os.environ.get('DATABASE_URL', 'mysql+pymysql://root:@localhost/student_marks')
SQLITE_URI = 'sqlite:///' + os.path.join(os.path.abspath(os.path.dirname(__file__)), 'student_marks.db')

use_sqlite = os.environ.get('USE_SQLITE') == '1'
app.config['SQLALCHEMY_DATABASE_URI'] = SQLITE_URI if use_sqlite else MYSQL_URI
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

# Helper function for grade calculation
def calculate_grade_and_result(total_mark):
    if total_mark >= 90:
        grade = 'A+'
    elif total_mark >= 80:
        grade = 'A'
    elif total_mark >= 70:
        grade = 'B'
    elif total_mark >= 60:
        grade = 'C'
    elif total_mark >= 50:
        grade = 'D'
    else:
        grade = 'F'

    if total_mark >= 50:
        result = '✓ Result: PASS'
    else:
        result = '⚠ Result: FAIL'

    return grade, result

class Student(db.Model):
    __tablename__ = 'students'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    register_number = db.Column(db.String(50), unique=True, nullable=False)
    department = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    marks = db.relationship('Mark', backref='student', lazy=True, cascade='all, delete-orphan')

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

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

class Mark(db.Model):
    __tablename__ = 'marks'
    id = db.Column(db.Integer, primary_key=True)
    student_id = db.Column(db.Integer, db.ForeignKey('students.id'), nullable=False)
    register_number = db.Column(db.String(50), nullable=False)
    subject = db.Column(db.String(100), nullable=False)
    internal_test_1 = db.Column(db.Float, nullable=False, default=0.0)
    internal_test_2 = db.Column(db.Float, nullable=False, default=0.0)
    assignment = db.Column(db.Float, nullable=False, default=0.0)
    attendance = db.Column(db.Float, nullable=False, default=0.0)
    total_mark = db.Column(db.Float, nullable=False, default=0.0)
    grade = db.Column(db.String(10), nullable=False)
    result = db.Column(db.String(20), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def update_totals(self):
        self.total_mark = round(self.internal_test_1 + self.internal_test_2 + self.assignment + self.attendance, 2)
        self.grade, self.result = calculate_grade_and_result(self.total_mark)

def seed_default_admin():
    if db.session.get(Admin, 1) is None and Admin.query.filter_by(username=ADMIN_USERNAME).first() is None:
        admin = Admin(username=ADMIN_USERNAME)
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
        register_number = request.form.get('register_number', '').strip().upper()
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
            (Student.email == email_or_reg.lower()) | (Student.register_number == email_or_reg.upper())
        ).first()

        if student and student.check_password(password):
            session['user_type'] = 'student'
            session['user_id'] = student.id
            session['user_name'] = student.name
            flash(f'Welcome back, {student.name}!', 'success')
            return redirect(url_for('student_dashboard'))
        else:
            flash('Invalid credentials. Please check your Email/Register Number and Password.', 'danger')
            return redirect(url_for('login'))

    return render_template('login.html')

# Admin Login
@app.route('/admin/login', methods=['GET', 'POST'])
def admin_login():
    if request.method == 'POST':
        username = request.form.get('username', '').strip()
        password = request.form.get('password', '')

        admin = Admin.query.filter_by(username=username).first()

        if admin and admin.check_password(password):
            session['user_type'] = 'admin'
            session['user_id'] = admin.id
            session['user_name'] = admin.username
            flash('Logged in successfully as Administrator.', 'success')
            return redirect(url_for('admin_dashboard'))
        elif username == ADMIN_USERNAME and password == ADMIN_PASSWORD:
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
    flash('You have been logged out.', 'info')
    return redirect(url_for('index'))

# Student Dashboard
@app.route('/student/dashboard')
@student_required
def student_dashboard():
    student_id = session.get('user_id')
    student = db.session.get(Student, student_id)
    marks = Mark.query.filter_by(student_id=student_id).all()

    total_subjects = len(marks)
    total_marks = sum(m.total_mark for m in marks) if marks else 0.0
    average_marks = round(total_marks / total_subjects, 2) if total_subjects > 0 else 0.0

    if total_subjects == 0:
        result_status = 'N/A (No Marks Added)'
    else:
        has_failed = any(m.total_mark < 50 for m in marks)
        result_status = '⚠ Result: FAIL' if has_failed else '✓ Result: PASS'

    return render_template(
        'student_dashboard.html',
        student=student,
        total_subjects=total_subjects,
        total_marks=total_marks,
        average_marks=average_marks,
        result_status=result_status,
        marks=marks
    )

# Result Tracker Page (for Student)
@app.route('/result')
@student_required
def result():
    student_id = session.get('user_id')
    student = db.session.get(Student, student_id)
    marks = Mark.query.filter_by(student_id=student_id).all()
    return render_template('result.html', student=student, marks=marks)

# Admin Dashboard
@app.route('/admin/dashboard')
@admin_required
def admin_dashboard():
    students = Student.query.order_by(Student.name.asc()).all()
    marks = Mark.query.order_by(Mark.id.desc()).all()
    return render_template('admin_dashboard.html', students=students, marks=marks)

# Marks page / Form page for Admin
@app.route('/marks')
@admin_required
def marks():
    students = Student.query.order_by(Student.name.asc()).all()
    marks_list = Mark.query.order_by(Mark.id.desc()).all()
    return render_template('marks.html', students=students, marks=marks_list)

# Add Internal Marks
@app.route('/admin/marks/add', methods=['POST'])
@admin_required
def add_marks():
    register_number = request.form.get('register_number', '').strip().upper()
    subject = request.form.get('subject', '').strip()

    try:
        internal_test_1 = float(request.form.get('internal_test_1', 0))
        internal_test_2 = float(request.form.get('internal_test_2', 0))
        assignment = float(request.form.get('assignment', 0))
        attendance = float(request.form.get('attendance', 0))
    except ValueError:
        flash('Invalid numeric marks entered.', 'danger')
        return redirect(url_for('marks'))

    student = Student.query.filter_by(register_number=register_number).first()
    if not student:
        flash(f'Student with Register Number "{register_number}" not found.', 'danger')
        return redirect(url_for('marks'))

    if not subject:
        flash('Subject name is required.', 'danger')
        return redirect(url_for('marks'))

    mark = Mark(
        student_id=student.id,
        register_number=student.register_number,
        subject=subject,
        internal_test_1=internal_test_1,
        internal_test_2=internal_test_2,
        assignment=assignment,
        attendance=attendance
    )
    mark.update_totals()

    db.session.add(mark)
    db.session.commit()

    flash(f'Marks added successfully for {student.name} ({student.register_number}) in {subject}.', 'success')
    return redirect(url_for('admin_dashboard'))

# Edit Internal Marks
@app.route('/admin/marks/edit/<int:mark_id>', methods=['POST'])
@admin_required
def edit_marks(mark_id):
    mark = db.session.get(Mark, mark_id)
    if not mark:
        flash('Mark record not found.', 'danger')
        return redirect(url_for('admin_dashboard'))

    subject = request.form.get('subject', '').strip()
    try:
        mark.internal_test_1 = float(request.form.get('internal_test_1', 0))
        mark.internal_test_2 = float(request.form.get('internal_test_2', 0))
        mark.assignment = float(request.form.get('assignment', 0))
        mark.attendance = float(request.form.get('attendance', 0))
    except ValueError:
        flash('Invalid numeric marks entered.', 'danger')
        return redirect(url_for('admin_dashboard'))

    if subject:
        mark.subject = subject

    mark.update_totals()
    db.session.commit()

    flash(f'Marks updated successfully for {mark.subject}.', 'success')
    return redirect(url_for('admin_dashboard'))

# Delete Internal Marks
@app.route('/admin/marks/delete/<int:mark_id>', methods=['POST'])
@admin_required
def delete_marks(mark_id):
    mark = db.session.get(Mark, mark_id)
    if mark:
        db.session.delete(mark)
        db.session.commit()
        flash('Mark record deleted successfully.', 'info')
    else:
        flash('Mark record not found.', 'danger')
    return redirect(url_for('admin_dashboard'))

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
        seed_default_admin()
    app.run(debug=True)
