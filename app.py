import os
from datetime import datetime, date
from functools import wraps
from flask import Flask, render_template, request, redirect, url_for, flash, session
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'library_book_fine_management_secret_key_987')

# Database configuration: Default to MySQL URI, fallback to SQLite when requested
MYSQL_URI = os.environ.get('DATABASE_URL', 'mysql+pymysql://root:@localhost/library_fine_db')
SQLITE_URI = 'sqlite:///' + os.path.join(os.path.abspath(os.path.dirname(__file__)), 'library_fine.db')

use_sqlite = os.environ.get('USE_SQLITE') == '1'
app.config['SQLALCHEMY_DATABASE_URI'] = SQLITE_URI if use_sqlite else MYSQL_URI
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

FINE_RATE_PER_DAY = 5.0  # ₹5 per late day

# Database Models
class Admin(db.Model):
    __tablename__ = 'admins'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    name = db.Column(db.String(100), nullable=False, default='Library Admin')
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

    issues = db.relationship('BookIssue', backref='student', lazy=True, cascade="all, delete-orphan")

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

class Book(db.Model):
    __tablename__ = 'books'
    id = db.Column(db.Integer, primary_key=True)
    book_name = db.Column(db.String(200), nullable=False)
    author_name = db.Column(db.String(150), nullable=False)
    book_code = db.Column(db.String(50), unique=True, nullable=False)
    category = db.Column(db.String(100), nullable=False)
    available_copies = db.Column(db.Integer, nullable=False, default=1)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    issues = db.relationship('BookIssue', backref='book', lazy=True, cascade="all, delete-orphan")

class BookIssue(db.Model):
    __tablename__ = 'book_issues'
    id = db.Column(db.Integer, primary_key=True)
    student_id = db.Column(db.Integer, db.ForeignKey('students.id'), nullable=False)
    book_id = db.Column(db.Integer, db.ForeignKey('books.id'), nullable=False)
    issue_date = db.Column(db.Date, nullable=False)
    due_date = db.Column(db.Date, nullable=False)
    return_date = db.Column(db.Date, nullable=True)
    status = db.Column(db.String(20), default='Issued')  # Issued, Returned, Overdue
    late_days = db.Column(db.Integer, default=0)
    fine_amount = db.Column(db.Float, default=0.0)
    fine_status = db.Column(db.String(20), default='No Fine')  # No Fine, Pending, Paid
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

def recalculate_fines():
    """Recalculate late days and fines for active (unreturned) issues."""
    today = date.today()
    unreturned_issues = BookIssue.query.filter(BookIssue.return_date.is_(None)).all()
    for issue in unreturned_issues:
        if today > issue.due_date:
            late_days = (today - issue.due_date).days
            issue.late_days = max(0, late_days)
            issue.fine_amount = issue.late_days * FINE_RATE_PER_DAY
            issue.status = 'Overdue'
            if issue.fine_status == 'No Fine' and issue.fine_amount > 0:
                issue.fine_status = 'Pending'
        else:
            issue.late_days = 0
            issue.fine_amount = 0.0
            issue.status = 'Issued'
            issue.fine_status = 'No Fine'
    db.session.commit()

def seed_default_data():
    """Seed initial admin user and sample books."""
    admin = Admin.query.filter_by(username='admin').first()
    if not admin:
        admin = Admin(username='admin', name='Library Admin')
        admin.set_password('admin123')
        db.session.add(admin)

    if Book.query.count() == 0:
        sample_books = [
            Book(book_name='Python Crash Course', author_name='Eric Matthes', book_code='BK-CS-001', category='Computer Science', available_copies=5),
            Book(book_name='Clean Code', author_name='Robert C. Martin', book_code='BK-CS-002', category='Computer Science', available_copies=3),
            Book(book_name='Introduction to Algorithms', author_name='Thomas H. Cormen', book_code='BK-CS-003', category='Computer Science', available_copies=4),
            Book(book_name='Database System Concepts', author_name='Abraham Silberschatz', book_code='BK-CS-004', category='Information Technology', available_copies=6),
            Book(book_name='Operating System Concepts', author_name='Abraham Silberschatz', book_code='BK-CS-005', category='Computer Science', available_copies=2),
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

# Routes

@app.route('/')
def index():
    total_books = Book.query.count()
    total_students = Student.query.count()
    return render_template('index.html', total_books=total_books, total_students=total_students)

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

# Student Login
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        login_type = request.form.get('login_type', 'student')

        if login_type == 'admin':
            return redirect(url_for('admin_login'))

        email_or_reg = request.form.get('email_or_reg', '').strip()
        password = request.form.get('password', '')

        if not email_or_reg or not password:
            flash('Please enter email/register number and password.', 'danger')
            return redirect(url_for('login'))

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
            flash('Invalid student credentials. Please check your details.', 'danger')
            return redirect(url_for('login'))

    return render_template('login.html')

# Admin Login
@app.route('/admin/login', methods=['GET', 'POST'])
def admin_login():
    if request.method == 'POST':
        username = request.form.get('username', '').strip()
        password = request.form.get('password', '')

        if not username or not password:
            flash('Username and password are required.', 'danger')
            return redirect(url_for('admin_login'))

        admin = Admin.query.filter_by(username=username).first()

        if admin and admin.check_password(password):
            session['user_type'] = 'admin'
            session['user_id'] = admin.id
            session['user_name'] = admin.name
            flash('Logged in successfully as Administrator.', 'success')
            return redirect(url_for('admin_dashboard'))
        else:
            flash('Invalid administrator credentials.', 'danger')
            return redirect(url_for('admin_login'))

    return render_template('admin_login.html')

# Logout
@app.route('/logout')
def logout():
    session.clear()
    flash('You have been logged out.', 'info')
    return redirect(url_for('index'))

# Student Dashboard & Views
@app.route('/student/dashboard')
@student_required
def student_dashboard():
    recalculate_fines()
    student_id = session.get('user_id')
    student = db.get_or_404(Student, student_id)
    my_issues = BookIssue.query.filter_by(student_id=student_id).order_by(BookIssue.created_at.desc()).all()

    total_books = len(my_issues)
    returned_books = len([i for i in my_issues if i.status == 'Returned'])
    overdue_books = len([i for i in my_issues if i.status == 'Overdue'])
    total_fine = sum(i.fine_amount for i in my_issues)

    return render_template(
        'student_dashboard.html',
        student=student,
        my_issues=my_issues,
        total_books=total_books,
        returned_books=returned_books,
        overdue_books=overdue_books,
        total_fine=total_fine
    )

@app.route('/student/my-books')
@student_required
def my_books():
    recalculate_fines()
    student_id = session.get('user_id')
    my_issues = BookIssue.query.filter_by(student_id=student_id).order_by(BookIssue.created_at.desc()).all()
    return render_template('my_books.html', my_issues=my_issues)

@app.route('/student/fine-details')
@student_required
def fine_details():
    recalculate_fines()
    student_id = session.get('user_id')
    my_issues = BookIssue.query.filter_by(student_id=student_id).order_by(BookIssue.created_at.desc()).all()
    fine_issues = [i for i in my_issues if i.fine_amount > 0 or i.fine_status != 'No Fine']
    total_fine = sum(i.fine_amount for i in my_issues)
    pending_fine = sum(i.fine_amount for i in my_issues if i.fine_status == 'Pending')
    return render_template('fine_details.html', my_issues=my_issues, fine_issues=fine_issues, total_fine=total_fine, pending_fine=pending_fine)

# Admin Dashboard & Management
@app.route('/admin/dashboard')
@admin_required
def admin_dashboard():
    recalculate_fines()
    total_students = Student.query.count()
    all_issues = BookIssue.query.all()
    total_issued_books = len([i for i in all_issues if i.status in ['Issued', 'Overdue']])
    overdue_books = len([i for i in all_issues if i.status == 'Overdue'])
    total_fine = sum(i.fine_amount for i in all_issues)
    pending_fine = sum(i.fine_amount for i in all_issues if i.fine_status == 'Pending')

    recent_issues = BookIssue.query.order_by(BookIssue.created_at.desc()).limit(10).all()

    return render_template(
        'admin_dashboard.html',
        total_students=total_students,
        total_issued_books=total_issued_books,
        overdue_books=overdue_books,
        total_fine=total_fine,
        pending_fine=pending_fine,
        recent_issues=recent_issues
    )

# Book Management
@app.route('/admin/books')
@admin_required
def manage_books():
    books = Book.query.order_by(Book.book_name.asc()).all()
    return render_template('manage_books.html', books=books)

@app.route('/admin/books/add', methods=['GET', 'POST'])
@admin_required
def add_book():
    if request.method == 'POST':
        book_name = request.form.get('book_name', '').strip()
        author_name = request.form.get('author_name', '').strip()
        book_code = request.form.get('book_code', '').strip().upper()
        category = request.form.get('category', '').strip()
        available_copies = request.form.get('available_copies', type=int, default=1)

        if not book_name or not author_name or not book_code or not category or available_copies < 0:
            flash('All fields are required and copies must be >= 0.', 'danger')
            return redirect(url_for('add_book'))

        existing_code = Book.query.filter_by(book_code=book_code).first()
        if existing_code:
            flash(f'Book with code "{book_code}" already exists.', 'danger')
            return redirect(url_for('add_book'))

        book = Book(
            book_name=book_name,
            author_name=author_name,
            book_code=book_code,
            category=category,
            available_copies=available_copies
        )
        db.session.add(book)
        db.session.commit()

        flash(f'Book "{book_name}" added successfully.', 'success')
        return redirect(url_for('manage_books'))

    return render_template('add_book.html')

@app.route('/admin/books/edit/<int:book_id>', methods=['GET', 'POST'])
@admin_required
def edit_book(book_id):
    book = db.get_or_404(Book, book_id)
    if request.method == 'POST':
        book_name = request.form.get('book_name', '').strip()
        author_name = request.form.get('author_name', '').strip()
        book_code = request.form.get('book_code', '').strip().upper()
        category = request.form.get('category', '').strip()
        available_copies = request.form.get('available_copies', type=int, default=0)

        if not book_name or not author_name or not book_code or not category or available_copies < 0:
            flash('All fields are required.', 'danger')
            return redirect(url_for('edit_book', book_id=book_id))

        existing_code = Book.query.filter(Book.book_code == book_code, Book.id != book_id).first()
        if existing_code:
            flash(f'Book code "{book_code}" is already used by another book.', 'danger')
            return redirect(url_for('edit_book', book_id=book_id))

        book.book_name = book_name
        book.author_name = author_name
        book.book_code = book_code
        book.category = category
        book.available_copies = available_copies

        db.session.commit()
        flash(f'Book "{book.book_name}" updated successfully.', 'success')
        return redirect(url_for('manage_books'))

    return render_template('edit_book.html', book=book)

@app.route('/admin/books/delete/<int:book_id>', methods=['POST'])
@admin_required
def delete_book(book_id):
    book = db.get_or_404(Book, book_id)
    db.session.delete(book)
    db.session.commit()
    flash('Book deleted successfully.', 'info')
    return redirect(url_for('manage_books'))

# Issue & Return Book Operations
@app.route('/admin/issue-book', methods=['GET', 'POST'])
@admin_required
def issue_book():
    if request.method == 'POST':
        student_id = request.form.get('student_id', type=int)
        book_id = request.form.get('book_id', type=int)
        issue_date_str = request.form.get('issue_date', '')
        due_date_str = request.form.get('due_date', '')

        if not student_id or not book_id or not issue_date_str or not due_date_str:
            flash('Please select a student, a book, and valid dates.', 'danger')
            return redirect(url_for('issue_book'))

        try:
            issue_date = datetime.strptime(issue_date_str, '%Y-%m-%d').date()
            due_date = datetime.strptime(due_date_str, '%Y-%m-%d').date()
        except ValueError:
            flash('Invalid date format.', 'danger')
            return redirect(url_for('issue_book'))

        if due_date < issue_date:
            flash('Due date cannot be before issue date.', 'danger')
            return redirect(url_for('issue_book'))

        student = db.session.get(Student, student_id)
        book = db.session.get(Book, book_id)

        if not student or not book:
            flash('Selected student or book not found.', 'danger')
            return redirect(url_for('issue_book'))

        if book.available_copies <= 0:
            flash(f'No available copies left for "{book.book_name}".', 'danger')
            return redirect(url_for('issue_book'))

        book.available_copies -= 1

        today = date.today()
        status = 'Issued'
        late_days = 0
        fine_amount = 0.0
        fine_status = 'No Fine'

        if today > due_date:
            status = 'Overdue'
            late_days = (today - due_date).days
            fine_amount = late_days * FINE_RATE_PER_DAY
            fine_status = 'Pending'

        issue = BookIssue(
            student_id=student_id,
            book_id=book_id,
            issue_date=issue_date,
            due_date=due_date,
            status=status,
            late_days=late_days,
            fine_amount=fine_amount,
            fine_status=fine_status
        )
        db.session.add(issue)
        db.session.commit()

        flash(f'Book "{book.book_name}" issued successfully to {student.name}.', 'success')
        return redirect(url_for('admin_dashboard'))

    students = Student.query.order_by(Student.name.asc()).all()
    books = Book.query.filter(Book.available_copies > 0).order_by(Book.book_name.asc()).all()
    today_str = date.today().isoformat()
    return render_template('issue_book.html', students=students, books=books, today=today_str)

@app.route('/admin/return-book', methods=['GET', 'POST'])
@app.route('/admin/return-book/<int:issue_id>', methods=['GET', 'POST'])
@admin_required
def return_book(issue_id=None):
    if request.method == 'POST':
        target_issue_id = issue_id or request.form.get('issue_id', type=int)

        if not target_issue_id:
            flash('Invalid book issue record.', 'danger')
            return redirect(url_for('return_book'))

        issue = db.get_or_404(BookIssue, target_issue_id)

        if issue.status == 'Returned':
            flash('This book has already been returned.', 'warning')
            return redirect(url_for('admin_dashboard'))

        return_date_str = request.form.get('return_date', '')
        if return_date_str:
            try:
                return_date = datetime.strptime(return_date_str, '%Y-%m-%d').date()
            except ValueError:
                return_date = date.today()
        else:
            return_date = date.today()

        issue.return_date = return_date
        issue.status = 'Returned'

        # Fine Calculation: Fine = Late Days * ₹5
        if return_date > issue.due_date:
            late_days = max(0, (return_date - issue.due_date).days)
            fine_amount = late_days * FINE_RATE_PER_DAY
            issue.late_days = late_days
            issue.fine_amount = fine_amount
            if fine_amount > 0 and issue.fine_status == 'No Fine':
                issue.fine_status = 'Pending'
        else:
            issue.late_days = 0
            issue.fine_amount = 0.0
            issue.fine_status = 'No Fine'

        # Increase available copies
        issue.book.available_copies += 1

        db.session.commit()

        flash(f'Book "{issue.book.book_name}" marked as Returned. Late Days: {issue.late_days}, Fine: ₹{issue.fine_amount:.2f}', 'success')
        return redirect(url_for('admin_dashboard'))

    active_issues = BookIssue.query.filter(BookIssue.return_date.is_(None)).order_by(BookIssue.issue_date.desc()).all()
    selected_issue = db.session.get(BookIssue, issue_id) if issue_id else None
    today_str = date.today().isoformat()
    return render_template('return_book.html', active_issues=active_issues, selected_issue=selected_issue, today=today_str)

# Fine Management
@app.route('/admin/fine-management')
@admin_required
def fine_management():
    recalculate_fines()
    all_issues = BookIssue.query.order_by(BookIssue.created_at.desc()).all()
    fine_issues = [i for i in all_issues if i.fine_amount > 0 or i.fine_status != 'No Fine']
    total_fine = sum(i.fine_amount for i in all_issues)
    pending_fine = sum(i.fine_amount for i in all_issues if i.fine_status == 'Pending')
    paid_fine = sum(i.fine_amount for i in all_issues if i.fine_status == 'Paid')

    return render_template(
        'fine_management.html',
        fine_issues=fine_issues,
        total_fine=total_fine,
        pending_fine=pending_fine,
        paid_fine=paid_fine
    )

@app.route('/admin/fine/update-status/<int:issue_id>', methods=['POST'])
@admin_required
def update_fine_status(issue_id):
    issue = db.get_or_404(BookIssue, issue_id)
    new_status = request.form.get('fine_status', '').strip()

    if new_status in ['No Fine', 'Pending', 'Paid']:
        issue.fine_status = new_status
        db.session.commit()
        flash(f'Fine status for issue #{issue.id} updated to "{new_status}".', 'success')
    else:
        flash('Invalid fine status.', 'danger')

    return redirect(url_for('fine_management'))

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
        seed_default_data()
    app.run(debug=True)
