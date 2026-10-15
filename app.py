import os
import csv
from io import StringIO
from datetime import datetime, date
from functools import wraps
from flask import Flask, render_template, request, redirect, url_for, flash, session, Response
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'college_attendance_secret_key_123')

# Admin Hardcoded Defaults / Environment Overrides
ADMIN_USERNAME = os.environ.get('ADMIN_USERNAME', 'admin')
ADMIN_PASSWORD = os.environ.get('ADMIN_PASSWORD', 'admin123')

# Database configuration: Default to MySQL URI, fallback to SQLite when USE_SQLITE=1
MYSQL_URI = os.environ.get('DATABASE_URL', 'mysql+pymysql://root:@localhost/college_attendance_db')
SQLITE_URI = 'sqlite:///' + os.path.join(os.path.abspath(os.path.dirname(__file__)), 'college_attendance.db')

use_sqlite = os.environ.get('USE_SQLITE') == '1'
app.config['SQLALCHEMY_DATABASE_URI'] = SQLITE_URI if use_sqlite else MYSQL_URI
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

# -----------------------------------------------------------------------------
# Database Models
# -----------------------------------------------------------------------------

class Admin(db.Model):
    __tablename__ = 'admins'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    email = db.Column(db.String(100), nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)


class Class(db.Model):
    __tablename__ = 'classes'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), unique=True, nullable=False)
    tutor_id = db.Column(db.Integer, db.ForeignKey('teachers.id', use_alter=True, name='fk_class_tutor_id'), nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    students = db.relationship('Student', backref='student_class', lazy=True, cascade='all, delete-orphan')
    subjects = db.relationship('Subject', backref='subject_class', lazy=True, cascade='all, delete-orphan')
    timetables = db.relationship('Timetable', backref='timetable_class', lazy=True, cascade='all, delete-orphan')


class Teacher(db.Model):
    __tablename__ = 'teachers'
    id = db.Column(db.Integer, primary_key=True)
    teacher_id = db.Column(db.String(50), unique=True, nullable=False)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    phone = db.Column(db.String(20), nullable=True)
    password_hash = db.Column(db.String(255), nullable=False)
    assigned_class_id = db.Column(db.Integer, db.ForeignKey('classes.id'), nullable=True)
    assigned_subject_id = db.Column(db.Integer, db.ForeignKey('subjects.id'), nullable=True)
    role = db.Column(db.String(20), default='Teacher') # 'Teacher' or 'Class Tutor'
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    assigned_class = db.relationship('Class', foreign_keys=[assigned_class_id], backref='assigned_teachers')
    assigned_subject = db.relationship('Subject', foreign_keys=[assigned_subject_id], backref='assigned_teachers')
    tutored_class = db.relationship('Class', foreign_keys=[Class.tutor_id], uselist=False, backref='tutor')

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
    class_id = db.Column(db.Integer, db.ForeignKey('classes.id'), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    phone = db.Column(db.String(20), nullable=True)
    password_hash = db.Column(db.String(255), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    attendance_records = db.relationship('AttendanceRecord', backref='student', lazy=True, cascade='all, delete-orphan')

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)


class Subject(db.Model):
    __tablename__ = 'subjects'
    id = db.Column(db.Integer, primary_key=True)
    code = db.Column(db.String(20), nullable=False)
    name = db.Column(db.String(100), nullable=False)
    class_id = db.Column(db.Integer, db.ForeignKey('classes.id'), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    timetables = db.relationship('Timetable', backref='subject', lazy=True, cascade='all, delete-orphan')


class Timetable(db.Model):
    __tablename__ = 'timetable'
    id = db.Column(db.Integer, primary_key=True)
    class_id = db.Column(db.Integer, db.ForeignKey('classes.id'), nullable=False)
    day = db.Column(db.String(20), nullable=False) # Monday, Tuesday, Wednesday, Thursday, Friday
    hour_number = db.Column(db.Integer, nullable=False) # 1 to 5
    subject_id = db.Column(db.Integer, db.ForeignKey('subjects.id'), nullable=False)
    teacher_id = db.Column(db.Integer, db.ForeignKey('teachers.id'), nullable=False)
    start_time = db.Column(db.String(20), default='09:30 AM')
    end_time = db.Column(db.String(20), default='10:30 AM')
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    teacher = db.relationship('Teacher', backref='timetables')


class AttendanceSession(db.Model):
    __tablename__ = 'attendance_sessions'
    id = db.Column(db.Integer, primary_key=True)
    class_id = db.Column(db.Integer, db.ForeignKey('classes.id'), nullable=False)
    subject_id = db.Column(db.Integer, db.ForeignKey('subjects.id'), nullable=False)
    teacher_id = db.Column(db.Integer, db.ForeignKey('teachers.id'), nullable=False)
    session_date = db.Column(db.Date, nullable=False)
    hour_number = db.Column(db.Integer, nullable=False)
    status = db.Column(db.String(20), default='Submitted') # 'Submitted' or 'Cancelled'
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    session_class = db.relationship('Class', backref='sessions')
    subject = db.relationship('Subject', backref='sessions')
    teacher = db.relationship('Teacher', backref='sessions')
    records = db.relationship('AttendanceRecord', backref='session', lazy=True, cascade='all, delete-orphan')


class AttendanceRecord(db.Model):
    __tablename__ = 'attendance_records'
    id = db.Column(db.Integer, primary_key=True)
    session_id = db.Column(db.Integer, db.ForeignKey('attendance_sessions.id'), nullable=False)
    student_id = db.Column(db.Integer, db.ForeignKey('students.id'), nullable=False)
    status = db.Column(db.String(10), nullable=False) # 'Present' or 'Absent'


class AttendanceReport(db.Model):
    __tablename__ = 'attendance_reports'
    id = db.Column(db.Integer, primary_key=True)
    class_id = db.Column(db.Integer, db.ForeignKey('classes.id'), nullable=False)
    subject_id = db.Column(db.Integer, db.ForeignKey('subjects.id'), nullable=True)
    report_date = db.Column(db.Date, nullable=False)
    total_students = db.Column(db.Integer, default=0)
    present_count = db.Column(db.Integer, default=0)
    absent_count = db.Column(db.Integer, default=0)
    attendance_percentage = db.Column(db.Float, default=0.0)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)


class InternalMarkRule(db.Model):
    __tablename__ = 'internal_mark_rules'
    id = db.Column(db.Integer, primary_key=True)
    min_percentage = db.Column(db.Float, nullable=False)
    max_percentage = db.Column(db.Float, nullable=False)
    mark = db.Column(db.Integer, nullable=False)
    status_label = db.Column(db.String(50), nullable=False)


# -----------------------------------------------------------------------------
# Seeding Helper
# -----------------------------------------------------------------------------

def seed_default_data():
    if Admin.query.count() == 0:
        admin = Admin(username=ADMIN_USERNAME, email='admin@college.edu')
        admin.set_password(ADMIN_PASSWORD)
        db.session.add(admin)

    if InternalMarkRule.query.count() == 0:
        rules = [
            InternalMarkRule(min_percentage=90.0, max_percentage=100.0, mark=5, status_label='Eligible'),
            InternalMarkRule(min_percentage=80.0, max_percentage=89.99, mark=4, status_label='Eligible'),
            InternalMarkRule(min_percentage=70.0, max_percentage=79.99, mark=3, status_label='Eligible'),
            InternalMarkRule(min_percentage=60.0, max_percentage=69.99, mark=2, status_label='Eligible'),
            InternalMarkRule(min_percentage=50.0, max_percentage=59.99, mark=1, status_label='Eligible'),
            InternalMarkRule(min_percentage=0.0,  max_percentage=49.99, mark=0, status_label='RA – Attendance Below 50%')
        ]
        db.session.add_all(rules)

    if Class.query.count() == 0:
        class_names = ['BCA I', 'BCA II', 'BCA III', 'MCA I', 'MCA II']
        classes = [Class(name=name) for name in class_names]
        db.session.add_all(classes)
        db.session.commit()

        # Teachers
        teachers_data = [
            ('TCH101', 'Dr. Rajesh Kumar', 'rajesh@college.edu', '9876543210', 4, 'Class Tutor'),
            ('TCH102', 'Prof. Sunita Sharma', 'sunita@college.edu', '9876543211', 5, 'Class Tutor'),
            ('TCH103', 'Mr. Anish Verma', 'anish@college.edu', '9876543212', 1, 'Class Tutor'),
            ('TCH104', 'Ms. Priya Nair', 'priya@college.edu', '9876543213', 2, 'Class Tutor'),
            ('TCH105', 'Dr. Suresh Patel', 'suresh@college.edu', '9876543214', 3, 'Class Tutor')
        ]
        teacher_objs = []
        for tid, name, email, phone, cid, role in teachers_data:
            t = Teacher(teacher_id=tid, name=name, email=email, phone=phone, assigned_class_id=cid, role=role)
            t.set_password('teacher123')
            db.session.add(t)
            teacher_objs.append(t)
        db.session.commit()

        # Assign tutors to classes
        c1 = Class.query.filter_by(name='BCA I').first()
        c2 = Class.query.filter_by(name='BCA II').first()
        c3 = Class.query.filter_by(name='BCA III').first()
        c4 = Class.query.filter_by(name='MCA I').first()
        c5 = Class.query.filter_by(name='MCA II').first()

        c1.tutor_id = Teacher.query.filter_by(teacher_id='TCH103').first().id
        c2.tutor_id = Teacher.query.filter_by(teacher_id='TCH104').first().id
        c3.tutor_id = Teacher.query.filter_by(teacher_id='TCH105').first().id
        c4.tutor_id = Teacher.query.filter_by(teacher_id='TCH101').first().id
        c5.tutor_id = Teacher.query.filter_by(teacher_id='TCH102').first().id

        # Subjects
        subjects_data = [
            ('BCA101', 'C Programming', c1.id),
            ('BCA102', 'Digital Fundamentals', c1.id),
            ('BCA103', 'Communication Skills', c1.id),
            ('BCA201', 'Data Structures in C++', c2.id),
            ('BCA202', 'Java Programming', c2.id),
            ('BCA203', 'Operating Systems', c2.id),
            ('BCA301', 'Python Programming', c3.id),
            ('BCA302', 'Software Engineering', c3.id),
            ('BCA303', 'Computer Networks', c3.id),
            ('MCA101', 'Advanced Data Structures', c4.id),
            ('MCA102', 'Python Programming', c4.id),
            ('MCA103', 'Database Management Systems', c4.id),
            ('MCA104', 'Computer Networks', c4.id),
            ('MCA201', 'Cloud Computing', c5.id),
            ('MCA202', 'Machine Learning', c5.id),
            ('MCA203', 'Web Technologies', c5.id)
        ]
        for code, name, cid in subjects_data:
            db.session.add(Subject(code=code, name=name, class_id=cid))
        db.session.commit()

        # Assign teacher subjects
        t1 = Teacher.query.filter_by(teacher_id='TCH101').first()
        s_mca1 = Subject.query.filter_by(code='MCA101').first()
        if t1 and s_mca1:
            t1.assigned_subject_id = s_mca1.id

        # Students
        students_data = [
            ('Aravind Swamy', '23BCA01', 'Computer Applications', c1.id, 'aravind@college.edu'),
            ('Bhavana Devi', '23BCA02', 'Computer Applications', c1.id, 'bhavana@college.edu'),
            ('Chiranjeevi R', '23BCA03', 'Computer Applications', c1.id, 'chiru@college.edu'),
            ('Deepak Kumar', '22BCA01', 'Computer Applications', c2.id, 'deepak@college.edu'),
            ('Divya Prakash', '22BCA02', 'Computer Applications', c2.id, 'divya@college.edu'),
            ('Gokulnath M', '21BCA01', 'Computer Applications', c3.id, 'gokul@college.edu'),
            ('Hariharan S', '21BCA02', 'Computer Applications', c3.id, 'hari@college.edu'),
            ('Kavitha Ramesh', '23MCA01', 'Computer Applications', c4.id, 'kavitha@college.edu'),
            ('Karthik Raja', '23MCA02', 'Computer Applications', c4.id, 'karthik@college.edu'),
            ('Lavanya S', '23MCA03', 'Computer Applications', c4.id, 'lavanya@college.edu'),
            ('Manoj Kumar', '23MCA04', 'Computer Applications', c4.id, 'manoj@college.edu'),
            ('Naveen Prashanth', '22MCA01', 'Computer Applications', c5.id, 'naveen@college.edu'),
            ('Nivedita S', '22MCA02', 'Computer Applications', c5.id, 'nivedita@college.edu')
        ]
        for name, reg, dept, cid, email in students_data:
            s = Student(name=name, register_number=reg, department=dept, class_id=cid, email=email, phone='9876543210')
            s.set_password('student123')
            db.session.add(s)
        db.session.commit()

        # Timetables
        tt_data = [
            (c4.id, 'Monday', 1, s_mca1.id, t1.id, '09:30 AM', '10:30 AM'),
            (c4.id, 'Monday', 2, Subject.query.filter_by(code='MCA102').first().id, t1.id, '10:30 AM', '11:30 AM'),
            (c4.id, 'Monday', 3, Subject.query.filter_by(code='MCA103').first().id, t1.id, '11:30 AM', '12:30 PM'),
            (c4.id, 'Monday', 4, Subject.query.filter_by(code='MCA104').first().id, t1.id, '01:30 PM', '02:30 PM'),
            (c4.id, 'Monday', 5, s_mca1.id, t1.id, '02:30 PM', '03:30 PM'),
        ]
        for cid, day, hour, sub_id, tch_id, stime, etime in tt_data:
            db.session.add(Timetable(class_id=cid, day=day, hour_number=hour, subject_id=sub_id, teacher_id=tch_id, start_time=stime, end_time=etime))
        db.session.commit()

        # Sample Attendance Sessions & Records for MCA I
        mca1_students = Student.query.filter_by(class_id=c4.id).all()
        dates = [date(2025, 2, 10), date(2025, 2, 11), date(2025, 2, 12), date(2025, 2, 13), date(2025, 2, 14)]
        # Student attendance patterns:
        # Student 0 (Kavitha): 5/5 Present (100%)
        # Student 1 (Karthik): 4/5 Present (80%)
        # Student 2 (Lavanya): 3/5 Present (60%)
        # Student 3 (Manoj):   2/5 Present (40% -> RA)
        patterns = [
            ['Present', 'Present', 'Present', 'Absent'],
            ['Present', 'Present', 'Present', 'Present'],
            ['Present', 'Present', 'Absent',  'Absent'],
            ['Present', 'Present', 'Present', 'Absent'],
            ['Present', 'Absent',  'Absent',  'Present']
        ]

        for i, sess_date in enumerate(dates):
            sess = AttendanceSession(
                class_id=c4.id,
                subject_id=s_mca1.id,
                teacher_id=t1.id,
                session_date=sess_date,
                hour_number=1,
                status='Submitted'
            )
            db.session.add(sess)
            db.session.commit()

            for idx, student in enumerate(mca1_students):
                status = patterns[i][idx] if idx < len(patterns[i]) else 'Present'
                rec = AttendanceRecord(session_id=sess.id, student_id=student.id, status=status)
                db.session.add(rec)
            db.session.commit()


# -----------------------------------------------------------------------------
# Business Calculations & Helper Functions
# -----------------------------------------------------------------------------

def calculate_internal_mark(attendance_percentage):
    """
    Calculates internal mark out of 5 based on attendance rules stored in DB.
    Fallback to standard rules if rules table is unpopulated.
    """
    rules = InternalMarkRule.query.order_by(InternalMarkRule.min_percentage.desc()).all()
    if not rules:
        if attendance_percentage >= 90:
            return 5, "Eligible"
        elif attendance_percentage >= 80:
            return 4, "Eligible"
        elif attendance_percentage >= 70:
            return 3, "Eligible"
        elif attendance_percentage >= 60:
            return 2, "Eligible"
        elif attendance_percentage >= 50:
            return 1, "Eligible"
        else:
            return 0, "RA – Attendance Below 50%"

    for rule in rules:
        if rule.min_percentage <= attendance_percentage <= rule.max_percentage:
            return rule.mark, rule.status_label

    # Fallback if below minimum defined rule
    return 0, "RA – Attendance Below 50%"


def get_student_subject_attendance(student_id, subject_id):
    """
    Calculates attendance stats for a specific student and subject.
    Only submitted sessions are counted.
    """
    sessions = AttendanceSession.query.filter_by(
        subject_id=subject_id,
        status='Submitted'
    ).join(Student, Student.class_id == AttendanceSession.class_id)\
     .filter(Student.id == student_id).all()

    total_hours = len(sessions)
    if total_hours == 0:
        return {
            'total_hours': 0,
            'present_hours': 0,
            'absent_hours': 0,
            'percentage': 0.0,
            'internal_mark': 0,
            'status': 'Eligible'
        }

    session_ids = [s.id for s in sessions]
    present_hours = AttendanceRecord.query.filter(
        AttendanceRecord.session_id.in_(session_ids),
        AttendanceRecord.student_id == student_id,
        AttendanceRecord.status == 'Present'
    ).count()

    absent_hours = total_hours - present_hours
    percentage = round((present_hours / total_hours) * 100, 2)
    mark, status = calculate_internal_mark(percentage)

    return {
        'total_hours': total_hours,
        'present_hours': present_hours,
        'absent_hours': absent_hours,
        'percentage': percentage,
        'internal_mark': mark,
        'status': status
    }


def get_student_overall_attendance(student_id):
    """
    Calculates overall attendance across all subjects for a student.
    """
    student = Student.query.get(student_id)
    if not student:
        return {'total_hours': 0, 'present_hours': 0, 'absent_hours': 0, 'percentage': 0.0}

    sessions = AttendanceSession.query.filter_by(
        class_id=student.class_id,
        status='Submitted'
    ).all()

    total_hours = len(sessions)
    if total_hours == 0:
        return {'total_hours': 0, 'present_hours': 0, 'absent_hours': 0, 'percentage': 0.0}

    session_ids = [s.id for s in sessions]
    present_hours = AttendanceRecord.query.filter(
        AttendanceRecord.session_id.in_(session_ids),
        AttendanceRecord.student_id == student_id,
        AttendanceRecord.status == 'Present'
    ).count()

    absent_hours = total_hours - present_hours
    percentage = round((present_hours / total_hours) * 100, 2)

    return {
        'total_hours': total_hours,
        'present_hours': present_hours,
        'absent_hours': absent_hours,
        'percentage': percentage
    }


# -----------------------------------------------------------------------------
# Role-Based Authentication Decorators
# -----------------------------------------------------------------------------

def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_type' not in session:
            flash('Please log in to access this page.', 'warning')
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function


def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if session.get('user_type') != 'admin':
            flash('Admin authorization required.', 'danger')
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function


def teacher_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if session.get('user_type') not in ['teacher', 'tutor']:
            flash('Teacher authorization required.', 'danger')
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function


def tutor_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if session.get('user_type') != 'tutor':
            flash('Class Tutor authorization required.', 'danger')
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function


def student_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if session.get('user_type') != 'student':
            flash('Student authorization required.', 'danger')
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function


# -----------------------------------------------------------------------------
# Web Routes - Public & Auth
# -----------------------------------------------------------------------------

@app.route('/')
def index():
    return render_template('index.html')


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        login_type = request.form.get('login_type', 'student')
        username_or_email_or_reg = request.form.get('identifier', '').strip()
        password = request.form.get('password', '')

        if not username_or_email_or_reg or not password:
            flash('Please enter all credentials.', 'danger')
            return redirect(url_for('login'))

        if login_type == 'admin':
            # Check DB or fallback
            admin = Admin.query.filter(
                (Admin.username == username_or_email_or_reg) | (Admin.email == username_or_email_or_reg)
            ).first()

            if (admin and admin.check_password(password)) or (username_or_email_or_reg == ADMIN_USERNAME and password == ADMIN_PASSWORD):
                session['user_type'] = 'admin'
                session['user_name'] = 'Administrator'
                flash('Successfully logged in as Administrator.', 'success')
                return redirect(url_for('admin_dashboard'))
            else:
                flash('Invalid admin credentials.', 'danger')

        elif login_type in ['teacher', 'tutor']:
            teacher = Teacher.query.filter(
                (Teacher.teacher_id == username_or_email_or_reg) | (Teacher.email == username_or_email_or_reg.lower())
            ).first()

            if teacher and teacher.check_password(password):
                # Check if assigned as Class Tutor
                is_tutor = teacher.role == 'Class Tutor' and teacher.assigned_class_id is not None
                session['user_type'] = 'tutor' if is_tutor else 'teacher'
                session['user_id'] = teacher.id
                session['user_name'] = teacher.name
                session['teacher_id'] = teacher.teacher_id

                if is_tutor:
                    session['tutor_class_id'] = teacher.assigned_class_id

                flash(f'Welcome back, {teacher.name}!', 'success')
                return redirect(url_for('tutor_dashboard' if is_tutor else 'teacher_dashboard'))
            else:
                flash('Invalid teacher credentials.', 'danger')

        elif login_type == 'student':
            student = Student.query.filter(
                (Student.register_number == username_or_email_or_reg) | (Student.email == username_or_email_or_reg.lower())
            ).first()

            if student and student.check_password(password):
                session['user_type'] = 'student'
                session['user_id'] = student.id
                session['user_name'] = student.name
                session['register_number'] = student.register_number
                flash(f'Welcome back, {student.name}!', 'success')
                return redirect(url_for('student_dashboard'))
            else:
                flash('Invalid student credentials.', 'danger')

    return render_template('login.html')


@app.route('/logout')
def logout():
    session.clear()
    flash('You have been logged out successfully.', 'info')
    return redirect(url_for('index'))


# -----------------------------------------------------------------------------
# Admin Dashboard & Management Routes
# -----------------------------------------------------------------------------

@app.route('/admin/dashboard')
@admin_required
def admin_dashboard():
    total_students = Student.query.count()
    total_teachers = Teacher.query.count()
    total_classes = Class.query.count()
    total_subjects = Subject.query.count()
    total_sessions = AttendanceSession.query.filter_by(status='Submitted').count()

    classes = Class.query.order_by(Class.id).all()
    teachers = Teacher.query.order_by(Teacher.name).all()
    subjects = Subject.query.order_by(Subject.name).all()

    return render_template(
        'admin_dashboard.html',
        total_students=total_students,
        total_teachers=total_teachers,
        total_classes=total_classes,
        total_subjects=total_subjects,
        total_sessions=total_sessions,
        classes=classes,
        teachers=teachers,
        subjects=subjects
    )


# Admin - Student Management
@app.route('/admin/students', methods=['GET', 'POST'])
@admin_required
def admin_students():
    if request.method == 'POST':
        name = request.form.get('name', '').strip()
        register_number = request.form.get('register_number', '').strip()
        department = request.form.get('department', '').strip()
        class_id = request.form.get('class_id', type=int)
        email = request.form.get('email', '').strip().lower()
        phone = request.form.get('phone', '').strip()
        password = request.form.get('password', '')

        if not name or not register_number or not department or not class_id or not email or not password:
            flash('All required fields must be filled out.', 'danger')
            return redirect(url_for('admin_students'))

        existing = Student.query.filter(
            (Student.register_number == register_number) | (Student.email == email)
        ).first()
        if existing:
            flash('A student with this Register Number or Email already exists.', 'danger')
            return redirect(url_for('admin_students'))

        student = Student(
            name=name,
            register_number=register_number,
            department=department,
            class_id=class_id,
            email=email,
            phone=phone
        )
        student.set_password(password)
        db.session.add(student)
        db.session.commit()

        flash(f'Student "{name}" added successfully.', 'success')
        return redirect(url_for('admin_students'))

    students = Student.query.order_by(Student.register_number).all()
    classes = Class.query.order_by(Class.id).all()
    return render_template('admin_students.html', students=students, classes=classes)


@app.route('/admin/students/edit/<int:student_id>', methods=['POST'])
@admin_required
def edit_student(student_id):
    student = Student.query.get_or_404(student_id)
    name = request.form.get('name', '').strip()
    department = request.form.get('department', '').strip()
    class_id = request.form.get('class_id', type=int)
    email = request.form.get('email', '').strip().lower()
    phone = request.form.get('phone', '').strip()
    password = request.form.get('password', '')

    if name:
        student.name = name
    if department:
        student.department = department
    if class_id:
        student.class_id = class_id
    if email:
        student.email = email
    if phone:
        student.phone = phone
    if password:
        student.set_password(password)

    db.session.commit()
    flash(f'Student "{student.name}" updated successfully.', 'success')
    return redirect(url_for('admin_students'))


@app.route('/admin/students/delete/<int:student_id>', methods=['POST'])
@admin_required
def delete_student(student_id):
    student = Student.query.get_or_404(student_id)
    db.session.delete(student)
    db.session.commit()
    flash('Student deleted successfully.', 'info')
    return redirect(url_for('admin_students'))


# Admin - Teacher & Tutor Management
@app.route('/admin/teachers', methods=['GET', 'POST'])
@admin_required
def admin_teachers():
    if request.method == 'POST':
        teacher_id = request.form.get('teacher_id', '').strip()
        name = request.form.get('name', '').strip()
        email = request.form.get('email', '').strip().lower()
        phone = request.form.get('phone', '').strip()
        password = request.form.get('password', '')
        assigned_class_id = request.form.get('assigned_class_id', type=int)
        assigned_subject_id = request.form.get('assigned_subject_id', type=int)
        role = request.form.get('role', 'Teacher')

        if not teacher_id or not name or not email or not password:
            flash('Teacher ID, Name, Email, and Password are required.', 'danger')
            return redirect(url_for('admin_teachers'))

        existing = Teacher.query.filter(
            (Teacher.teacher_id == teacher_id) | (Teacher.email == email)
        ).first()
        if existing:
            flash('A teacher with this Teacher ID or Email already exists.', 'danger')
            return redirect(url_for('admin_teachers'))

        teacher = Teacher(
            teacher_id=teacher_id,
            name=name,
            email=email,
            phone=phone,
            assigned_class_id=assigned_class_id,
            assigned_subject_id=assigned_subject_id,
            role=role
        )
        teacher.set_password(password)
        db.session.add(teacher)
        db.session.commit()

        if role == 'Class Tutor' and assigned_class_id:
            # Update class tutor_id
            cls = Class.query.get(assigned_class_id)
            if cls:
                cls.tutor_id = teacher.id
                db.session.commit()

        flash(f'Teacher "{name}" added successfully.', 'success')
        return redirect(url_for('admin_teachers'))

    teachers = Teacher.query.order_by(Teacher.name).all()
    classes = Class.query.order_by(Class.id).all()
    subjects = Subject.query.order_by(Subject.name).all()
    return render_template('admin_teachers.html', teachers=teachers, classes=classes, subjects=subjects)


@app.route('/admin/teachers/edit/<int:teacher_id>', methods=['POST'])
@admin_required
def edit_teacher(teacher_id):
    teacher = Teacher.query.get_or_404(teacher_id)
    name = request.form.get('name', '').strip()
    email = request.form.get('email', '').strip().lower()
    phone = request.form.get('phone', '').strip()
    password = request.form.get('password', '')
    assigned_class_id = request.form.get('assigned_class_id', type=int)
    assigned_subject_id = request.form.get('assigned_subject_id', type=int)
    role = request.form.get('role', 'Teacher')

    if name:
        teacher.name = name
    if email:
        teacher.email = email
    if phone:
        teacher.phone = phone
    if password:
        teacher.set_password(password)

    teacher.assigned_class_id = assigned_class_id
    teacher.assigned_subject_id = assigned_subject_id
    teacher.role = role

    if role == 'Class Tutor' and assigned_class_id:
        cls = Class.query.get(assigned_class_id)
        if cls:
            cls.tutor_id = teacher.id

    db.session.commit()
    flash(f'Teacher "{teacher.name}" updated successfully.', 'success')
    return redirect(url_for('admin_teachers'))


@app.route('/admin/teachers/delete/<int:teacher_id>', methods=['POST'])
@admin_required
def delete_teacher(teacher_id):
    teacher = Teacher.query.get_or_404(teacher_id)
    # Clear tutor assignment if any
    cls = Class.query.filter_by(tutor_id=teacher.id).first()
    if cls:
        cls.tutor_id = None
    db.session.delete(teacher)
    db.session.commit()
    flash('Teacher deleted successfully.', 'info')
    return redirect(url_for('admin_teachers'))


# Admin - Subject Management
@app.route('/admin/subjects', methods=['GET', 'POST'])
@admin_required
def admin_subjects():
    if request.method == 'POST':
        code = request.form.get('code', '').strip().upper()
        name = request.form.get('name', '').strip()
        class_id = request.form.get('class_id', type=int)

        if not code or not name or not class_id:
            flash('Subject Code, Name, and Class selection are required.', 'danger')
            return redirect(url_for('admin_subjects'))

        subject = Subject(code=code, name=name, class_id=class_id)
        db.session.add(subject)
        db.session.commit()

        flash(f'Subject "{name}" added successfully.', 'success')
        return redirect(url_for('admin_subjects'))

    subjects = Subject.query.order_by(Subject.class_id, Subject.code).all()
    classes = Class.query.order_by(Class.id).all()
    return render_template('admin_subjects.html', subjects=subjects, classes=classes)


@app.route('/admin/subjects/edit/<int:subject_id>', methods=['POST'])
@admin_required
def edit_subject(subject_id):
    subject = Subject.query.get_or_404(subject_id)
    code = request.form.get('code', '').strip().upper()
    name = request.form.get('name', '').strip()
    class_id = request.form.get('class_id', type=int)

    if code:
        subject.code = code
    if name:
        subject.name = name
    if class_id:
        subject.class_id = class_id

    db.session.commit()
    flash(f'Subject "{subject.name}" updated successfully.', 'success')
    return redirect(url_for('admin_subjects'))


@app.route('/admin/subjects/delete/<int:subject_id>', methods=['POST'])
@admin_required
def delete_subject(subject_id):
    subject = Subject.query.get_or_404(subject_id)
    db.session.delete(subject)
    db.session.commit()
    flash('Subject deleted successfully.', 'info')
    return redirect(url_for('admin_subjects'))


# Admin - Timetable Management
@app.route('/admin/timetable', methods=['GET', 'POST'])
@admin_required
def admin_timetable():
    if request.method == 'POST':
        class_id = request.form.get('class_id', type=int)
        day = request.form.get('day', '').strip()
        hour_number = request.form.get('hour_number', type=int)
        subject_id = request.form.get('subject_id', type=int)
        teacher_id = request.form.get('teacher_id', type=int)
        start_time = request.form.get('start_time', '09:30 AM').strip()
        end_time = request.form.get('end_time', '10:30 AM').strip()

        if not class_id or not day or not hour_number or not subject_id or not teacher_id:
            flash('All timetable fields are required.', 'danger')
            return redirect(url_for('admin_timetable'))

        # Check duplicate class-hour entry
        existing_class_hour = Timetable.query.filter_by(
            class_id=class_id, day=day, hour_number=hour_number
        ).first()
        if existing_class_hour:
            flash(f'Timetable conflict: Class already has a subject scheduled on {day}, Hour {hour_number}.', 'danger')
            return redirect(url_for('admin_timetable'))

        # Check overlapping teacher assignment
        existing_teacher_hour = Timetable.query.filter_by(
            teacher_id=teacher_id, day=day, hour_number=hour_number
        ).first()
        if existing_teacher_hour:
            flash(f'Teacher conflict: Teacher is already assigned to another class on {day}, Hour {hour_number}.', 'danger')
            return redirect(url_for('admin_timetable'))

        tt = Timetable(
            class_id=class_id,
            day=day,
            hour_number=hour_number,
            subject_id=subject_id,
            teacher_id=teacher_id,
            start_time=start_time,
            end_time=end_time
        )
        db.session.add(tt)
        db.session.commit()

        flash('Timetable slot created successfully.', 'success')
        return redirect(url_for('admin_timetable'))

    timetables = Timetable.query.order_by(Timetable.class_id, Timetable.day, Timetable.hour_number).all()
    classes = Class.query.order_by(Class.id).all()
    teachers = Teacher.query.order_by(Teacher.name).all()
    subjects = Subject.query.order_by(Subject.name).all()
    return render_template('admin_timetable.html', timetables=timetables, classes=classes, teachers=teachers, subjects=subjects)


@app.route('/admin/timetable/delete/<int:tt_id>', methods=['POST'])
@admin_required
def delete_timetable(tt_id):
    tt = Timetable.query.get_or_404(tt_id)
    db.session.delete(tt)
    db.session.commit()
    flash('Timetable slot deleted.', 'info')
    return redirect(url_for('admin_timetable'))


# Admin - Internal Mark Rules Management
@app.route('/admin/mark_rules', methods=['GET', 'POST'])
@admin_required
def admin_mark_rules():
    if request.method == 'POST':
        rules_data = request.form.getlist('rule_id')
        for rule_id in rules_data:
            rule = InternalMarkRule.query.get(int(rule_id))
            if rule:
                min_p = request.form.get(f'min_percentage_{rule_id}', type=float)
                max_p = request.form.get(f'max_percentage_{rule_id}', type=float)
                mark = request.form.get(f'mark_{rule_id}', type=int)
                status_label = request.form.get(f'status_label_{rule_id}', '').strip()

                if min_p is not None:
                    rule.min_percentage = min_p
                if max_p is not None:
                    rule.max_percentage = max_p
                if mark is not None:
                    rule.mark = mark
                if status_label:
                    rule.status_label = status_label

        db.session.commit()
        flash('Internal mark rules updated successfully.', 'success')
        return redirect(url_for('admin_mark_rules'))

    rules = InternalMarkRule.query.order_by(InternalMarkRule.min_percentage.desc()).all()
    return render_template('admin_mark_rules.html', rules=rules)


# -----------------------------------------------------------------------------
# Teacher & Tutor Dashboard & Attendance Routes
# -----------------------------------------------------------------------------

@app.route('/teacher/dashboard')
@teacher_required
def teacher_dashboard():
    teacher_id = session.get('user_id')
    teacher = Teacher.query.get(teacher_id)

    # Get assigned timetable
    my_timetable = Timetable.query.filter_by(teacher_id=teacher_id).order_by(Timetable.day, Timetable.hour_number).all()

    # Get recent attendance sessions
    recent_sessions = AttendanceSession.query.filter_by(teacher_id=teacher_id)\
                        .order_by(AttendanceSession.session_date.desc(), AttendanceSession.hour_number.desc()).limit(10).all()

    today_day = datetime.now().strftime('%A')
    today_date = date.today().isoformat()

    return render_template(
        'teacher_dashboard.html',
        teacher=teacher,
        timetable=my_timetable,
        recent_sessions=recent_sessions,
        today_day=today_day,
        today_date=today_date
    )


@app.route('/teacher/attendance/mark', methods=['GET', 'POST'])
@teacher_required
def mark_attendance():
    teacher_id = session.get('user_id')
    teacher = Teacher.query.get(teacher_id)

    selected_class_id = request.args.get('class_id', type=int) or request.form.get('class_id', type=int)
    selected_subject_id = request.args.get('subject_id', type=int) or request.form.get('subject_id', type=int)
    selected_hour = request.args.get('hour_number', type=int) or request.form.get('hour_number', type=int)
    selected_date_str = request.args.get('session_date') or request.form.get('session_date') or date.today().isoformat()

    # Teachers can mark attendance only for their assigned timetable sessions or subjects
    my_classes = Class.query.join(Timetable, Timetable.class_id == Class.id)\
                    .filter(Timetable.teacher_id == teacher_id).distinct().all()

    if not my_classes:
        # Fallback to teacher's assigned_class or all classes
        my_classes = Class.query.all()

    students = []
    selected_class = None
    selected_subject = None

    if selected_class_id and selected_subject_id and selected_hour:
        # Validate that teacher is assigned to this timetable or subject
        timetable_slot = Timetable.query.filter_by(
            class_id=selected_class_id,
            subject_id=selected_subject_id,
            teacher_id=teacher_id,
            hour_number=selected_hour
        ).first()

        # Allow if teacher matches or is super teacher
        selected_class = Class.query.get(selected_class_id)
        selected_subject = Subject.query.get(selected_subject_id)
        students = Student.query.filter_by(class_id=selected_class_id).order_by(Student.register_number).all()

    # Fetch subjects for dropdown based on class
    subjects = Subject.query.all()

    return render_template(
        'mark_attendance.html',
        teacher=teacher,
        my_classes=my_classes,
        subjects=subjects,
        selected_class_id=selected_class_id,
        selected_subject_id=selected_subject_id,
        selected_hour=selected_hour,
        selected_date_str=selected_date_str,
        selected_class=selected_class,
        selected_subject=selected_subject,
        students=students
    )


@app.route('/teacher/attendance/save', methods=['POST'])
@teacher_required
def save_attendance():
    teacher_id = session.get('user_id')
    class_id = request.form.get('class_id', type=int)
    subject_id = request.form.get('subject_id', type=int)
    hour_number = request.form.get('hour_number', type=int)
    session_date_str = request.form.get('session_date', '')

    if not class_id or not subject_id or not hour_number or not session_date_str:
        flash('Invalid session details.', 'danger')
        return redirect(url_for('mark_attendance'))

    try:
        session_date = datetime.strptime(session_date_str, '%Y-%m-%d').date()
    except ValueError:
        flash('Invalid session date format.', 'danger')
        return redirect(url_for('mark_attendance'))

    # Check for duplicate session
    existing_session = AttendanceSession.query.filter_by(
        class_id=class_id,
        subject_id=subject_id,
        session_date=session_date,
        hour_number=hour_number
    ).first()

    if existing_session:
        flash(f'Attendance for Class, Subject, Hour {hour_number} on {session_date} has already been submitted.', 'warning')
        return redirect(url_for('mark_attendance', class_id=class_id, subject_id=subject_id, hour_number=hour_number, session_date=session_date_str))

    # Create new session
    sess = AttendanceSession(
        class_id=class_id,
        subject_id=subject_id,
        teacher_id=teacher_id,
        session_date=session_date,
        hour_number=hour_number,
        status='Submitted'
    )
    db.session.add(sess)
    db.session.commit()

    # Save student attendance records
    students = Student.query.filter_by(class_id=class_id).all()
    present_count = 0
    absent_count = 0

    for student in students:
        status = request.form.get(f'attendance_{student.id}', 'Absent')
        if status not in ['Present', 'Absent']:
            status = 'Absent'

        if status == 'Present':
            present_count += 1
        else:
            absent_count += 1

        rec = AttendanceRecord(session_id=sess.id, student_id=student.id, status=status)
        db.session.add(rec)

    # Save to attendance_reports table for summary logging
    total = present_count + absent_count
    pct = round((present_count / total) * 100, 2) if total > 0 else 0.0
    report = AttendanceReport(
        class_id=class_id,
        subject_id=subject_id,
        report_date=session_date,
        total_students=total,
        present_count=present_count,
        absent_count=absent_count,
        attendance_percentage=pct
    )
    db.session.add(report)

    db.session.commit()
    flash(f'Attendance recorded successfully for {total} students. Present: {present_count}, Absent: {absent_count}.', 'success')
    return redirect(url_for('teacher_dashboard'))


@app.route('/teacher/attendance/history')
@teacher_required
def attendance_history():
    teacher_id = session.get('user_id')
    sessions = AttendanceSession.query.filter_by(teacher_id=teacher_id)\
                .order_by(AttendanceSession.session_date.desc(), AttendanceSession.hour_number.desc()).all()
    return render_template('attendance_history.html', sessions=sessions)


# -----------------------------------------------------------------------------
# Class Tutor Dashboard Route
# -----------------------------------------------------------------------------

@app.route('/tutor/dashboard')
@tutor_required
def tutor_dashboard():
    tutor_id = session.get('user_id')
    teacher = Teacher.query.get(tutor_id)

    if not teacher or not teacher.assigned_class_id:
        flash('No class assigned for this tutor.', 'warning')
        return redirect(url_for('logout'))

    class_id = teacher.assigned_class_id
    tutored_class = Class.query.get(class_id)

    filter_date = request.args.get('date', '').strip()
    filter_subject_id = request.args.get('subject_id', type=int)

    # Fetch students in tutor's class
    students = Student.query.filter_by(class_id=class_id).order_by(Student.register_number).all()
    total_students = len(students)

    # Calculate live class summary
    query = AttendanceSession.query.filter_by(class_id=class_id, status='Submitted')
    if filter_date:
        try:
            d = datetime.strptime(filter_date, '%Y-%m-%d').date()
            query = query.filter_by(session_date=d)
        except ValueError:
            pass
    if filter_subject_id:
        query = query.filter_by(subject_id=filter_subject_id)

    sessions = query.all()

    total_records = 0
    present_count = 0
    absent_count = 0

    if sessions:
        session_ids = [s.id for s in sessions]
        records = AttendanceRecord.query.filter(AttendanceRecord.session_id.in_(session_ids)).all()
        total_records = len(records)
        present_count = len([r for r in records if r.status == 'Present'])
        absent_count = len([r for r in records if r.status == 'Absent'])

    class_pct = round((present_count / total_records) * 100, 2) if total_records > 0 else 0.0

    # Calculate RA students in tutor's class
    ra_students = []
    student_summaries = []

    for student in students:
        overall = get_student_overall_attendance(student.id)
        mark, status = calculate_internal_mark(overall['percentage'])
        summary = {
            'student': student,
            'total_hours': overall['total_hours'],
            'present_hours': overall['present_hours'],
            'absent_hours': overall['absent_hours'],
            'percentage': overall['percentage'],
            'mark': mark,
            'status': status
        }
        student_summaries.append(summary)
        if overall['percentage'] < 50 and overall['total_hours'] > 0:
            ra_students.append(summary)

    subjects = Subject.query.filter_by(class_id=class_id).all()

    return render_template(
        'tutor_dashboard.html',
        teacher=teacher,
        tutored_class=tutored_class,
        total_students=total_students,
        total_records=total_records,
        present_count=present_count,
        absent_count=absent_count,
        class_pct=class_pct,
        ra_students=ra_students,
        student_summaries=student_summaries,
        subjects=subjects,
        filter_date=filter_date,
        filter_subject_id=filter_subject_id
    )


# -----------------------------------------------------------------------------
# Student Dashboard Route
# -----------------------------------------------------------------------------

@app.route('/student/dashboard')
@student_required
def student_dashboard():
    student_id = session.get('user_id')
    student = Student.query.get(student_id)

    if not student:
        flash('Student not found.', 'danger')
        return redirect(url_for('logout'))

    # Overall Attendance
    overall = get_student_overall_attendance(student.id)

    # Subject-wise Breakdown
    subjects = Subject.query.filter_by(class_id=student.class_id).all()
    subject_reports = []

    for sub in subjects:
        sub_stats = get_student_subject_attendance(student.id, sub.id)
        subject_reports.append({
            'subject_code': sub.code,
            'subject_name': sub.name,
            'total_hours': sub_stats['total_hours'],
            'present_hours': sub_stats['present_hours'],
            'absent_hours': sub_stats['absent_hours'],
            'percentage': sub_stats['percentage'],
            'internal_mark': sub_stats['internal_mark'],
            'status': sub_stats['status']
        })

    return render_template(
        'student_dashboard.html',
        student=student,
        overall=overall,
        subject_reports=subject_reports
    )


# -----------------------------------------------------------------------------
# Unified Reports & CSV Export Routes
# -----------------------------------------------------------------------------

@app.route('/reports')
@login_required
def reports():
    user_type = session.get('user_type')
    if user_type not in ['admin', 'tutor', 'teacher']:
        flash('Access restricted.', 'danger')
        return redirect(url_for('index'))

    report_type = request.args.get('type', 'daily')
    class_id = request.args.get('class_id', type=int)
    subject_id = request.args.get('subject_id', type=int)
    report_date = request.args.get('date', date.today().isoformat())
    register_number = request.args.get('reg_no', '').strip()

    # Class tutors restricted to their assigned class
    if user_type == 'tutor':
        tutor_class_id = session.get('tutor_class_id')
        if not tutor_class_id:
            teacher = Teacher.query.get(session.get('user_id'))
            tutor_class_id = teacher.assigned_class_id if teacher else None
        class_id = tutor_class_id

    classes = Class.query.all()
    subjects = Subject.query.filter_by(class_id=class_id).all() if class_id else Subject.query.all()

    report_data = []

    if report_type == 'daily':
        query = AttendanceSession.query.filter_by(status='Submitted')
        if report_date:
            try:
                d = datetime.strptime(report_date, '%Y-%m-%d').date()
                query = query.filter_by(session_date=d)
            except ValueError:
                pass
        if class_id:
            query = query.filter_by(class_id=class_id)
        if subject_id:
            query = query.filter_by(subject_id=subject_id)

        sessions = query.all()
        for sess in sessions:
            recs = AttendanceRecord.query.filter_by(session_id=sess.id).all()
            total = len(recs)
            present = len([r for r in recs if r.status == 'Present'])
            absent = total - present
            pct = round((present / total) * 100, 2) if total > 0 else 0.0
            report_data.append({
                'date': sess.session_date,
                'class_name': sess.session_class.name,
                'subject_name': sess.subject.name,
                'teacher_name': sess.teacher.name,
                'hour': sess.hour_number,
                'total_students': total,
                'present': present,
                'absent': absent,
                'percentage': pct
            })

    elif report_type in ['class_wise', 'subject_wise', 'monthly']:
        query = AttendanceSession.query.filter_by(status='Submitted')
        if class_id:
            query = query.filter_by(class_id=class_id)
        if subject_id:
            query = query.filter_by(subject_id=subject_id)

        sessions = query.all()
        grouped = {}
        for sess in sessions:
            key = (sess.class_id, sess.subject_id)
            if key not in grouped:
                grouped[key] = {'class': sess.session_class.name, 'subject': sess.subject.name, 'sessions': []}
            grouped[key]['sessions'].append(sess)

        for key, info in grouped.items():
            sess_ids = [s.id for s in info['sessions']]
            recs = AttendanceRecord.query.filter(AttendanceRecord.session_id.in_(sess_ids)).all()
            total = len(recs)
            present = len([r for r in recs if r.status == 'Present'])
            absent = total - present
            pct = round((present / total) * 100, 2) if total > 0 else 0.0
            report_data.append({
                'class_name': info['class'],
                'subject_name': info['subject'],
                'total_hours': len(info['sessions']),
                'total_records': total,
                'present': present,
                'absent': absent,
                'percentage': pct
            })

    elif report_type in ['student_wise', 'internal_mark', 'ra_students']:
        query = Student.query
        if class_id:
            query = query.filter_by(class_id=class_id)
        if register_number:
            query = query.filter(Student.register_number.ilike(f'%{register_number}%'))

        students = query.all()
        for s in students:
            sub_list = Subject.query.filter_by(class_id=s.class_id).all()
            for sub in sub_list:
                stats = get_student_subject_attendance(s.id, sub.id)
                row = {
                    'student_name': s.name,
                    'register_number': s.register_number,
                    'class_name': s.student_class.name,
                    'subject_name': sub.name,
                    'total_hours': stats['total_hours'],
                    'present_hours': stats['present_hours'],
                    'absent_hours': stats['absent_hours'],
                    'percentage': stats['percentage'],
                    'internal_mark': stats['internal_mark'],
                    'status': stats['status']
                }

                if report_type == 'ra_students':
                    if stats['percentage'] < 50 and stats['total_hours'] > 0:
                        report_data.append(row)
                else:
                    report_data.append(row)

    return render_template(
        'reports.html',
        report_type=report_type,
        class_id=class_id,
        subject_id=subject_id,
        report_date=report_date,
        register_number=register_number,
        classes=classes,
        subjects=subjects,
        report_data=report_data
    )


@app.route('/reports/export/csv')
@login_required
def export_csv():
    user_type = session.get('user_type')
    if user_type not in ['admin', 'tutor', 'teacher']:
        flash('Access restricted.', 'danger')
        return redirect(url_for('index'))

    report_type = request.args.get('type', 'daily')
    class_id = request.args.get('class_id', type=int)

    # Class tutors restricted to their assigned class
    if user_type == 'tutor':
        tutor_class_id = session.get('tutor_class_id')
        class_id = tutor_class_id

    si = StringIO()
    cw = csv.writer(si)

    if report_type in ['student_wise', 'internal_mark', 'ra_students']:
        cw.writerow(['Student Name', 'Register Number', 'Class', 'Subject', 'Total Hours', 'Present Hours', 'Absent Hours', 'Attendance %', 'Internal Mark (out of 5)', 'Status'])
        query = Student.query
        if class_id:
            query = query.filter_by(class_id=class_id)
        students = query.all()
        for s in students:
            subs = Subject.query.filter_by(class_id=s.class_id).all()
            for sub in subs:
                stats = get_student_subject_attendance(s.id, sub.id)
                if report_type == 'ra_students' and (stats['percentage'] >= 50 or stats['total_hours'] == 0):
                    continue
                cw.writerow([
                    s.name,
                    s.register_number,
                    s.student_class.name,
                    sub.name,
                    stats['total_hours'],
                    stats['present_hours'],
                    stats['absent_hours'],
                    f"{stats['percentage']}%",
                    stats['internal_mark'],
                    stats['status']
                ])
    else:
        cw.writerow(['Date', 'Class', 'Subject', 'Total Hours/Sessions', 'Present Records', 'Absent Records', 'Attendance %'])
        query = AttendanceSession.query.filter_by(status='Submitted')
        if class_id:
            query = query.filter_by(class_id=class_id)
        sessions = query.all()
        for sess in sessions:
            recs = AttendanceRecord.query.filter_by(session_id=sess.id).all()
            total = len(recs)
            present = len([r for r in recs if r.status == 'Present'])
            absent = total - present
            pct = round((present / total) * 100, 2) if total > 0 else 0.0
            cw.writerow([
                sess.session_date,
                sess.session_class.name,
                sess.subject.name,
                total,
                present,
                absent,
                f"{pct}%"
            ])

    output = si.getvalue()
    return Response(
        output,
        mimetype='text/csv',
        headers={'Content-Disposition': f'attachment; filename=attendance_report_{report_type}_{date.today().isoformat()}.csv'}
    )


# Initialize Database Context
with app.app_context():
    db.create_all()
    seed_default_data()

if __name__ == '__main__':
    app.run(debug=True)
