import os
from datetime import datetime, timezone
from functools import wraps
from flask import Flask, render_template, request, redirect, url_for, flash, session
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'alumni_mentorship_portal_secret_key_2025')

# Database configuration: Default to MySQL URI, fallback/option for SQLite
MYSQL_URI = os.environ.get('DATABASE_URL', 'mysql+pymysql://root:@localhost/alumni_mentorship')
SQLITE_URI = 'sqlite:///' + os.path.join(os.path.abspath(os.path.dirname(__file__)), 'alumni_mentorship.db')

use_sqlite = os.environ.get('USE_SQLITE') == '1'
app.config['SQLALCHEMY_DATABASE_URI'] = SQLITE_URI if use_sqlite else MYSQL_URI
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

def utc_now():
    return datetime.now(timezone.utc)

# Database Models
class Student(db.Model):
    __tablename__ = 'students'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    register_number = db.Column(db.String(50), unique=True, nullable=False)
    department = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    created_at = db.Column(db.DateTime, default=utc_now)

    requests = db.relationship('MentorshipRequest', backref='student', cascade='all, delete-orphan', lazy=True)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)


class Alumni(db.Model):
    __tablename__ = 'alumni'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    department = db.Column(db.String(100), nullable=False)
    graduation_year = db.Column(db.Integer, nullable=False)
    job_role = db.Column(db.String(100), nullable=False)
    company = db.Column(db.String(100), nullable=False)
    experience = db.Column(db.String(50), nullable=False, default='2+ Years')
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    created_at = db.Column(db.DateTime, default=utc_now)

    requests = db.relationship('MentorshipRequest', backref='alumni', cascade='all, delete-orphan', lazy=True)
    guidance_posts = db.relationship('CareerGuidance', backref='alumni', cascade='all, delete-orphan', lazy=True)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)


class MentorshipRequest(db.Model):
    __tablename__ = 'mentorship_requests'
    id = db.Column(db.Integer, primary_key=True)
    student_id = db.Column(db.Integer, db.ForeignKey('students.id'), nullable=False)
    alumni_id = db.Column(db.Integer, db.ForeignKey('alumni.id'), nullable=False)
    question = db.Column(db.Text, nullable=False)
    response = db.Column(db.Text, nullable=True)
    status = db.Column(db.String(20), default='Pending') # Pending, Accepted, Rejected
    created_at = db.Column(db.DateTime, default=utc_now)


class CareerGuidance(db.Model):
    __tablename__ = 'career_guidance'
    id = db.Column(db.Integer, primary_key=True)
    alumni_id = db.Column(db.Integer, db.ForeignKey('alumni.id'), nullable=False)
    title = db.Column(db.String(200), nullable=False)
    category = db.Column(db.String(50), nullable=False) # Career Advice, Interview Tips, Resume Tips, Skill Suggestions
    content = db.Column(db.Text, nullable=False)
    created_at = db.Column(db.DateTime, default=utc_now)


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


# Seed default data function
def seed_default_data():
    if db.session.query(Admin).count() == 0:
        admin = Admin(username='admin')
        admin.set_password('admin123')
        db.session.add(admin)
        db.session.commit()

    if db.session.query(Alumni).count() == 0:
        a1 = Alumni(
            name='Sarah Jenkins',
            department='Computer Science & Engineering',
            graduation_year=2021,
            job_role='Software Engineer',
            company='Google',
            experience='3+ Years',
            email='sarah.j@gmail.com'
        )
        a1.set_password('alumni123')

        a2 = Alumni(
            name='Michael Chen',
            department='Information Technology',
            graduation_year=2020,
            job_role='Data Scientist',
            company='Amazon',
            experience='4+ Years',
            email='michael.c@gmail.com'
        )
        a2.set_password('alumni123')

        a3 = Alumni(
            name='Priya Sharma',
            department='Electronics & Communication',
            graduation_year=2022,
            job_role='Product Manager',
            company='Microsoft',
            experience='2+ Years',
            email='priya.s@gmail.com'
        )
        a3.set_password('alumni123')

        db.session.add_all([a1, a2, a3])
        db.session.commit()

        # Seed sample guidance
        cg1 = CareerGuidance(
            alumni_id=a1.id,
            title='Cracking Tech Coding Interviews: A Step-by-Step Guide',
            category='Interview Tips',
            content='Mastering Data Structures and Algorithms is essential. Focus on dynamic programming, graphs, and system design fundamentals. Practice 2-3 LeetCode problems daily and do mock interviews with peers.'
        )
        cg2 = CareerGuidance(
            alumni_id=a2.id,
            title='How to Build an Outstanding Resume for Data & Tech Roles',
            category='Resume Tips',
            content='Use the Action-Impact framework for every bullet point on your resume. Highlight hands-on projects, metrics, and quantitative achievements rather than listing passive responsibilities.'
        )
        cg3 = CareerGuidance(
            alumni_id=a3.id,
            title='Essential Skills Every Fresh Graduate Should Learn in 2025',
            category='Skill Suggestions',
            content='Beyond core coding skills, learn Cloud basics (AWS/Azure), Version Control (Git), Docker, and effective written communication. Soft skills and teamwork are highly valued in top firms.'
        )
        db.session.add_all([cg1, cg2, cg3])
        db.session.commit()


# Auth Decorators
def student_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if session.get('user_type') != 'student':
            flash('Please log in as a Student to access this page.', 'warning')
            return redirect(url_for('student_login'))
        return f(*args, **kwargs)
    return decorated_function


def alumni_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if session.get('user_type') != 'alumni':
            flash('Please log in as an Alumni to access this page.', 'warning')
            return redirect(url_for('alumni_login'))
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


# Home Route
@app.route('/')
def index():
    alumni_count = db.session.query(Alumni).count()
    student_count = db.session.query(Student).count()
    mentorship_count = db.session.query(MentorshipRequest).count()
    guidance_count = db.session.query(CareerGuidance).count()
    recent_alumni = Alumni.query.order_by(Alumni.created_at.desc()).limit(3).all()
    recent_guidance = CareerGuidance.query.order_by(CareerGuidance.created_at.desc()).limit(3).all()
    return render_template(
        'index.html',
        alumni_count=alumni_count,
        student_count=student_count,
        mentorship_count=mentorship_count,
        guidance_count=guidance_count,
        recent_alumni=recent_alumni,
        recent_guidance=recent_guidance
    )


# Student Registration & Login
@app.route('/student/register', methods=['GET', 'POST'])
def student_register():
    if request.method == 'POST':
        name = request.form.get('name', '').strip()
        register_number = request.form.get('register_number', '').strip()
        department = request.form.get('department', '').strip()
        email = request.form.get('email', '').strip().lower()
        password = request.form.get('password', '')

        if not name or not register_number or not department or not email or not password:
            flash('All fields are required.', 'danger')
            return redirect(url_for('student_register'))

        existing_student = db.session.query(Student).filter(
            (Student.email == email) | (Student.register_number == register_number)
        ).first()

        if existing_student:
            flash('Student with this Email or Register Number already exists.', 'danger')
            return redirect(url_for('student_register'))

        student = Student(
            name=name,
            register_number=register_number,
            department=department,
            email=email
        )
        student.set_password(password)
        db.session.add(student)
        db.session.commit()

        flash('Student registration successful! Please log in.', 'success')
        return redirect(url_for('student_login'))

    return render_template('student_register.html')


@app.route('/student/login', methods=['GET', 'POST'])
def student_login():
    if request.method == 'POST':
        email_or_reg = request.form.get('email_or_reg', '').strip()
        password = request.form.get('password', '')

        student = db.session.query(Student).filter(
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
            flash('Invalid Email/Register Number or Password.', 'danger')
            return redirect(url_for('student_login'))

    return render_template('student_login.html')


# Alumni Registration & Login
@app.route('/alumni/register', methods=['GET', 'POST'])
def alumni_register():
    if request.method == 'POST':
        name = request.form.get('name', '').strip()
        department = request.form.get('department', '').strip()
        graduation_year = request.form.get('graduation_year', type=int)
        job_role = request.form.get('job_role', '').strip()
        company = request.form.get('company', '').strip()
        experience = request.form.get('experience', '').strip() or '1-2 Years'
        email = request.form.get('email', '').strip().lower()
        password = request.form.get('password', '')

        if not name or not department or not graduation_year or not job_role or not company or not email or not password:
            flash('All required fields must be filled.', 'danger')
            return redirect(url_for('alumni_register'))

        existing_alumni = db.session.query(Alumni).filter_by(email=email).first()
        if existing_alumni:
            flash('Alumni with this Email address already exists.', 'danger')
            return redirect(url_for('alumni_register'))

        alumni = Alumni(
            name=name,
            department=department,
            graduation_year=graduation_year,
            job_role=job_role,
            company=company,
            experience=experience,
            email=email
        )
        alumni.set_password(password)
        db.session.add(alumni)
        db.session.commit()

        flash('Alumni registration successful! Please log in.', 'success')
        return redirect(url_for('alumni_login'))

    return render_template('alumni_register.html')


@app.route('/alumni/login', methods=['GET', 'POST'])
def alumni_login():
    if request.method == 'POST':
        email = request.form.get('email', '').strip().lower()
        password = request.form.get('password', '')

        alumni = db.session.query(Alumni).filter_by(email=email).first()
        if alumni and alumni.check_password(password):
            session.clear()
            session['user_type'] = 'alumni'
            session['user_id'] = alumni.id
            session['user_name'] = alumni.name
            flash(f'Welcome back, {alumni.name}!', 'success')
            return redirect(url_for('alumni_dashboard'))
        else:
            flash('Invalid Email or Password.', 'danger')
            return redirect(url_for('alumni_login'))

    return render_template('alumni_login.html')


# Admin Login
@app.route('/admin/login', methods=['GET', 'POST'])
def admin_login():
    if request.method == 'POST':
        username = request.form.get('username', '').strip()
        password = request.form.get('password', '')

        admin = db.session.query(Admin).filter_by(username=username).first()
        if admin and admin.check_password(password):
            session.clear()
            session['user_type'] = 'admin'
            session['user_id'] = admin.id
            session['user_name'] = 'Administrator'
            flash('Logged in successfully as Administrator.', 'success')
            return redirect(url_for('admin_dashboard'))
        elif username == 'admin' and password == 'admin123':
            if not admin:
                admin = Admin(username='admin')
                admin.set_password('admin123')
                db.session.add(admin)
                db.session.commit()
            session.clear()
            session['user_type'] = 'admin'
            session['user_id'] = admin.id
            session['user_name'] = 'Administrator'
            flash('Logged in successfully as Administrator.', 'success')
            return redirect(url_for('admin_dashboard'))
        else:
            flash('Invalid Admin Credentials.', 'danger')
            return redirect(url_for('admin_login'))

    return render_template('admin_login.html')


# Logout Route
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
    if not student:
        flash('Student profile not found.', 'danger')
        return redirect(url_for('student_login'))

    all_alumni = Alumni.query.order_by(Alumni.created_at.desc()).all()
    my_requests = MentorshipRequest.query.filter_by(student_id=student_id).order_by(MentorshipRequest.created_at.desc()).all()
    accepted_requests = [r for r in my_requests if r.status == 'Accepted']
    career_guidance_posts = CareerGuidance.query.order_by(CareerGuidance.created_at.desc()).limit(6).all()

    return render_template(
        'student_dashboard.html',
        student=student,
        all_alumni=all_alumni,
        my_requests=my_requests,
        accepted_requests=accepted_requests,
        career_guidance_posts=career_guidance_posts
    )


# Alumni Dashboard
@app.route('/alumni/dashboard')
@alumni_required
def alumni_dashboard():
    alumni_id = session.get('user_id')
    alumni = db.session.get(Alumni, alumni_id)
    if not alumni:
        flash('Alumni profile not found.', 'danger')
        return redirect(url_for('alumni_login'))

    requests_received = MentorshipRequest.query.filter_by(alumni_id=alumni_id).order_by(MentorshipRequest.created_at.desc()).all()
    pending_requests = [r for r in requests_received if r.status == 'Pending']
    accepted_requests = [r for r in requests_received if r.status == 'Accepted']
    my_guidance = CareerGuidance.query.filter_by(alumni_id=alumni_id).order_by(CareerGuidance.created_at.desc()).all()

    return render_template(
        'alumni_dashboard.html',
        alumni=alumni,
        requests_received=requests_received,
        pending_requests=pending_requests,
        accepted_requests=accepted_requests,
        my_guidance=my_guidance
    )


# Find Alumni Mentor
@app.route('/find-mentor')
def find_mentor():
    department = request.args.get('department', '').strip()
    graduation_year = request.args.get('graduation_year', '').strip()
    job_role = request.args.get('job_role', '').strip()
    company = request.args.get('company', '').strip()

    query = Alumni.query

    if department:
        query = query.filter(Alumni.department.ilike(f'%{department}%'))
    if graduation_year:
        try:
            year_val = int(graduation_year)
            query = query.filter(Alumni.graduation_year == year_val)
        except ValueError:
            pass
    if job_role:
        query = query.filter(Alumni.job_role.ilike(f'%{job_role}%'))
    if company:
        query = query.filter(Alumni.company.ilike(f'%{company}%'))

    alumni_list = query.order_by(Alumni.name.asc()).all()

    # Get unique filter dropdown values
    departments = sorted(list(set([a.department for a in Alumni.query.all()])))
    graduation_years = sorted(list(set([a.graduation_year for a in Alumni.query.all()])), reverse=True)
    companies = sorted(list(set([a.company for a in Alumni.query.all()])))
    job_roles = sorted(list(set([a.job_role for a in Alumni.query.all()])))

    return render_template(
        'find_mentor.html',
        alumni_list=alumni_list,
        departments=departments,
        graduation_years=graduation_years,
        companies=companies,
        job_roles=job_roles,
        selected_department=department,
        selected_year=graduation_year,
        selected_role=job_role,
        selected_company=company
    )


# Mentorship Request
@app.route('/mentorship-request', methods=['GET', 'POST'])
@app.route('/mentorship-request/<int:alumni_id>', methods=['GET', 'POST'])
@student_required
def mentorship_request(alumni_id=None):
    student_id = session.get('user_id')
    selected_alumni = None
    if alumni_id:
        selected_alumni = db.session.get(Alumni, alumni_id)

    all_alumni = Alumni.query.order_by(Alumni.name.asc()).all()

    if request.method == 'POST':
        target_alumni_id = request.form.get('alumni_id', type=int)
        question = request.form.get('question', '').strip()

        if not target_alumni_id or not question:
            flash('Please select an alumni mentor and enter your career question.', 'danger')
            return redirect(url_for('mentorship_request', alumni_id=alumni_id or target_alumni_id))

        mentor = db.session.get(Alumni, target_alumni_id)
        if not mentor:
            flash('Selected alumni mentor not found.', 'danger')
            return redirect(url_for('mentorship_request'))

        # Create mentorship request
        m_req = MentorshipRequest(
            student_id=student_id,
            alumni_id=target_alumni_id,
            question=question,
            status='Pending'
        )
        db.session.add(m_req)
        db.session.commit()

        flash(f'Mentorship request submitted successfully to {mentor.name}!', 'success')
        return redirect(url_for('student_dashboard'))

    return render_template(
        'mentorship_request.html',
        selected_alumni=selected_alumni,
        all_alumni=all_alumni
    )


# Respond to Mentorship Request (Alumni)
@app.route('/mentorship-request/respond/<int:request_id>', methods=['POST'])
@alumni_required
def respond_mentorship_request(request_id):
    alumni_id = session.get('user_id')
    m_req = db.session.get(MentorshipRequest, request_id)
    if not m_req:
        flash('Mentorship request not found.', 'danger')
        return redirect(url_for('alumni_dashboard'))

    if m_req.alumni_id != alumni_id:
        flash('Unauthorized action.', 'danger')
        return redirect(url_for('alumni_dashboard'))

    action = request.form.get('action', '').strip()
    response_text = request.form.get('response', '').strip()

    if action == 'accept':
        m_req.status = 'Accepted'
        if response_text:
            m_req.response = response_text
        flash(f'Mentorship request from {m_req.student.name} accepted.', 'success')
    elif action == 'reject':
        m_req.status = 'Rejected'
        if response_text:
            m_req.response = response_text
        flash(f'Mentorship request from {m_req.student.name} rejected.', 'info')
    elif action == 'reply':
        m_req.response = response_text
        flash('Reply saved successfully.', 'success')

    db.session.commit()
    return redirect(url_for('alumni_dashboard'))


# Career Guidance
@app.route('/career-guidance', methods=['GET', 'POST'])
def career_guidance():
    category_filter = request.args.get('category', '').strip()

    if request.method == 'POST':
        if session.get('user_type') != 'alumni':
            flash('Only registered Alumni can post career guidance.', 'warning')
            return redirect(url_for('alumni_login'))

        alumni_id = session.get('user_id')
        title = request.form.get('title', '').strip()
        category = request.form.get('category', '').strip()
        content = request.form.get('content', '').strip()

        if not title or not category or not content:
            flash('Title, category, and content are required.', 'danger')
            return redirect(url_for('career_guidance'))

        guidance = CareerGuidance(
            alumni_id=alumni_id,
            title=title,
            category=category,
            content=content
        )
        db.session.add(guidance)
        db.session.commit()

        flash('Career Guidance advice posted successfully!', 'success')
        return redirect(url_for('career_guidance'))

    query = CareerGuidance.query
    if category_filter:
        query = query.filter_by(category=category_filter)

    guidance_list = query.order_by(CareerGuidance.created_at.desc()).all()
    categories = ['Career Advice', 'Interview Tips', 'Resume Tips', 'Skill Suggestions']

    return render_template(
        'career_guidance.html',
        guidance_list=guidance_list,
        categories=categories,
        selected_category=category_filter
    )


# Admin Dashboard & Management
@app.route('/admin/dashboard')
@admin_required
def admin_dashboard():
    students = Student.query.order_by(Student.created_at.desc()).all()
    alumni_list = Alumni.query.order_by(Alumni.created_at.desc()).all()
    requests_list = MentorshipRequest.query.order_by(MentorshipRequest.created_at.desc()).all()
    guidance_list = CareerGuidance.query.order_by(CareerGuidance.created_at.desc()).all()

    return render_template(
        'admin_dashboard.html',
        students=students,
        alumni_list=alumni_list,
        requests_list=requests_list,
        guidance_list=guidance_list,
        total_students=len(students),
        total_alumni=len(alumni_list),
        total_requests=len(requests_list),
        total_guidance=len(guidance_list)
    )


# Admin Delete Actions
@app.route('/admin/student/delete/<int:student_id>', methods=['POST'])
@admin_required
def admin_delete_student(student_id):
    student = db.session.get(Student, student_id)
    if not student:
        flash('Student not found.', 'danger')
        return redirect(url_for('admin_dashboard'))

    db.session.delete(student)
    db.session.commit()
    flash(f'Student "{student.name}" deleted successfully.', 'info')
    return redirect(url_for('admin_dashboard'))


@app.route('/admin/alumni/delete/<int:alumni_id>', methods=['POST'])
@admin_required
def admin_delete_alumni(alumni_id):
    alumni = db.session.get(Alumni, alumni_id)
    if not alumni:
        flash('Alumni not found.', 'danger')
        return redirect(url_for('admin_dashboard'))

    db.session.delete(alumni)
    db.session.commit()
    flash(f'Alumni "{alumni.name}" deleted successfully.', 'info')
    return redirect(url_for('admin_dashboard'))


@app.route('/admin/request/delete/<int:request_id>', methods=['POST'])
@admin_required
def admin_delete_request(request_id):
    m_req = db.session.get(MentorshipRequest, request_id)
    if not m_req:
        flash('Mentorship Request not found.', 'danger')
        return redirect(url_for('admin_dashboard'))

    db.session.delete(m_req)
    db.session.commit()
    flash(f'Mentorship Request #{request_id} deleted successfully.', 'info')
    return redirect(url_for('admin_dashboard'))


@app.route('/admin/guidance/delete/<int:guidance_id>', methods=['POST'])
@admin_required
def admin_delete_guidance(guidance_id):
    guidance = db.session.get(CareerGuidance, guidance_id)
    if not guidance:
        flash('Career guidance post not found.', 'danger')
        return redirect(url_for('admin_dashboard'))

    db.session.delete(guidance)
    db.session.commit()
    flash('Career Guidance post deleted successfully.', 'info')
    return redirect(url_for('admin_dashboard'))


if __name__ == '__main__':
    with app.app_context():
        db.create_all()
        seed_default_data()
    app.run(debug=True)
