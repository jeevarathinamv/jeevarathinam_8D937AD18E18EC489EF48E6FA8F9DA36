import os
from datetime import datetime
from functools import wraps
from flask import Flask, render_template, request, redirect, url_for, flash, session
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'student_subject_reg_secret_key_2025')

# Admin Hardcoded Credentials fallback
ADMIN_USERNAME = os.environ.get('ADMIN_USERNAME', 'admin')
ADMIN_PASSWORD = os.environ.get('ADMIN_PASSWORD', 'admin123')

# Database configuration: Default to MySQL URI, fallback/option for SQLite
MYSQL_URI = os.environ.get('DATABASE_URL', 'mysql+pymysql://root:@localhost/subject_registration_db')
SQLITE_URI = 'sqlite:///' + os.path.join(os.path.abspath(os.path.dirname(__file__)), 'subject_registration.db')

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

    def set_password(self, pwd):
        self.password = generate_password_hash(pwd)

    def check_password(self, pwd):
        return check_password_hash(self.password, pwd)

class Student(db.Model):
    __tablename__ = 'students'
    id = db.Column(db.Integer, primary_key=True)
    student_name = db.Column(db.String(100), nullable=False)
    register_number = db.Column(db.String(50), unique=True, nullable=False)
    department = db.Column(db.String(100), nullable=False)
    year = db.Column(db.Integer, nullable=False)
    semester = db.Column(db.Integer, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(255), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    registrations = db.relationship('Registration', backref='student', cascade='all, delete-orphan', lazy=True)

    def set_password(self, pwd):
        self.password = generate_password_hash(pwd)

    def check_password(self, pwd):
        return check_password_hash(self.password, pwd)

class Subject(db.Model):
    __tablename__ = 'subjects'
    id = db.Column(db.Integer, primary_key=True)
    subject_name = db.Column(db.String(100), nullable=False)
    subject_code = db.Column(db.String(20), unique=True, nullable=False)
    department = db.Column(db.String(100), nullable=False)
    semester = db.Column(db.Integer, nullable=False)
    subject_type = db.Column(db.String(20), nullable=False) # Core, Elective, Practical
    credits = db.Column(db.Integer, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    registrations = db.relationship('Registration', backref='subject', cascade='all, delete-orphan', lazy=True)

class Registration(db.Model):
    __tablename__ = 'registrations'
    id = db.Column(db.Integer, primary_key=True)
    student_id = db.Column(db.Integer, db.ForeignKey('students.id'), nullable=False)
    subject_id = db.Column(db.Integer, db.ForeignKey('subjects.id'), nullable=False)
    registration_date = db.Column(db.DateTime, default=datetime.utcnow)
    status = db.Column(db.String(20), default='Registered') # Registered, Cancelled

def seed_default_data():
    # Create default admin if not exists
    if Admin.query.filter_by(username=ADMIN_USERNAME).first() is None:
        admin = Admin(username=ADMIN_USERNAME)
        admin.set_password(ADMIN_PASSWORD)
        db.session.add(admin)

    # Create initial subjects if none exist
    if Subject.query.count() == 0:
        sample_subjects = [
            Subject(subject_name='Advanced Java Programming', subject_code='MCA101', department='Computer Applications', semester=1, subject_type='Core', credits=4),
            Subject(subject_name='Database Management Systems', subject_code='MCA102', department='Computer Applications', semester=1, subject_type='Core', credits=4),
            Subject(subject_name='Web Technologies Lab', subject_code='MCA103', department='Computer Applications', semester=1, subject_type='Practical', credits=2),
            Subject(subject_name='Cloud Computing', subject_code='MCA104', department='Computer Applications', semester=1, subject_type='Elective', credits=3),
            Subject(subject_name='Python Application Programming', subject_code='MCA201', department='Computer Applications', semester=2, subject_type='Core', credits=4),
            Subject(subject_name='Data Structures and Algorithms', subject_code='MCA202', department='Computer Applications', semester=2, subject_type='Core', credits=4),
            Subject(subject_name='Software Engineering Lab', subject_code='MCA203', department='Computer Applications', semester=2, subject_type='Practical', credits=2),
            Subject(subject_name='Cyber Security & Cyber Laws', subject_code='MCA204', department='Computer Applications', semester=2, subject_type='Elective', credits=3),
        ]
        db.session.add_all(sample_subjects)

    db.session.commit()

# Authentication Decorators
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
            flash('Admin login required to access this area.', 'warning')
            return redirect(url_for('admin_login'))
        return f(*args, **kwargs)
    return decorated_function

# Public Routes
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
        year = request.form.get('year', type=int)
        semester = request.form.get('semester', type=int)
        email = request.form.get('email', '').strip().lower()
        password = request.form.get('password', '')

        if not student_name or not register_number or not department or not year or not semester or not email or not password:
            flash('All registration fields are required.', 'danger')
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
            year=year,
            semester=semester,
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

        student = Student.query.filter(
            (Student.email == email_or_reg.lower()) | (Student.register_number == email_or_reg)
        ).first()

        if student and student.check_password(password):
            session['user_type'] = 'student'
            session['user_id'] = student.id
            session['student_name'] = student.student_name
            session['department'] = student.department
            session['semester'] = student.semester
            flash(f'Welcome back, {student.student_name}!', 'success')
            return redirect(url_for('student_dashboard'))
        else:
            flash('Invalid email/register number or password.', 'danger')
            return redirect(url_for('login'))

    return render_template('login.html')

# Admin Login
@app.route('/admin/login', methods=['GET', 'POST'])
def admin_login():
    if request.method == 'POST':
        username = request.form.get('username', '').strip()
        password = request.form.get('password', '')

        admin = Admin.query.filter_by(username=username).first()
        if (admin and admin.check_password(password)) or (username == ADMIN_USERNAME and password == ADMIN_PASSWORD):
            session['user_type'] = 'admin'
            session['user_id'] = admin.id if admin else 1
            session['admin_username'] = username
            flash('Logged in successfully as Admin.', 'success')
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
    student = Student.query.get(student_id)

    if not student:
        session.clear()
        return redirect(url_for('login'))

    # Available subjects matching student's department and semester
    available_subjects = Subject.query.filter_by(
        department=student.department,
        semester=student.semester
    ).all()

    # Registered subjects for this student
    my_registrations = Registration.query.filter_by(
        student_id=student_id,
        status='Registered'
    ).all()

    total_credits = sum(reg.subject.credits for reg in my_registrations)

    return render_template(
        'student_dashboard.html',
        student=student,
        available_count=len(available_subjects),
        registered_count=len(my_registrations),
        total_credits=total_credits
    )

# Available Subjects
@app.route('/student/subjects')
@student_required
def subjects():
    student_id = session.get('user_id')
    student = Student.query.get(student_id)

    # Search & Filter parameters
    search_query = request.args.get('search', '').strip()
    type_filter = request.args.get('type', '').strip()
    sem_filter = request.args.get('semester', type=int)

    # Base query restricted to student's department & semester by default
    query = Subject.query.filter_by(department=student.department, semester=student.semester)

    if sem_filter:
        query = query.filter_by(semester=sem_filter)

    if type_filter:
        query = query.filter_by(subject_type=type_filter)

    if search_query:
        query = query.filter(
            (Subject.subject_name.ilike(f'%{search_query}%')) |
            (Subject.subject_code.ilike(f'%{search_query}%'))
        )

    available_subjects = query.all()

    # Existing active registrations for student
    registered_subject_ids = [
        r.subject_id for r in Registration.query.filter_by(student_id=student_id, status='Registered').all()
    ]

    return render_template(
        'subjects.html',
        student=student,
        subjects=available_subjects,
        registered_subject_ids=registered_subject_ids,
        search_query=search_query,
        type_filter=type_filter,
        sem_filter=sem_filter
    )

# Register Subject Action
@app.route('/student/register_subject/<int:subject_id>', methods=['POST'])
@student_required
def register_subject(subject_id):
    student_id = session.get('user_id')
    student = Student.query.get(student_id)
    subject = Subject.query.get_or_404(subject_id)

    # Rule: Student can register only for subjects belonging to their department and semester
    if subject.department != student.department or subject.semester != student.semester:
        flash('You can only register for subjects in your department and semester.', 'danger')
        return redirect(url_for('subjects'))

    # Rule: Prevent duplicate registration for active status 'Registered'
    existing_reg = Registration.query.filter_by(
        student_id=student_id,
        subject_id=subject_id
    ).first()

    if existing_reg:
        if existing_reg.status == 'Registered':
            flash(f'You are already registered for {subject.subject_name} ({subject.subject_code}).', 'warning')
            return redirect(url_for('subjects'))
        else:
            # Re-activate previously cancelled registration
            existing_reg.status = 'Registered'
            existing_reg.registration_date = datetime.utcnow()
            db.session.commit()
            flash(f'Successfully re-registered for {subject.subject_name}!', 'success')
            return redirect(url_for('my_subjects'))

    new_reg = Registration(
        student_id=student_id,
        subject_id=subject_id,
        status='Registered'
    )
    db.session.add(new_reg)
    db.session.commit()

    flash(f'Successfully registered for {subject.subject_name} ({subject.subject_code})!', 'success')
    return redirect(url_for('my_subjects'))

# My Registered Subjects
@app.route('/student/my_subjects')
@student_required
def my_subjects():
    student_id = session.get('user_id')
    student = Student.query.get(student_id)

    registrations = Registration.query.filter_by(student_id=student_id).order_by(Registration.registration_date.desc()).all()

    total_credits = sum(r.subject.credits for r in registrations if r.status == 'Registered')

    return render_template(
        'my_subjects.html',
        student=student,
        registrations=registrations,
        total_credits=total_credits
    )

# Cancel Registration
@app.route('/student/cancel_registration/<int:registration_id>', methods=['POST'])
@student_required
def cancel_registration(registration_id):
    student_id = session.get('user_id')
    reg = Registration.query.filter_by(id=registration_id, student_id=student_id).first_or_404()

    if reg.status == 'Cancelled':
        flash('Registration is already cancelled.', 'info')
    else:
        reg.status = 'Cancelled'
        db.session.commit()
        flash(f'Registration for {reg.subject.subject_name} has been cancelled.', 'success')

    return redirect(url_for('my_subjects'))

# Admin Dashboard
@app.route('/admin/dashboard')
@admin_required
def admin_dashboard():
    total_students = Student.query.count()
    total_subjects = Subject.query.count()
    total_registrations = Registration.query.count()
    active_registrations = Registration.query.filter_by(status='Registered').count()

    recent_registrations = Registration.query.order_by(Registration.registration_date.desc()).limit(5).all()

    return render_template(
        'admin_dashboard.html',
        total_students=total_students,
        total_subjects=total_subjects,
        total_registrations=total_registrations,
        active_registrations=active_registrations,
        recent_registrations=recent_registrations
    )

# Manage Subjects
@app.route('/admin/subjects')
@admin_required
def manage_subjects():
    subjects_list = Subject.query.order_by(Subject.department, Subject.semester, Subject.subject_code).all()
    return render_template('manage_subjects.html', subjects=subjects_list)

# Add Subject
@app.route('/admin/subjects/add', methods=['GET', 'POST'])
@admin_required
def add_subject():
    if request.method == 'POST':
        subject_name = request.form.get('subject_name', '').strip()
        subject_code = request.form.get('subject_code', '').strip().upper()
        department = request.form.get('department', '').strip()
        semester = request.form.get('semester', type=int)
        subject_type = request.form.get('subject_type', '').strip()
        credits = request.form.get('credits', type=int)

        if not subject_name or not subject_code or not department or not semester or not subject_type or credits is None:
            flash('All subject fields are required.', 'danger')
            return redirect(url_for('add_subject'))

        existing_subject = Subject.query.filter_by(subject_code=subject_code).first()
        if existing_subject:
            flash(f'Subject with code "{subject_code}" already exists.', 'danger')
            return redirect(url_for('add_subject'))

        subject = Subject(
            subject_name=subject_name,
            subject_code=subject_code,
            department=department,
            semester=semester,
            subject_type=subject_type,
            credits=credits
        )
        db.session.add(subject)
        db.session.commit()

        flash(f'Subject "{subject_name}" added successfully.', 'success')
        return redirect(url_for('manage_subjects'))

    return render_template('add_subject.html')

# Edit Subject
@app.route('/admin/subjects/edit/<int:subject_id>', methods=['GET', 'POST'])
@admin_required
def edit_subject(subject_id):
    subject = Subject.query.get_or_404(subject_id)

    if request.method == 'POST':
        subject_name = request.form.get('subject_name', '').strip()
        subject_code = request.form.get('subject_code', '').strip().upper()
        department = request.form.get('department', '').strip()
        semester = request.form.get('semester', type=int)
        subject_type = request.form.get('subject_type', '').strip()
        credits = request.form.get('credits', type=int)

        if not subject_name or not subject_code or not department or not semester or not subject_type or credits is None:
            flash('All fields are required.', 'danger')
            return redirect(url_for('edit_subject', subject_id=subject_id))

        existing_subject = Subject.query.filter(Subject.subject_code == subject_code, Subject.id != subject_id).first()
        if existing_subject:
            flash(f'Subject code "{subject_code}" is already used by another subject.', 'danger')
            return redirect(url_for('edit_subject', subject_id=subject_id))

        subject.subject_name = subject_name
        subject.subject_code = subject_code
        subject.department = department
        subject.semester = semester
        subject.subject_type = subject_type
        subject.credits = credits

        db.session.commit()
        flash(f'Subject "{subject_name}" updated successfully.', 'success')
        return redirect(url_for('manage_subjects'))

    return render_template('edit_subject.html', subject=subject)

# Delete Subject
@app.route('/admin/subjects/delete/<int:subject_id>', methods=['POST'])
@admin_required
def delete_subject(subject_id):
    subject = Subject.query.get_or_404(subject_id)
    db.session.delete(subject)
    db.session.commit()
    flash('Subject deleted successfully.', 'info')
    return redirect(url_for('manage_subjects'))

# Manage Registrations
@app.route('/admin/registrations')
@admin_required
def manage_registrations():
    registrations = Registration.query.order_by(Registration.registration_date.desc()).all()
    return render_template('manage_registrations.html', registrations=registrations)

# Admin Cancel Registration
@app.route('/admin/registrations/cancel/<int:registration_id>', methods=['POST'])
@admin_required
def admin_cancel_registration(registration_id):
    reg = Registration.query.get_or_404(registration_id)
    reg.status = 'Cancelled'
    db.session.commit()
    flash(f'Registration #{reg.id} for {reg.student.student_name} cancelled.', 'info')
    return redirect(url_for('manage_registrations'))

# Manage Students
@app.route('/admin/students')
@admin_required
def manage_students():
    students_list = Student.query.order_by(Student.student_name).all()
    return render_template('manage_students.html', students=students_list)

# Delete Student
@app.route('/admin/students/delete/<int:student_id>', methods=['POST'])
@admin_required
def delete_student(student_id):
    student = Student.query.get_or_404(student_id)
    db.session.delete(student)
    db.session.commit()
    flash(f'Student "{student.student_name}" removed successfully.', 'info')
    return redirect(url_for('manage_students'))

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
        seed_default_data()
    app.run(debug=True)
