import os
from datetime import datetime
from functools import wraps
from flask import Flask, render_template, request, redirect, url_for, flash, session
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename

app = Flask(__name__)
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'college_doc_verification_secret_key_12345')

# File Upload Configurations
UPLOAD_FOLDER = os.path.join(app.root_path, 'static', 'uploads')
ALLOWED_EXTENSIONS = {'pdf', 'jpg', 'jpeg', 'png'}
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max upload size

# Ensure upload directory exists
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# Admin Hardcoded Fallback Credentials
ADMIN_DEFAULT_USER = os.environ.get('ADMIN_USERNAME', 'admin')
ADMIN_DEFAULT_PASS = os.environ.get('ADMIN_PASSWORD', 'admin123')

# Database configuration: Default to MySQL URI, option/fallback for SQLite
MYSQL_URI = os.environ.get('DATABASE_URL', 'mysql+pymysql://root:@localhost/doc_verification_db')
SQLITE_URI = 'sqlite:///' + os.path.join(os.path.abspath(os.path.dirname(__file__)), 'doc_verification.db')

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

    documents = db.relationship('Document', backref='student', lazy=True, cascade="all, delete-orphan")

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)


class Document(db.Model):
    __tablename__ = 'documents'
    id = db.Column(db.Integer, primary_key=True)
    student_id = db.Column(db.Integer, db.ForeignKey('students.id'), nullable=False)
    document_name = db.Column(db.String(150), nullable=False)
    document_type = db.Column(db.String(50), nullable=False)  # ID Proof, Mark Sheet, Bonafide Certificate, Transfer Certificate, Other
    filename = db.Column(db.String(255), nullable=False)
    file_path = db.Column(db.String(255), nullable=False)
    upload_date = db.Column(db.DateTime, default=datetime.utcnow)
    status = db.Column(db.String(20), default='Pending')  # Pending, Verified, Rejected
    admin_remark = db.Column(db.Text, nullable=True)


def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


def seed_default_admin():
    """Seeds default admin account if none exists in database."""
    if db.session.query(Admin).count() == 0:
        admin = Admin(username=ADMIN_DEFAULT_USER)
        admin.set_password(ADMIN_DEFAULT_PASS)
        db.session.add(admin)
        db.session.commit()


# Decorators for route protection
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


# Landing Page
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
            flash('All registration fields are required.', 'danger')
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

        flash('Registration successful! You can now log in.', 'success')
        return redirect(url_for('login'))

    return render_template('register.html')


# Student Login
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email_or_reg = request.form.get('email_or_reg', '').strip()
        password = request.form.get('password', '')

        if not email_or_reg or not password:
            flash('Please fill in all login fields.', 'danger')
            return redirect(url_for('login'))

        student = Student.query.filter(
            (Student.email == email_or_reg.lower()) | (Student.register_number == email_or_reg)
        ).first()

        if student and student.check_password(password):
            session.clear()
            session['user_type'] = 'student'
            session['user_id'] = student.id
            session['user_name'] = student.name
            session['user_email'] = student.email
            flash(f'Welcome back, {student.name}!', 'success')
            return redirect(url_for('student_dashboard'))

        flash('Invalid Credentials. Please check your Email/Reg No and Password.', 'danger')
        return redirect(url_for('login'))

    return render_template('login.html')


# Admin Login
@app.route('/admin/login', methods=['GET', 'POST'])
def admin_login():
    if request.method == 'POST':
        username = request.form.get('username', '').strip()
        password = request.form.get('password', '')

        if not username or not password:
            flash('Please enter Admin username and password.', 'danger')
            return redirect(url_for('admin_login'))

        admin = Admin.query.filter_by(username=username).first()

        if admin and admin.check_password(password):
            session.clear()
            session['user_type'] = 'admin'
            session['admin_id'] = admin.id
            session['user_name'] = f'Admin ({admin.username})'
            flash('Administrator logged in successfully.', 'success')
            return redirect(url_for('admin_dashboard'))
        elif username == ADMIN_DEFAULT_USER and password == ADMIN_DEFAULT_PASS:
            session.clear()
            session['user_type'] = 'admin'
            session['user_name'] = f'Admin ({ADMIN_DEFAULT_USER})'
            flash('Administrator logged in successfully.', 'success')
            return redirect(url_for('admin_dashboard'))

        flash('Invalid Admin Credentials.', 'danger')
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
        flash('Student record not found.', 'danger')
        return redirect(url_for('login'))

    documents = Document.query.filter_by(student_id=student_id).all()

    total_docs = len(documents)
    pending_docs = sum(1 for d in documents if d.status == 'Pending')
    verified_docs = sum(1 for d in documents if d.status == 'Verified')
    rejected_docs = sum(1 for d in documents if d.status == 'Rejected')

    recent_documents = sorted(documents, key=lambda d: d.upload_date, reverse=True)[:5]

    return render_template(
        'student_dashboard.html',
        student=student,
        total_docs=total_docs,
        pending_docs=pending_docs,
        verified_docs=verified_docs,
        rejected_docs=rejected_docs,
        recent_documents=recent_documents
    )


# Upload Document
@app.route('/student/upload', methods=['GET', 'POST'])
@student_required
def upload_document():
    if request.method == 'POST':
        document_name = request.form.get('document_name', '').strip()
        document_type = request.form.get('document_type', '').strip()

        if not document_name or not document_type:
            flash('Document Name and Document Type are required.', 'danger')
            return redirect(url_for('upload_document'))

        valid_types = ['ID Proof', 'Mark Sheet', 'Bonafide Certificate', 'Transfer Certificate', 'Other']
        if document_type not in valid_types:
            flash('Invalid Document Type selected.', 'danger')
            return redirect(url_for('upload_document'))

        if 'document_file' not in request.files:
            flash('No document file uploaded.', 'danger')
            return redirect(url_for('upload_document'))

        file = request.files['document_file']
        if file.filename == '':
            flash('No file selected for uploading.', 'danger')
            return redirect(url_for('upload_document'))

        if not allowed_file(file.filename):
            flash('Invalid file format. Only PDF, JPG, and PNG files are allowed.', 'danger')
            return redirect(url_for('upload_document'))

        student_id = session.get('user_id')
        original_filename = secure_filename(file.filename)
        timestamp = datetime.now().strftime('%Y%m%d%H%M%S')
        unique_filename = f"std_{student_id}_{timestamp}_{original_filename}"

        saved_path = os.path.join(app.config['UPLOAD_FOLDER'], unique_filename)
        file.save(saved_path)

        relative_file_path = f"uploads/{unique_filename}"

        document = Document(
            student_id=student_id,
            document_name=document_name,
            document_type=document_type,
            filename=unique_filename,
            file_path=relative_file_path,
            status='Pending'
        )
        db.session.add(document)
        db.session.commit()

        flash('Document uploaded successfully! Verification is pending.', 'success')
        return redirect(url_for('my_documents'))

    return render_template('upload_document.html')


# My Documents (Student View)
@app.route('/student/my-documents')
@student_required
def my_documents():
    student_id = session.get('user_id')
    documents = Document.query.filter_by(student_id=student_id).order_by(Document.upload_date.desc()).all()
    return render_template('my_documents.html', documents=documents)


# Admin Dashboard
@app.route('/admin/dashboard')
@admin_required
def admin_dashboard():
    total_students = Student.query.count()
    documents = Document.query.all()

    total_docs = len(documents)
    pending_docs = sum(1 for d in documents if d.status == 'Pending')
    verified_docs = sum(1 for d in documents if d.status == 'Verified')
    rejected_docs = sum(1 for d in documents if d.status == 'Rejected')

    recent_documents = sorted(documents, key=lambda d: d.upload_date, reverse=True)[:5]
    students = Student.query.order_by(Student.created_at.desc()).all()

    return render_template(
        'admin_dashboard.html',
        total_students=total_students,
        total_docs=total_docs,
        pending_docs=pending_docs,
        verified_docs=verified_docs,
        rejected_docs=rejected_docs,
        recent_documents=recent_documents,
        students=students
    )


# Manage Documents (Admin View)
@app.route('/admin/manage-documents')
@admin_required
def manage_documents():
    status_filter = request.args.get('status', '').strip()
    if status_filter in ['Pending', 'Verified', 'Rejected']:
        documents = Document.query.filter_by(status=status_filter).order_by(Document.upload_date.desc()).all()
    else:
        documents = Document.query.order_by(Document.upload_date.desc()).all()

    return render_template('manage_documents.html', documents=documents, current_filter=status_filter)


# View Document Details & Action (Admin View)
@app.route('/admin/document/<int:doc_id>', methods=['GET', 'POST'])
@admin_required
def document_details(doc_id):
    document = db.session.get(Document, doc_id)
    if not document:
        flash('Document not found.', 'danger')
        return redirect(url_for('manage_documents'))

    if request.method == 'POST':
        action = request.form.get('action', '').strip()
        admin_remark = request.form.get('admin_remark', '').strip()

        if action == 'verify':
            document.status = 'Verified'
            document.admin_remark = admin_remark if admin_remark else 'Document verified successfully.'
            db.session.commit()
            flash(f'Document "{document.document_name}" marked as Verified.', 'success')
            return redirect(url_for('document_details', doc_id=doc_id))

        elif action == 'reject':
            document.status = 'Rejected'
            document.admin_remark = admin_remark if admin_remark else 'Document rejected. Please re-upload clear document.'
            db.session.commit()
            flash(f'Document "{document.document_name}" marked as Rejected.', 'warning')
            return redirect(url_for('document_details', doc_id=doc_id))

        elif action == 'delete':
            file_disk_path = os.path.join(app.config['UPLOAD_FOLDER'], document.filename)
            if os.path.exists(file_disk_path):
                try:
                    os.remove(file_disk_path)
                except OSError:
                    pass

            doc_name = document.document_name
            db.session.delete(document)
            db.session.commit()
            flash(f'Document "{doc_name}" has been deleted.', 'danger')
            return redirect(url_for('manage_documents'))

    return render_template('document_details.html', document=document)


# Delete Document Route for Admin
@app.route('/admin/document/delete/<int:doc_id>', methods=['POST'])
@admin_required
def delete_document(doc_id):
    document = db.session.get(Document, doc_id)
    if not document:
        flash('Document not found.', 'danger')
        return redirect(url_for('manage_documents'))

    file_disk_path = os.path.join(app.config['UPLOAD_FOLDER'], document.filename)
    if os.path.exists(file_disk_path):
        try:
            os.remove(file_disk_path)
        except OSError:
            pass

    doc_name = document.document_name
    db.session.delete(document)
    db.session.commit()
    flash(f'Document "{doc_name}" deleted successfully.', 'info')
    return redirect(url_for('manage_documents'))


if __name__ == '__main__':
    with app.app_context():
        db.create_all()
        seed_default_admin()
    app.run(debug=True)
