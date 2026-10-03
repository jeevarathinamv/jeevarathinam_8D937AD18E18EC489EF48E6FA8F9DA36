import os
from datetime import datetime, date, timedelta
from functools import wraps
from flask import Flask, render_template, request, redirect, url_for, flash, session
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'college_library_secret_key_987654')

# Database configuration: MySQL URI by default, SQLite fallback for development/testing
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

    issues = db.relationship('BookIssue', backref='student', lazy=True, cascade='all, delete-orphan')

    def set_password(self, password):
        self.password = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password, password)


class Book(db.Model):
    __tablename__ = 'books'
    id = db.Column(db.Integer, primary_key=True)
    book_name = db.Column(db.String(150), nullable=False)
    author_name = db.Column(db.String(100), nullable=False)
    isbn = db.Column(db.String(50), unique=True, nullable=False)
    category = db.Column(db.String(50), nullable=False)
    total_copies = db.Column(db.Integer, nullable=False, default=1)
    available_copies = db.Column(db.Integer, nullable=False, default=1)

    issues = db.relationship('BookIssue', backref='book', lazy=True, cascade='all, delete-orphan')


class BookIssue(db.Model):
    __tablename__ = 'book_issues'
    id = db.Column(db.Integer, primary_key=True)
    student_id = db.Column(db.Integer, db.ForeignKey('students.id'), nullable=False)
    book_id = db.Column(db.Integer, db.ForeignKey('books.id'), nullable=False)
    issue_date = db.Column(db.Date, nullable=False, default=date.today)
    due_date = db.Column(db.Date, nullable=False)
    return_date = db.Column(db.Date, nullable=True)
    status = db.Column(db.String(20), nullable=False, default='Issued')  # Issued, Returned, Overdue


def check_and_update_overdue():
    """Helper function to automatically identify overdue books based on due date."""
    today = date.today()
    overdue_issues = BookIssue.query.filter(
        BookIssue.status == 'Issued',
        BookIssue.due_date < today
    ).all()
    if overdue_issues:
        for issue in overdue_issues:
            issue.status = 'Overdue'
        db.session.commit()


def seed_default_data():
    """Seeds initial admin credentials and sample library books if empty."""
    if Admin.query.count() == 0:
        admin = Admin(username='admin')
        admin.set_password('admin123')
        db.session.add(admin)
        db.session.commit()

    if Book.query.count() == 0:
        sample_books = [
            Book(book_name='Python Programming: An Introduction', author_name='John Zelle', isbn='978-1590282410', category='Programming', total_copies=5, available_copies=5),
            Book(book_name='Database System Concepts', author_name='Abraham Silberschatz', isbn='978-0078022159', category='Database', total_copies=4, available_copies=4),
            Book(book_name='Learning Web Design', author_name='Jennifer Robbins', isbn='978-1491960202', category='Web Development', total_copies=6, available_copies=6),
            Book(book_name='Introduction to Algorithms', author_name='Thomas H. Cormen', isbn='978-0262033848', category='Computer Science', total_copies=3, available_copies=3),
            Book(book_name='Principles of Software Engineering', author_name='Ian Sommerville', isbn='978-0133943030', category='Management', total_copies=4, available_copies=4),
            Book(book_name='Clean Code: A Handbook of Agile Software Craftsmanship', author_name='Robert C. Martin', isbn='978-0132350884', category='General', total_copies=5, available_copies=5),
            Book(book_name='Artificial Intelligence: A Modern Approach', author_name='Stuart Russell', isbn='978-0134610993', category='Other', total_copies=2, available_copies=2),
        ]
        db.session.add_all(sample_books)
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
            flash('Admin access required. Please log in as Admin.', 'warning')
            return redirect(url_for('admin_login'))
        return f(*args, **kwargs)
    return decorated_function


# General Routes
@app.route('/')
def index():
    check_and_update_overdue()
    total_books = Book.query.count()
    total_copies = db.session.query(db.func.sum(Book.total_copies)).scalar() or 0
    available_copies = db.session.query(db.func.sum(Book.available_copies)).scalar() or 0
    return render_template('index.html', total_books=total_books, total_copies=total_copies, available_copies=available_copies)


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
            flash('Please provide email/register number and password.', 'danger')
            return redirect(url_for('login'))

        student = Student.query.filter(
            (Student.email == email_or_reg.lower()) | (Student.register_number == email_or_reg)
        ).first()

        if student and student.check_password(password):
            session['user_type'] = 'student'
            session['student_id'] = student.id
            session['student_name'] = student.student_name
            session['user_name'] = student.student_name
            flash(f'Welcome back, {student.student_name}!', 'success')
            return redirect(url_for('student_dashboard'))
        else:
            flash('Invalid credentials. Please check your Register Number/Email and Password.', 'danger')
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
            session['admin_id'] = admin.id
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


# Student Dashboard & Book Browsing
@app.route('/student/dashboard')
@student_required
def student_dashboard():
    check_and_update_overdue()
    student_id = session.get('student_id')
    student = db.session.get(Student, student_id)

    total_books = Book.query.count()
    my_issues = BookIssue.query.filter_by(student_id=student_id).all()
    issued_count = len([i for i in my_issues if i.status == 'Issued'])
    returned_count = len([i for i in my_issues if i.status == 'Returned'])
    pending_count = len([i for i in my_issues if i.status in ['Issued', 'Overdue']])

    recent_issues = BookIssue.query.filter_by(student_id=student_id).order_by(BookIssue.id.desc()).limit(5).all()

    return render_template(
        'student_dashboard.html',
        student=student,
        total_books=total_books,
        issued_count=issued_count,
        returned_count=returned_count,
        pending_count=pending_count,
        recent_issues=recent_issues
    )


@app.route('/books')
def books():
    check_and_update_overdue()
    search = request.args.get('search', '').strip()
    category = request.args.get('category', '').strip()

    query = Book.query

    if search:
        search_filter = f"%{search}%"
        query = query.filter(
            (Book.book_name.ilike(search_filter)) |
            (Book.author_name.ilike(search_filter)) |
            (Book.isbn.ilike(search_filter))
        )

    if category and category != 'All':
        query = query.filter(Book.category == category)

    book_list = query.order_by(Book.book_name.asc()).all()

    # If student is logged in, collect active issue book IDs
    active_issue_book_ids = set()
    if session.get('user_type') == 'student':
        student_id = session.get('student_id')
        active_issues = BookIssue.query.filter(
            BookIssue.student_id == student_id,
            BookIssue.status.in_(['Issued', 'Overdue'])
        ).all()
        active_issue_book_ids = {issue.book_id for issue in active_issues}

    categories = ['Programming', 'Database', 'Web Development', 'Computer Science', 'Management', 'General', 'Other']

    return render_template(
        'books.html',
        books=book_list,
        search=search,
        selected_category=category,
        categories=categories,
        active_issue_book_ids=active_issue_book_ids
    )


@app.route('/student/issue/<int:book_id>', methods=['POST'])
@student_required
def issue_book(book_id):
    check_and_update_overdue()
    student_id = session.get('student_id')
    book = db.session.get(Book, book_id)
    if not book:
        flash('Book not found.', 'danger')
        return redirect(url_for('books'))

    # Validation: Available copies check
    if book.available_copies <= 0:
        flash(f'Sorry, "{book.book_name}" currently has no available copies.', 'danger')
        return redirect(url_for('books'))

    # Validation: Prevent duplicate active issue by same student
    existing_issue = BookIssue.query.filter(
        BookIssue.student_id == student_id,
        BookIssue.book_id == book_id,
        BookIssue.status.in_(['Issued', 'Overdue'])
    ).first()

    if existing_issue:
        flash(f'You have already issued "{book.book_name}" and it is currently active in your account.', 'warning')
        return redirect(url_for('my_books'))

    # Process book issue
    issue_date = date.today()
    due_date = issue_date + timedelta(days=14)

    new_issue = BookIssue(
        student_id=student_id,
        book_id=book_id,
        issue_date=issue_date,
        due_date=due_date,
        status='Issued'
    )

    book.available_copies -= 1
    db.session.add(new_issue)
    db.session.commit()

    flash(f'Successfully issued "{book.book_name}"! Due date is {due_date}.', 'success')
    return redirect(url_for('my_books'))


@app.route('/student/my-books')
@student_required
def my_books():
    check_and_update_overdue()
    student_id = session.get('student_id')
    my_issues = BookIssue.query.filter_by(student_id=student_id).order_by(BookIssue.id.desc()).all()
    today = date.today()
    return render_template('my_books.html', issues=my_issues, today=today)


# Admin Routes & Dashboard
@app.route('/admin/dashboard')
@admin_required
def admin_dashboard():
    check_and_update_overdue()
    total_books = Book.query.count()
    total_students = Student.query.count()
    issued_count = BookIssue.query.filter_by(status='Issued').count()
    returned_count = BookIssue.query.filter_by(status='Returned').count()
    overdue_count = BookIssue.query.filter_by(status='Overdue').count()

    recent_issues = BookIssue.query.order_by(BookIssue.id.desc()).limit(5).all()

    return render_template(
        'admin_dashboard.html',
        total_books=total_books,
        total_students=total_students,
        issued_count=issued_count,
        returned_count=returned_count,
        overdue_count=overdue_count,
        recent_issues=recent_issues
    )


@app.route('/admin/books')
@admin_required
def manage_books():
    search = request.args.get('search', '').strip()
    category = request.args.get('category', '').strip()

    query = Book.query

    if search:
        search_filter = f"%{search}%"
        query = query.filter(
            (Book.book_name.ilike(search_filter)) |
            (Book.author_name.ilike(search_filter)) |
            (Book.isbn.ilike(search_filter))
        )

    if category and category != 'All':
        query = query.filter(Book.category == category)

    book_list = query.order_by(Book.id.desc()).all()
    categories = ['Programming', 'Database', 'Web Development', 'Computer Science', 'Management', 'General', 'Other']

    return render_template(
        'manage_books.html',
        books=book_list,
        search=search,
        selected_category=category,
        categories=categories
    )


@app.route('/admin/books/add', methods=['GET', 'POST'])
@admin_required
def add_book():
    categories = ['Programming', 'Database', 'Web Development', 'Computer Science', 'Management', 'General', 'Other']

    if request.method == 'POST':
        book_name = request.form.get('book_name', '').strip()
        author_name = request.form.get('author_name', '').strip()
        isbn = request.form.get('isbn', '').strip()
        category = request.form.get('category', '').strip()
        total_copies = request.form.get('total_copies', type=int, default=1)

        if not book_name or not author_name or not isbn or not category:
            flash('All book fields are required.', 'danger')
            return redirect(url_for('add_book'))

        if total_copies < 1:
            flash('Total copies must be at least 1.', 'danger')
            return redirect(url_for('add_book'))

        existing_isbn = Book.query.filter_by(isbn=isbn).first()
        if existing_isbn:
            flash('A book with this ISBN already exists.', 'danger')
            return redirect(url_for('add_book'))

        new_book = Book(
            book_name=book_name,
            author_name=author_name,
            isbn=isbn,
            category=category,
            total_copies=total_copies,
            available_copies=total_copies
        )
        db.session.add(new_book)
        db.session.commit()

        flash(f'Book "{book_name}" added successfully!', 'success')
        return redirect(url_for('manage_books'))

    return render_template('add_book.html', categories=categories)


@app.route('/admin/books/edit/<int:book_id>', methods=['GET', 'POST'])
@admin_required
def edit_book(book_id):
    book = db.session.get(Book, book_id)
    if not book:
        flash('Book not found.', 'danger')
        return redirect(url_for('manage_books'))
    categories = ['Programming', 'Database', 'Web Development', 'Computer Science', 'Management', 'General', 'Other']

    if request.method == 'POST':
        book_name = request.form.get('book_name', '').strip()
        author_name = request.form.get('author_name', '').strip()
        isbn = request.form.get('isbn', '').strip()
        category = request.form.get('category', '').strip()
        total_copies = request.form.get('total_copies', type=int)
        available_copies = request.form.get('available_copies', type=int)

        if not book_name or not author_name or not isbn or not category:
            flash('All book fields are required.', 'danger')
            return redirect(url_for('edit_book', book_id=book.id))

        if total_copies is None or total_copies < 0:
            flash('Total copies cannot be negative.', 'danger')
            return redirect(url_for('edit_book', book_id=book.id))

        if available_copies is None or available_copies < 0:
            flash('Available copies cannot be negative.', 'danger')
            return redirect(url_for('edit_book', book_id=book.id))

        if available_copies > total_copies:
            flash('Available copies cannot be greater than Total copies.', 'danger')
            return redirect(url_for('edit_book', book_id=book.id))

        # Check ISBN uniqueness if changed
        if isbn != book.isbn:
            existing_isbn = Book.query.filter_by(isbn=isbn).first()
            if existing_isbn:
                flash('Another book with this ISBN already exists.', 'danger')
                return redirect(url_for('edit_book', book_id=book.id))

        book.book_name = book_name
        book.author_name = author_name
        book.isbn = isbn
        book.category = category
        book.total_copies = total_copies
        book.available_copies = available_copies

        db.session.commit()

        flash(f'Book "{book_name}" updated successfully!', 'success')
        return redirect(url_for('manage_books'))

    return render_template('edit_book.html', book=book, categories=categories)


@app.route('/admin/books/delete/<int:book_id>', methods=['POST'])
@admin_required
def delete_book(book_id):
    book = db.session.get(Book, book_id)
    if not book:
        flash('Book not found.', 'danger')
        return redirect(url_for('manage_books'))

    active_issues = BookIssue.query.filter(
        BookIssue.book_id == book_id,
        BookIssue.status.in_(['Issued', 'Overdue'])
    ).first()

    if active_issues:
        flash(f'Cannot delete "{book.book_name}" because it currently has active issued copies.', 'danger')
        return redirect(url_for('manage_books'))

    db.session.delete(book)
    db.session.commit()

    flash('Book deleted successfully.', 'info')
    return redirect(url_for('manage_books'))


@app.route('/admin/issues')
@admin_required
def issue_records():
    check_and_update_overdue()
    search = request.args.get('search', '').strip()
    status_filter = request.args.get('status', 'All').strip()

    query = BookIssue.query.join(Student).join(Book)

    if search:
        search_pattern = f"%{search}%"
        query = query.filter(
            (Student.student_name.ilike(search_pattern)) |
            (Student.register_number.ilike(search_pattern)) |
            (Book.book_name.ilike(search_pattern)) |
            (Book.isbn.ilike(search_pattern))
        )

    if status_filter in ['Issued', 'Returned', 'Overdue']:
        query = query.filter(BookIssue.status == status_filter)

    records = query.order_by(BookIssue.id.desc()).all()

    return render_template(
        'issue_records.html',
        records=records,
        search=search,
        status_filter=status_filter
    )


@app.route('/admin/issues/return/<int:issue_id>', methods=['POST'])
@admin_required
def return_book(issue_id):
    issue = db.session.get(BookIssue, issue_id)
    if not issue:
        flash('Book issue record not found.', 'danger')
        return redirect(url_for('issue_records'))

    if issue.status == 'Returned':
        flash('This book issue record is already marked as Returned.', 'warning')
        return redirect(url_for('issue_records'))

    issue.status = 'Returned'
    issue.return_date = date.today()

    book = issue.book
    book.available_copies += 1
    if book.available_copies > book.total_copies:
        book.available_copies = book.total_copies

    db.session.commit()

    flash(f'Book "{book.book_name}" issued to {issue.student.student_name} marked as Returned.', 'success')
    return redirect(url_for('issue_records'))


@app.route('/admin/students')
@admin_required
def manage_students():
    search = request.args.get('search', '').strip()
    query = Student.query

    if search:
        search_pattern = f"%{search}%"
        query = query.filter(
            (Student.student_name.ilike(search_pattern)) |
            (Student.register_number.ilike(search_pattern)) |
            (Student.department.ilike(search_pattern)) |
            (Student.email.ilike(search_pattern))
        )

    student_list = query.order_by(Student.student_name.asc()).all()

    return render_template('manage_students.html', students=student_list, search=search)


@app.route('/admin/students/delete/<int:student_id>', methods=['POST'])
@admin_required
def delete_student(student_id):
    student = db.session.get(Student, student_id)
    if not student:
        flash('Student not found.', 'danger')
        return redirect(url_for('manage_students'))

    active_issues = BookIssue.query.filter(
        BookIssue.student_id == student_id,
        BookIssue.status.in_(['Issued', 'Overdue'])
    ).first()

    if active_issues:
        flash(f'Cannot delete student "{student.student_name}" because they have unreturned books.', 'danger')
        return redirect(url_for('manage_students'))

    db.session.delete(student)
    db.session.commit()

    flash(f'Student "{student.student_name}" removed successfully.', 'info')
    return redirect(url_for('manage_students'))


if __name__ == '__main__':
    with app.app_context():
        db.create_all()
        seed_default_data()
    app.run(debug=True)
