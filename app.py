import os
import random
import string
from datetime import datetime, date
from functools import wraps
from flask import Flask, render_template, request, redirect, url_for, flash, session
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'canteen_feedback_secret_key_987654')

# Database configuration: Default to MySQL URI, fallback/option for SQLite
MYSQL_URI = os.environ.get('DATABASE_URL', 'mysql+pymysql://root:@localhost/canteen_feedback_db')
SQLITE_URI = 'sqlite:///' + os.path.join(os.path.abspath(os.path.dirname(__file__)), 'canteen_feedback.db')

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
    full_name = db.Column(db.String(100), nullable=False, default='Canteen Admin')
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

    feedbacks = db.relationship('Feedback', backref='student', lazy=True, cascade="all, delete-orphan")
    complaints = db.relationship('Complaint', backref='student', lazy=True, cascade="all, delete-orphan")

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

class Feedback(db.Model):
    __tablename__ = 'feedback'
    id = db.Column(db.Integer, primary_key=True)
    student_id = db.Column(db.Integer, db.ForeignKey('students.id'), nullable=False)
    food_quality_rating = db.Column(db.Integer, nullable=False, default=5)
    taste_rating = db.Column(db.Integer, nullable=False, default=5)
    cleanliness_rating = db.Column(db.Integer, nullable=False, default=5)
    service_rating = db.Column(db.Integer, nullable=False, default=5)
    overall_rating = db.Column(db.Integer, nullable=False, default=5)
    message = db.Column(db.Text, nullable=False)
    feedback_date = db.Column(db.Date, nullable=False, default=date.today)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class Complaint(db.Model):
    __tablename__ = 'complaints'
    id = db.Column(db.Integer, primary_key=True)
    complaint_id = db.Column(db.String(30), unique=True, nullable=False)
    student_id = db.Column(db.Integer, db.ForeignKey('students.id'), nullable=False)
    complaint_type = db.Column(db.String(50), nullable=False)
    description = db.Column(db.Text, nullable=False)
    complaint_date = db.Column(db.Date, nullable=False, default=date.today)
    status = db.Column(db.String(20), nullable=False, default='Pending') # Pending, In Progress, Resolved, Rejected
    admin_remarks = db.Column(db.Text, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

def generate_complaint_id():
    """Generates a unique Complaint ID like CMP-20231024-8F32."""
    date_str = date.today().strftime('%Y%m%d')
    rand_str = ''.join(random.choices(string.ascii_uppercase + string.digits, k=4))
    complaint_id = f"CMP-{date_str}-{rand_str}"
    while Complaint.query.filter_by(complaint_id=complaint_id).first():
        rand_str = ''.join(random.choices(string.ascii_uppercase + string.digits, k=4))
        complaint_id = f"CMP-{date_str}-{rand_str}"
    return complaint_id

def seed_default_admin():
    """Seeds the initial admin account if not already present."""
    if Admin.query.filter_by(username='admin').first() is None:
        admin = Admin(username='admin', full_name='Main Canteen Administrator')
        admin.set_password('admin123')
        db.session.add(admin)
        db.session.commit()

# Authentication Decorators
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

# Home Page
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

        flash('Registration successful! Please log in to continue.', 'success')
        return redirect(url_for('login'))

    return render_template('register.html')

# Student Login
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email_or_reg = request.form.get('email_or_reg', '').strip()
        password = request.form.get('password', '')

        if not email_or_reg or not password:
            flash('Please provide both Register Number/Email and Password.', 'danger')
            return redirect(url_for('login'))

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
            flash('Invalid Register Number/Email or Password.', 'danger')
            return redirect(url_for('login'))

    return render_template('login.html')

# Admin Login
@app.route('/admin/login', methods=['GET', 'POST'])
def admin_login():
    if request.method == 'POST':
        username = request.form.get('username', '').strip()
        password = request.form.get('password', '')

        if not username or not password:
            flash('Please enter Admin Username and Password.', 'danger')
            return redirect(url_for('admin_login'))

        admin = Admin.query.filter_by(username=username).first()
        if admin and admin.check_password(password):
            session['user_type'] = 'admin'
            session['user_id'] = admin.id
            session['user_name'] = admin.full_name
            flash('Logged in successfully as Administrator.', 'success')
            return redirect(url_for('admin_dashboard'))
        else:
            flash('Invalid Admin Credentials.', 'danger')
            return redirect(url_for('admin_login'))

    return render_template('admin_login.html')

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
    student_id = session.get('user_id')
    student = Student.query.get(student_id)

    feedbacks = Feedback.query.filter_by(student_id=student_id).all()
    complaints = Complaint.query.filter_by(student_id=student_id).all()

    total_feedback = len(feedbacks)
    total_complaints = len(complaints)
    pending_complaints = len([c for c in complaints if c.status == 'Pending'])
    resolved_complaints = len([c for c in complaints if c.status == 'Resolved'])

    return render_template(
        'student_dashboard.html',
        student=student,
        total_feedback=total_feedback,
        total_complaints=total_complaints,
        pending_complaints=pending_complaints,
        resolved_complaints=resolved_complaints
    )

# Submit Feedback
@app.route('/student/feedback', methods=['GET', 'POST'])
@student_required
def submit_feedback():
    if request.method == 'POST':
        student_id = session.get('user_id')
        food_quality = request.form.get('food_quality_rating', type=int, default=5)
        taste = request.form.get('taste_rating', type=int, default=5)
        cleanliness = request.form.get('cleanliness_rating', type=int, default=5)
        service = request.form.get('service_rating', type=int, default=5)
        overall = request.form.get('overall_rating', type=int, default=5)
        message = request.form.get('message', '').strip()
        feedback_date_str = request.form.get('feedback_date', date.today().isoformat())

        if not message:
            flash('Please enter your feedback message.', 'danger')
            return redirect(url_for('submit_feedback'))

        try:
            feedback_date = datetime.strptime(feedback_date_str, '%Y-%m-%d').date()
        except ValueError:
            feedback_date = date.today()

        feedback = Feedback(
            student_id=student_id,
            food_quality_rating=food_quality,
            taste_rating=taste,
            cleanliness_rating=cleanliness,
            service_rating=service,
            overall_rating=overall,
            message=message,
            feedback_date=feedback_date
        )
        db.session.add(feedback)
        db.session.commit()

        flash('Thank you! Your feedback has been submitted successfully.', 'success')
        return redirect(url_for('my_feedback'))

    today_str = date.today().isoformat()
    return render_template('feedback.html', today=today_str)

# Submit Complaint
@app.route('/student/complaint', methods=['GET', 'POST'])
@student_required
def submit_complaint():
    if request.method == 'POST':
        student_id = session.get('user_id')
        complaint_type = request.form.get('complaint_type', '').strip()
        description = request.form.get('description', '').strip()
        complaint_date_str = request.form.get('complaint_date', date.today().isoformat())

        valid_types = ['Food Quality', 'Cleanliness', 'Service', 'Price', 'Staff Behaviour', 'Other']
        if not complaint_type or complaint_type not in valid_types:
            flash('Please select a valid Complaint Type.', 'danger')
            return redirect(url_for('submit_complaint'))

        if not description:
            flash('Please provide a detailed complaint description.', 'danger')
            return redirect(url_for('submit_complaint'))

        try:
            complaint_date = datetime.strptime(complaint_date_str, '%Y-%m-%d').date()
        except ValueError:
            complaint_date = date.today()

        complaint_id = generate_complaint_id()

        complaint = Complaint(
            complaint_id=complaint_id,
            student_id=student_id,
            complaint_type=complaint_type,
            description=description,
            complaint_date=complaint_date,
            status='Pending'
        )
        db.session.add(complaint)
        db.session.commit()

        flash(f'Complaint submitted successfully! Your Complaint ID is {complaint_id}.', 'success')
        return redirect(url_for('my_complaints'))

    today_str = date.today().isoformat()
    return render_template('complaint.html', today=today_str)

# My Feedback
@app.route('/student/my-feedback')
@student_required
def my_feedback():
    student_id = session.get('user_id')
    feedbacks = Feedback.query.filter_by(student_id=student_id).order_by(Feedback.created_at.desc()).all()
    return render_template('my_feedback.html', feedbacks=feedbacks)

# My Complaints
@app.route('/student/my-complaints')
@student_required
def my_complaints():
    student_id = session.get('user_id')
    complaints = Complaint.query.filter_by(student_id=student_id).order_by(Complaint.created_at.desc()).all()
    return render_template('my_complaints.html', complaints=complaints)

# Admin Dashboard
@app.route('/admin/dashboard')
@admin_required
def admin_dashboard():
    total_students = Student.query.count()
    total_feedback = Feedback.query.count()
    complaints = Complaint.query.all()
    total_complaints = len(complaints)
    pending_complaints = len([c for c in complaints if c.status == 'Pending'])
    resolved_complaints = len([c for c in complaints if c.status == 'Resolved'])

    recent_feedbacks = Feedback.query.order_by(Feedback.created_at.desc()).limit(5).all()
    recent_complaints = Complaint.query.order_by(Complaint.created_at.desc()).limit(5).all()

    return render_template(
        'admin_dashboard.html',
        total_students=total_students,
        total_feedback=total_feedback,
        total_complaints=total_complaints,
        pending_complaints=pending_complaints,
        resolved_complaints=resolved_complaints,
        recent_feedbacks=recent_feedbacks,
        recent_complaints=recent_complaints
    )

# Admin Manage Feedback
@app.route('/admin/feedback')
@admin_required
def manage_feedback():
    feedbacks = Feedback.query.order_by(Feedback.created_at.desc()).all()
    return render_template('manage_feedback.html', feedbacks=feedbacks)

# Admin Delete Feedback
@app.route('/admin/feedback/delete/<int:feedback_id>', methods=['POST'])
@admin_required
def delete_feedback(feedback_id):
    feedback = Feedback.query.get_or_404(feedback_id)
    db.session.delete(feedback)
    db.session.commit()
    flash('Feedback record deleted successfully.', 'info')
    return redirect(url_for('manage_feedback'))

# Admin Manage Complaints
@app.route('/admin/complaints')
@admin_required
def manage_complaints():
    status_filter = request.args.get('status', '').strip()
    search_query = request.args.get('q', '').strip()

    query = Complaint.query.join(Student)

    if status_filter and status_filter in ['Pending', 'In Progress', 'Resolved', 'Rejected']:
        query = query.filter(Complaint.status == status_filter)

    if search_query:
        search_pattern = f"%{search_query}%"
        query = query.filter(
            (Complaint.complaint_id.ilike(search_pattern)) |
            (Complaint.complaint_type.ilike(search_pattern)) |
            (Complaint.description.ilike(search_pattern)) |
            (Student.name.ilike(search_pattern)) |
            (Student.register_number.ilike(search_pattern))
        )

    complaints = query.order_by(Complaint.created_at.desc()).all()
    return render_template(
        'manage_complaints.html',
        complaints=complaints,
        status_filter=status_filter,
        search_query=search_query
    )

# Admin Update Complaint Status & Remarks
@app.route('/admin/complaints/update/<int:complaint_id>', methods=['POST'])
@admin_required
def update_complaint_status(complaint_id):
    complaint = Complaint.query.get_or_404(complaint_id)
    new_status = request.form.get('status', '').strip()
    admin_remarks = request.form.get('admin_remarks', '').strip()

    valid_statuses = ['Pending', 'In Progress', 'Resolved', 'Rejected']
    if new_status in valid_statuses:
        complaint.status = new_status

    complaint.admin_remarks = admin_remarks
    db.session.commit()

    flash(f'Complaint #{complaint.complaint_id} updated successfully to "{complaint.status}".', 'success')
    return redirect(url_for('manage_complaints'))

# Admin Delete Complaint
@app.route('/admin/complaints/delete/<int:complaint_id>', methods=['POST'])
@admin_required
def delete_complaint(complaint_id):
    complaint = Complaint.query.get_or_404(complaint_id)
    db.session.delete(complaint)
    db.session.commit()
    flash(f'Complaint #{complaint.complaint_id} deleted successfully.', 'info')
    return redirect(url_for('manage_complaints'))

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
        seed_default_admin()
    app.run(debug=True)
