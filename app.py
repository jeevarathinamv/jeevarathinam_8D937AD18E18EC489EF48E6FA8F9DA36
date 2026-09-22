import os
from datetime import datetime, date
from functools import wraps
from flask import Flask, render_template, request, redirect, url_for, flash, session
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'student_tracker_secret_key_2025_gradient_blue_purple_pink')

# Admin Hardcoded/Default Credentials
ADMIN_USERNAME = os.environ.get('ADMIN_USERNAME', 'admin')
ADMIN_PASSWORD = os.environ.get('ADMIN_PASSWORD', 'admin123')

# Database configuration: Default to MySQL URI, fallback/option for SQLite
MYSQL_URI = os.environ.get('DATABASE_URL', 'mysql+pymysql://root:@localhost/student_course_tracker')
SQLITE_URI = 'sqlite:///' + os.path.join(os.path.abspath(os.path.dirname(__file__)), 'student_tracker.db')

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

    courses = db.relationship('Course', backref='student', lazy=True, cascade='all, delete-orphan')
    certifications = db.relationship('Certification', backref='student', lazy=True, cascade='all, delete-orphan')

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

class Course(db.Model):
    __tablename__ = 'courses'
    id = db.Column(db.Integer, primary_key=True)
    student_id = db.Column(db.Integer, db.ForeignKey('students.id'), nullable=False)
    course_name = db.Column(db.String(150), nullable=False)
    course_provider = db.Column(db.String(100), nullable=False)
    course_category = db.Column(db.String(100), nullable=False)
    start_date = db.Column(db.Date, nullable=False)
    end_date = db.Column(db.Date, nullable=True)
    course_status = db.Column(db.String(20), nullable=False, default='Ongoing') # Ongoing, Completed
    course_link = db.Column(db.String(255), nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class Certification(db.Model):
    __tablename__ = 'certifications'
    id = db.Column(db.Integer, primary_key=True)
    student_id = db.Column(db.Integer, db.ForeignKey('students.id'), nullable=False)
    certificate_name = db.Column(db.String(150), nullable=False)
    course_name = db.Column(db.String(150), nullable=False)
    issuing_organization = db.Column(db.String(100), nullable=False)
    issue_date = db.Column(db.Date, nullable=False)
    certificate_id = db.Column(db.String(100), nullable=True)
    certificate_link = db.Column(db.String(255), nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

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

        existing_student = db.session.query(Student).filter(
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

        student = db.session.query(Student).filter(
            (Student.email == email_or_reg.lower()) | (Student.register_number == email_or_reg)
        ).first()

        if student and student.check_password(password):
            session['user_type'] = 'student'
            session['user_id'] = student.id
            session['user_name'] = student.name
            flash(f'Welcome back, {student.name}!', 'success')
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

        # Check DB admin or default fallback credentials
        admin = db.session.query(Admin).filter_by(username=username).first()
        valid = False
        if admin and admin.check_password(password):
            valid = True
        elif username == ADMIN_USERNAME and password == ADMIN_PASSWORD:
            valid = True

        if valid:
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
    if not student:
        session.clear()
        flash('Student profile not found.', 'danger')
        return redirect(url_for('login'))

    courses = db.session.query(Course).filter_by(student_id=student_id).all()
    certifications = db.session.query(Certification).filter_by(student_id=student_id).all()

    total_courses = len(courses)
    completed_courses = len([c for c in courses if c.course_status == 'Completed'])
    ongoing_courses = len([c for c in courses if c.course_status == 'Ongoing'])
    total_certifications = len(certifications)

    recent_courses = sorted(courses, key=lambda x: x.created_at, reverse=True)[:3]
    recent_certifications = sorted(certifications, key=lambda x: x.created_at, reverse=True)[:3]

    return render_template(
        'student_dashboard.html',
        student=student,
        total_courses=total_courses,
        completed_courses=completed_courses,
        ongoing_courses=ongoing_courses,
        total_certifications=total_certifications,
        recent_courses=recent_courses,
        recent_certifications=recent_certifications
    )

# Add Course
@app.route('/courses/add', methods=['GET', 'POST'])
@student_required
def add_course():
    if request.method == 'POST':
        course_name = request.form.get('course_name', '').strip()
        course_provider = request.form.get('course_provider', '').strip()
        course_category = request.form.get('course_category', '').strip()
        start_date_str = request.form.get('start_date', '')
        end_date_str = request.form.get('end_date', '')
        course_status = request.form.get('course_status', 'Ongoing').strip()
        course_link = request.form.get('course_link', '').strip()

        if not course_name or not course_provider or not course_category or not start_date_str:
            flash('Course Name, Provider, Category, and Start Date are required.', 'danger')
            return redirect(url_for('add_course'))

        try:
            start_date = datetime.strptime(start_date_str, '%Y-%m-%d').date()
            end_date = datetime.strptime(end_date_str, '%Y-%m-%d').date() if end_date_str else None
        except ValueError:
            flash('Invalid date format.', 'danger')
            return redirect(url_for('add_course'))

        course = Course(
            student_id=session['user_id'],
            course_name=course_name,
            course_provider=course_provider,
            course_category=course_category,
            start_date=start_date,
            end_date=end_date,
            course_status=course_status if course_status in ['Ongoing', 'Completed'] else 'Ongoing',
            course_link=course_link if course_link else None
        )
        db.session.add(course)
        db.session.commit()

        flash('Course added successfully!', 'success')
        return redirect(url_for('courses'))

    return render_template('add_course.html')

# View Courses (Course Tracker)
@app.route('/courses')
@student_required
def courses():
    student_id = session.get('user_id')
    student_courses = db.session.query(Course).filter_by(student_id=student_id).order_by(Course.created_at.desc()).all()
    return render_template('courses.html', courses=student_courses)

# Delete Course
@app.route('/courses/delete/<int:course_id>', methods=['POST'])
@student_required
def delete_course(course_id):
    student_id = session.get('user_id')
    course = db.session.get(Course, course_id)
    if course and course.student_id == student_id:
        db.session.delete(course)
        db.session.commit()
        flash('Course record deleted successfully.', 'info')
    else:
        flash('Course not found or unauthorized action.', 'danger')
    return redirect(url_for('courses'))

# Add Certificate
@app.route('/certifications/add', methods=['GET', 'POST'])
@student_required
def add_certificate():
    if request.method == 'POST':
        certificate_name = request.form.get('certificate_name', '').strip()
        course_name = request.form.get('course_name', '').strip()
        issuing_organization = request.form.get('issuing_organization', '').strip()
        issue_date_str = request.form.get('issue_date', '')
        certificate_id = request.form.get('certificate_id', '').strip()
        certificate_link = request.form.get('certificate_link', '').strip()

        if not certificate_name or not course_name or not issuing_organization or not issue_date_str:
            flash('Certificate Name, Course Name, Organization, and Issue Date are required.', 'danger')
            return redirect(url_for('add_certificate'))

        try:
            issue_date = datetime.strptime(issue_date_str, '%Y-%m-%d').date()
        except ValueError:
            flash('Invalid issue date format.', 'danger')
            return redirect(url_for('add_certificate'))

        certificate = Certification(
            student_id=session['user_id'],
            certificate_name=certificate_name,
            course_name=course_name,
            issuing_organization=issuing_organization,
            issue_date=issue_date,
            certificate_id=certificate_id if certificate_id else None,
            certificate_link=certificate_link if certificate_link else None
        )
        db.session.add(certificate)
        db.session.commit()

        flash('Certificate added successfully!', 'success')
        return redirect(url_for('certifications'))

    return render_template('add_certificate.html')

# View Certifications (Certification Tracker)
@app.route('/certifications')
@student_required
def certifications():
    student_id = session.get('user_id')
    student_certs = db.session.query(Certification).filter_by(student_id=student_id).order_by(Certification.created_at.desc()).all()
    return render_template('certifications.html', certifications=student_certs)

# Delete Certificate
@app.route('/certifications/delete/<int:cert_id>', methods=['POST'])
@student_required
def delete_certificate(cert_id):
    student_id = session.get('user_id')
    cert = db.session.get(Certification, cert_id)
    if cert and cert.student_id == student_id:
        db.session.delete(cert)
        db.session.commit()
        flash('Certification record deleted successfully.', 'info')
    else:
        flash('Certificate not found or unauthorized action.', 'danger')
    return redirect(url_for('certifications'))

# Admin Dashboard
@app.route('/admin/dashboard')
@admin_required
def admin_dashboard():
    students = db.session.query(Student).order_by(Student.created_at.desc()).all()
    all_courses = db.session.query(Course).order_by(Course.created_at.desc()).all()
    all_certifications = db.session.query(Certification).order_by(Certification.created_at.desc()).all()

    total_students = len(students)
    total_courses = len(all_courses)
    total_certifications = len(all_certifications)

    return render_template(
        'admin_dashboard.html',
        students=students,
        courses=all_courses,
        certifications=all_certifications,
        total_students=total_students,
        total_courses=total_courses,
        total_certifications=total_certifications
    )

# Admin Delete Student
@app.route('/admin/student/delete/<int:student_id>', methods=['POST'])
@admin_required
def admin_delete_student(student_id):
    student = db.session.get(Student, student_id)
    if student:
        db.session.delete(student)
        db.session.commit()
        flash(f'Student "{student.name}" and associated records deleted.', 'info')
    else:
        flash('Student not found.', 'danger')
    return redirect(url_for('admin_dashboard'))

# Admin Delete Course
@app.route('/admin/course/delete/<int:course_id>', methods=['POST'])
@admin_required
def admin_delete_course(course_id):
    course = db.session.get(Course, course_id)
    if course:
        db.session.delete(course)
        db.session.commit()
        flash('Course record deleted.', 'info')
    else:
        flash('Course not found.', 'danger')
    return redirect(url_for('admin_dashboard'))

# Admin Delete Certification
@app.route('/admin/certification/delete/<int:cert_id>', methods=['POST'])
@admin_required
def admin_delete_certification(cert_id):
    cert = db.session.get(Certification, cert_id)
    if cert:
        db.session.delete(cert)
        db.session.commit()
        flash('Certification record deleted.', 'info')
    else:
        flash('Certification not found.', 'danger')
    return redirect(url_for('admin_dashboard'))

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True)
