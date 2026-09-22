import os
from datetime import datetime, date, timezone
from functools import wraps
from flask import Flask, render_template, request, redirect, url_for, flash, session
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'internship_tracker_secret_key_98765')

# Database configuration: Default to MySQL URI, fallback/option for SQLite
MYSQL_URI = os.environ.get('DATABASE_URL', 'mysql+pymysql://root:@localhost/internship_tracker')
SQLITE_URI = 'sqlite:///' + os.path.join(os.path.abspath(os.path.dirname(__file__)), 'internship_tracker.db')

use_sqlite = os.environ.get('USE_SQLITE') == '1'
app.config['SQLALCHEMY_DATABASE_URI'] = SQLITE_URI if use_sqlite else MYSQL_URI
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

def utcnow():
    return datetime.now(timezone.utc)

# Models
class Student(db.Model):
    __tablename__ = 'students'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    register_number = db.Column(db.String(50), unique=True, nullable=False)
    department = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    created_at = db.Column(db.DateTime, default=utcnow)

    applications = db.relationship('InternshipApplication', backref='student', lazy=True, cascade='all, delete-orphan')

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

class Admin(db.Model):
    __tablename__ = 'admins'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    created_at = db.Column(db.DateTime, default=utcnow)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

class InternshipApplication(db.Model):
    __tablename__ = 'internship_applications'
    id = db.Column(db.Integer, primary_key=True)
    student_id = db.Column(db.Integer, db.ForeignKey('students.id'), nullable=False)
    company_name = db.Column(db.String(100), nullable=False)
    role = db.Column(db.String(100), nullable=False)
    location = db.Column(db.String(100), nullable=False)
    application_date = db.Column(db.Date, nullable=False)
    application_link = db.Column(db.String(255), nullable=True)
    status = db.Column(db.String(50), default='Applied') # Statuses: Applied, Shortlisted, Interview Scheduled, Selected, Rejected
    interview_date = db.Column(db.Date, nullable=True)
    notes = db.Column(db.Text, nullable=True)
    admin_remarks = db.Column(db.Text, nullable=True)
    created_at = db.Column(db.DateTime, default=utcnow)

    followups = db.relationship('Followup', backref='application', lazy=True, cascade='all, delete-orphan', order_by='Followup.followup_date.desc()')

class Followup(db.Model):
    __tablename__ = 'followups'
    id = db.Column(db.Integer, primary_key=True)
    application_id = db.Column(db.Integer, db.ForeignKey('internship_applications.id'), nullable=False)
    followup_date = db.Column(db.Date, nullable=False)
    notes = db.Column(db.Text, nullable=False)
    updated_status = db.Column(db.String(50), nullable=True)
    created_at = db.Column(db.DateTime, default=utcnow)

def seed_default_data():
    if db.session.query(Admin).count() == 0:
        default_admin = Admin(username='admin')
        default_admin.set_password('admin123')
        db.session.add(default_admin)
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

# Routes

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

        flash('Registration successful! Please log in to your account.', 'success')
        return redirect(url_for('login'))

    return render_template('register.html')

# Student Login
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email_or_reg = request.form.get('email_or_reg', '').strip()
        password = request.form.get('password', '')

        if not email_or_reg or not password:
            flash('Please enter your email/register number and password.', 'danger')
            return redirect(url_for('login'))

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

        admin = db.session.query(Admin).filter_by(username=username).first()

        if admin and admin.check_password(password):
            session['user_type'] = 'admin'
            session['admin_id'] = admin.id
            session['user_name'] = admin.username
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
    flash('You have been logged out.', 'info')
    return redirect(url_for('index'))

# Student Dashboard
@app.route('/student/dashboard')
@student_required
def student_dashboard():
    student_id = session.get('user_id')
    student = db.session.get(Student, student_id)

    applications = db.session.query(InternshipApplication).filter_by(student_id=student_id).order_by(InternshipApplication.created_at.desc()).all()

    total_applications = len(applications)
    applied_count = len([a for a in applications if a.status == 'Applied'])
    shortlisted_count = len([a for a in applications if a.status == 'Shortlisted'])
    interview_count = len([a for a in applications if a.status == 'Interview Scheduled'])
    selected_count = len([a for a in applications if a.status == 'Selected'])
    rejected_count = len([a for a in applications if a.status == 'Rejected'])

    recent_applications = applications[:5]

    return render_template(
        'student_dashboard.html',
        student=student,
        applications=recent_applications,
        total_applications=total_applications,
        applied_count=applied_count,
        shortlisted_count=shortlisted_count,
        interview_count=interview_count,
        selected_count=selected_count,
        rejected_count=rejected_count
    )

# Add Internship Application
@app.route('/student/application/add', methods=['GET', 'POST'])
@student_required
def add_application():
    if request.method == 'POST':
        company_name = request.form.get('company_name', '').strip()
        role = request.form.get('role', '').strip()
        location = request.form.get('location', '').strip()
        application_date_str = request.form.get('application_date', '').strip()
        application_link = request.form.get('application_link', '').strip()
        notes = request.form.get('notes', '').strip()

        if not company_name or not role or not location or not application_date_str:
            flash('Company name, role, location, and application date are required.', 'danger')
            return redirect(url_for('add_application'))

        try:
            app_date = datetime.strptime(application_date_str, '%Y-%m-%d').date()
        except ValueError:
            flash('Invalid application date format.', 'danger')
            return redirect(url_for('add_application'))

        application = InternshipApplication(
            student_id=session.get('user_id'),
            company_name=company_name,
            role=role,
            location=location,
            application_date=app_date,
            application_link=application_link if application_link else None,
            notes=notes if notes else None,
            status='Applied'
        )
        db.session.add(application)
        db.session.commit()

        flash(f'Application for {role} at {company_name} added successfully!', 'success')
        return redirect(url_for('applications'))

    today_str = date.today().isoformat()
    return render_template('add_application.html', today=today_str)

# Application Tracker (Student View)
@app.route('/student/applications')
@student_required
def applications():
    student_id = session.get('user_id')
    status_filter = request.args.get('status', '').strip()

    query = db.session.query(InternshipApplication).filter_by(student_id=student_id)
    if status_filter:
        query = query.filter_by(status=status_filter)

    applications = query.order_by(InternshipApplication.application_date.desc()).all()

    return render_template('applications.html', applications=applications, current_filter=status_filter)

# Follow-up Management
@app.route('/application/<int:app_id>/followup', methods=['GET', 'POST'])
@student_required
def followup(app_id):
    student_id = session.get('user_id')
    application = db.session.query(InternshipApplication).filter_by(id=app_id, student_id=student_id).first_or_404()

    if request.method == 'POST':
        followup_date_str = request.form.get('followup_date', '').strip()
        notes = request.form.get('notes', '').strip()
        updated_status = request.form.get('updated_status', '').strip()

        if not followup_date_str or not notes:
            flash('Follow-up date and notes are required.', 'danger')
            return redirect(url_for('followup', app_id=app_id))

        try:
            f_date = datetime.strptime(followup_date_str, '%Y-%m-%d').date()
        except ValueError:
            flash('Invalid date format.', 'danger')
            return redirect(url_for('followup', app_id=app_id))

        followup_entry = Followup(
            application_id=application.id,
            followup_date=f_date,
            notes=notes,
            updated_status=updated_status if updated_status else application.status
        )
        db.session.add(followup_entry)

        if updated_status and updated_status != application.status:
            application.status = updated_status

        db.session.commit()

        flash('Follow-up record added successfully!', 'success')
        return redirect(url_for('followup', app_id=app_id))

    today_str = date.today().isoformat()
    return render_template('followup.html', application=application, today=today_str)

# Application Details View (Student or Admin)
@app.route('/application/<int:app_id>')
def application_details(app_id):
    user_type = session.get('user_type')
    if not user_type:
        flash('Please log in to view application details.', 'warning')
        return redirect(url_for('login'))

    application = db.session.get(InternshipApplication, app_id)
    if not application:
        flash('Application not found.', 'danger')
        return redirect(url_for('index'))

    # If student, ensure ownership
    if user_type == 'student' and application.student_id != session.get('user_id'):
        flash('Unauthorized access to application details.', 'danger')
        return redirect(url_for('student_dashboard'))

    return render_template('application_details.html', application=application)

# Admin Dashboard
@app.route('/admin/dashboard')
@admin_required
def admin_dashboard():
    status_filter = request.args.get('status', '').strip()
    search_query = request.args.get('search', '').strip()

    all_students = db.session.query(Student).all()
    query = db.session.query(InternshipApplication).join(Student)

    if status_filter:
        query = query.filter(InternshipApplication.status == status_filter)

    if search_query:
        search_pattern = f"%{search_query}%"
        query = query.filter(
            (InternshipApplication.company_name.ilike(search_pattern)) |
            (InternshipApplication.role.ilike(search_pattern)) |
            (Student.name.ilike(search_pattern)) |
            (Student.register_number.ilike(search_pattern))
        )

    applications = query.order_by(InternshipApplication.created_at.desc()).all()

    all_apps = db.session.query(InternshipApplication).all()
    total_applications = len(all_apps)
    applied_count = len([a for a in all_apps if a.status == 'Applied'])
    shortlisted_count = len([a for a in all_apps if a.status == 'Shortlisted'])
    interview_count = len([a for a in all_apps if a.status == 'Interview Scheduled'])
    selected_count = len([a for a in all_apps if a.status == 'Selected'])
    rejected_count = len([a for a in all_apps if a.status == 'Rejected'])

    return render_template(
        'admin_dashboard.html',
        applications=applications,
        total_students=len(all_students),
        total_applications=total_applications,
        applied_count=applied_count,
        shortlisted_count=shortlisted_count,
        interview_count=interview_count,
        selected_count=selected_count,
        rejected_count=rejected_count,
        current_status=status_filter,
        search_query=search_query
    )

# Admin Update Application Status, Interview Date & Remarks
@app.route('/admin/application/update/<int:app_id>', methods=['POST'])
@admin_required
def admin_update_application(app_id):
    application = db.session.get(InternshipApplication, app_id)
    if not application:
        flash('Application not found.', 'danger')
        return redirect(url_for('admin_dashboard'))

    status = request.form.get('status', '').strip()
    interview_date_str = request.form.get('interview_date', '').strip()
    admin_remarks = request.form.get('admin_remarks', '').strip()

    if status:
        application.status = status

    if interview_date_str:
        try:
            application.interview_date = datetime.strptime(interview_date_str, '%Y-%m-%d').date()
        except ValueError:
            flash('Invalid interview date format.', 'danger')
            return redirect(url_for('admin_dashboard'))
    elif 'clear_interview_date' in request.form:
        application.interview_date = None

    if admin_remarks:
        application.admin_remarks = admin_remarks

    db.session.commit()
    flash(f'Application #{application.id} for {application.company_name} updated successfully!', 'success')
    return redirect(url_for('admin_dashboard'))

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
        seed_default_data()
    app.run(debug=True)
