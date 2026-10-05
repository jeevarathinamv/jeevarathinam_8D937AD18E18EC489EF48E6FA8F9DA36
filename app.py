import os
import random
from datetime import datetime, date, timezone
from functools import wraps
from flask import Flask, render_template, request, redirect, url_for, flash, session
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'library_book_request_secret_key_98765')

# Admin Credentials
ADMIN_USERNAME = os.environ.get('ADMIN_USERNAME', 'admin')
ADMIN_PASSWORD = os.environ.get('ADMIN_PASSWORD', 'admin123')

# Database configuration: Default to MySQL URI, fallback/option for SQLite
MYSQL_URI = os.environ.get('DATABASE_URL', 'mysql+pymysql://root:@localhost/library_db')
SQLITE_URI = 'sqlite:///' + os.path.join(os.path.abspath(os.path.dirname(__file__)), 'library.db')

use_sqlite = os.environ.get('USE_SQLITE') == '1'
app.config['SQLALCHEMY_DATABASE_URI'] = SQLITE_URI if use_sqlite else MYSQL_URI
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

# Book Categories
BOOK_CATEGORIES = [
    'Programming',
    'Database',
    'Web Development',
    'Computer Science',
    'Management',
    'General',
    'Other'
]

# Database Models
class Admin(db.Model):
    __tablename__ = 'admins'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))

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
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))

    requests = db.relationship('BookRequest', backref='student', lazy=True, cascade="all, delete-orphan")

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)


class BookRequest(db.Model):
    __tablename__ = 'book_requests'
    id = db.Column(db.Integer, primary_key=True)
    request_id = db.Column(db.String(20), unique=True, nullable=False)
    student_id = db.Column(db.Integer, db.ForeignKey('students.id'), nullable=False)
    book_name = db.Column(db.String(200), nullable=False)
    author_name = db.Column(db.String(150), nullable=False)
    category = db.Column(db.String(50), nullable=False)
    reason = db.Column(db.Text, nullable=False)
    request_date = db.Column(db.Date, nullable=False, default=date.today)
    status = db.Column(db.String(20), nullable=False, default='Pending') # Pending, Approved, Rejected
    admin_remarks = db.Column(db.Text, nullable=True, default='')
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))


def generate_unique_request_id():
    """Generates a unique Request ID formatted as REQ-XXXXXX."""
    while True:
        req_id = f"REQ-{random.randint(100000, 999999)}"
        if not BookRequest.query.filter_by(request_id=req_id).first():
            return req_id


def seed_default_admin():
    """Seeds a default admin user if none exists."""
    if Admin.query.count() == 0:
        default_admin = Admin(username=ADMIN_USERNAME)
        default_admin.set_password(ADMIN_PASSWORD)
        db.session.add(default_admin)
        db.session.commit()


# Decorators
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


# Public Routes
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


# Student Login
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email_or_reg = request.form.get('email_or_reg', '').strip()
        password = request.form.get('password', '')

        if not email_or_reg or not password:
            flash('Please fill in all fields.', 'danger')
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
            flash('Invalid Email/Register Number or Password.', 'danger')
            return redirect(url_for('login'))

    return render_template('login.html')


# Admin Login
@app.route('/admin/login', methods=['GET', 'POST'])
@app.route('/admin_login', methods=['GET', 'POST'])
def admin_login():
    if request.method == 'POST':
        username = request.form.get('username', '').strip()
        password = request.form.get('password', '')

        if not username or not password:
            flash('Please fill in all fields.', 'danger')
            return redirect(url_for('admin_login'))

        admin = Admin.query.filter_by(username=username).first()

        # Fallback to config admin if DB admin not seeded or matching env
        if (admin and admin.check_password(password)) or (username == ADMIN_USERNAME and password == ADMIN_PASSWORD):
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
    return redirect(url_for('index'))


# Student Dashboard
@app.route('/student/dashboard')
@student_required
def student_dashboard():
    student_id = session.get('user_id')
    student = db.session.get(Student, student_id)
    requests = BookRequest.query.filter_by(student_id=student_id).order_by(BookRequest.created_at.desc()).all()

    total_requests = len(requests)
    pending_requests = len([r for r in requests if r.status == 'Pending'])
    approved_requests = len([r for r in requests if r.status == 'Approved'])
    rejected_requests = len([r for r in requests if r.status == 'Rejected'])

    recent_requests = requests[:5]

    return render_template(
        'student_dashboard.html',
        student=student,
        total_requests=total_requests,
        pending_requests=pending_requests,
        approved_requests=approved_requests,
        rejected_requests=rejected_requests,
        recent_requests=recent_requests
    )


# Request New Book
@app.route('/request_book', methods=['GET', 'POST'])
@student_required
def request_book():
    if request.method == 'POST':
        book_name = request.form.get('book_name', '').strip()
        author_name = request.form.get('author_name', '').strip()
        category = request.form.get('category', '').strip()
        reason = request.form.get('reason', '').strip()

        if not book_name or not author_name or not category or not reason:
            flash('All fields are required to submit a book request.', 'danger')
            return redirect(url_for('request_book'))

        if category not in BOOK_CATEGORIES:
            flash('Please select a valid category.', 'danger')
            return redirect(url_for('request_book'))

        request_id = generate_unique_request_id()
        new_request = BookRequest(
            request_id=request_id,
            student_id=session.get('user_id'),
            book_name=book_name,
            author_name=author_name,
            category=category,
            reason=reason,
            request_date=date.today(),
            status='Pending'
        )
        db.session.add(new_request)
        db.session.commit()

        flash(f'Book request submitted successfully! Your Request ID is {request_id}.', 'success')
        return redirect(url_for('my_requests'))

    return render_template('request_book.html', categories=BOOK_CATEGORIES)


# My Book Requests
@app.route('/my_requests')
@student_required
def my_requests():
    student_id = session.get('user_id')
    requests = BookRequest.query.filter_by(student_id=student_id).order_by(BookRequest.created_at.desc()).all()
    return render_template('my_requests.html', requests=requests)


# Request Details
@app.route('/request_details/<int:id>')
@app.route('/request/<int:id>')
def request_details(id):
    req = db.session.get(BookRequest, id)
    if not req:
        flash('Book request not found.', 'danger')
        return redirect(url_for('index'))

    user_type = session.get('user_type')
    user_id = session.get('user_id')

    # Security check: Students can only view their own requests
    if user_type == 'student' and req.student_id != user_id:
        flash('Access denied. You can only view your own book requests.', 'danger')
        return redirect(url_for('my_requests'))

    if not user_type:
        flash('Please log in to view request details.', 'warning')
        return redirect(url_for('login'))

    return render_template('request_details.html', req=req)


# Admin Dashboard
@app.route('/admin/dashboard')
@admin_required
def admin_dashboard():
    total_students = Student.query.count()
    all_requests = BookRequest.query.order_by(BookRequest.created_at.desc()).all()

    total_requests = len(all_requests)
    pending_requests = len([r for r in all_requests if r.status == 'Pending'])
    approved_requests = len([r for r in all_requests if r.status == 'Approved'])
    rejected_requests = len([r for r in all_requests if r.status == 'Rejected'])

    recent_requests = all_requests[:5]

    return render_template(
        'admin_dashboard.html',
        total_students=total_students,
        total_requests=total_requests,
        pending_requests=pending_requests,
        approved_requests=approved_requests,
        rejected_requests=rejected_requests,
        recent_requests=recent_requests
    )


# Admin Manage Requests
@app.route('/admin/manage_requests', methods=['GET'])
@admin_required
def manage_requests():
    status_filter = request.args.get('status', 'All').strip()
    search_query = request.args.get('search', '').strip()

    query = BookRequest.query.join(Student)

    if status_filter in ['Pending', 'Approved', 'Rejected']:
        query = query.filter(BookRequest.status == status_filter)

    if search_query:
        search_pattern = f"%{search_query}%"
        query = query.filter(
            (BookRequest.request_id.like(search_pattern)) |
            (BookRequest.book_name.like(search_pattern)) |
            (BookRequest.author_name.like(search_pattern)) |
            (Student.name.like(search_pattern)) |
            (Student.register_number.like(search_pattern))
        )

    requests = query.order_by(BookRequest.created_at.desc()).all()

    return render_template(
        'manage_requests.html',
        requests=requests,
        status_filter=status_filter,
        search_query=search_query
    )


# Update Request Status (Approve / Reject & Remarks)
@app.route('/admin/request/update/<int:id>', methods=['POST'])
@admin_required
def update_request_status(id):
    req = db.session.get(BookRequest, id)
    if not req:
        flash('Book request not found.', 'danger')
        return redirect(url_for('manage_requests'))

    action = request.form.get('action', '').strip()
    admin_remarks = request.form.get('admin_remarks', '').strip()

    if action not in ['Approved', 'Rejected']:
        flash('Invalid status update action.', 'danger')
        return redirect(url_for('manage_requests'))

    req.status = action
    req.admin_remarks = admin_remarks
    db.session.commit()

    flash(f'Request #{req.request_id} has been marked as {action}.', 'success')
    return redirect(url_for('manage_requests'))


# Delete Request
@app.route('/admin/request/delete/<int:id>', methods=['POST'])
@admin_required
def delete_request(id):
    req = db.session.get(BookRequest, id)
    if not req:
        flash('Book request not found.', 'danger')
        return redirect(url_for('manage_requests'))

    req_id = req.request_id
    db.session.delete(req)
    db.session.commit()

    flash(f'Book request #{req_id} deleted successfully.', 'info')
    return redirect(url_for('manage_requests'))


if __name__ == '__main__':
    with app.app_context():
        db.create_all()
        seed_default_admin()
    app.run(debug=True)
