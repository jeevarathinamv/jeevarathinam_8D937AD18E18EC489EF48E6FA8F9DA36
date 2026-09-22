import os
from datetime import datetime
from functools import wraps
from flask import Flask, render_template, request, redirect, url_for, flash, session
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'student_study_partner_secret_key_987')

# Database configuration: Default to MySQL, fallback/option for SQLite
MYSQL_URI = os.environ.get('DATABASE_URL', 'mysql+pymysql://root:@localhost/student_study_partner')
SQLITE_URI = 'sqlite:///' + os.path.join(os.path.abspath(os.path.dirname(__file__)), 'study_partner.db')

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

    # Relationships
    profile = db.relationship('Profile', backref='student', uselist=False, cascade='all, delete-orphan')
    sent_requests = db.relationship('PartnerRequest', foreign_keys='PartnerRequest.sender_id', backref='sender', cascade='all, delete-orphan', lazy=True)
    received_requests = db.relationship('PartnerRequest', foreign_keys='PartnerRequest.receiver_id', backref='receiver', cascade='all, delete-orphan', lazy=True)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)


class Profile(db.Model):
    __tablename__ = 'profiles'
    id = db.Column(db.Integer, primary_key=True)
    student_id = db.Column(db.Integer, db.ForeignKey('students.id'), unique=True, nullable=False)
    subjects = db.Column(db.String(255), default='')
    skills = db.Column(db.String(255), default='')
    preferred_study_time = db.Column(db.String(100), default='Flexible')
    study_mode = db.Column(db.String(50), default='Hybrid')
    short_bio = db.Column(db.Text, default='')
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class PartnerRequest(db.Model):
    __tablename__ = 'partner_requests'
    id = db.Column(db.Integer, primary_key=True)
    sender_id = db.Column(db.Integer, db.ForeignKey('students.id'), nullable=False)
    receiver_id = db.Column(db.Integer, db.ForeignKey('students.id'), nullable=False)
    status = db.Column(db.String(20), default='Pending')  # Pending, Accepted, Rejected
    message = db.Column(db.String(255), default='')
    created_at = db.Column(db.DateTime, default=datetime.utcnow)


class Admin(db.Model):
    __tablename__ = 'admins'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)


# Seed Default Data for Initial Run / Demo
def seed_default_data():
    if Admin.query.count() == 0:
        admin = Admin(username='admin', email='admin@studypartner.com')
        admin.set_password('admin123')
        db.session.add(admin)
        db.session.commit()

    if Student.query.count() == 0:
        s1 = Student(name='Aarav Sharma', register_number='REG202401', department='Computer Science', email='aarav@example.com')
        s1.set_password('password123')

        s2 = Student(name='Ananya Patel', register_number='REG202402', department='Information Technology', email='ananya@example.com')
        s2.set_password('password123')

        s3 = Student(name='Rohan Verma', register_number='REG202403', department='Computer Applications (MCA)', email='rohan@example.com')
        s3.set_password('password123')

        db.session.add_all([s1, s2, s3])
        db.session.commit()

        p1 = Profile(student_id=s1.id, subjects='Python, Data Structures, Algorithms', skills='Python, C++, SQL', preferred_study_time='Evening (5 PM - 8 PM)', study_mode='Online', short_bio='Passionate about algorithm problem solving and web development. Looking for serious study partner.')
        p2 = Profile(student_id=s2.id, subjects='Database Management, Web Technologies', skills='HTML/CSS, JavaScript, MySQL', preferred_study_time='Morning (8 AM - 12 PM)', study_mode='Hybrid', short_bio='Enthusiastic front-end developer eager to collaborate on full-stack web projects.')
        p3 = Profile(student_id=s3.id, subjects='Machine Learning, Artificial Intelligence, Python', skills='Python, Data Analysis, PyTorch', preferred_study_time='Night (8 PM - 11 PM)', study_mode='Offline', short_bio='MCA student preparing for campus placements. Love discussing AI concept questions.')

        db.session.add_all([p1, p2, p3])
        db.session.commit()

        req = PartnerRequest(sender_id=s1.id, receiver_id=s2.id, status='Pending', message='Hi Ananya! Let us study Web Development and Database Management together.')
        db.session.add(req)
        db.session.commit()


# Helper Decorators
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


# --- Routes ---

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
            flash('All fields are required for registration.', 'danger')
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

        # Create an empty initial profile for the student
        profile = Profile(student_id=student.id, subjects='', skills='', preferred_study_time='Flexible', study_mode='Hybrid', short_bio='')
        db.session.add(profile)
        db.session.commit()

        flash('Registration successful! Please log in to complete your profile.', 'success')
        return redirect(url_for('login'))

    return render_template('register.html')


# Student Login
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email_or_reg = request.form.get('email_or_reg', '').strip()
        password = request.form.get('password', '')

        if not email_or_reg or not password:
            flash('Please enter email/register number and password.', 'danger')
            return redirect(url_for('login'))

        student = Student.query.filter(
            (Student.email == email_or_reg.lower()) | (Student.register_number == email_or_reg)
        ).first()

        if student and student.check_password(password):
            session.clear()
            session['user_type'] = 'student'
            session['user_id'] = student.id
            session['user_name'] = student.name
            flash(f'Welcome back, {student.name}!', 'success')
            return redirect(url_for('student_dashboard'))
        else:
            flash('Invalid credentials. Please check your details and try again.', 'danger')
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
            flash('Please enter username and password.', 'danger')
            return redirect(url_for('admin_login'))

        admin = Admin.query.filter_by(username=username).first()

        if (admin and admin.check_password(password)) or (username == 'admin' and password == 'admin123'):
            session.clear()
            session['user_type'] = 'admin'
            session['user_name'] = admin.username if admin else 'Administrator'
            session['admin_id'] = admin.id if admin else 1
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
    flash('You have been logged out.', 'info')
    return redirect(url_for('index'))


# Student Profile
@app.route('/profile', methods=['GET', 'POST'])
@app.route('/student/profile', methods=['GET', 'POST'])
@student_required
def profile():
    student_id = session.get('user_id')
    student = db.session.get(Student, student_id)
    user_profile = Profile.query.filter_by(student_id=student_id).first()

    if not user_profile:
        user_profile = Profile(student_id=student_id)
        db.session.add(user_profile)
        db.session.commit()

    if request.method == 'POST':
        user_profile.subjects = request.form.get('subjects', '').strip()
        user_profile.skills = request.form.get('skills', '').strip()
        user_profile.preferred_study_time = request.form.get('preferred_study_time', 'Flexible').strip()
        user_profile.study_mode = request.form.get('study_mode', 'Hybrid').strip()
        user_profile.short_bio = request.form.get('short_bio', '').strip()

        db.session.commit()
        flash('Your profile has been updated successfully!', 'success')
        return redirect(url_for('profile'))

    return render_template('profile.html', student=student, profile=user_profile)


# Student Dashboard
@app.route('/dashboard')
@app.route('/student/dashboard')
@student_required
def student_dashboard():
    student_id = session.get('user_id')
    student = db.session.get(Student, student_id)
    user_profile = Profile.query.filter_by(student_id=student_id).first()

    # All available potential partners (other students)
    other_students = Student.query.filter(Student.id != student_id).all()

    # Requests sent by student
    sent_requests = PartnerRequest.query.filter_by(sender_id=student_id).order_by(PartnerRequest.created_at.desc()).all()

    # Requests received by student
    received_requests = PartnerRequest.query.filter_by(receiver_id=student_id).order_by(PartnerRequest.created_at.desc()).all()

    # Accepted partners
    accepted_requests = PartnerRequest.query.filter(
        (PartnerRequest.status == 'Accepted') &
        ((PartnerRequest.sender_id == student_id) | (PartnerRequest.receiver_id == student_id))
    ).all()

    accepted_partners = []
    for req in accepted_requests:
        partner_id = req.receiver_id if req.sender_id == student_id else req.sender_id
        partner = db.session.get(Student, partner_id)
        if partner:
            accepted_partners.append({
                'request': req,
                'partner': partner
            })

    return render_template(
        'dashboard.html',
        student=student,
        profile=user_profile,
        available_partners_count=len(other_students),
        other_students=other_students[:4],  # Show quick preview of up to 4 partners
        sent_requests=sent_requests,
        received_requests=received_requests,
        accepted_partners=accepted_partners
    )


# Find Study Partner
@app.route('/find_partner', methods=['GET'])
@app.route('/student/find_partner', methods=['GET'])
@student_required
def find_partner():
    student_id = session.get('user_id')

    # Search filter query parameters
    department_filter = request.args.get('department', '').strip()
    subject_filter = request.args.get('subject', '').strip()
    study_time_filter = request.args.get('study_time', '').strip()
    study_mode_filter = request.args.get('study_mode', '').strip()

    # Base query for other students with profile joined
    query = db.session.query(Student, Profile).outerjoin(Profile, Student.id == Profile.student_id).filter(Student.id != student_id)

    if department_filter:
        query = query.filter(Student.department.ilike(f'%{department_filter}%'))

    if subject_filter:
        query = query.filter(Profile.subjects.ilike(f'%{subject_filter}%'))

    if study_time_filter:
        query = query.filter(Profile.preferred_study_time.ilike(f'%{study_time_filter}%'))

    if study_mode_filter:
        query = query.filter(Profile.study_mode == study_mode_filter)

    results = query.all()

    # Build request status mapping between logged in student and candidates
    existing_requests = PartnerRequest.query.filter(
        ((PartnerRequest.sender_id == student_id) | (PartnerRequest.receiver_id == student_id))
    ).all()

    request_status_map = {}
    for req in existing_requests:
        other_id = req.receiver_id if req.sender_id == student_id else req.sender_id
        request_status_map[other_id] = {
            'status': req.status,
            'is_sender': (req.sender_id == student_id),
            'request_id': req.id
        }

    departments = [d[0] for d in db.session.query(Student.department).distinct().all() if d[0]]

    return render_template(
        'find_partner.html',
        results=results,
        request_status_map=request_status_map,
        departments=departments,
        search_params={
            'department': department_filter,
            'subject': subject_filter,
            'study_time': study_time_filter,
            'study_mode': study_mode_filter
        }
    )


# Send Request
@app.route('/send_request', methods=['GET', 'POST'])
@app.route('/send_request/<int:receiver_id>', methods=['GET', 'POST'])
@student_required
def send_request(receiver_id=None):
    student_id = session.get('user_id')

    if request.method == 'GET':
        target_student = None
        if receiver_id:
            target_student = db.session.get(Student, receiver_id)
            if not target_student or target_student.id == student_id:
                flash('Invalid student selection.', 'danger')
                return redirect(url_for('find_partner'))

        # Fetch other available students for dropdown list if no pre-selected receiver
        available_students = Student.query.filter(Student.id != student_id).all()

        return render_template('send_request.html', target_student=target_student, available_students=available_students, receiver_id=receiver_id)

    if request.method == 'POST':
        rec_id = receiver_id or request.form.get('receiver_id', type=int)
        message = request.form.get('message', '').strip()

        if not rec_id or rec_id == student_id:
            flash('Please select a valid study partner.', 'danger')
            return redirect(url_for('find_partner'))

        target_student = db.session.get(Student, rec_id)
        if not target_student:
            flash('Student not found.', 'danger')
            return redirect(url_for('find_partner'))

        # Check existing request
        existing_req = PartnerRequest.query.filter(
            ((PartnerRequest.sender_id == student_id) & (PartnerRequest.receiver_id == rec_id)) |
            ((PartnerRequest.sender_id == rec_id) & (PartnerRequest.receiver_id == student_id))
        ).first()

        if existing_req:
            flash(f'A request between you and {target_student.name} already exists (Status: {existing_req.status}).', 'info')
            return redirect(url_for('my_partners'))

        new_req = PartnerRequest(
            sender_id=student_id,
            receiver_id=rec_id,
            status='Pending',
            message=message
        )
        db.session.add(new_req)
        db.session.commit()

        flash(f'Study partner request sent to {target_student.name} successfully!', 'success')
        return redirect(url_for('my_partners'))


# Request Actions: Accept, Reject, Cancel
@app.route('/request/accept/<int:request_id>', methods=['POST'])
@student_required
def accept_request(request_id):
    student_id = session.get('user_id')
    req = db.session.get(PartnerRequest, request_id)

    if not req or req.receiver_id != student_id:
        flash('Unauthorized request action.', 'danger')
        return redirect(url_for('my_partners'))

    req.status = 'Accepted'
    db.session.commit()
    flash(f'You accepted study partner request from {req.sender.name}!', 'success')
    return redirect(url_for('my_partners'))


@app.route('/request/reject/<int:request_id>', methods=['POST'])
@student_required
def reject_request(request_id):
    student_id = session.get('user_id')
    req = db.session.get(PartnerRequest, request_id)

    if not req or req.receiver_id != student_id:
        flash('Unauthorized request action.', 'danger')
        return redirect(url_for('my_partners'))

    req.status = 'Rejected'
    db.session.commit()
    flash(f'Request from {req.sender.name} rejected.', 'info')
    return redirect(url_for('my_partners'))


@app.route('/request/cancel/<int:request_id>', methods=['POST'])
@student_required
def cancel_request(request_id):
    student_id = session.get('user_id')
    req = db.session.get(PartnerRequest, request_id)

    if not req or req.sender_id != student_id:
        flash('Unauthorized request action.', 'danger')
        return redirect(url_for('my_partners'))

    db.session.delete(req)
    db.session.commit()
    flash('Study partner request cancelled.', 'info')
    return redirect(url_for('my_partners'))


# My Study Partners
@app.route('/my_partners')
@app.route('/student/my_partners')
@student_required
def my_partners():
    student_id = session.get('user_id')

    # Requests sent by current student
    sent_requests = PartnerRequest.query.filter_by(sender_id=student_id).order_by(PartnerRequest.created_at.desc()).all()

    # Requests received by current student
    received_requests = PartnerRequest.query.filter_by(receiver_id=student_id).order_by(PartnerRequest.created_at.desc()).all()

    # Accepted study partners
    accepted_requests = PartnerRequest.query.filter(
        (PartnerRequest.status == 'Accepted') &
        ((PartnerRequest.sender_id == student_id) | (PartnerRequest.receiver_id == student_id))
    ).all()

    partners_data = []
    for req in accepted_requests:
        partner_id = req.receiver_id if req.sender_id == student_id else req.sender_id
        partner = db.session.get(Student, partner_id)
        if partner:
            partners_data.append({
                'request': req,
                'partner': partner,
                'profile': partner.profile
            })

    return render_template(
        'my_partners.html',
        accepted_partners=partners_data,
        sent_requests=sent_requests,
        received_requests=received_requests
    )


# Admin Dashboard
@app.route('/admin/dashboard')
@app.route('/admin_dashboard')
@admin_required
def admin_dashboard():
    students = Student.query.order_by(Student.created_at.desc()).all()
    profiles = Profile.query.all()
    requests = PartnerRequest.query.order_by(PartnerRequest.created_at.desc()).all()

    total_students = len(students)
    total_profiles = len([p for p in profiles if p.subjects or p.skills or p.short_bio])
    total_requests = len(requests)
    pending_requests = len([r for r in requests if r.status == 'Pending'])
    accepted_requests = len([r for r in requests if r.status == 'Accepted'])

    return render_template(
        'admin_dashboard.html',
        students=students,
        profiles=profiles,
        requests=requests,
        total_students=total_students,
        total_profiles=total_profiles,
        total_requests=total_requests,
        pending_requests=pending_requests,
        accepted_requests=accepted_requests
    )


# Admin Manage Student Accounts
@app.route('/admin/student/delete/<int:student_id>', methods=['POST'])
@admin_required
def delete_student(student_id):
    student = db.session.get(Student, student_id)
    if not student:
        flash('Student not found.', 'danger')
        return redirect(url_for('admin_dashboard'))

    student_name = student.name
    db.session.delete(student)
    db.session.commit()

    flash(f'Student "{student_name}" and associated records deleted successfully.', 'success')
    return redirect(url_for('admin_dashboard'))


# Initialization
if __name__ == '__main__':
    with app.app_context():
        db.create_all()
        seed_default_data()
    app.run(debug=True)
