import os
from datetime import datetime, date, timezone
from functools import wraps
from flask import Flask, render_template, request, redirect, url_for, flash, session
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'service_booking_secret_key_2025')

# Admin Credentials Defaults
ADMIN_DEFAULT_USERNAME = os.environ.get('ADMIN_USERNAME', 'admin')
ADMIN_DEFAULT_PASSWORD = os.environ.get('ADMIN_PASSWORD', 'admin123')

# Database configuration: Default to MySQL URI, fallback/option for SQLite
MYSQL_URI = os.environ.get('DATABASE_URL', 'mysql+pymysql://root:@localhost/service_booking_db')
SQLITE_URI = 'sqlite:///' + os.path.join(os.path.abspath(os.path.dirname(__file__)), 'service_booking.db')

use_sqlite = os.environ.get('USE_SQLITE') == '1'
app.config['SQLALCHEMY_DATABASE_URI'] = SQLITE_URI if use_sqlite else MYSQL_URI
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)


def utc_now():
    return datetime.now(timezone.utc)


# Models
class Admin(db.Model):
    __tablename__ = 'admins'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    name = db.Column(db.String(100), nullable=False, default='Administrator')
    created_at = db.Column(db.DateTime, default=utc_now)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)


class Customer(db.Model):
    __tablename__ = 'customers'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    phone = db.Column(db.String(20), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    created_at = db.Column(db.DateTime, default=utc_now)

    bookings = db.relationship('Booking', backref='customer', lazy=True, cascade="all, delete-orphan")

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)


class Service(db.Model):
    __tablename__ = 'services'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text, nullable=False)
    price = db.Column(db.Float, nullable=False)
    duration = db.Column(db.String(50), nullable=False)  # e.g., "1 Hour", "2 Hours"
    availability = db.Column(db.String(50), nullable=False, default='Available')  # "Available", "Unavailable"
    created_at = db.Column(db.DateTime, default=utc_now)

    bookings = db.relationship('Booking', backref='service', lazy=True, cascade="all, delete-orphan")


class Booking(db.Model):
    __tablename__ = 'bookings'
    id = db.Column(db.Integer, primary_key=True)
    customer_id = db.Column(db.Integer, db.ForeignKey('customers.id'), nullable=False)
    service_id = db.Column(db.Integer, db.ForeignKey('services.id'), nullable=False)
    booking_date = db.Column(db.Date, nullable=False)
    booking_time = db.Column(db.String(20), nullable=False)
    customer_name = db.Column(db.String(100), nullable=False)
    customer_phone = db.Column(db.String(20), nullable=False)
    notes = db.Column(db.Text, nullable=True)
    status = db.Column(db.String(20), nullable=False, default='Pending')  # Pending, Confirmed, Completed, Cancelled
    created_at = db.Column(db.DateTime, default=utc_now)


def seed_default_data():
    # Seed default Admin if none exists
    if Admin.query.count() == 0:
        default_admin = Admin(username=ADMIN_DEFAULT_USERNAME, name='System Admin')
        default_admin.set_password(ADMIN_DEFAULT_PASSWORD)
        db.session.add(default_admin)

    # Seed default Services if none exist
    if Service.query.count() == 0:
        sample_services = [
            Service(
                name='Deep House Cleaning',
                description='Comprehensive deep cleaning service for home bedrooms, kitchen, living room, and bathrooms.',
                price=89.99,
                duration='3 Hours',
                availability='Available'
            ),
            Service(
                name='AC Maintenance & Repair',
                description='Complete air conditioner inspection, filter cleaning, refrigerant refill, and cooling test.',
                price=49.99,
                duration='1.5 Hours',
                availability='Available'
            ),
            Service(
                name='Car Wash & Detailing',
                description='Premium exterior eco-wash, interior vacuuming, dashboard polish, and tire shining.',
                price=35.00,
                duration='1 Hour',
                availability='Available'
            ),
            Service(
                name='Plumbing Repair & Inspection',
                description='Fixing pipe leaks, tap installations, drain cleaning, and water pressure checks.',
                price=55.00,
                duration='2 Hours',
                availability='Available'
            ),
            Service(
                name='Electrical Safety Audit & Fix',
                description='Wiring inspection, circuit breaker repair, switch installation, and electrical troubleshooting.',
                price=60.00,
                duration='2 Hours',
                availability='Available'
            )
        ]
        db.session.add_all(sample_services)

    db.session.commit()


# Authentication Decorators
def customer_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if session.get('user_type') != 'customer':
            flash('Please log in as a customer to access this page.', 'warning')
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function


def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if session.get('user_type') != 'admin':
            flash('Admin authentication required.', 'warning')
            return redirect(url_for('admin_login'))
        return f(*args, **kwargs)
    return decorated_function


# General Routes
@app.route('/')
def index():
    services = Service.query.filter_by(availability='Available').limit(6).all()
    return render_template('index.html', services=services)


# Customer Authentication Routes
@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        name = request.form.get('name', '').strip()
        phone = request.form.get('phone', '').strip()
        email = request.form.get('email', '').strip().lower()
        password = request.form.get('password', '')

        if not name or not phone or not email or not password:
            flash('All registration fields are required.', 'danger')
            return redirect(url_for('register'))

        existing_customer = Customer.query.filter_by(email=email).first()
        if existing_customer:
            flash('An account with this email address already exists.', 'danger')
            return redirect(url_for('register'))

        customer = Customer(name=name, phone=phone, email=email)
        customer.set_password(password)
        db.session.add(customer)
        db.session.commit()

        flash('Registration successful! You can now log in.', 'success')
        return redirect(url_for('login'))

    return render_template('register.html')


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form.get('email', '').strip().lower()
        password = request.form.get('password', '')

        customer = Customer.query.filter_by(email=email).first()
        if customer and customer.check_password(password):
            session['user_type'] = 'customer'
            session['customer_id'] = customer.id
            session['customer_name'] = customer.name
            session['customer_email'] = customer.email
            session['customer_phone'] = customer.phone
            flash(f'Welcome back, {customer.name}!', 'success')
            return redirect(url_for('customer_dashboard'))
        else:
            flash('Invalid email or password. Please try again.', 'danger')
            return redirect(url_for('login'))

    return render_template('login.html')


@app.route('/logout')
def logout():
    session.clear()
    flash('You have been logged out successfully.', 'info')
    return redirect(url_for('index'))


# Customer Module Routes
@app.route('/customer/dashboard')
@customer_required
def customer_dashboard():
    customer_id = session.get('customer_id')
    customer = db.get_or_404(Customer, customer_id)
    bookings = Booking.query.filter_by(customer_id=customer_id).order_by(Booking.created_at.desc()).all()

    total_bookings = len(bookings)
    pending_bookings = len([b for b in bookings if b.status == 'Pending'])
    confirmed_bookings = len([b for b in bookings if b.status == 'Confirmed'])
    completed_bookings = len([b for b in bookings if b.status == 'Completed'])

    recent_bookings = bookings[:5]

    return render_template(
        'customer_dashboard.html',
        customer=customer,
        total_bookings=total_bookings,
        pending_bookings=pending_bookings,
        confirmed_bookings=confirmed_bookings,
        completed_bookings=completed_bookings,
        recent_bookings=recent_bookings
    )


@app.route('/services')
def services():
    all_services = Service.query.all()
    return render_template('services.html', services=all_services)


@app.route('/book-service', methods=['GET', 'POST'])
@app.route('/book-service/<int:service_id>', methods=['GET', 'POST'])
@customer_required
def book_service(service_id=None):
    selected_service = db.session.get(Service, service_id) if service_id else None
    available_services = Service.query.filter_by(availability='Available').all()

    if request.method == 'POST':
        srv_id = request.form.get('service_id', type=int)
        pref_date_str = request.form.get('preferred_date', '')
        pref_time = request.form.get('preferred_time', '').strip()
        cust_name = request.form.get('customer_name', '').strip()
        cust_phone = request.form.get('customer_phone', '').strip()
        notes = request.form.get('notes', '').strip()

        if not srv_id or not pref_date_str or not pref_time or not cust_name or not cust_phone:
            flash('Please fill in all required booking details.', 'danger')
            return redirect(url_for('book_service', service_id=srv_id if srv_id else ''))

        service = db.session.get(Service, srv_id)
        if not service:
            flash('Selected service was not found.', 'danger')
            return redirect(url_for('services'))

        if service.availability != 'Available':
            flash('Selected service is currently unavailable for booking.', 'warning')
            return redirect(url_for('services'))

        try:
            pref_date = datetime.strptime(pref_date_str, '%Y-%m-%d').date()
        except ValueError:
            flash('Invalid date format.', 'danger')
            return redirect(url_for('book_service', service_id=srv_id))

        if pref_date < date.today():
            flash('Preferred date cannot be in the past.', 'danger')
            return redirect(url_for('book_service', service_id=srv_id))

        customer_id = session.get('customer_id')

        booking = Booking(
            customer_id=customer_id,
            service_id=service.id,
            booking_date=pref_date,
            booking_time=pref_time,
            customer_name=cust_name,
            customer_phone=cust_phone,
            notes=notes,
            status='Pending'
        )

        db.session.add(booking)
        db.session.commit()

        flash(f'Booking for "{service.name}" submitted successfully! Status is Pending.', 'success')
        return redirect(url_for('my_bookings'))

    today_str = date.today().isoformat()
    return render_template(
        'book_service.html',
        selected_service=selected_service,
        available_services=available_services,
        today=today_str
    )


@app.route('/my-bookings')
@customer_required
def my_bookings():
    customer_id = session.get('customer_id')
    bookings = Booking.query.filter_by(customer_id=customer_id).order_by(Booking.created_at.desc()).all()
    return render_template('my_bookings.html', bookings=bookings)


# Admin Authentication Routes
@app.route('/admin/login', methods=['GET', 'POST'])
def admin_login():
    if request.method == 'POST':
        username = request.form.get('username', '').strip()
        password = request.form.get('password', '')

        admin = Admin.query.filter_by(username=username).first()
        if admin and admin.check_password(password):
            session['user_type'] = 'admin'
            session['admin_id'] = admin.id
            session['admin_name'] = admin.username
            flash('Logged in successfully as Administrator.', 'success')
            return redirect(url_for('admin_dashboard'))
        else:
            flash('Invalid admin credentials.', 'danger')
            return redirect(url_for('admin_login'))

    return render_template('admin_login.html')


# Admin Dashboard Routes
@app.route('/admin/dashboard')
@admin_required
def admin_dashboard():
    total_customers = Customer.query.count()
    total_services = Service.query.count()
    bookings = Booking.query.order_by(Booking.created_at.desc()).all()

    total_bookings = len(bookings)
    pending_bookings = len([b for b in bookings if b.status == 'Pending'])
    confirmed_bookings = len([b for b in bookings if b.status == 'Confirmed'])
    completed_bookings = len([b for b in bookings if b.status == 'Completed'])

    recent_bookings = bookings[:5]
    recent_customers = Customer.query.order_by(Customer.created_at.desc()).limit(5).all()

    return render_template(
        'admin_dashboard.html',
        total_customers=total_customers,
        total_services=total_services,
        total_bookings=total_bookings,
        pending_bookings=pending_bookings,
        confirmed_bookings=confirmed_bookings,
        completed_bookings=completed_bookings,
        recent_bookings=recent_bookings,
        recent_customers=recent_customers
    )


# Admin Service Management
@app.route('/admin/services', methods=['GET'])
@admin_required
def manage_services():
    services_list = Service.query.order_by(Service.id.desc()).all()
    return render_template('manage_services.html', services=services_list)


@app.route('/admin/services/add', methods=['POST'])
@admin_required
def add_service():
    name = request.form.get('name', '').strip()
    description = request.form.get('description', '').strip()
    price = request.form.get('price', type=float)
    duration = request.form.get('duration', '').strip()
    availability = request.form.get('availability', 'Available').strip()

    if not name or not description or price is None or price < 0 or not duration:
        flash('All service fields are required with a valid non-negative price.', 'danger')
        return redirect(url_for('manage_services'))

    service = Service(
        name=name,
        description=description,
        price=price,
        duration=duration,
        availability=availability
    )

    db.session.add(service)
    db.session.commit()

    flash(f'Service "{name}" added successfully.', 'success')
    return redirect(url_for('manage_services'))


@app.route('/admin/services/edit/<int:service_id>', methods=['POST'])
@admin_required
def edit_service(service_id):
    service = db.get_or_404(Service, service_id)

    name = request.form.get('name', '').strip()
    description = request.form.get('description', '').strip()
    price = request.form.get('price', type=float)
    duration = request.form.get('duration', '').strip()
    availability = request.form.get('availability', service.availability).strip()

    if not name or not description or price is None or price < 0 or not duration:
        flash('Invalid service data provided for update.', 'danger')
        return redirect(url_for('manage_services'))

    service.name = name
    service.description = description
    service.price = price
    service.duration = duration
    service.availability = availability

    db.session.commit()
    flash(f'Service "{service.name}" updated successfully.', 'success')
    return redirect(url_for('manage_services'))


@app.route('/admin/services/delete/<int:service_id>', methods=['POST'])
@admin_required
def delete_service(service_id):
    service = db.get_or_404(Service, service_id)
    name = service.name
    db.session.delete(service)
    db.session.commit()
    flash(f'Service "{name}" deleted successfully.', 'info')
    return redirect(url_for('manage_services'))


# Admin Booking Management
@app.route('/admin/bookings', methods=['GET'])
@admin_required
def manage_bookings():
    selected_service_id = request.args.get('service_id', type=int)
    selected_date = request.args.get('booking_date', '')
    selected_status = request.args.get('status', '')

    query = Booking.query

    if selected_service_id:
        query = query.filter_by(service_id=selected_service_id)
    if selected_date:
        try:
            d = datetime.strptime(selected_date, '%Y-%m-%d').date()
            query = query.filter_by(booking_date=d)
        except ValueError:
            pass
    if selected_status:
        query = query.filter_by(status=selected_status)

    bookings_list = query.order_by(Booking.created_at.desc()).all()
    services_list = Service.query.all()

    return render_template(
        'manage_bookings.html',
        bookings=bookings_list,
        services=services_list,
        selected_service_id=selected_service_id,
        selected_date=selected_date,
        selected_status=selected_status
    )


@app.route('/admin/bookings/details/<int:booking_id>')
@admin_required
def booking_details(booking_id):
    booking = db.get_or_404(Booking, booking_id)
    return render_template('booking_details.html', booking=booking)


@app.route('/admin/bookings/confirm/<int:booking_id>', methods=['POST'])
@admin_required
def confirm_booking(booking_id):
    booking = db.get_or_404(Booking, booking_id)
    booking.status = 'Confirmed'
    db.session.commit()
    flash(f'Booking #{booking.id} confirmed.', 'success')
    return redirect(request.referrer or url_for('manage_bookings'))


@app.route('/admin/bookings/complete/<int:booking_id>', methods=['POST'])
@admin_required
def complete_booking(booking_id):
    booking = db.get_or_404(Booking, booking_id)
    booking.status = 'Completed'
    db.session.commit()
    flash(f'Booking #{booking.id} marked as Completed.', 'success')
    return redirect(request.referrer or url_for('manage_bookings'))


@app.route('/admin/bookings/cancel/<int:booking_id>', methods=['POST'])
@admin_required
def cancel_booking(booking_id):
    booking = db.get_or_404(Booking, booking_id)
    booking.status = 'Cancelled'
    db.session.commit()
    flash(f'Booking #{booking.id} cancelled.', 'info')
    return redirect(request.referrer or url_for('manage_bookings'))


@app.route('/admin/bookings/delete/<int:booking_id>', methods=['POST'])
@admin_required
def delete_booking(booking_id):
    booking = db.get_or_404(Booking, booking_id)
    db.session.delete(booking)
    db.session.commit()
    flash(f'Booking #{booking_id} deleted.', 'info')
    return redirect(url_for('manage_bookings'))


# Admin Customer Management
@app.route('/admin/customers', methods=['GET'])
@admin_required
def manage_customers():
    search_query = request.args.get('q', '').strip()
    if search_query:
        customers_list = Customer.query.filter(
            (Customer.name.ilike(f'%{search_query}%')) |
            (Customer.email.ilike(f'%{search_query}%')) |
            (Customer.phone.ilike(f'%{search_query}%'))
        ).order_by(Customer.created_at.desc()).all()
    else:
        customers_list = Customer.query.order_by(Customer.created_at.desc()).all()

    return render_template(
        'manage_customers.html',
        customers=customers_list,
        search_query=search_query
    )


@app.route('/admin/customers/delete/<int:customer_id>', methods=['POST'])
@admin_required
def delete_customer(customer_id):
    customer = db.get_or_404(Customer, customer_id)
    name = customer.name
    db.session.delete(customer)
    db.session.commit()
    flash(f'Customer "{name}" and associated bookings deleted.', 'info')
    return redirect(url_for('manage_customers'))


if __name__ == '__main__':
    with app.app_context():
        db.create_all()
        seed_default_data()
    app.run(debug=True)
