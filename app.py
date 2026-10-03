import os
from datetime import datetime, date
from functools import wraps
from flask import Flask, render_template, request, redirect, url_for, flash, session
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'student_freelance_portal_secret_key_987')

# Admin Credentials (Hardcoded fallback + ENV)
ADMIN_USERNAME = os.environ.get('ADMIN_USERNAME', 'admin')
ADMIN_PASSWORD = os.environ.get('ADMIN_PASSWORD', 'admin123')

# Database configuration: Default MySQL URI, fallback/option for SQLite
MYSQL_URI = os.environ.get('DATABASE_URL', 'mysql+pymysql://root:@localhost/freelance_db')
SQLITE_URI = 'sqlite:///' + os.path.join(os.path.abspath(os.path.dirname(__file__)), 'freelance.db')

use_sqlite = os.environ.get('USE_SQLITE') == '1'
app.config['SQLALCHEMY_DATABASE_URI'] = SQLITE_URI if use_sqlite else MYSQL_URI
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

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

    profile = db.relationship('StudentProfile', backref='student', uselist=False, cascade='all, delete-orphan')
    clients = db.relationship('Client', backref='student', cascade='all, delete-orphan', lazy=True)
    projects = db.relationship('Project', backref='student', cascade='all, delete-orphan', lazy=True)
    tasks = db.relationship('Task', backref='student', cascade='all, delete-orphan', lazy=True)
    payments = db.relationship('Payment', backref='student', cascade='all, delete-orphan', lazy=True)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

class StudentProfile(db.Model):
    __tablename__ = 'student_profiles'
    id = db.Column(db.Integer, primary_key=True)
    student_id = db.Column(db.Integer, db.ForeignKey('students.id'), unique=True, nullable=False)
    photo = db.Column(db.String(255), default='default_profile.png')
    skills = db.Column(db.Text, nullable=True)
    experience = db.Column(db.Text, nullable=True)
    bio = db.Column(db.Text, nullable=True)
    portfolio_link = db.Column(db.String(255), nullable=True)
    contact_email = db.Column(db.String(120), nullable=True)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

class Client(db.Model):
    __tablename__ = 'clients'
    id = db.Column(db.Integer, primary_key=True)
    student_id = db.Column(db.Integer, db.ForeignKey('students.id'), nullable=False)
    name = db.Column(db.String(100), nullable=False)
    phone = db.Column(db.String(20), nullable=True)
    email = db.Column(db.String(120), nullable=True)
    company_name = db.Column(db.String(100), nullable=True)
    address = db.Column(db.Text, nullable=True)
    notes = db.Column(db.Text, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    projects = db.relationship('Project', backref='client_rel', lazy=True)

class Project(db.Model):
    __tablename__ = 'projects'
    id = db.Column(db.Integer, primary_key=True)
    student_id = db.Column(db.Integer, db.ForeignKey('students.id'), nullable=False)
    client_id = db.Column(db.Integer, db.ForeignKey('clients.id'), nullable=True)
    title = db.Column(db.String(150), nullable=False)
    client_name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text, nullable=True)
    category = db.Column(db.String(50), nullable=True)
    start_date = db.Column(db.Date, nullable=True)
    deadline = db.Column(db.Date, nullable=True)
    budget = db.Column(db.Float, default=0.0)
    status = db.Column(db.String(20), default='New') # New, In Progress, On Hold, Completed, Cancelled
    progress_percentage = db.Column(db.Integer, default=0)
    progress_notes = db.Column(db.Text, nullable=True)
    last_updated_date = db.Column(db.Date, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    tasks = db.relationship('Task', backref='project', cascade='all, delete-orphan', lazy=True)
    payments = db.relationship('Payment', backref='project', cascade='all, delete-orphan', lazy=True)

class Task(db.Model):
    __tablename__ = 'tasks'
    id = db.Column(db.Integer, primary_key=True)
    project_id = db.Column(db.Integer, db.ForeignKey('projects.id'), nullable=False)
    student_id = db.Column(db.Integer, db.ForeignKey('students.id'), nullable=False)
    title = db.Column(db.String(150), nullable=False)
    description = db.Column(db.Text, nullable=True)
    due_date = db.Column(db.Date, nullable=True)
    priority = db.Column(db.String(20), default='Medium') # High, Medium, Low
    status = db.Column(db.String(20), default='Pending') # Pending, In Progress, Completed
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class Payment(db.Model):
    __tablename__ = 'payments'
    id = db.Column(db.Integer, primary_key=True)
    project_id = db.Column(db.Integer, db.ForeignKey('projects.id'), nullable=False)
    student_id = db.Column(db.Integer, db.ForeignKey('students.id'), nullable=False)
    client_name = db.Column(db.String(100), nullable=False)
    amount = db.Column(db.Float, nullable=False, default=0.0)
    payment_date = db.Column(db.Date, nullable=False)
    status = db.Column(db.String(20), default='Pending') # Pending, Partially Paid, Paid
    notes = db.Column(db.Text, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

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

# Helper for date parsing
def parse_date(date_str):
    if not date_str:
        return None
    try:
        return datetime.strptime(date_str, '%Y-%m-%d').date()
    except ValueError:
        return None

# Routes: Index & Authentication
@app.route('/')
def index():
    if session.get('user_type') == 'student':
        return redirect(url_for('student_dashboard'))
    elif session.get('user_type') == 'admin':
        return redirect(url_for('admin_dashboard'))
    return redirect(url_for('login'))

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
            flash('A student with this Email or Register Number already exists.', 'danger')
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

        profile = StudentProfile(student_id=student.id, contact_email=student.email)
        db.session.add(profile)
        db.session.commit()

        flash('Registration successful! Please log in.', 'success')
        return redirect(url_for('login'))

    return render_template('register.html')

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
            flash('Invalid email/register number or password.', 'danger')
            return redirect(url_for('login'))

    return render_template('login.html')

@app.route('/admin/login', methods=['GET', 'POST'])
def admin_login():
    if request.method == 'POST':
        username = request.form.get('username', '').strip()
        password = request.form.get('password', '')

        admin_db = Admin.query.filter_by(username=username).first()

        if (admin_db and admin_db.check_password(password)) or (username == ADMIN_USERNAME and password == ADMIN_PASSWORD):
            session['user_type'] = 'admin'
            session['user_name'] = 'Administrator'
            flash('Logged in successfully as Admin.', 'success')
            return redirect(url_for('admin_dashboard'))
        else:
            flash('Invalid admin credentials.', 'danger')
            return redirect(url_for('admin_login'))

    return render_template('admin_login.html')

@app.route('/logout')
def logout():
    session.clear()
    flash('You have been logged out.', 'info')
    return redirect(url_for('login'))

# Student Profile Route
@app.route('/student/profile', methods=['GET', 'POST'])
@student_required
def profile():
    student_id = session.get('user_id')
    student = Student.query.get_or_404(student_id)
    student_profile = StudentProfile.query.filter_by(student_id=student_id).first()

    if not student_profile:
        student_profile = StudentProfile(student_id=student_id, contact_email=student.email)
        db.session.add(student_profile)
        db.session.commit()

    if request.method == 'POST':
        student.name = request.form.get('name', student.name).strip()
        student.department = request.form.get('department', student.department).strip()
        student_profile.skills = request.form.get('skills', '').strip()
        student_profile.experience = request.form.get('experience', '').strip()
        student_profile.bio = request.form.get('bio', '').strip()
        student_profile.portfolio_link = request.form.get('portfolio_link', '').strip()
        student_profile.contact_email = request.form.get('contact_email', '').strip()

        db.session.commit()
        session['user_name'] = student.name
        flash('Profile updated successfully!', 'success')
        return redirect(url_for('profile'))

    return render_template('profile.html', student=student, profile=student_profile)

# Student Dashboard & Deadline Reminders
@app.route('/student/dashboard')
@student_required
def student_dashboard():
    student_id = session.get('user_id')
    student = Student.query.get_or_404(student_id)
    projects = Project.query.filter_by(student_id=student_id).all()
    tasks = Task.query.filter_by(student_id=student_id).all()
    payments = Payment.query.filter_by(student_id=student_id).all()

    total_projects = len(projects)
    active_projects = len([p for p in projects if p.status in ['New', 'In Progress', 'On Hold']])
    completed_projects = len([p for p in projects if p.status == 'Completed'])
    pending_projects = len([p for p in projects if p.status in ['New', 'On Hold']])

    paid_payments = [p.amount for p in payments if p.status == 'Paid']
    total_earnings = sum(paid_payments)

    today = date.today()
    upcoming_deadlines = [p for p in projects if p.deadline and p.deadline >= today and p.status != 'Completed']
    pending_tasks = [t for t in tasks if t.status in ['Pending', 'In Progress']]
    overdue_tasks = [t for t in tasks if t.due_date and t.due_date < today and t.status != 'Completed']
    pending_payments = [p for p in payments if p.status in ['Pending', 'Partially Paid']]

    return render_template(
        'student_dashboard.html',
        student=student,
        total_projects=total_projects,
        active_projects=active_projects,
        completed_projects=completed_projects,
        pending_projects=pending_projects,
        total_earnings=total_earnings,
        upcoming_deadlines=upcoming_deadlines,
        pending_tasks=pending_tasks,
        overdue_tasks=overdue_tasks,
        pending_payments=pending_payments,
        today=today
    )

# Project Management
@app.route('/student/projects')
@student_required
def projects():
    student_id = session.get('user_id')
    search_query = request.args.get('search', '').strip()
    status_filter = request.args.get('status', '').strip()

    query = Project.query.filter_by(student_id=student_id)

    if search_query:
        query = query.filter(
            (Project.title.ilike(f'%{search_query}%')) |
            (Project.client_name.ilike(f'%{search_query}%')) |
            (Project.category.ilike(f'%{search_query}%'))
        )
    if status_filter:
        query = query.filter_by(status=status_filter)

    student_projects = query.order_by(Project.created_at.desc()).all()
    return render_template('projects.html', projects=student_projects, search=search_query, status_filter=status_filter)

@app.route('/student/projects/add', methods=['GET', 'POST'])
@student_required
def add_project():
    student_id = session.get('user_id')
    clients = Client.query.filter_by(student_id=student_id).all()

    if request.method == 'POST':
        title = request.form.get('title', '').strip()
        client_id = request.form.get('client_id', type=int)
        client_name = request.form.get('client_name', '').strip()
        description = request.form.get('description', '').strip()
        category = request.form.get('category', '').strip()
        start_date = parse_date(request.form.get('start_date'))
        deadline = parse_date(request.form.get('deadline'))
        budget = request.form.get('budget', type=float, default=0.0)
        status = request.form.get('status', 'New')
        progress_percentage = request.form.get('progress_percentage', type=int, default=0)

        if not title:
            flash('Project Title is required.', 'danger')
            return redirect(url_for('add_project'))

        if client_id:
            client_obj = Client.query.get(client_id)
            if client_obj:
                client_name = client_obj.name

        project = Project(
            student_id=student_id,
            client_id=client_id if client_id else None,
            title=title,
            client_name=client_name or 'Independent Client',
            description=description,
            category=category,
            start_date=start_date,
            deadline=deadline,
            budget=budget,
            status=status,
            progress_percentage=progress_percentage,
            last_updated_date=date.today()
        )
        db.session.add(project)
        db.session.commit()

        flash(f'Project "{title}" added successfully!', 'success')
        return redirect(url_for('projects'))

    return render_template('add_project.html', clients=clients)

@app.route('/student/projects/edit/<int:project_id>', methods=['GET', 'POST'])
@student_required
def edit_project(project_id):
    student_id = session.get('user_id')
    project = Project.query.filter_by(id=project_id, student_id=student_id).first_or_404()
    clients = Client.query.filter_by(student_id=student_id).all()

    if request.method == 'POST':
        project.title = request.form.get('title', project.title).strip()
        client_id = request.form.get('client_id', type=int)
        project.client_id = client_id if client_id else None

        if client_id:
            client_obj = Client.query.get(client_id)
            if client_obj:
                project.client_name = client_obj.name
        else:
            project.client_name = request.form.get('client_name', project.client_name).strip()

        project.description = request.form.get('description', '').strip()
        project.category = request.form.get('category', '').strip()
        project.start_date = parse_date(request.form.get('start_date'))
        project.deadline = parse_date(request.form.get('deadline'))
        project.budget = request.form.get('budget', type=float, default=project.budget)
        project.status = request.form.get('status', project.status)
        project.progress_percentage = request.form.get('progress_percentage', type=int, default=project.progress_percentage)
        project.progress_notes = request.form.get('progress_notes', project.progress_notes)
        project.last_updated_date = date.today()

        db.session.commit()
        flash('Project updated successfully!', 'success')
        return redirect(url_for('project_details', project_id=project.id))

    return render_template('edit_project.html', project=project, clients=clients)

@app.route('/student/projects/<int:project_id>')
@student_required
def project_details(project_id):
    student_id = session.get('user_id')
    project = Project.query.filter_by(id=project_id, student_id=student_id).first_or_404()
    tasks = Task.query.filter_by(project_id=project_id).all()
    payments = Payment.query.filter_by(project_id=project_id).all()
    return render_template('project_details.html', project=project, tasks=tasks, payments=payments)

@app.route('/student/projects/delete/<int:project_id>', methods=['POST'])
@student_required
def delete_project(project_id):
    student_id = session.get('user_id')
    project = Project.query.filter_by(id=project_id, student_id=student_id).first_or_404()
    db.session.delete(project)
    db.session.commit()
    flash('Project deleted successfully.', 'info')
    return redirect(url_for('projects'))

# Progress Update Route
@app.route('/student/projects/update_progress/<int:project_id>', methods=['POST'])
@student_required
def update_progress(project_id):
    student_id = session.get('user_id')
    project = Project.query.filter_by(id=project_id, student_id=student_id).first_or_404()

    progress = request.form.get('progress_percentage', type=int, default=project.progress_percentage)
    status = request.form.get('status', project.status)
    notes = request.form.get('progress_notes', '').strip()

    project.progress_percentage = max(0, min(100, progress))
    project.status = status
    project.progress_notes = notes
    project.last_updated_date = date.today()

    if project.progress_percentage == 100 and project.status != 'Cancelled':
        project.status = 'Completed'

    db.session.commit()
    flash('Project progress updated successfully!', 'success')
    return redirect(url_for('project_details', project_id=project.id))

# Task Management
@app.route('/student/tasks', methods=['GET', 'POST'])
@student_required
def tasks():
    student_id = session.get('user_id')
    projects = Project.query.filter_by(student_id=student_id).all()

    if request.method == 'POST':
        project_id = request.form.get('project_id', type=int)
        title = request.form.get('title', '').strip()
        description = request.form.get('description', '').strip()
        due_date = parse_date(request.form.get('due_date'))
        priority = request.form.get('priority', 'Medium')
        status = request.form.get('status', 'Pending')

        if not project_id or not title:
            flash('Project selection and Task Title are required.', 'danger')
            return redirect(url_for('tasks'))

        task = Task(
            project_id=project_id,
            student_id=student_id,
            title=title,
            description=description,
            due_date=due_date,
            priority=priority,
            status=status
        )
        db.session.add(task)
        db.session.commit()
        flash('Task added successfully!', 'success')
        return redirect(url_for('tasks'))

    filter_project = request.args.get('project_id', type=int)
    filter_status = request.args.get('status', '').strip()

    query = Task.query.filter_by(student_id=student_id)
    if filter_project:
        query = query.filter_by(project_id=filter_project)
    if filter_status:
        query = query.filter_by(status=filter_status)

    student_tasks = query.order_by(Task.created_at.desc()).all()
    return render_template('tasks.html', tasks=student_tasks, projects=projects, filter_project=filter_project, filter_status=filter_status)

@app.route('/student/tasks/update_status/<int:task_id>', methods=['POST'])
@student_required
def update_task_status(task_id):
    student_id = session.get('user_id')
    task = Task.query.filter_by(id=task_id, student_id=student_id).first_or_404()
    new_status = request.form.get('status', task.status)
    task.status = new_status
    db.session.commit()
    flash('Task status updated successfully!', 'success')
    return redirect(request.referrer or url_for('tasks'))

@app.route('/student/tasks/delete/<int:task_id>', methods=['POST'])
@student_required
def delete_task(task_id):
    student_id = session.get('user_id')
    task = Task.query.filter_by(id=task_id, student_id=student_id).first_or_404()
    db.session.delete(task)
    db.session.commit()
    flash('Task deleted.', 'info')
    return redirect(request.referrer or url_for('tasks'))

# Client Management
@app.route('/student/clients')
@student_required
def clients():
    student_id = session.get('user_id')
    student_clients = Client.query.filter_by(student_id=student_id).all()
    return render_template('clients.html', clients=student_clients)

@app.route('/student/clients/add', methods=['GET', 'POST'])
@student_required
def add_client():
    student_id = session.get('user_id')
    if request.method == 'POST':
        name = request.form.get('name', '').strip()
        phone = request.form.get('phone', '').strip()
        email = request.form.get('email', '').strip()
        company_name = request.form.get('company_name', '').strip()
        address = request.form.get('address', '').strip()
        notes = request.form.get('notes', '').strip()

        if not name:
            flash('Client Name is required.', 'danger')
            return redirect(url_for('add_client'))

        client = Client(
            student_id=student_id,
            name=name,
            phone=phone,
            email=email,
            company_name=company_name,
            address=address,
            notes=notes
        )
        db.session.add(client)
        db.session.commit()
        flash(f'Client "{name}" added successfully!', 'success')
        return redirect(url_for('clients'))

    return render_template('add_client.html')

@app.route('/student/clients/edit/<int:client_id>', methods=['POST'])
@student_required
def edit_client(client_id):
    student_id = session.get('user_id')
    client = Client.query.filter_by(id=client_id, student_id=student_id).first_or_404()

    client.name = request.form.get('name', client.name).strip()
    client.phone = request.form.get('phone', '').strip()
    client.email = request.form.get('email', '').strip()
    client.company_name = request.form.get('company_name', '').strip()
    client.address = request.form.get('address', '').strip()
    client.notes = request.form.get('notes', '').strip()

    db.session.commit()
    flash('Client updated successfully!', 'success')
    return redirect(url_for('clients'))

@app.route('/student/clients/delete/<int:client_id>', methods=['POST'])
@student_required
def delete_client(client_id):
    student_id = session.get('user_id')
    client = Client.query.filter_by(id=client_id, student_id=student_id).first_or_404()
    db.session.delete(client)
    db.session.commit()
    flash('Client deleted.', 'info')
    return redirect(url_for('clients'))

# Payment Tracking
@app.route('/student/payments', methods=['GET', 'POST'])
@student_required
def payments():
    student_id = session.get('user_id')
    projects = Project.query.filter_by(student_id=student_id).all()

    if request.method == 'POST':
        project_id = request.form.get('project_id', type=int)
        client_name = request.form.get('client_name', '').strip()
        amount = request.form.get('amount', type=float, default=0.0)
        payment_date = parse_date(request.form.get('payment_date')) or date.today()
        status = request.form.get('status', 'Pending')
        notes = request.form.get('notes', '').strip()

        if not project_id or amount <= 0:
            flash('Project and valid positive Amount are required.', 'danger')
            return redirect(url_for('payments'))

        if not client_name:
            project_obj = Project.query.get(project_id)
            if project_obj:
                client_name = project_obj.client_name

        payment = Payment(
            project_id=project_id,
            student_id=student_id,
            client_name=client_name or 'Client',
            amount=amount,
            payment_date=payment_date,
            status=status,
            notes=notes
        )
        db.session.add(payment)
        db.session.commit()
        flash('Payment record added successfully!', 'success')
        return redirect(url_for('payments'))

    student_payments = Payment.query.filter_by(student_id=student_id).order_by(Payment.payment_date.desc()).all()
    return render_template('payments.html', payments=student_payments, projects=projects)

@app.route('/student/payments/update_status/<int:payment_id>', methods=['POST'])
@student_required
def update_payment_status(payment_id):
    student_id = session.get('user_id')
    payment = Payment.query.filter_by(id=payment_id, student_id=student_id).first_or_404()
    payment.status = request.form.get('status', payment.status)
    db.session.commit()
    flash('Payment status updated!', 'success')
    return redirect(url_for('payments'))

@app.route('/student/payments/delete/<int:payment_id>', methods=['POST'])
@student_required
def delete_payment(payment_id):
    student_id = session.get('user_id')
    payment = Payment.query.filter_by(id=payment_id, student_id=student_id).first_or_404()
    db.session.delete(payment)
    db.session.commit()
    flash('Payment record deleted.', 'info')
    return redirect(url_for('payments'))

# Admin Module Routes
@app.route('/admin/dashboard')
@admin_required
def admin_dashboard():
    total_students = Student.query.count()
    all_projects = Project.query.all()
    total_projects = len(all_projects)
    active_projects = len([p for p in all_projects if p.status in ['New', 'In Progress', 'On Hold']])
    completed_projects = len([p for p in all_projects if p.status == 'Completed'])
    pending_projects = len([p for p in all_projects if p.status in ['New', 'On Hold']])
    total_clients = Client.query.count()

    recent_students = Student.query.order_by(Student.created_at.desc()).limit(5).all()
    recent_projects = Project.query.order_by(Project.created_at.desc()).limit(5).all()

    return render_template(
        'admin_dashboard.html',
        total_students=total_students,
        total_projects=total_projects,
        active_projects=active_projects,
        completed_projects=completed_projects,
        pending_projects=pending_projects,
        total_clients=total_clients,
        recent_students=recent_students,
        recent_projects=recent_projects
    )

@app.route('/admin/students')
@admin_required
def manage_students():
    search_query = request.args.get('search', '').strip()
    query = Student.query

    if search_query:
        query = query.filter(
            (Student.name.ilike(f'%{search_query}%')) |
            (Student.register_number.ilike(f'%{search_query}%')) |
            (Student.department.ilike(f'%{search_query}%')) |
            (Student.email.ilike(f'%{search_query}%'))
        )

    students_list = query.order_by(Student.created_at.desc()).all()
    return render_template('manage_students.html', students=students_list, search=search_query)

@app.route('/admin/students/<int:student_id>')
@admin_required
def view_student_profile(student_id):
    student = Student.query.get_or_404(student_id)
    profile = StudentProfile.query.filter_by(student_id=student.id).first()
    projects = Project.query.filter_by(student_id=student.id).all()
    clients = Client.query.filter_by(student_id=student.id).all()
    return render_template('view_student_profile.html', student=student, profile=profile, projects=projects, clients=clients)

@app.route('/admin/students/delete/<int:student_id>', methods=['POST'])
@admin_required
def delete_student(student_id):
    student = Student.query.get_or_404(student_id)
    db.session.delete(student)
    db.session.commit()
    flash(f'Student "{student.name}" deleted successfully.', 'info')
    return redirect(url_for('manage_students'))

@app.route('/admin/projects')
@admin_required
def monitor_projects():
    search_query = request.args.get('search', '').strip()
    status_filter = request.args.get('status', '').strip()

    query = Project.query.join(Student)

    if search_query:
        query = query.filter(
            (Project.title.ilike(f'%{search_query}%')) |
            (Project.client_name.ilike(f'%{search_query}%')) |
            (Student.name.ilike(f'%{search_query}%'))
        )
    if status_filter:
        query = query.filter(Project.status == status_filter)

    all_projects = query.order_by(Project.created_at.desc()).all()
    return render_template('monitor_projects.html', projects=all_projects, search=search_query, status_filter=status_filter)

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True)
