import os
import re
from datetime import datetime
from functools import wraps
from flask import Flask, render_template, request, redirect, url_for, flash, session
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'student_mock_interview_secret_key_98765')

# Admin Hardcoded Credentials
ADMIN_USERNAME = os.environ.get('ADMIN_USERNAME', 'admin')
ADMIN_PASSWORD = os.environ.get('ADMIN_PASSWORD', 'admin123')

# Database configuration: Default to MySQL URI, fallback/option for SQLite
MYSQL_URI = os.environ.get('DATABASE_URL', 'mysql+pymysql://root:@localhost/mock_interview_db')
SQLITE_URI = 'sqlite:///' + os.path.join(os.path.abspath(os.path.dirname(__file__)), 'mock_interview.db')

use_sqlite = os.environ.get('USE_SQLITE') == '1'
app.config['SQLALCHEMY_DATABASE_URI'] = SQLITE_URI if use_sqlite else MYSQL_URI
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

# Database Models
class Student(db.Model):
    __tablename__ = 'students'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    register_number = db.Column(db.String(50), unique=True, nullable=False)
    department = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    attempts = db.relationship('InterviewAttempt', backref='student', lazy=True, cascade='all, delete-orphan')

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)


class Category(db.Model):
    __tablename__ = 'categories'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), unique=True, nullable=False)
    description = db.Column(db.Text, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    questions = db.relationship('Question', backref='category', lazy=True, cascade='all, delete-orphan')
    attempts = db.relationship('InterviewAttempt', backref='category', lazy=True, cascade='all, delete-orphan')


class Question(db.Model):
    __tablename__ = 'questions'
    id = db.Column(db.Integer, primary_key=True)
    category_id = db.Column(db.Integer, db.ForeignKey('categories.id'), nullable=False)
    question_text = db.Column(db.Text, nullable=False)
    sample_answer = db.Column(db.Text, nullable=False)
    keywords = db.Column(db.Text, nullable=False)  # Comma separated keywords
    max_marks = db.Column(db.Integer, nullable=False, default=10)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    answers = db.relationship('InterviewAnswer', backref='question', lazy=True, cascade='all, delete-orphan')


class InterviewAttempt(db.Model):
    __tablename__ = 'interview_attempts'
    id = db.Column(db.Integer, primary_key=True)
    student_id = db.Column(db.Integer, db.ForeignKey('students.id'), nullable=False)
    category_id = db.Column(db.Integer, db.ForeignKey('categories.id'), nullable=False)
    total_score = db.Column(db.Float, nullable=False, default=0.0)
    max_possible_score = db.Column(db.Float, nullable=False, default=0.0)
    percentage = db.Column(db.Float, nullable=False, default=0.0)
    feedback = db.Column(db.Text, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    answers = db.relationship('InterviewAnswer', backref='attempt', lazy=True, cascade='all, delete-orphan')


class InterviewAnswer(db.Model):
    __tablename__ = 'interview_answers'
    id = db.Column(db.Integer, primary_key=True)
    attempt_id = db.Column(db.Integer, db.ForeignKey('interview_attempts.id'), nullable=False)
    question_id = db.Column(db.Integer, db.ForeignKey('questions.id'), nullable=False)
    user_answer = db.Column(db.Text, nullable=True)
    score = db.Column(db.Float, nullable=False, default=0.0)
    max_marks = db.Column(db.Integer, nullable=False, default=10)
    feedback = db.Column(db.Text, nullable=True)


def evaluate_answer(user_answer, sample_answer, keywords_str, max_marks=10):
    """
    Evaluates student's written response against sample answer & predefined keywords.
    Returns: (score, feedback)
    """
    if not user_answer or not user_answer.strip():
        return 0.0, "No answer provided."

    clean_user_ans = user_answer.strip().lower()

    keywords = [kw.strip().lower() for kw in keywords_str.split(',') if kw.strip()]
    if not keywords:
        keywords = [kw.strip().lower() for kw in re.findall(r'\b\w+\b', sample_answer.lower()) if len(kw) > 3]

    matched_keywords = [kw for kw in keywords if kw in clean_user_ans]
    match_ratio = len(matched_keywords) / len(keywords) if keywords else 0.0

    # Calculate score
    score = round(match_ratio * max_marks, 1)

    # Feedback generation
    if score >= max_marks * 0.85:
        feedback = f"Excellent answer! You effectively covered key concepts ({', '.join(matched_keywords)})."
    elif score >= max_marks * 0.5:
        feedback = f"Good effort. Mentioned key concepts: {', '.join(matched_keywords)}. Try adding more explanations."
    elif score > 0:
        feedback = f"Partially correct. Identified terms: {', '.join(matched_keywords)}. Please review the sample answer."
    else:
        feedback = "Answer needs improvement. Crucial keywords were missing. Please study the sample answer."

    return min(score, float(max_marks)), feedback


def seed_default_data():
    """Seeds initial categories and sample interview questions if empty."""
    if Category.query.count() == 0:
        python_cat = Category(name='Python', description='Core Python concepts, data structures, OOP, and standard library questions.')
        java_cat = Category(name='Java', description='Java fundamentals, Object-Oriented Programming, collections, and exception handling.')
        sql_cat = Category(name='SQL', description='Relational database concepts, SQL queries, joins, indexing, and aggregations.')
        hr_cat = Category(name='HR', description='Behavioral, situational, soft skills, and HR interview questions.')

        db.session.add_all([python_cat, java_cat, sql_cat, hr_cat])
        db.session.commit()

        questions = [
            # Python
            Question(
                category_id=python_cat.id,
                question_text='What is the difference between list and tuple in Python?',
                sample_answer='Lists are mutable while tuples are immutable. Lists use square brackets [] whereas tuples use parentheses ().',
                keywords='mutable, immutable, brackets, parentheses, tuple, list',
                max_marks=10
            ),
            Question(
                category_id=python_cat.id,
                question_text='Explain PEP 8 and why it is important.',
                sample_answer='PEP 8 is Python style guide. It provides guidelines and best practices on how to format Python code for readability and consistency.',
                keywords='style, guide, readability, formatting, guidelines, standard',
                max_marks=10
            ),
            Question(
                category_id=python_cat.id,
                question_text='What are decorators in Python and how do they work?',
                sample_answer='A decorator is a design pattern in Python used to extend or modify the behavior of a function or method without altering its actual code structure.',
                keywords='function, modify, behavior, wrapper, pattern, extend',
                max_marks=10
            ),

            # Java
            Question(
                category_id=java_cat.id,
                question_text='What are the main principles of Object-Oriented Programming (OOP) in Java?',
                sample_answer='The four main OOP principles in Java are Encapsulation, Inheritance, Polymorphism, and Abstraction.',
                keywords='encapsulation, inheritance, polymorphism, abstraction, oop',
                max_marks=10
            ),
            Question(
                category_id=java_cat.id,
                question_text='What is the difference between JDK, JRE, and JVM?',
                sample_answer='JVM executes bytecode, JRE provides libraries and runtime environment, and JDK is the development kit containing debugging tools and compiler.',
                keywords='jvm, jre, jdk, bytecode, runtime, compiler, development',
                max_marks=10
            ),

            # SQL
            Question(
                category_id=sql_cat.id,
                question_text='What is the difference between INNER JOIN and LEFT JOIN in SQL?',
                sample_answer='INNER JOIN returns records that have matching values in both tables, while LEFT JOIN returns all records from the left table and matched records from the right table.',
                keywords='inner, left, join, matching, records, left table, right table',
                max_marks=10
            ),
            Question(
                category_id=sql_cat.id,
                question_text='What is a Primary Key and how does it differ from a Unique Key?',
                sample_answer='A Primary Key uniquely identifies a record and cannot contain NULL values, whereas a Unique Key prevents duplicate values but can accept one NULL value.',
                keywords='primary key, unique key, null, duplicate, unique, record',
                max_marks=10
            ),

            # HR
            Question(
                category_id=hr_cat.id,
                question_text='Tell me about yourself and your professional goals.',
                sample_answer='I am a dedicated student passionate about technology and software development. My goal is to build a successful career by continuously learning and solving real-world problems.',
                keywords='passion, learning, goals, technology, development, dedicated, problem',
                max_marks=10
            ),
            Question(
                category_id=hr_cat.id,
                question_text='How do you handle pressure or tight deadlines?',
                sample_answer='I prioritize tasks, break down complex requirements into smaller milestones, maintain clear communication, and remain focused on delivery.',
                keywords='prioritize, focus, deadline, communication, milestone, pressure, task',
                max_marks=10
            )
        ]
        db.session.add_all(questions)
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

# --- Routes ---

@app.route('/')
def index():
    categories = Category.query.all()
    return render_template('index.html', categories=categories)

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

        flash('Registration successful! Please log in to start practicing.', 'success')
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
                flash('Invalid login credentials. Please try again.', 'danger')
                return redirect(url_for('login'))

    return render_template('login.html')

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
    categories = Category.query.all()
    attempts = InterviewAttempt.query.filter_by(student_id=student_id).order_by(InterviewAttempt.created_at.desc()).all()

    return render_template(
        'student_dashboard.html',
        student=student,
        categories=categories,
        attempts=attempts
    )

# Practice Interview: Start Session
@app.route('/student/interview/start/<int:category_id>')
@student_required
def start_interview(category_id):
    category = Category.query.get_or_404(category_id)
    questions = Question.query.filter_by(category_id=category_id).all()

    if not questions:
        flash(f'No interview questions available yet for category "{category.name}".', 'warning')
        return redirect(url_for('student_dashboard'))

    # Store interview state in session
    session['interview_category_id'] = category.id
    session['interview_category_name'] = category.name
    session['interview_q_ids'] = [q.id for q in questions]
    session['interview_index'] = 0
    session['interview_answers'] = {}

    return redirect(url_for('interview_question'))

# Practice Interview: Single Question Page
@app.route('/student/interview/question', methods=['GET', 'POST'])
@student_required
def interview_question():
    q_ids = session.get('interview_q_ids', [])
    index = session.get('interview_index', 0)
    category_id = session.get('interview_category_id')

    if not q_ids or index >= len(q_ids) or not category_id:
        flash('No active interview session found.', 'warning')
        return redirect(url_for('student_dashboard'))

    current_q_id = q_ids[index]
    question = db.session.get(Question, current_q_id)
    category = db.session.get(Category, category_id)

    if request.method == 'POST':
        user_answer = request.form.get('user_answer', '').strip()
        action = request.form.get('action', 'next')

        # Store user answer for current question
        answers_dict = session.get('interview_answers', {})
        answers_dict[str(current_q_id)] = user_answer
        session['interview_answers'] = answers_dict

        if action == 'prev' and index > 0:
            session['interview_index'] = index - 1
            return redirect(url_for('interview_question'))
        elif action == 'submit' or (action == 'next' and index == len(q_ids) - 1):
            return redirect(url_for('submit_interview'))
        else:
            session['interview_index'] = index + 1
            return redirect(url_for('interview_question'))

    # Retrieve existing answer if user navigated back/forth
    existing_answer = session.get('interview_answers', {}).get(str(current_q_id), '')

    return render_template(
        'interview_question.html',
        question=question,
        category=category,
        index=index + 1,
        total_questions=len(q_ids),
        existing_answer=existing_answer
    )

# Practice Interview: Final Submission & Evaluation
@app.route('/student/interview/submit', methods=['GET', 'POST'])
@student_required
def submit_interview():
    student_id = session.get('user_id')
    category_id = session.get('interview_category_id')
    q_ids = session.get('interview_q_ids', [])
    saved_answers = session.get('interview_answers', {})

    if not category_id or not q_ids:
        flash('Invalid or expired interview session.', 'warning')
        return redirect(url_for('student_dashboard'))

    questions = Question.query.filter(Question.id.in_(q_ids)).all()

    total_score = 0.0
    max_possible_score = 0.0
    answer_objects = []

    for q in questions:
        user_ans = saved_answers.get(str(q.id), '')
        score, feedback = evaluate_answer(
            user_answer=user_ans,
            sample_answer=q.sample_answer,
            keywords_str=q.keywords,
            max_marks=q.max_marks
        )
        total_score += score
        max_possible_score += q.max_marks

        answer_objects.append({
            'question_id': q.id,
            'user_answer': user_ans,
            'score': score,
            'max_marks': q.max_marks,
            'feedback': feedback
        })

    percentage = round((total_score / max_possible_score * 100), 1) if max_possible_score > 0 else 0.0

    # Generate overall attempt feedback
    if percentage >= 85:
        overall_feedback = "Outstanding performance! You have a solid grasp of key concepts in this category."
    elif percentage >= 65:
        overall_feedback = "Good attempt! You demonstrated good knowledge, but review sample answers for details."
    elif percentage >= 40:
        overall_feedback = "Fair attempt. Focus on practicing key terminology and sample answers."
    else:
        overall_feedback = "Needs improvement. Review course material and try this practice interview again."

    attempt = InterviewAttempt(
        student_id=student_id,
        category_id=category_id,
        total_score=total_score,
        max_possible_score=max_possible_score,
        percentage=percentage,
        feedback=overall_feedback
    )
    db.session.add(attempt)
    db.session.flush()  # Obtain attempt.id

    for ans_data in answer_objects:
        ans_record = InterviewAnswer(
            attempt_id=attempt.id,
            question_id=ans_data['question_id'],
            user_answer=ans_data['user_answer'],
            score=ans_data['score'],
            max_marks=ans_data['max_marks'],
            feedback=ans_data['feedback']
        )
        db.session.add(ans_record)

    db.session.commit()

    # Clear practice session variables
    session.pop('interview_category_id', None)
    session.pop('interview_category_name', None)
    session.pop('interview_q_ids', None)
    session.pop('interview_index', None)
    session.pop('interview_answers', None)

    flash('Mock interview completed! Here are your detailed results.', 'success')
    return redirect(url_for('view_interview_result', attempt_id=attempt.id))

# Interview Result Page
@app.route('/student/interview/result/<int:attempt_id>')
@student_required
def view_interview_result(attempt_id):
    attempt = InterviewAttempt.query.get_or_404(attempt_id)
    student_id = session.get('user_id')

    # Security check: Ensure student can only view their own attempts
    if attempt.student_id != student_id and session.get('user_type') != 'admin':
        flash('Unauthorized to view this interview result.', 'danger')
        return redirect(url_for('student_dashboard'))

    answers = InterviewAnswer.query.filter_by(attempt_id=attempt.id).all()

    return render_template(
        'interview_result.html',
        attempt=attempt,
        answers=answers
    )

# Admin Dashboard
@app.route('/admin/dashboard')
@admin_required
def admin_dashboard():
    categories = Category.query.all()
    questions = Question.query.order_by(Question.created_at.desc()).all()
    students = Student.query.order_by(Student.created_at.desc()).all()
    attempts = InterviewAttempt.query.order_by(InterviewAttempt.created_at.desc()).all()

    total_categories = len(categories)
    total_questions = len(questions)
    total_students = len(students)
    total_attempts = len(attempts)

    return render_template(
        'admin_dashboard.html',
        categories=categories,
        questions=questions,
        students=students,
        attempts=attempts,
        total_categories=total_categories,
        total_questions=total_questions,
        total_students=total_students,
        total_attempts=total_attempts
    )

# Admin: Add Category
@app.route('/admin/category/add', methods=['POST'])
@admin_required
def add_category():
    name = request.form.get('name', '').strip()
    description = request.form.get('description', '').strip()

    if not name:
        flash('Category name is required.', 'danger')
        return redirect(url_for('admin_dashboard'))

    if Category.query.filter_by(name=name).first():
        flash(f'Category "{name}" already exists.', 'warning')
        return redirect(url_for('admin_dashboard'))

    category = Category(name=name, description=description)
    db.session.add(category)
    db.session.commit()
    flash(f'Category "{name}" created successfully.', 'success')
    return redirect(url_for('admin_dashboard'))

# Admin: Delete Category
@app.route('/admin/category/delete/<int:category_id>', methods=['POST'])
@admin_required
def delete_category(category_id):
    category = Category.query.get_or_404(category_id)
    db.session.delete(category)
    db.session.commit()
    flash('Category deleted successfully.', 'info')
    return redirect(url_for('admin_dashboard'))

# Admin: Add Question
@app.route('/admin/question/add', methods=['POST'])
@admin_required
def add_question():
    category_id = request.form.get('category_id', type=int)
    question_text = request.form.get('question_text', '').strip()
    sample_answer = request.form.get('sample_answer', '').strip()
    keywords = request.form.get('keywords', '').strip()
    max_marks = request.form.get('max_marks', type=int, default=10)

    if not category_id or not question_text or not sample_answer or not keywords:
        flash('All question details are required.', 'danger')
        return redirect(url_for('admin_dashboard'))

    question = Question(
        category_id=category_id,
        question_text=question_text,
        sample_answer=sample_answer,
        keywords=keywords,
        max_marks=max_marks
    )
    db.session.add(question)
    db.session.commit()
    flash('Question added successfully.', 'success')
    return redirect(url_for('admin_dashboard'))

# Admin: Edit Question
@app.route('/admin/question/edit/<int:question_id>', methods=['POST'])
@admin_required
def edit_question(question_id):
    question = Question.query.get_or_404(question_id)

    category_id = request.form.get('category_id', type=int)
    question_text = request.form.get('question_text', '').strip()
    sample_answer = request.form.get('sample_answer', '').strip()
    keywords = request.form.get('keywords', '').strip()
    max_marks = request.form.get('max_marks', type=int)

    if category_id:
        question.category_id = category_id
    if question_text:
        question.question_text = question_text
    if sample_answer:
        question.sample_answer = sample_answer
    if keywords:
        question.keywords = keywords
    if max_marks and max_marks > 0:
        question.max_marks = max_marks

    db.session.commit()
    flash('Question updated successfully.', 'success')
    return redirect(url_for('admin_dashboard'))

# Admin: Delete Question
@app.route('/admin/question/delete/<int:question_id>', methods=['POST'])
@admin_required
def delete_question(question_id):
    question = Question.query.get_or_404(question_id)
    db.session.delete(question)
    db.session.commit()
    flash('Question deleted successfully.', 'info')
    return redirect(url_for('admin_dashboard'))

# Admin: View specific attempt result
@app.route('/admin/attempt/view/<int:attempt_id>')
@admin_required
def admin_view_attempt(attempt_id):
    attempt = InterviewAttempt.query.get_or_404(attempt_id)
    answers = InterviewAnswer.query.filter_by(attempt_id=attempt.id).all()
    return render_template('interview_result.html', attempt=attempt, answers=answers, is_admin_view=True)

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
        seed_default_data()
    app.run(debug=True)
