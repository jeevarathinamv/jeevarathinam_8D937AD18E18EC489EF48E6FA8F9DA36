import os
from datetime import datetime, date
from functools import wraps
from flask import Flask, render_template, request, redirect, url_for, flash, session
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'mca_student_exam_timetable_secret_key_2025')

# Admin Hardcoded Fallback Credentials
DEFAULT_ADMIN_USERNAME = os.environ.get('ADMIN_USERNAME', 'admin')
DEFAULT_ADMIN_PASSWORD = os.environ.get('ADMIN_PASSWORD', 'admin123')

# Database configuration: Default to MySQL URI, fallback to SQLite when USE_SQLITE=1
MYSQL_URI = os.environ.get('DATABASE_URL', 'mysql+pymysql://root:@localhost/exam_timetable_db')
SQLITE_URI = 'sqlite:///' + os.path.join(os.path.abspath(os.path.dirname(__file__)), 'exam_timetable.db')

use_sqlite = os.environ.get('USE_SQLITE') == '1'
app.config['SQLALCHEMY_DATABASE_URI'] = SQLITE_URI if use_sqlite else MYSQL_URI
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

# Database Models
class Admin(db.Model):
    __tablename__ = 'admins'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), unique=True, nullable=False)
    password = db.Column(db.String(255), nullable=False)

    def set_password(self, password):
        self.password = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password, password)

class Student(db.Model):
    __tablename__ = 'students'
    id = db.Column(db.Integer, primary_key=True)
    student_name = db.Column(db.String(100), nullable=False)
    register_number = db.Column(db.String(50), unique=True, nullable=False)
    department = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(255), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def set_password(self, password):
        self.password = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password, password)

class ExamTimetable(db.Model):
    __tablename__ = 'exam_timetable'
    id = db.Column(db.Integer, primary_key=True)
    exam_name = db.Column(db.String(100), nullable=False)
    department = db.Column(db.String(100), nullable=False)
    semester = db.Column(db.String(20), nullable=False)
    subject_name = db.Column(db.String(100), nullable=False)
    subject_code = db.Column(db.String(50), nullable=False)
    exam_date = db.Column(db.Date, nullable=False)
    exam_time = db.Column(db.String(50), nullable=False)
    exam_venue = db.Column(db.String(100), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

def seed_default_data():
    """Seed initial admin and sample exam timetable for demonstration."""
    # Seed default Admin
    if db.session.query(Admin).count() == 0:
        admin = Admin(username=DEFAULT_ADMIN_USERNAME)
        admin.set_password(DEFAULT_ADMIN_PASSWORD)
        db.session.add(admin)
        db.session.commit()

    # Seed sample exam timetable records if empty
    if db.session.query(ExamTimetable).count() == 0:
        from datetime import timedelta
        base_date = date.today()
        sample_exams = [
            ExamTimetable(
                exam_name='End Semester Examinations 2025-26',
                department='Master of Computer Applications (MCA)',
                semester='Semester 1',
                subject_name='Data Structures and Algorithms',
                subject_code='MCA101',
                exam_date=base_date + timedelta(days=5),
                exam_time='10:00 AM - 01:00 PM',
                exam_venue='Lab Hall A (Ground Floor)'
            ),
            ExamTimetable(
                exam_name='End Semester Examinations 2025-26',
                department='Master of Computer Applications (MCA)',
                semester='Semester 1',
                subject_name='Database Management Systems',
                subject_code='MCA102',
                exam_date=base_date + timedelta(days=7),
                exam_time='10:00 AM - 01:00 PM',
                exam_venue='Main Exam Hall 2'
            ),
            ExamTimetable(
                exam_name='End Semester Examinations 2025-26',
                department='Master of Computer Applications (MCA)',
                semester='Semester 1',
                subject_name='Python Web Development with Flask',
                subject_code='MCA103',
                exam_date=base_date + timedelta(days=10),
                exam_time='10:00 AM - 01:00 PM',
                exam_venue='Computer Lab 3'
            ),
            ExamTimetable(
                exam_name='End Semester Examinations 2025-26',
                department='Master of Computer Applications (MCA)',
                semester='Semester 2',
                subject_name='Advanced Java & Enterprise Applications',
                subject_code='MCA201',
                exam_date=base_date + timedelta(days=6),
                exam_time='02:00 PM - 05:00 PM',
                exam_venue='Main Exam Hall 1'
            ),
            ExamTimetable(
                exam_name='End Semester Examinations 2025-26',
                department='Master of Computer Applications (MCA)',
                semester='Semester 2',
                subject_name='Cloud Computing & DevOps',
                subject_code='MCA202',
                exam_date=base_date + timedelta(days=9),
                exam_time='02:00 PM - 05:00 PM',
                exam_venue='Seminar Hall B'
            ),
            ExamTimetable(
                exam_name='Mid Term Examinations 2025-26',
                department='Department of Information Technology',
                semester='Semester 1',
                subject_name='Software Engineering & Agile Methodologies',
                subject_code='IT101',
                exam_date=base_date + timedelta(days=3),
                exam_time='10:00 AM - 12:00 PM',
                exam_venue='IT Block Hall 101'
            )
        ]
        db.session.add_all(sample_exams)
        db.session.commit()

# Helper Functions & Decorators
def student_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if session.get('user_type') != 'student':
            flash('Please log in as a student to access this page.', 'warning')
            return redirect(url_for('login'))
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

@app.context_processor
def inject_now():
    return {'today': date.today()}

# Routes
@app.route('/')
def index():
    departments = db.session.query(ExamTimetable.department).distinct().all()
    departments = [d[0] for d in departments if d[0]]
    exams = db.session.query(ExamTimetable.exam_name).distinct().all()
    exams = [e[0] for e in exams if e[0]]
    total_exams_count = db.session.query(ExamTimetable).count()
    return render_template('index.html', departments=departments, exams=exams, total_exams_count=total_exams_count)

# Student Registration
@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        student_name = request.form.get('student_name', '').strip()
        register_number = request.form.get('register_number', '').strip().upper()
        department = request.form.get('department', '').strip()
        email = request.form.get('email', '').strip().lower()
        password = request.form.get('password', '')

        if not student_name or not register_number or not department or not email or not password:
            flash('All registration fields are required.', 'danger')
            return redirect(url_for('register'))

        if len(password) < 6:
            flash('Password must be at least 6 characters long.', 'danger')
            return redirect(url_for('register'))

        existing_student = db.session.query(Student).filter(
            (Student.email == email) | (Student.register_number == register_number)
        ).first()

        if existing_student:
            flash('A student with this Email or Register Number is already registered.', 'danger')
            return redirect(url_for('register'))

        new_student = Student(
            student_name=student_name,
            register_number=register_number,
            department=department,
            email=email
        )
        new_student.set_password(password)
        db.session.add(new_student)
        db.session.commit()

        flash('Registration successful! Please log in to view your exam timetable.', 'success')
        return redirect(url_for('login'))

    return render_template('register.html')

# Student Login
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email_or_reg = request.form.get('email_or_reg', '').strip()
        password = request.form.get('password', '')

        if not email_or_reg or not password:
            flash('Please fill in both fields.', 'danger')
            return redirect(url_for('login'))

        student = db.session.query(Student).filter(
            (Student.email == email_or_reg.lower()) | (Student.register_number == email_or_reg.upper())
        ).first()

        if student and student.check_password(password):
            session.clear()
            session['user_type'] = 'student'
            session['student_id'] = student.id
            session['student_name'] = student.student_name
            session['register_number'] = student.register_number
            session['department'] = student.department
            flash(f'Welcome back, {student.student_name}!', 'success')
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

        if not username or not password:
            flash('Username and password are required.', 'danger')
            return redirect(url_for('admin_login'))

        admin = db.session.query(Admin).filter_by(username=username).first()

        if admin and admin.check_password(password):
            session.clear()
            session['user_type'] = 'admin'
            session['admin_username'] = admin.username
            flash('Successfully logged in as Administrator.', 'success')
            return redirect(url_for('admin_dashboard'))
        elif username == DEFAULT_ADMIN_USERNAME and password == DEFAULT_ADMIN_PASSWORD:
            session.clear()
            session['user_type'] = 'admin'
            session['admin_username'] = DEFAULT_ADMIN_USERNAME
            flash('Successfully logged in as Administrator.', 'success')
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
    student_id = session.get('student_id')
    student = db.session.get(Student, student_id) if hasattr(db.session, 'get') else Student.query.get(student_id)

    # Get filter query parameters
    selected_dept = request.args.get('department', student.department if student else '').strip()
    selected_sem = request.args.get('semester', '').strip()
    selected_exam = request.args.get('exam', '').strip()

    query = db.session.query(ExamTimetable)

    if selected_dept:
        query = query.filter(ExamTimetable.department.ilike(f"%{selected_dept}%"))
    if selected_sem:
        query = query.filter(ExamTimetable.semester == selected_sem)
    if selected_exam:
        query = query.filter(ExamTimetable.exam_name.ilike(f"%{selected_exam}%"))

    timetable = query.order_by(ExamTimetable.exam_date.asc(), ExamTimetable.exam_time.asc()).all()

    today_date = date.today()

    # Calculate Student Metrics
    all_student_exams = db.session.query(ExamTimetable).filter(
        ExamTimetable.department.ilike(f"%{student.department}%")
    ).all() if student else []

    upcoming_exams = [e for e in all_student_exams if e.exam_date >= today_date]

    # Unique subjects count
    unique_subjects = set(e.subject_code for e in all_student_exams)

    # Next Exam (closest upcoming exam)
    upcoming_sorted = sorted(upcoming_exams, key=lambda x: x.exam_date)
    next_exam = upcoming_sorted[0] if upcoming_sorted else None

    # Distinct options for dropdown filters
    departments = [d[0] for d in db.session.query(ExamTimetable.department).distinct().all() if d[0]]
    semesters = [s[0] for s in db.session.query(ExamTimetable.semester).distinct().all() if s[0]]
    exams = [e[0] for e in db.session.query(ExamTimetable.exam_name).distinct().all() if e[0]]

    return render_template(
        'student_dashboard.html',
        student=student,
        timetable=timetable,
        upcoming_count=len(upcoming_exams),
        total_subjects_count=len(unique_subjects),
        next_exam=next_exam,
        departments=departments,
        semesters=semesters,
        exams=exams,
        selected_dept=selected_dept,
        selected_sem=selected_sem,
        selected_exam=selected_exam
    )

# Dedicated Timetable View Page (Accessible to Students & Public)
@app.route('/timetable')
def timetable():
    selected_dept = request.args.get('department', '').strip()
    selected_sem = request.args.get('semester', '').strip()
    selected_exam = request.args.get('exam', '').strip()

    query = db.session.query(ExamTimetable)

    if selected_dept:
        query = query.filter(ExamTimetable.department.ilike(f"%{selected_dept}%"))
    if selected_sem:
        query = query.filter(ExamTimetable.semester == selected_sem)
    if selected_exam:
        query = query.filter(ExamTimetable.exam_name.ilike(f"%{selected_exam}%"))

    timetable_records = query.order_by(ExamTimetable.exam_date.asc(), ExamTimetable.exam_time.asc()).all()

    departments = [d[0] for d in db.session.query(ExamTimetable.department).distinct().all() if d[0]]
    semesters = [s[0] for s in db.session.query(ExamTimetable.semester).distinct().all() if s[0]]
    exams = [e[0] for e in db.session.query(ExamTimetable.exam_name).distinct().all() if e[0]]

    return render_template(
        'timetable.html',
        timetable=timetable_records,
        departments=departments,
        semesters=semesters,
        exams=exams,
        selected_dept=selected_dept,
        selected_sem=selected_sem,
        selected_exam=selected_exam
    )

# Admin Dashboard
@app.route('/admin/dashboard')
@admin_required
def admin_dashboard():
    total_students = db.session.query(Student).count()
    total_exams = len(set(e.exam_name for e in db.session.query(ExamTimetable).all()))
    total_subjects = len(set(e.subject_code for e in db.session.query(ExamTimetable).all()))
    upcoming_exams = db.session.query(ExamTimetable).filter(ExamTimetable.exam_date >= date.today()).count()

    students = db.session.query(Student).order_by(Student.created_at.desc()).all()

    return render_template(
        'admin_dashboard.html',
        total_students=total_students,
        total_exams=total_exams,
        total_subjects=total_subjects,
        upcoming_exams=upcoming_exams,
        students=students
    )

# Admin Manage Timetable List
@app.route('/admin/timetable')
@admin_required
def manage_timetable():
    selected_dept = request.args.get('department', '').strip()
    selected_sem = request.args.get('semester', '').strip()
    selected_exam = request.args.get('exam', '').strip()

    query = db.session.query(ExamTimetable)

    if selected_dept:
        query = query.filter(ExamTimetable.department.ilike(f"%{selected_dept}%"))
    if selected_sem:
        query = query.filter(ExamTimetable.semester == selected_sem)
    if selected_exam:
        query = query.filter(ExamTimetable.exam_name.ilike(f"%{selected_exam}%"))

    timetable_records = query.order_by(ExamTimetable.exam_date.asc(), ExamTimetable.exam_time.asc()).all()

    departments = [d[0] for d in db.session.query(ExamTimetable.department).distinct().all() if d[0]]
    semesters = [s[0] for s in db.session.query(ExamTimetable.semester).distinct().all() if s[0]]
    exams = [e[0] for e in db.session.query(ExamTimetable.exam_name).distinct().all() if e[0]]

    return render_template(
        'manage_timetable.html',
        timetable=timetable_records,
        departments=departments,
        semesters=semesters,
        exams=exams,
        selected_dept=selected_dept,
        selected_sem=selected_sem,
        selected_exam=selected_exam
    )

# Admin Add Exam Timetable
@app.route('/admin/timetable/add', methods=['GET', 'POST'])
@admin_required
def add_exam():
    if request.method == 'POST':
        exam_name = request.form.get('exam_name', '').strip()
        department = request.form.get('department', '').strip()
        semester = request.form.get('semester', '').strip()
        subject_name = request.form.get('subject_name', '').strip()
        subject_code = request.form.get('subject_code', '').strip().upper()
        exam_date_str = request.form.get('exam_date', '').strip()
        exam_time = request.form.get('exam_time', '').strip()
        exam_venue = request.form.get('exam_venue', '').strip()

        if not all([exam_name, department, semester, subject_name, subject_code, exam_date_str, exam_time, exam_venue]):
            flash('All exam fields are required.', 'danger')
            return redirect(url_for('add_exam'))

        try:
            exam_date_val = datetime.strptime(exam_date_str, '%Y-%m-%d').date()
        except ValueError:
            flash('Invalid date format. Please use YYYY-MM-DD.', 'danger')
            return redirect(url_for('add_exam'))

        new_exam = ExamTimetable(
            exam_name=exam_name,
            department=department,
            semester=semester,
            subject_name=subject_name,
            subject_code=subject_code,
            exam_date=exam_date_val,
            exam_time=exam_time,
            exam_venue=exam_venue
        )
        db.session.add(new_exam)
        db.session.commit()

        flash('Exam timetable entry added successfully!', 'success')
        return redirect(url_for('manage_timetable'))

    return render_template('add_exam.html')

# Admin Edit Exam Timetable
@app.route('/admin/timetable/edit/<int:exam_id>', methods=['GET', 'POST'])
@admin_required
def edit_exam(exam_id):
    exam = db.session.get(ExamTimetable, exam_id) if hasattr(db.session, 'get') else ExamTimetable.query.get_or_404(exam_id)
    if not exam:
        flash('Exam record not found.', 'danger')
        return redirect(url_for('manage_timetable'))

    if request.method == 'POST':
        exam_name = request.form.get('exam_name', '').strip()
        department = request.form.get('department', '').strip()
        semester = request.form.get('semester', '').strip()
        subject_name = request.form.get('subject_name', '').strip()
        subject_code = request.form.get('subject_code', '').strip().upper()
        exam_date_str = request.form.get('exam_date', '').strip()
        exam_time = request.form.get('exam_time', '').strip()
        exam_venue = request.form.get('exam_venue', '').strip()

        if not all([exam_name, department, semester, subject_name, subject_code, exam_date_str, exam_time, exam_venue]):
            flash('All exam fields are required.', 'danger')
            return redirect(url_for('edit_exam', exam_id=exam_id))

        try:
            exam_date_val = datetime.strptime(exam_date_str, '%Y-%m-%d').date()
        except ValueError:
            flash('Invalid date format.', 'danger')
            return redirect(url_for('edit_exam', exam_id=exam_id))

        exam.exam_name = exam_name
        exam.department = department
        exam.semester = semester
        exam.subject_name = subject_name
        exam.subject_code = subject_code
        exam.exam_date = exam_date_val
        exam.exam_time = exam_time
        exam.exam_venue = exam_venue

        db.session.commit()

        flash('Exam timetable entry updated successfully!', 'success')
        return redirect(url_for('manage_timetable'))

    return render_template('edit_exam.html', exam=exam)

# Admin Delete Exam Timetable
@app.route('/admin/timetable/delete/<int:exam_id>', methods=['POST'])
@admin_required
def delete_exam(exam_id):
    exam = db.session.get(ExamTimetable, exam_id) if hasattr(db.session, 'get') else ExamTimetable.query.get_or_404(exam_id)
    if exam:
        db.session.delete(exam)
        db.session.commit()
        flash('Exam timetable entry deleted successfully.', 'success')
    else:
        flash('Exam record not found.', 'danger')
    return redirect(url_for('manage_timetable'))

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
        seed_default_data()
    app.run(debug=True)
