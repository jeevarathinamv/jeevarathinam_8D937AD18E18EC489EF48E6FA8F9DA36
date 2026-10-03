import os
from datetime import datetime
from functools import wraps
from flask import Flask, render_template, request, redirect, url_for, flash, session
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename

app = Flask(__name__)
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'student_project_showcase_secret_key_123')

# Database configuration: Default to MySQL URI, fallback/option for SQLite
MYSQL_URI = os.environ.get('DATABASE_URL', 'mysql+pymysql://root:@localhost/student_project_showcase')
SQLITE_URI = 'sqlite:///' + os.path.join(os.path.abspath(os.path.dirname(__file__)), 'student_project_showcase.db')

use_sqlite = os.environ.get('USE_SQLITE') == '1'
app.config['SQLALCHEMY_DATABASE_URI'] = SQLITE_URI if use_sqlite else MYSQL_URI
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# File Upload Configuration
UPLOAD_FOLDER = os.path.join(os.path.abspath(os.path.dirname(__file__)), 'static', 'uploads')
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'webp'}
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16 MB max upload limit

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

    projects = db.relationship('Project', backref='student', cascade='all, delete-orphan', lazy=True)

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

class Project(db.Model):
    __tablename__ = 'projects'
    id = db.Column(db.Integer, primary_key=True)
    student_id = db.Column(db.Integer, db.ForeignKey('students.id', ondelete='CASCADE'), nullable=False)
    title = db.Column(db.String(150), nullable=False)
    description = db.Column(db.Text, nullable=False)
    category = db.Column(db.String(50), nullable=False)
    technologies = db.Column(db.String(200), nullable=False)
    image_path = db.Column(db.String(255), nullable=True)
    project_link = db.Column(db.String(255), nullable=True)
    status = db.Column(db.String(20), default='Pending', nullable=False) # Pending, Approved, Rejected
    admin_remark = db.Column(db.Text, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

CATEGORIES = [
    'Web Development',
    'Python',
    'Java',
    'Mobile App',
    'Data Science',
    'Other'
]

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def save_upload_file(file):
    if file and file.filename != '' and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S_')
        unique_filename = timestamp + filename
        os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
        file_path = os.path.join(app.config['UPLOAD_FOLDER'], unique_filename)
        file.save(file_path)
        return f'uploads/{unique_filename}'
    return None

def seed_default_data():
    os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

    # Ensure default admin exists
    admin = db.session.query(Admin).filter_by(username='admin').first()
    if not admin:
        admin = Admin(username='admin')
        admin.set_password('admin123')
        db.session.add(admin)
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

@app.context_processor
def inject_categories():
    return dict(categories=CATEGORIES)

# Routes

@app.route('/')
def index():
    approved_projects = db.session.query(Project).filter_by(status='Approved').order_by(Project.created_at.desc()).limit(6).all()
    total_approved = db.session.query(Project).filter_by(status='Approved').count()
    total_students = db.session.query(Student).count()
    return render_template('index.html', projects=approved_projects, total_approved=total_approved, total_students=total_students)

@app.route('/showcase')
def showcase():
    category = request.args.get('category', '').strip()
    search = request.args.get('search', '').strip()

    query = db.session.query(Project).filter_by(status='Approved')

    if category and category in CATEGORIES:
        query = query.filter(Project.category == category)

    if search:
        search_pattern = f"%{search}%"
        query = query.join(Student).filter(
            (Project.title.ilike(search_pattern)) |
            (Project.technologies.ilike(search_pattern)) |
            (Project.description.ilike(search_pattern)) |
            (Student.name.ilike(search_pattern)) |
            (Student.department.ilike(search_pattern))
        )

    projects = query.order_by(Project.created_at.desc()).all()
    return render_template('showcase.html', projects=projects, selected_category=category, search_query=search)

@app.route('/project/<int:project_id>')
def project_details(project_id):
    project = db.session.get(Project, project_id)
    if not project:
        flash('Project not found.', 'danger')
        return redirect(url_for('showcase'))

    # Access control: approved projects are public; non-approved projects only visible to owner student or admin
    is_owner = session.get('user_type') == 'student' and session.get('user_id') == project.student_id
    is_admin = session.get('user_type') == 'admin'

    if project.status != 'Approved' and not is_owner and not is_admin:
        flash('This project is not currently published.', 'warning')
        return redirect(url_for('showcase'))

    return render_template('project_details.html', project=project, is_owner=is_owner, is_admin=is_admin)

# Student Auth & Dashboard

@app.route('/register', methods=['GET', 'POST'])
def register():
    if session.get('user_type') == 'student':
        return redirect(url_for('student_dashboard'))

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

        flash('Registration successful! Please log in.', 'success')
        return redirect(url_for('login'))

    return render_template('register.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if session.get('user_type') == 'student':
        return redirect(url_for('student_dashboard'))

    if request.method == 'POST':
        login_input = request.form.get('login_input', '').strip()
        password = request.form.get('password', '')

        if not login_input or not password:
            flash('Please enter both Register Number/Email and Password.', 'danger')
            return redirect(url_for('login'))

        student = db.session.query(Student).filter(
            (Student.email == login_input.lower()) | (Student.register_number == login_input)
        ).first()

        if student and student.check_password(password):
            session['user_type'] = 'student'
            session['user_id'] = student.id
            session['user_name'] = student.name
            flash(f'Welcome back, {student.name}!', 'success')
            return redirect(url_for('student_dashboard'))
        else:
            flash('Invalid Register Number/Email or Password.', 'danger')
            return redirect(url_for('login'))

    return render_template('login.html')

@app.route('/logout')
def logout():
    session.clear()
    flash('You have been logged out.', 'info')
    return redirect(url_for('index'))

@app.route('/student/dashboard')
@student_required
def student_dashboard():
    student_id = session.get('user_id')
    student = db.session.get(Student, student_id)

    student_projects = db.session.query(Project).filter_by(student_id=student_id).all()

    total_my_projects = len(student_projects)
    published_count = len([p for p in student_projects if p.status == 'Approved'])
    pending_count = len([p for p in student_projects if p.status == 'Pending'])
    rejected_count = len([p for p in student_projects if p.status == 'Rejected'])

    recent_projects = db.session.query(Project).filter_by(student_id=student_id).order_by(Project.created_at.desc()).limit(5).all()

    return render_template(
        'student_dashboard.html',
        student=student,
        total_my_projects=total_my_projects,
        published_count=published_count,
        pending_count=pending_count,
        rejected_count=rejected_count,
        recent_projects=recent_projects
    )

@app.route('/student/add_project', methods=['GET', 'POST'])
@student_required
def add_project():
    if request.method == 'POST':
        title = request.form.get('title', '').strip()
        description = request.form.get('description', '').strip()
        technologies = request.form.get('technologies', '').strip()
        category = request.form.get('category', '').strip()
        project_link = request.form.get('project_link', '').strip()

        if not title or not description or not technologies or not category:
            flash('Title, Description, Category, and Technologies are required.', 'danger')
            return redirect(url_for('add_project'))

        if category not in CATEGORIES:
            flash('Please select a valid Category.', 'danger')
            return redirect(url_for('add_project'))

        image_path = None
        if 'project_image' in request.files:
            file = request.files['project_image']
            if file and file.filename != '':
                if allowed_file(file.filename):
                    image_path = save_upload_file(file)
                else:
                    flash('Invalid image format. Allowed formats: PNG, JPG, JPEG, GIF, WEBP.', 'danger')
                    return redirect(url_for('add_project'))

        project = Project(
            student_id=session.get('user_id'),
            title=title,
            description=description,
            technologies=technologies,
            category=category,
            project_link=project_link if project_link else None,
            image_path=image_path,
            status='Pending'
        )
        db.session.add(project)
        db.session.commit()

        flash('Project submitted successfully! It is currently pending admin approval.', 'success')
        return redirect(url_for('my_projects'))

    return render_template('add_project.html')

@app.route('/student/my_projects')
@student_required
def my_projects():
    student_id = session.get('user_id')
    projects = db.session.query(Project).filter_by(student_id=student_id).order_by(Project.created_at.desc()).all()
    return render_template('my_projects.html', projects=projects)

@app.route('/student/edit_project/<int:project_id>', methods=['GET', 'POST'])
@student_required
def edit_project(project_id):
    project = db.session.get(Project, project_id)
    if not project:
        flash('Project not found.', 'danger')
        return redirect(url_for('my_projects'))

    # Ownership Check
    if project.student_id != session.get('user_id'):
        flash('Access denied. You cannot edit another student\'s project.', 'danger')
        return redirect(url_for('my_projects'))

    if request.method == 'POST':
        title = request.form.get('title', '').strip()
        description = request.form.get('description', '').strip()
        technologies = request.form.get('technologies', '').strip()
        category = request.form.get('category', '').strip()
        project_link = request.form.get('project_link', '').strip()

        if not title or not description or not technologies or not category:
            flash('Title, Description, Category, and Technologies are required.', 'danger')
            return redirect(url_for('edit_project', project_id=project.id))

        if category not in CATEGORIES:
            flash('Please select a valid Category.', 'danger')
            return redirect(url_for('edit_project', project_id=project.id))

        if 'project_image' in request.files:
            file = request.files['project_image']
            if file and file.filename != '':
                if allowed_file(file.filename):
                    new_image_path = save_upload_file(file)
                    if new_image_path:
                        project.image_path = new_image_path
                else:
                    flash('Invalid image format. Allowed formats: PNG, JPG, JPEG, GIF, WEBP.', 'danger')
                    return redirect(url_for('edit_project', project_id=project.id))

        project.title = title
        project.description = description
        project.technologies = technologies
        project.category = category
        project.project_link = project_link if project_link else None

        # Reset status to Pending upon editing
        project.status = 'Pending'
        project.admin_remark = None
        db.session.commit()

        flash('Project updated successfully! Status reset to Pending for re-review.', 'success')
        return redirect(url_for('my_projects'))

    return render_template('edit_project.html', project=project)

@app.route('/student/delete_project/<int:project_id>', methods=['POST'])
@student_required
def delete_project(project_id):
    project = db.session.get(Project, project_id)
    if not project:
        flash('Project not found.', 'danger')
        return redirect(url_for('my_projects'))

    # Ownership Check
    if project.student_id != session.get('user_id'):
        flash('Access denied. You cannot delete another student\'s project.', 'danger')
        return redirect(url_for('my_projects'))

    db.session.delete(project)
    db.session.commit()
    flash('Project deleted successfully.', 'info')
    return redirect(url_for('my_projects'))

# Admin Module

@app.route('/admin/login', methods=['GET', 'POST'])
def admin_login():
    if session.get('user_type') == 'admin':
        return redirect(url_for('admin_dashboard'))

    if request.method == 'POST':
        username = request.form.get('username', '').strip()
        password = request.form.get('password', '')

        admin = db.session.query(Admin).filter_by(username=username).first()
        if admin and admin.check_password(password):
            session['user_type'] = 'admin'
            session['user_name'] = 'Administrator'
            flash('Logged in successfully as Administrator.', 'success')
            return redirect(url_for('admin_dashboard'))
        else:
            flash('Invalid Admin Username or Password.', 'danger')
            return redirect(url_for('admin_login'))

    return render_template('admin_login.html')

@app.route('/admin/dashboard')
@admin_required
def admin_dashboard():
    total_students = db.session.query(Student).count()
    total_projects = db.session.query(Project).count()
    pending_projects = db.session.query(Project).filter_by(status='Pending').count()
    approved_projects = db.session.query(Project).filter_by(status='Approved').count()
    rejected_projects = db.session.query(Project).filter_by(status='Rejected').count()

    recent_submissions = db.session.query(Project).order_by(Project.created_at.desc()).limit(5).all()

    return render_template(
        'admin_dashboard.html',
        total_students=total_students,
        total_projects=total_projects,
        pending_projects=pending_projects,
        approved_projects=approved_projects,
        rejected_projects=rejected_projects,
        recent_submissions=recent_submissions
    )

@app.route('/admin/manage_projects')
@admin_required
def manage_projects():
    status_filter = request.args.get('status', 'all').strip()
    query = db.session.query(Project)

    if status_filter in ['Pending', 'Approved', 'Rejected']:
        query = query.filter_by(status=status_filter)

    projects = query.order_by(Project.created_at.desc()).all()
    return render_template('manage_projects.html', projects=projects, current_status=status_filter)

@app.route('/admin/project/approve/<int:project_id>', methods=['POST'])
@admin_required
def approve_project(project_id):
    project = db.session.get(Project, project_id)
    if not project:
        flash('Project not found.', 'danger')
        return redirect(url_for('manage_projects'))

    remark = request.form.get('admin_remark', '').strip()
    project.status = 'Approved'
    if remark:
        project.admin_remark = remark

    db.session.commit()
    flash(f'Project "{project.title}" has been Approved and published to Showcase.', 'success')
    return redirect(url_for('manage_projects'))

@app.route('/admin/project/reject/<int:project_id>', methods=['POST'])
@admin_required
def reject_project(project_id):
    project = db.session.get(Project, project_id)
    if not project:
        flash('Project not found.', 'danger')
        return redirect(url_for('manage_projects'))

    remark = request.form.get('admin_remark', '').strip()
    project.status = 'Rejected'
    project.admin_remark = remark if remark else 'No specific remark provided.'

    db.session.commit()
    flash(f'Project "{project.title}" has been Rejected.', 'info')
    return redirect(url_for('manage_projects'))

@app.route('/admin/project/delete/<int:project_id>', methods=['POST'])
@admin_required
def admin_delete_project(project_id):
    project = db.session.get(Project, project_id)
    if not project:
        flash('Project not found.', 'danger')
        return redirect(url_for('manage_projects'))

    db.session.delete(project)
    db.session.commit()
    flash('Project deleted by admin.', 'info')
    return redirect(url_for('manage_projects'))

@app.route('/admin/manage_students')
@admin_required
def manage_students():
    students = db.session.query(Student).order_by(Student.created_at.desc()).all()
    return render_template('manage_students.html', students=students)

@app.route('/admin/student/delete/<int:student_id>', methods=['POST'])
@admin_required
def delete_student(student_id):
    student = db.session.get(Student, student_id)
    if not student:
        flash('Student not found.', 'danger')
        return redirect(url_for('manage_students'))

    db.session.delete(student)
    db.session.commit()
    flash(f'Student "{student.name}" and all associated projects deleted.', 'info')
    return redirect(url_for('manage_students'))

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
        seed_default_data()
    app.run(debug=True)
