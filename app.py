import os
from datetime import datetime
from functools import wraps
from flask import Flask, render_template, request, redirect, url_for, flash, session
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'library_reservation_secret_key_987')

# Database configuration: Default to MySQL URI, fallback/option for SQLite
MYSQL_URI = os.environ.get('DATABASE_URL', 'mysql+pymysql://root:@localhost/library_db')
SQLITE_URI = 'sqlite:///' + os.path.join(os.path.abspath(os.path.dirname(__file__)), 'library.db')

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

    def set_password(self, password_text):
        self.password = generate_password_hash(password_text)

    def check_password(self, password_text):
        return check_password_hash(self.password, password_text)

class Student(db.Model):
    __tablename__ = 'students'
    id = db.Column(db.Integer, primary_key=True)
    student_name = db.Column(db.String(100), nullable=False)
    register_number = db.Column(db.String(50), unique=True, nullable=False)
    department = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(255), nullable=False)

    reservations = db.relationship('Reservation', backref='student', cascade="all, delete-orphan", lazy=True)

    def set_password(self, password_text):
        self.password = generate_password_hash(password_text)

    def check_password(self, password_text):
        return check_password_hash(self.password, password_text)

class Book(db.Model):
    __tablename__ = 'books'
    id = db.Column(db.Integer, primary_key=True)
    book_name = db.Column(db.String(150), nullable=False)
    author_name = db.Column(db.String(100), nullable=False)
    isbn = db.Column(db.String(30), unique=True, nullable=False)
    category = db.Column(db.String(50), nullable=False)
    description = db.Column(db.Text, nullable=True)
    total_copies = db.Column(db.Integer, nullable=False, default=1)
    available_copies = db.Column(db.Integer, nullable=False, default=1)

    reservations = db.relationship('Reservation', backref='book', cascade="all, delete-orphan", lazy=True)

    @property
    def availability_status(self):
        if self.available_copies <= 0:
            return 'Not Available'
        elif self.available_copies <= 2 and self.total_copies > 2:
            return 'Limited'
        elif self.available_copies == 1 and self.total_copies <= 2:
            return 'Limited'
        return 'Available'

class Reservation(db.Model):
    __tablename__ = 'reservations'
    id = db.Column(db.Integer, primary_key=True)
    student_id = db.Column(db.Integer, db.ForeignKey('students.id'), nullable=False)
    book_id = db.Column(db.Integer, db.ForeignKey('books.id'), nullable=False)
    reservation_date = db.Column(db.DateTime, default=datetime.utcnow)
    status = db.Column(db.String(20), default='Reserved') # Reserved, Cancelled, Completed

def seed_initial_data():
    if Admin.query.count() == 0:
        admin = Admin(username='admin')
        admin.set_password('admin123')
        db.session.add(admin)

    if Book.query.count() == 0:
        sample_books = [
            Book(
                book_name='Python Programming',
                author_name='John Zelle',
                isbn='978-1590282410',
                category='Computer Science',
                description='An introduction to computer science using Python.',
                total_copies=5,
                available_copies=5
            ),
            Book(
                book_name='Data Structures and Algorithms in Python',
                author_name='Michael T. Goodrich',
                isbn='978-1118290279',
                category='Computer Science',
                description='Comprehensive guide to algorithms and data structures.',
                total_copies=3,
                available_copies=2
            ),
            Book(
                book_name='Database System Concepts',
                author_name='Abraham Silberschatz',
                isbn='978-0078022159',
                category='Information Technology',
                description='Fundamental concepts of database design and management.',
                total_copies=4,
                available_copies=1
            ),
            Book(
                book_name='Operating System Concepts',
                author_name='Abraham Silberschatz',
                isbn='978-1118063330',
                category='Computer Science',
                description='Essential operating system principles and architectures.',
                total_copies=2,
                available_copies=0
            ),
            Book(
                book_name='Web Engineering',
                author_name='Gerti Kappel',
                isbn='978-0470015575',
                category='Web Development',
                description='Practices and specifications for web applications.',
                total_copies=6,
                available_copies=6
            )
        ]
        db.session.add_all(sample_books)

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
            return redirect(url_for('admin_login'))
        return f(*args, **kwargs)
    return decorated_function

@app.route('/')
def index():
    return render_template('index.html')

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

        existing_student = Student.query.filter(
            (Student.email == email) | (Student.register_number == register_number)
        ).first()

        if existing_student:
            flash('Student with this Email or Register Number already exists.', 'danger')
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

        flash('Registration successful! Please log in.', 'success')
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
            session['student_id'] = student.id
            session['student_name'] = student.student_name
            flash(f'Welcome back, {student.student_name}!', 'success')
            return redirect(url_for('student_dashboard'))
        else:
            flash('Invalid credentials. Please check your email/register number and password.', 'danger')
            return redirect(url_for('login'))

    return render_template('login.html')

# Admin Login
@app.route('/admin_login', methods=['GET', 'POST'])
@app.route('/admin/login', methods=['GET', 'POST'])
def admin_login():
    if request.method == 'POST':
        username = request.form.get('username', '').strip()
        password = request.form.get('password', '')

        admin = Admin.query.filter_by(username=username).first()

        if admin and admin.check_password(password):
            session['user_type'] = 'admin'
            session['admin_id'] = admin.id
            session['admin_username'] = admin.username
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
    student_id = session.get('student_id')
    student = Student.query.get_or_404(student_id)

    total_books = Book.query.count()
    available_books = Book.query.filter(Book.available_copies > 0).count()
    my_reservations_count = Reservation.query.filter_by(student_id=student_id).count()
    active_reservations_count = Reservation.query.filter_by(student_id=student_id, status='Reserved').count()

    recent_reservations = Reservation.query.filter_by(student_id=student_id).order_by(Reservation.reservation_date.desc()).limit(5).all()

    return render_template(
        'student_dashboard.html',
        student=student,
        total_books=total_books,
        available_books=available_books,
        my_reservations_count=my_reservations_count,
        active_reservations_count=active_reservations_count,
        recent_reservations=recent_reservations
    )

# Book List (Search & Filter)
@app.route('/books')
def books():
    search_query = request.args.get('search', '').strip()
    status_filter = request.args.get('status', '').strip()

    query = Book.query

    if search_query:
        query = query.filter(
            (Book.book_name.ilike(f'%{search_query}%')) |
            (Book.author_name.ilike(f'%{search_query}%')) |
            (Book.isbn.ilike(f'%{search_query}%')) |
            (Book.category.ilike(f'%{search_query}%'))
        )

    all_books = query.all()

    if status_filter:
        filtered_books = [b for b in all_books if b.availability_status == status_filter]
    else:
        filtered_books = all_books

    return render_template('books.html', books=filtered_books, search_query=search_query, status_filter=status_filter)

# Book Details
@app.route('/book/<int:book_id>')
def book_details(book_id):
    book = Book.query.get_or_404(book_id)
    already_reserved = False

    if session.get('user_type') == 'student':
        student_id = session.get('student_id')
        active_res = Reservation.query.filter_by(
            student_id=student_id,
            book_id=book_id,
            status='Reserved'
        ).first()
        if active_res:
            already_reserved = True

    return render_template('book_details.html', book=book, already_reserved=already_reserved)

# Book Reservation
@app.route('/reserve/<int:book_id>', methods=['POST'])
@student_required
def reserve_book(book_id):
    student_id = session.get('student_id')
    book = Book.query.get_or_404(book_id)

    # Check duplicate active reservation
    existing_reservation = Reservation.query.filter_by(
        student_id=student_id,
        book_id=book_id,
        status='Reserved'
    ).first()

    if existing_reservation:
        flash('You already have an active reservation for this book.', 'warning')
        return redirect(url_for('book_details', book_id=book_id))

    # Check available copies
    if book.available_copies <= 0:
        flash('Sorry, this book is currently not available for reservation.', 'danger')
        return redirect(url_for('book_details', book_id=book_id))

    # Reduce available copies
    book.available_copies -= 1

    # Create reservation
    reservation = Reservation(
        student_id=student_id,
        book_id=book_id,
        status='Reserved'
    )
    db.session.add(reservation)
    db.session.commit()

    flash(f'Book "{book.book_name}" reserved successfully!', 'success')
    return redirect(url_for('my_reservations'))

# My Reservations
@app.route('/my_reservations')
@student_required
def my_reservations():
    student_id = session.get('student_id')
    reservations = Reservation.query.filter_by(student_id=student_id).order_by(Reservation.reservation_date.desc()).all()
    return render_template('my_reservations.html', reservations=reservations)

# Cancel Reservation (Student)
@app.route('/cancel_reservation/<int:reservation_id>', methods=['POST'])
@student_required
def cancel_reservation(reservation_id):
    student_id = session.get('student_id')
    reservation = Reservation.query.filter_by(id=reservation_id, student_id=student_id).first_or_404()

    if reservation.status != 'Reserved':
        flash('Only active reservations can be cancelled.', 'warning')
        return redirect(url_for('my_reservations'))

    reservation.status = 'Cancelled'
    # Increase available copies
    reservation.book.available_copies += 1
    if reservation.book.available_copies > reservation.book.total_copies:
        reservation.book.available_copies = reservation.book.total_copies

    db.session.commit()
    flash(f'Reservation for "{reservation.book.book_name}" cancelled successfully.', 'info')
    return redirect(url_for('my_reservations'))

# Admin Dashboard
@app.route('/admin/dashboard')
@admin_required
def admin_dashboard():
    total_books = Book.query.count()
    available_books = Book.query.filter(Book.available_copies > 0).count()
    reserved_books_count = Reservation.query.filter_by(status='Reserved').count()
    total_students = Student.query.count()

    recent_reservations = Reservation.query.order_by(Reservation.reservation_date.desc()).limit(5).all()

    return render_template(
        'admin_dashboard.html',
        total_books=total_books,
        available_books=available_books,
        reserved_books_count=reserved_books_count,
        total_students=total_students,
        recent_reservations=recent_reservations
    )

# Book Management (Admin)
@app.route('/admin/manage_books')
@app.route('/admin/books')
@admin_required
def manage_books():
    books = Book.query.order_by(Book.id.desc()).all()
    return render_template('manage_books.html', books=books)

@app.route('/admin/books/add', methods=['GET', 'POST'])
@admin_required
def add_book():
    if request.method == 'POST':
        book_name = request.form.get('book_name', '').strip()
        author_name = request.form.get('author_name', '').strip()
        isbn = request.form.get('isbn', '').strip()
        category = request.form.get('category', '').strip()
        description = request.form.get('description', '').strip()
        total_copies = request.form.get('total_copies', type=int, default=1)

        if not book_name or not author_name or not isbn or not category or total_copies <= 0:
            flash('Book Name, Author, ISBN, Category and Total Copies (>0) are required.', 'danger')
            return redirect(url_for('add_book'))

        existing_isbn = Book.query.filter_by(isbn=isbn).first()
        if existing_isbn:
            flash('A book with this ISBN already exists.', 'danger')
            return redirect(url_for('add_book'))

        book = Book(
            book_name=book_name,
            author_name=author_name,
            isbn=isbn,
            category=category,
            description=description,
            total_copies=total_copies,
            available_copies=total_copies
        )
        db.session.add(book)
        db.session.commit()

        flash(f'Book "{book_name}" added successfully.', 'success')
        return redirect(url_for('manage_books'))

    return render_template('add_book.html')

@app.route('/admin/books/edit/<int:book_id>', methods=['GET', 'POST'])
@admin_required
def edit_book(book_id):
    book = Book.query.get_or_404(book_id)

    if request.method == 'POST':
        book_name = request.form.get('book_name', '').strip()
        author_name = request.form.get('author_name', '').strip()
        isbn = request.form.get('isbn', '').strip()
        category = request.form.get('category', '').strip()
        description = request.form.get('description', '').strip()
        total_copies = request.form.get('total_copies', type=int)
        available_copies = request.form.get('available_copies', type=int)

        if not book_name or not author_name or not isbn or not category:
            flash('All primary book details are required.', 'danger')
            return redirect(url_for('edit_book', book_id=book_id))

        if total_copies is not None and total_copies < 0:
            flash('Total copies cannot be negative.', 'danger')
            return redirect(url_for('edit_book', book_id=book_id))

        if available_copies is not None and available_copies > total_copies:
            flash('Available copies cannot exceed total copies.', 'danger')
            return redirect(url_for('edit_book', book_id=book_id))

        book.book_name = book_name
        book.author_name = author_name
        book.isbn = isbn
        book.category = category
        book.description = description
        if total_copies is not None:
            book.total_copies = total_copies
        if available_copies is not None:
            book.available_copies = available_copies

        db.session.commit()
        flash(f'Book "{book.book_name}" updated successfully.', 'success')
        return redirect(url_for('manage_books'))

    return render_template('edit_book.html', book=book)

@app.route('/admin/books/delete/<int:book_id>', methods=['POST'])
@admin_required
def delete_book(book_id):
    book = Book.query.get_or_404(book_id)
    db.session.delete(book)
    db.session.commit()
    flash('Book deleted successfully.', 'info')
    return redirect(url_for('manage_books'))

# Reservation Management (Admin)
@app.route('/admin/manage_reservations')
@app.route('/admin/reservations')
@admin_required
def manage_reservations():
    reservations = Reservation.query.order_by(Reservation.reservation_date.desc()).all()
    return render_template('manage_reservations.html', reservations=reservations)

@app.route('/admin/reservations/cancel/<int:reservation_id>', methods=['POST'])
@admin_required
def admin_cancel_reservation(reservation_id):
    reservation = Reservation.query.get_or_404(reservation_id)

    if reservation.status == 'Reserved':
        reservation.status = 'Cancelled'
        reservation.book.available_copies += 1
        if reservation.book.available_copies > reservation.book.total_copies:
            reservation.book.available_copies = reservation.book.total_copies
        db.session.commit()
        flash(f'Reservation #{reservation.id} cancelled.', 'info')
    else:
        flash('Reservation is not active.', 'warning')

    return redirect(url_for('manage_reservations'))

@app.route('/admin/reservations/complete/<int:reservation_id>', methods=['POST'])
@admin_required
def admin_complete_reservation(reservation_id):
    reservation = Reservation.query.get_or_404(reservation_id)

    if reservation.status == 'Reserved':
        reservation.status = 'Completed'
        # Mark as completed (book issued/returned as complete)
        # Note: Depending on library rules, completed means finished reservation session.
        # Restoring available copy upon completion or return:
        reservation.book.available_copies += 1
        if reservation.book.available_copies > reservation.book.total_copies:
            reservation.book.available_copies = reservation.book.total_copies
        db.session.commit()
        flash(f'Reservation #{reservation.id} marked as Completed.', 'success')
    else:
        flash('Only active reservations can be marked as completed.', 'warning')

    return redirect(url_for('manage_reservations'))

# Student Management (Admin)
@app.route('/admin/manage_students')
@app.route('/admin/students')
@admin_required
def manage_students():
    students = Student.query.order_by(Student.id.desc()).all()
    return render_template('manage_students.html', students=students)

@app.route('/admin/students/delete/<int:student_id>', methods=['POST'])
@admin_required
def delete_student(student_id):
    student = Student.query.get_or_404(student_id)
    db.session.delete(student)
    db.session.commit()
    flash('Student deleted successfully.', 'info')
    return redirect(url_for('manage_students'))

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
        seed_initial_data()
    app.run(debug=True)
