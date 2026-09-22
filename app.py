import os
from datetime import datetime
from functools import wraps
from flask import Flask, render_template, request, redirect, url_for, flash, session
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'college_grievance_secret_key_98765')

# Admin Credentials fallback / defaults
DEFAULT_ADMIN_USERNAME = os.environ.get('ADMIN_USERNAME', 'admin')
DEFAULT_ADMIN_PASSWORD = os.environ.get('ADMIN_PASSWORD', 'admin123')

# Database configuration: Default to MySQL URI, fallback/option for SQLite
MYSQL_URI = os.environ.get('DATABASE_URL', 'mysql+pymysql://root:@localhost/college_grievance')
SQLITE_URI = 'sqlite:///' + os.path.join(os.path.abspath(os.path.dirname(__file__)), 'college_grievance.db')

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

    grievances = db.relationship('Grievance', backref='student', lazy=True, cascade='all, delete-orphan')

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

class Admin(db.Model):
    __tablename__ = 'admins'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    email = db.Column(db.String(120), nullable=False, default='admin@college.edu')
    name = db.Column(db.String(100), nullable=False, default='System Administrator')
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

class Grievance(db.Model):
    __tablename__ = 'grievances'
    id = db.Column(db.Integer, primary_key=True)
    student_id = db.Column(db.Integer, db.ForeignKey('students.id'), nullable=False)
    category = db.Column(db.String(50), nullable=False) # Academic, Fees, Hostel, Transport, Lab, Other
    subject = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text, nullable=False)
    status = db.Column(db.String(20), default='Pending') # Pending, In Progress, Resolved, Rejected
    admin_reply = db.Column(db.Text, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

def seed_default_data():
    if Admin.query.count() == 0:
        default_admin = Admin(
            username=DEFAULT_ADMIN_USERNAME,
            email='admin@college.edu',
            name='System Administrator'
        )
        default_admin.set_password(DEFAULT_ADMIN_PASSWORD)
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

        flash('Registration successful! Please log in with your credentials.', 'success')
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
            session['register_number'] = student.register_number
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

        admin = Admin.query.filter_by(username=username).first()

        if admin and admin.check_password(password):
            session['user_type'] = 'admin'
            session['user_id'] = admin.id
            session['user_name'] = admin.name
            flash('Logged in successfully as Administrator.', 'success')
            return redirect(url_for('admin_dashboard'))
        elif username == DEFAULT_ADMIN_USERNAME and password == DEFAULT_ADMIN_PASSWORD:
            session['user_type'] = 'admin'
            session['user_id'] = 0
            session['user_name'] = 'Administrator'
            flash('Logged in successfully as Administrator.', 'success')
            return redirect(url_for('admin_dashboard'))
        else:
            flash('Invalid administrator credentials.', 'danger')
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
    student = Student.query.get_or_404(student_id)
    grievances = Grievance.query.filter_by(student_id=student_id).order_by(Grievance.created_at.desc()).all()

    total_grievances = len(grievances)
    pending_grievances = len([g for g in grievances if g.status == 'Pending'])
    in_progress_grievances = len([g for g in grievances if g.status == 'In Progress'])
    resolved_grievances = len([g for g in grievances if g.status == 'Resolved'])

    recent_grievances = grievances[:5]

    return render_template(
        'student_dashboard.html',
        student=student,
        grievances=recent_grievances,
        total_grievances=total_grievances,
        pending_grievances=pending_grievances,
        in_progress_grievances=in_progress_grievances,
        resolved_grievances=resolved_grievances
    )

# Submit Grievance
@app.route('/student/submit-grievance', methods=['GET', 'POST'])
@student_required
def submit_grievance():
    if request.method == 'POST':
        category = request.form.get('category', '').strip()
        subject = request.form.get('subject', '').strip()
        description = request.form.get('description', '').strip()

        categories = ['Academic', 'Fees', 'Hostel', 'Transport', 'Lab', 'Other']
        if not category or category not in categories or not subject or not description:
            flash('Please complete all required fields with valid input.', 'danger')
            return redirect(url_for('submit_grievance'))

        student_id = session.get('user_id')
        grievance = Grievance(
            student_id=student_id,
            category=category,
            subject=subject,
            description=description,
            status='Pending'
        )
        db.session.add(grievance)
        db.session.commit()

        flash(f'Grievance #{grievance.id} submitted successfully! You can track its status here.', 'success')
        return redirect(url_for('grievance_history'))

    return render_template('submit_grievance.html')

# Grievance History
@app.route('/student/grievance-history')
@student_required
def grievance_history():
    student_id = session.get('user_id')
    grievances = Grievance.query.filter_by(student_id=student_id).order_by(Grievance.created_at.desc()).all()
    return render_template('grievance_history.html', grievances=grievances)

# Grievance Details / Tracking for Student
@app.route('/student/grievance/<int:grievance_id>')
@student_required
def grievance_details(grievance_id):
    student_id = session.get('user_id')
    grievance = Grievance.query.filter_by(id=grievance_id, student_id=student_id).first_or_404()
    return render_template('grievance_details.html', grievance=grievance)

# Admin Dashboard
@app.route('/admin/dashboard')
@admin_required
def admin_dashboard():
    status_filter = request.args.get('status', '').strip()
    category_filter = request.args.get('category', '').strip()
    search_query = request.args.get('search', '').strip()

    query = Grievance.query.join(Student)

    if status_filter:
        query = query.filter(Grievance.status == status_filter)
    if category_filter:
        query = query.filter(Grievance.category == category_filter)
    if search_query:
        search_pattern = f"%{search_query}%"
        query = query.filter(
            (Student.name.ilike(search_pattern)) |
            (Student.register_number.ilike(search_pattern)) |
            (Grievance.subject.ilike(search_pattern))
        )

    grievances = query.order_by(Grievance.created_at.desc()).all()
    all_grievances = Grievance.query.all()

    total_count = len(all_grievances)
    pending_count = len([g for g in all_grievances if g.status == 'Pending'])
    in_progress_count = len([g for g in all_grievances if g.status == 'In Progress'])
    resolved_count = len([g for g in all_grievances if g.status == 'Resolved'])
    rejected_count = len([g for g in all_grievances if g.status == 'Rejected'])

    return render_template(
        'admin_dashboard.html',
        grievances=grievances,
        total_count=total_count,
        pending_count=pending_count,
        in_progress_count=in_progress_count,
        resolved_count=resolved_count,
        rejected_count=rejected_count,
        status_filter=status_filter,
        category_filter=category_filter,
        search_query=search_query
    )

# Admin Grievance Details
@app.route('/admin/grievance/<int:grievance_id>')
@admin_required
def admin_grievance_details(grievance_id):
    grievance = Grievance.query.get_or_404(grievance_id)
    return render_template('admin_grievance_details.html', grievance=grievance)

# Admin Reply & Status Update
@app.route('/admin/grievance/reply/<int:grievance_id>', methods=['POST'])
@admin_required
def admin_reply_grievance(grievance_id):
    grievance = Grievance.query.get_or_404(grievance_id)
    status = request.form.get('status', '').strip()
    admin_reply = request.form.get('admin_reply', '').strip()

    valid_statuses = ['Pending', 'In Progress', 'Resolved', 'Rejected']
    if status in valid_statuses:
        grievance.status = status
    if admin_reply:
        grievance.admin_reply = admin_reply

    grievance.updated_at = datetime.utcnow()
    db.session.commit()

    flash(f'Grievance #{grievance.id} updated successfully.', 'success')
    return redirect(url_for('admin_grievance_details', grievance_id=grievance.id))

# Admin Delete Grievance
@app.route('/admin/grievance/delete/<int:grievance_id>', methods=['POST'])
@admin_required
def admin_delete_grievance(grievance_id):
    grievance = Grievance.query.get_or_404(grievance_id)
    db.session.delete(grievance)
    db.session.commit()

    flash(f'Grievance #{grievance_id} deleted successfully.', 'info')
    return redirect(url_for('admin_dashboard'))

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
        seed_default_data()
    app.run(debug=True)
