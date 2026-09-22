import os
from datetime import datetime
from functools import wraps
from flask import Flask, render_template, request, redirect, url_for, flash, session
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename

app = Flask(__name__)
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'student_portfolio_secret_key_98765')

# Upload configuration
UPLOAD_FOLDER = os.path.join(app.root_path, 'static', 'uploads')
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'webp'}
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# Admin Default Credentials
ADMIN_USERNAME = os.environ.get('ADMIN_USERNAME', 'admin')
ADMIN_PASSWORD = os.environ.get('ADMIN_PASSWORD', 'admin123')

# Database configuration: MySQL URI for XAMPP, fallback/option for SQLite
MYSQL_URI = os.environ.get('DATABASE_URL', 'mysql+pymysql://root:@localhost/student_portfolio')
SQLITE_URI = 'sqlite:///' + os.path.join(os.path.abspath(os.path.dirname(__file__)), 'student_portfolio.db')

use_sqlite = os.environ.get('USE_SQLITE') == '1'
app.config['SQLALCHEMY_DATABASE_URI'] = SQLITE_URI if use_sqlite else MYSQL_URI
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

# Models
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

    profile = db.relationship('Profile', backref='student', uselist=False, cascade="all, delete-orphan")
    education = db.relationship('Education', backref='student', cascade="all, delete-orphan", lazy=True)
    skills = db.relationship('Skill', backref='student', cascade="all, delete-orphan", lazy=True)
    projects = db.relationship('Project', backref='student', cascade="all, delete-orphan", lazy=True)
    certifications = db.relationship('Certification', backref='student', cascade="all, delete-orphan", lazy=True)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

class Profile(db.Model):
    __tablename__ = 'profiles'
    id = db.Column(db.Integer, primary_key=True)
    student_id = db.Column(db.Integer, db.ForeignKey('students.id'), unique=True, nullable=False)
    profile_photo = db.Column(db.String(255), default='default_avatar.png')
    about_me = db.Column(db.Text, nullable=True)
    career_objective = db.Column(db.Text, nullable=True)
    hobbies = db.Column(db.Text, nullable=True)
    phone = db.Column(db.String(20), nullable=True)
    address = db.Column(db.Text, nullable=True)
    linkedin_url = db.Column(db.String(255), nullable=True)
    github_url = db.Column(db.String(255), nullable=True)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

class Education(db.Model):
    __tablename__ = 'education'
    id = db.Column(db.Integer, primary_key=True)
    student_id = db.Column(db.Integer, db.ForeignKey('students.id'), nullable=False)
    degree = db.Column(db.String(100), nullable=False)
    institution = db.Column(db.String(150), nullable=False)
    year_of_passing = db.Column(db.String(20), nullable=False)
    score = db.Column(db.String(50), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class Skill(db.Model):
    __tablename__ = 'skills'
    id = db.Column(db.Integer, primary_key=True)
    student_id = db.Column(db.Integer, db.ForeignKey('students.id'), nullable=False)
    skill_name = db.Column(db.String(100), nullable=False)
    proficiency = db.Column(db.String(50), default='Intermediate')
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class Project(db.Model):
    __tablename__ = 'projects'
    id = db.Column(db.Integer, primary_key=True)
    student_id = db.Column(db.Integer, db.ForeignKey('students.id'), nullable=False)
    title = db.Column(db.String(150), nullable=False)
    description = db.Column(db.Text, nullable=False)
    technologies_used = db.Column(db.String(255), nullable=False)
    project_link = db.Column(db.String(255), nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class Certification(db.Model):
    __tablename__ = 'certifications'
    id = db.Column(db.Integer, primary_key=True)
    student_id = db.Column(db.Integer, db.ForeignKey('students.id'), nullable=False)
    certificate_title = db.Column(db.String(150), nullable=False)
    issuing_organization = db.Column(db.String(150), nullable=False)
    issue_date = db.Column(db.String(50), nullable=True)
    certificate_link = db.Column(db.String(255), nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def seed_admin():
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
        db.session.flush()

        # Create empty profile for student
        profile = Profile(student_id=student.id)
        db.session.add(profile)
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
            session['user_id'] = student.id
            session['user_name'] = student.name
            flash(f'Welcome back, {student.name}!', 'success')
            return redirect(url_for('dashboard'))
        else:
            flash('Invalid login credentials. Please try again.', 'danger')
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
            session['admin_id'] = admin.id
            session['user_name'] = admin.username
            flash('Admin login successful!', 'success')
            return redirect(url_for('admin_dashboard'))
        elif username == ADMIN_USERNAME and password == ADMIN_PASSWORD:
            session['user_type'] = 'admin'
            session['user_name'] = ADMIN_USERNAME
            flash('Admin login successful!', 'success')
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
@app.route('/dashboard')
@student_required
def dashboard():
    student_id = session.get('user_id')
    student = Student.query.get_or_404(student_id)
    return render_template('dashboard.html', student=student)

# Student Profile
@app.route('/profile', methods=['GET', 'POST'])
@student_required
def profile():
    student_id = session.get('user_id')
    student = Student.query.get_or_404(student_id)
    prof = student.profile
    if not prof:
        prof = Profile(student_id=student.id)
        db.session.add(prof)
        db.session.commit()

    if request.method == 'POST':
        student.name = request.form.get('name', student.name).strip()
        student.department = request.form.get('department', student.department).strip()
        prof.about_me = request.form.get('about_me', '').strip()
        prof.career_objective = request.form.get('career_objective', '').strip()
        prof.hobbies = request.form.get('hobbies', '').strip()
        prof.phone = request.form.get('phone', '').strip()
        prof.address = request.form.get('address', '').strip()
        prof.linkedin_url = request.form.get('linkedin_url', '').strip()
        prof.github_url = request.form.get('github_url', '').strip()

        # Handle Profile Photo Upload
        if 'profile_photo' in request.files:
            file = request.files['profile_photo']
            if file and file.filename != '' and allowed_file(file.filename):
                filename = f"user_{student.id}_{secure_filename(file.filename)}"
                file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
                prof.profile_photo = filename

        db.session.commit()
        session['user_name'] = student.name
        flash('Profile updated successfully!', 'success')
        return redirect(url_for('profile'))

    return render_template('profile.html', student=student, profile=prof)

# Education Management
@app.route('/education')
@student_required
def education():
    student_id = session.get('user_id')
    education_list = Education.query.filter_by(student_id=student_id).all()
    return render_template('education.html', education_list=education_list)

@app.route('/education/add', methods=['POST'])
@student_required
def add_education():
    student_id = session.get('user_id')
    degree = request.form.get('degree', '').strip()
    institution = request.form.get('institution', '').strip()
    year_of_passing = request.form.get('year_of_passing', '').strip()
    score = request.form.get('score', '').strip()

    if not degree or not institution or not year_of_passing or not score:
        flash('All fields are required.', 'danger')
        return redirect(url_for('education'))

    item = Education(
        student_id=student_id,
        degree=degree,
        institution=institution,
        year_of_passing=year_of_passing,
        score=score
    )
    db.session.add(item)
    db.session.commit()
    flash('Education details added successfully!', 'success')
    return redirect(url_for('education'))

@app.route('/education/edit/<int:id>', methods=['POST'])
@student_required
def edit_education(id):
    student_id = session.get('user_id')
    item = Education.query.filter_by(id=id, student_id=student_id).first_or_404()

    item.degree = request.form.get('degree', item.degree).strip()
    item.institution = request.form.get('institution', item.institution).strip()
    item.year_of_passing = request.form.get('year_of_passing', item.year_of_passing).strip()
    item.score = request.form.get('score', item.score).strip()

    db.session.commit()
    flash('Education record updated!', 'success')
    return redirect(url_for('education'))

@app.route('/education/delete/<int:id>', methods=['POST'])
@student_required
def delete_education(id):
    student_id = session.get('user_id')
    item = Education.query.filter_by(id=id, student_id=student_id).first_or_404()
    db.session.delete(item)
    db.session.commit()
    flash('Education record deleted.', 'info')
    return redirect(url_for('education'))

# Skills Management
@app.route('/skills')
@student_required
def skills():
    student_id = session.get('user_id')
    skills_list = Skill.query.filter_by(student_id=student_id).all()
    return render_template('skills.html', skills_list=skills_list)

@app.route('/skills/add', methods=['POST'])
@student_required
def add_skill():
    student_id = session.get('user_id')
    skill_name = request.form.get('skill_name', '').strip()
    proficiency = request.form.get('proficiency', 'Intermediate').strip()

    if not skill_name:
        flash('Skill name is required.', 'danger')
        return redirect(url_for('skills'))

    item = Skill(student_id=student_id, skill_name=skill_name, proficiency=proficiency)
    db.session.add(item)
    db.session.commit()
    flash('Skill added successfully!', 'success')
    return redirect(url_for('skills'))

@app.route('/skills/edit/<int:id>', methods=['POST'])
@student_required
def edit_skill(id):
    student_id = session.get('user_id')
    item = Skill.query.filter_by(id=id, student_id=student_id).first_or_404()

    item.skill_name = request.form.get('skill_name', item.skill_name).strip()
    item.proficiency = request.form.get('proficiency', item.proficiency).strip()

    db.session.commit()
    flash('Skill updated successfully!', 'success')
    return redirect(url_for('skills'))

@app.route('/skills/delete/<int:id>', methods=['POST'])
@student_required
def delete_skill(id):
    student_id = session.get('user_id')
    item = Skill.query.filter_by(id=id, student_id=student_id).first_or_404()
    db.session.delete(item)
    db.session.commit()
    flash('Skill deleted.', 'info')
    return redirect(url_for('skills'))

# Projects Management
@app.route('/projects')
@student_required
def projects():
    student_id = session.get('user_id')
    projects_list = Project.query.filter_by(student_id=student_id).all()
    return render_template('projects.html', projects_list=projects_list)

@app.route('/projects/add', methods=['POST'])
@student_required
def add_project():
    student_id = session.get('user_id')
    title = request.form.get('title', '').strip()
    description = request.form.get('description', '').strip()
    technologies_used = request.form.get('technologies_used', '').strip()
    project_link = request.form.get('project_link', '').strip()

    if not title or not description or not technologies_used:
        flash('Title, description, and technologies are required.', 'danger')
        return redirect(url_for('projects'))

    item = Project(
        student_id=student_id,
        title=title,
        description=description,
        technologies_used=technologies_used,
        project_link=project_link
    )
    db.session.add(item)
    db.session.commit()
    flash('Project added successfully!', 'success')
    return redirect(url_for('projects'))

@app.route('/projects/edit/<int:id>', methods=['POST'])
@student_required
def edit_project(id):
    student_id = session.get('user_id')
    item = Project.query.filter_by(id=id, student_id=student_id).first_or_404()

    item.title = request.form.get('title', item.title).strip()
    item.description = request.form.get('description', item.description).strip()
    item.technologies_used = request.form.get('technologies_used', item.technologies_used).strip()
    item.project_link = request.form.get('project_link', item.project_link).strip()

    db.session.commit()
    flash('Project updated successfully!', 'success')
    return redirect(url_for('projects'))

@app.route('/projects/delete/<int:id>', methods=['POST'])
@student_required
def delete_project(id):
    student_id = session.get('user_id')
    item = Project.query.filter_by(id=id, student_id=student_id).first_or_404()
    db.session.delete(item)
    db.session.commit()
    flash('Project deleted.', 'info')
    return redirect(url_for('projects'))

# Certifications Management
@app.route('/certifications')
@student_required
def certifications():
    student_id = session.get('user_id')
    certifications_list = Certification.query.filter_by(student_id=student_id).all()
    return render_template('certifications.html', certifications_list=certifications_list)

@app.route('/certifications/add', methods=['POST'])
@student_required
def add_certification():
    student_id = session.get('user_id')
    certificate_title = request.form.get('certificate_title', '').strip()
    issuing_organization = request.form.get('issuing_organization', '').strip()
    issue_date = request.form.get('issue_date', '').strip()
    certificate_link = request.form.get('certificate_link', '').strip()

    if not certificate_title or not issuing_organization:
        flash('Title and Issuing Organization are required.', 'danger')
        return redirect(url_for('certifications'))

    item = Certification(
        student_id=student_id,
        certificate_title=certificate_title,
        issuing_organization=issuing_organization,
        issue_date=issue_date,
        certificate_link=certificate_link
    )
    db.session.add(item)
    db.session.commit()
    flash('Certification added successfully!', 'success')
    return redirect(url_for('certifications'))

@app.route('/certifications/edit/<int:id>', methods=['POST'])
@student_required
def edit_certification(id):
    student_id = session.get('user_id')
    item = Certification.query.filter_by(id=id, student_id=student_id).first_or_404()

    item.certificate_title = request.form.get('certificate_title', item.certificate_title).strip()
    item.issuing_organization = request.form.get('issuing_organization', item.issuing_organization).strip()
    item.issue_date = request.form.get('issue_date', item.issue_date).strip()
    item.certificate_link = request.form.get('certificate_link', item.certificate_link).strip()

    db.session.commit()
    flash('Certification updated successfully!', 'success')
    return redirect(url_for('certifications'))

@app.route('/certifications/delete/<int:id>', methods=['POST'])
@student_required
def delete_certification(id):
    student_id = session.get('user_id')
    item = Certification.query.filter_by(id=id, student_id=student_id).first_or_404()
    db.session.delete(item)
    db.session.commit()
    flash('Certification deleted.', 'info')
    return redirect(url_for('certifications'))

# Portfolio Generator View
@app.route('/portfolio')
@app.route('/portfolio/<int:student_id>')
def portfolio(student_id=None):
    if student_id is None:
        student_id = session.get('user_id')
        if not student_id:
            flash('Please log in or select a portfolio to view.', 'info')
            return redirect(url_for('login'))

    student = Student.query.get_or_404(student_id)
    return render_template('portfolio.html', student=student)

# Admin Dashboard
@app.route('/admin/dashboard')
@admin_required
def admin_dashboard():
    students = Student.query.order_by(Student.created_at.desc()).all()
    total_students = len(students)
    total_projects = Project.query.count()
    total_skills = Skill.query.count()
    return render_template('admin_dashboard.html', students=students, total_students=total_students, total_projects=total_projects, total_skills=total_skills)

@app.route('/admin/student/delete/<int:student_id>', methods=['POST'])
@admin_required
def admin_delete_student(student_id):
    student = Student.query.get_or_404(student_id)
    db.session.delete(student)
    db.session.commit()
    flash(f'Student "{student.name}" and all associated data deleted.', 'info')
    return redirect(url_for('admin_dashboard'))

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
        seed_admin()
    app.run(debug=True)
