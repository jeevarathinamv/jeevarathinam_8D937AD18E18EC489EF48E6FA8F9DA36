import os
import random
import string
from datetime import datetime, date
from functools import wraps
from flask import Flask, render_template, request, redirect, url_for, flash, session
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'hostel_room_change_secret_key_98765')

# Database configuration: Default to MySQL URI, fallback/option for SQLite
MYSQL_URI = os.environ.get('DATABASE_URL', 'mysql+pymysql://root:@localhost/hostel_room_change_db')
SQLITE_URI = 'sqlite:///' + os.path.join(os.path.abspath(os.path.dirname(__file__)), 'hostel_room_change.db')

use_sqlite = os.environ.get('USE_SQLITE') == '1'
app.config['SQLALCHEMY_DATABASE_URI'] = SQLITE_URI if use_sqlite else MYSQL_URI
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

# ----------------------------------------------------
# Database Models (5 Tables: admins, students, rooms, room_allocations, room_change_requests)
# ----------------------------------------------------

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

    allocations = db.relationship('RoomAllocation', backref='student', lazy=True, cascade='all, delete-orphan')
    change_requests = db.relationship('RoomChangeRequest', backref='student', lazy=True, cascade='all, delete-orphan')

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)


class Room(db.Model):
    __tablename__ = 'rooms'
    id = db.Column(db.Integer, primary_key=True)
    room_number = db.Column(db.String(20), unique=True, nullable=False)
    hostel_name = db.Column(db.String(100), nullable=False)
    room_type = db.Column(db.String(50), nullable=False)  # Single, Double, Triple, etc.
    capacity = db.Column(db.Integer, nullable=False, default=2)
    available_beds = db.Column(db.Integer, nullable=False, default=2)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    allocations = db.relationship('RoomAllocation', backref='room', lazy=True)


class RoomAllocation(db.Model):
    __tablename__ = 'room_allocations'
    id = db.Column(db.Integer, primary_key=True)
    student_id = db.Column(db.Integer, db.ForeignKey('students.id'), nullable=False)
    room_id = db.Column(db.Integer, db.ForeignKey('rooms.id'), nullable=False)
    allocation_date = db.Column(db.Date, nullable=False, default=date.today)
    status = db.Column(db.String(20), default='Active')  # Active, Inactive
    created_at = db.Column(db.DateTime, default=datetime.utcnow)


class RoomChangeRequest(db.Model):
    __tablename__ = 'room_change_requests'
    id = db.Column(db.Integer, primary_key=True)
    request_id = db.Column(db.String(50), unique=True, nullable=False)
    student_id = db.Column(db.Integer, db.ForeignKey('students.id'), nullable=False)
    current_room_id = db.Column(db.Integer, db.ForeignKey('rooms.id'), nullable=True)
    requested_room_id = db.Column(db.Integer, db.ForeignKey('rooms.id'), nullable=False)
    reason = db.Column(db.String(100), nullable=False)
    request_date = db.Column(db.Date, nullable=False, default=date.today)
    status = db.Column(db.String(20), default='Pending')  # Pending, Approved, Rejected
    admin_remarks = db.Column(db.Text, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    current_room = db.relationship('Room', foreign_keys=[current_room_id])
    requested_room = db.relationship('Room', foreign_keys=[requested_room_id])

# ----------------------------------------------------
# Helper Functions
# ----------------------------------------------------

def generate_unique_request_id():
    while True:
        rand_digits = ''.join(random.choices(string.digits, k=6))
        req_id = f"REQ{rand_digits}"
        if not db.session.get(RoomChangeRequest, req_id) and not RoomChangeRequest.query.filter_by(request_id=req_id).first():
            return req_id

def get_student_active_allocation(student_id):
    return RoomAllocation.query.filter_by(student_id=student_id, status='Active').first()

def seed_default_data():
    # Create default Admin if none exists
    if Admin.query.count() == 0:
        default_admin = Admin(username='admin')
        default_admin.set_password('admin123')
        db.session.add(default_admin)

    # Seed sample rooms if none exist
    if Room.query.count() == 0:
        sample_rooms = [
            Room(room_number='101', hostel_name='A Block Hostel', room_type='Double', capacity=2, available_beds=1),
            Room(room_number='102', hostel_name='A Block Hostel', room_type='Single', capacity=1, available_beds=1),
            Room(room_number='201', hostel_name='B Block Hostel', room_type='Triple', capacity=3, available_beds=2),
            Room(room_number='202', hostel_name='B Block Hostel', room_type='Double', capacity=2, available_beds=2),
            Room(room_number='301', hostel_name='C Block Hostel', room_type='Single', capacity=1, available_beds=0),
        ]
        db.session.add_all(sample_rooms)

    db.session.commit()

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
            flash('Admin access required. Please log in as Admin.', 'warning')
            return redirect(url_for('admin_login'))
        return f(*args, **kwargs)
    return decorated_function

# ----------------------------------------------------
# Routes & Controllers
# ----------------------------------------------------

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
            flash('All fields are required for registration.', 'danger')
            return redirect(url_for('register'))

        existing_student = Student.query.filter(
            (Student.email == email) | (Student.register_number == register_number)
        ).first()

        if existing_student:
            flash('A student with this Email or Register Number already exists.', 'danger')
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
            flash('Please enter your Register Number / Email and Password.', 'danger')
            return redirect(url_for('login'))

        student = Student.query.filter(
            (Student.email == email_or_reg.lower()) | (Student.register_number == email_or_reg)
        ).first()

        if student and student.check_password(password):
            session['user_type'] = 'student'
            session['user_id'] = student.id
            session['user_name'] = student.name
            flash(f'Welcome, {student.name}!', 'success')
            return redirect(url_for('student_dashboard'))
        else:
            flash('Invalid credentials. Please verify your details and try again.', 'danger')
            return redirect(url_for('login'))

    return render_template('login.html')

# Admin Login
@app.route('/admin/login', methods=['GET', 'POST'])
def admin_login():
    if request.method == 'POST':
        username = request.form.get('username', '').strip()
        password = request.form.get('password', '')

        admin = Admin.query.filter_by(username=username).first()
        if admin and admin.check_password(password):
            session['user_type'] = 'admin'
            session['user_id'] = admin.id
            session['user_name'] = admin.username
            flash('Logged in successfully as Administrator.', 'success')
            return redirect(url_for('admin_dashboard'))
        else:
            flash('Invalid admin username or password.', 'danger')
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
    student_id = session.get('user_id')
    student = db.session.get(Student, student_id)
    active_allocation = get_student_active_allocation(student_id)

    my_requests = RoomChangeRequest.query.filter_by(student_id=student_id).all()
    total_requests = len(my_requests)
    pending_requests = len([r for r in my_requests if r.status == 'Pending'])
    approved_requests = len([r for r in my_requests if r.status == 'Approved'])
    rejected_requests = len([r for r in my_requests if r.status == 'Rejected'])

    return render_template(
        'student_dashboard.html',
        student=student,
        active_allocation=active_allocation,
        total_requests=total_requests,
        pending_requests=pending_requests,
        approved_requests=approved_requests,
        rejected_requests=rejected_requests
    )

# Current Room Details
@app.route('/student/current-room')
@student_required
def current_room():
    student_id = session.get('user_id')
    student = db.session.get(Student, student_id)
    active_allocation = get_student_active_allocation(student_id)
    return render_template('current_room.html', student=student, active_allocation=active_allocation)

# Request Room Change
@app.route('/student/request-change', methods=['GET', 'POST'])
@student_required
def request_change():
    student_id = session.get('user_id')
    student = db.session.get(Student, student_id)
    active_allocation = get_student_active_allocation(student_id)

    # Check rule: Student can have only one active (Pending) room change request
    existing_pending = RoomChangeRequest.query.filter_by(student_id=student_id, status='Pending').first()

    if request.method == 'POST':
        if existing_pending:
            flash('You already have an active room change request pending admin approval.', 'warning')
            return redirect(url_for('my_requests'))

        requested_room_id = request.form.get('requested_room_id', type=int)
        reason = request.form.get('reason', '').strip()

        if not requested_room_id or not reason:
            flash('Please select a requested room and specify a reason.', 'danger')
            return redirect(url_for('request_change'))

        requested_room = db.session.get(Room, requested_room_id)
        if not requested_room:
            flash('Selected room does not exist.', 'danger')
            return redirect(url_for('request_change'))

        # Check rule: Cannot request same room as current room
        current_room_id = active_allocation.room_id if active_allocation else None
        if current_room_id and requested_room_id == current_room_id:
            flash('Requested room cannot be the same as your current room.', 'danger')
            return redirect(url_for('request_change'))

        request_id = generate_unique_request_id()

        change_request = RoomChangeRequest(
            request_id=request_id,
            student_id=student_id,
            current_room_id=current_room_id,
            requested_room_id=requested_room_id,
            reason=reason,
            request_date=date.today(),
            status='Pending'
        )
        db.session.add(change_request)
        db.session.commit()

        flash(f'Room change request submitted successfully! Request ID: {request_id}', 'success')
        return redirect(url_for('my_requests'))

    rooms = Room.query.order_by(Room.hostel_name, Room.room_number).all()
    today_str = date.today().strftime('%Y-%m-%d')
    generated_id = generate_unique_request_id()

    return render_template(
        'request_change.html',
        student=student,
        active_allocation=active_allocation,
        rooms=rooms,
        today_str=today_str,
        generated_id=generated_id,
        existing_pending=existing_pending
    )

# My Room Change Requests
@app.route('/student/my-requests')
@student_required
def my_requests():
    student_id = session.get('user_id')
    student = db.session.get(Student, student_id)
    requests_list = RoomChangeRequest.query.filter_by(student_id=student_id).order_by(RoomChangeRequest.created_at.desc()).all()
    return render_template('my_requests.html', student=student, requests=requests_list)

# Request Details
@app.route('/request-details/<string:request_id>')
def request_details(request_id):
    req = RoomChangeRequest.query.filter_by(request_id=request_id).first_or_404()

    # Authorization check: Student can view only their own request, Admin can view all
    if session.get('user_type') == 'student' and session.get('user_id') != req.student_id:
        flash('You are not authorized to view this request.', 'danger')
        return redirect(url_for('my_requests'))
    elif 'user_type' not in session:
        flash('Please log in to view request details.', 'warning')
        return redirect(url_for('login'))

    return render_template('request_details.html', req=req)

# Admin Dashboard
@app.route('/admin/dashboard')
@admin_required
def admin_dashboard():
    total_students = Student.query.count()
    requests_list = RoomChangeRequest.query.order_by(RoomChangeRequest.created_at.desc()).all()
    total_requests = len(requests_list)
    pending_requests = len([r for r in requests_list if r.status == 'Pending'])
    approved_requests = len([r for r in requests_list if r.status == 'Approved'])
    rejected_requests = len([r for r in requests_list if r.status == 'Rejected'])
    students = Student.query.order_by(Student.created_at.desc()).all()
    total_rooms = Room.query.count()

    return render_template(
        'admin_dashboard.html',
        total_students=total_students,
        total_requests=total_requests,
        pending_requests=pending_requests,
        approved_requests=approved_requests,
        rejected_requests=rejected_requests,
        students=students,
        total_rooms=total_rooms
    )

# Room Management - List Rooms
@app.route('/admin/manage-rooms')
@admin_required
def manage_rooms():
    rooms = Room.query.order_by(Room.hostel_name, Room.room_number).all()
    return render_template('manage_rooms.html', rooms=rooms)

# Room Management - Add Room
@app.route('/admin/add-room', methods=['GET', 'POST'])
@admin_required
def add_room():
    if request.method == 'POST':
        room_number = request.form.get('room_number', '').strip()
        hostel_name = request.form.get('hostel_name', '').strip()
        room_type = request.form.get('room_type', '').strip()
        capacity = request.form.get('capacity', type=int)
        available_beds = request.form.get('available_beds', type=int)

        if not room_number or not hostel_name or not room_type or capacity is None or available_beds is None:
            flash('All fields are required.', 'danger')
            return redirect(url_for('add_room'))

        if capacity <= 0 or available_beds < 0:
            flash('Capacity must be > 0 and Available Beds cannot be negative.', 'danger')
            return redirect(url_for('add_room'))

        if available_beds > capacity:
            flash('Available beds cannot exceed room capacity.', 'danger')
            return redirect(url_for('add_room'))

        existing_room = Room.query.filter_by(room_number=room_number).first()
        if existing_room:
            flash(f'Room number "{room_number}" already exists.', 'danger')
            return redirect(url_for('add_room'))

        room = Room(
            room_number=room_number,
            hostel_name=hostel_name,
            room_type=room_type,
            capacity=capacity,
            available_beds=available_beds
        )
        db.session.add(room)
        db.session.commit()

        flash(f'Room {room_number} ({hostel_name}) added successfully!', 'success')
        return redirect(url_for('manage_rooms'))

    return render_template('add_room.html')

# Room Management - Edit Room
@app.route('/admin/edit-room/<int:room_id>', methods=['GET', 'POST'])
@admin_required
def edit_room(room_id):
    room = Room.query.get_or_404(room_id)

    if request.method == 'POST':
        room_number = request.form.get('room_number', '').strip()
        hostel_name = request.form.get('hostel_name', '').strip()
        room_type = request.form.get('room_type', '').strip()
        capacity = request.form.get('capacity', type=int)
        available_beds = request.form.get('available_beds', type=int)

        if not room_number or not hostel_name or not room_type or capacity is None or available_beds is None:
            flash('All fields are required.', 'danger')
            return redirect(url_for('edit_room', room_id=room.id))

        if capacity <= 0 or available_beds < 0:
            flash('Capacity must be > 0 and Available Beds cannot be negative.', 'danger')
            return redirect(url_for('edit_room', room_id=room.id))

        if available_beds > capacity:
            flash('Available beds cannot exceed room capacity.', 'danger')
            return redirect(url_for('edit_room', room_id=room.id))

        existing_room = Room.query.filter(Room.room_number == room_number, Room.id != room.id).first()
        if existing_room:
            flash(f'Room number "{room_number}" is already used by another room.', 'danger')
            return redirect(url_for('edit_room', room_id=room.id))

        room.room_number = room_number
        room.hostel_name = hostel_name
        room.room_type = room_type
        room.capacity = capacity
        room.available_beds = available_beds

        db.session.commit()
        flash(f'Room {room_number} details updated successfully!', 'success')
        return redirect(url_for('manage_rooms'))

    return render_template('edit_room.html', room=room)

# Room Management - Delete Room
@app.route('/admin/delete-room/<int:room_id>', methods=['POST'])
@admin_required
def delete_room(room_id):
    room = Room.query.get_or_404(room_id)
    db.session.delete(room)
    db.session.commit()
    flash('Room deleted successfully.', 'info')
    return redirect(url_for('manage_rooms'))

# Admin Manage Requests (Filter and Search)
@app.route('/admin/manage-requests')
@admin_required
def manage_requests():
    status_filter = request.args.get('status', '').strip()
    search_query = request.args.get('q', '').strip()

    query = RoomChangeRequest.query.join(Student)

    if status_filter in ['Pending', 'Approved', 'Rejected']:
        query = query.filter(RoomChangeRequest.status == status_filter)

    if search_query:
        search_pattern = f"%{search_query}%"
        query = query.filter(
            (RoomChangeRequest.request_id.like(search_pattern)) |
            (Student.name.like(search_pattern)) |
            (Student.register_number.like(search_pattern))
        )

    requests_list = query.order_by(RoomChangeRequest.created_at.desc()).all()

    return render_template(
        'manage_requests.html',
        requests=requests_list,
        status_filter=status_filter,
        search_query=search_query
    )

# Admin Approve Request
@app.route('/admin/approve-request/<int:request_db_id>', methods=['POST'])
@admin_required
def approve_request(request_db_id):
    req = RoomChangeRequest.query.get_or_404(request_db_id)

    if req.status != 'Pending':
        flash('This request has already been processed.', 'warning')
        return redirect(url_for('manage_requests'))

    requested_room = req.requested_room
    if not requested_room:
        flash('Requested room does not exist.', 'danger')
        return redirect(url_for('manage_requests'))

    # Check rule: Requested room must have an available bed
    if requested_room.available_beds <= 0:
        flash(f'Cannot approve request: Room {requested_room.room_number} has no available beds.', 'danger')
        return redirect(url_for('manage_requests'))

    admin_remarks = request.form.get('admin_remarks', '').strip() or 'Approved by Admin.'

    # Update student room allocation
    current_active_alloc = RoomAllocation.query.filter_by(student_id=req.student_id, status='Active').first()

    if current_active_alloc:
        # Deactivate previous room allocation
        current_active_alloc.status = 'Inactive'
        old_room = current_active_alloc.room
        if old_room:
            # Increase available beds in previous room
            old_room.available_beds = min(old_room.capacity, old_room.available_beds + 1)

    # Allocate new room to student
    new_alloc = RoomAllocation(
        student_id=req.student_id,
        room_id=requested_room.id,
        allocation_date=date.today(),
        status='Active'
    )
    db.session.add(new_alloc)

    # Decrease available beds in new room
    requested_room.available_beds -= 1

    # Update request status
    req.status = 'Approved'
    req.admin_remarks = admin_remarks

    db.session.commit()

    flash(f'Request {req.request_id} approved successfully! Student room updated to {requested_room.room_number}.', 'success')
    return redirect(url_for('manage_requests'))

# Admin Reject Request
@app.route('/admin/reject-request/<int:request_db_id>', methods=['POST'])
@admin_required
def reject_request(request_db_id):
    req = RoomChangeRequest.query.get_or_404(request_db_id)

    if req.status != 'Pending':
        flash('This request has already been processed.', 'warning')
        return redirect(url_for('manage_requests'))

    admin_remarks = request.form.get('admin_remarks', '').strip() or 'Rejected by Admin.'

    req.status = 'Rejected'
    req.admin_remarks = admin_remarks

    db.session.commit()

    flash(f'Request {req.request_id} rejected.', 'info')
    return redirect(url_for('manage_requests'))

# Admin Delete Request
@app.route('/admin/delete-request/<int:request_db_id>', methods=['POST'])
@admin_required
def delete_request(request_db_id):
    req = RoomChangeRequest.query.get_or_404(request_db_id)
    db.session.delete(req)
    db.session.commit()

    flash(f'Request {req.request_id} deleted successfully.', 'info')
    return redirect(url_for('manage_requests'))

# Admin Initial Room Allocation route (Optional/Utility helper for student initial allocation)
@app.route('/admin/assign-room', methods=['POST'])
@admin_required
def assign_room():
    student_id = request.form.get('student_id', type=int)
    room_id = request.form.get('room_id', type=int)

    student = db.session.get(Student, student_id)
    room = db.session.get(Room, room_id)

    if not student or not room:
        flash('Invalid student or room selection.', 'danger')
        return redirect(url_for('admin_dashboard'))

    if room.available_beds <= 0:
        flash(f'Room {room.room_number} has no available beds.', 'danger')
        return redirect(url_for('admin_dashboard'))

    # Deactivate existing active allocation
    existing_alloc = get_student_active_allocation(student.id)
    if existing_alloc:
        existing_alloc.status = 'Inactive'
        if existing_alloc.room:
            existing_alloc.room.available_beds = min(existing_alloc.room.capacity, existing_alloc.room.available_beds + 1)

    new_alloc = RoomAllocation(
        student_id=student.id,
        room_id=room.id,
        allocation_date=date.today(),
        status='Active'
    )
    db.session.add(new_alloc)
    room.available_beds -= 1

    db.session.commit()
    flash(f'Room {room.room_number} assigned to student {student.name}.', 'success')
    return redirect(url_for('admin_dashboard'))


if __name__ == '__main__':
    with app.app_context():
        db.create_all()
        seed_default_data()
    app.run(debug=True)
