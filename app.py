import os
import random
import string
from datetime import datetime, date, timedelta
from functools import wraps
from flask import Flask, render_template, request, redirect, url_for, flash, session
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'student_workshop_system_secret_key_999')

# Admin Credentials Fallback / Environment Variables
ADMIN_USERNAME = os.environ.get('ADMIN_USERNAME', 'admin')
ADMIN_PASSWORD = os.environ.get('ADMIN_PASSWORD', 'admin123')

# Database Configuration: Default to MySQL, fallback to SQLite if USE_SQLITE=1
MYSQL_URI = os.environ.get('DATABASE_URL', 'mysql+pymysql://root:@localhost/student_workshop_system')
SQLITE_URI = 'sqlite:///' + os.path.join(os.path.abspath(os.path.dirname(__file__)), 'student_workshop.db')

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
    year = db.Column(db.String(20), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    phone_number = db.Column(db.String(20), nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    registrations = db.relationship('Registration', backref='student', lazy=True, cascade='all, delete-orphan')

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

class Admin(db.Model):
    __tablename__ = 'admins'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    name = db.Column(db.String(100), nullable=False, default='System Administrator')
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

class Workshop(db.Model):
    __tablename__ = 'workshops'
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text, nullable=False)
    category = db.Column(db.String(100), nullable=False)
    trainer_name = db.Column(db.String(100), nullable=False)
    date = db.Column(db.Date, nullable=False)
    start_time = db.Column(db.Time, nullable=False)
    end_time = db.Column(db.Time, nullable=False)
    venue = db.Column(db.String(150), nullable=False)
    total_seats = db.Column(db.Integer, nullable=False, default=0)
    registration_deadline = db.Column(db.Date, nullable=False)
    status = db.Column(db.String(20), default='Upcoming') # Upcoming, Ongoing, Completed, Cancelled
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    registrations = db.relationship('Registration', backref='workshop', lazy=True, cascade='all, delete-orphan')

    @property
    def available_seats(self):
        active_count = Registration.query.filter(
            Registration.workshop_id == self.id,
            Registration.status != 'Cancelled'
        ).count()
        seats_left = self.total_seats - active_count
        return max(0, seats_left)

class Registration(db.Model):
    __tablename__ = 'registrations'
    id = db.Column(db.Integer, primary_key=True)
    registration_id = db.Column(db.String(50), unique=True, nullable=False)
    student_id = db.Column(db.Integer, db.ForeignKey('students.id'), nullable=False)
    workshop_id = db.Column(db.Integer, db.ForeignKey('workshops.id'), nullable=False)
    registration_date = db.Column(db.DateTime, default=datetime.utcnow)
    status = db.Column(db.String(20), default='Registered') # Registered, Cancelled, Attended

    attendance = db.relationship('Attendance', backref='registration', uselist=False, cascade='all, delete-orphan')

    __table_args__ = (
        db.UniqueConstraint('student_id', 'workshop_id', name='unique_student_workshop'),
    )

class Attendance(db.Model):
    __tablename__ = 'attendance'
    id = db.Column(db.Integer, primary_key=True)
    registration_id = db.Column(db.Integer, db.ForeignKey('registrations.id'), unique=True, nullable=False)
    status = db.Column(db.String(20), nullable=False, default='Absent') # Present, Absent
    marked_at = db.Column(db.DateTime, default=datetime.utcnow)

WORKSHOP_CATEGORIES = [
    'Programming',
    'Web Development',
    'Data Science',
    'Cyber Security',
    'Cloud Computing',
    'Soft Skills',
    'Entrepreneurship',
    'Other'
]

# Helper Function: Generate Unique Registration ID
def generate_registration_id():
    prefix = "REGWS"
    rand_digits = "".join(random.choices(string.digits, k=5))
    code = f"{prefix}{rand_digits}"
    while Registration.query.filter_by(registration_id=code).first() is not None:
        rand_digits = "".join(random.choices(string.digits, k=5))
        code = f"{prefix}{rand_digits}"
    return code

# Default Data Seeding
def seed_default_data():
    if Admin.query.count() == 0:
        admin_user = Admin(username=ADMIN_USERNAME, name='System Administrator')
        admin_user.set_password(ADMIN_PASSWORD)
        db.session.add(admin_user)
        db.session.commit()

    if Workshop.query.count() == 0:
        today = date.today()
        sample_workshops = [
            Workshop(
                title='Full Stack Web Development with Flask & React',
                description='Learn full stack web application development using Python Flask and React JS with hands-on project implementation.',
                category='Web Development',
                trainer_name='Dr. Aris Thorne',
                date=today + timedelta(days=5),
                start_time=datetime.strptime('09:30', '%H:%M').time(),
                end_time=datetime.strptime('12:30', '%H:%M').time(),
                venue='Seminar Hall A',
                total_seats=40,
                registration_deadline=today + timedelta(days=4),
                status='Upcoming'
            ),
            Workshop(
                title='Data Science & Machine Learning Fundamentals',
                description='An introductory workshop covering data analysis, Python Pandas, Scikit-Learn, and building predictive models.',
                category='Data Science',
                trainer_name='Prof. Sarah Jenkins',
                date=today + timedelta(days=1), # Scheduled for tomorrow for reminder testing
                start_time=datetime.strptime('10:00', '%H:%M').time(),
                end_time=datetime.strptime('13:00', '%H:%M').time(),
                venue='Computer Lab 3',
                total_seats=30,
                registration_deadline=today,
                status='Upcoming'
            ),
            Workshop(
                title='Ethical Hacking & Cyber Security Essentials',
                description='Understand network security fundamentals, penetration testing concepts, and defensive cyber security strategies.',
                category='Cyber Security',
                trainer_name='Alex Mercer',
                date=today + timedelta(days=12),
                start_time=datetime.strptime('14:00', '%H:%M').time(),
                end_time=datetime.strptime('17:00', '%H:%M').time(),
                venue='Auditorium',
                total_seats=50,
                registration_deadline=today + timedelta(days=11),
                status='Upcoming'
            ),
            Workshop(
                title='Cloud Computing with AWS Fundamentals',
                description='Introduction to Amazon Web Services, cloud architecture, EC2 instances, S3 storage, and deployment models.',
                category='Cloud Computing',
                trainer_name='Vikram Malhotra',
                date=today + timedelta(days=18),
                start_time=datetime.strptime('10:00', '%H:%M').time(),
                end_time=datetime.strptime('12:30', '%H:%M').time(),
                venue='Seminar Hall B',
                total_seats=35,
                registration_deadline=today + timedelta(days=17),
                status='Upcoming'
            ),
            Workshop(
                title='Soft Skills & Leadership for IT Professionals',
                description='Interactive session focusing on communication skills, resume building, interview techniques, and team leadership.',
                category='Soft Skills',
                trainer_name='Clara Vance',
                date=today - timedelta(days=10),
                start_time=datetime.strptime('11:00', '%H:%M').time(),
                end_time=datetime.strptime('13:00', '%H:%M').time(),
                venue='Conference Room 1',
                total_seats=60,
                registration_deadline=today - timedelta(days=11),
                status='Completed'
            )
        ]
        db.session.add_all(sample_workshops)
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
            flash('Admin authentication required.', 'danger')
            return redirect(url_for('admin_login'))
        return f(*args, **kwargs)
    return decorated_function

# Context Processor
@app.context_processor
def inject_now():
    return {'year': datetime.utcnow().year}

# Public Routes
@app.route('/')
def index():
    featured = Workshop.query.filter_by(status='Upcoming').order_by(Workshop.date.asc()).limit(3).all()
    return render_template('index.html', featured_workshops=featured)

# Student Registration
@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        name = request.form.get('name', '').strip()
        register_number = request.form.get('register_number', '').strip()
        department = request.form.get('department', '').strip()
        year = request.form.get('year', '').strip()
        email = request.form.get('email', '').strip().lower()
        phone_number = request.form.get('phone_number', '').strip()
        password = request.form.get('password', '')

        if not name or not register_number or not department or not year or not email or not phone_number or not password:
            flash('All fields are required.', 'danger')
            return redirect(url_for('register'))

        existing_student = Student.query.filter(
            (Student.email == email) | (Student.register_number == register_number)
        ).first()

        if existing_student:
            flash('A student with this Email Address or Register Number is already registered.', 'danger')
            return redirect(url_for('register'))

        student = Student(
            name=name,
            register_number=register_number,
            department=department,
            year=year,
            email=email,
            phone_number=phone_number
        )
        student.set_password(password)
        db.session.add(student)
        db.session.commit()

        flash('Student account registered successfully! Please log in.', 'success')
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
            flash(f'Welcome back, {student.name}!', 'success')
            return redirect(url_for('student_dashboard'))
        else:
            flash('Invalid login credentials. Please check your Register Number/Email and password.', 'danger')
            return redirect(url_for('login'))

    return render_template('login.html')

# Admin Login
@app.route('/admin/login', methods=['GET', 'POST'])
def admin_login():
    if request.method == 'POST':
        username = request.form.get('username', '').strip()
        password = request.form.get('password', '')

        admin = Admin.query.filter_by(username=username).first()

        # Database or fallback verification
        if (admin and admin.check_password(password)) or (username == ADMIN_USERNAME and password == ADMIN_PASSWORD):
            session['user_type'] = 'admin'
            session['user_id'] = admin.id if admin else 1
            session['user_name'] = admin.name if admin else 'Administrator'
            flash('Successfully authenticated as Administrator.', 'success')
            return redirect(url_for('admin_dashboard'))
        else:
            flash('Invalid admin username or password.', 'danger')
            return redirect(url_for('admin_login'))

    return render_template('admin_login.html')

# Logout Route
@app.route('/logout')
def logout():
    session.clear()
    flash('You have been logged out successfully.', 'info')
    return redirect(url_for('index'))

# Student Dashboard & Reminder Alert
@app.route('/student/dashboard')
@student_required
def student_dashboard():
    student_id = session.get('user_id')
    student = Student.query.get_or_404(student_id)

    total_workshops = Workshop.query.count()
    my_registrations = Registration.query.filter_by(student_id=student_id).all()
    registered_workshop_ids = [r.workshop_id for r in my_registrations if r.status != 'Cancelled']

    registered_count = len(registered_workshop_ids)

    upcoming_workshops = Workshop.query.filter_by(status='Upcoming').order_by(Workshop.date.asc()).all()
    completed_count = Workshop.query.filter_by(status='Completed').count()
    upcoming_count = len(upcoming_workshops)

    # Generate Reminders for registered upcoming workshops happening tomorrow or soon
    reminders = []
    tomorrow = date.today() + timedelta(days=1)

    for reg in my_registrations:
        if reg.status != 'Cancelled' and reg.workshop:
            if reg.workshop.date == tomorrow:
                reminders.append(f"Your workshop '{reg.workshop.title}' is scheduled for tomorrow ({reg.workshop.date}) at {reg.workshop.venue}.")
            elif date.today() <= reg.workshop.date <= date.today() + timedelta(days=3):
                reminders.append(f"Upcoming Workshop: '{reg.workshop.title}' is coming up on {reg.workshop.date} at {reg.workshop.venue}.")

    return render_template(
        'student_dashboard.html',
        student=student,
        total_workshops=total_workshops,
        registered_count=registered_count,
        upcoming_count=upcoming_count,
        completed_count=completed_count,
        upcoming_workshops=upcoming_workshops,
        registered_workshop_ids=registered_workshop_ids,
        reminders=reminders
    )

# All Workshops List with Search & Filtering
@app.route('/workshops')
def workshops():
    search_query = request.args.get('search', '').strip()
    selected_category = request.args.get('category', '').strip()
    selected_status = request.args.get('status', '').strip()
    selected_date = request.args.get('date', '').strip()

    query = Workshop.query

    if search_query:
        query = query.filter(
            (Workshop.title.ilike(f'%{search_query}%')) |
            (Workshop.trainer_name.ilike(f'%{search_query}%'))
        )

    if selected_category:
        query = query.filter(Workshop.category == selected_category)

    if selected_status:
        query = query.filter(Workshop.status == selected_status)

    if selected_date:
        try:
            filter_dt = datetime.strptime(selected_date, '%Y-%m-%d').date()
            query = query.filter(Workshop.date == filter_dt)
        except ValueError:
            pass

    all_workshops = query.order_by(Workshop.date.asc()).all()

    return render_template(
        'workshops.html',
        workshops=all_workshops,
        categories=WORKSHOP_CATEGORIES,
        search_query=search_query,
        selected_category=selected_category,
        selected_status=selected_status,
        selected_date=selected_date
    )

# Workshop Details
@app.route('/workshop/<int:workshop_id>')
def workshop_details(workshop_id):
    workshop = Workshop.query.get_or_404(workshop_id)
    is_registered = False
    existing_registration = None

    if session.get('user_type') == 'student':
        student_id = session.get('user_id')
        existing_registration = Registration.query.filter_by(
            student_id=student_id,
            workshop_id=workshop_id
        ).first()
        if existing_registration and existing_registration.status != 'Cancelled':
            is_registered = True

    return render_template(
        'workshop_details.html',
        workshop=workshop,
        is_registered=is_registered,
        existing_registration=existing_registration
    )

# Register Workshop for Student
@app.route('/workshop/<int:workshop_id>/register', methods=['POST'])
@student_required
def register_workshop(workshop_id):
    student_id = session.get('user_id')
    workshop = Workshop.query.get_or_404(workshop_id)

    # Check Workshop Status & Seat Availability
    if workshop.status != 'Upcoming':
        flash(f'Cannot register for a workshop that is {workshop.status.lower()}.', 'danger')
        return redirect(url_for('workshop_details', workshop_id=workshop_id))

    if workshop.available_seats <= 0:
        flash('Sorry, this workshop is full. No available seats remaining.', 'danger')
        return redirect(url_for('workshop_details', workshop_id=workshop_id))

    if date.today() > workshop.registration_deadline:
        flash('Registration deadline for this workshop has passed.', 'danger')
        return redirect(url_for('workshop_details', workshop_id=workshop_id))

    # Duplicate registration check
    existing_reg = Registration.query.filter_by(
        student_id=student_id,
        workshop_id=workshop_id
    ).first()

    if existing_reg:
        if existing_reg.status == 'Cancelled':
            # Re-activate cancelled registration
            existing_reg.status = 'Registered'
            existing_reg.registration_date = datetime.utcnow()
            db.session.commit()
            flash('Workshop registration completed successfully.', 'success')
            return redirect(url_for('my_workshops'))
        else:
            flash('You are already registered for this workshop.', 'warning')
            return redirect(url_for('workshop_details', workshop_id=workshop_id))

    # Create new registration
    reg_code = generate_registration_id()
    new_registration = Registration(
        registration_id=reg_code,
        student_id=student_id,
        workshop_id=workshop_id,
        status='Registered'
    )
    db.session.add(new_registration)
    db.session.commit()

    flash('Workshop registration completed successfully.', 'success')
    return redirect(url_for('my_workshops'))

# My Workshops (Student View)
@app.route('/my-workshops')
@student_required
def my_workshops():
    student_id = session.get('user_id')
    registrations = Registration.query.filter_by(student_id=student_id).order_by(Registration.registration_date.desc()).all()
    return render_template('my_workshops.html', registrations=registrations)

# Cancel Registration (Student Action)
@app.route('/registration/<int:registration_id>/cancel', methods=['POST'])
@student_required
def cancel_registration(registration_id):
    student_id = session.get('user_id')
    reg = Registration.query.filter_by(id=registration_id, student_id=student_id).first_or_404()

    if reg.workshop.status != 'Upcoming':
        flash('Only upcoming workshop registrations can be cancelled.', 'warning')
        return redirect(url_for('my_workshops'))

    reg.status = 'Cancelled'
    db.session.commit()

    flash('Workshop registration has been cancelled successfully.', 'info')
    return redirect(url_for('my_workshops'))

# Workshop History Route (Student & Admin)
@app.route('/workshop-history')
def workshop_history():
    if session.get('user_type') == 'student':
        student_id = session.get('user_id')
        history_items = Registration.query.join(Workshop).filter(
            Registration.student_id == student_id,
            (Workshop.status == 'Completed') | (Registration.status == 'Attended')
        ).order_by(Workshop.date.desc()).all()
    elif session.get('user_type') == 'admin':
        history_items = Registration.query.join(Workshop).filter(
            (Workshop.status == 'Completed') | (Registration.status == 'Attended')
        ).order_by(Workshop.date.desc()).all()
    else:
        flash('Please log in to view workshop history.', 'warning')
        return redirect(url_for('login'))

    return render_template('workshop_history.html', history_items=history_items)

# Admin Dashboard
@app.route('/admin/dashboard')
@admin_required
def admin_dashboard():
    total_students = Student.query.count()
    total_workshops = Workshop.query.count()
    total_registrations = Registration.query.count()

    upcoming_count = Workshop.query.filter_by(status='Upcoming').count()
    completed_count = Workshop.query.filter_by(status='Completed').count()
    cancelled_registrations_count = Registration.query.filter_by(status='Cancelled').count()

    recent_workshops = Workshop.query.order_by(Workshop.created_at.desc()).limit(5).all()

    return render_template(
        'admin_dashboard.html',
        total_students=total_students,
        total_workshops=total_workshops,
        total_registrations=total_registrations,
        upcoming_count=upcoming_count,
        completed_count=completed_count,
        cancelled_registrations_count=cancelled_registrations_count,
        recent_workshops=recent_workshops
    )

# Manage Workshops (Admin View)
@app.route('/admin/workshops')
@admin_required
def manage_workshops():
    search_query = request.args.get('search', '').strip()
    selected_category = request.args.get('category', '').strip()
    selected_status = request.args.get('status', '').strip()

    query = Workshop.query

    if search_query:
        query = query.filter(
            (Workshop.title.ilike(f'%{search_query}%')) |
            (Workshop.trainer_name.ilike(f'%{search_query}%'))
        )

    if selected_category:
        query = query.filter(Workshop.category == selected_category)

    if selected_status:
        query = query.filter(Workshop.status == selected_status)

    workshops = query.order_by(Workshop.date.desc()).all()

    return render_template(
        'manage_workshops.html',
        workshops=workshops,
        categories=WORKSHOP_CATEGORIES,
        search_query=search_query,
        selected_category=selected_category,
        selected_status=selected_status
    )

# Add Workshop (Admin Action)
@app.route('/admin/workshop/add', methods=['GET', 'POST'])
@admin_required
def add_workshop():
    if request.method == 'POST':
        title = request.form.get('title', '').strip()
        category = request.form.get('category', '').strip()
        description = request.form.get('description', '').strip()
        trainer_name = request.form.get('trainer_name', '').strip()
        venue = request.form.get('venue', '').strip()
        date_str = request.form.get('date', '').strip()
        start_time_str = request.form.get('start_time', '').strip()
        end_time_str = request.form.get('end_time', '').strip()
        total_seats = request.form.get('total_seats', type=int, default=0)
        deadline_str = request.form.get('registration_deadline', '').strip()
        status = request.form.get('status', 'Upcoming').strip()

        if not title or not category or not description or not trainer_name or not venue or not date_str or not start_time_str or not end_time_str or total_seats <= 0 or not deadline_str:
            flash('All workshop fields are required and total seats must be greater than 0.', 'danger')
            return redirect(url_for('add_workshop'))

        try:
            ws_date = datetime.strptime(date_str, '%Y-%m-%d').date()
            start_time = datetime.strptime(start_time_str, '%H:%M').time()
            end_time = datetime.strptime(end_time_str, '%H:%M').time()
            deadline = datetime.strptime(deadline_str, '%Y-%m-%d').date()
        except ValueError:
            flash('Invalid date or time format provided.', 'danger')
            return redirect(url_for('add_workshop'))

        new_ws = Workshop(
            title=title,
            category=category,
            description=description,
            trainer_name=trainer_name,
            venue=venue,
            date=ws_date,
            start_time=start_time,
            end_time=end_time,
            total_seats=total_seats,
            registration_deadline=deadline,
            status=status
        )
        db.session.add(new_ws)
        db.session.commit()

        flash(f'Workshop "{title}" created successfully.', 'success')
        return redirect(url_for('manage_workshops'))

    return render_template('add_workshop.html', categories=WORKSHOP_CATEGORIES)

# Edit Workshop (Admin Action)
@app.route('/admin/workshop/edit/<int:workshop_id>', methods=['GET', 'POST'])
@admin_required
def edit_workshop(workshop_id):
    ws = Workshop.query.get_or_404(workshop_id)

    if request.method == 'POST':
        ws.title = request.form.get('title', '').strip()
        ws.category = request.form.get('category', '').strip()
        ws.description = request.form.get('description', '').strip()
        ws.trainer_name = request.form.get('trainer_name', '').strip()
        ws.venue = request.form.get('venue', '').strip()
        date_str = request.form.get('date', '').strip()
        start_time_str = request.form.get('start_time', '').strip()
        end_time_str = request.form.get('end_time', '').strip()
        ws.total_seats = request.form.get('total_seats', type=int, default=ws.total_seats)
        deadline_str = request.form.get('registration_deadline', '').strip()
        ws.status = request.form.get('status', ws.status).strip()

        try:
            if date_str:
                ws.date = datetime.strptime(date_str, '%Y-%m-%d').date()
            if start_time_str:
                ws.start_time = datetime.strptime(start_time_str, '%H:%M').time()
            if end_time_str:
                ws.end_time = datetime.strptime(end_time_str, '%H:%M').time()
            if deadline_str:
                ws.registration_deadline = datetime.strptime(deadline_str, '%Y-%m-%d').date()
        except ValueError:
            flash('Invalid date or time format provided.', 'danger')
            return redirect(url_for('edit_workshop', workshop_id=workshop_id))

        db.session.commit()
        flash(f'Workshop "{ws.title}" updated successfully.', 'success')
        return redirect(url_for('manage_workshops'))

    return render_template('edit_workshop.html', workshop=ws, categories=WORKSHOP_CATEGORIES)

# Delete Workshop (Admin Action)
@app.route('/admin/workshop/delete/<int:workshop_id>', methods=['POST'])
@admin_required
def delete_workshop(workshop_id):
    ws = Workshop.query.get_or_404(workshop_id)
    db.session.delete(ws)
    db.session.commit()
    flash('Workshop deleted successfully.', 'info')
    return redirect(url_for('manage_workshops'))

# Registration Management (Admin View)
@app.route('/admin/registrations')
@admin_required
def manage_registrations():
    search_query = request.args.get('search', '').strip()
    selected_status = request.args.get('status', '').strip()

    query = Registration.query.join(Student).join(Workshop)

    if search_query:
        query = query.filter(
            (Student.name.ilike(f'%{search_query}%')) |
            (Student.register_number.ilike(f'%{search_query}%')) |
            (Workshop.title.ilike(f'%{search_query}%')) |
            (Registration.registration_id.ilike(f'%{search_query}%'))
        )

    if selected_status:
        query = query.filter(Registration.status == selected_status)

    registrations = query.order_by(Registration.registration_date.desc()).all()

    return render_template(
        'manage_registrations.html',
        registrations=registrations,
        search_query=search_query,
        selected_status=selected_status
    )

# Update Registration Status (Admin Action)
@app.route('/admin/registration/status/<int:registration_id>', methods=['POST'])
@admin_required
def update_registration_status(registration_id):
    reg = Registration.query.get_or_404(registration_id)
    new_status = request.form.get('status', '').strip()

    if new_status in ['Registered', 'Cancelled', 'Attended']:
        reg.status = new_status
        db.session.commit()
        flash(f'Registration status for {reg.registration_id} updated to {new_status}.', 'success')

    return redirect(url_for('manage_registrations'))

# Student Directory Management (Admin View)
@app.route('/admin/students')
@admin_required
def manage_students():
    search_query = request.args.get('search', '').strip()

    query = Student.query

    if search_query:
        query = query.filter(
            (Student.name.ilike(f'%{search_query}%')) |
            (Student.register_number.ilike(f'%{search_query}%')) |
            (Student.department.ilike(f'%{search_query}%')) |
            (Student.email.ilike(f'%{search_query}%'))
        )

    students = query.order_by(Student.created_at.desc()).all()

    return render_template(
        'manage_students.html',
        students=students,
        search_query=search_query
    )

# Attendance Management (Admin View)
@app.route('/admin/attendance')
@admin_required
def admin_attendance():
    selected_workshop_id = request.args.get('workshop_id', type=int)
    search_query = request.args.get('search', '').strip()

    workshops = Workshop.query.order_by(Workshop.date.desc()).all()

    query = Registration.query.join(Student).join(Workshop).filter(Registration.status != 'Cancelled')

    if selected_workshop_id:
        query = query.filter(Registration.workshop_id == selected_workshop_id)

    if search_query:
        query = query.filter(
            (Student.name.ilike(f'%{search_query}%')) |
            (Registration.registration_id.ilike(f'%{search_query}%')) |
            (Student.register_number.ilike(f'%{search_query}%'))
        )

    registrations = query.order_by(Workshop.date.desc(), Student.name.asc()).all()

    return render_template(
        'attendance.html',
        registrations=registrations,
        workshops=workshops,
        selected_workshop_id=selected_workshop_id,
        search_query=search_query
    )

# Mark Attendance (Admin Action)
@app.route('/admin/attendance/mark/<int:registration_id>', methods=['POST'])
@admin_required
def mark_attendance(registration_id):
    reg = Registration.query.get_or_404(registration_id)
    status = request.form.get('status', 'Absent').strip()

    if status not in ['Present', 'Absent']:
        status = 'Absent'

    attendance_record = Attendance.query.filter_by(registration_id=registration_id).first()
    if not attendance_record:
        attendance_record = Attendance(registration_id=registration_id, status=status)
        db.session.add(attendance_record)
    else:
        attendance_record.status = status
        attendance_record.marked_at = datetime.utcnow()

    if status == 'Present':
        reg.status = 'Attended'

    db.session.commit()
    flash(f'Attendance for {reg.student.name} marked as {status}.', 'success')
    return redirect(url_for('admin_attendance'))

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
        seed_default_data()
    app.run(debug=True)
