import os
from datetime import datetime, timedelta, date
from functools import wraps
from flask import Flask, render_template, request, redirect, url_for, flash, session
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'college_academic_calendar_secret_key_987')

# Admin Hardcoded Credentials
ADMIN_USERNAME = os.environ.get('ADMIN_USERNAME', 'admin')
ADMIN_PASSWORD = os.environ.get('ADMIN_PASSWORD', 'admin123')

# Database configuration: Default to MySQL URI, fallback/option for SQLite
MYSQL_URI = os.environ.get('DATABASE_URL', 'mysql+pymysql://root:@localhost/academic_calendar_db')
SQLITE_URI = 'sqlite:///' + os.path.join(os.path.abspath(os.path.dirname(__file__)), 'academic_calendar.db')

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

class AcademicEvent(db.Model):
    __tablename__ = 'academic_events'
    id = db.Column(db.Integer, primary_key=True)
    event_title = db.Column(db.String(150), nullable=False)
    event_type = db.Column(db.String(50), nullable=False)
    department = db.Column(db.String(100), nullable=False)
    semester = db.Column(db.String(20), nullable=False)
    start_date = db.Column(db.Date, nullable=False)
    end_date = db.Column(db.Date, nullable=False)
    venue = db.Column(db.String(150), nullable=False)
    description = db.Column(db.Text, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

def seed_default_data():
    admin = db.session.query(Admin).filter_by(username=ADMIN_USERNAME).first()
    if not admin:
        admin = Admin(username=ADMIN_USERNAME)
        admin.set_password(ADMIN_PASSWORD)
        db.session.add(admin)
        db.session.commit()

    if db.session.query(AcademicEvent).count() == 0:
        today = date.today()
        sample_events = [
            AcademicEvent(
                event_title='Semester Orientation Program',
                event_type='College Event',
                department='All Departments',
                semester='Semester 1',
                start_date=today,
                end_date=today,
                venue='Main Auditorium',
                description='Welcoming first semester MCA students and introducing college faculty and campus amenities.'
            ),
            AcademicEvent(
                event_title='Mid-Semester Internal Examination',
                event_type='Internal Exam',
                department='Computer Applications (MCA)',
                semester='Semester 2',
                start_date=today + timedelta(days=5),
                end_date=today + timedelta(days=10),
                venue='Exam Hall B',
                description='Mid-semester assessment covering Units 1, 2, and 3.'
            ),
            AcademicEvent(
                event_title='National Seminar on Cloud Computing & AI',
                event_type='Seminar',
                department='Computer Applications (MCA)',
                semester='All Semesters',
                start_date=today + timedelta(days=15),
                end_date=today + timedelta(days=15),
                venue='Seminar Hall 1',
                description='Expert lectures by industry experts on cloud infrastructure and artificial intelligence applications.'
            ),
            AcademicEvent(
                event_title='National Youth Day Holiday',
                event_type='Holiday',
                department='All Departments',
                semester='All Semesters',
                start_date=today + timedelta(days=20),
                end_date=today + timedelta(days=20),
                venue='N/A',
                description='College holiday on account of National Youth Day.'
            ),
            AcademicEvent(
                event_title='End-Semester Practical Examinations',
                event_type='Semester Exam',
                department='Computer Science',
                semester='Semester 4',
                start_date=today + timedelta(days=30),
                end_date=today + timedelta(days=35),
                venue='Computer Lab 3',
                description='Practical lab examinations for Web Development and Database Lab.'
            )
        ]
        db.session.add_all(sample_events)
        db.session.commit()

# Auth Decorators
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
            flash('Administrator access required.', 'warning')
            return redirect(url_for('admin_login'))
        return f(*args, **kwargs)
    return decorated_function

# Public Index Page
@app.route('/')
def index():
    today = date.today()
    all_events = db.session.query(AcademicEvent).order_by(AcademicEvent.start_date.asc()).all()
    today_events = [e for e in all_events if e.start_date <= today <= e.end_date]
    upcoming_events = [e for e in all_events if e.start_date > today][:4]
    return render_template('index.html', today_events=today_events, upcoming_events=upcoming_events, today=today)

# Student Registration
@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        student_name = request.form.get('student_name', '').strip()
        register_number = request.form.get('register_number', '').strip()
        department = request.form.get('department', '').strip()
        email = request.form.get('email', '').strip().lower()
        password = request.form.get('password', '')

        if not student_name or not register_number or not department or not email or not password:
            flash('All fields are required.', 'danger')
            return redirect(url_for('register'))

        existing_student = db.session.query(Student).filter(
            (Student.email == email) | (Student.register_number == register_number)
        ).first()

        if existing_student:
            flash('A student with this Email or Register Number already exists.', 'danger')
            return redirect(url_for('register'))

        student = Student(
            student_name=student_name,
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
            flash('Please enter your email/register number and password.', 'danger')
            return redirect(url_for('login'))

        student = db.session.query(Student).filter(
            (Student.email == email_or_reg.lower()) | (Student.register_number == email_or_reg)
        ).first()

        if student and student.check_password(password):
            session['user_type'] = 'student'
            session['user_id'] = student.id
            session['user_name'] = student.student_name
            session['department'] = student.department
            flash(f'Welcome back, {student.student_name}!', 'success')
            return redirect(url_for('student_dashboard'))
        else:
            flash('Invalid credentials. Please check your details and try again.', 'danger')
            return redirect(url_for('login'))

    return render_template('login.html')

# Admin Login
@app.route('/admin_login', methods=['GET', 'POST'])
def admin_login():
    if request.method == 'POST':
        username = request.form.get('username', '').strip()
        password = request.form.get('password', '')

        if not username or not password:
            flash('Please enter username and password.', 'danger')
            return redirect(url_for('admin_login'))

        admin = db.session.query(Admin).filter_by(username=username).first()
        if admin and admin.check_password(password):
            session['user_type'] = 'admin'
            session['user_name'] = admin.username
            flash('Logged in successfully as Administrator.', 'success')
            return redirect(url_for('admin_dashboard'))
        elif username == ADMIN_USERNAME and password == ADMIN_PASSWORD:
            session['user_type'] = 'admin'
            session['user_name'] = 'admin'
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

# Student Dashboard
@app.route('/student/dashboard')
@student_required
def student_dashboard():
    student_id = session.get('user_id')
    student = db.session.get(Student, student_id)
    today = date.today()

    all_events = db.session.query(AcademicEvent).order_by(AcademicEvent.start_date.asc()).all()
    today_events = [e for e in all_events if e.start_date <= today <= e.end_date]
    upcoming_events = [e for e in all_events if e.start_date > today]

    total_events_count = len(all_events)
    today_events_count = len(today_events)
    upcoming_events_count = len(upcoming_events)

    return render_template(
        'student_dashboard.html',
        student=student,
        today_events=today_events,
        upcoming_events=upcoming_events[:5],
        total_events_count=total_events_count,
        today_events_count=today_events_count,
        upcoming_events_count=upcoming_events_count,
        today=today
    )

# Academic Calendar View & Filter
@app.route('/calendar')
@student_required
def calendar():
    today = date.today()
    selected_type = request.args.get('event_type', '').strip()
    selected_dept = request.args.get('department', '').strip()
    selected_semester = request.args.get('semester', '').strip()
    selected_month = request.args.get('month', '').strip()

    query = db.session.query(AcademicEvent)

    if selected_type and selected_type != 'All':
        query = query.filter(AcademicEvent.event_type == selected_type)

    if selected_dept and selected_dept != 'All':
        query = query.filter(
            (AcademicEvent.department == selected_dept) | (AcademicEvent.department == 'All Departments')
        )

    if selected_semester and selected_semester != 'All':
        query = query.filter(
            (AcademicEvent.semester == selected_semester) | (AcademicEvent.semester == 'All Semesters')
        )

    events = query.order_by(AcademicEvent.start_date.asc()).all()

    # Filter by month if provided
    if selected_month and selected_month.isdigit():
        month_num = int(selected_month)
        events = [e for e in events if e.start_date.month == month_num or e.end_date.month == month_num]

    today_events = [e for e in events if e.start_date <= today <= e.end_date]
    upcoming_events = [e for e in events if e.start_date > today]

    event_types = [
        'College Event', 'Semester Exam', 'Internal Exam', 'Holiday',
        'Workshop', 'Seminar', 'Assignment Deadline', 'Result Date', 'Other'
    ]
    departments = [
        'All Departments', 'Computer Applications (MCA)', 'Computer Science',
        'Information Technology', 'Business Administration', 'Commerce', 'Mathematics'
    ]
    semesters = [
        'All Semesters', 'Semester 1', 'Semester 2', 'Semester 3',
        'Semester 4', 'Semester 5', 'Semester 6'
    ]

    return render_template(
        'calendar.html',
        events=events,
        today_events=today_events,
        upcoming_events=upcoming_events,
        today=today,
        event_types=event_types,
        departments=departments,
        semesters=semesters,
        selected_type=selected_type,
        selected_dept=selected_dept,
        selected_semester=selected_semester,
        selected_month=selected_month
    )

# Event Details View
@app.route('/event/<int:event_id>')
def event_details(event_id):
    event = db.session.get(AcademicEvent, event_id)
    if not event:
        flash('Event not found.', 'danger')
        return redirect(url_for('index'))

    today = date.today()
    is_today = event.start_date <= today <= event.end_date
    is_upcoming = event.start_date > today
    is_past = event.end_date < today

    return render_template(
        'event_details.html',
        event=event,
        is_today=is_today,
        is_upcoming=is_upcoming,
        is_past=is_past,
        today=today
    )

# Admin Dashboard
@app.route('/admin/dashboard')
@admin_required
def admin_dashboard():
    today = date.today()
    total_students_count = db.session.query(Student).count()
    total_events_count = db.session.query(AcademicEvent).count()

    all_events = db.session.query(AcademicEvent).order_by(AcademicEvent.start_date.asc()).all()
    today_events = [e for e in all_events if e.start_date <= today <= e.end_date]
    upcoming_events = [e for e in all_events if e.start_date > today]

    today_events_count = len(today_events)
    upcoming_events_count = len(upcoming_events)

    recent_students = db.session.query(Student).order_by(Student.created_at.desc()).limit(5).all()
    recent_events = all_events[:5]

    return render_template(
        'admin_dashboard.html',
        total_students_count=total_students_count,
        total_events_count=total_events_count,
        today_events_count=today_events_count,
        upcoming_events_count=upcoming_events_count,
        today_events=today_events,
        upcoming_events=upcoming_events[:5],
        recent_students=recent_students,
        recent_events=recent_events,
        today=today
    )

# Admin: Manage Events
@app.route('/admin/events')
@admin_required
def manage_events():
    search_query = request.args.get('q', '').strip()
    query = db.session.query(AcademicEvent)

    if search_query:
        query = query.filter(
            (AcademicEvent.event_title.ilike(f'%{search_query}%')) |
            (AcademicEvent.department.ilike(f'%{search_query}%')) |
            (AcademicEvent.event_type.ilike(f'%{search_query}%'))
        )

    events = query.order_by(AcademicEvent.start_date.asc()).all()
    today = date.today()
    return render_template('manage_events.html', events=events, search_query=search_query, today=today)

# Admin: Add Event
@app.route('/admin/event/add', methods=['GET', 'POST'])
@admin_required
def add_event():
    if request.method == 'POST':
        event_title = request.form.get('event_title', '').strip()
        event_type = request.form.get('event_type', '').strip()
        department = request.form.get('department', '').strip()
        semester = request.form.get('semester', '').strip()
        start_date_str = request.form.get('start_date', '').strip()
        end_date_str = request.form.get('end_date', '').strip()
        venue = request.form.get('venue', '').strip()
        description = request.form.get('description', '').strip()

        if not event_title or not event_type or not department or not semester or not start_date_str or not end_date_str or not venue:
            flash('All required fields must be filled out.', 'danger')
            return redirect(url_for('add_event'))

        try:
            start_date = datetime.strptime(start_date_str, '%Y-%m-%d').date()
            end_date = datetime.strptime(end_date_str, '%Y-%m-%d').date()
        except ValueError:
            flash('Invalid date format provided.', 'danger')
            return redirect(url_for('add_event'))

        if end_date < start_date:
            flash('End Date cannot be earlier than Start Date.', 'danger')
            return redirect(url_for('add_event'))

        event = AcademicEvent(
            event_title=event_title,
            event_type=event_type,
            department=department,
            semester=semester,
            start_date=start_date,
            end_date=end_date,
            venue=venue,
            description=description
        )
        db.session.add(event)
        db.session.commit()

        flash(f'Academic Event "{event_title}" created successfully.', 'success')
        return redirect(url_for('manage_events'))

    event_types = [
        'College Event', 'Semester Exam', 'Internal Exam', 'Holiday',
        'Workshop', 'Seminar', 'Assignment Deadline', 'Result Date', 'Other'
    ]
    departments = [
        'All Departments', 'Computer Applications (MCA)', 'Computer Science',
        'Information Technology', 'Business Administration', 'Commerce', 'Mathematics'
    ]
    semesters = [
        'All Semesters', 'Semester 1', 'Semester 2', 'Semester 3',
        'Semester 4', 'Semester 5', 'Semester 6'
    ]

    return render_template('add_event.html', event_types=event_types, departments=departments, semesters=semesters)

# Admin: Edit Event
@app.route('/admin/event/edit/<int:event_id>', methods=['GET', 'POST'])
@admin_required
def edit_event(event_id):
    event = db.session.get(AcademicEvent, event_id)
    if not event:
        flash('Event not found.', 'danger')
        return redirect(url_for('manage_events'))

    if request.method == 'POST':
        event_title = request.form.get('event_title', '').strip()
        event_type = request.form.get('event_type', '').strip()
        department = request.form.get('department', '').strip()
        semester = request.form.get('semester', '').strip()
        start_date_str = request.form.get('start_date', '').strip()
        end_date_str = request.form.get('end_date', '').strip()
        venue = request.form.get('venue', '').strip()
        description = request.form.get('description', '').strip()

        if not event_title or not event_type or not department or not semester or not start_date_str or not end_date_str or not venue:
            flash('All required fields must be filled out.', 'danger')
            return redirect(url_for('edit_event', event_id=event_id))

        try:
            start_date = datetime.strptime(start_date_str, '%Y-%m-%d').date()
            end_date = datetime.strptime(end_date_str, '%Y-%m-%d').date()
        except ValueError:
            flash('Invalid date format provided.', 'danger')
            return redirect(url_for('edit_event', event_id=event_id))

        if end_date < start_date:
            flash('End Date cannot be earlier than Start Date.', 'danger')
            return redirect(url_for('edit_event', event_id=event_id))

        event.event_title = event_title
        event.event_type = event_type
        event.department = department
        event.semester = semester
        event.start_date = start_date
        event.end_date = end_date
        event.venue = venue
        event.description = description

        db.session.commit()
        flash(f'Academic Event "{event_title}" updated successfully.', 'success')
        return redirect(url_for('manage_events'))

    event_types = [
        'College Event', 'Semester Exam', 'Internal Exam', 'Holiday',
        'Workshop', 'Seminar', 'Assignment Deadline', 'Result Date', 'Other'
    ]
    departments = [
        'All Departments', 'Computer Applications (MCA)', 'Computer Science',
        'Information Technology', 'Business Administration', 'Commerce', 'Mathematics'
    ]
    semesters = [
        'All Semesters', 'Semester 1', 'Semester 2', 'Semester 3',
        'Semester 4', 'Semester 5', 'Semester 6'
    ]

    return render_template(
        'edit_event.html',
        event=event,
        event_types=event_types,
        departments=departments,
        semesters=semesters
    )

# Admin: Delete Event
@app.route('/admin/event/delete/<int:event_id>', methods=['POST'])
@admin_required
def delete_event(event_id):
    event = db.session.get(AcademicEvent, event_id)
    if event:
        title = event.event_title
        db.session.delete(event)
        db.session.commit()
        flash(f'Event "{title}" deleted successfully.', 'info')
    else:
        flash('Event not found.', 'danger')
    return redirect(url_for('manage_events'))

# Admin: Manage Students
@app.route('/admin/students')
@admin_required
def manage_students():
    search_query = request.args.get('q', '').strip()
    query = db.session.query(Student)

    if search_query:
        query = query.filter(
            (Student.student_name.ilike(f'%{search_query}%')) |
            (Student.register_number.ilike(f'%{search_query}%')) |
            (Student.department.ilike(f'%{search_query}%')) |
            (Student.email.ilike(f'%{search_query}%'))
        )

    students = query.order_by(Student.student_name.asc()).all()
    return render_template('manage_students.html', students=students, search_query=search_query)

# Admin: Delete Student
@app.route('/admin/student/delete/<int:student_id>', methods=['POST'])
@admin_required
def delete_student(student_id):
    student = db.session.get(Student, student_id)
    if student:
        name = student.student_name
        db.session.delete(student)
        db.session.commit()
        flash(f'Student record for "{name}" deleted successfully.', 'info')
    else:
        flash('Student record not found.', 'danger')
    return redirect(url_for('manage_students'))

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
        seed_default_data()
    app.run(debug=True)
