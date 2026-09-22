import os
from datetime import datetime, date
from functools import wraps
from flask import Flask, render_template, request, redirect, url_for, flash, session
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'college_sports_booking_secret_key_123')

# Admin Hardcoded Credentials
ADMIN_USERNAME = os.environ.get('ADMIN_USERNAME', 'admin')
ADMIN_PASSWORD = os.environ.get('ADMIN_PASSWORD', 'admin123')

# Database configuration: Default to MySQL URI, fallback/option for SQLite
MYSQL_URI = os.environ.get('DATABASE_URL', 'mysql+pymysql://root:@localhost/sports_booking_db')
SQLITE_URI = 'sqlite:///' + os.path.join(os.path.abspath(os.path.dirname(__file__)), 'sports_booking.db')

use_sqlite = os.environ.get('USE_SQLITE') == '1'
app.config['SQLALCHEMY_DATABASE_URI'] = SQLITE_URI if use_sqlite else MYSQL_URI
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

class Student(db.Model):
    __tablename__ = 'students'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    register_number = db.Column(db.String(50), unique=True, nullable=False)
    department = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    bookings = db.relationship('Booking', backref='student', lazy=True)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

class Equipment(db.Model):
    __tablename__ = 'equipment'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    category = db.Column(db.String(50), nullable=False)
    total_quantity = db.Column(db.Integer, nullable=False, default=0)
    available_quantity = db.Column(db.Integer, nullable=False, default=0)
    description = db.Column(db.Text, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    bookings = db.relationship('Booking', backref='equipment', lazy=True)

class Booking(db.Model):
    __tablename__ = 'bookings'
    id = db.Column(db.Integer, primary_key=True)
    student_id = db.Column(db.Integer, db.ForeignKey('students.id'), nullable=False)
    equipment_id = db.Column(db.Integer, db.ForeignKey('equipment.id'), nullable=False)
    booking_date = db.Column(db.Date, nullable=False)
    quantity = db.Column(db.Integer, nullable=False, default=1)
    status = db.Column(db.String(20), default='Pending') # Pending, Approved, Rejected, Returned
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

def seed_default_data():
    if Equipment.query.count() == 0:
        items = [
            Equipment(name='Cricket Bat', category='Cricket', total_quantity=15, available_quantity=15, description='English Willow Quality Cricket Bat'),
            Equipment(name='Cricket Ball', category='Cricket', total_quantity=30, available_quantity=30, description='Standard Red Leather Cricket Ball'),
            Equipment(name='Football', category='Football', total_quantity=20, available_quantity=20, description='Size 5 Tournament Football'),
            Equipment(name='Volleyball', category='Volleyball', total_quantity=12, available_quantity=12, description='Official Match Size Volleyball'),
            Equipment(name='Volleyball Net', category='Volleyball', total_quantity=4, available_quantity=4, description='Durable Nylon Volleyball Net'),
            Equipment(name='Badminton Racket', category='Badminton', total_quantity=25, available_quantity=25, description='Lightweight Graphite Badminton Racket'),
            Equipment(name='Shuttlecocks (Box)', category='Badminton', total_quantity=15, available_quantity=15, description='Feather Shuttlecock Box of 10'),
            Equipment(name='Basketball', category='Basketball', total_quantity=10, available_quantity=10, description='Composite Leather Basketball'),
        ]
        db.session.add_all(items)
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
        department = request.form.get('department', '').strip()
        email = request.form.get('email', '').strip().lower()
        password = request.form.get('password', '')

        if not name or not register_number or not department or not email or not password:
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
            department=department,
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

# Student Dashboard & Equipment Booking
@app.route('/student/dashboard')
@student_required
def student_dashboard():
    student_id = session.get('user_id')
    student = Student.query.get(student_id)
    equipments = Equipment.query.all()
    my_bookings = Booking.query.filter_by(student_id=student_id).order_by(Booking.created_at.desc()).all()
    today_str = date.today().isoformat()
    return render_template('student_dashboard.html', student=student, equipments=equipments, bookings=my_bookings, today=today_str)

@app.route('/student/book', methods=['POST'])
@student_required
def book_equipment():
    student_id = session.get('user_id')
    equipment_id = request.form.get('equipment_id', type=int)
    booking_date_str = request.form.get('booking_date', '')
    quantity = request.form.get('quantity', type=int, default=1)

    if not equipment_id or not booking_date_str or quantity <= 0:
        flash('Invalid booking details.', 'danger')
        return redirect(url_for('student_dashboard'))

    try:
        booking_date = datetime.strptime(booking_date_str, '%Y-%m-%d').date()
    except ValueError:
        flash('Invalid date format.', 'danger')
        return redirect(url_for('student_dashboard'))

    if booking_date < date.today():
        flash('Booking date cannot be in the past.', 'danger')
        return redirect(url_for('student_dashboard'))

    equipment = Equipment.query.get(equipment_id)
    if not equipment:
        flash('Equipment not found.', 'danger')
        return redirect(url_for('student_dashboard'))

    if equipment.available_quantity <= 0:
        flash(f'Sorry, {equipment.name} is currently out of stock.', 'danger')
        return redirect(url_for('student_dashboard'))

    if quantity > equipment.available_quantity:
        flash(f'Requested quantity ({quantity}) exceeds available stock ({equipment.available_quantity}).', 'danger')
        return redirect(url_for('student_dashboard'))

    booking = Booking(
        student_id=student_id,
        equipment_id=equipment_id,
        booking_date=booking_date,
        quantity=quantity,
        status='Pending'
    )
    db.session.add(booking)
    db.session.commit()

    flash(f'Booking request submitted for {quantity} x {equipment.name} on {booking_date}. Awaiting Admin approval.', 'success')
    return redirect(url_for('student_dashboard'))

# Admin Dashboard & Equipment Management
@app.route('/admin/dashboard')
@admin_required
def admin_dashboard():
    equipments = Equipment.query.all()
    bookings = Booking.query.order_by(Booking.created_at.desc()).all()

    # Simple statistics
    total_equipments = len(equipments)
    total_bookings = len(bookings)
    pending_count = len([b for b in bookings if b.status == 'Pending'])
    approved_count = len([b for b in bookings if b.status == 'Approved'])

    return render_template(
        'admin_dashboard.html',
        equipments=equipments,
        bookings=bookings,
        total_equipments=total_equipments,
        total_bookings=total_bookings,
        pending_count=pending_count,
        approved_count=approved_count
    )

@app.route('/admin/equipment/add', methods=['POST'])
@admin_required
def add_equipment():
    name = request.form.get('name', '').strip()
    category = request.form.get('category', '').strip()
    total_quantity = request.form.get('total_quantity', type=int, default=0)
    description = request.form.get('description', '').strip()

    if not name or not category or total_quantity <= 0:
        flash('Name, category, and total quantity (>0) are required.', 'danger')
        return redirect(url_for('admin_dashboard'))

    equipment = Equipment(
        name=name,
        category=category,
        total_quantity=total_quantity,
        available_quantity=total_quantity,
        description=description
    )
    db.session.add(equipment)
    db.session.commit()
    flash(f'Equipment "{name}" added successfully.', 'success')
    return redirect(url_for('admin_dashboard'))

@app.route('/admin/equipment/update/<int:equipment_id>', methods=['POST'])
@admin_required
def update_equipment(equipment_id):
    equipment = Equipment.query.get_or_404(equipment_id)
    name = request.form.get('name', '').strip()
    category = request.form.get('category', '').strip()
    total_quantity = request.form.get('total_quantity', type=int)
    available_quantity = request.form.get('available_quantity', type=int)
    description = request.form.get('description', '').strip()

    if name:
        equipment.name = name
    if category:
        equipment.category = category
    if total_quantity is not None and total_quantity >= 0:
        equipment.total_quantity = total_quantity
    if available_quantity is not None and available_quantity >= 0:
        if available_quantity > equipment.total_quantity:
            flash('Available quantity cannot exceed total quantity.', 'danger')
            return redirect(url_for('admin_dashboard'))
        equipment.available_quantity = available_quantity
    equipment.description = description

    db.session.commit()
    flash(f'Equipment "{equipment.name}" updated successfully.', 'success')
    return redirect(url_for('admin_dashboard'))

@app.route('/admin/equipment/delete/<int:equipment_id>', methods=['POST'])
@admin_required
def delete_equipment(equipment_id):
    equipment = Equipment.query.get_or_404(equipment_id)
    db.session.delete(equipment)
    db.session.commit()
    flash('Equipment deleted successfully.', 'info')
    return redirect(url_for('admin_dashboard'))

@app.route('/admin/booking/approve/<int:booking_id>', methods=['POST'])
@admin_required
def approve_booking(booking_id):
    booking = Booking.query.get_or_404(booking_id)
    if booking.status != 'Pending':
        flash('Only pending bookings can be approved.', 'warning')
        return redirect(url_for('admin_dashboard'))

    equipment = booking.equipment
    if equipment.available_quantity < booking.quantity:
        flash(f'Insufficient available stock for {equipment.name}. Available: {equipment.available_quantity}, Requested: {booking.quantity}', 'danger')
        return redirect(url_for('admin_dashboard'))

    # Deduct stock on approval
    equipment.available_quantity -= booking.quantity
    booking.status = 'Approved'
    db.session.commit()

    flash(f'Booking #{booking.id} approved successfully.', 'success')
    return redirect(url_for('admin_dashboard'))

@app.route('/admin/booking/reject/<int:booking_id>', methods=['POST'])
@admin_required
def reject_booking(booking_id):
    booking = Booking.query.get_or_404(booking_id)
    if booking.status not in ['Pending', 'Approved']:
        flash('Booking status cannot be rejected.', 'warning')
        return redirect(url_for('admin_dashboard'))

    # If it was approved earlier, return stock
    if booking.status == 'Approved':
        booking.equipment.available_quantity += booking.quantity

    booking.status = 'Rejected'
    db.session.commit()

    flash(f'Booking #{booking.id} rejected.', 'info')
    return redirect(url_for('admin_dashboard'))

@app.route('/admin/booking/return/<int:booking_id>', methods=['POST'])
@admin_required
def return_booking(booking_id):
    booking = Booking.query.get_or_404(booking_id)
    if booking.status != 'Approved':
        flash('Only approved bookings can be marked as returned.', 'warning')
        return redirect(url_for('admin_dashboard'))

    # Restock equipment
    booking.equipment.available_quantity += booking.quantity
    # Prevent available quantity from exceeding total quantity
    if booking.equipment.available_quantity > booking.equipment.total_quantity:
        booking.equipment.available_quantity = booking.equipment.total_quantity

    booking.status = 'Returned'
    db.session.commit()

    flash(f'Equipment for Booking #{booking.id} marked as Returned. Stock updated (+{booking.quantity}).', 'success')
    return redirect(url_for('admin_dashboard'))

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
        seed_default_data()
    app.run(debug=True)
