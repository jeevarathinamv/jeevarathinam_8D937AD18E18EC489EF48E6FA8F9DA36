import os
import uuid
from datetime import datetime, timezone
from functools import wraps
from flask import (
    Flask, render_template, request, redirect, url_for, flash, session,
    send_from_directory
)
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename

app = Flask(__name__)
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'college_digital_library_secret_key_2025')

# Allowed categories for books
BOOK_CATEGORIES = [
    'Programming',
    'Database',
    'Web Development',
    'Computer Science',
    'Management',
    'General',
    'Other'
]

# Configure Uploads Directory
UPLOAD_FOLDER = os.path.join(app.root_path, 'static', 'uploads')
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16 MB max limit
ALLOWED_EXTENSIONS = {'pdf'}

if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# Database Configuration: Default to MySQL URI, fallback to SQLite if USE_SQLITE=1
MYSQL_URI = os.environ.get('DATABASE_URL', 'mysql+pymysql://root:@localhost/college_library_db')
SQLITE_URI = 'sqlite:///' + os.path.join(os.path.abspath(os.path.dirname(__file__)), 'college_library.db')

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
    name = db.Column(db.String(100), default='Administrator')
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))

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
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))

    downloads = db.relationship('Download', backref='student', lazy=True, cascade='all, delete-orphan')

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

class Book(db.Model):
    __tablename__ = 'books'
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    author = db.Column(db.String(100), nullable=False)
    category = db.Column(db.String(50), nullable=False)
    description = db.Column(db.Text, nullable=True)
    filename = db.Column(db.String(255), nullable=False)
    upload_date = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))

    downloads = db.relationship('Download', backref='book', lazy=True, cascade='all, delete-orphan')

class Download(db.Model):
    __tablename__ = 'downloads'
    id = db.Column(db.Integer, primary_key=True)
    student_id = db.Column(db.Integer, db.ForeignKey('students.id'), nullable=False)
    book_id = db.Column(db.Integer, db.ForeignKey('books.id'), nullable=False)
    download_date = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def seed_default_data():
    """Seeds initial admin account and sample books if missing."""
    if Admin.query.count() == 0:
        admin = Admin(
            username='admin',
            name='System Administrator'
        )
        admin.set_password('admin123')
        db.session.add(admin)
        db.session.commit()

    if Book.query.count() == 0:
        sample_books = [
            Book(
                title='Python Programming Fundamentals',
                author='Guido van Rossum',
                category='Programming',
                description='Comprehensive guide to Python syntax, data structures, and object-oriented concepts.',
                filename='sample_python_guide.pdf'
            ),
            Book(
                title='Database Management Systems & SQL',
                author='Raghu Ramakrishnan',
                category='Database',
                description='In-depth introduction to relational databases, SQL queries, normalization, and indexing.',
                filename='sample_dbms_guide.pdf'
            ),
            Book(
                title='Modern Web Development with Flask & Bootstrap',
                author='Miguel Grinberg',
                category='Web Development',
                description='Practical reference for building modern full-stack web applications using Flask and Bootstrap 5.',
                filename='sample_web_dev_guide.pdf'
            ),
            Book(
                title='Data Structures and Algorithms in Python',
                author='Michael T. Goodrich',
                category='Computer Science',
                description='Core computer science algorithms, complexity analysis, trees, graphs, and sorting.',
                filename='sample_dsa_guide.pdf'
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
            flash('Admin access required. Please log in as Administrator.', 'warning')
            return redirect(url_for('admin_login'))
        return f(*args, **kwargs)
    return decorated_function

# Home / Index Route
@app.route('/')
def index():
    recent_books = Book.query.order_by(Book.upload_date.desc()).limit(6).all()
    total_books = Book.query.count()
    total_students = Student.query.count()
    total_downloads = Download.query.count()
    return render_template(
        'index.html',
        recent_books=recent_books,
        total_books=total_books,
        total_students=total_students,
        total_downloads=total_downloads
    )

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
            flash('All registration fields are required.', 'danger')
            return redirect(url_for('register'))

        existing_student = Student.query.filter(
            (Student.email == email) | (Student.register_number == register_number)
        ).first()

        if existing_student:
            flash('Student with this Email or Register Number is already registered.', 'danger')
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
            flash('Please enter your email/register number and password.', 'danger')
            return redirect(url_for('login'))

        student = Student.query.filter(
            (Student.email == email_or_reg.lower()) | (Student.register_number == email_or_reg)
        ).first()

        if student and student.check_password(password):
            session['user_type'] = 'student'
            session['user_id'] = student.id
            session['user_name'] = student.name
            session['user_email'] = student.email
            flash(f'Welcome back, {student.name}!', 'success')
            return redirect(url_for('student_dashboard'))
        else:
            flash('Invalid credentials. Please check your details and try again.', 'danger')
            return redirect(url_for('login'))

    return render_template('login.html')

# Admin Login Route
@app.route('/admin/login', methods=['GET', 'POST'])
def admin_login():
    if request.method == 'POST':
        username = request.form.get('username', '').strip()
        password = request.form.get('password', '')

        if not username or not password:
            flash('Please enter username and password.', 'danger')
            return redirect(url_for('admin_login'))

        admin = Admin.query.filter_by(username=username).first()

        if admin and admin.check_password(password):
            session['user_type'] = 'admin'
            session['user_id'] = admin.id
            session['user_name'] = admin.name
            flash('Successfully logged in as Administrator.', 'success')
            return redirect(url_for('admin_dashboard'))
        else:
            flash('Invalid admin credentials.', 'danger')
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
    if not student:
        session.clear()
        flash('Student profile not found.', 'danger')
        return redirect(url_for('login'))

    total_books = Book.query.count()
    my_downloads_count = Download.query.filter_by(student_id=student_id).count()
    my_recent_downloads = Download.query.filter_by(student_id=student_id)\
        .order_by(Download.download_date.desc()).limit(5).all()

    return render_template(
        'student_dashboard.html',
        student=student,
        total_books=total_books,
        available_books=total_books,
        my_downloads_count=my_downloads_count,
        recent_downloads=my_recent_downloads
    )

# Digital Book Catalog / Search
@app.route('/books')
def books():
    search_query = request.args.get('q', '').strip()
    selected_category = request.args.get('category', '').strip()

    query = Book.query

    if search_query:
        query = query.filter(
            (Book.title.ilike(f'%{search_query}%')) |
            (Book.author.ilike(f'%{search_query}%')) |
            (Book.description.ilike(f'%{search_query}%'))
        )

    if selected_category and selected_category != 'All':
        query = query.filter(Book.category == selected_category)

    all_books = query.order_by(Book.upload_date.desc()).all()

    return render_template(
        'books.html',
        books=all_books,
        categories=BOOK_CATEGORIES,
        search_query=search_query,
        selected_category=selected_category
    )

# Book Details View
@app.route('/books/<int:book_id>')
def book_details(book_id):
    book = db.session.get(Book, book_id)
    if not book:
        flash('Book not found.', 'danger')
        return redirect(url_for('books'))
    return render_template('book_details.html', book=book)

# View Book PDF Inline
@app.route('/books/view/<int:book_id>')
def view_book(book_id):
    book = db.session.get(Book, book_id)
    if not book:
        flash('Book not found.', 'danger')
        return redirect(url_for('books'))

    filepath = os.path.join(app.config['UPLOAD_FOLDER'], book.filename)
    if not os.path.exists(filepath):
        flash('Book file is missing or not found on server.', 'danger')
        return redirect(url_for('book_details', book_id=book.id))

    return send_from_directory(
        app.config['UPLOAD_FOLDER'],
        book.filename,
        mimetype='application/pdf',
        as_attachment=False
    )

# Download Book PDF and Record Download History
@app.route('/books/download/<int:book_id>')
def download_book(book_id):
    book = db.session.get(Book, book_id)
    if not book:
        flash('Book not found.', 'danger')
        return redirect(url_for('books'))

    filepath = os.path.join(app.config['UPLOAD_FOLDER'], book.filename)

    if not os.path.exists(filepath):
        flash('Book file is missing or not found on server.', 'danger')
        return redirect(url_for('book_details', book_id=book.id))

    # Automatically record download history if student is logged in
    if session.get('user_type') == 'student' and session.get('user_id'):
        download_entry = Download(
            student_id=session['user_id'],
            book_id=book.id,
            download_date=datetime.now(timezone.utc)
        )
        db.session.add(download_entry)
        db.session.commit()

    return send_from_directory(
        app.config['UPLOAD_FOLDER'],
        book.filename,
        as_attachment=True,
        download_name=f"{secure_filename(book.title)}.pdf"
    )

# Student My Downloads History Page
@app.route('/student/downloads')
@student_required
def my_downloads():
    student_id = session.get('user_id')
    student_downloads = Download.query.filter_by(student_id=student_id)\
        .order_by(Download.download_date.desc()).all()

    return render_template('my_downloads.html', downloads=student_downloads)

# Admin Dashboard
@app.route('/admin/dashboard')
@admin_required
def admin_dashboard():
    total_students = Student.query.count()
    total_books = Book.query.count()
    available_books = total_books
    total_downloads = Download.query.count()

    students = Student.query.order_by(Student.created_at.desc()).all()
    downloads_history = Download.query.order_by(Download.download_date.desc()).all()

    return render_template(
        'admin_dashboard.html',
        total_students=total_students,
        total_books=total_books,
        available_books=available_books,
        total_downloads=total_downloads,
        students=students,
        downloads=downloads_history
    )

# Admin Digital Book Management List
@app.route('/admin/books')
@admin_required
def manage_books():
    all_books = Book.query.order_by(Book.upload_date.desc()).all()
    return render_template('manage_books.html', books=all_books)

# Admin Add Book
@app.route('/admin/books/add', methods=['GET', 'POST'])
@admin_required
def add_book():
    if request.method == 'POST':
        title = request.form.get('title', '').strip()
        author = request.form.get('author', '').strip()
        category = request.form.get('category', '').strip()
        description = request.form.get('description', '').strip()

        if 'file' not in request.files:
            flash('Book PDF file is required.', 'danger')
            return redirect(url_for('add_book'))

        file = request.files['file']

        if file.filename == '':
            flash('No PDF file selected for upload.', 'danger')
            return redirect(url_for('add_book'))

        if not title or not author or not category:
            flash('Book title, author, and category are required.', 'danger')
            return redirect(url_for('add_book'))

        if not allowed_file(file.filename):
            flash('Invalid file type! Only PDF files (.pdf) are allowed.', 'danger')
            return redirect(url_for('add_book'))

        # Generate unique filename to avoid overwrites
        original_secure_name = secure_filename(file.filename)
        unique_filename = f"{uuid.uuid4().hex[:10]}_{original_secure_name}"
        save_path = os.path.join(app.config['UPLOAD_FOLDER'], unique_filename)
        file.save(save_path)

        new_book = Book(
            title=title,
            author=author,
            category=category,
            description=description,
            filename=unique_filename
        )
        db.session.add(new_book)
        db.session.commit()

        flash(f'Book "{title}" added successfully to digital library!', 'success')
        return redirect(url_for('manage_books'))

    return render_template('add_book.html', categories=BOOK_CATEGORIES)

# Admin Edit Book
@app.route('/admin/books/edit/<int:book_id>', methods=['GET', 'POST'])
@admin_required
def edit_book(book_id):
    book = db.session.get(Book, book_id)
    if not book:
        flash('Book not found.', 'danger')
        return redirect(url_for('manage_books'))

    if request.method == 'POST':
        title = request.form.get('title', '').strip()
        author = request.form.get('author', '').strip()
        category = request.form.get('category', '').strip()
        description = request.form.get('description', '').strip()

        if not title or not author or not category:
            flash('Book title, author, and category are required.', 'danger')
            return redirect(url_for('edit_book', book_id=book.id))

        # Check if new PDF file was uploaded
        if 'file' in request.files and request.files['file'].filename != '':
            file = request.files['file']
            if not allowed_file(file.filename):
                flash('Invalid file type! Only PDF files (.pdf) are allowed.', 'danger')
                return redirect(url_for('edit_book', book_id=book.id))

            original_secure_name = secure_filename(file.filename)
            unique_filename = f"{uuid.uuid4().hex[:10]}_{original_secure_name}"
            save_path = os.path.join(app.config['UPLOAD_FOLDER'], unique_filename)
            file.save(save_path)

            # Update filename
            book.filename = unique_filename

        book.title = title
        book.author = author
        book.category = category
        book.description = description

        db.session.commit()
        flash(f'Book "{title}" updated successfully!', 'success')
        return redirect(url_for('manage_books'))

    return render_template('edit_book.html', book=book, categories=BOOK_CATEGORIES)

# Admin Delete Book
@app.route('/admin/books/delete/<int:book_id>', methods=['POST'])
@admin_required
def delete_book(book_id):
    book = db.session.get(Book, book_id)
    if not book:
        flash('Book not found.', 'danger')
        return redirect(url_for('manage_books'))

    book_title = book.title

    # Remove file if it exists and is not one of the default sample files
    filepath = os.path.join(app.config['UPLOAD_FOLDER'], book.filename)
    if os.path.exists(filepath) and not book.filename.startswith('sample_'):
        try:
            os.remove(filepath)
        except OSError:
            pass

    db.session.delete(book)
    db.session.commit()

    flash(f'Book "{book_title}" deleted successfully.', 'info')
    return redirect(url_for('manage_books'))

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
        seed_default_data()
    app.run(debug=True)
