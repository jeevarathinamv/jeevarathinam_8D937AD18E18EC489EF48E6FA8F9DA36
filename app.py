import os
from datetime import datetime, date
from functools import wraps
from flask import Flask, render_template, request, redirect, url_for, flash, session
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'student_assignment_secret_key_2025')

# Admin Hardcoded Fallback Credentials
ADMIN_USERNAME = os.environ.get('ADMIN_USERNAME', 'admin')
ADMIN_PASSWORD = os.environ.get('ADMIN_PASSWORD', 'admin123')

# Database Configuration
MYSQL_URI = os.environ.get('DATABASE_URL', 'mysql+pymysql://root:@localhost/student_assignment_db')
SQLITE_URI = 'sqlite:///' + os.path.join(os.path.abspath(os.path.dirname(__file__)), 'assignment_tracker.db')

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
    password_hash = db.Column(db.String(255), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    submissions = db.relationship('Submission', backref='student', lazy=True, cascade='all, delete-orphan')

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

class Admin(db.Model):
    __tablename__ = 'admins'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

class Assignment(db.Model):
    __tablename__ = 'assignments'
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    subject = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text, nullable=False)
    given_date = db.Column(db.Date, nullable=False)
    deadline_date = db.Column(db.Date, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    submissions = db.relationship('Submission', backref='assignment', lazy=True, cascade='all, delete-orphan')

class Submission(db.Model):
    __tablename__ = 'submissions'
    id = db.Column(db.Integer, primary_key=True)
    assignment_id = db.Column(db.Integer, db.ForeignKey('assignments.id', ondelete='CASCADE'), nullable=False)
    student_id = db.Column(db.Integer, db.ForeignKey('students.id', ondelete='CASCADE'), nullable=False)
    student_register_number = db.Column(db.String(50), nullable=False)
    submission_date = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    submission_text = db.Column(db.Text, nullable=False)
    status = db.Column(db.String(20), default='Submitted') # 'Submitted' or 'Late'
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

# Helper Functions
def get_deadline_status(deadline_date):
    """Calculates deadline status relative to today's date."""
    today = date.today()
    if isinstance(deadline_date, str):
        deadline_date = datetime.strptime(deadline_date, '%Y-%m-%d').date()

    days_left = (deadline_date - today).days

    if days_left < 0:
        return {'label': 'Deadline Passed', 'class': 'danger', 'days_left': days_left}
    elif days_left <= 2:
        return {'label': 'Due Soon', 'class': 'warning', 'days_left': days_left}
    else:
        return {'label': 'Upcoming', 'class': 'info', 'days_left': days_left}

def seed_default_data():
    """Seeds default admin and initial assignments if database is empty."""
    if Admin.query.count() == 0:
        admin = Admin(
            username=ADMIN_USERNAME,
            email='admin@college.edu'
        )
        admin.set_password(ADMIN_PASSWORD)
        db.session.add(admin)
        db.session.commit()

    if Assignment.query.count() == 0:
        today = date.today()
        from datetime import timedelta
        sample_assignments = [
            Assignment(
                title='Flask Web Architecture & Routing',
                subject='Web Technologies',
                description='Build a multi-route web application using Python Flask, Werkzeug routing, and Jinja templates.',
                given_date=today - timedelta(days=5),
                deadline_date=today + timedelta(days=5)
            ),
            Assignment(
                title='Database Normalization & ER Diagrams',
                subject='Database Management Systems',
                description='Explain 1NF, 2NF, 3NF, and BCNF with real-world examples and entity-relationship diagrams.',
                given_date=today - timedelta(days=3),
                deadline_date=today + timedelta(days=1)
            ),
            Assignment(
                title='Data Structures: Tree Traversals',
                subject='Data Structures & Algorithms',
                description='Implement In-order, Pre-order, and Post-order traversals in Python with time complexity analysis.',
                given_date=today - timedelta(days=10),
                deadline_date=today - timedelta(days=2)
            )
        ]
        db.session.add_all(sample_assignments)
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
            flash('Admin access required. Please log in as Admin.', 'warning')
            return redirect(url_for('admin_login'))
        return f(*args, **kwargs)
    return decorated_function

# Context Processor for Templates
@app.context_processor
def utility_processor():
    return dict(get_deadline_status=get_deadline_status, today_date=date.today())

# Routes
@app.route('/')
def index():
    if session.get('user_type') == 'student':
        return redirect(url_for('student_dashboard'))
    elif session.get('user_type') == 'admin':
        return redirect(url_for('admin_dashboard'))
    return redirect(url_for('login'))

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
            flash('All registration fields are required.', 'danger')
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
            flash('Please enter your Email/Register Number and Password.', 'danger')
            return redirect(url_for('login'))

        student = Student.query.filter(
            (Student.email == email_or_reg.lower()) | (Student.register_number == email_or_reg)
        ).first()

        if student and student.check_password(password):
            session['user_type'] = 'student'
            session['user_id'] = student.id
            session['user_name'] = student.name
            session['register_number'] = student.register_number
            flash(f'Welcome back, {student.name}!', 'success')
            return redirect(url_for('student_dashboard'))
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

        if not username or not password:
            flash('Username and password are required.', 'danger')
            return redirect(url_for('admin_login'))

        admin = Admin.query.filter_by(username=username).first()

        if admin and admin.check_password(password):
            session['user_type'] = 'admin'
            session['user_id'] = admin.id
            session['user_name'] = 'Administrator'
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
    flash('You have been logged out successfully.', 'info')
    return redirect(url_for('login'))

# Student Dashboard
@app.route('/student/dashboard')
@student_required
def student_dashboard():
    student_id = session.get('user_id')
    student = Student.query.get_or_404(student_id)

    assignments = Assignment.query.order_by(Assignment.deadline_date.asc()).all()
    my_submissions = Submission.query.filter_by(student_id=student_id).all()
    submitted_assignment_ids = {s.assignment_id for s in my_submissions}

    total_assignments = len(assignments)
    submitted_count = len(submitted_assignment_ids)
    pending_count = total_assignments - submitted_count

    today = date.today()
    upcoming_deadlines = len([
        a for a in assignments
        if a.id not in submitted_assignment_ids and a.deadline_date >= today
    ])

    return render_template(
        'student_dashboard.html',
        student=student,
        assignments=assignments,
        submitted_assignment_ids=submitted_assignment_ids,
        total_assignments=total_assignments,
        submitted_count=submitted_count,
        pending_count=pending_count,
        upcoming_deadlines=upcoming_deadlines
    )

# Student Assignment List
@app.route('/student/assignments')
@student_required
def student_assignments():
    student_id = session.get('user_id')
    assignments = Assignment.query.order_by(Assignment.deadline_date.asc()).all()

    my_submissions = Submission.query.filter_by(student_id=student_id).all()
    submissions_dict = {s.assignment_id: s for s in my_submissions}

    return render_template(
        'assignments.html',
        assignments=assignments,
        submissions_dict=submissions_dict
    )

# Student Submit Assignment
@app.route('/student/submit/<int:assignment_id>', methods=['GET', 'POST'])
@student_required
def submit_assignment(assignment_id):
    student_id = session.get('user_id')
    student = Student.query.get_or_404(student_id)
    assignment = Assignment.query.get_or_404(assignment_id)

    existing_submission = Submission.query.filter_by(
        assignment_id=assignment_id,
        student_id=student_id
    ).first()

    if request.method == 'POST':
        submission_text = request.form.get('submission_text', '').strip()

        if not submission_text:
            flash('Submission text or link cannot be empty.', 'danger')
            return redirect(url_for('submit_assignment', assignment_id=assignment_id))

        now = datetime.now()

        # Determine status: if submission date is past the deadline date
        if now.date() > assignment.deadline_date:
            status = 'Late'
        else:
            status = 'Submitted'

        if existing_submission:
            existing_submission.submission_text = submission_text
            existing_submission.submission_date = now
            existing_submission.status = status
            flash('Assignment submission updated successfully!', 'success')
        else:
            submission = Submission(
                assignment_id=assignment_id,
                student_id=student_id,
                student_register_number=student.register_number,
                submission_date=now,
                submission_text=submission_text,
                status=status
            )
            db.session.add(submission)
            flash(f'Assignment submitted successfully! Status: {status}', 'success')

        db.session.commit()
        return redirect(url_for('submission_history'))

    return render_template(
        'submit_assignment.html',
        assignment=assignment,
        student=student,
        existing_submission=existing_submission
    )

# Student Submission History
@app.route('/student/history')
@student_required
def submission_history():
    student_id = session.get('user_id')
    submissions = Submission.query.filter_by(student_id=student_id).order_by(Submission.submission_date.desc()).all()
    return render_template('submission_history.html', submissions=submissions)

# Admin Dashboard
@app.route('/admin/dashboard')
@admin_required
def admin_dashboard():
    total_students = Student.query.count()
    total_assignments = Assignment.query.count()

    submissions = Submission.query.all()
    submitted_count = len([s for s in submissions if s.status == 'Submitted'])
    late_count = len([s for s in submissions if s.status == 'Late'])

    # Pending count: Total required submissions across all active students minus actual submissions made
    total_possible_submissions = total_students * total_assignments
    actual_submissions_count = len(submissions)
    pending_count = max(0, total_possible_submissions - actual_submissions_count)

    recent_submissions = Submission.query.order_by(Submission.submission_date.desc()).limit(5).all()

    return render_template(
        'admin_dashboard.html',
        total_students=total_students,
        total_assignments=total_assignments,
        submitted_count=submitted_count,
        pending_count=pending_count,
        late_count=late_count,
        recent_submissions=recent_submissions
    )

# Admin Assignment Management
@app.route('/admin/assignments')
@admin_required
def manage_assignments():
    assignments = Assignment.query.order_by(Assignment.created_at.desc()).all()
    return render_template('manage_assignments.html', assignments=assignments)

@app.route('/admin/assignment/add', methods=['POST'])
@admin_required
def add_assignment():
    title = request.form.get('title', '').strip()
    subject = request.form.get('subject', '').strip()
    description = request.form.get('description', '').strip()
    given_date_str = request.form.get('given_date', '')
    deadline_date_str = request.form.get('deadline_date', '')

    if not title or not subject or not description or not given_date_str or not deadline_date_str:
        flash('All assignment fields are required.', 'danger')
        return redirect(url_for('manage_assignments'))

    try:
        given_date = datetime.strptime(given_date_str, '%Y-%m-%d').date()
        deadline_date = datetime.strptime(deadline_date_str, '%Y-%m-%d').date()
    except ValueError:
        flash('Invalid date format provided.', 'danger')
        return redirect(url_for('manage_assignments'))

    if deadline_date < given_date:
        flash('Deadline date cannot be earlier than given date.', 'danger')
        return redirect(url_for('manage_assignments'))

    assignment = Assignment(
        title=title,
        subject=subject,
        description=description,
        given_date=given_date,
        deadline_date=deadline_date
    )
    db.session.add(assignment)
    db.session.commit()

    flash(f'Assignment "{title}" created successfully.', 'success')
    return redirect(url_for('manage_assignments'))

@app.route('/admin/assignment/edit/<int:assignment_id>', methods=['POST'])
@admin_required
def edit_assignment(assignment_id):
    assignment = Assignment.query.get_or_404(assignment_id)

    title = request.form.get('title', '').strip()
    subject = request.form.get('subject', '').strip()
    description = request.form.get('description', '').strip()
    given_date_str = request.form.get('given_date', '')
    deadline_date_str = request.form.get('deadline_date', '')

    if not title or not subject or not description or not given_date_str or not deadline_date_str:
        flash('All assignment fields are required.', 'danger')
        return redirect(url_for('manage_assignments'))

    try:
        given_date = datetime.strptime(given_date_str, '%Y-%m-%d').date()
        deadline_date = datetime.strptime(deadline_date_str, '%Y-%m-%d').date()
    except ValueError:
        flash('Invalid date format.', 'danger')
        return redirect(url_for('manage_assignments'))

    if deadline_date < given_date:
        flash('Deadline date cannot be earlier than given date.', 'danger')
        return redirect(url_for('manage_assignments'))

    assignment.title = title
    assignment.subject = subject
    assignment.description = description
    assignment.given_date = given_date
    assignment.deadline_date = deadline_date

    db.session.commit()
    flash(f'Assignment "{assignment.title}" updated successfully.', 'success')
    return redirect(url_for('manage_assignments'))

@app.route('/admin/assignment/delete/<int:assignment_id>', methods=['POST'])
@admin_required
def delete_assignment(assignment_id):
    assignment = Assignment.query.get_or_404(assignment_id)
    title = assignment.title
    db.session.delete(assignment)
    db.session.commit()

    flash(f'Assignment "{title}" deleted successfully.', 'info')
    return redirect(url_for('manage_assignments'))

# Admin Submissions Management
@app.route('/admin/submissions')
@admin_required
def manage_submissions():
    submissions = Submission.query.order_by(Submission.submission_date.desc()).all()
    return render_template('submissions.html', submissions=submissions)

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
        seed_default_data()
    app.run(debug=True)
