import os
import random
from datetime import datetime, date
from functools import wraps
from flask import Flask, render_template, request, redirect, url_for, flash, session
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'college_entrepreneurship_secret_key_123')

# Admin Hardcoded Fallback Credentials
ADMIN_USERNAME = os.environ.get('ADMIN_USERNAME', 'admin')
ADMIN_PASSWORD = os.environ.get('ADMIN_PASSWORD', 'admin123')

# Database configuration: Default to MySQL URI, fallback to SQLite if USE_SQLITE=1
MYSQL_URI = os.environ.get('DATABASE_URL', 'mysql+pymysql://root:@localhost/college_entrepreneurship_portal')
SQLITE_URI = 'sqlite:///' + os.path.join(os.path.abspath(os.path.dirname(__file__)), 'college_entrepreneurship.db')

use_sqlite = os.environ.get('USE_SQLITE') == '1'
app.config['SQLALCHEMY_DATABASE_URI'] = SQLITE_URI if use_sqlite else MYSQL_URI
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

# ---------------------------------------------------------------------------
# Database Models
# ---------------------------------------------------------------------------

class Student(db.Model):
    __tablename__ = 'students'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    register_number = db.Column(db.String(50), unique=True, nullable=False)
    department = db.Column(db.String(100), nullable=False)
    year = db.Column(db.String(20), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    phone = db.Column(db.String(20), nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    ideas = db.relationship('Idea', backref='student', lazy=True, cascade="all, delete-orphan")

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


class Idea(db.Model):
    __tablename__ = 'ideas'
    id = db.Column(db.Integer, primary_key=True)
    idea_id = db.Column(db.String(50), unique=True, nullable=False)
    student_id = db.Column(db.Integer, db.ForeignKey('students.id'), nullable=False)
    title = db.Column(db.String(200), nullable=False)
    problem_statement = db.Column(db.Text, nullable=False)
    proposed_solution = db.Column(db.Text, nullable=False)
    target_customers = db.Column(db.Text, nullable=False)
    category = db.Column(db.String(50), nullable=False)
    required_resources = db.Column(db.Text, nullable=False)
    estimated_budget = db.Column(db.String(100), nullable=False)
    expected_benefits = db.Column(db.Text, nullable=False)
    submission_date = db.Column(db.Date, nullable=False, default=date.today)
    status = db.Column(db.String(20), default='Pending')  # Pending, Under Review, Approved, Rejected, Selected
    admin_remarks = db.Column(db.Text, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    evaluation = db.relationship('Evaluation', uselist=False, backref='idea', lazy=True, cascade="all, delete-orphan")


class Evaluation(db.Model):
    __tablename__ = 'evaluations'
    id = db.Column(db.Integer, primary_key=True)
    idea_id = db.Column(db.Integer, db.ForeignKey('ideas.id'), unique=True, nullable=False)
    innovation_score = db.Column(db.Integer, nullable=False, default=0)
    feasibility_score = db.Column(db.Integer, nullable=False, default=0)
    market_potential_score = db.Column(db.Integer, nullable=False, default=0)
    social_impact_score = db.Column(db.Integer, nullable=False, default=0)
    total_score = db.Column(db.Integer, nullable=False, default=0)
    overall_remarks = db.Column(db.Text, nullable=True)
    evaluated_at = db.Column(db.DateTime, default=datetime.utcnow)


def generate_unique_idea_id():
    """Generates a unique Idea ID like IDEA-1001"""
    while True:
        num = random.randint(1000, 9999)
        candidate = f"IDEA-{num}"
        if not db.session.query(Idea).filter_by(idea_id=candidate).first():
            return candidate


def seed_default_data():
    """Seeds default Admin account if not existing"""
    admin = db.session.query(Admin).filter_by(username='admin').first()
    if not admin:
        default_admin = Admin(username='admin')
        default_admin.set_password('admin123')
        db.session.add(default_admin)
        db.session.commit()

# ---------------------------------------------------------------------------
# Authentication Decorators
# ---------------------------------------------------------------------------

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

# ---------------------------------------------------------------------------
# General & Authentication Routes
# ---------------------------------------------------------------------------

@app.route('/')
def index():
    return render_template('index.html')


@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        name = request.form.get('name', '').strip()
        register_number = request.form.get('register_number', '').strip()
        department = request.form.get('department', '').strip()
        year = request.form.get('year', '').strip()
        email = request.form.get('email', '').strip().lower()
        phone = request.form.get('phone', '').strip()
        password = request.form.get('password', '')

        if not name or not register_number or not department or not year or not email or not phone or not password:
            flash('All registration fields are required.', 'danger')
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
            year=year,
            email=email,
            phone=phone
        )
        student.set_password(password)
        db.session.add(student)
        db.session.commit()

        flash('Registration successful! Please log in.', 'success')
        return redirect(url_for('login'))

    return render_template('register.html')


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        login_id = request.form.get('login_id', '').strip()
        password = request.form.get('password', '')

        student = db.session.query(Student).filter(
            (Student.email == login_id.lower()) | (Student.register_number == login_id)
        ).first()

        if student and student.check_password(password):
            session['user_type'] = 'student'
            session['user_id'] = student.id
            session['user_name'] = student.name
            session['register_number'] = student.register_number
            flash(f'Welcome back, {student.name}!', 'success')
            return redirect(url_for('student_dashboard'))
        else:
            flash('Invalid Register Number / Email or Password.', 'danger')
            return redirect(url_for('login'))

    return render_template('login.html')


@app.route('/admin/login', methods=['GET', 'POST'])
def admin_login():
    if request.method == 'POST':
        username = request.form.get('username', '').strip()
        password = request.form.get('password', '')

        admin = db.session.query(Admin).filter_by(username=username).first()

        if (admin and admin.check_password(password)) or (username == ADMIN_USERNAME and password == ADMIN_PASSWORD):
            session['user_type'] = 'admin'
            session['user_name'] = 'Administrator'
            flash('Logged in successfully as Administrator.', 'success')
            return redirect(url_for('admin_dashboard'))
        else:
            flash('Invalid admin credentials.', 'danger')
            return redirect(url_for('admin_login'))

    return render_template('admin_login.html')


@app.route('/logout')
def logout():
    session.clear()
    flash('You have been logged out.', 'info')
    return redirect(url_for('index'))

# ---------------------------------------------------------------------------
# Student Routes
# ---------------------------------------------------------------------------

@app.route('/student/dashboard')
@student_required
def student_dashboard():
    student_id = session.get('user_id')
    student = db.session.get(Student, student_id)

    ideas = db.session.query(Idea).filter_by(student_id=student_id).order_by(Idea.created_at.desc()).all()

    total_ideas = len(ideas)
    pending_ideas = len([i for i in ideas if i.status == 'Pending'])
    approved_ideas = len([i for i in ideas if i.status == 'Approved'])
    rejected_ideas = len([i for i in ideas if i.status == 'Rejected'])
    selected_ideas = len([i for i in ideas if i.status == 'Selected'])

    return render_template(
        'student_dashboard.html',
        student=student,
        ideas=ideas[:5], # Recent 5 ideas
        total_ideas=total_ideas,
        pending_ideas=pending_ideas,
        approved_ideas=approved_ideas,
        rejected_ideas=rejected_ideas,
        selected_ideas=selected_ideas
    )


@app.route('/submit_idea', methods=['GET', 'POST'])
@student_required
def submit_idea():
    student_id = session.get('user_id')
    student = db.session.get(Student, student_id)

    if request.method == 'POST':
        title = request.form.get('title', '').strip()
        problem_statement = request.form.get('problem_statement', '').strip()
        proposed_solution = request.form.get('proposed_solution', '').strip()
        target_customers = request.form.get('target_customers', '').strip()
        category = request.form.get('category', '').strip()
        required_resources = request.form.get('required_resources', '').strip()
        estimated_budget = request.form.get('estimated_budget', '').strip()
        expected_benefits = request.form.get('expected_benefits', '').strip()

        if not title or not problem_statement or not proposed_solution or not target_customers or not category or not required_resources or not estimated_budget or not expected_benefits:
            flash('All fields in the idea submission form are required.', 'danger')
            return redirect(url_for('submit_idea'))

        idea_id = generate_unique_idea_id()

        new_idea = Idea(
            idea_id=idea_id,
            student_id=student_id,
            title=title,
            problem_statement=problem_statement,
            proposed_solution=proposed_solution,
            target_customers=target_customers,
            category=category,
            required_resources=required_resources,
            estimated_budget=estimated_budget,
            expected_benefits=expected_benefits,
            submission_date=date.today(),
            status='Pending'
        )

        db.session.add(new_idea)
        db.session.commit()

        flash('Your entrepreneurship idea has been submitted successfully.', 'success')
        return redirect(url_for('my_ideas'))

    today_str = date.today().strftime('%Y-%m-%d')
    return render_template('submit_idea.html', student=student, today_str=today_str)


@app.route('/my_ideas')
@student_required
def my_ideas():
    student_id = session.get('user_id')
    ideas = db.session.query(Idea).filter_by(student_id=student_id).order_by(Idea.created_at.desc()).all()
    return render_template('my_ideas.html', ideas=ideas)


@app.route('/idea/<int:id>')
def idea_details(id):
    idea = db.session.get(Idea, id)
    if not idea:
        flash('Idea not found.', 'danger')
        return redirect(url_for('index'))

    # Access control: Student can view their own, Admin can view all
    user_type = session.get('user_type')
    user_id = session.get('user_id')

    if user_type == 'student' and idea.student_id != user_id:
        flash('Unauthorized access to this idea.', 'danger')
        return redirect(url_for('my_ideas'))
    elif not user_type:
        flash('Please log in to view idea details.', 'warning')
        return redirect(url_for('login'))

    return render_template('idea_details.html', idea=idea)


@app.route('/resources')
def resources():
    return render_template('resources.html')

# ---------------------------------------------------------------------------
# Admin Routes
# ---------------------------------------------------------------------------

@app.route('/admin/dashboard')
@admin_required
def admin_dashboard():
    total_students = db.session.query(Student).count()
    total_ideas = db.session.query(Idea).count()

    pending_ideas = db.session.query(Idea).filter_by(status='Pending').count()
    under_review_ideas = db.session.query(Idea).filter_by(status='Under Review').count()
    approved_ideas = db.session.query(Idea).filter_by(status='Approved').count()
    rejected_ideas = db.session.query(Idea).filter_by(status='Rejected').count()
    selected_ideas = db.session.query(Idea).filter_by(status='Selected').count()

    recent_ideas = db.session.query(Idea).order_by(Idea.created_at.desc()).limit(5).all()

    return render_template(
        'admin_dashboard.html',
        total_students=total_students,
        total_ideas=total_ideas,
        pending_ideas=pending_ideas,
        under_review_ideas=under_review_ideas,
        approved_ideas=approved_ideas,
        rejected_ideas=rejected_ideas,
        selected_ideas=selected_ideas,
        recent_ideas=recent_ideas
    )


@app.route('/admin/students')
@admin_required
def manage_students():
    search_query = request.args.get('search', '').strip()
    if search_query:
        students = db.session.query(Student).filter(
            (Student.name.ilike(f'%{search_query}%')) |
            (Student.register_number.ilike(f'%{search_query}%')) |
            (Student.department.ilike(f'%{search_query}%'))
        ).order_by(Student.created_at.desc()).all()
    else:
        students = db.session.query(Student).order_by(Student.created_at.desc()).all()

    return render_template('manage_students.html', students=students, search_query=search_query)


@app.route('/admin/ideas')
@admin_required
def manage_ideas():
    search_query = request.args.get('search', '').strip()
    category_filter = request.args.get('category', '').strip()
    status_filter = request.args.get('status', '').strip()

    query = db.session.query(Idea).join(Student)

    if search_query:
        query = query.filter(
            (Idea.idea_id.ilike(f'%{search_query}%')) |
            (Student.name.ilike(f'%{search_query}%')) |
            (Idea.title.ilike(f'%{search_query}%'))
        )

    if category_filter:
        query = query.filter(Idea.category == category_filter)

    if status_filter:
        query = query.filter(Idea.status == status_filter)

    ideas = query.order_by(Idea.created_at.desc()).all()

    categories = ["Technology", "Education", "Healthcare", "Agriculture", "Food", "E-Commerce", "Finance", "Environment", "Other"]
    statuses = ["Pending", "Under Review", "Approved", "Rejected", "Selected"]

    return render_template(
        'manage_ideas.html',
        ideas=ideas,
        categories=categories,
        statuses=statuses,
        search_query=search_query,
        category_filter=category_filter,
        status_filter=status_filter
    )


@app.route('/admin/idea/update_status/<int:id>', methods=['POST'])
@admin_required
def update_idea_status(id):
    idea = db.session.get(Idea, id)
    if not idea:
        flash('Idea not found.', 'danger')
        return redirect(url_for('manage_ideas'))

    new_status = request.form.get('status', '').strip()
    admin_remarks = request.form.get('admin_remarks', '').strip()

    if new_status in ["Pending", "Under Review", "Approved", "Rejected", "Selected"]:
        idea.status = new_status
        idea.admin_remarks = admin_remarks
        db.session.commit()
        flash(f'Status for idea {idea.idea_id} updated to "{new_status}".', 'success')
    else:
        flash('Invalid status selected.', 'danger')

    return redirect(request.referrer or url_for('manage_ideas'))


@app.route('/admin/idea/evaluate/<int:id>', methods=['GET', 'POST'])
@admin_required
def evaluate_idea(id):
    idea = db.session.get(Idea, id)
    if not idea:
        flash('Idea not found.', 'danger')
        return redirect(url_for('manage_ideas'))

    evaluation = idea.evaluation

    if request.method == 'POST':
        try:
            innovation_score = int(request.form.get('innovation_score', 0))
            feasibility_score = int(request.form.get('feasibility_score', 0))
            market_potential_score = int(request.form.get('market_potential_score', 0))
            social_impact_score = int(request.form.get('social_impact_score', 0))
        except ValueError:
            flash('Scores must be integers between 1 and 10.', 'danger')
            return redirect(url_for('evaluate_idea', id=id))

        overall_remarks = request.form.get('overall_remarks', '').strip()

        # Validate range 1 to 10
        for name, score in [('Innovation', innovation_score), ('Feasibility', feasibility_score), ('Market Potential', market_potential_score), ('Social Impact', social_impact_score)]:
            if score < 1 or score > 10:
                flash(f'{name} Score must be between 1 and 10.', 'danger')
                return redirect(url_for('evaluate_idea', id=id))

        total_score = innovation_score + feasibility_score + market_potential_score + social_impact_score

        if not evaluation:
            evaluation = Evaluation(idea_id=idea.id)

        evaluation.innovation_score = innovation_score
        evaluation.feasibility_score = feasibility_score
        evaluation.market_potential_score = market_potential_score
        evaluation.social_impact_score = social_impact_score
        evaluation.total_score = total_score
        evaluation.overall_remarks = overall_remarks

        db.session.add(evaluation)
        db.session.commit()

        flash(f'Evaluation saved successfully for {idea.idea_id}. Total Score: {total_score}/40.', 'success')
        return redirect(url_for('manage_ideas'))

    return render_template('evaluate_idea.html', idea=idea, evaluation=evaluation)


@app.route('/selected_ideas')
def selected_ideas():
    ideas = db.session.query(Idea).filter_by(status='Selected').order_by(Idea.created_at.desc()).all()
    return render_template('selected_ideas.html', ideas=ideas)


if __name__ == '__main__':
    with app.app_context():
        db.create_all()
        seed_default_data()
    app.run(debug=True)
