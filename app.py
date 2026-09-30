import os
from datetime import datetime, date, timezone
from flask import Flask, render_template, request, redirect, url_for, flash
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'college_admission_secret_key_mca_123')

# Database configuration: Default to MySQL URI, fallback/option for SQLite
MYSQL_URI = os.environ.get('DATABASE_URL', 'mysql+pymysql://root:@localhost/college_admission')
SQLITE_URI = 'sqlite:///' + os.path.join(os.path.abspath(os.path.dirname(__file__)), 'college_admission.db')

use_sqlite = os.environ.get('USE_SQLITE') == '1'
app.config['SQLALCHEMY_DATABASE_URI'] = SQLITE_URI if use_sqlite else MYSQL_URI
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

class Settings(db.Model):
    __tablename__ = 'settings'
    id = db.Column(db.Integer, primary_key=True, default=1)
    oc_seats = db.Column(db.Integer, nullable=False, default=9)
    bc_seats = db.Column(db.Integer, nullable=False, default=8)
    bcm_seats = db.Column(db.Integer, nullable=False, default=1)
    mbc_seats = db.Column(db.Integer, nullable=False, default=6)
    sc_seats = db.Column(db.Integer, nullable=False, default=5)
    sca_seats = db.Column(db.Integer, nullable=False, default=1)
    updated_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))

    @classmethod
    def get_settings(cls):
        settings = db.session.get(cls, 1)
        if not settings:
            settings = cls(id=1, oc_seats=9, bc_seats=8, bcm_seats=1, mbc_seats=6, sc_seats=5, sca_seats=1)
            db.session.add(settings)
            db.session.commit()
        return settings

class Student(db.Model):
    __tablename__ = 'students'
    id = db.Column(db.Integer, primary_key=True)
    application_no = db.Column(db.String(50), unique=True, nullable=False)
    name = db.Column(db.String(100), nullable=False)
    gender = db.Column(db.String(20), nullable=False)
    community = db.Column(db.String(20), nullable=False)
    marks = db.Column(db.Float, nullable=False)
    rank_no = db.Column(db.Integer, nullable=False)
    admission_date = db.Column(db.Date, nullable=True)
    status = db.Column(db.String(20), default='Waiting') # Waiting, Allocated, Admitted
    allocated_category = db.Column(db.String(20), nullable=True)
    remark = db.Column(db.Text, nullable=True)
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))

def recalculate_allocations():
    """
    Recalculates seat allocations for all students based on:
    1. Rank Number - ascending
    2. Marks - descending
    3. Community seat availability -> OC fallback -> Waiting
    """
    settings = Settings.get_settings()
    capacity = {
        'OC': settings.oc_seats,
        'BC': settings.bc_seats,
        'BCM': settings.bcm_seats,
        'MBC': settings.mbc_seats,
        'SC': settings.sc_seats,
        'SCA': settings.sca_seats
    }

    used = {cat: 0 for cat in capacity}

    # Order students by Rank No ASC, Marks DESC, ID ASC
    students = Student.query.order_by(Student.rank_no.asc(), Student.marks.desc(), Student.id.asc()).all()

    for student in students:
        comm = student.community.upper() if student.community else ''
        category_to_allocate = None

        # Check if student's community category has available seats
        if comm in capacity and used[comm] < capacity[comm]:
            category_to_allocate = comm
        # If community category is full or OC itself, try OC
        elif used['OC'] < capacity['OC']:
            category_to_allocate = 'OC'

        if category_to_allocate:
            used[category_to_allocate] += 1
            student.allocated_category = category_to_allocate
            if student.status != 'Admitted':
                student.status = 'Allocated'
        else:
            student.allocated_category = None
            student.status = 'Waiting'
            student.admission_date = None

    db.session.commit()

def get_category_stats(gender_filter=None):
    """
    Generates category-wise allocation, admission, and vacancy stats.
    """
    settings = Settings.get_settings()
    categories = ['OC', 'BC', 'BCM', 'MBC', 'SC', 'SCA']
    capacity_map = {
        'OC': settings.oc_seats,
        'BC': settings.bc_seats,
        'BCM': settings.bcm_seats,
        'MBC': settings.mbc_seats,
        'SC': settings.sc_seats,
        'SCA': settings.sca_seats
    }

    stats = []
    all_students = Student.query.all()

    for cat in categories:
        if gender_filter:
            cat_students = [s for s in all_students if s.allocated_category == cat and s.gender.lower() == gender_filter.lower()]
            allocated = len(cat_students)
            admitted = len([s for s in cat_students if s.status == 'Admitted'])
            vacancy = max(0, allocated - admitted)
            total_seats = allocated
        else:
            cat_students = [s for s in all_students if s.allocated_category == cat]
            total_seats = capacity_map[cat]
            allocated = len(cat_students)
            admitted = len([s for s in cat_students if s.status == 'Admitted'])
            vacancy = max(0, total_seats - admitted)

        stats.append({
            'category': cat,
            'total_seats': total_seats,
            'allocated': allocated,
            'admitted': admitted,
            'vacancy': vacancy
        })

    return stats

@app.route('/')
def dashboard():
    recalculate_allocations()
    settings = Settings.get_settings()
    students = Student.query.all()

    total_seats = (settings.oc_seats + settings.bc_seats + settings.bcm_seats +
                   settings.mbc_seats + settings.sc_seats + settings.sca_seats)
    total_students = len(students)
    total_allocated = len([s for s in students if s.status in ['Allocated', 'Admitted']])
    total_admitted = len([s for s in students if s.status == 'Admitted'])
    total_waiting = len([s for s in students if s.status == 'Waiting'])
    total_vacancy = max(0, total_seats - total_admitted)

    total_boys = len([s for s in students if s.gender.lower() == 'male'])
    total_girls = len([s for s in students if s.gender.lower() == 'female'])

    cat_stats = get_category_stats()

    # Boys and Girls category-wise stats
    boys_stats = get_category_stats(gender_filter='male')
    girls_stats = get_category_stats(gender_filter='female')

    return render_template('dashboard.html',
                           total_students=total_students,
                           total_allocated=total_allocated,
                           total_admitted=total_admitted,
                           total_waiting=total_waiting,
                           total_vacancy=total_vacancy,
                           total_boys=total_boys,
                           total_girls=total_girls,
                           cat_stats=cat_stats,
                           boys_stats=boys_stats,
                           girls_stats=girls_stats,
                           datetime=datetime)

@app.route('/students')
def view_students():
    recalculate_allocations()
    query = Student.query

    search = request.args.get('search', '').strip()
    category = request.args.get('category', '').strip()
    gender = request.args.get('gender', '').strip()
    status = request.args.get('status', '').strip()

    if search:
        query = query.filter(
            (Student.name.ilike(f'%{search}%')) |
            (Student.application_no.ilike(f'%{search}%'))
        )
    if category:
        query = query.filter(Student.community == category)
    if gender:
        query = query.filter(Student.gender == gender)
    if status:
        query = query.filter(Student.status == status)

    students = query.order_by(Student.rank_no.asc(), Student.marks.desc()).all()

    return render_template('students.html',
                           students=students,
                           search=search,
                           selected_category=category,
                           selected_gender=gender,
                           selected_status=status,
                           datetime=datetime)

@app.route('/students/add', methods=['GET', 'POST'])
def add_student():
    if request.method == 'POST':
        application_no = request.form.get('application_no', '').strip()
        name = request.form.get('name', '').strip()
        gender = request.form.get('gender', '').strip()
        community = request.form.get('community', '').strip()
        marks_raw = request.form.get('marks', '').strip()
        rank_no_raw = request.form.get('rank_no', '').strip()
        remark = request.form.get('remark', '').strip()

        if not application_no or not name or not gender or not community or not marks_raw or not rank_no_raw:
            flash('All required fields must be filled out.', 'danger')
            return redirect(url_for('add_student'))

        try:
            marks = float(marks_raw)
            rank_no = int(rank_no_raw)
        except ValueError:
            flash('Marks must be a number and Rank must be an integer.', 'danger')
            return redirect(url_for('add_student'))

        existing_app = Student.query.filter_by(application_no=application_no).first()
        if existing_app:
            flash(f'Student with Application No "{application_no}" already exists.', 'danger')
            return redirect(url_for('add_student'))

        student = Student(
            application_no=application_no,
            name=name,
            gender=gender,
            community=community,
            marks=marks,
            rank_no=rank_no,
            remark=remark
        )
        db.session.add(student)
        db.session.commit()

        recalculate_allocations()
        flash(f'Student "{name}" added successfully.', 'success')
        return redirect(url_for('view_students'))

    return render_template('add_student.html', datetime=datetime)

@app.route('/students/edit/<int:id>', methods=['GET', 'POST'])
def edit_student(id):
    student = db.session.get(Student, id)
    if not student:
        flash('Student not found.', 'danger')
        return redirect(url_for('view_students'))

    if request.method == 'POST':
        application_no = request.form.get('application_no', '').strip()
        name = request.form.get('name', '').strip()
        gender = request.form.get('gender', '').strip()
        community = request.form.get('community', '').strip()
        marks_raw = request.form.get('marks', '').strip()
        rank_no_raw = request.form.get('rank_no', '').strip()
        remark = request.form.get('remark', '').strip()

        if not application_no or not name or not gender or not community or not marks_raw or not rank_no_raw:
            flash('All required fields must be filled out.', 'danger')
            return redirect(url_for('edit_student', id=id))

        try:
            marks = float(marks_raw)
            rank_no = int(rank_no_raw)
        except ValueError:
            flash('Marks must be a number and Rank must be an integer.', 'danger')
            return redirect(url_for('edit_student', id=id))

        existing_app = Student.query.filter(Student.application_no == application_no, Student.id != id).first()
        if existing_app:
            flash(f'Another student with Application No "{application_no}" already exists.', 'danger')
            return redirect(url_for('edit_student', id=id))

        student.application_no = application_no
        student.name = name
        student.gender = gender
        student.community = community
        student.marks = marks
        student.rank_no = rank_no
        student.remark = remark

        db.session.commit()
        recalculate_allocations()

        flash(f'Student "{name}" updated successfully.', 'success')
        return redirect(url_for('view_students'))

    return render_template('edit_student.html', student=student, datetime=datetime)

@app.route('/students/delete/<int:id>', methods=['POST'])
def delete_student(id):
    student = db.session.get(Student, id)
    if not student:
        flash('Student not found.', 'danger')
        return redirect(url_for('view_students'))

    name = student.name
    db.session.delete(student)
    db.session.commit()

    recalculate_allocations()
    flash(f'Student "{name}" deleted successfully.', 'success')
    return redirect(url_for('view_students'))

@app.route('/admission')
def view_admission():
    recalculate_allocations()
    cat_stats = get_category_stats()
    allocated_students = Student.query.filter(Student.status.in_(['Allocated', 'Admitted'])).order_by(Student.rank_no.asc()).all()

    return render_template('admission.html',
                           cat_stats=cat_stats,
                           allocated_students=allocated_students,
                           datetime=datetime)

@app.route('/admission/admit/<int:id>', methods=['POST'])
def admit_student(id):
    student = db.session.get(Student, id)
    if not student:
        flash('Student not found.', 'danger')
        return redirect(url_for('view_admission'))

    if student.allocated_category:
        student.status = 'Admitted'
        student.admission_date = date.today()
        db.session.commit()
        flash(f'Student "{student.name}" admitted successfully!', 'success')
    else:
        flash(f'Cannot admit student "{student.name}" - No seat allocated.', 'danger')

    return redirect(url_for('view_admission'))

@app.route('/settings', methods=['GET', 'POST'])
def view_settings():
    settings = Settings.get_settings()

    if request.method == 'POST':
        try:
            settings.oc_seats = int(request.form.get('oc_seats', 0))
            settings.bc_seats = int(request.form.get('bc_seats', 0))
            settings.bcm_seats = int(request.form.get('bcm_seats', 0))
            settings.mbc_seats = int(request.form.get('mbc_seats', 0))
            settings.sc_seats = int(request.form.get('sc_seats', 0))
            settings.sca_seats = int(request.form.get('sca_seats', 0))

            db.session.commit()
            recalculate_allocations()
            flash('Seat reservation settings updated successfully and allocations recalculated.', 'success')
            return redirect(url_for('view_settings'))
        except ValueError:
            flash('Invalid seat count input. All fields must be integers.', 'danger')
            return redirect(url_for('view_settings'))

    return render_template('settings.html', settings=settings, datetime=datetime)

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
        Settings.get_settings()
        recalculate_allocations()
    app.run(debug=True)
