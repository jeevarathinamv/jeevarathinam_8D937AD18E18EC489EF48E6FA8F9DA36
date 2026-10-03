import os
from datetime import datetime, date, timedelta
from functools import wraps
from flask import Flask, render_template, request, redirect, url_for, flash, session
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'student_skill_workshop_secret_key_2025')

# Admin Hardcoded Fallback Credentials
ADMIN_USERNAME = os.environ.get('ADMIN_USERNAME', 'admin')
ADMIN_PASSWORD = os.environ.get('ADMIN_PASSWORD', 'admin123')

# Database configuration: Default to MySQL URI, fallback/option for SQLite
MYSQL_URI = os.environ.get('DATABASE_URL', 'mysql+pymysql://root:@localhost/student_skill_workshop')
SQLITE_URI = 'sqlite:///' + os.path.join(os.path.abspath(os.path.dirname(__file__)), 'student_skill_workshop.db')

use_sqlite = os.environ.get('USE_SQLITE') == '1'
app.config['SQLALCHEMY_DATABASE_URI'] = SQLITE_URI if use_sqlite else MYSQL_URI
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

# Categories
CATEGORIES = [
    'Python',
    'Web Development',
    'Java',
    'Database',
    'Data Science',
    'Communication',
    'Soft Skills',
    'Other'
]

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

    registrations = db.relationship('Registration', backref='student', cascade='all, delete-orphan', lazy=True)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)


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


class Workshop(db.Model):
    __tablename__ = 'workshops'
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(150), nullable=False)
    description = db.Column(db.Text, nullable=True)
    category = db.Column(db.String(50), nullable=False)
    trainer_name = db.Column(db.String(100), nullable=False)
    date = db.Column(db.Date, nullable=False)
    time = db.Column(db.String(50), nullable=False)
    venue = db.Column(db.String(150), nullable=False)
    total_seats = db.Column(db.Integer, nullable=False, default=30)
    available_seats = db.Column(db.Integer, nullable=False, default=30)
    status = db.Column(db.String(20), default='Upcoming')  # Upcoming, Completed, Cancelled
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    registrations = db.relationship('Registration', backref='workshop', cascade='all, delete-orphan', lazy=True)

    @property
    def is_completed(self):
        if self.status == 'Completed':
            return True
        if self.date < date.today():
            return True
        return False


class Registration(db.Model):
    __tablename__ = 'registrations'
    id = db.Column(db.Integer, primary_key=True)
    student_id = db.Column(db.Integer, db.ForeignKey('students.id'), nullable=False)
    workshop_id = db.Column(db.Integer, db.ForeignKey('workshops.id'), nullable=False)
    registration_date = db.Column(db.DateTime, default=datetime.utcnow)
    status = db.Column(db.String(20), default='Registered')  # Registered, Cancelled

    __table_args__ = (
        db.UniqueConstraint('student_id', 'workshop_id', name='unique_student_workshop'),
    )


def seed_default_data():
    # Ensure default admin exists
    admin = Admin.query.filter_by(username=ADMIN_USERNAME).first()
    if not admin:
        admin = Admin(username=ADMIN_USERNAME)
        admin.set_password(ADMIN_PASSWORD)
        db.session.add(admin)
        db.session.commit()

    if Workshop.query.count() == 0:
        today = date.today()
        sample_workshops = [
            Workshop(
                title='Mastering Python & Flask',
                description='Hands-on workshop covering Python fundamentals, OOP, web routing, templates, and RESTful web development using Flask framework.',
                category='Python',
                trainer_name='Prof. Ramesh Kumar',
                date=today + timedelta(days=10),
                time='10:00 AM - 01:00 PM',
                venue='Seminar Hall A',
                total_seats=40,
                available_seats=40,
                status='Upcoming'
            ),
            Workshop(
                title='Modern Web Development with Bootstrap 5',
                description='Learn responsive frontend design, modern CSS grid/flexbox layouts, UI cards, modals, and interactive web elements with Bootstrap 5.',
                category='Web Development',
                trainer_name='Dr. Priya Sharma',
                date=today + timedelta(days=15),
                time='02:00 PM - 05:00 PM',
                venue='Computer Lab 2',
                total_seats=35,
                available_seats=35,
                status='Upcoming'
            ),
            Workshop(
                title='Java Enterprise Concepts & Spring Boot',
                description='Deep dive into Core Java, Object-Oriented Design patterns, and basic web application architecture with Spring Boot.',
                category='Java',
                trainer_name='Prof. Anita Roy',
                date=today + timedelta(days=20),
                time='11:00 AM - 02:00 PM',
                venue='Seminar Hall B',
                total_seats=50,
                available_seats=50,
                status='Upcoming'
            ),
            Workshop(
                title='MySQL Database Design & Query Optimization',
                description='Master relational database modeling, ER diagrams, normalization (1NF to 3NF), JOIN queries, and SQL performance tuning.',
                category='Database',
                trainer_name='Dr. K. V. Sundaram',
                date=today + timedelta(days=25),
                time='09:30 AM - 12:30 PM',
                venue='Computer Lab 1',
                total_seats=30,
                available_seats=30,
                status='Upcoming'
            ),
            Workshop(
                title='Data Science & Analytics with Python',
                description='Comprehensive introduction to data processing with Pandas, NumPy calculations, and exploratory data visualization with Matplotlib.',
                category='Data Science',
                trainer_name='Dr. Suresh Nair',
                date=today + timedelta(days=30),
                time='10:00 AM - 04:00 PM',
                venue='Auditorium',
                total_seats=60,
                available_seats=60,
                status='Upcoming'
            ),
            Workshop(
                title='Effective Corporate Communication Skills',
                description='Interactive seminar on professional presentation skills, corporate email etiquette, cross-cultural communication, and confidence building.',
                category='Communication',
                trainer_name='Prof. Meera Menen',
                date=today + timedelta(days=35),
                time='02:00 PM - 04:00 PM',
                venue='Seminar Hall A',
                total_seats=45,
                available_seats=45,
                status='Upcoming'
            ),
            Workshop(
                title='Soft Skills & Technical Interview Mastery',
                description='Practical guidance on resume preparation, group discussion tactics, technical interview strategies, and mock interviews.',
                category='Soft Skills',
                trainer_name='Mr. Vikram Verma',
                date=today + timedelta(days=40),
                time='10:00 AM - 01:00 PM',
                venue='Placement Cell',
                total_seats=50,
                available_seats=50,
                status='Upcoming'
            )
        ]
        db.session.add_all(sample_workshops)
        db.session.commit()


# Decorators
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
            flash('Admin authentication required.', 'warning')
            return redirect(url_for('admin_login'))
        return f(*args, **kwargs)
    return decorated_function


# Context Processor to pass categories to templates
@app.context_processor
def inject_globals():
    return dict(categories=CATEGORIES, today_date=date.today())


# Public Routes
@app.route('/')
def index():
    workshops = Workshop.query.order_by(Workshop.date.asc()).limit(6).all()
    total_students = Student.query.count()
    total_workshops = Workshop.query.count()
    total_registrations = Registration.query.filter_by(status='Registered').count()
    return render_template(
        'index.html',
        workshops=workshops,
        total_students=total_students,
        total_workshops=total_workshops,
        total_registrations=total_registrations
    )


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

        existing_reg = Student.query.filter_by(register_number=register_number).first()
        if existing_reg:
            flash('A student with this Register Number already exists.', 'danger')
            return redirect(url_for('register'))

        existing_email = Student.query.filter_by(email=email).first()
        if existing_email:
            flash('A student with this Email address already exists.', 'danger')
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

        flash('Registration successful! Please login to your account.', 'success')
        return redirect(url_for('login'))

    return render_template('register.html')


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        login_input = request.form.get('login_input', '').strip()
        password = request.form.get('password', '')

        if not login_input or not password:
            flash('Please enter both login identifier and password.', 'danger')
            return redirect(url_for('login'))

        student = Student.query.filter(
            (Student.email == login_input.lower()) | (Student.register_number == login_input)
        ).first()

        if student and student.check_password(password):
            session['user_type'] = 'student'
            session['user_id'] = student.id
            session['user_name'] = student.name
            session['register_number'] = student.register_number
            flash(f'Welcome back, {student.name}!', 'success')
            return redirect(url_for('student_dashboard'))
        else:
            flash('Invalid Register Number / Email or Password.', 'danger')
            return redirect(url_for('login'))

    return render_template('login.html')


@app.route('/admin/login', methods=['GET', 'POST'])
@app.route('/admin_login', methods=['GET', 'POST'])
def admin_login():
    if request.method == 'POST':
        username = request.form.get('username', '').strip()
        password = request.form.get('password', '')

        if not username or not password:
            flash('Please enter both username and password.', 'danger')
            return redirect(url_for('admin_login'))

        # Check DB first or fallback to hardcoded admin credentials
        admin = Admin.query.filter_by(username=username).first()
        if admin and admin.check_password(password):
            session['user_type'] = 'admin'
            session['user_id'] = admin.id
            session['user_name'] = admin.username
            flash('Successfully logged in as Administrator.', 'success')
            return redirect(url_for('admin_dashboard'))
        elif username == ADMIN_USERNAME and password == ADMIN_PASSWORD:
            session['user_type'] = 'admin'
            session['user_id'] = 1
            session['user_name'] = ADMIN_USERNAME
            flash('Successfully logged in as Administrator.', 'success')
            return redirect(url_for('admin_dashboard'))
        else:
            flash('Invalid Admin credentials.', 'danger')
            return redirect(url_for('admin_login'))

    return render_template('admin_login.html')


@app.route('/logout')
def logout():
    session.clear()
    flash('You have been logged out successfully.', 'info')
    return redirect(url_for('index'))


# Student Module Routes
@app.route('/student/dashboard')
@student_required
def student_dashboard():
    student_id = session.get('user_id')
    student = Student.query.get_or_404(student_id)

    # All upcoming workshops
    available_workshops = Workshop.query.filter(
        Workshop.status == 'Upcoming',
        Workshop.date >= date.today()
    ).order_by(Workshop.date.asc()).all()

    # Registered workshops for this student
    student_regs = Registration.query.filter_by(student_id=student_id).all()
    reg_workshop_ids = [r.workshop_id for r in student_regs if r.status == 'Registered']

    registered_workshops = []
    completed_workshops = []

    for reg in student_regs:
        if reg.status == 'Registered':
            ws = reg.workshop
            if ws.date < date.today() or ws.status == 'Completed':
                completed_workshops.append(ws)
            else:
                registered_workshops.append(ws)

    return render_template(
        'student_dashboard.html',
        student=student,
        available_workshops=available_workshops,
        registered_workshops=registered_workshops,
        completed_workshops=completed_workshops,
        reg_workshop_ids=reg_workshop_ids
    )


@app.route('/workshops')
def workshops():
    selected_category = request.args.get('category', '').strip()
    search_query = request.args.get('search', '').strip()

    query = Workshop.query

    if selected_category:
        query = query.filter_by(category=selected_category)
    if search_query:
        query = query.filter(Workshop.title.ilike(f'%{search_query}%') | Workshop.trainer_name.ilike(f'%{search_query}%'))

    all_workshops = query.order_by(Workshop.date.asc()).all()

    # If student logged in, get their registration workshop IDs
    reg_workshop_ids = []
    if session.get('user_type') == 'student':
        student_id = session.get('user_id')
        regs = Registration.query.filter_by(student_id=student_id, status='Registered').all()
        reg_workshop_ids = [r.workshop_id for r in regs]

    return render_template(
        'workshops.html',
        workshops=all_workshops,
        selected_category=selected_category,
        search_query=search_query,
        reg_workshop_ids=reg_workshop_ids
    )


@app.route('/workshop/<int:workshop_id>')
def workshop_details(workshop_id):
    workshop = Workshop.query.get_or_404(workshop_id)
    is_registered = False
    registration = None

    if session.get('user_type') == 'student':
        student_id = session.get('user_id')
        registration = Registration.query.filter_by(student_id=student_id, workshop_id=workshop_id).first()
        if registration and registration.status == 'Registered':
            is_registered = True

    return render_template(
        'workshop_details.html',
        workshop=workshop,
        is_registered=is_registered,
        registration=registration
    )


@app.route('/workshop/<int:workshop_id>/register', methods=['POST'])
@student_required
def register_workshop(workshop_id):
    student_id = session.get('user_id')
    workshop = Workshop.query.get_or_404(workshop_id)

    # Check if workshop is upcoming
    if workshop.status != 'Upcoming' or workshop.date < date.today():
        flash('This workshop is not active or has already passed.', 'danger')
        return redirect(url_for('workshop_details', workshop_id=workshop_id))

    # Check available seats
    if workshop.available_seats <= 0:
        flash('Sorry, no seats are available for this workshop.', 'danger')
        return redirect(url_for('workshop_details', workshop_id=workshop_id))

    # Check existing registration
    existing_reg = Registration.query.filter_by(student_id=student_id, workshop_id=workshop_id).first()

    if existing_reg:
        if existing_reg.status == 'Registered':
            flash('You are already registered for this workshop.', 'warning')
            return redirect(url_for('workshop_details', workshop_id=workshop_id))
        else:
            # Re-activate registration
            existing_reg.status = 'Registered'
            existing_reg.registration_date = datetime.utcnow()
            workshop.available_seats -= 1
            db.session.commit()
            flash(f'Successfully re-registered for {workshop.title}!', 'success')
            return redirect(url_for('my_workshops'))

    # New Registration
    new_reg = Registration(
        student_id=student_id,
        workshop_id=workshop_id,
        status='Registered'
    )
    workshop.available_seats -= 1
    db.session.add(new_reg)
    db.session.commit()

    flash(f'Congratulations! You have successfully registered for "{workshop.title}".', 'success')
    return redirect(url_for('my_workshops'))


@app.route('/workshop/<int:workshop_id>/cancel', methods=['POST'])
@student_required
def cancel_workshop_registration(workshop_id):
    student_id = session.get('user_id')
    registration = Registration.query.filter_by(student_id=student_id, workshop_id=workshop_id).first_or_404()

    if registration.status == 'Registered':
        registration.status = 'Cancelled'
        workshop = registration.workshop
        workshop.available_seats += 1
        if workshop.available_seats > workshop.total_seats:
            workshop.available_seats = workshop.total_seats
        db.session.commit()
        flash(f'Your registration for "{workshop.title}" has been cancelled.', 'info')

    return redirect(url_for('my_workshops'))


@app.route('/my_workshops')
@app.route('/my-workshops')
@student_required
def my_workshops():
    student_id = session.get('user_id')
    registrations = Registration.query.filter_by(student_id=student_id).order_by(Registration.registration_date.desc()).all()
    return render_template('my_workshops.html', registrations=registrations)


# Admin Module Routes
@app.route('/admin/dashboard')
@admin_required
def admin_dashboard():
    total_students = Student.query.count()
    total_workshops = Workshop.query.count()
    total_registrations = Registration.query.filter_by(status='Registered').count()
    upcoming_workshops_count = Workshop.query.filter(
        Workshop.status == 'Upcoming',
        Workshop.date >= date.today()
    ).count()

    recent_registrations = Registration.query.order_by(Registration.registration_date.desc()).limit(5).all()
    upcoming_workshops = Workshop.query.filter(
        Workshop.status == 'Upcoming',
        Workshop.date >= date.today()
    ).order_by(Workshop.date.asc()).limit(5).all()

    return render_template(
        'admin_dashboard.html',
        total_students=total_students,
        total_workshops=total_workshops,
        total_registrations=total_registrations,
        upcoming_workshops_count=upcoming_workshops_count,
        recent_registrations=recent_registrations,
        upcoming_workshops=upcoming_workshops
    )


@app.route('/admin/workshops')
@app.route('/admin/manage_workshops')
@admin_required
def manage_workshops():
    workshops_list = Workshop.query.order_by(Workshop.date.asc()).all()
    return render_template('manage_workshops.html', workshops=workshops_list)


@app.route('/admin/workshops/add', methods=['GET', 'POST'])
@app.route('/admin/add_workshop', methods=['GET', 'POST'])
@admin_required
def add_workshop():
    if request.method == 'POST':
        title = request.form.get('title', '').strip()
        description = request.form.get('description', '').strip()
        category = request.form.get('category', '').strip()
        trainer_name = request.form.get('trainer_name', '').strip()
        date_str = request.form.get('date', '').strip()
        time_str = request.form.get('time', '').strip()
        venue = request.form.get('venue', '').strip()
        total_seats = request.form.get('total_seats', type=int, default=30)
        status = request.form.get('status', 'Upcoming').strip()

        if not title or not category or not trainer_name or not date_str or not time_str or not venue or total_seats <= 0:
            flash('Please fill in all required fields properly.', 'danger')
            return redirect(url_for('add_workshop'))

        try:
            ws_date = datetime.strptime(date_str, '%Y-%m-%d').date()
        except ValueError:
            flash('Invalid date format. Use YYYY-MM-DD.', 'danger')
            return redirect(url_for('add_workshop'))

        workshop = Workshop(
            title=title,
            description=description,
            category=category,
            trainer_name=trainer_name,
            date=ws_date,
            time=time_str,
            venue=venue,
            total_seats=total_seats,
            available_seats=total_seats,
            status=status
        )
        db.session.add(workshop)
        db.session.commit()

        flash(f'Workshop "{title}" created successfully!', 'success')
        return redirect(url_for('manage_workshops'))

    return render_template('add_workshop.html')


@app.route('/admin/workshops/edit/<int:workshop_id>', methods=['GET', 'POST'])
@app.route('/admin/edit_workshop/<int:workshop_id>', methods=['GET', 'POST'])
@admin_required
def edit_workshop(workshop_id):
    workshop = Workshop.query.get_or_404(workshop_id)

    if request.method == 'POST':
        title = request.form.get('title', '').strip()
        description = request.form.get('description', '').strip()
        category = request.form.get('category', '').strip()
        trainer_name = request.form.get('trainer_name', '').strip()
        date_str = request.form.get('date', '').strip()
        time_str = request.form.get('time', '').strip()
        venue = request.form.get('venue', '').strip()
        total_seats = request.form.get('total_seats', type=int)
        status = request.form.get('status', 'Upcoming').strip()

        if not title or not category or not trainer_name or not date_str or not time_str or not venue or total_seats <= 0:
            flash('Please fill in all required fields.', 'danger')
            return redirect(url_for('edit_workshop', workshop_id=workshop_id))

        try:
            ws_date = datetime.strptime(date_str, '%Y-%m-%d').date()
        except ValueError:
            flash('Invalid date format.', 'danger')
            return redirect(url_for('edit_workshop', workshop_id=workshop_id))

        # Adjust available seats based on change in total_seats
        active_regs = Registration.query.filter_by(workshop_id=workshop_id, status='Registered').count()
        new_available = total_seats - active_regs
        if new_available < 0:
            flash(f'Total seats cannot be less than current active registrations ({active_regs}).', 'danger')
            return redirect(url_for('edit_workshop', workshop_id=workshop_id))

        workshop.title = title
        workshop.description = description
        workshop.category = category
        workshop.trainer_name = trainer_name
        workshop.date = ws_date
        workshop.time = time_str
        workshop.venue = venue
        workshop.total_seats = total_seats
        workshop.available_seats = new_available
        workshop.status = status

        db.session.commit()
        flash(f'Workshop "{title}" updated successfully!', 'success')
        return redirect(url_for('manage_workshops'))

    return render_template('edit_workshop.html', workshop=workshop)


@app.route('/admin/workshops/delete/<int:workshop_id>', methods=['POST'])
@admin_required
def delete_workshop(workshop_id):
    workshop = Workshop.query.get_or_404(workshop_id)
    title = workshop.title
    db.session.delete(workshop)
    db.session.commit()
    flash(f'Workshop "{title}" deleted successfully.', 'info')
    return redirect(url_for('manage_workshops'))


@app.route('/admin/registrations')
@admin_required
def registrations():
    registrations_list = Registration.query.order_by(Registration.registration_date.desc()).all()
    return render_template('registrations.html', registrations=registrations_list)


@app.route('/admin/registrations/status/<int:registration_id>', methods=['POST'])
@admin_required
def update_registration_status(registration_id):
    registration = Registration.query.get_or_404(registration_id)
    new_status = request.form.get('status', '').strip()

    if new_status in ['Registered', 'Cancelled']:
        if registration.status != new_status:
            workshop = registration.workshop
            if new_status == 'Cancelled' and registration.status == 'Registered':
                workshop.available_seats += 1
                if workshop.available_seats > workshop.total_seats:
                    workshop.available_seats = workshop.total_seats
            elif new_status == 'Registered' and registration.status == 'Cancelled':
                if workshop.available_seats <= 0:
                    flash('Cannot set status to Registered because no seats are available.', 'danger')
                    return redirect(url_for('registrations'))
                workshop.available_seats -= 1

            registration.status = new_status
            db.session.commit()
            flash(f'Registration status updated to "{new_status}".', 'success')

    return redirect(url_for('registrations'))


@app.route('/admin/students')
@app.route('/admin/manage_students')
@admin_required
def manage_students():
    students = Student.query.order_by(Student.name.asc()).all()
    return render_template('manage_students.html', students=students)


if __name__ == '__main__':
    with app.app_context():
        db.create_all()
        seed_default_data()
    app.run(debug=True)
