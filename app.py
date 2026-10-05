import os
from datetime import datetime, date
from functools import wraps
from flask import Flask, render_template, request, redirect, url_for, flash, session
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'college_dept_secret_key_98765')

# Database configuration: Default to MySQL URI (department_db), fallback/option for SQLite
MYSQL_URI = os.environ.get('DATABASE_URL', 'mysql+pymysql://root:@localhost/department_db')
SQLITE_URI = 'sqlite:///' + os.path.join(os.path.abspath(os.path.dirname(__file__)), 'department.db')

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
    year = db.Column(db.String(50), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

class Department(db.Model):
    __tablename__ = 'department'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    code = db.Column(db.String(20), nullable=False)
    head = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(120), nullable=False)
    phone = db.Column(db.String(20), nullable=False)
    description = db.Column(db.Text, nullable=False)

class Faculty(db.Model):
    __tablename__ = 'faculty'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    faculty_id = db.Column(db.String(50), unique=True, nullable=False)
    department = db.Column(db.String(100), nullable=False)
    designation = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(120), nullable=False)
    phone = db.Column(db.String(20), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class Notice(db.Model):
    __tablename__ = 'notices'
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text, nullable=False)
    notice_date = db.Column(db.Date, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

# Seed default database values if empty
def seed_default_data():
    if Admin.query.count() == 0:
        admin = Admin(username='admin')
        admin.set_password('admin123')
        db.session.add(admin)

    if Department.query.count() == 0:
        dept = Department(
            id=1,
            name='Department of Computer Applications',
            code='MCA-DEPT',
            head='Dr. S. Ramanathan',
            email='mca.dept@college.edu',
            phone='+91 98765 43210',
            description='The Department of Computer Applications is committed to excellence in computer science education, practical software development skills, and modern technology research.'
        )
        db.session.add(dept)

    if Faculty.query.count() == 0:
        fac1 = Faculty(name='Dr. S. Ramanathan', faculty_id='FAC101', department='Computer Applications', designation='Head of Department & Professor', email='ramanathan@college.edu', phone='+91 98765 43210')
        fac2 = Faculty(name='Prof. Anita Sharma', faculty_id='FAC102', department='Computer Applications', designation='Associate Professor', email='anita.sharma@college.edu', phone='+91 98765 43211')
        fac3 = Faculty(name='Prof. Rajesh Kumar', faculty_id='FAC103', department='Computer Applications', designation='Assistant Professor', email='rajesh.kumar@college.edu', phone='+91 98765 43212')
        db.session.add_all([fac1, fac2, fac3])

    if Notice.query.count() == 0:
        n1 = Notice(title='Welcome to the New Academic Session', description='Classes for the upcoming semester will commence on Monday. All students are requested to review their updated timetable on the department notice board.', notice_date=date(2025, 2, 1))
        n2 = Notice(title='Technical Seminar on Web Technologies', description='A special guest lecture on Modern Web Development Frameworks will be conducted in the Main Auditorium at 10:00 AM this Friday.', notice_date=date(2025, 2, 10))
        n3 = Notice(title='Submission of Project Phase 1 Documentation', description='Final year MCA students are required to submit their Project Phase 1 synopsis and documentation to their respective faculty guides by the end of this week.', notice_date=date(2025, 2, 15))
        db.session.add_all([n1, n2, n3])

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
            flash('Admin access required.', 'warning')
            return redirect(url_for('admin_login'))
        return f(*args, **kwargs)
    return decorated_function

# General / Student Routes

@app.route('/')
def index():
    dept = Department.query.first()
    recent_notices = Notice.query.order_by(Notice.notice_date.desc()).limit(3).all()
    return render_template('index.html', department=dept, recent_notices=recent_notices)

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        name = request.form.get('name', '').strip()
        register_number = request.form.get('register_number', '').strip()
        department = request.form.get('department', '').strip()
        year = request.form.get('year', '').strip()
        email = request.form.get('email', '').strip().lower()
        password = request.form.get('password', '')

        if not name or not register_number or not department or not year or not email or not password:
            flash('All fields are required.', 'danger')
            return redirect(url_for('register'))

        existing_student = Student.query.filter(
            (Student.email == email) | (Student.register_number == register_number)
        ).first()

        if existing_student:
            flash('A student with this Register Number or Email already exists.', 'danger')
            return redirect(url_for('register'))

        student = Student(
            name=name,
            register_number=register_number,
            department=department,
            year=year,
            email=email
        )
        student.set_password(password)
        db.session.add(student)
        db.session.commit()

        flash('Registration successful! Please log in.', 'success')
        return redirect(url_for('login'))

    return render_template('register.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email_or_reg = request.form.get('email_or_reg', '').strip()
        password = request.form.get('password', '')

        if not email_or_reg or not password:
            flash('Please provide email/register number and password.', 'danger')
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

        flash('Invalid register number/email or password.', 'danger')
        return redirect(url_for('login'))

    return render_template('login.html')

@app.route('/logout')
def logout():
    session.clear()
    flash('You have been logged out successfully.', 'info')
    return redirect(url_for('index'))

@app.route('/student/dashboard')
@student_required
def student_dashboard():
    student_id = session.get('user_id')
    student = Student.query.get_or_404(student_id)
    dept = Department.query.first()
    return render_template('student_dashboard.html', student=student, department=dept)

@app.route('/department')
def view_department():
    dept = Department.query.first()
    return render_template('department.html', department=dept)

@app.route('/faculty')
def view_faculty():
    faculties = Faculty.query.all()
    return render_template('faculty.html', faculties=faculties)

@app.route('/notices')
def view_notices():
    notices_list = Notice.query.order_by(Notice.notice_date.desc()).all()
    return render_template('notices.html', notices=notices_list)

# Admin Routes

@app.route('/admin/login', methods=['GET', 'POST'])
def admin_login():
    if request.method == 'POST':
        username = request.form.get('username', '').strip()
        password = request.form.get('password', '')

        admin = Admin.query.filter_by(username=username).first()
        if admin and admin.check_password(password):
            session['user_type'] = 'admin'
            session['admin_id'] = admin.id
            session['user_name'] = admin.username
            flash('Logged in successfully as Administrator.', 'success')
            return redirect(url_for('admin_dashboard'))

        flash('Invalid admin credentials.', 'danger')
        return redirect(url_for('admin_login'))

    return render_template('admin_login.html')

@app.route('/admin/dashboard')
@admin_required
def admin_dashboard():
    students = Student.query.order_by(Student.created_at.desc()).all()
    faculty_count = Faculty.query.count()
    notice_count = Notice.query.count()
    student_count = len(students)
    dept = Department.query.first()

    return render_template(
        'admin_dashboard.html',
        students=students,
        total_students=student_count,
        total_faculty=faculty_count,
        total_notices=notice_count,
        department=dept
    )

@app.route('/admin/department', methods=['GET', 'POST'])
@admin_required
def manage_department():
    dept = Department.query.first()
    if not dept:
        dept = Department(
            name='Department of Computer Applications',
            code='MCA-DEPT',
            head='Dr. S. Ramanathan',
            email='mca.dept@college.edu',
            phone='+91 98765 43210',
            description='Department overview and details.'
        )
        db.session.add(dept)
        db.session.commit()

    if request.method == 'POST':
        dept.name = request.form.get('name', '').strip()
        dept.code = request.form.get('code', '').strip()
        dept.head = request.form.get('head', '').strip()
        dept.email = request.form.get('email', '').strip()
        dept.phone = request.form.get('phone', '').strip()
        dept.description = request.form.get('description', '').strip()

        if not dept.name or not dept.code or not dept.head or not dept.email or not dept.phone or not dept.description:
            flash('All fields are required.', 'danger')
            return redirect(url_for('manage_department'))

        db.session.commit()
        flash('Department information updated successfully.', 'success')
        return redirect(url_for('manage_department'))

    return render_template('manage_department.html', department=dept)

@app.route('/admin/faculty')
@admin_required
def manage_faculty():
    faculties = Faculty.query.all()
    return render_template('manage_faculty.html', faculties=faculties)

@app.route('/admin/faculty/add', methods=['GET', 'POST'])
@admin_required
def add_faculty():
    if request.method == 'POST':
        name = request.form.get('name', '').strip()
        faculty_id = request.form.get('faculty_id', '').strip()
        department = request.form.get('department', '').strip()
        designation = request.form.get('designation', '').strip()
        email = request.form.get('email', '').strip()
        phone = request.form.get('phone', '').strip()

        if not name or not faculty_id or not department or not designation or not email or not phone:
            flash('All fields are required.', 'danger')
            return redirect(url_for('add_faculty'))

        existing_fac = Faculty.query.filter_by(faculty_id=faculty_id).first()
        if existing_fac:
            flash('Faculty with this ID already exists.', 'danger')
            return redirect(url_for('add_faculty'))

        fac = Faculty(
            name=name,
            faculty_id=faculty_id,
            department=department,
            designation=designation,
            email=email,
            phone=phone
        )
        db.session.add(fac)
        db.session.commit()

        flash(f'Faculty "{name}" added successfully.', 'success')
        return redirect(url_for('manage_faculty'))

    return render_template('add_faculty.html')

@app.route('/admin/faculty/edit/<int:faculty_id>', methods=['GET', 'POST'])
@admin_required
def edit_faculty(faculty_id):
    fac = Faculty.query.get_or_404(faculty_id)

    if request.method == 'POST':
        name = request.form.get('name', '').strip()
        fac_id = request.form.get('faculty_id', '').strip()
        department = request.form.get('department', '').strip()
        designation = request.form.get('designation', '').strip()
        email = request.form.get('email', '').strip()
        phone = request.form.get('phone', '').strip()

        if not name or not fac_id or not department or not designation or not email or not phone:
            flash('All fields are required.', 'danger')
            return redirect(url_for('edit_faculty', faculty_id=faculty_id))

        existing_fac = Faculty.query.filter(Faculty.faculty_id == fac_id, Faculty.id != faculty_id).first()
        if existing_fac:
            flash('Another faculty member with this ID already exists.', 'danger')
            return redirect(url_for('edit_faculty', faculty_id=faculty_id))

        fac.name = name
        fac.faculty_id = fac_id
        fac.department = department
        fac.designation = designation
        fac.email = email
        fac.phone = phone

        db.session.commit()
        flash('Faculty details updated successfully.', 'success')
        return redirect(url_for('manage_faculty'))

    return render_template('edit_faculty.html', faculty=fac)

@app.route('/admin/faculty/delete/<int:faculty_id>', methods=['POST'])
@admin_required
def delete_faculty(faculty_id):
    fac = Faculty.query.get_or_404(faculty_id)
    db.session.delete(fac)
    db.session.commit()
    flash('Faculty deleted successfully.', 'info')
    return redirect(url_for('manage_faculty'))

@app.route('/admin/notices')
@admin_required
def manage_notices():
    notices_list = Notice.query.order_by(Notice.notice_date.desc()).all()
    return render_template('manage_notices.html', notices=notices_list)

@app.route('/admin/notices/add', methods=['GET', 'POST'])
@admin_required
def add_notice():
    if request.method == 'POST':
        title = request.form.get('title', '').strip()
        description = request.form.get('description', '').strip()
        notice_date_str = request.form.get('notice_date', '').strip()

        if not title or not description or not notice_date_str:
            flash('All fields are required.', 'danger')
            return redirect(url_for('add_notice'))

        try:
            notice_date = datetime.strptime(notice_date_str, '%Y-%m-%d').date()
        except ValueError:
            flash('Invalid date format.', 'danger')
            return redirect(url_for('add_notice'))

        notice = Notice(
            title=title,
            description=description,
            notice_date=notice_date
        )
        db.session.add(notice)
        db.session.commit()

        flash('Notice published successfully.', 'success')
        return redirect(url_for('manage_notices'))

    today_str = date.today().isoformat()
    return render_template('add_notice.html', today=today_str)

@app.route('/admin/notices/edit/<int:notice_id>', methods=['GET', 'POST'])
@admin_required
def edit_notice(notice_id):
    notice = Notice.query.get_or_404(notice_id)

    if request.method == 'POST':
        title = request.form.get('title', '').strip()
        description = request.form.get('description', '').strip()
        notice_date_str = request.form.get('notice_date', '').strip()

        if not title or not description or not notice_date_str:
            flash('All fields are required.', 'danger')
            return redirect(url_for('edit_notice', notice_id=notice_id))

        try:
            notice_date = datetime.strptime(notice_date_str, '%Y-%m-%d').date()
        except ValueError:
            flash('Invalid date format.', 'danger')
            return redirect(url_for('edit_notice', notice_id=notice_id))

        notice.title = title
        notice.description = description
        notice.notice_date = notice_date

        db.session.commit()
        flash('Notice updated successfully.', 'success')
        return redirect(url_for('manage_notices'))

    return render_template('edit_notice.html', notice=notice)

@app.route('/admin/notices/delete/<int:notice_id>', methods=['POST'])
@admin_required
def delete_notice(notice_id):
    notice = Notice.query.get_or_404(notice_id)
    db.session.delete(notice)
    db.session.commit()
    flash('Notice deleted successfully.', 'info')
    return redirect(url_for('manage_notices'))

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
        seed_default_data()
    app.run(debug=True)
