import os
from datetime import datetime, date
from functools import wraps
from flask import Flask, render_template, request, redirect, url_for, flash, session
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'campus_recruitment_secret_key_2025')

# Admin Hardcoded Fallback Credentials
ADMIN_USERNAME = os.environ.get('ADMIN_USERNAME', 'admin')
ADMIN_PASSWORD = os.environ.get('ADMIN_PASSWORD', 'admin123')

# Database configuration: Default to MySQL URI, fallback/option for SQLite
MYSQL_URI = os.environ.get('DATABASE_URL', 'mysql+pymysql://root:@localhost/campus_recruitment')
SQLITE_URI = 'sqlite:///' + os.path.join(os.path.abspath(os.path.dirname(__file__)), 'campus_recruitment.db')

use_sqlite = os.environ.get('USE_SQLITE') == '1'
app.config['SQLALCHEMY_DATABASE_URI'] = SQLITE_URI if use_sqlite else MYSQL_URI
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)


# Database Models
class Student(db.Model):
    __tablename__ = 'students'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    register_number = db.Column(db.String(50), unique=True, nullable=False)
    department = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    phone_number = db.Column(db.String(20), nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    registrations = db.relationship('Registration', backref='student', lazy=True, cascade="all, delete-orphan")

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)


class RecruitmentDrive(db.Model):
    __tablename__ = 'recruitment_drives'
    id = db.Column(db.Integer, primary_key=True)
    company_name = db.Column(db.String(150), nullable=False)
    job_role = db.Column(db.String(100), nullable=False)
    eligibility = db.Column(db.String(200), nullable=False)
    package = db.Column(db.String(100), nullable=False)
    drive_date = db.Column(db.Date, nullable=False)
    location = db.Column(db.String(150), nullable=False)
    description = db.Column(db.Text, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    registrations = db.relationship('Registration', backref='drive', lazy=True, cascade="all, delete-orphan")


class Registration(db.Model):
    __tablename__ = 'registrations'
    id = db.Column(db.Integer, primary_key=True)
    student_id = db.Column(db.Integer, db.ForeignKey('students.id'), nullable=False)
    drive_id = db.Column(db.Integer, db.ForeignKey('recruitment_drives.id'), nullable=False)
    registration_date = db.Column(db.DateTime, default=datetime.utcnow)
    status = db.Column(db.String(20), default='Registered')  # Registered, Shortlisted, Selected, Rejected
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    __table_args__ = (db.UniqueConstraint('student_id', 'drive_id', name='unique_student_drive'),)


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


# Seed Initial Default Data
def seed_default_data():
    if Admin.query.count() == 0:
        admin_user = Admin(username=ADMIN_USERNAME)
        admin_user.set_password(ADMIN_PASSWORD)
        db.session.add(admin_user)
        db.session.commit()

    if RecruitmentDrive.query.count() == 0:
        today = date.today()
        sample_drives = [
            RecruitmentDrive(
                company_name='TechCorp Solutions',
                job_role='Software Development Engineer',
                eligibility='B.Tech CS/IT, MCA with 60%+',
                package='$12,000 / 8 LPA',
                drive_date=date(today.year, today.month, min(today.day + 10, 28)),
                location='Main Campus Auditorium',
                description='Full-stack software development role focusing on Python, Flask, SQL, and modern web applications.'
            ),
            RecruitmentDrive(
                company_name='DataViz Innovations',
                job_role='Data Analyst',
                eligibility='All B.E / B.Tech / B.Sc / MCA graduates',
                package='$10,000 / 6.5 LPA',
                drive_date=date(today.year, today.month, min(today.day + 15, 28)),
                location='Virtual / Zoom',
                description='Analyzing large datasets, writing complex SQL queries, and creating visual BI dashboards.'
            ),
            RecruitmentDrive(
                company_name='CloudNet Systems',
                job_role='DevOps & Cloud Trainee',
                eligibility='CS / IT / ECE graduates',
                package='$11,000 / 7 LPA',
                drive_date=date(today.year, today.month, min(today.day + 20, 28)),
                location='Tech Park Block B',
                description='Automating deployments, Docker containerization, and AWS cloud architecture management.'
            )
        ]
        db.session.add_all(sample_drives)
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


# Home Route
@app.route('/')
def index():
    upcoming_drives = RecruitmentDrive.query.order_by(RecruitmentDrive.drive_date.asc()).limit(3).all()
    total_drives = RecruitmentDrive.query.count()
    total_students = Student.query.count()
    total_selected = Registration.query.filter_by(status='Selected').count()
    return render_template(
        'index.html',
        upcoming_drives=upcoming_drives,
        total_drives=total_drives,
        total_students=total_students,
        total_selected=total_selected
    )


# Student Registration
@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        name = request.form.get('name', '').strip()
        register_number = request.form.get('register_number', '').strip()
        department = request.form.get('department', '').strip()
        email = request.form.get('email', '').strip().lower()
        phone_number = request.form.get('phone_number', '').strip()
        password = request.form.get('password', '')

        if not name or not register_number or not department or not email or not phone_number or not password:
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
            email=email,
            phone_number=phone_number
        )
        student.set_password(password)
        db.session.add(student)
        db.session.commit()

        flash('Registration successful! You can now log in.', 'success')
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
            session['user_name'] = student.name
            flash(f'Welcome back, {student.name}!', 'success')
            return redirect(url_for('student_dashboard'))
        else:
            flash('Invalid Email/Register Number or Password.', 'danger')
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
            session['user_name'] = 'Administrator'
            flash('Logged in successfully as Admin.', 'success')
            return redirect(url_for('admin_dashboard'))
        elif username == ADMIN_USERNAME and password == ADMIN_PASSWORD:
            session['user_type'] = 'admin'
            session['user_name'] = 'Administrator'
            flash('Logged in successfully as Admin.', 'success')
            return redirect(url_for('admin_dashboard'))
        else:
            flash('Invalid Admin Credentials.', 'danger')
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
    student = Student.query.get_or_404(student_id)

    total_drives = RecruitmentDrive.query.count()
    my_registrations = Registration.query.filter_by(student_id=student_id).all()
    registered_drive_ids = [r.drive_id for r in my_registrations]

    registered_drives_count = len(registered_drive_ids)
    upcoming_drives_count = RecruitmentDrive.query.filter(RecruitmentDrive.drive_date >= date.today()).count()
    selected_drives_count = Registration.query.filter_by(student_id=student_id, status='Selected').count()

    upcoming_drives = RecruitmentDrive.query.order_by(RecruitmentDrive.drive_date.asc()).limit(5).all()

    return render_template(
        'student_dashboard.html',
        student=student,
        total_drives=total_drives,
        registered_drives_count=registered_drives_count,
        upcoming_drives_count=upcoming_drives_count,
        selected_drives_count=selected_drives_count,
        upcoming_drives=upcoming_drives,
        registered_drive_ids=registered_drive_ids
    )


# Drive List
@app.route('/drives')
def drives():
    all_drives = RecruitmentDrive.query.order_by(RecruitmentDrive.drive_date.asc()).all()
    registered_drive_ids = []
    if session.get('user_type') == 'student':
        student_id = session.get('user_id')
        registrations = Registration.query.filter_by(student_id=student_id).all()
        registered_drive_ids = [r.drive_id for r in registrations]

    return render_template('drives.html', drives=all_drives, registered_drive_ids=registered_drive_ids)


# Drive Details
@app.route('/drives/<int:drive_id>')
def drive_details(drive_id):
    drive = RecruitmentDrive.query.get_or_404(drive_id)
    is_registered = False
    student_registration = None

    if session.get('user_type') == 'student':
        student_id = session.get('user_id')
        student_registration = Registration.query.filter_by(student_id=student_id, drive_id=drive_id).first()
        if student_registration:
            is_registered = True

    return render_template('drive_details.html', drive=drive, is_registered=is_registered, registration=student_registration)


# Drive Registration
@app.route('/drives/<int:drive_id>/register', methods=['POST'])
@student_required
def register_drive(drive_id):
    student_id = session.get('user_id')
    drive = RecruitmentDrive.query.get_or_404(drive_id)

    existing_reg = Registration.query.filter_by(student_id=student_id, drive_id=drive_id).first()
    if existing_reg:
        flash(f'You are already registered for {drive.company_name} - {drive.job_role}.', 'info')
        return redirect(url_for('drive_details', drive_id=drive_id))

    registration = Registration(
        student_id=student_id,
        drive_id=drive_id,
        status='Registered'
    )
    db.session.add(registration)
    db.session.commit()

    flash(f'Successfully registered for {drive.company_name} - {drive.job_role}!', 'success')
    return redirect(url_for('my_registrations'))


# Student My Registrations / Recruitment History / Application Status
@app.route('/my-registrations')
@student_required
def my_registrations():
    student_id = session.get('user_id')
    student = Student.query.get_or_404(student_id)
    registrations = Registration.query.filter_by(student_id=student_id).order_by(Registration.registration_date.desc()).all()
    return render_template('my_registrations.html', student=student, registrations=registrations)


# Admin Dashboard
@app.route('/admin/dashboard')
@admin_required
def admin_dashboard():
    drives = RecruitmentDrive.query.order_by(RecruitmentDrive.drive_date.desc()).all()
    total_drives = len(drives)
    total_students = Student.query.count()
    total_registrations = Registration.query.count()
    selected_students_count = Registration.query.filter_by(status='Selected').count()

    return render_template(
        'admin_dashboard.html',
        drives=drives,
        total_drives=total_drives,
        total_students=total_students,
        total_registrations=total_registrations,
        selected_students_count=selected_students_count
    )


# Admin Add Recruitment Drive
@app.route('/admin/drives/add', methods=['GET', 'POST'])
@admin_required
def add_drive():
    if request.method == 'POST':
        company_name = request.form.get('company_name', '').strip()
        job_role = request.form.get('job_role', '').strip()
        eligibility = request.form.get('eligibility', '').strip()
        package = request.form.get('package', '').strip()
        drive_date_str = request.form.get('drive_date', '')
        location = request.form.get('location', '').strip()
        description = request.form.get('description', '').strip()

        if not company_name or not job_role or not eligibility or not package or not drive_date_str or not location:
            flash('All required fields must be filled.', 'danger')
            return redirect(url_for('add_drive'))

        try:
            drive_date = datetime.strptime(drive_date_str, '%Y-%m-%d').date()
        except ValueError:
            flash('Invalid date format.', 'danger')
            return redirect(url_for('add_drive'))

        drive = RecruitmentDrive(
            company_name=company_name,
            job_role=job_role,
            eligibility=eligibility,
            package=package,
            drive_date=drive_date,
            location=location,
            description=description
        )
        db.session.add(drive)
        db.session.commit()

        flash(f'Recruitment drive for "{company_name}" created successfully.', 'success')
        return redirect(url_for('admin_dashboard'))

    return render_template('add_drive.html', drive=None)


# Admin Edit Recruitment Drive
@app.route('/admin/drives/edit/<int:drive_id>', methods=['GET', 'POST'])
@admin_required
def edit_drive(drive_id):
    drive = RecruitmentDrive.query.get_or_404(drive_id)

    if request.method == 'POST':
        company_name = request.form.get('company_name', '').strip()
        job_role = request.form.get('job_role', '').strip()
        eligibility = request.form.get('eligibility', '').strip()
        package = request.form.get('package', '').strip()
        drive_date_str = request.form.get('drive_date', '')
        location = request.form.get('location', '').strip()
        description = request.form.get('description', '').strip()

        if not company_name or not job_role or not eligibility or not package or not drive_date_str or not location:
            flash('All required fields must be filled.', 'danger')
            return redirect(url_for('edit_drive', drive_id=drive_id))

        try:
            drive_date = datetime.strptime(drive_date_str, '%Y-%m-%d').date()
        except ValueError:
            flash('Invalid date format.', 'danger')
            return redirect(url_for('edit_drive', drive_id=drive_id))

        drive.company_name = company_name
        drive.job_role = job_role
        drive.eligibility = eligibility
        drive.package = package
        drive.drive_date = drive_date
        drive.location = location
        drive.description = description

        db.session.commit()
        flash(f'Recruitment drive for "{company_name}" updated successfully.', 'success')
        return redirect(url_for('admin_dashboard'))

    return render_template('add_drive.html', drive=drive)


# Admin Delete Recruitment Drive
@app.route('/admin/drives/delete/<int:drive_id>', methods=['POST'])
@admin_required
def delete_drive(drive_id):
    drive = RecruitmentDrive.query.get_or_404(drive_id)
    db.session.delete(drive)
    db.session.commit()
    flash(f'Recruitment drive for "{drive.company_name}" deleted.', 'info')
    return redirect(url_for('admin_dashboard'))


# Admin View Registrations & Update Status
@app.route('/admin/registrations')
@admin_required
def admin_registrations():
    drive_id = request.args.get('drive_id', type=int)
    drives = RecruitmentDrive.query.order_by(RecruitmentDrive.company_name.asc()).all()

    if drive_id:
        registrations = Registration.query.filter_by(drive_id=drive_id).order_by(Registration.registration_date.desc()).all()
        selected_drive = RecruitmentDrive.query.get(drive_id)
    else:
        registrations = Registration.query.order_by(Registration.registration_date.desc()).all()
        selected_drive = None

    return render_template(
        'admin_registrations.html',
        registrations=registrations,
        drives=drives,
        selected_drive=selected_drive,
        selected_drive_id=drive_id
    )


# Admin Update Registration Status
@app.route('/admin/registrations/update-status/<int:reg_id>', methods=['POST'])
@admin_required
def update_registration_status(reg_id):
    registration = Registration.query.get_or_404(reg_id)
    new_status = request.form.get('status', '').strip()

    valid_statuses = ['Registered', 'Shortlisted', 'Selected', 'Rejected']
    if new_status in valid_statuses:
        registration.status = new_status
        db.session.commit()
        flash(f'Application status for {registration.student.name} updated to "{new_status}".', 'success')
    else:
        flash('Invalid status selected.', 'danger')

    redirect_drive_id = request.args.get('drive_id')
    if redirect_drive_id:
        return redirect(url_for('admin_registrations', drive_id=redirect_drive_id))
    return redirect(url_for('admin_registrations'))


if __name__ == '__main__':
    with app.app_context():
        db.create_all()
        seed_default_data()
    app.run(debug=True)
