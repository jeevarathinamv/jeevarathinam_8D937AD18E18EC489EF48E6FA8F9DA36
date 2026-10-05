import os
from datetime import datetime
from functools import wraps
from flask import Flask, render_template, request, redirect, url_for, flash, session
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'student_course_registration_secret_key_123')

# Admin Credentials
ADMIN_USERNAME = os.environ.get('ADMIN_USERNAME', 'admin')
ADMIN_PASSWORD = os.environ.get('ADMIN_PASSWORD', 'admin123')

# Database configuration: Default to MySQL URI, fallback/option for SQLite
MYSQL_URI = os.environ.get('DATABASE_URL', 'mysql+pymysql://root:@localhost/student_course_registration')
SQLITE_URI = 'sqlite:///' + os.path.join(os.path.abspath(os.path.dirname(__file__)), 'student_course_reg.db')

use_sqlite = os.environ.get('USE_SQLITE') == '1'
app.config['SQLALCHEMY_DATABASE_URI'] = SQLITE_URI if use_sqlite else MYSQL_URI
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

# Database Models
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
    year = db.Column(db.Integer, nullable=False)
    semester = db.Column(db.Integer, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    registrations = db.relationship('Registration', backref='student', lazy=True, cascade="all, delete-orphan")

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

class Course(db.Model):
    __tablename__ = 'courses'
    id = db.Column(db.Integer, primary_key=True)
    course_name = db.Column(db.String(100), nullable=False)
    course_code = db.Column(db.String(50), unique=True, nullable=False)
    department = db.Column(db.String(100), nullable=False)
    semester = db.Column(db.Integer, nullable=False)
    course_type = db.Column(db.String(50), nullable=False) # Core, Elective, Practical
    credits = db.Column(db.Integer, nullable=False, default=3)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    registrations = db.relationship('Registration', backref='course', lazy=True, cascade="all, delete-orphan")

class Registration(db.Model):
    __tablename__ = 'registrations'
    id = db.Column(db.Integer, primary_key=True)
    student_id = db.Column(db.Integer, db.ForeignKey('students.id'), nullable=False)
    course_id = db.Column(db.Integer, db.ForeignKey('courses.id'), nullable=False)
    registration_date = db.Column(db.DateTime, default=datetime.utcnow)
    status = db.Column(db.String(20), default='Registered') # Registered, Cancelled

def seed_default_data():
    if Admin.query.count() == 0:
        admin = Admin(username=ADMIN_USERNAME)
        admin.set_password(ADMIN_PASSWORD)
        db.session.add(admin)

    if Course.query.count() == 0:
        sample_courses = [
            Course(course_name='Advanced Java Programming', course_code='MCA101', department='Computer Applications (MCA)', semester=1, course_type='Core', credits=4),
            Course(course_name='Database Management Systems', course_code='MCA102', department='Computer Applications (MCA)', semester=1, course_type='Core', credits=4),
            Course(course_name='Web Technologies Lab', course_code='MCA103', department='Computer Applications (MCA)', semester=1, course_type='Practical', credits=2),
            Course(course_name='Software Engineering', course_code='MCA104', department='Computer Applications (MCA)', semester=1, course_type='Elective', credits=3),
            Course(course_name='Python Web Development', course_code='MCA201', department='Computer Applications (MCA)', semester=2, course_type='Core', credits=4),
            Course(course_name='Data Science & Analytics', course_code='MCA202', department='Computer Applications (MCA)', semester=2, course_type='Core', credits=4),
            Course(course_name='Cloud Computing Lab', course_code='MCA203', department='Computer Applications (MCA)', semester=2, course_type='Practical', credits=2),
        ]
        db.session.add_all(sample_courses)

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
        year = request.form.get('year', type=int)
        semester = request.form.get('semester', type=int)
        email = request.form.get('email', '').strip().lower()
        password = request.form.get('password', '')

        if not all([name, register_number, department, year, semester, email, password]):
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
            year=year,
            semester=semester,
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
            session['student_name'] = student.name
            flash(f'Welcome back, {student.name}!', 'success')
            return redirect(url_for('student_dashboard'))
        else:
            flash('Invalid credentials. Please check your Email/Register Number and Password.', 'danger')
            return redirect(url_for('login'))

    return render_template('login.html')

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
    student_id = session.get('student_id')
    student = Student.query.get_or_404(student_id)

    # Available courses for student's department and semester
    available_courses = Course.query.filter_by(
        department=student.department,
        semester=student.semester
    ).all()

    # Active registrations for this student
    active_registrations = Registration.query.filter_by(
        student_id=student.id,
        status='Registered'
    ).all()

    total_courses = len(available_courses)
    registered_courses_count = len(active_registrations)
    total_credits = sum(reg.course.credits for reg in active_registrations)

    return render_template(
        'student_dashboard.html',
        student=student,
        total_courses=total_courses,
        registered_courses_count=registered_courses_count,
        total_credits=total_credits,
        active_registrations=active_registrations
    )

# ----------------- Course Registration Logic -----------------
@app.route('/courses')
@student_required
def courses():
    student_id = session.get('student_id')
    student = Student.query.get_or_404(student_id)

    # Available courses for student's department and semester
    available_courses = Course.query.filter_by(
        department=student.department,
        semester=student.semester
    ).all()

    # Get IDs of currently registered (active) courses for the student
    registered_course_ids = [
        reg.course_id for reg in Registration.query.filter_by(
            student_id=student.id,
            status='Registered'
        ).all()
    ]

    return render_template(
        'courses.html',
        student=student,
        courses=available_courses,
        registered_course_ids=registered_course_ids
    )

@app.route('/register_course/<int:course_id>', methods=['POST'])
@student_required
def register_course(course_id):
    student_id = session.get('student_id')
    student = Student.query.get_or_404(student_id)
    course = Course.query.get_or_404(course_id)

    # Rule 1: Student can register only courses belonging to their department and semester
    if course.department != student.department or course.semester != student.semester:
        flash('You can only register courses belonging to your department and semester.', 'danger')
        return redirect(url_for('courses'))

    # Rule 2: Student cannot register the same course twice (active registration check)
    existing_registration = Registration.query.filter_by(
        student_id=student.id,
        course_id=course.id,
        status='Registered'
    ).first()

    if existing_registration:
        flash(f'You are already registered for "{course.course_name}".', 'warning')
        return redirect(url_for('courses'))

    # Check if there is a previous cancelled registration, re-activate or create new
    cancelled_registration = Registration.query.filter_by(
        student_id=student.id,
        course_id=course.id,
        status='Cancelled'
    ).first()

    if cancelled_registration:
        cancelled_registration.status = 'Registered'
        cancelled_registration.registration_date = datetime.utcnow()
    else:
        new_registration = Registration(
            student_id=student.id,
            course_id=course.id,
            status='Registered'
        )
        db.session.add(new_registration)

    db.session.commit()
    flash(f'Successfully registered for course "{course.course_name}" ({course.course_code})!', 'success')
    return redirect(url_for('my_courses'))

@app.route('/my_courses')
@student_required
def my_courses():
    student_id = session.get('student_id')
    student = Student.query.get_or_404(student_id)

    registrations = Registration.query.filter_by(student_id=student.id).order_by(Registration.registration_date.desc()).all()

    # Total credits for active registrations
    total_credits = sum(reg.course.credits for reg in registrations if reg.status == 'Registered')

    return render_template(
        'my_courses.html',
        student=student,
        registrations=registrations,
        total_credits=total_credits
    )

@app.route('/cancel_course/<int:registration_id>', methods=['POST'])
@student_required
def cancel_course(registration_id):
    student_id = session.get('student_id')
    registration = Registration.query.get_or_404(registration_id)

    if registration.student_id != student_id:
        flash('Unauthorized action.', 'danger')
        return redirect(url_for('my_courses'))

    if registration.status == 'Cancelled':
        flash('This course registration is already cancelled.', 'warning')
        return redirect(url_for('my_courses'))

    registration.status = 'Cancelled'
    db.session.commit()

    flash(f'Course "{registration.course.course_name}" registration has been cancelled successfully.', 'info')
    return redirect(url_for('my_courses'))

# ----------------- Admin Routes -----------------
@app.route('/admin/login', methods=['GET', 'POST'])
def admin_login():
    if request.method == 'POST':
        username = request.form.get('username', '').strip()
        password = request.form.get('password', '')

        admin = Admin.query.filter_by(username=username).first()

        if admin and admin.check_password(password):
            session['user_type'] = 'admin'
            session['admin_id'] = admin.id
            session['admin_username'] = admin.username
            flash('Logged in successfully as Administrator.', 'success')
            return redirect(url_for('admin_dashboard'))
        elif username == ADMIN_USERNAME and password == ADMIN_PASSWORD:
            # Fallback for hardcoded credentials if not in DB
            session['user_type'] = 'admin'
            session['admin_username'] = ADMIN_USERNAME
            flash('Logged in successfully as Administrator.', 'success')
            return redirect(url_for('admin_dashboard'))
        else:
            flash('Invalid admin credentials.', 'danger')
            return redirect(url_for('admin_login'))

    return render_template('admin_login.html')

@app.route('/admin/dashboard')
@admin_required
def admin_dashboard():
    total_students = Student.query.count()
    total_courses = Course.query.count()
    total_registrations = Registration.query.count()
    active_registrations = Registration.query.filter_by(status='Registered').count()

    return render_template(
        'admin_dashboard.html',
        total_students=total_students,
        total_courses=total_courses,
        total_registrations=total_registrations,
        active_registrations=active_registrations
    )

# Course Management Routes
@app.route('/admin/courses')
@admin_required
def manage_courses():
    courses_list = Course.query.order_by(Course.department, Course.semester, Course.course_code).all()
    return render_template('manage_courses.html', courses=courses_list)

@app.route('/admin/courses/add', methods=['GET', 'POST'])
@admin_required
def add_course():
    if request.method == 'POST':
        course_name = request.form.get('course_name', '').strip()
        course_code = request.form.get('course_code', '').strip().upper()
        department = request.form.get('department', '').strip()
        semester = request.form.get('semester', type=int)
        course_type = request.form.get('course_type', '').strip()
        credits = request.form.get('credits', type=int)

        if not all([course_name, course_code, department, semester, course_type, credits]):
            flash('All fields are required.', 'danger')
            return redirect(url_for('add_course'))

        existing_course = Course.query.filter_by(course_code=course_code).first()
        if existing_course:
            flash(f'Course with code "{course_code}" already exists.', 'danger')
            return redirect(url_for('add_course'))

        course = Course(
            course_name=course_name,
            course_code=course_code,
            department=department,
            semester=semester,
            course_type=course_type,
            credits=credits
        )
        db.session.add(course)
        db.session.commit()

        flash(f'Course "{course_name}" ({course_code}) added successfully!', 'success')
        return redirect(url_for('manage_courses'))

    return render_template('add_course.html')

@app.route('/admin/courses/edit/<int:course_id>', methods=['GET', 'POST'])
@admin_required
def edit_course(course_id):
    course = Course.query.get_or_404(course_id)

    if request.method == 'POST':
        course_name = request.form.get('course_name', '').strip()
        course_code = request.form.get('course_code', '').strip().upper()
        department = request.form.get('department', '').strip()
        semester = request.form.get('semester', type=int)
        course_type = request.form.get('course_type', '').strip()
        credits = request.form.get('credits', type=int)

        if not all([course_name, course_code, department, semester, course_type, credits]):
            flash('All fields are required.', 'danger')
            return redirect(url_for('edit_course', course_id=course_id))

        existing_code = Course.query.filter(Course.course_code == course_code, Course.id != course_id).first()
        if existing_code:
            flash(f'Another course with code "{course_code}" already exists.', 'danger')
            return redirect(url_for('edit_course', course_id=course_id))

        course.course_name = course_name
        course.course_code = course_code
        course.department = department
        course.semester = semester
        course.course_type = course_type
        course.credits = credits

        db.session.commit()
        flash(f'Course "{course.course_name}" updated successfully!', 'success')
        return redirect(url_for('manage_courses'))

    return render_template('edit_course.html', course=course)

@app.route('/admin/courses/delete/<int:course_id>', methods=['POST'])
@admin_required
def delete_course(course_id):
    course = Course.query.get_or_404(course_id)
    db.session.delete(course)
    db.session.commit()
    flash('Course deleted successfully.', 'info')
    return redirect(url_for('manage_courses'))

@app.route('/admin/registrations')
@admin_required
def view_registrations():
    registrations_list = Registration.query.order_by(Registration.registration_date.desc()).all()
    return render_template('registrations.html', registrations=registrations_list)

@app.route('/admin/students')
@admin_required
def view_students():
    students_list = Student.query.order_by(Student.created_at.desc()).all()
    return render_template('view_students.html', students=students_list)

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
        seed_default_data()
    app.run(debug=True)
