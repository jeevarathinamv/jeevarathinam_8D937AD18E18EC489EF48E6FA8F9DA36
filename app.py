import os
import io
from datetime import datetime
from functools import wraps
from flask import Flask, render_template, request, redirect, url_for, flash, session, make_response
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash

# ReportLab imports for PDF generation
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, HRFlowable, Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib import colors

app = Flask(__name__)
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'resume_builder_secret_key_12345')

# Admin Hardcoded Credentials
ADMIN_USERNAME = os.environ.get('ADMIN_USERNAME', 'admin')
ADMIN_PASSWORD = os.environ.get('ADMIN_PASSWORD', 'admin123')

# Database configuration: Default to MySQL URI (for XAMPP/phpMyAdmin), fallback to SQLite when USE_SQLITE=1
MYSQL_URI = os.environ.get('DATABASE_URL', 'mysql+pymysql://root:@localhost/resume_builder_db')
SQLITE_URI = 'sqlite:///' + os.path.join(os.path.abspath(os.path.dirname(__file__)), 'resume_builder.db')

use_sqlite = os.environ.get('USE_SQLITE') == '1'
app.config['SQLALCHEMY_DATABASE_URI'] = SQLITE_URI if use_sqlite else MYSQL_URI
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

class Student(db.Model):
    __tablename__ = 'students'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    register_number = db.Column(db.String(50), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    resumes = db.relationship('Resume', backref='student', lazy=True, cascade='all, delete-orphan')

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

class Resume(db.Model):
    __tablename__ = 'resumes'
    id = db.Column(db.Integer, primary_key=True)
    student_id = db.Column(db.Integer, db.ForeignKey('students.id'), nullable=False)
    title = db.Column(db.String(100), nullable=False, default='My Resume')
    full_name = db.Column(db.String(100), nullable=False)
    phone = db.Column(db.String(20), nullable=False)
    email = db.Column(db.String(120), nullable=False)
    address = db.Column(db.Text, nullable=False)
    career_objective = db.Column(db.Text, nullable=False)
    education = db.Column(db.Text, nullable=False)
    skills = db.Column(db.Text, nullable=False)
    projects = db.Column(db.Text, nullable=True)
    certifications = db.Column(db.Text, nullable=True)
    hobbies = db.Column(db.Text, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

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

@app.route('/')
def index():
    return render_template('index.html')

# Student Registration
@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        name = request.form.get('name', '').strip()
        register_number = request.form.get('register_number', '').strip()
        email = request.form.get('email', '').strip().lower()
        password = request.form.get('password', '')

        if not name or not register_number or not email or not password:
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
            if username == ADMIN_USERNAME and password == ADMIN_PASSWORD:
                session['user_type'] = 'admin'
                session['user_name'] = 'Administrator'
                flash('Logged in successfully as Administrator.', 'success')
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

# Student Dashboard
@app.route('/student/dashboard')
@student_required
def student_dashboard():
    student_id = session.get('user_id')
    student = Student.query.get(student_id)
    resumes = Resume.query.filter_by(student_id=student_id).order_by(Resume.updated_at.desc()).all()
    return render_template('student_dashboard.html', student=student, resumes=resumes)

# Create Resume
@app.route('/resume/create', methods=['GET', 'POST'])
@student_required
def create_resume():
    student_id = session.get('user_id')
    student = Student.query.get(student_id)

    if request.method == 'POST':
        title = request.form.get('title', 'My Resume').strip()
        full_name = request.form.get('full_name', '').strip()
        phone = request.form.get('phone', '').strip()
        email = request.form.get('email', '').strip()
        address = request.form.get('address', '').strip()
        career_objective = request.form.get('career_objective', '').strip()
        education = request.form.get('education', '').strip()
        skills = request.form.get('skills', '').strip()
        projects = request.form.get('projects', '').strip()
        certifications = request.form.get('certifications', '').strip()
        hobbies = request.form.get('hobbies', '').strip()

        if not full_name or not phone or not email or not address or not career_objective or not education or not skills:
            flash('Please fill in all required fields (Name, Phone, Email, Address, Career Objective, Education, Skills).', 'danger')
            return render_template('resume_form.html', student=student, resume=None, action='create')

        resume = Resume(
            student_id=student_id,
            title=title if title else 'My Resume',
            full_name=full_name,
            phone=phone,
            email=email,
            address=address,
            career_objective=career_objective,
            education=education,
            skills=skills,
            projects=projects,
            certifications=certifications,
            hobbies=hobbies
        )
        db.session.add(resume)
        db.session.commit()

        flash('Resume created successfully!', 'success')
        return redirect(url_for('student_dashboard'))

    return render_template('resume_form.html', student=student, resume=None, action='create')

# Edit Resume
@app.route('/resume/edit/<int:resume_id>', methods=['GET', 'POST'])
@student_required
def edit_resume(resume_id):
    student_id = session.get('user_id')
    resume = Resume.query.filter_by(id=resume_id, student_id=student_id).first_or_404()

    if request.method == 'POST':
        title = request.form.get('title', 'My Resume').strip()
        full_name = request.form.get('full_name', '').strip()
        phone = request.form.get('phone', '').strip()
        email = request.form.get('email', '').strip()
        address = request.form.get('address', '').strip()
        career_objective = request.form.get('career_objective', '').strip()
        education = request.form.get('education', '').strip()
        skills = request.form.get('skills', '').strip()
        projects = request.form.get('projects', '').strip()
        certifications = request.form.get('certifications', '').strip()
        hobbies = request.form.get('hobbies', '').strip()

        if not full_name or not phone or not email or not address or not career_objective or not education or not skills:
            flash('Please fill in all required fields.', 'danger')
            return render_template('resume_form.html', resume=resume, action='edit')

        resume.title = title if title else 'My Resume'
        resume.full_name = full_name
        resume.phone = phone
        resume.email = email
        resume.address = address
        resume.career_objective = career_objective
        resume.education = education
        resume.skills = skills
        resume.projects = projects
        resume.certifications = certifications
        resume.hobbies = hobbies

        db.session.commit()
        flash('Resume updated successfully!', 'success')
        return redirect(url_for('student_dashboard'))

    return render_template('resume_form.html', resume=resume, action='edit')

# View Resume HTML
@app.route('/resume/view/<int:resume_id>')
def view_resume(resume_id):
    # Allow viewing by owner student or admin or direct link
    resume = Resume.query.get_or_404(resume_id)
    return render_template('resume_view.html', resume=resume)

# Delete Resume (Student)
@app.route('/resume/delete/<int:resume_id>', methods=['POST'])
@student_required
def delete_resume_student(resume_id):
    student_id = session.get('user_id')
    resume = Resume.query.filter_by(id=resume_id, student_id=student_id).first_or_404()
    db.session.delete(resume)
    db.session.commit()
    flash('Resume deleted successfully.', 'info')
    return redirect(url_for('student_dashboard'))

# Admin Dashboard
@app.route('/admin/dashboard')
@admin_required
def admin_dashboard():
    students = Student.query.order_by(Student.created_at.desc()).all()
    resumes = Resume.query.order_by(Resume.updated_at.desc()).all()
    total_students = len(students)
    total_resumes = len(resumes)
    return render_template('admin_dashboard.html', students=students, resumes=resumes, total_students=total_students, total_resumes=total_resumes)

# Delete Resume (Admin)
@app.route('/admin/resume/delete/<int:resume_id>', methods=['POST'])
@admin_required
def delete_resume_admin(resume_id):
    resume = Resume.query.get_or_404(resume_id)
    db.session.delete(resume)
    db.session.commit()
    flash(f'Resume "{resume.title}" belonging to student "{resume.full_name}" has been deleted.', 'info')
    return redirect(url_for('admin_dashboard'))

# Generate & Download Resume PDF
@app.route('/resume/download/<int:resume_id>')
def download_resume_pdf(resume_id):
    resume = Resume.query.get_or_404(resume_id)

    # Helper function to convert multiline text into Paragraph elements
    def text_to_paragraphs(text, style):
        if not text:
            return []
        lines = [line.strip() for line in text.split('\n') if line.strip()]
        paragraphs = []
        for line in lines:
            clean_line = line.replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;')
            if clean_line.startswith('-') or clean_line.startswith('•'):
                clean_line = '• ' + clean_line.lstrip('-• ').strip()
            paragraphs.append(Paragraph(clean_line, style))
        return paragraphs

    buffer = io.BytesIO()
    doc = SimpleDocTemplate(
        buffer,
        pagesize=letter,
        rightMargin=40,
        leftMargin=40,
        topMargin=40,
        bottomMargin=40
    )

    styles = getSampleStyleSheet()

    # Custom Color Palette
    primary_color = colors.HexColor('#0d6efd') # Bootstrap Primary
    dark_color = colors.HexColor('#212529')
    text_color = colors.HexColor('#333333')

    # Custom Typography Styles
    name_style = ParagraphStyle(
        'NameStyle',
        parent=styles['Heading1'],
        fontName='Helvetica-Bold',
        fontSize=24,
        leading=28,
        textColor=primary_color,
        spaceAfter=4
    )

    contact_style = ParagraphStyle(
        'ContactStyle',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=10,
        leading=14,
        textColor=dark_color,
        alignment=0 # Left aligned
    )

    section_heading_style = ParagraphStyle(
        'SectionHeadingStyle',
        parent=styles['Heading2'],
        fontName='Helvetica-Bold',
        fontSize=13,
        leading=16,
        textColor=primary_color,
        spaceBefore=10,
        spaceAfter=4,
        textTransform='uppercase'
    )

    body_style = ParagraphStyle(
        'BodyStyle',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=10,
        leading=14,
        textColor=text_color,
        spaceAfter=4
    )

    story = []

    # Header section: Name and Contact info
    story.append(Paragraph(resume.full_name, name_style))
    contact_info = f"<b>Email:</b> {resume.email} &nbsp;|&nbsp; <b>Phone:</b> {resume.phone}<br/><b>Address:</b> {resume.address}"
    story.append(Paragraph(contact_info, contact_style))
    story.append(Spacer(1, 10))
    story.append(HRFlowable(width="100%", thickness=1.5, color=primary_color, spaceBefore=0, spaceAfter=10))

    # Function to add section
    def add_section(title, content):
        if content:
            story.append(Paragraph(title, section_heading_style))
            story.append(HRFlowable(width="100%", thickness=0.5, color=colors.lightgrey, spaceBefore=2, spaceAfter=6))
            paras = text_to_paragraphs(content, body_style)
            for p in paras:
                story.append(p)
            story.append(Spacer(1, 8))

    add_section("Career Objective", resume.career_objective)
    add_section("Education Details", resume.education)
    add_section("Technical Skills", resume.skills)
    add_section("Projects", resume.projects)
    add_section("Certifications", resume.certifications)
    add_section("Hobbies & Interests", resume.hobbies)

    doc.build(story)
    buffer.seek(0)

    filename = f"{resume.full_name.replace(' ', '_')}_Resume.pdf"
    response = make_response(buffer.getvalue())
    response.headers['Content-Type'] = 'application/pdf'
    response.headers['Content-Disposition'] = f'inline; filename="{filename}"'

    return response

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True)
