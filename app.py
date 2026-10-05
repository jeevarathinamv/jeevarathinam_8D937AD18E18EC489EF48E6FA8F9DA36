import os
from datetime import datetime, date
from functools import wraps
from flask import Flask, render_template, request, redirect, url_for, flash, session
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'college_hostel_secret_key_98765')

# Admin Hardcoded Fallback / Environment Credentials
ADMIN_USERNAME = os.environ.get('ADMIN_USERNAME', 'admin')
ADMIN_PASSWORD = os.environ.get('ADMIN_PASSWORD', 'admin123')

# Database configuration: Default to MySQL URI, fallback to SQLite if USE_SQLITE=1
MYSQL_URI = os.environ.get('DATABASE_URL', 'mysql+pymysql://root:@localhost/hostel_db')
SQLITE_URI = 'sqlite:///' + os.path.join(os.path.abspath(os.path.dirname(__file__)), 'hostel.db')

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
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    allocations = db.relationship('Allocation', backref='student', lazy=True, cascade='all, delete-orphan')

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)


class Room(db.Model):
    __tablename__ = 'rooms'
    id = db.Column(db.Integer, primary_key=True)
    room_number = db.Column(db.String(20), nullable=False)
    hostel_name = db.Column(db.String(100), nullable=False)
    room_type = db.Column(db.String(20), nullable=False)  # Single, Double, Triple
    capacity = db.Column(db.Integer, nullable=False)
    available_beds = db.Column(db.Integer, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    allocations = db.relationship('Allocation', backref='room', lazy=True, cascade='all, delete-orphan')


class Allocation(db.Model):
    __tablename__ = 'allocations'
    id = db.Column(db.Integer, primary_key=True)
    student_id = db.Column(db.Integer, db.ForeignKey('students.id'), nullable=False)
    room_id = db.Column(db.Integer, db.ForeignKey('rooms.id'), nullable=False)
    allocation_date = db.Column(db.Date, nullable=False)
    status = db.Column(db.String(20), default='Allocated')  # Allocated, Cancelled
    created_at = db.Column(db.DateTime, default=datetime.utcnow)


def seed_default_data():
    # Seed default admin if not exists
    admin = db.session.query(Admin).filter_by(username=ADMIN_USERNAME).first()
    if not admin:
        admin = Admin(username=ADMIN_USERNAME)
        admin.set_password(ADMIN_PASSWORD)
        db.session.add(admin)
        db.session.commit()

    # Seed sample rooms if none exist
    if db.session.query(Room).count() == 0:
        sample_rooms = [
            Room(room_number='A-101', hostel_name='Boys Hostel Block A', room_type='Single', capacity=1, available_beds=1),
            Room(room_number='A-102', hostel_name='Boys Hostel Block A', room_type='Double', capacity=2, available_beds=2),
            Room(room_number='A-103', hostel_name='Boys Hostel Block A', room_type='Triple', capacity=3, available_beds=3),
            Room(room_number='B-201', hostel_name='Girls Hostel Block B', room_type='Single', capacity=1, available_beds=1),
            Room(room_number='B-202', hostel_name='Girls Hostel Block B', room_type='Double', capacity=2, available_beds=2),
        ]
        db.session.add_all(sample_rooms)
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
            flash('Admin login required.', 'warning')
            return redirect(url_for('admin_login'))
        return f(*args, **kwargs)
    return decorated_function


# Routes
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
            flash('All fields are required.', 'danger')
            return redirect(url_for('register'))

        existing_student = db.session.query(Student).filter(
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

        flash('Registration successful! Please log in.', 'success')
        return redirect(url_for('login'))

    return render_template('register.html')


# Student Login
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email_or_reg = request.form.get('email_or_reg', '').strip()
        password = request.form.get('password', '')

        if not email_or_reg or not password:
            flash('Please fill in all fields.', 'danger')
            return redirect(url_for('login'))

        student = db.session.query(Student).filter(
            (Student.email == email_or_reg.lower()) | (Student.register_number == email_or_reg)
        ).first()

        if student and student.check_password(password):
            session['user_type'] = 'student'
            session['user_id'] = student.id
            session['user_name'] = student.name
            flash(f'Welcome back, {student.name}!', 'success')
            return redirect(url_for('student_dashboard'))
        else:
            flash('Invalid Email/Register Number or Password.', 'danger')
            return redirect(url_for('login'))

    return render_template('login.html')


# Admin Login
@app.route('/admin/login', methods=['GET', 'POST'])
def admin_login():
    if request.method == 'POST':
        username = request.form.get('username', '').strip()
        password = request.form.get('password', '')

        if not username or not password:
            flash('Please enter admin credentials.', 'danger')
            return redirect(url_for('admin_login'))

        admin = db.session.query(Admin).filter_by(username=username).first()
        if admin and admin.check_password(password):
            session['user_type'] = 'admin'
            session['user_id'] = admin.id
            session['user_name'] = 'Administrator'
            flash('Logged in successfully as Administrator.', 'success')
            return redirect(url_for('admin_dashboard'))
        elif username == ADMIN_USERNAME and password == ADMIN_PASSWORD:
            session['user_type'] = 'admin'
            session['user_name'] = 'Administrator'
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
    active_allocation = db.session.query(Allocation).filter_by(student_id=student_id, status='Allocated').first()
    return render_template('student_dashboard.html', student=student, allocation=active_allocation)


# My Room (Student View)
@app.route('/student/my_room')
@student_required
def my_room():
    student_id = session.get('user_id')
    student = db.session.get(Student, student_id)
    allocations = db.session.query(Allocation).filter_by(student_id=student_id).order_by(Allocation.created_at.desc()).all()
    active_allocation = db.session.query(Allocation).filter_by(student_id=student_id, status='Allocated').first()
    return render_template('my_room.html', student=student, allocations=allocations, active_allocation=active_allocation)


# Admin Dashboard
@app.route('/admin/dashboard')
@admin_required
def admin_dashboard():
    total_students = db.session.query(Student).count()
    total_rooms = db.session.query(Room).count()
    allocated_rooms = db.session.query(Allocation).filter_by(status='Allocated').count()

    all_rooms = db.session.query(Room).all()
    total_available_beds = sum(room.available_beds for room in all_rooms)

    recent_allocations = db.session.query(Allocation).order_by(Allocation.created_at.desc()).limit(5).all()

    return render_template(
        'admin_dashboard.html',
        total_students=total_students,
        total_rooms=total_rooms,
        allocated_rooms=allocated_rooms,
        total_available_beds=total_available_beds,
        recent_allocations=recent_allocations
    )


# View Registered Students (Admin)
@app.route('/admin/students')
@admin_required
def view_students():
    students = db.session.query(Student).order_by(Student.created_at.desc()).all()
    return render_template('admin_students.html', students=students)


# Manage Rooms List (Admin)
@app.route('/admin/rooms')
@admin_required
def manage_rooms():
    rooms = db.session.query(Room).order_by(Room.hostel_name, Room.room_number).all()
    return render_template('manage_rooms.html', rooms=rooms)


# Add Room (Admin)
@app.route('/admin/rooms/add', methods=['GET', 'POST'])
@admin_required
def add_room():
    if request.method == 'POST':
        room_number = request.form.get('room_number', '').strip()
        hostel_name = request.form.get('hostel_name', '').strip()
        room_type = request.form.get('room_type', '').strip()
        capacity = request.form.get('capacity', type=int)

        if not room_number or not hostel_name or not room_type or capacity is None or capacity <= 0:
            flash('Please fill out all room fields with valid values.', 'danger')
            return redirect(url_for('add_room'))

        room = Room(
            room_number=room_number,
            hostel_name=hostel_name,
            room_type=room_type,
            capacity=capacity,
            available_beds=capacity
        )
        db.session.add(room)
        db.session.commit()
        flash(f'Room {room_number} added successfully.', 'success')
        return redirect(url_for('manage_rooms'))

    return render_template('add_room.html')


# Edit Room (Admin)
@app.route('/admin/rooms/edit/<int:room_id>', methods=['GET', 'POST'])
@admin_required
def edit_room(room_id):
    room = db.session.get(Room, room_id)
    if not room:
        flash('Room not found.', 'danger')
        return redirect(url_for('manage_rooms'))

    if request.method == 'POST':
        room_number = request.form.get('room_number', '').strip()
        hostel_name = request.form.get('hostel_name', '').strip()
        room_type = request.form.get('room_type', '').strip()
        capacity = request.form.get('capacity', type=int)
        available_beds = request.form.get('available_beds', type=int)

        if not room_number or not hostel_name or not room_type or capacity is None or available_beds is None:
            flash('All fields are required.', 'danger')
            return redirect(url_for('edit_room', room_id=room_id))

        if available_beds > capacity:
            flash('Available beds cannot exceed total capacity.', 'danger')
            return redirect(url_for('edit_room', room_id=room_id))

        room.room_number = room_number
        room.hostel_name = hostel_name
        room.room_type = room_type
        room.capacity = capacity
        room.available_beds = available_beds

        db.session.commit()
        flash(f'Room {room.room_number} updated successfully.', 'success')
        return redirect(url_for('manage_rooms'))

    return render_template('edit_room.html', room=room)


# Delete Room (Admin)
@app.route('/admin/rooms/delete/<int:room_id>', methods=['POST'])
@admin_required
def delete_room(room_id):
    room = db.session.get(Room, room_id)
    if room:
        db.session.delete(room)
        db.session.commit()
        flash('Room deleted successfully.', 'info')
    else:
        flash('Room not found.', 'danger')
    return redirect(url_for('manage_rooms'))


# Allocate Room (Admin)
@app.route('/admin/allocate', methods=['GET', 'POST'])
@admin_required
def allocate_room():
    if request.method == 'POST':
        student_id = request.form.get('student_id', type=int)
        room_id = request.form.get('room_id', type=int)
        allocation_date_str = request.form.get('allocation_date', '')

        if not student_id or not room_id or not allocation_date_str:
            flash('Please select a student, room, and allocation date.', 'danger')
            return redirect(url_for('allocate_room'))

        student = db.session.get(Student, student_id)
        room = db.session.get(Room, room_id)

        if not student or not room:
            flash('Invalid student or room selection.', 'danger')
            return redirect(url_for('allocate_room'))

        # Check if student already has an active allocation
        active_alloc = db.session.query(Allocation).filter_by(student_id=student_id, status='Allocated').first()
        if active_alloc:
            flash(f'Student {student.name} already has an active room allocation ({active_alloc.room.room_number}).', 'danger')
            return redirect(url_for('allocate_room'))

        # Check if room has available beds
        if room.available_beds <= 0:
            flash(f'Room {room.room_number} in {room.hostel_name} has no available beds.', 'danger')
            return redirect(url_for('allocate_room'))

        try:
            alloc_date = datetime.strptime(allocation_date_str, '%Y-%m-%d').date()
        except ValueError:
            flash('Invalid date format.', 'danger')
            return redirect(url_for('allocate_room'))

        # Perform allocation and auto decrease available beds
        allocation = Allocation(
            student_id=student_id,
            room_id=room_id,
            allocation_date=alloc_date,
            status='Allocated'
        )
        room.available_beds -= 1

        db.session.add(allocation)
        db.session.commit()

        flash(f'Room {room.room_number} successfully allocated to {student.name}.', 'success')
        return redirect(url_for('view_allocations'))

    students = db.session.query(Student).order_by(Student.name).all()
    rooms = db.session.query(Room).filter(Room.available_beds > 0).order_by(Room.hostel_name, Room.room_number).all()
    today_str = date.today().isoformat()
    return render_template('allocate_room.html', students=students, rooms=rooms, today=today_str)


# View Allocations (Admin)
@app.route('/admin/allocations')
@admin_required
def view_allocations():
    allocations = db.session.query(Allocation).order_by(Allocation.created_at.desc()).all()
    return render_template('allocations.html', allocations=allocations)


# Cancel Allocation (Admin)
@app.route('/admin/allocations/cancel/<int:allocation_id>', methods=['POST'])
@admin_required
def cancel_allocation(allocation_id):
    allocation = db.session.get(Allocation, allocation_id)
    if not allocation:
        flash('Allocation record not found.', 'danger')
        return redirect(url_for('view_allocations'))

    if allocation.status == 'Cancelled':
        flash('Allocation is already cancelled.', 'warning')
        return redirect(url_for('view_allocations'))

    # Change status and increase available beds
    allocation.status = 'Cancelled'
    if allocation.room and allocation.room.available_beds < allocation.room.capacity:
        allocation.room.available_beds += 1

    db.session.commit()
    flash(f'Allocation for student {allocation.student.name} cancelled. Available beds updated.', 'info')
    return redirect(url_for('view_allocations'))


if __name__ == '__main__':
    with app.app_context():
        db.create_all()
        seed_default_data()
    app.run(debug=True)
