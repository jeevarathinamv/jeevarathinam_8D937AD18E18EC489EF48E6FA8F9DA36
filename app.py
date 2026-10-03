import os
from datetime import datetime, date, timedelta, timezone
from functools import wraps
from flask import Flask, render_template, request, redirect, url_for, flash, session
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'student_career_tracker_secret_key_9988')

# Admin Credentials
ADMIN_USERNAME = os.environ.get('ADMIN_USERNAME', 'admin')
ADMIN_PASSWORD = os.environ.get('ADMIN_PASSWORD', 'admin123')

# Database configuration: Default to MySQL URI, fallback to SQLite for testing/standalone
MYSQL_URI = os.environ.get('DATABASE_URL', 'mysql+pymysql://root:@localhost/student_career_tracker_db')
SQLITE_URI = 'sqlite:///' + os.path.join(os.path.abspath(os.path.dirname(__file__)), 'student_career.db')

use_sqlite = os.environ.get('USE_SQLITE') == '1'
app.config['SQLALCHEMY_DATABASE_URI'] = SQLITE_URI if use_sqlite else MYSQL_URI
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

def utc_now():
    return datetime.now(timezone.utc)

# Database Models
class Admin(db.Model):
    __tablename__ = 'admins'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    created_at = db.Column(db.DateTime, default=utc_now)

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
    created_at = db.Column(db.DateTime, default=utc_now)

    profile = db.relationship('CareerProfile', backref='student', uselist=False, cascade="all, delete-orphan")
    goals = db.relationship('CareerGoal', backref='student', lazy=True, cascade="all, delete-orphan")
    skills = db.relationship('Skill', backref='student', lazy=True, cascade="all, delete-orphan")
    certifications = db.relationship('Certification', backref='student', lazy=True, cascade="all, delete-orphan")
    milestones = db.relationship('Milestone', backref='student', lazy=True, cascade="all, delete-orphan")

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

class CareerProfile(db.Model):
    __tablename__ = 'career_profiles'
    id = db.Column(db.Integer, primary_key=True)
    student_id = db.Column(db.Integer, db.ForeignKey('students.id'), unique=True, nullable=False)
    career_objective = db.Column(db.Text, nullable=True)
    target_job_role = db.Column(db.String(100), nullable=True)
    target_industry = db.Column(db.String(100), nullable=True)
    skills = db.Column(db.Text, nullable=True)
    preferred_career_field = db.Column(db.String(100), nullable=True)
    short_term_goal = db.Column(db.Text, nullable=True)
    long_term_goal = db.Column(db.Text, nullable=True)
    updated_at = db.Column(db.DateTime, default=utc_now, onupdate=utc_now)

class CareerGoal(db.Model):
    __tablename__ = 'career_goals'
    id = db.Column(db.Integer, primary_key=True)
    student_id = db.Column(db.Integer, db.ForeignKey('students.id'), nullable=False)
    title = db.Column(db.String(150), nullable=False)
    category = db.Column(db.String(50), nullable=False)
    description = db.Column(db.Text, nullable=True)
    start_date = db.Column(db.Date, nullable=False)
    target_date = db.Column(db.Date, nullable=False)
    priority = db.Column(db.String(20), nullable=False, default='Medium') # High, Medium, Low
    progress_percentage = db.Column(db.Integer, nullable=False, default=0)
    status = db.Column(db.String(20), nullable=False, default='Not Started') # Not Started, In Progress, Completed, Overdue
    notes = db.Column(db.Text, nullable=True)
    last_updated = db.Column(db.DateTime, default=utc_now, onupdate=utc_now)

    def check_and_update_status(self):
        """Automatically evaluate overdue status based on target date."""
        today = date.today()
        if self.progress_percentage >= 100:
            self.status = 'Completed'
            self.progress_percentage = 100
        elif self.target_date < today:
            self.status = 'Overdue'
        elif self.progress_percentage > 0:
            self.status = 'In Progress'
        else:
            self.status = 'Not Started'

class Skill(db.Model):
    __tablename__ = 'skills'
    id = db.Column(db.Integer, primary_key=True)
    student_id = db.Column(db.Integer, db.ForeignKey('students.id'), nullable=False)
    skill_name = db.Column(db.String(100), nullable=False)
    skill_category = db.Column(db.String(50), nullable=False)
    skill_level = db.Column(db.String(20), nullable=False, default='Beginner') # Beginner, Intermediate, Advanced
    target_level = db.Column(db.String(20), nullable=False, default='Intermediate')
    created_at = db.Column(db.DateTime, default=utc_now)

class Certification(db.Model):
    __tablename__ = 'certifications'
    id = db.Column(db.Integer, primary_key=True)
    student_id = db.Column(db.Integer, db.ForeignKey('students.id'), nullable=False)
    name = db.Column(db.String(150), nullable=False)
    issuing_organization = db.Column(db.String(150), nullable=False)
    issue_date = db.Column(db.Date, nullable=True)
    expiry_date = db.Column(db.Date, nullable=True)
    certificate_id = db.Column(db.String(100), nullable=True)
    certificate_link = db.Column(db.String(255), nullable=True)
    status = db.Column(db.String(20), nullable=False, default='Active') # Active, Expired, In Progress
    created_at = db.Column(db.DateTime, default=utc_now)

class Milestone(db.Model):
    __tablename__ = 'milestones'
    id = db.Column(db.Integer, primary_key=True)
    student_id = db.Column(db.Integer, db.ForeignKey('students.id'), nullable=False)
    title = db.Column(db.String(150), nullable=False)
    milestone_type = db.Column(db.String(50), nullable=False)
    date_achieved = db.Column(db.Date, nullable=False)
    description = db.Column(db.Text, nullable=True)
    created_at = db.Column(db.DateTime, default=utc_now)

# Helper Functions
def update_student_goal_statuses(student_id=None):
    """Refreshes goal statuses for past target dates."""
    query = CareerGoal.query
    if student_id:
        query = query.filter_by(student_id=student_id)
    goals = query.all()
    for goal in goals:
        goal.check_and_update_status()
    db.session.commit()

def calculate_student_overall_progress(student_id):
    goals = CareerGoal.query.filter_by(student_id=student_id).all()
    if not goals:
        return 0
    total_perc = sum(g.progress_percentage for g in goals)
    return round(total_perc / len(goals))

def seed_default_admin():
    if Admin.query.count() == 0:
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
            flash('Admin login required to access this area.', 'warning')
            return redirect(url_for('admin_login'))
        return f(*args, **kwargs)
    return decorated_function

# Context Processor for Templates
@app.context_processor
def inject_now():
    return {'now': datetime.now(timezone.utc)}

# Routes
@app.route('/')
def index():
    if session.get('user_type') == 'student':
        return redirect(url_for('student_dashboard'))
    elif session.get('user_type') == 'admin':
        return redirect(url_for('admin_dashboard'))
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
            flash('All fields are required for student registration.', 'danger')
            return render_template('register.html')

        existing_student = Student.query.filter(
            (Student.email == email) | (Student.register_number == register_number)
        ).first()

        if existing_student:
            flash('A student with this Email or Register Number already exists.', 'danger')
            return render_template('register.html')

        student = Student(
            name=name,
            register_number=register_number,
            department=department,
            email=email
        )
        student.set_password(password)
        db.session.add(student)
        db.session.commit()

        # Create empty profile for student
        profile = CareerProfile(student_id=student.id)
        db.session.add(profile)
        db.session.commit()

        flash('Registration successful! Please log in with your credentials.', 'success')
        return redirect(url_for('login'))

    return render_template('register.html')

# Student Login
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email_or_reg = request.form.get('email_or_reg', '').strip()
        password = request.form.get('password', '')

        if not email_or_reg or not password:
            flash('Please fill in all fields.', 'danger')
            return render_template('login.html')

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
            return render_template('login.html')

    return render_template('login.html')

# Admin Login
@app.route('/admin/login', methods=['GET', 'POST'])
def admin_login():
    if request.method == 'POST':
        username = request.form.get('username', '').strip()
        password = request.form.get('password', '')

        if not username or not password:
            flash('Username and Password are required.', 'danger')
            return render_template('admin_login.html')

        admin = Admin.query.filter_by(username=username).first()
        if (admin and admin.check_password(password)) or (username == ADMIN_USERNAME and password == ADMIN_PASSWORD):
            session['user_type'] = 'admin'
            session['user_name'] = 'Administrator'
            flash('Logged in successfully as Administrator.', 'success')
            return redirect(url_for('admin_dashboard'))
        else:
            flash('Invalid Admin credentials.', 'danger')
            return render_template('admin_login.html')

    return render_template('admin_login.html')

# Logout
@app.route('/logout')
def logout():
    session.clear()
    flash('You have been logged out successfully.', 'info')
    return redirect(url_for('login'))

# Student Dashboard
@app.route('/student/dashboard')
@student_required
def student_dashboard():
    student_id = session.get('user_id')
    student = db.session.get(Student, student_id)
    if not student:
        session.clear()
        return redirect(url_for('login'))

    # Check and update overdue goals
    update_student_goal_statuses(student_id)

    goals = CareerGoal.query.filter_by(student_id=student_id).all()
    total_goals = len(goals)
    completed_goals = sum(1 for g in goals if g.status == 'Completed')
    in_progress_goals = sum(1 for g in goals if g.status == 'In Progress')
    not_started_goals = sum(1 for g in goals if g.status == 'Not Started')
    overdue_goals = sum(1 for g in goals if g.status == 'Overdue')
    pending_goals = not_started_goals + overdue_goals

    overall_progress = calculate_student_overall_progress(student_id)

    # Goal Reminders
    today = date.today()
    seven_days_later = today + timedelta(days=7)

    upcoming_deadlines = [g for g in goals if g.status != 'Completed' and today <= g.target_date <= seven_days_later]
    overdue_list = [g for g in goals if g.status == 'Overdue']
    nearing_completion = [g for g in goals if 80 <= g.progress_percentage < 100 and g.status != 'Completed']

    recent_goals = CareerGoal.query.filter_by(student_id=student_id).order_by(CareerGoal.last_updated.desc()).limit(5).all()

    return render_template(
        'student_dashboard.html',
        student=student,
        total_goals=total_goals,
        completed_goals=completed_goals,
        in_progress_goals=in_progress_goals,
        not_started_goals=not_started_goals,
        overdue_goals=overdue_goals,
        pending_goals=pending_goals,
        overall_progress=overall_progress,
        upcoming_deadlines=upcoming_deadlines,
        overdue_list=overdue_list,
        nearing_completion=nearing_completion,
        recent_goals=recent_goals,
        today=today
    )

# Student Career Profile
@app.route('/student/profile', methods=['GET', 'POST'])
@student_required
def career_profile():
    student_id = session.get('user_id')
    student = db.session.get(Student, student_id)
    if not student:
        session.clear()
        return redirect(url_for('login'))

    profile = CareerProfile.query.filter_by(student_id=student_id).first()

    if not profile:
        profile = CareerProfile(student_id=student_id)
        db.session.add(profile)
        db.session.commit()

    if request.method == 'POST':
        profile.career_objective = request.form.get('career_objective', '').strip()
        profile.target_job_role = request.form.get('target_job_role', '').strip()
        profile.target_industry = request.form.get('target_industry', '').strip()
        profile.skills = request.form.get('skills', '').strip()
        profile.preferred_career_field = request.form.get('preferred_career_field', '').strip()
        profile.short_term_goal = request.form.get('short_term_goal', '').strip()
        profile.long_term_goal = request.form.get('long_term_goal', '').strip()

        db.session.commit()
        flash('Career profile updated successfully!', 'success')
        return redirect(url_for('career_profile'))

    return render_template('career_profile.html', student=student, profile=profile)

# Career Goal Management - View All Goals
@app.route('/student/goals')
@student_required
def goals():
    student_id = session.get('user_id')
    student = db.session.get(Student, student_id)
    if not student:
        session.clear()
        return redirect(url_for('login'))

    update_student_goal_statuses(student_id)

    category_filter = request.args.get('category', '')
    status_filter = request.args.get('status', '')

    query = CareerGoal.query.filter_by(student_id=student_id)
    if category_filter:
        query = query.filter_by(category=category_filter)
    if status_filter:
        query = query.filter_by(status=status_filter)

    goal_list = query.order_by(CareerGoal.target_date.asc()).all()

    categories = [
        'Technical Skills', 'Programming', 'Certification', 'Internship',
        'Placement', 'Higher Studies', 'Communication', 'Personal Development'
    ]

    return render_template(
        'goals.html',
        student=student,
        goals=goal_list,
        categories=categories,
        category_filter=category_filter,
        status_filter=status_filter,
        today=date.today()
    )

# Add Career Goal
@app.route('/student/goals/add', methods=['GET', 'POST'])
@student_required
def add_goal():
    student_id = session.get('user_id')
    student = db.session.get(Student, student_id)
    if not student:
        session.clear()
        return redirect(url_for('login'))

    categories = [
        'Technical Skills', 'Programming', 'Certification', 'Internship',
        'Placement', 'Higher Studies', 'Communication', 'Personal Development'
    ]

    if request.method == 'POST':
        title = request.form.get('title', '').strip()
        category = request.form.get('category', '').strip()
        description = request.form.get('description', '').strip()
        start_date_str = request.form.get('start_date', '')
        target_date_str = request.form.get('target_date', '')
        priority = request.form.get('priority', 'Medium')
        progress_percentage = request.form.get('progress_percentage', type=int, default=0)
        status = request.form.get('status', 'Not Started')

        if not title or not category or not start_date_str or not target_date_str:
            flash('Goal title, category, start date, and target date are required.', 'danger')
            return render_template('add_goal.html', categories=categories)

        try:
            start_date = datetime.strptime(start_date_str, '%Y-%m-%d').date()
            target_date = datetime.strptime(target_date_str, '%Y-%m-%d').date()
        except ValueError:
            flash('Invalid date format.', 'danger')
            return render_template('add_goal.html', categories=categories)

        if target_date < start_date:
            flash('Target date cannot be earlier than start date.', 'danger')
            return render_template('add_goal.html', categories=categories)

        progress_percentage = max(0, min(100, progress_percentage))

        goal = CareerGoal(
            student_id=student_id,
            title=title,
            category=category,
            description=description,
            start_date=start_date,
            target_date=target_date,
            priority=priority,
            progress_percentage=progress_percentage,
            status=status
        )
        goal.check_and_update_status()

        db.session.add(goal)
        db.session.commit()

        flash('New career goal added successfully!', 'success')
        return redirect(url_for('goals'))

    return render_template('add_goal.html', categories=categories, today=date.today().isoformat())

# Edit Career Goal
@app.route('/student/goals/edit/<int:goal_id>', methods=['GET', 'POST'])
@student_required
def edit_goal(goal_id):
    student_id = session.get('user_id')
    goal = CareerGoal.query.filter_by(id=goal_id, student_id=student_id).first_or_404()

    categories = [
        'Technical Skills', 'Programming', 'Certification', 'Internship',
        'Placement', 'Higher Studies', 'Communication', 'Personal Development'
    ]

    if request.method == 'POST':
        title = request.form.get('title', '').strip()
        category = request.form.get('category', '').strip()
        description = request.form.get('description', '').strip()
        start_date_str = request.form.get('start_date', '')
        target_date_str = request.form.get('target_date', '')
        priority = request.form.get('priority', 'Medium')
        progress_percentage = request.form.get('progress_percentage', type=int, default=0)
        status = request.form.get('status', 'In Progress')
        notes = request.form.get('notes', '').strip()

        if not title or not category or not start_date_str or not target_date_str:
            flash('Goal title, category, start date, and target date are required.', 'danger')
            return render_template('edit_goal.html', goal=goal, categories=categories)

        try:
            start_date = datetime.strptime(start_date_str, '%Y-%m-%d').date()
            target_date = datetime.strptime(target_date_str, '%Y-%m-%d').date()
        except ValueError:
            flash('Invalid date format.', 'danger')
            return render_template('edit_goal.html', goal=goal, categories=categories)

        if target_date < start_date:
            flash('Target date cannot be earlier than start date.', 'danger')
            return render_template('edit_goal.html', goal=goal, categories=categories)

        progress_percentage = max(0, min(100, progress_percentage))

        goal.title = title
        goal.category = category
        goal.description = description
        goal.start_date = start_date
        goal.target_date = target_date
        goal.priority = priority
        goal.progress_percentage = progress_percentage
        goal.status = status
        goal.notes = notes
        goal.last_updated = utc_now()

        goal.check_and_update_status()

        db.session.commit()
        flash('Career goal updated successfully!', 'success')
        return redirect(url_for('goals'))

    return render_template('edit_goal.html', goal=goal, categories=categories)

# Quick Progress Update
@app.route('/student/goals/update_progress/<int:goal_id>', methods=['POST'])
@student_required
def update_goal_progress(goal_id):
    student_id = session.get('user_id')
    goal = CareerGoal.query.filter_by(id=goal_id, student_id=student_id).first_or_404()

    progress_percentage = request.form.get('progress_percentage', type=int)
    status = request.form.get('status', '').strip()
    notes = request.form.get('notes', '').strip()

    if progress_percentage is not None:
        goal.progress_percentage = max(0, min(100, progress_percentage))

    if status:
        goal.status = status

    if notes:
        goal.notes = notes

    goal.last_updated = utc_now()
    goal.check_and_update_status()

    db.session.commit()
    flash(f'Progress for "{goal.title}" updated to {goal.progress_percentage}%.', 'success')
    return redirect(request.referrer or url_for('goals'))

# Delete Career Goal
@app.route('/student/goals/delete/<int:goal_id>', methods=['POST'])
@student_required
def delete_goal(goal_id):
    student_id = session.get('user_id')
    goal = CareerGoal.query.filter_by(id=goal_id, student_id=student_id).first_or_404()
    db.session.delete(goal)
    db.session.commit()
    flash('Goal deleted successfully.', 'info')
    return redirect(url_for('goals'))

# Skill Tracker
@app.route('/student/skills', methods=['GET', 'POST'])
@student_required
def skills():
    student_id = session.get('user_id')
    student = db.session.get(Student, student_id)
    if not student:
        session.clear()
        return redirect(url_for('login'))

    if request.method == 'POST':
        skill_name = request.form.get('skill_name', '').strip()
        skill_category = request.form.get('skill_category', '').strip()
        skill_level = request.form.get('skill_level', 'Beginner')
        target_level = request.form.get('target_level', 'Intermediate')

        if not skill_name or not skill_category:
            flash('Skill name and category are required.', 'danger')
            return redirect(url_for('skills'))

        skill = Skill(
            student_id=student_id,
            skill_name=skill_name,
            skill_category=skill_category,
            skill_level=skill_level,
            target_level=target_level
        )
        db.session.add(skill)
        db.session.commit()

        flash('Skill added successfully!', 'success')
        return redirect(url_for('skills'))

    skill_list = Skill.query.filter_by(student_id=student_id).order_by(Skill.created_at.desc()).all()
    return render_template('skills.html', student=student, skills=skill_list)

@app.route('/student/skills/delete/<int:skill_id>', methods=['POST'])
@student_required
def delete_skill(skill_id):
    student_id = session.get('user_id')
    skill = Skill.query.filter_by(id=skill_id, student_id=student_id).first_or_404()
    db.session.delete(skill)
    db.session.commit()
    flash('Skill deleted.', 'info')
    return redirect(url_for('skills'))

# Certification Tracker
@app.route('/student/certifications', methods=['GET', 'POST'])
@student_required
def certifications():
    student_id = session.get('user_id')
    student = db.session.get(Student, student_id)
    if not student:
        session.clear()
        return redirect(url_for('login'))

    if request.method == 'POST':
        name = request.form.get('name', '').strip()
        issuing_organization = request.form.get('issuing_organization', '').strip()
        issue_date_str = request.form.get('issue_date', '')
        expiry_date_str = request.form.get('expiry_date', '')
        certificate_id = request.form.get('certificate_id', '').strip()
        certificate_link = request.form.get('certificate_link', '').strip()
        status = request.form.get('status', 'Active')

        if not name or not issuing_organization:
            flash('Certification Name and Issuing Organization are required.', 'danger')
            return redirect(url_for('certifications'))

        issue_date = datetime.strptime(issue_date_str, '%Y-%m-%d').date() if issue_date_str else None
        expiry_date = datetime.strptime(expiry_date_str, '%Y-%m-%d').date() if expiry_date_str else None

        cert = Certification(
            student_id=student_id,
            name=name,
            issuing_organization=issuing_organization,
            issue_date=issue_date,
            expiry_date=expiry_date,
            certificate_id=certificate_id,
            certificate_link=certificate_link,
            status=status
        )
        db.session.add(cert)
        db.session.commit()

        flash('Certification added successfully!', 'success')
        return redirect(url_for('certifications'))

    cert_list = Certification.query.filter_by(student_id=student_id).order_by(Certification.created_at.desc()).all()
    return render_template('certifications.html', student=student, certifications=cert_list)

@app.route('/student/certifications/delete/<int:cert_id>', methods=['POST'])
@student_required
def delete_certification(cert_id):
    student_id = session.get('user_id')
    cert = Certification.query.filter_by(id=cert_id, student_id=student_id).first_or_404()
    db.session.delete(cert)
    db.session.commit()
    flash('Certification deleted.', 'info')
    return redirect(url_for('certifications'))

# Career Milestones
@app.route('/student/milestones', methods=['GET', 'POST'])
@student_required
def milestones():
    student_id = session.get('user_id')
    student = db.session.get(Student, student_id)
    if not student:
        session.clear()
        return redirect(url_for('login'))

    milestone_types = [
        'Completed Course', 'Completed Certification', 'Finished Project',
        'Internship', 'Placement Preparation', 'Interview Preparation'
    ]

    if request.method == 'POST':
        title = request.form.get('title', '').strip()
        milestone_type = request.form.get('milestone_type', '').strip()
        date_achieved_str = request.form.get('date_achieved', '')
        description = request.form.get('description', '').strip()

        if not title or not milestone_type or not date_achieved_str:
            flash('Title, milestone type, and date achieved are required.', 'danger')
            return redirect(url_for('milestones'))

        try:
            date_achieved = datetime.strptime(date_achieved_str, '%Y-%m-%d').date()
        except ValueError:
            flash('Invalid date format.', 'danger')
            return redirect(url_for('milestones'))

        milestone = Milestone(
            student_id=student_id,
            title=title,
            milestone_type=milestone_type,
            date_achieved=date_achieved,
            description=description
        )
        db.session.add(milestone)
        db.session.commit()

        flash('Career milestone added successfully!', 'success')
        return redirect(url_for('milestones'))

    milestone_list = Milestone.query.filter_by(student_id=student_id).order_by(Milestone.date_achieved.desc()).all()
    return render_template('milestones.html', student=student, milestones=milestone_list, milestone_types=milestone_types)

@app.route('/student/milestones/delete/<int:milestone_id>', methods=['POST'])
@student_required
def delete_milestone(milestone_id):
    student_id = session.get('user_id')
    milestone = Milestone.query.filter_by(id=milestone_id, student_id=student_id).first_or_404()
    db.session.delete(milestone)
    db.session.commit()
    flash('Milestone removed.', 'info')
    return redirect(url_for('milestones'))

# Admin Dashboard
@app.route('/admin/dashboard')
@admin_required
def admin_dashboard():
    # Update overdue statuses for all goals
    update_student_goal_statuses()

    total_students = Student.query.count()
    total_goals = CareerGoal.query.count()
    completed_goals = CareerGoal.query.filter_by(status='Completed').count()
    in_progress_goals = CareerGoal.query.filter_by(status='In Progress').count()
    overdue_goals = CareerGoal.query.filter_by(status='Overdue').count()
    total_certifications = Certification.query.count()

    recent_students = Student.query.order_by(Student.created_at.desc()).limit(5).all()

    return render_template(
        'admin_dashboard.html',
        total_students=total_students,
        total_goals=total_goals,
        completed_goals=completed_goals,
        in_progress_goals=in_progress_goals,
        overdue_goals=overdue_goals,
        total_certifications=total_certifications,
        recent_students=recent_students
    )

# Admin Student Management
@app.route('/admin/students')
@admin_required
def manage_students():
    search_query = request.args.get('search', '').strip()
    query = Student.query

    if search_query:
        search_pattern = f"%{search_query}%"
        query = query.filter(
            (Student.name.ilike(search_pattern)) |
            (Student.register_number.ilike(search_pattern)) |
            (Student.department.ilike(search_pattern)) |
            (Student.email.ilike(search_pattern))
        )

    students = query.order_by(Student.name.asc()).all()

    # Pre-calculate progress for each student
    student_data = []
    for st in students:
        goals = st.goals
        total_g = len(goals)
        comp_g = sum(1 for g in goals if g.status == 'Completed')
        overall_p = calculate_student_overall_progress(st.id)
        student_data.append({
            'student': st,
            'total_goals': total_g,
            'completed_goals': comp_g,
            'overall_progress': overall_p
        })

    return render_template('manage_students.html', student_data=student_data, search_query=search_query)

# Admin Career Progress Monitoring
@app.route('/admin/students/progress')
@admin_required
def student_progress():
    update_student_goal_statuses()

    students = Student.query.order_by(Student.name.asc()).all()
    progress_report = []

    for st in students:
        goals = st.goals
        total_g = len(goals)
        comp_g = sum(1 for g in goals if g.status == 'Completed')
        in_prog_g = sum(1 for g in goals if g.status == 'In Progress')
        overdue_g = sum(1 for g in goals if g.status == 'Overdue')
        overall_p = calculate_student_overall_progress(st.id)
        target_role = st.profile.target_job_role if st.profile and st.profile.target_job_role else 'Not Set'

        progress_report.append({
            'student_id': st.id,
            'name': st.name,
            'register_number': st.register_number,
            'department': st.department,
            'target_job_role': target_role,
            'total_goals': total_g,
            'completed_goals': comp_g,
            'in_progress_goals': in_prog_g,
            'overdue_goals': overdue_g,
            'overall_progress': overall_p
        })

    return render_template('student_progress.html', progress_report=progress_report)

# Admin View Specific Student Details
@app.route('/admin/student/<int:student_id>')
@admin_required
def view_student_detail(student_id):
    student = db.session.get(Student, student_id)
    if not student:
        flash('Student not found.', 'danger')
        return redirect(url_for('manage_students'))

    update_student_goal_statuses(student_id)

    overall_progress = calculate_student_overall_progress(student.id)

    return render_template(
        'student_detail.html',
        student=student,
        profile=student.profile,
        goals=student.goals,
        skills=student.skills,
        certifications=student.certifications,
        milestones=student.milestones,
        overall_progress=overall_progress
    )

# Admin Delete Student
@app.route('/admin/students/delete/<int:student_id>', methods=['POST'])
@admin_required
def delete_student(student_id):
    student = db.session.get(Student, student_id)
    if not student:
        flash('Student not found.', 'danger')
        return redirect(url_for('manage_students'))

    db.session.delete(student)
    db.session.commit()
    flash(f'Student "{student.name}" ({student.register_number}) deleted successfully.', 'info')
    return redirect(url_for('manage_students'))

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
        seed_default_admin()
    app.run(debug=True)
