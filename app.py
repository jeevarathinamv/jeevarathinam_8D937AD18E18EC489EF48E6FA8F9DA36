import os
from datetime import datetime
from functools import wraps
from flask import Flask, render_template, request, redirect, url_for, flash, session
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'smart_college_helpdesk_secret_key_98765')

# Admin Hardcoded Fallback Credentials
ADMIN_USERNAME = os.environ.get('ADMIN_USERNAME', 'admin')
ADMIN_PASSWORD = os.environ.get('ADMIN_PASSWORD', 'admin123')

# Database configuration: Default to MySQL URI, fallback/option for SQLite
MYSQL_URI = os.environ.get('DATABASE_URL', 'mysql+pymysql://root:@localhost/smart_college_helpdesk')
SQLITE_URI = 'sqlite:///' + os.path.join(os.path.abspath(os.path.dirname(__file__)), 'smart_college_helpdesk.db')

use_sqlite = os.environ.get('USE_SQLITE') == '1'
app.config['SQLALCHEMY_DATABASE_URI'] = SQLITE_URI if use_sqlite else MYSQL_URI
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

# Models
class Student(db.Model):
    __tablename__ = 'students'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    register_number = db.Column(db.String(50), unique=True, nullable=False)
    department = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    requests = db.relationship('HelpRequest', backref='student', lazy=True)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

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

class HelpRequest(db.Model):
    __tablename__ = 'help_requests'
    id = db.Column(db.Integer, primary_key=True)
    student_id = db.Column(db.Integer, db.ForeignKey('students.id'), nullable=False)
    category = db.Column(db.String(50), nullable=False) # Academic, Fees, Exam, Lab, Other
    subject = db.Column(db.String(150), nullable=False)
    description = db.Column(db.Text, nullable=False)
    status = db.Column(db.String(20), default='Pending') # Pending, In Progress, Resolved
    admin_reply = db.Column(db.Text, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

def seed_default_admin():
    admin = Admin.query.filter_by(username=ADMIN_USERNAME).first()
    if not admin:
        new_admin = Admin(username=ADMIN_USERNAME)
        new_admin.set_password(ADMIN_PASSWORD)
        db.session.add(new_admin)
        db.session.commit()

# Predefined FAQs for Smart Help
FAQS = {
    'Academic': [
        {
            'question': 'How can I request attendance correction or leave approval?',
            'answer': 'Attendance corrections require an application endorsed by your Head of Department (HOD) submitted to the academic office within 3 working days.'
        },
        {
            'question': 'What is the procedure to change or add elective courses?',
            'answer': 'Elective changes can be requested during the first week of the semester through your academic coordinator.'
        }
    ],
    'Fees': [
        {
            'question': 'How can I pay tuition fees online?',
            'answer': 'Visit the official college portal student accounts section. We support net banking, UPI, and major debit/credit cards.'
        },
        {
            'question': 'What is the deadline for late fee waiver requests?',
            'answer': 'Late fee waiver requests must be submitted to the accounts office prior to the last date of fee payment with supporting documents.'
        }
    ],
    'Exam': [
        {
            'question': 'When will the hall ticket / admit card be issued?',
            'answer': 'Hall tickets are available for download from the student portal 5 days before the semester examinations commence, provided all dues are cleared.'
        },
        {
            'question': 'How do I apply for revaluation of exam papers?',
            'answer': 'Revaluation applications are open for 10 days after result announcement. Submit the form in the Controller of Examinations section.'
        }
    ],
    'Lab': [
        {
            'question': 'What are the computer lab timing hours for self-study?',
            'answer': 'The central computing facility is open from 8:00 AM to 7:00 PM on working weekdays.'
        },
        {
            'question': 'How do I get access to specialized lab software/hardware?',
            'answer': 'Submit a request approved by your lab instructor specifying project requirements and system configuration needs.'
        }
    ],
    'Other': [
        {
            'question': 'How do I apply for a bonafide or transfer certificate?',
            'answer': 'Certificate applications can be submitted online or directly at the student administrative office with valid student ID.'
        },
        {
            'question': 'Who should I contact for hostel or transportation queries?',
            'answer': 'Please contact the Student Welfare Officer or visit the Campus Administrative Desk on Floor 1.'
        }
    ]
}

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

            admin = Admin.query.filter_by(username=username).first()
            if (admin and admin.check_password(password)) or (username == ADMIN_USERNAME and password == ADMIN_PASSWORD):
                session['user_type'] = 'admin'
                session['user_name'] = 'Administrator'
                flash('Logged in successfully as Help Desk Administrator.', 'success')
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

# Smart Help Module
@app.route('/smart-help')
def smart_help():
    selected_category = request.args.get('category', 'Academic')
    if selected_category not in FAQS:
        selected_category = 'Academic'

    suggested_faqs = FAQS.get(selected_category, [])
    return render_template(
        'smart_help.html',
        categories=list(FAQS.keys()),
        selected_category=selected_category,
        faqs=suggested_faqs
    )

# Submit Help Request Page & Action
@app.route('/student/request/new', methods=['GET', 'POST'])
@student_required
def submit_request():
    if request.method == 'POST':
        category = request.form.get('category', '').strip()
        subject = request.form.get('subject', '').strip()
        description = request.form.get('description', '').strip()

        valid_categories = ['Academic', 'Fees', 'Exam', 'Lab', 'Other']
        if not category or category not in valid_categories or not subject or not description:
            flash('Please fill in all fields with valid information.', 'danger')
            return redirect(url_for('submit_request'))

        student_id = session.get('user_id')
        help_req = HelpRequest(
            student_id=student_id,
            category=category,
            subject=subject,
            description=description,
            status='Pending'
        )
        db.session.add(help_req)
        db.session.commit()

        flash('Your help request has been submitted successfully!', 'success')
        return redirect(url_for('student_dashboard'))

    category_param = request.args.get('category', 'Academic')
    return render_template('submit_request.html', default_category=category_param)

# Student Dashboard
@app.route('/student/dashboard')
@student_required
def student_dashboard():
    student_id = session.get('user_id')
    student = db.session.get(Student, student_id)
    requests_list = HelpRequest.query.filter_by(student_id=student_id).order_by(HelpRequest.created_at.desc()).all()

    pending_count = len([r for r in requests_list if r.status == 'Pending'])
    in_progress_count = len([r for r in requests_list if r.status == 'In Progress'])
    resolved_count = len([r for r in requests_list if r.status == 'Resolved'])

    return render_template(
        'student_dashboard.html',
        student=student,
        requests=requests_list,
        pending_count=pending_count,
        in_progress_count=in_progress_count,
        resolved_count=resolved_count
    )

# Admin Help Desk Dashboard
@app.route('/admin/dashboard')
@admin_required
def admin_dashboard():
    category_filter = request.args.get('category', 'All')
    status_filter = request.args.get('status', 'All')

    query = HelpRequest.query
    if category_filter != 'All':
        query = query.filter_by(category=category_filter)
    if status_filter != 'All':
        query = query.filter_by(status=status_filter)

    all_requests = query.order_by(HelpRequest.created_at.desc()).all()

    total_requests = HelpRequest.query.count()
    pending_count = HelpRequest.query.filter_by(status='Pending').count()
    in_progress_count = HelpRequest.query.filter_by(status='In Progress').count()
    resolved_count = HelpRequest.query.filter_by(status='Resolved').count()

    return render_template(
        'admin_dashboard.html',
        requests=all_requests,
        total_requests=total_requests,
        pending_count=pending_count,
        in_progress_count=in_progress_count,
        resolved_count=resolved_count,
        selected_category=category_filter,
        selected_status=status_filter
    )

# Admin Reply & Status Update
@app.route('/admin/request/reply/<int:request_id>', methods=['POST'])
@admin_required
def admin_reply_request(request_id):
    help_req = db.session.get(HelpRequest, request_id)
    if not help_req:
        flash('Help request not found.', 'danger')
        return redirect(url_for('admin_dashboard'))

    reply_text = request.form.get('admin_reply', '').strip()
    status = request.form.get('status', 'Pending').strip()

    valid_statuses = ['Pending', 'In Progress', 'Resolved']
    if status not in valid_statuses:
        status = 'Pending'

    if reply_text:
        help_req.admin_reply = reply_text
    help_req.status = status
    help_req.updated_at = datetime.utcnow()

    db.session.commit()
    flash(f'Request #{help_req.id} updated successfully to status "{status}".', 'success')
    return redirect(url_for('admin_dashboard'))

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
        seed_default_admin()
    app.run(debug=True)
