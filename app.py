import os
from datetime import datetime
from functools import wraps
from flask import Flask, render_template, request, redirect, url_for, flash, session
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'college_placement_portal_secret_key_123')

# Admin Hardcoded Credentials
ADMIN_USERNAME = os.environ.get('ADMIN_USERNAME', 'admin')
ADMIN_PASSWORD = os.environ.get('ADMIN_PASSWORD', 'admin123')

# Database configuration: Default to MySQL URI, fallback/option for SQLite
MYSQL_URI = os.environ.get('DATABASE_URL', 'mysql+pymysql://root:@localhost/placement_portal_db')
SQLITE_URI = 'sqlite:///' + os.path.join(os.path.abspath(os.path.dirname(__file__)), 'placement_portal.db')

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

    applications = db.relationship('Application', backref='student', lazy=True, cascade='all, delete-orphan')

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

class Job(db.Model):
    __tablename__ = 'jobs'
    id = db.Column(db.Integer, primary_key=True)
    company_name = db.Column(db.String(100), nullable=False)
    job_role = db.Column(db.String(100), nullable=False)
    salary_package = db.Column(db.String(50), nullable=False)
    eligibility_criteria = db.Column(db.String(255), nullable=False)
    description = db.Column(db.Text, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    applications = db.relationship('Application', backref='job', lazy=True, cascade='all, delete-orphan')

class Application(db.Model):
    __tablename__ = 'applications'
    id = db.Column(db.Integer, primary_key=True)
    student_id = db.Column(db.Integer, db.ForeignKey('students.id'), nullable=False)
    job_id = db.Column(db.Integer, db.ForeignKey('jobs.id'), nullable=False)
    status = db.Column(db.String(20), default='Pending') # Pending, Selected, Rejected
    applied_at = db.Column(db.DateTime, default=datetime.utcnow)

def seed_default_data():
    if Job.query.count() == 0:
        jobs = [
            Job(
                company_name='TechSolutions Inc.',
                job_role='Software Engineer Trainee',
                salary_package='6.5 LPA',
                eligibility_criteria='BE/B.Tech/MCA/M.Sc (CS/IT), 60% throughout',
                description='Looking for enthusiastic entry-level software developers with strong problem-solving and coding skills in Python, Java, or C++.'
            ),
            Job(
                company_name='DataDynamics Ltd.',
                job_role='Data Analyst',
                salary_package='5.0 LPA',
                eligibility_criteria='All B.E/B.Tech, MCA, B.Sc (Maths/Stats/CS)',
                description='Responsible for analyzing datasets, building interactive dashboards, and preparing data insights for clients.'
            ),
            Job(
                company_name='CloudScale Systems',
                job_role='DevOps & Cloud Associate',
                salary_package='7.2 LPA',
                eligibility_criteria='CSE, IT, ECE, MCA - 65% aggregate',
                description='Role involves working with AWS/Azure services, Docker containerization, CI/CD pipelines, and Linux administration.'
            ),
            Job(
                company_name='NextGen Solutions',
                job_role='UI/UX Frontend Developer',
                salary_package='4.8 LPA',
                eligibility_criteria='Open to all departments with Web Development skills',
                description='Front-end development using HTML5, CSS3, JavaScript, and Bootstrap/React framework.'
            ),
            Job(
                company_name='FinTech Corp',
                job_role='QA & Automation Engineer',
                salary_package='5.5 LPA',
                eligibility_criteria='CSE, IT, ECE, MCA',
                description='Software testing role including automated test scripts execution, bug tracking, and quality assurance.'
            ),
        ]
        db.session.add_all(jobs)
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
            return redirect(url_for('login'))
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

# Student & Admin Login
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        login_type = request.form.get('login_type', 'student')

        if login_type == 'admin':
            username = request.form.get('username', '').strip()
            password = request.form.get('password', '')
            if username == ADMIN_USERNAME and password == ADMIN_PASSWORD:
                session['user_type'] = 'admin'
                session['user_name'] = 'Administrator'
                flash('Logged in successfully as Administrator.', 'success')
                return redirect(url_for('admin_dashboard'))
            else:
                flash('Invalid admin credentials.', 'danger')
                return redirect(url_for('login'))
        else:
            email_or_reg = request.form.get('email_or_reg', '').strip()
            password = request.form.get('password', '')

            student = Student.query.filter(
                (Student.email == email_or_reg.lower()) | (Student.register_number == email_or_reg)
            ).first()

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

# Logout
@app.route('/logout')
def logout():
    session.clear()
    flash('You have been logged out.', 'info')
    return redirect(url_for('index'))

# Student Dashboard & Job Application
@app.route('/student/dashboard')
@student_required
def student_dashboard():
    student_id = session.get('user_id')
    student = db.session.get(Student, student_id)
    jobs = Job.query.order_by(Job.created_at.desc()).all()
    my_applications = Application.query.filter_by(student_id=student_id).order_by(Application.applied_at.desc()).all()
    applied_job_ids = [app.job_id for app in my_applications]

    return render_template(
        'student_dashboard.html',
        student=student,
        jobs=jobs,
        applications=my_applications,
        applied_job_ids=applied_job_ids
    )

@app.route('/student/apply/<int:job_id>', methods=['POST'])
@student_required
def apply_job(job_id):
    student_id = session.get('user_id')
    job = db.session.get(Job, job_id)

    if not job:
        flash('Job opportunity not found.', 'danger')
        return redirect(url_for('student_dashboard'))

    existing_application = Application.query.filter_by(student_id=student_id, job_id=job_id).first()
    if existing_application:
        flash('You have already applied for this job opportunity.', 'warning')
        return redirect(url_for('student_dashboard'))

    application = Application(
        student_id=student_id,
        job_id=job_id,
        status='Pending'
    )
    db.session.add(application)
    db.session.commit()

    flash(f'Successfully applied for {job.job_role} at {job.company_name}!', 'success')
    return redirect(url_for('student_dashboard'))

# Admin Dashboard & Job/Application Management
@app.route('/admin/dashboard')
@admin_required
def admin_dashboard():
    jobs = Job.query.order_by(Job.created_at.desc()).all()
    students = Student.query.order_by(Student.created_at.desc()).all()
    applications = Application.query.order_by(Application.applied_at.desc()).all()

    total_jobs = len(jobs)
    total_students = len(students)
    total_applications = len(applications)
    pending_count = len([a for a in applications if a.status == 'Pending'])

    return render_template(
        'admin_dashboard.html',
        jobs=jobs,
        students=students,
        applications=applications,
        total_jobs=total_jobs,
        total_students=total_students,
        total_applications=total_applications,
        pending_count=pending_count
    )

@app.route('/admin/job/add', methods=['POST'])
@admin_required
def add_job():
    company_name = request.form.get('company_name', '').strip()
    job_role = request.form.get('job_role', '').strip()
    salary_package = request.form.get('salary_package', '').strip()
    eligibility_criteria = request.form.get('eligibility_criteria', '').strip()
    description = request.form.get('description', '').strip()

    if not company_name or not job_role or not salary_package or not eligibility_criteria:
        flash('Company name, job role, salary package, and eligibility criteria are required.', 'danger')
        return redirect(url_for('admin_dashboard'))

    job = Job(
        company_name=company_name,
        job_role=job_role,
        salary_package=salary_package,
        eligibility_criteria=eligibility_criteria,
        description=description
    )
    db.session.add(job)
    db.session.commit()

    flash(f'Job opportunity "{job_role}" at {company_name} added successfully.', 'success')
    return redirect(url_for('admin_dashboard'))

@app.route('/admin/job/update/<int:job_id>', methods=['POST'])
@admin_required
def update_job(job_id):
    job = db.session.get(Job, job_id)
    if not job:
        flash('Job opportunity not found.', 'danger')
        return redirect(url_for('admin_dashboard'))

    company_name = request.form.get('company_name', '').strip()
    job_role = request.form.get('job_role', '').strip()
    salary_package = request.form.get('salary_package', '').strip()
    eligibility_criteria = request.form.get('eligibility_criteria', '').strip()
    description = request.form.get('description', '').strip()

    if company_name:
        job.company_name = company_name
    if job_role:
        job.job_role = job_role
    if salary_package:
        job.salary_package = salary_package
    if eligibility_criteria:
        job.eligibility_criteria = eligibility_criteria
    job.description = description

    db.session.commit()
    flash(f'Job opportunity "{job.job_role}" updated successfully.', 'success')
    return redirect(url_for('admin_dashboard'))

@app.route('/admin/job/delete/<int:job_id>', methods=['POST'])
@admin_required
def delete_job(job_id):
    job = db.session.get(Job, job_id)
    if not job:
        flash('Job opportunity not found.', 'danger')
        return redirect(url_for('admin_dashboard'))

    db.session.delete(job)
    db.session.commit()
    flash('Job opportunity deleted successfully.', 'info')
    return redirect(url_for('admin_dashboard'))

@app.route('/admin/application/update_status/<int:app_id>', methods=['POST'])
@admin_required
def update_application_status(app_id):
    application = db.session.get(Application, app_id)
    if not application:
        flash('Application not found.', 'danger')
        return redirect(url_for('admin_dashboard'))

    new_status = request.form.get('status', '').strip()
    if new_status not in ['Pending', 'Selected', 'Rejected']:
        flash('Invalid application status.', 'danger')
        return redirect(url_for('admin_dashboard'))

    application.status = new_status
    db.session.commit()

    flash(f'Application #{application.id} status updated to "{new_status}".', 'success')
    return redirect(url_for('admin_dashboard'))

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
        seed_default_data()
    app.run(debug=True)
