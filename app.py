import os
import csv
import io
from datetime import datetime, date
from functools import wraps
from flask import Flask, render_template, request, redirect, url_for, flash, session, Response, make_response
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'college_attendance_secret_key_2025_mca')

# Database configuration: Default to MySQL URI, fallback to SQLite when USE_SQLITE=1
MYSQL_URI = os.environ.get('DATABASE_URL', 'mysql+pymysql://root:@localhost/college_attendance_db')
SQLITE_URI = 'sqlite:///' + os.path.join(os.path.abspath(os.path.dirname(__file__)), 'college_attendance.db')

use_sqlite = os.environ.get('USE_SQLITE') == '1'
app.config['SQLALCHEMY_DATABASE_URI'] = SQLITE_URI if use_sqlite else MYSQL_URI
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

# -----------------------------------------------------------------------------
# Models
# -----------------------------------------------------------------------------

class Admin(db.Model):
    __tablename__ = 'admins'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), unique=True, nullable=False)
    email = db.Column(db.String(100), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)


class Teacher(db.Model):
    __tablename__ = 'teachers'
    id = db.Column(db.Integer, primary_key=True)
    teacher_id_code = db.Column(db.String(50), unique=True, nullable=False)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(100), unique=True, nullable=False)
    department = db.Column(db.String(100), nullable=False)
    phone = db.Column(db.String(20), nullable=True)
    password_hash = db.Column(db.String(255), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    tutored_class = db.relationship('ClassModel', backref='tutor', uselist=False, foreign_keys='ClassModel.tutor_id')
    timetable_entries = db.relationship('Timetable', backref='teacher', lazy=True)
    sessions = db.relationship('AttendanceSession', backref='teacher', lazy=True)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)


class ClassModel(db.Model):
    __tablename__ = 'classes'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), unique=True, nullable=False) # e.g., BCA I, BCA II, BCA III, MCA I, MCA II
    code = db.Column(db.String(20), unique=True, nullable=False)
    tutor_id = db.Column(db.Integer, db.ForeignKey('teachers.id'), nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    students = db.relationship('Student', backref='student_class', lazy=True, cascade="all, delete-orphan")
    subjects = db.relationship('Subject', backref='subject_class', lazy=True, cascade="all, delete-orphan")
    timetable_entries = db.relationship('Timetable', backref='timetable_class', lazy=True, cascade="all, delete-orphan")
    sessions = db.relationship('AttendanceSession', backref='session_class', lazy=True, cascade="all, delete-orphan")


class Student(db.Model):
    __tablename__ = 'students'
    id = db.Column(db.Integer, primary_key=True)
    register_number = db.Column(db.String(50), unique=True, nullable=False)
    name = db.Column(db.String(100), nullable=False)
    class_id = db.Column(db.Integer, db.ForeignKey('classes.id'), nullable=False)
    email = db.Column(db.String(100), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    attendance_records = db.relationship('AttendanceRecord', backref='student', lazy=True, cascade="all, delete-orphan")

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

    timetable_entries = db.relationship('Timetable', backref='subject', lazy=True, cascade="all, delete-orphan")
    sessions = db.relationship('AttendanceSession', backref='subject', lazy=True, cascade="all, delete-orphan")


class Timetable(db.Model):
    __tablename__ = 'timetable'
    id = db.Column(db.Integer, primary_key=True)
    class_id = db.Column(db.Integer, db.ForeignKey('classes.id'), nullable=False)
    day = db.Column(db.String(20), nullable=False) # Monday - Friday
    hour_number = db.Column(db.Integer, nullable=False) # 1 to 5
    subject_id = db.Column(db.Integer, db.ForeignKey('subjects.id'), nullable=False)
    teacher_id = db.Column(db.Integer, db.ForeignKey('teachers.id'), nullable=False)
    start_time = db.Column(db.String(20), default='09:00 AM')
    end_time = db.Column(db.String(20), default='10:00 AM')
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    sessions = db.relationship('AttendanceSession', backref='timetable_ref', lazy=True)

    __table_args__ = (
        db.UniqueConstraint('class_id', 'day', 'hour_number', name='unique_class_day_hour'),
        db.UniqueConstraint('teacher_id', 'day', 'hour_number', name='unique_teacher_day_hour'),
    )


class AttendanceSession(db.Model):
    __tablename__ = 'attendance_sessions'
    id = db.Column(db.Integer, primary_key=True)
    class_id = db.Column(db.Integer, db.ForeignKey('classes.id'), nullable=False)
    subject_id = db.Column(db.Integer, db.ForeignKey('subjects.id'), nullable=False)
    teacher_id = db.Column(db.Integer, db.ForeignKey('teachers.id'), nullable=False)
    date = db.Column(db.Date, nullable=False)
    hour_number = db.Column(db.Integer, nullable=False) # 1 to 5
    timetable_id = db.Column(db.Integer, db.ForeignKey('timetable.id'), nullable=True)
    submitted_at = db.Column(db.DateTime, default=datetime.utcnow)
    status = db.Column(db.String(20), default='Submitted')

    records = db.relationship('AttendanceRecord', backref='session', lazy=True, cascade="all, delete-orphan")

    __table_args__ = (
        db.UniqueConstraint('class_id', 'subject_id', 'date', 'hour_number', name='unique_session_class_subject_date_hour'),
    )


class AttendanceRecord(db.Model):
    __tablename__ = 'attendance_records'
    id = db.Column(db.Integer, primary_key=True)
    session_id = db.Column(db.Integer, db.ForeignKey('attendance_sessions.id'), nullable=False)
    student_id = db.Column(db.Integer, db.ForeignKey('students.id'), nullable=False)
    status = db.Column(db.String(10), nullable=False) # 'Present' or 'Absent'
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    __table_args__ = (
        db.UniqueConstraint('session_id', 'student_id', name='unique_session_student'),
    )


class InternalMarkRule(db.Model):
    __tablename__ = 'internal_mark_rules'
    id = db.Column(db.Integer, primary_key=True)
    min_percentage = db.Column(db.Float, nullable=False)
    max_percentage = db.Column(db.Float, nullable=False)
    mark = db.Column(db.Integer, nullable=False) # 0 for RA or 1..5
    label = db.Column(db.String(50), nullable=False)


# -----------------------------------------------------------------------------
# Seeding Helper
# -----------------------------------------------------------------------------

def seed_default_data():
    """Seeds initial default data if database is empty."""
    if Admin.query.count() == 0:
        admin = Admin(username='admin', email='admin@college.edu')
        admin.set_password('admin123')
        db.session.add(admin)

    if InternalMarkRule.query.count() == 0:
        rules = [
            InternalMarkRule(min_percentage=90.0, max_percentage=100.0, mark=5, label='5 Marks (Outstanding)'),
            InternalMarkRule(min_percentage=80.0, max_percentage=89.99, mark=4, label='4 Marks (Very Good)'),
            InternalMarkRule(min_percentage=70.0, max_percentage=79.99, mark=3, label='3 Marks (Good)'),
            InternalMarkRule(min_percentage=60.0, max_percentage=69.99, mark=2, label='2 Marks (Satisfactory)'),
            InternalMarkRule(min_percentage=50.0, max_percentage=59.99, mark=1, label='1 Mark (Pass Margin)'),
            InternalMarkRule(min_percentage=0.0, max_percentage=49.99, mark=0, label='RA - Redo Attendance'),
        ]
        db.session.add_all(rules)

    if Teacher.query.count() == 0:
        t1 = Teacher(teacher_id_code='TCH101', name='Dr. Aris Thorne', email='aris@college.edu', department='Computer Applications', phone='9876543210')
        t1.set_password('teacher123')
        t2 = Teacher(teacher_id_code='TCH102', name='Prof. Sarah Lin', email='sarah@college.edu', department='Computer Applications', phone='9876543211')
        t2.set_password('teacher123')
        t3 = Teacher(teacher_id_code='TCH103', name='Dr. Rajesh Kumar', email='rajesh@college.edu', department='Computer Applications', phone='9876543212')
        t3.set_password('teacher123')
        t4 = Teacher(teacher_id_code='TCH104', name='Prof. Elena Rostova', email='elena@college.edu', department='Computer Applications', phone='9876543213')
        t4.set_password('teacher123')
        t5 = Teacher(teacher_id_code='TCH105', name='Dr. Michael Chang', email='michael@college.edu', department='Computer Applications', phone='9876543214')
        t5.set_password('teacher123')
        db.session.add_all([t1, t2, t3, t4, t5])
        db.session.commit()

    if ClassModel.query.count() == 0:
        teachers = Teacher.query.order_by(Teacher.id).all()
        c1 = ClassModel(name='BCA I', code='BCA1', tutor_id=teachers[0].id if len(teachers)>0 else None)
        c2 = ClassModel(name='BCA II', code='BCA2', tutor_id=teachers[1].id if len(teachers)>1 else None)
        c3 = ClassModel(name='BCA III', code='BCA3', tutor_id=teachers[2].id if len(teachers)>2 else None)
        c4 = ClassModel(name='MCA I', code='MCA1', tutor_id=teachers[3].id if len(teachers)>3 else None)
        c5 = ClassModel(name='MCA II', code='MCA2', tutor_id=teachers[4].id if len(teachers)>4 else None)
        db.session.add_all([c1, c2, c3, c4, c5])
        db.session.commit()

    if Subject.query.count() == 0:
        classes_map = {c.name: c.id for c in ClassModel.query.all()}
        subjects = [
            Subject(code='BCA101', name='Programming in C', class_id=classes_map.get('BCA I')),
            Subject(code='BCA102', name='Digital Fundamentals', class_id=classes_map.get('BCA I')),
            Subject(code='BCA201', name='Data Structures', class_id=classes_map.get('BCA II')),
            Subject(code='BCA202', name='Database Systems', class_id=classes_map.get('BCA II')),
            Subject(code='BCA301', name='Web Technologies', class_id=classes_map.get('BCA III')),
            Subject(code='BCA302', name='Software Engineering', class_id=classes_map.get('BCA III')),
            Subject(code='MCA101', name='Python Web Development', class_id=classes_map.get('MCA I')),
            Subject(code='MCA102', name='Advanced Database Systems', class_id=classes_map.get('MCA I')),
            Subject(code='MCA201', name='Cloud Computing & DevOps', class_id=classes_map.get('MCA II')),
            Subject(code='MCA202', name='Artificial Intelligence', class_id=classes_map.get('MCA II')),
        ]
        db.session.add_all(subjects)
        db.session.commit()

    if Student.query.count() == 0:
        classes_map = {c.name: c.id for c in ClassModel.query.all()}
        s_list = [
            ('2024BCA001', 'Alan Turing', 'BCA I', 'alan@student.edu'),
            ('2024BCA002', 'Ada Lovelace', 'BCA I', 'ada@student.edu'),
            ('2023BCA001', 'Grace Hopper', 'BCA II', 'grace@student.edu'),
            ('2022BCA001', 'Dennis Ritchie', 'BCA III', 'dennis@student.edu'),
            ('2024MCA001', 'Guido van Rossum', 'MCA I', 'guido@student.edu'),
            ('2024MCA002', 'Linus Torvalds', 'MCA I', 'linus@student.edu'),
            ('2024MCA003', 'Tim Berners-Lee', 'MCA I', 'tim@student.edu'),
            ('2023MCA001', 'Margaret Hamilton', 'MCA II', 'margaret@student.edu'),
        ]
        for reg, name, cname, email in s_list:
            stu = Student(register_number=reg, name=name, class_id=classes_map.get(cname), email=email)
            stu.set_password('student123')
            db.session.add(stu)
        db.session.commit()

    if Timetable.query.count() == 0:
        mca1 = ClassModel.query.filter_by(name='MCA I').first()
        if mca1:
            subs = Subject.query.filter_by(class_id=mca1.id).all()
            teachers = Teacher.query.all()
            if len(subs) >= 2 and len(teachers) >= 2:
                t_entries = [
                    Timetable(class_id=mca1.id, day='Monday', hour_number=1, subject_id=subs[0].id, teacher_id=teachers[3].id, start_time='09:00 AM', end_time='10:00 AM'),
                    Timetable(class_id=mca1.id, day='Monday', hour_number=2, subject_id=subs[1].id, teacher_id=teachers[1].id, start_time='10:00 AM', end_time='11:00 AM'),
                    Timetable(class_id=mca1.id, day='Monday', hour_number=3, subject_id=subs[0].id, teacher_id=teachers[3].id, start_time='11:15 AM', end_time='12:15 PM'),
                    Timetable(class_id=mca1.id, day='Monday', hour_number=4, subject_id=subs[1].id, teacher_id=teachers[1].id, start_time='01:15 PM', end_time='02:15 PM'),
                    Timetable(class_id=mca1.id, day='Monday', hour_number=5, subject_id=subs[0].id, teacher_id=teachers[3].id, start_time='02:15 PM', end_time='03:15 PM'),
                ]
                db.session.add_all(t_entries)
                db.session.commit()


# -----------------------------------------------------------------------------
# Calculation Helpers
# -----------------------------------------------------------------------------

def calculate_internal_mark(percentage):
    """Calculates internal mark out of 5 based on percentage rules."""
    rules = InternalMarkRule.query.order_by(InternalMarkRule.min_percentage.desc()).all()
    for rule in rules:
        if percentage >= rule.min_percentage:
            if rule.mark == 0:
                return 'RA', 'RA - Attendance Below 50%'
            return rule.mark, f'{rule.mark} / 5'
    return 'RA', 'RA - Attendance Below 50%'


def get_student_subject_attendance(student_id, subject_id):
    """Calculates attendance stats for a specific student and subject."""
    student = Student.query.get(student_id)
    if not student:
        return None

    # Find all submitted sessions for student's class and subject
    sessions = AttendanceSession.query.filter_by(
        class_id=student.class_id,
        subject_id=subject_id,
        status='Submitted'
    ).all()

    total_hours = len(sessions)
    if total_hours == 0:
        return {
            'total_hours': 0,
            'present_hours': 0,
            'absent_hours': 0,
            'percentage': 0.0,
            'internal_mark': 0,
            'status_label': 'No Sessions Recorded',
            'is_ra': False
        }

    session_ids = [s.id for s in sessions]
    records = AttendanceRecord.query.filter(
        AttendanceRecord.session_id.in_(session_ids),
        AttendanceRecord.student_id == student_id
    ).all()

    present_hours = sum(1 for r in records if r.status == 'Present')
    absent_hours = total_hours - present_hours
    percentage = round((present_hours / total_hours) * 100, 2)
    mark, label = calculate_internal_mark(percentage)

    return {
        'total_hours': total_hours,
        'present_hours': present_hours,
        'absent_hours': absent_hours,
        'percentage': percentage,
        'internal_mark': mark,
        'status_label': label,
        'is_ra': percentage < 50.0
    }


def get_student_overall_attendance(student_id):
    """Calculates overall attendance stats for a student across all subjects."""
    student = Student.query.get(student_id)
    if not student:
        return None

    subjects = Subject.query.filter_by(class_id=student.class_id).all()
    subject_stats = []
    total_present_all = 0
    total_hours_all = 0

    for sub in subjects:
        stats = get_student_subject_attendance(student_id, sub.id)
        stats['subject'] = sub
        subject_stats.append(stats)
        total_present_all += stats['present_hours']
        total_hours_all += stats['total_hours']

    overall_percentage = round((total_present_all / total_hours_all) * 100, 2) if total_hours_all > 0 else 0.0
    overall_mark, overall_label = calculate_internal_mark(overall_percentage)

    return {
        'student': student,
        'overall_total_hours': total_hours_all,
        'overall_present_hours': total_present_all,
        'overall_absent_hours': total_hours_all - total_present_all,
        'overall_percentage': overall_percentage,
        'overall_internal_mark': overall_mark,
        'overall_label': overall_label,
        'is_ra': overall_percentage < 50.0 if total_hours_all > 0 else False,
        'subject_stats': subject_stats
    }


# -----------------------------------------------------------------------------
# Auth Decorators
# -----------------------------------------------------------------------------

def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'role' not in session:
            flash('Please log in to access this page.', 'warning')
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function


def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if session.get('role') != 'admin':
            flash('Administrator privilege required.', 'danger')
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function


def teacher_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if session.get('role') not in ['teacher', 'tutor']:
            flash('Teacher login required.', 'danger')
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function


def tutor_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if session.get('role') not in ['teacher', 'tutor']:
            flash('Class Tutor login required.', 'danger')
            return redirect(url_for('login'))

        # Check if teacher is assigned as tutor
        teacher_id = session.get('user_id')
        tutored_class = ClassModel.query.filter_by(tutor_id=teacher_id).first()
        if not tutored_class:
            flash('You are not currently assigned as a Class Tutor for any class.', 'warning')
            return redirect(url_for('teacher_dashboard'))
        return f(*args, **kwargs)
    return decorated_function


def student_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if session.get('role') != 'student':
            flash('Student access required.', 'danger')
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function


# -----------------------------------------------------------------------------
# Auth Routes
# -----------------------------------------------------------------------------

@app.route('/')
def index():
    if 'role' in session:
        role = session['role']
        if role == 'admin':
            return redirect(url_for('admin_dashboard'))
        elif role in ['teacher', 'tutor']:
            return redirect(url_for('teacher_dashboard'))
        elif role == 'student':
            return redirect(url_for('student_dashboard'))
    return redirect(url_for('login'))


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        role = request.form.get('role')
        identifier = request.form.get('identifier', '').strip()
        password = request.form.get('password', '')

        if not role or not identifier or not password:
            flash('All login fields are required.', 'danger')
            return render_template('login.html')

        if role == 'admin':
            admin = Admin.query.filter((Admin.username == identifier) | (Admin.email == identifier)).first()
            if admin and admin.check_password(password):
                session.clear()
                session['role'] = 'admin'
                session['user_id'] = admin.id
                session['user_name'] = admin.username
                flash('Welcome to Admin Portal.', 'success')
                return redirect(url_for('admin_dashboard'))
            else:
                flash('Invalid Admin Username or Password.', 'danger')

        elif role in ['teacher', 'tutor']:
            teacher = Teacher.query.filter(
                (Teacher.teacher_id_code == identifier) | (Teacher.email == identifier)
            ).first()
            if teacher and teacher.check_password(password):
                session.clear()
                is_tutor = ClassModel.query.filter_by(tutor_id=teacher.id).first() is not None
                session['role'] = 'tutor' if (role == 'tutor' and is_tutor) else 'teacher'
                session['is_tutor'] = is_tutor
                session['user_id'] = teacher.id
                session['user_name'] = teacher.name
                flash(f'Welcome, {teacher.name}!', 'success')
                if session['role'] == 'tutor':
                    return redirect(url_for('tutor_dashboard'))
                return redirect(url_for('teacher_dashboard'))
            else:
                flash('Invalid Teacher ID / Email or Password.', 'danger')

        elif role == 'student':
            student = Student.query.filter(
                (Student.register_number == identifier) | (Student.email == identifier)
            ).first()
            if student and student.check_password(password):
                session.clear()
                session['role'] = 'student'
                session['user_id'] = student.id
                session['user_name'] = student.name
                session['register_number'] = student.register_number
                flash(f'Welcome back, {student.name}!', 'success')
                return redirect(url_for('student_dashboard'))
            else:
                flash('Invalid Register Number / Email or Password.', 'danger')

    return render_template('login.html')


@app.route('/logout')
def logout():
    session.clear()
    flash('You have been logged out successfully.', 'info')
    return redirect(url_for('login'))


# -----------------------------------------------------------------------------
# Admin Dashboard & Management Routes
# -----------------------------------------------------------------------------

@app.route('/admin/dashboard')
@admin_required
def admin_dashboard():
    total_students = Student.query.count()
    total_teachers = Teacher.query.count()
    total_classes = ClassModel.query.count()

    today = date.today()
    today_sessions = AttendanceSession.query.filter_by(date=today, status='Submitted').all()
    today_attendance_count = len(today_sessions)

    # RA Students calculation
    students = Student.query.all()
    ra_students_count = 0
    for s in students:
        overall = get_student_overall_attendance(s.id)
        if overall and overall['is_ra']:
            ra_students_count += 1

    students_list = Student.query.order_by(Student.register_number).all()
    teachers_list = Teacher.query.order_by(Teacher.name).all()
    classes_list = ClassModel.query.order_by(ClassModel.name).all()
    subjects_list = Subject.query.all()
    timetable_list = Timetable.query.order_by(Timetable.day, Timetable.hour_number).all()
    rules_list = InternalMarkRule.query.order_by(InternalMarkRule.min_percentage.desc()).all()

    return render_template(
        'admin_dashboard.html',
        total_students=total_students,
        total_teachers=total_teachers,
        total_classes=total_classes,
        today_attendance_count=today_attendance_count,
        ra_students_count=ra_students_count,
        students=students_list,
        teachers=teachers_list,
        classes=classes_list,
        subjects=subjects_list,
        timetable=timetable_list,
        rules=rules_list,
        today_date=today.strftime('%Y-%m-%d')
    )


# Admin - Student Operations
@app.route('/admin/student/add', methods=['POST'])
@admin_required
def admin_add_student():
    reg_num = request.form.get('register_number', '').strip().upper()
    name = request.form.get('name', '').strip()
    class_id = request.form.get('class_id', type=int)
    email = request.form.get('email', '').strip().lower()
    password = request.form.get('password', 'student123')

    if not reg_num or not name or not class_id or not email:
        flash('All student fields are required.', 'danger')
        return redirect(url_for('admin_dashboard'))

    existing = Student.query.filter(
        (Student.register_number == reg_num) | (Student.email == email)
    ).first()
    if existing:
        flash('Student with this Register Number or Email already exists.', 'danger')
        return redirect(url_for('admin_dashboard'))

    student = Student(register_number=reg_num, name=name, class_id=class_id, email=email)
    student.set_password(password)
    db.session.add(student)
    db.session.commit()
    flash(f'Student "{name}" ({reg_num}) added successfully.', 'success')
    return redirect(url_for('admin_dashboard'))


@app.route('/admin/student/edit/<int:student_id>', methods=['POST'])
@admin_required
def admin_edit_student(student_id):
    student = Student.query.get_or_404(student_id)
    student.register_number = request.form.get('register_number', '').strip().upper()
    student.name = request.form.get('name', '').strip()
    student.class_id = request.form.get('class_id', type=int)
    student.email = request.form.get('email', '').strip().lower()

    new_pass = request.form.get('password', '').strip()
    if new_pass:
        student.set_password(new_pass)

    db.session.commit()
    flash(f'Student {student.name} updated successfully.', 'success')
    return redirect(url_for('admin_dashboard'))


@app.route('/admin/student/delete/<int:student_id>', methods=['POST'])
@admin_required
def admin_delete_student(student_id):
    student = Student.query.get_or_404(student_id)
    db.session.delete(student)
    db.session.commit()
    flash('Student deleted successfully.', 'info')
    return redirect(url_for('admin_dashboard'))


# Admin - Teacher Operations
@app.route('/admin/teacher/add', methods=['POST'])
@admin_required
def admin_add_teacher():
    teacher_id_code = request.form.get('teacher_id_code', '').strip().upper()
    name = request.form.get('name', '').strip()
    email = request.form.get('email', '').strip().lower()
    department = request.form.get('department', '').strip()
    phone = request.form.get('phone', '').strip()
    password = request.form.get('password', 'teacher123')

    existing = Teacher.query.filter(
        (Teacher.teacher_id_code == teacher_id_code) | (Teacher.email == email)
    ).first()
    if existing:
        flash('Teacher with this Teacher ID or Email already exists.', 'danger')
        return redirect(url_for('admin_dashboard'))

    teacher = Teacher(
        teacher_id_code=teacher_id_code,
        name=name,
        email=email,
        department=department,
        phone=phone
    )
    teacher.set_password(password)
    db.session.add(teacher)
    db.session.commit()
    flash(f'Teacher "{name}" added successfully.', 'success')
    return redirect(url_for('admin_dashboard'))


@app.route('/admin/teacher/edit/<int:teacher_id>', methods=['POST'])
@admin_required
def admin_edit_teacher(teacher_id):
    teacher = Teacher.query.get_or_404(teacher_id)
    teacher.teacher_id_code = request.form.get('teacher_id_code', '').strip().upper()
    teacher.name = request.form.get('name', '').strip()
    teacher.email = request.form.get('email', '').strip().lower()
    teacher.department = request.form.get('department', '').strip()
    teacher.phone = request.form.get('phone', '').strip()

    new_pass = request.form.get('password', '').strip()
    if new_pass:
        teacher.set_password(new_pass)

    db.session.commit()
    flash(f'Teacher "{teacher.name}" updated successfully.', 'success')
    return redirect(url_for('admin_dashboard'))


@app.route('/admin/teacher/delete/<int:teacher_id>', methods=['POST'])
@admin_required
def admin_delete_teacher(teacher_id):
    teacher = Teacher.query.get_or_404(teacher_id)
    db.session.delete(teacher)
    db.session.commit()
    flash('Teacher deleted successfully.', 'info')
    return redirect(url_for('admin_dashboard'))


# Admin - Class Tutor Assignment
@app.route('/admin/class/assign_tutor', methods=['POST'])
@admin_required
def admin_assign_tutor():
    class_id = request.form.get('class_id', type=int)
    tutor_id = request.form.get('tutor_id', type=int)

    cls = ClassModel.query.get_or_404(class_id)
    cls.tutor_id = tutor_id if tutor_id and tutor_id > 0 else None
    db.session.commit()

    flash(f'Class tutor for {cls.name} updated.', 'success')
    return redirect(url_for('admin_dashboard'))


# Admin - Subject Operations
@app.route('/admin/subject/add', methods=['POST'])
@admin_required
def admin_add_subject():
    code = request.form.get('code', '').strip().upper()
    name = request.form.get('name', '').strip()
    class_id = request.form.get('class_id', type=int)

    if not code or not name or not class_id:
        flash('Subject code, name and class are required.', 'danger')
        return redirect(url_for('admin_dashboard'))

    sub = Subject(code=code, name=name, class_id=class_id)
    db.session.add(sub)
    db.session.commit()
    flash(f'Subject "{name}" added successfully.', 'success')
    return redirect(url_for('admin_dashboard'))


@app.route('/admin/subject/delete/<int:subject_id>', methods=['POST'])
@admin_required
def admin_delete_subject(subject_id):
    sub = Subject.query.get_or_404(subject_id)
    db.session.delete(sub)
    db.session.commit()
    flash('Subject deleted successfully.', 'info')
    return redirect(url_for('admin_dashboard'))


# Admin - Timetable Operations with Validation
@app.route('/admin/timetable/add', methods=['POST'])
@admin_required
def admin_add_timetable():
    class_id = request.form.get('class_id', type=int)
    day = request.form.get('day', '').strip()
    hour_number = request.form.get('hour_number', type=int)
    subject_id = request.form.get('subject_id', type=int)
    teacher_id = request.form.get('teacher_id', type=int)
    start_time = request.form.get('start_time', '09:00 AM').strip()
    end_time = request.form.get('end_time', '10:00 AM').strip()

    if not class_id or not day or not hour_number or not subject_id or not teacher_id:
        flash('All timetable fields are required.', 'danger')
        return redirect(url_for('admin_dashboard'))

    # Check validation 1: Class already has subject in that day/hour
    class_conflict = Timetable.query.filter_by(
        class_id=class_id, day=day, hour_number=hour_number
    ).first()
    if class_conflict:
        flash(f'Timetable conflict: Class already has a session on {day} Hour {hour_number}.', 'danger')
        return redirect(url_for('admin_dashboard'))

    # Check validation 2: Teacher is already assigned to another class in that day/hour
    teacher_conflict = Timetable.query.filter_by(
        teacher_id=teacher_id, day=day, hour_number=hour_number
    ).first()
    if teacher_conflict:
        flash(f'Teacher conflict: Teacher is already teaching another class on {day} Hour {hour_number}.', 'danger')
        return redirect(url_for('admin_dashboard'))

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
    flash('Timetable slot added successfully.', 'success')
    return redirect(url_for('admin_dashboard'))


@app.route('/admin/timetable/delete/<int:timetable_id>', methods=['POST'])
@admin_required
def admin_delete_timetable(timetable_id):
    tt = Timetable.query.get_or_404(timetable_id)
    db.session.delete(tt)
    db.session.commit()
    flash('Timetable entry deleted successfully.', 'info')
    return redirect(url_for('admin_dashboard'))


# Admin - Rule Management
@app.route('/admin/rule/update/<int:rule_id>', methods=['POST'])
@admin_required
def admin_update_rule(rule_id):
    rule = InternalMarkRule.query.get_or_404(rule_id)
    rule.min_percentage = request.form.get('min_percentage', type=float)
    rule.max_percentage = request.form.get('max_percentage', type=float)
    rule.mark = request.form.get('mark', type=int)
    rule.label = request.form.get('label', '').strip()
    db.session.commit()
    flash('Internal mark rule updated.', 'success')
    return redirect(url_for('admin_dashboard'))


# -----------------------------------------------------------------------------
# Teacher Routes
# -----------------------------------------------------------------------------

@app.route('/teacher/dashboard')
@teacher_required
def teacher_dashboard():
    teacher_id = session.get('user_id')
    teacher = Teacher.query.get_or_404(teacher_id)

    selected_day = request.args.get('day', datetime.now().strftime('%A'))
    if selected_day not in ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday']:
        selected_day = 'Monday'

    # Get teacher's assigned timetable for the day
    my_schedule = Timetable.query.filter_by(
        teacher_id=teacher_id,
        day=selected_day
    ).order_by(Timetable.hour_number).all()

    # Get recent submitted sessions
    recent_sessions = AttendanceSession.query.filter_by(
        teacher_id=teacher_id
    ).order_by(AttendanceSession.submitted_at.desc()).limit(10).all()

    today_str = date.today().strftime('%Y-%m-%d')

    return render_template(
        'teacher_dashboard.html',
        teacher=teacher,
        schedule=my_schedule,
        selected_day=selected_day,
        recent_sessions=recent_sessions,
        today_date=today_str
    )


@app.route('/teacher/mark_attendance/<int:timetable_id>', methods=['GET', 'POST'])
@teacher_required
def mark_attendance(timetable_id):
    teacher_id = session.get('user_id')
    timetable_slot = Timetable.query.get_or_404(timetable_id)

    # Validate that teacher is assigned to this slot
    if timetable_slot.teacher_id != teacher_id:
        flash('You are not authorized to mark attendance for this slot.', 'danger')
        return redirect(url_for('teacher_dashboard'))

    selected_date_str = request.args.get('date', date.today().strftime('%Y-%m-%d'))
    try:
        session_date = datetime.strptime(selected_date_str, '%Y-%m-%d').date()
    except ValueError:
        session_date = date.today()

    # Check if attendance already submitted for this date/class/subject/hour
    existing_session = AttendanceSession.query.filter_by(
        class_id=timetable_slot.class_id,
        subject_id=timetable_slot.subject_id,
        date=session_date,
        hour_number=timetable_slot.hour_number
    ).first()

    students = Student.query.filter_by(class_id=timetable_slot.class_id).order_by(Student.register_number).all()

    if request.method == 'POST':
        # Create or update session
        if existing_session:
            session_obj = existing_session
            session_obj.submitted_at = datetime.utcnow()
        else:
            session_obj = AttendanceSession(
                class_id=timetable_slot.class_id,
                subject_id=timetable_slot.subject_id,
                teacher_id=teacher_id,
                date=session_date,
                hour_number=timetable_slot.hour_number,
                timetable_id=timetable_slot.id,
                status='Submitted'
            )
            db.session.add(session_obj)
            db.session.flush()

        # Update student records
        for student in students:
            status = request.form.get(f'status_{student.id}', 'Absent')
            record = AttendanceRecord.query.filter_by(
                session_id=session_obj.id,
                student_id=student.id
            ).first()

            if record:
                record.status = status
            else:
                record = AttendanceRecord(
                    session_id=session_obj.id,
                    student_id=student.id,
                    status=status
                )
                db.session.add(record)

        db.session.commit()
        flash(f'Attendance for {timetable_slot.subject.name} (Hour {timetable_slot.hour_number}) submitted successfully!', 'success')
        return redirect(url_for('teacher_dashboard'))

    # Load existing status map if updating
    status_map = {}
    if existing_session:
        records = AttendanceRecord.query.filter_by(session_id=existing_session.id).all()
        for r in records:
            status_map[r.student_id] = r.status

    return render_template(
        'mark_attendance.html',
        slot=timetable_slot,
        students=students,
        session_date=session_date.strftime('%Y-%m-%d'),
        status_map=status_map,
        existing_session=existing_session
    )


# -----------------------------------------------------------------------------
# Class Tutor Routes
# -----------------------------------------------------------------------------

@app.route('/tutor/dashboard')
@tutor_required
def tutor_dashboard():
    teacher_id = session.get('user_id')
    tutored_class = ClassModel.query.filter_by(tutor_id=teacher_id).first()

    selected_subject_id = request.args.get('subject_id', type=int)
    date_filter = request.args.get('date', '')

    students = Student.query.filter_by(class_id=tutored_class.id).order_by(Student.register_number).all()
    subjects = Subject.query.filter_by(class_id=tutored_class.id).all()

    # Calculate student stats
    reports = []
    total_class_present_hours = 0
    total_class_hours = 0
    ra_count = 0

    for s in students:
        if selected_subject_id:
            sub_stat = get_student_subject_attendance(s.id, selected_subject_id)
            sub = Subject.query.get(selected_subject_id)
            sub_stat['student'] = s
            sub_stat['subject'] = sub
            reports.append(sub_stat)
            total_class_present_hours += sub_stat['present_hours']
            total_class_hours += sub_stat['total_hours']
            if sub_stat['is_ra']:
                ra_count += 1
        else:
            overall = get_student_overall_attendance(s.id)
            reports.append(overall)
            total_class_present_hours += overall['overall_present_hours']
            total_class_hours += overall['overall_total_hours']
            if overall['is_ra']:
                ra_count += 1

    class_avg_percentage = round((total_class_present_hours / total_class_hours) * 100, 2) if total_class_hours > 0 else 0.0

    return render_template(
        'tutor_dashboard.html',
        tutored_class=tutored_class,
        students=students,
        subjects=subjects,
        reports=reports,
        selected_subject_id=selected_subject_id,
        total_students=len(students),
        class_avg_percentage=class_avg_percentage,
        ra_count=ra_count,
        date_filter=date_filter
    )


# -----------------------------------------------------------------------------
# Student Routes
# -----------------------------------------------------------------------------

@app.route('/student/dashboard')
@student_required
def student_dashboard():
    student_id = session.get('user_id')
    overall_summary = get_student_overall_attendance(student_id)

    return render_template(
        'student_dashboard.html',
        summary=overall_summary
    )


# -----------------------------------------------------------------------------
# Reports & CSV Export Routes
# -----------------------------------------------------------------------------

@app.route('/reports')
@login_required
def reports_view():
    report_type = request.args.get('type', 'daily')
    class_id = request.args.get('class_id', type=int)
    subject_id = request.args.get('subject_id', type=int)
    selected_date = request.args.get('date', date.today().strftime('%Y-%m-%d'))

    classes = ClassModel.query.all()
    subjects = Subject.query.filter_by(class_id=class_id).all() if class_id else []

    report_data = []

    if report_type == 'daily':
        query = AttendanceSession.query.filter_by(date=datetime.strptime(selected_date, '%Y-%m-%d').date())
        if class_id:
            query = query.filter_by(class_id=class_id)
        sessions = query.all()
        for s in sessions:
            present_c = sum(1 for r in s.records if r.status == 'Present')
            absent_c = len(s.records) - present_c
            pct = round((present_c / len(s.records)) * 100, 2) if s.records else 0.0
            report_data.append({
                'date': s.date,
                'class': s.session_class.name,
                'subject': s.subject.name,
                'hour': s.hour_number,
                'teacher': s.teacher.name,
                'total_students': len(s.records),
                'present_count': present_c,
                'absent_count': absent_c,
                'percentage': pct
            })

    elif report_type == 'ra_students':
        students = Student.query.all()
        for st in students:
            ov = get_student_overall_attendance(st.id)
            if ov['is_ra']:
                report_data.append(ov)

    elif report_type == 'internal_marks':
        if class_id:
            students = Student.query.filter_by(class_id=class_id).all()
            for st in students:
                ov = get_student_overall_attendance(st.id)
                report_data.append(ov)

    return render_template(
        'reports.html',
        report_type=report_type,
        classes=classes,
        subjects=subjects,
        selected_class_id=class_id,
        selected_subject_id=subject_id,
        selected_date=selected_date,
        report_data=report_data
    )


@app.route('/export/csv')
@login_required
def export_csv():
    report_type = request.args.get('type', 'attendance')
    class_id = request.args.get('class_id', type=int)

    output = io.StringIO()
    writer = csv.writer(output)

    if report_type == 'ra_students':
        writer.writerow(['Register Number', 'Student Name', 'Class', 'Total Hours', 'Present Hours', 'Absent Hours', 'Percentage (%)', 'Internal Mark', 'Status'])
        students = Student.query.all()
        for st in students:
            ov = get_student_overall_attendance(st.id)
            if ov['is_ra']:
                writer.writerow([
                    st.register_number,
                    st.name,
                    st.student_class.name,
                    ov['overall_total_hours'],
                    ov['overall_present_hours'],
                    ov['overall_absent_hours'],
                    ov['overall_percentage'],
                    ov['overall_internal_mark'],
                    'RA - Attendance Below 50%'
                ])

    elif report_type == 'class_tutor':
        writer.writerow(['Register Number', 'Student Name', 'Total Hours', 'Present Hours', 'Absent Hours', 'Percentage (%)', 'Internal Mark', 'Status'])
        if class_id:
            students = Student.query.filter_by(class_id=class_id).all()
            for st in students:
                ov = get_student_overall_attendance(st.id)
                writer.writerow([
                    st.register_number,
                    st.name,
                    ov['overall_total_hours'],
                    ov['overall_present_hours'],
                    ov['overall_absent_hours'],
                    ov['overall_percentage'],
                    ov['overall_internal_mark'],
                    ov['overall_label']
                ])

    else:
        writer.writerow(['Register Number', 'Student Name', 'Class', 'Total Hours', 'Present Hours', 'Percentage (%)', 'Internal Mark'])
        students = Student.query.filter_by(class_id=class_id).all() if class_id else Student.query.all()
        for st in students:
            ov = get_student_overall_attendance(st.id)
            writer.writerow([
                st.register_number,
                st.name,
                st.student_class.name,
                ov['overall_total_hours'],
                ov['overall_present_hours'],
                ov['overall_percentage'],
                ov['overall_internal_mark']
            ])

    response = make_response(output.getvalue())
    response.headers["Content-Disposition"] = f"attachment; filename={report_type}_report.csv"
    response.headers["Content-type"] = "text/csv"
    return response


# -----------------------------------------------------------------------------
# Main Entry Point
# -----------------------------------------------------------------------------

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
        seed_default_data()
    app.run(debug=True)
