import os
import io
import csv
from datetime import datetime, date, timedelta
from functools import wraps
from flask import Flask, render_template, request, redirect, url_for, flash, session, jsonify, send_file, Response
from database import (
    db, User, Teacher, CollegeClass, ClassTutor, Subject, TeacherSubject,
    Student, Timetable, AttendanceSession, AttendanceRecord, Notification,
    TheoryInternalMark, PracticalInternalMark, ExamConfig,
    calculate_attendance_mark, init_db
)

app = Flask(__name__)
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'smart_classroom_attendance_secret_key_98765')

db_path = os.path.join(os.path.abspath(os.path.dirname(__file__)), 'college_attendance.db')
app.config['SQLALCHEMY_DATABASE_URI'] = f'sqlite:///{db_path}'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db.init_app(app)

# Helper Decorators
def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            flash('Please log in to access this page.', 'warning')
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function

def teacher_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session or session.get('role') not in ['teacher', 'both']:
            flash('Teacher access required.', 'danger')
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function

def tutor_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session or session.get('role') not in ['tutor', 'both']:
            flash('Class Tutor access required.', 'danger')
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function

def get_current_user():
    if 'user_id' in session:
        return db.session.get(User, session['user_id'])
    return None

def get_current_teacher():
    user = get_current_user()
    if user and user.teacher:
        return user.teacher
    return None

def get_tutor_assigned_class(teacher_id):
    assignment = ClassTutor.query.filter_by(teacher_id=teacher_id).first()
    if assignment:
        return db.session.get(CollegeClass, assignment.class_id)
    return None

@app.context_processor
def inject_user_context():
    user = get_current_user()
    teacher = get_current_teacher()
    tutor_class = get_tutor_assigned_class(teacher.id) if teacher else None

    unread_notifications_count = 0
    if tutor_class:
        ct_assignment = ClassTutor.query.filter_by(class_id=tutor_class.id).first()
        if ct_assignment:
            unread_notifications_count = Notification.query.filter_by(
                tutor_id=ct_assignment.id, is_read=False
            ).count()

    return dict(
        current_user=user,
        current_teacher=teacher,
        tutor_class=tutor_class,
        unread_notifications_count=unread_notifications_count
    )

# Authentication Routes
@app.route('/')
def index():
    if 'user_id' in session:
        if session.get('role') == 'tutor':
            return redirect(url_for('tutor_dashboard'))
        return redirect(url_for('teacher_dashboard'))
    return redirect(url_for('login'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username', '').strip()
        password = request.form.get('password', '')

        if not username or not password:
            flash('Please fill in both username and password.', 'danger')
            return render_template('login.html')

        user = User.query.filter_by(username=username).first()

        if user and user.check_password(password):
            session['user_id'] = user.id
            session['user_name'] = user.name
            session['username'] = user.username
            session['role'] = user.role

            teacher = Teacher.query.filter_by(user_id=user.id).first()
            if teacher:
                session['teacher_id'] = teacher.id

            flash(f'Welcome, {user.name}!', 'success')
            if user.role == 'tutor':
                return redirect(url_for('tutor_dashboard'))
            return redirect(url_for('teacher_dashboard'))

        flash('Invalid username or password.', 'danger')

    return render_template('login.html')

@app.route('/logout')
def logout():
    session.clear()
    flash('You have been logged out successfully.', 'info')
    return redirect(url_for('login'))

# Teacher Dashboard
@app.route('/teacher/dashboard')
@teacher_required
def teacher_dashboard():
    teacher = get_current_teacher()
    if not teacher:
        flash('Teacher profile not found.', 'danger')
        return redirect(url_for('login'))

    ts_list = TeacherSubject.query.filter_by(teacher_id=teacher.id).all()
    assigned_subject_ids = [ts.subject_id for ts in ts_list]
    assigned_subjects = Subject.query.filter(Subject.id.in_(assigned_subject_ids)).all() if assigned_subject_ids else []

    timetable_entries = Timetable.query.filter_by(teacher_id=teacher.id).order_by(Timetable.day, Timetable.period).all()

    recent_sessions = AttendanceSession.query.filter_by(teacher_id=teacher.id)\
        .order_by(AttendanceSession.date.desc(), AttendanceSession.created_at.desc()).limit(10).all()

    total_sessions_taken = AttendanceSession.query.filter_by(teacher_id=teacher.id).count()

    return render_template(
        'teacher_dashboard.html',
        teacher=teacher,
        assigned_subjects=assigned_subjects,
        timetable_entries=timetable_entries,
        recent_sessions=recent_sessions,
        total_sessions_taken=total_sessions_taken
    )

# Tutor Dashboard
@app.route('/tutor/dashboard')
@tutor_required
def tutor_dashboard():
    teacher = get_current_teacher()
    tutor_class = get_tutor_assigned_class(teacher.id)

    if not tutor_class:
        flash('You are not currently assigned as a Class Tutor for any class.', 'warning')
        return redirect(url_for('teacher_dashboard'))

    students = Student.query.filter_by(class_id=tutor_class.id, status='Active').all()
    total_students = len(students)

    class_sessions = AttendanceSession.query.filter_by(class_id=tutor_class.id)\
        .order_by(AttendanceSession.date.desc(), AttendanceSession.created_at.desc()).all()

    total_present_sum = sum(s.present_students for s in class_sessions)
    total_records_sum = sum(s.total_students for s in class_sessions)
    overall_percentage = round((total_present_sum / total_records_sum * 100), 2) if total_records_sum > 0 else 0.0

    ra_student_count = 0
    below_threshold_students = []

    for student in students:
        total_st_records = AttendanceRecord.query.join(AttendanceSession)\
            .filter(AttendanceSession.class_id == tutor_class.id, AttendanceRecord.student_id == student.id).all()
        st_total = len(total_st_records)
        st_present = len([r for r in total_st_records if r.status == 'Present'])
        st_perc = round((st_present / st_total * 100), 2) if st_total > 0 else 100.0

        if st_perc < 50.0:
            ra_student_count += 1
            below_threshold_students.append({'student': student, 'percentage': st_perc, 'present': st_present, 'total': st_total})

    ct_assignment = ClassTutor.query.filter_by(class_id=tutor_class.id).first()
    notifications = Notification.query.filter_by(tutor_id=ct_assignment.id)\
        .order_by(Notification.created_at.desc()).limit(10).all() if ct_assignment else []

    return render_template(
        'tutor_dashboard.html',
        tutor_class=tutor_class,
        total_students=total_students,
        total_sessions=len(class_sessions),
        overall_percentage=overall_percentage,
        ra_student_count=ra_student_count,
        below_threshold_students=below_threshold_students,
        class_sessions=class_sessions,
        notifications=notifications
    )

# Student Management
@app.route('/students', methods=['GET', 'POST'])
@login_required
def students_management():
    all_classes = CollegeClass.query.all()
    selected_class_id = request.args.get('class_id', type=int)
    search_query = request.args.get('search', '').strip()

    if request.method == 'POST':
        action = request.form.get('action')

        if action == 'add':
            reg_num = request.form.get('register_number', '').strip()
            name = request.form.get('name', '').strip()
            class_id = request.form.get('class_id', type=int)

            if not reg_num or not name or not class_id:
                flash('All fields are required.', 'danger')
                return redirect(url_for('students_management', class_id=class_id))

            c_obj = db.session.get(CollegeClass, class_id)
            if not c_obj:
                flash('Selected class does not exist.', 'danger')
                return redirect(url_for('students_management'))

            existing = Student.query.filter_by(class_id=class_id, register_number=reg_num).first()
            if existing:
                flash(f'Student with Register Number {reg_num} already exists in {c_obj.name}.', 'danger')
                return redirect(url_for('students_management', class_id=class_id))

            student = Student(
                register_number=reg_num,
                name=name,
                class_id=class_id,
                department=c_obj.department,
                academic_year=c_obj.academic_year,
                semester=c_obj.semester,
                status='Active'
            )
            db.session.add(student)
            db.session.commit()
            flash(f'Student {name} ({reg_num}) added successfully.', 'success')
            return redirect(url_for('students_management', class_id=class_id))

        elif action == 'edit':
            student_id = request.form.get('student_id', type=int)
            student = db.session.get(Student, student_id)
            if not student:
                flash('Student not found.', 'danger')
                return redirect(url_for('students_management'))

            reg_num = request.form.get('register_number', '').strip()
            name = request.form.get('name', '').strip()
            class_id = request.form.get('class_id', type=int)
            status = request.form.get('status', 'Active')

            existing = Student.query.filter(
                Student.class_id == class_id,
                Student.register_number == reg_num,
                Student.id != student_id
            ).first()
            if existing:
                flash(f'Register number {reg_num} already assigned to another student in this class.', 'danger')
                return redirect(url_for('students_management', class_id=class_id))

            c_obj = db.session.get(CollegeClass, class_id)
            student.register_number = reg_num
            student.name = name
            student.class_id = class_id
            student.department = c_obj.department
            student.academic_year = c_obj.academic_year
            student.semester = c_obj.semester
            student.status = status

            db.session.commit()
            flash('Student updated successfully.', 'success')
            return redirect(url_for('students_management', class_id=class_id))

        elif action == 'import_csv':
            class_id = request.form.get('class_id', type=int)
            file = request.files.get('csv_file')
            if not file or not class_id:
                flash('Please select a class and CSV file.', 'danger')
                return redirect(url_for('students_management'))

            c_obj = db.session.get(CollegeClass, class_id)
            stream = io.StringIO(file.stream.read().decode("UTF-8"), newline=None)
            csv_input = csv.reader(stream)
            header = next(csv_input, None)

            imported_count = 0
            for row in csv_input:
                if len(row) >= 2:
                    reg_num = row[0].strip()
                    name = row[1].strip()
                    if reg_num and name:
                        existing = Student.query.filter_by(class_id=class_id, register_number=reg_num).first()
                        if not existing:
                            s = Student(
                                register_number=reg_num,
                                name=name,
                                class_id=class_id,
                                department=c_obj.department,
                                academic_year=c_obj.academic_year,
                                semester=c_obj.semester,
                                status='Active'
                            )
                            db.session.add(s)
                            imported_count += 1
            db.session.commit()
            flash(f'Successfully imported {imported_count} students into {c_obj.name}.', 'success')
            return redirect(url_for('students_management', class_id=class_id))

    query = Student.query
    if selected_class_id:
        query = query.filter_by(class_id=selected_class_id)
    if search_query:
        query = query.filter(
            (Student.name.ilike(f'%{search_query}%')) |
            (Student.register_number.ilike(f'%{search_query}%'))
        )

    students = query.order_by(Student.register_number).all()

    return render_template(
        'students.html',
        students=students,
        classes=all_classes,
        selected_class_id=selected_class_id,
        search_query=search_query
    )

# Subject Management
@app.route('/subjects', methods=['GET', 'POST'])
@login_required
def subjects_management():
    all_classes = CollegeClass.query.all()
    selected_class_id = request.args.get('class_id', type=int)

    if request.method == 'POST':
        action = request.form.get('action')

        if action == 'add':
            code = request.form.get('code', '').strip().upper()
            name = request.form.get('name', '').strip()
            class_id = request.form.get('class_id', type=int)
            sub_type = request.form.get('type', 'Theory')
            credits = request.form.get('credits', type=int, default=3)

            if not code or not name or not class_id:
                flash('Subject code, name, and class are required.', 'danger')
                return redirect(url_for('subjects_management', class_id=class_id))

            existing = Subject.query.filter_by(class_id=class_id, code=code).first()
            if existing:
                flash(f'Subject code {code} already exists for this class.', 'danger')
                return redirect(url_for('subjects_management', class_id=class_id))

            subj = Subject(class_id=class_id, code=code, name=name, type=sub_type, credits=credits)
            db.session.add(subj)
            db.session.commit()
            flash(f'Subject "{name}" ({code}) added.', 'success')
            return redirect(url_for('subjects_management', class_id=class_id))

        elif action == 'edit':
            subject_id = request.form.get('subject_id', type=int)
            subj = db.session.get(Subject, subject_id)
            if subj:
                subj.code = request.form.get('code', '').strip().upper()
                subj.name = request.form.get('name', '').strip()
                subj.type = request.form.get('type', 'Theory')
                subj.credits = request.form.get('credits', type=int, default=3)
                db.session.commit()
                flash('Subject updated successfully.', 'success')
                return redirect(url_for('subjects_management', class_id=subj.class_id))

    query = Subject.query
    if selected_class_id:
        query = query.filter_by(class_id=selected_class_id)

    subjects = query.order_by(Subject.class_id, Subject.code).all()

    return render_template(
        'subjects.html',
        subjects=subjects,
        classes=all_classes,
        selected_class_id=selected_class_id
    )

# Teacher & Tutor Assignments
@app.route('/assignments', methods=['GET', 'POST'])
@login_required
def assignments_management():
    all_classes = CollegeClass.query.all()
    all_teachers = Teacher.query.all()
    all_subjects = Subject.query.order_by(Subject.class_id, Subject.code).all()

    if request.method == 'POST':
        action = request.form.get('action')

        if action == 'assign_tutor':
            class_id = request.form.get('class_id', type=int)
            teacher_id = request.form.get('teacher_id', type=int)

            if not class_id or not teacher_id:
                flash('Class and Teacher are required.', 'danger')
                return redirect(url_for('assignments_management'))

            existing_tutor = ClassTutor.query.filter_by(class_id=class_id).first()
            if existing_tutor:
                existing_tutor.teacher_id = teacher_id
            else:
                ct = ClassTutor(class_id=class_id, teacher_id=teacher_id)
                db.session.add(ct)

            teacher = db.session.get(Teacher, teacher_id)
            if teacher and teacher.user and teacher.user.role == 'teacher':
                teacher.user.role = 'both'

            db.session.commit()
            flash('Class Tutor assigned successfully.', 'success')
            return redirect(url_for('assignments_management'))

        elif action == 'assign_teacher_subject':
            teacher_id = request.form.get('teacher_id', type=int)
            subject_id = request.form.get('subject_id', type=int)

            if not teacher_id or not subject_id:
                flash('Teacher and Subject selection required.', 'danger')
                return redirect(url_for('assignments_management'))

            subj = db.session.get(Subject, subject_id)
            if subj:
                existing = TeacherSubject.query.filter_by(
                    teacher_id=teacher_id, subject_id=subject_id, class_id=subj.class_id
                ).first()
                if not existing:
                    ts = TeacherSubject(teacher_id=teacher_id, subject_id=subject_id, class_id=subj.class_id)
                    db.session.add(ts)
                    db.session.commit()
                    flash('Teacher assigned to subject successfully.', 'success')
                else:
                    flash('Teacher is already assigned to this subject.', 'info')

            return redirect(url_for('assignments_management'))

    tutor_assignments = ClassTutor.query.all()
    teacher_subjects = TeacherSubject.query.all()

    return render_template(
        'assignments.html',
        classes=all_classes,
        teachers=all_teachers,
        subjects=all_subjects,
        tutor_assignments=tutor_assignments,
        teacher_subjects=teacher_subjects
    )

# Timetable Management
@app.route('/timetable', methods=['GET', 'POST'])
@login_required
def timetable_management():
    all_classes = CollegeClass.query.all()
    selected_class_id = request.args.get('class_id', type=int, default=all_classes[0].id if all_classes else None)

    selected_class = db.session.get(CollegeClass, selected_class_id) if selected_class_id else None
    class_subjects = Subject.query.filter_by(class_id=selected_class_id).all() if selected_class_id else []
    all_teachers = Teacher.query.all()

    if request.method == 'POST':
        action = request.form.get('action')

        if action == 'add_entry':
            class_id = request.form.get('class_id', type=int)
            day = request.form.get('day')
            period = request.form.get('period', type=int)
            subject_id = request.form.get('subject_id', type=int)
            teacher_id = request.form.get('teacher_id', type=int)
            start_time = request.form.get('start_time')
            end_time = request.form.get('end_time')

            if not all([class_id, day, period, subject_id, teacher_id, start_time, end_time]):
                flash('All timetable fields are required.', 'danger')
                return redirect(url_for('timetable_management', class_id=class_id))

            subj = db.session.get(Subject, subject_id)
            if not subj or subj.class_id != class_id:
                flash('Invalid subject selection for this class.', 'danger')
                return redirect(url_for('timetable_management', class_id=class_id))

            existing_class_slot = Timetable.query.filter_by(
                class_id=class_id, day=day, period=period
            ).first()
            if existing_class_slot:
                flash(f'Period {period} on {day} is already scheduled for this class.', 'danger')
                return redirect(url_for('timetable_management', class_id=class_id))

            existing_teacher_slot = Timetable.query.filter_by(
                teacher_id=teacher_id, day=day, period=period
            ).first()
            if existing_teacher_slot:
                t_obj = db.session.get(Teacher, teacher_id)
                c_conflict = db.session.get(CollegeClass, existing_teacher_slot.class_id)
                flash(f'Teacher {t_obj.name} is already teaching {c_conflict.name} during {day} Period {period}.', 'danger')
                return redirect(url_for('timetable_management', class_id=class_id))

            tt_entry = Timetable(
                class_id=class_id,
                day=day,
                period=period,
                subject_id=subject_id,
                teacher_id=teacher_id,
                start_time=start_time,
                end_time=end_time,
                type=subj.type
            )
            db.session.add(tt_entry)
            db.session.commit()
            flash('Timetable slot added successfully.', 'success')
            return redirect(url_for('timetable_management', class_id=class_id))

        elif action == 'delete_entry':
            entry_id = request.form.get('entry_id', type=int)
            tt_entry = db.session.get(Timetable, entry_id)
            if tt_entry:
                c_id = tt_entry.class_id
                db.session.delete(tt_entry)
                db.session.commit()
                flash('Timetable entry deleted.', 'info')
                return redirect(url_for('timetable_management', class_id=c_id))

    days = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday']
    periods = [1, 2, 3, 4, 5]

    timetable_entries = Timetable.query.filter_by(class_id=selected_class_id).all() if selected_class_id else []

    grid = {day: {p: None for p in periods} for day in days}
    for entry in timetable_entries:
        if entry.day in grid and entry.period in grid[entry.day]:
            grid[entry.day][entry.period] = entry

    return render_template(
        'timetable.html',
        classes=all_classes,
        selected_class=selected_class,
        selected_class_id=selected_class_id,
        class_subjects=class_subjects,
        teachers=all_teachers,
        days=days,
        periods=periods,
        grid=grid
    )

# Attendance Marking Sheet Route
@app.route('/attendance', methods=['GET', 'POST'])
@teacher_required
def attendance_marking():
    teacher = get_current_teacher()
    all_classes = CollegeClass.query.all()

    class_id = request.args.get('class_id', type=int)
    subject_id = request.args.get('subject_id', type=int)
    att_date_str = request.args.get('date', date.today().isoformat())
    period = request.args.get('period', type=int, default=1)

    try:
        att_date = datetime.strptime(att_date_str, '%Y-%m-%d').date()
    except ValueError:
        att_date = date.today()
        att_date_str = att_date.isoformat()

    selected_class = db.session.get(CollegeClass, class_id) if class_id else None
    selected_subject = db.session.get(Subject, subject_id) if subject_id else None

    ts_list = TeacherSubject.query.filter_by(teacher_id=teacher.id).all()
    assigned_subject_ids = [ts.subject_id for ts in ts_list]

    if class_id:
        available_subjects = Subject.query.filter(
            Subject.class_id == class_id,
            Subject.id.in_(assigned_subject_ids)
        ).all()
    else:
        available_subjects = Subject.query.filter(Subject.id.in_(assigned_subject_ids)).all() if assigned_subject_ids else []

    students = []
    existing_session = None
    saved_status_map = {}

    if selected_class and selected_subject:
        students = Student.query.filter_by(class_id=selected_class.id, status='Active').order_by(Student.register_number).all()

        existing_session = AttendanceSession.query.filter_by(
            class_id=selected_class.id,
            subject_id=selected_subject.id,
            date=att_date,
            period=period
        ).first()

        if existing_session:
            records = AttendanceRecord.query.filter_by(session_id=existing_session.id).all()
            for r in records:
                saved_status_map[r.student_id] = r.status

    if request.method == 'POST':
        post_class_id = request.form.get('class_id', type=int)
        post_subject_id = request.form.get('subject_id', type=int)
        post_date_str = request.form.get('date')
        post_period = request.form.get('period', type=int)

        try:
            post_date = datetime.strptime(post_date_str, '%Y-%m-%d').date()
        except Exception:
            post_date = date.today()

        post_class = db.session.get(CollegeClass, post_class_id)
        post_subject = db.session.get(Subject, post_subject_id)

        if not post_class or not post_subject:
            flash('Invalid class or subject.', 'danger')
            return redirect(url_for('attendance_marking'))

        class_students = Student.query.filter_by(class_id=post_class.id, status='Active').all()
        total_st_count = len(class_students)

        present_count = 0
        absent_count = 0
        student_status_inputs = {}

        for student in class_students:
            status_val = request.form.get(f'status_{student.id}', 'Absent')
            if status_val not in ['Present', 'Absent']:
                status_val = 'Absent'
            student_status_inputs[student.id] = status_val
            if status_val == 'Present':
                present_count += 1
            else:
                absent_count += 1

        attendance_pct = round((present_count / total_st_count * 100), 2) if total_st_count > 0 else 0.0

        try:
            session_obj = AttendanceSession.query.filter_by(
                class_id=post_class.id,
                subject_id=post_subject.id,
                date=post_date,
                period=post_period
            ).first()

            if not session_obj:
                session_obj = AttendanceSession(
                    class_id=post_class.id,
                    subject_id=post_subject.id,
                    teacher_id=teacher.id,
                    date=post_date,
                    period=post_period,
                    type=post_subject.type,
                    total_students=total_st_count,
                    present_students=present_count,
                    absent_students=absent_count,
                    attendance_percentage=attendance_pct
                )
                db.session.add(session_obj)
                db.session.flush()
            else:
                session_obj.teacher_id = teacher.id
                session_obj.total_students = total_st_count
                session_obj.present_students = present_count
                session_obj.absent_students = absent_count
                session_obj.attendance_percentage = attendance_pct
                session_obj.updated_at = datetime.utcnow()

            for student_id, st_status in student_status_inputs.items():
                record = AttendanceRecord.query.filter_by(
                    session_id=session_obj.id,
                    student_id=student_id
                ).first()

                if not record:
                    record = AttendanceRecord(
                        session_id=session_obj.id,
                        student_id=student_id,
                        status=st_status
                    )
                    db.session.add(record)
                else:
                    record.status = st_status

            ct_assignment = ClassTutor.query.filter_by(class_id=post_class.id).first()
            if ct_assignment:
                notif = Notification(
                    tutor_id=ct_assignment.id,
                    session_id=session_obj.id,
                    title=f"Attendance Submitted: {post_class.name} - {post_subject.name}",
                    message=f"Teacher {teacher.name} submitted attendance for {post_subject.name} ({post_subject.type}) on {post_date.strftime('%Y-%m-%d')} (Period {post_period}). Present: {present_count}/{total_st_count} ({attendance_pct}%).",
                    is_read=False
                )
                db.session.add(notif)

            db.session.commit()
            flash('Attendance saved successfully! Automated report notification sent to Class Tutor.', 'success')
            return redirect(url_for('view_attendance_report', session_id=session_obj.id))

        except Exception as e:
            db.session.rollback()
            flash(f'Failed to save attendance: {str(e)}', 'danger')
            return redirect(url_for('attendance_marking', class_id=post_class_id, subject_id=post_subject_id, date=post_date_str, period=post_period))

    return render_template(
        'attendance.html',
        classes=all_classes,
        available_subjects=available_subjects,
        selected_class=selected_class,
        selected_subject=selected_subject,
        selected_class_id=class_id,
        selected_subject_id=subject_id,
        att_date=att_date_str,
        period=period,
        students=students,
        existing_session=existing_session,
        saved_status_map=saved_status_map
    )

# View Attendance Session Report
@app.route('/attendance/report/<int:session_id>')
@login_required
def view_attendance_report(session_id):
    session_obj = db.session.get(AttendanceSession, session_id)
    if not session_obj:
        flash('Attendance report not found.', 'danger')
        return redirect(url_for('teacher_dashboard'))

    teacher = get_current_teacher()

    is_session_teacher = (teacher and session_obj.teacher_id == teacher.id)
    tutor_class = get_tutor_assigned_class(teacher.id) if teacher else None
    is_session_tutor = (tutor_class and tutor_class.id == session_obj.class_id)

    if not is_session_teacher and not is_session_tutor:
        flash('Access denied. You can only view reports for your assigned class or subjects.', 'danger')
        return redirect(url_for('teacher_dashboard'))

    records = AttendanceRecord.query.filter_by(session_id=session_id).join(Student).order_by(Student.register_number).all()

    return render_template(
        'attendance_report.html',
        session_obj=session_obj,
        records=records
    )

# Notifications list & Mark as read API
@app.route('/notifications')
@tutor_required
def notifications_page():
    teacher = get_current_teacher()
    tutor_class = get_tutor_assigned_class(teacher.id)
    if not tutor_class:
        flash('No class assigned.', 'warning')
        return redirect(url_for('teacher_dashboard'))

    ct_assignment = ClassTutor.query.filter_by(class_id=tutor_class.id).first()
    notifications = Notification.query.filter_by(tutor_id=ct_assignment.id).order_by(Notification.created_at.desc()).all() if ct_assignment else []

    return render_template('notifications.html', notifications=notifications, tutor_class=tutor_class)

@app.route('/notifications/mark_read/<int:notification_id>', methods=['POST'])
@tutor_required
def mark_notification_read(notification_id):
    notif = db.session.get(Notification, notification_id)
    if notif:
        notif.is_read = True
        db.session.commit()
    return jsonify({'status': 'success'})

@app.route('/api/notifications')
@tutor_required
def api_notifications():
    teacher = get_current_teacher()
    tutor_class = get_tutor_assigned_class(teacher.id)
    if not tutor_class:
        return jsonify([])

    ct_assignment = ClassTutor.query.filter_by(class_id=tutor_class.id).first()
    if not ct_assignment:
        return jsonify([])

    unread = Notification.query.filter_by(tutor_id=ct_assignment.id, is_read=False).order_by(Notification.created_at.desc()).all()

    data = [{
        'id': n.id,
        'title': n.title,
        'message': n.message,
        'created_at': n.created_at.strftime('%Y-%m-%d %H:%M:%S'),
        'session_id': n.session_id
    } for n in unread]

    return jsonify(data)

# Theory Internal Marks
@app.route('/marks/theory', methods=['GET', 'POST'])
@teacher_required
def theory_marks():
    teacher = get_current_teacher()
    all_classes = CollegeClass.query.all()

    class_id = request.args.get('class_id', type=int)
    subject_id = request.args.get('subject_id', type=int)

    ts_list = TeacherSubject.query.filter_by(teacher_id=teacher.id).all()
    assigned_subject_ids = [ts.subject_id for ts in ts_list]

    if class_id:
        theory_subjects = Subject.query.filter(
            Subject.class_id == class_id,
            Subject.type == 'Theory',
            Subject.id.in_(assigned_subject_ids)
        ).all()
    else:
        theory_subjects = Subject.query.filter(
            Subject.type == 'Theory',
            Subject.id.in_(assigned_subject_ids)
        ).all() if assigned_subject_ids else []

    selected_class = db.session.get(CollegeClass, class_id) if class_id else None
    selected_subject = db.session.get(Subject, subject_id) if subject_id else None

    students_mark_list = []

    if selected_class and selected_subject:
        students = Student.query.filter_by(class_id=selected_class.id, status='Active').order_by(Student.register_number).all()

        for student in students:
            st_records = AttendanceRecord.query.join(AttendanceSession).filter(
                AttendanceSession.class_id == selected_class.id,
                AttendanceSession.subject_id == selected_subject.id,
                AttendanceRecord.student_id == student.id
            ).all()

            st_total = len(st_records)
            st_present = len([r for r in st_records if r.status == 'Present'])
            att_percentage = round((st_present / st_total * 100), 2) if st_total > 0 else 100.0

            att_mark = calculate_attendance_mark(att_percentage)

            existing_mark = TheoryInternalMark.query.filter_by(
                student_id=student.id,
                subject_id=selected_subject.id
            ).first()

            students_mark_list.append({
                'student': student,
                'attendance_percentage': att_percentage,
                'attendance_mark': att_mark,
                'existing_mark': existing_mark
            })

    if request.method == 'POST':
        post_class_id = request.form.get('class_id', type=int)
        post_subject_id = request.form.get('subject_id', type=int)
        exam_name = request.form.get('exam_name', 'Mid-Term Exam').strip()
        max_marks = request.form.get('max_marks', type=float, default=100.0)

        post_class = db.session.get(CollegeClass, post_class_id)
        post_subject = db.session.get(Subject, post_subject_id)

        if not post_class or not post_subject:
            flash('Invalid class or subject for internal marks.', 'danger')
            return redirect(url_for('theory_marks'))

        cfg = ExamConfig.query.filter_by(type='Theory').first()
        exam_max_weight = cfg.exam_max_weight if cfg else 20.0

        students = Student.query.filter_by(class_id=post_class.id, status='Active').all()

        for student in students:
            obtained_str = request.form.get(f'marks_{student.id}', '0')
            try:
                marks_obtained = float(obtained_str)
            except ValueError:
                marks_obtained = 0.0

            st_records = AttendanceRecord.query.join(AttendanceSession).filter(
                AttendanceSession.class_id == post_class.id,
                AttendanceSession.subject_id == post_subject.id,
                AttendanceRecord.student_id == student.id
            ).all()
            st_total = len(st_records)
            st_present = len([r for r in st_records if r.status == 'Present'])
            att_percentage = round((st_present / st_total * 100), 2) if st_total > 0 else 100.0

            att_mark = calculate_attendance_mark(att_percentage)

            scaled_exam_mark = round((marks_obtained / max_marks * exam_max_weight), 2) if max_marks > 0 else 0.0
            final_mark = round(scaled_exam_mark + att_mark, 2)

            if att_percentage < 50.0:
                result_status = 'RA'
            elif final_mark < 10.0:
                result_status = 'RA'
            else:
                result_status = 'Pass'

            m_record = TheoryInternalMark.query.filter_by(
                student_id=student.id,
                subject_id=post_subject.id
            ).first()

            if not m_record:
                m_record = TheoryInternalMark(
                    student_id=student.id,
                    subject_id=post_subject.id,
                    teacher_id=teacher.id,
                    exam_name=exam_name,
                    max_marks=max_marks,
                    marks_obtained=marks_obtained,
                    attendance_percentage=att_percentage,
                    attendance_mark=att_mark,
                    final_mark=final_mark,
                    status=result_status
                )
                db.session.add(m_record)
            else:
                m_record.exam_name = exam_name
                m_record.max_marks = max_marks
                m_record.marks_obtained = marks_obtained
                m_record.attendance_percentage = att_percentage
                m_record.attendance_mark = att_mark
                m_record.final_mark = final_mark
                m_record.status = result_status

        db.session.commit()
        flash('Theory internal marks saved successfully.', 'success')
        return redirect(url_for('theory_marks', class_id=post_class_id, subject_id=post_subject_id))

    return render_template(
        'theory_marks.html',
        classes=all_classes,
        theory_subjects=theory_subjects,
        selected_class=selected_class,
        selected_subject=selected_subject,
        selected_class_id=class_id,
        selected_subject_id=subject_id,
        students_mark_list=students_mark_list
    )

# Practical/Lab Internal Marks
@app.route('/marks/practical', methods=['GET', 'POST'])
@teacher_required
def practical_marks():
    teacher = get_current_teacher()
    all_classes = CollegeClass.query.all()

    class_id = request.args.get('class_id', type=int)
    subject_id = request.args.get('subject_id', type=int)

    ts_list = TeacherSubject.query.filter_by(teacher_id=teacher.id).all()
    assigned_subject_ids = [ts.subject_id for ts in ts_list]

    if class_id:
        practical_subjects = Subject.query.filter(
            Subject.class_id == class_id,
            Subject.type == 'Practical',
            Subject.id.in_(assigned_subject_ids)
        ).all()
    else:
        practical_subjects = Subject.query.filter(
            Subject.type == 'Practical',
            Subject.id.in_(assigned_subject_ids)
        ).all() if assigned_subject_ids else []

    selected_class = db.session.get(CollegeClass, class_id) if class_id else None
    selected_subject = db.session.get(Subject, subject_id) if subject_id else None

    students_mark_list = []

    if selected_class and selected_subject:
        students = Student.query.filter_by(class_id=selected_class.id, status='Active').order_by(Student.register_number).all()

        for student in students:
            st_records = AttendanceRecord.query.join(AttendanceSession).filter(
                AttendanceSession.class_id == selected_class.id,
                AttendanceSession.subject_id == selected_subject.id,
                AttendanceRecord.student_id == student.id
            ).all()

            st_total = len(st_records)
            st_present = len([r for r in st_records if r.status == 'Present'])
            att_percentage = round((st_present / st_total * 100), 2) if st_total > 0 else 100.0

            att_mark = calculate_attendance_mark(att_percentage)

            existing_mark = PracticalInternalMark.query.filter_by(
                student_id=student.id,
                subject_id=selected_subject.id
            ).first()

            students_mark_list.append({
                'student': student,
                'attendance_percentage': att_percentage,
                'attendance_mark': att_mark,
                'existing_mark': existing_mark
            })

    if request.method == 'POST':
        post_class_id = request.form.get('class_id', type=int)
        post_subject_id = request.form.get('subject_id', type=int)
        exam_name = request.form.get('exam_name', 'Lab Practical Exam').strip()
        max_marks = request.form.get('max_marks', type=float, default=100.0)

        post_class = db.session.get(CollegeClass, post_class_id)
        post_subject = db.session.get(Subject, post_subject_id)

        if not post_class or not post_subject:
            flash('Invalid class or subject for practical marks.', 'danger')
            return redirect(url_for('practical_marks'))

        cfg = ExamConfig.query.filter_by(type='Practical').first()
        exam_max_weight = cfg.exam_max_weight if cfg else 20.0

        students = Student.query.filter_by(class_id=post_class.id, status='Active').all()

        for student in students:
            obtained_str = request.form.get(f'marks_{student.id}', '0')
            try:
                marks_obtained = float(obtained_str)
            except ValueError:
                marks_obtained = 0.0

            st_records = AttendanceRecord.query.join(AttendanceSession).filter(
                AttendanceSession.class_id == post_class.id,
                AttendanceSession.subject_id == post_subject.id,
                AttendanceRecord.student_id == student.id
            ).all()
            st_total = len(st_records)
            st_present = len([r for r in st_records if r.status == 'Present'])
            att_percentage = round((st_present / st_total * 100), 2) if st_total > 0 else 100.0

            att_mark = calculate_attendance_mark(att_percentage)

            scaled_exam_mark = round((marks_obtained / max_marks * exam_max_weight), 2) if max_marks > 0 else 0.0
            final_mark = round(scaled_exam_mark + att_mark, 2)

            if att_percentage < 50.0:
                result_status = 'RA'
            elif final_mark < 10.0:
                result_status = 'RA'
            else:
                result_status = 'Pass'

            m_record = PracticalInternalMark.query.filter_by(
                student_id=student.id,
                subject_id=post_subject.id
            ).first()

            if not m_record:
                m_record = PracticalInternalMark(
                    student_id=student.id,
                    subject_id=post_subject.id,
                    teacher_id=teacher.id,
                    exam_name=exam_name,
                    max_marks=max_marks,
                    marks_obtained=marks_obtained,
                    attendance_percentage=att_percentage,
                    attendance_mark=att_mark,
                    final_mark=final_mark,
                    status=result_status
                )
                db.session.add(m_record)
            else:
                m_record.exam_name = exam_name
                m_record.max_marks = max_marks
                m_record.marks_obtained = marks_obtained
                m_record.attendance_percentage = att_percentage
                m_record.attendance_mark = att_mark
                m_record.final_mark = final_mark
                m_record.status = result_status

        db.session.commit()
        flash('Practical internal marks saved successfully.', 'success')
        return redirect(url_for('practical_marks', class_id=post_class_id, subject_id=post_subject_id))

    return render_template(
        'practical_marks.html',
        classes=all_classes,
        practical_subjects=practical_subjects,
        selected_class=selected_class,
        selected_subject=selected_subject,
        selected_class_id=class_id,
        selected_subject_id=subject_id,
        students_mark_list=students_mark_list
    )

# Comprehensive Reports View
@app.route('/reports')
@login_required
def reports_dashboard():
    user = get_current_user()
    teacher = get_current_teacher()
    all_classes = CollegeClass.query.all()

    report_type = request.args.get('report_type', 'daily_attendance')
    selected_class_id = request.args.get('class_id', type=int)
    selected_subject_id = request.args.get('subject_id', type=int)
    start_date_str = request.args.get('start_date', (date.today() - timedelta(days=30)).isoformat())
    end_date_str = request.args.get('end_date', date.today().isoformat())

    try:
        start_date = datetime.strptime(start_date_str, '%Y-%m-%d').date()
        end_date = datetime.strptime(end_date_str, '%Y-%m-%d').date()
    except Exception:
        start_date = date.today() - timedelta(days=30)
        end_date = date.today()

    if user.role == 'tutor':
        tutor_class = get_tutor_assigned_class(teacher.id)
        if tutor_class:
            selected_class_id = tutor_class.id

    selected_class = db.session.get(CollegeClass, selected_class_id) if selected_class_id else None
    available_subjects = Subject.query.filter_by(class_id=selected_class_id).all() if selected_class_id else Subject.query.all()

    report_data = []

    if report_type in ['daily_attendance', 'weekly_attendance', 'monthly_attendance']:
        query = AttendanceSession.query.filter(AttendanceSession.date >= start_date, AttendanceSession.date <= end_date)
        if selected_class_id:
            query = query.filter_by(class_id=selected_class_id)
        if selected_subject_id:
            query = query.filter_by(subject_id=selected_subject_id)
        report_data = query.order_by(AttendanceSession.date.desc(), AttendanceSession.period).all()

    elif report_type in ['theory_attendance', 'practical_attendance']:
        sub_type = 'Theory' if report_type == 'theory_attendance' else 'Practical'
        query = AttendanceSession.query.filter(
            AttendanceSession.type == sub_type,
            AttendanceSession.date >= start_date,
            AttendanceSession.date <= end_date
        )
        if selected_class_id:
            query = query.filter_by(class_id=selected_class_id)
        if selected_subject_id:
            query = query.filter_by(subject_id=selected_subject_id)
        report_data = query.order_by(AttendanceSession.date.desc()).all()

    elif report_type == 'student_wise':
        if selected_class_id:
            students = Student.query.filter_by(class_id=selected_class_id, status='Active').all()
            for st in students:
                st_records = AttendanceRecord.query.join(AttendanceSession).filter(
                    AttendanceSession.class_id == selected_class_id,
                    AttendanceRecord.student_id == st.id,
                    AttendanceSession.date >= start_date,
                    AttendanceSession.date <= end_date
                ).all()
                total = len(st_records)
                present = len([r for r in st_records if r.status == 'Present'])
                pct = round((present / total * 100), 2) if total > 0 else 0.0
                report_data.append({
                    'student': st,
                    'total': total,
                    'present': present,
                    'absent': total - present,
                    'percentage': pct
                })

    elif report_type == 'below_threshold':
        threshold = request.args.get('threshold', type=float, default=75.0)
        if selected_class_id:
            students = Student.query.filter_by(class_id=selected_class_id, status='Active').all()
            for st in students:
                st_records = AttendanceRecord.query.join(AttendanceSession).filter(
                    AttendanceSession.class_id == selected_class_id,
                    AttendanceRecord.student_id == st.id
                ).all()
                total = len(st_records)
                present = len([r for r in st_records if r.status == 'Present'])
                pct = round((present / total * 100), 2) if total > 0 else 100.0
                if pct < threshold:
                    report_data.append({
                        'student': st,
                        'total': total,
                        'present': present,
                        'absent': total - present,
                        'percentage': pct
                    })

    elif report_type == 'ra_students':
        if selected_class_id:
            students = Student.query.filter_by(class_id=selected_class_id, status='Active').all()
            for st in students:
                st_records = AttendanceRecord.query.join(AttendanceSession).filter(
                    AttendanceSession.class_id == selected_class_id,
                    AttendanceRecord.student_id == st.id
                ).all()
                total = len(st_records)
                present = len([r for r in st_records if r.status == 'Present'])
                pct = round((present / total * 100), 2) if total > 0 else 100.0
                if pct < 50.0:
                    report_data.append({
                        'student': st,
                        'total': total,
                        'present': present,
                        'absent': total - present,
                        'percentage': pct,
                        'status': 'RA (Below 50%)'
                    })

    elif report_type == 'theory_marks_report':
        query = TheoryInternalMark.query.join(Student)
        if selected_class_id:
            query = query.filter(Student.class_id == selected_class_id)
        if selected_subject_id:
            query = query.filter(TheoryInternalMark.subject_id == selected_subject_id)
        report_data = query.all()

    elif report_type == 'practical_marks_report':
        query = PracticalInternalMark.query.join(Student)
        if selected_class_id:
            query = query.filter(Student.class_id == selected_class_id)
        if selected_subject_id:
            query = query.filter(PracticalInternalMark.subject_id == selected_subject_id)
        report_data = query.all()

    return render_template(
        'reports.html',
        classes=all_classes,
        available_subjects=available_subjects,
        selected_class=selected_class,
        selected_class_id=selected_class_id,
        selected_subject_id=selected_subject_id,
        report_type=report_type,
        start_date=start_date_str,
        end_date=end_date_str,
        report_data=report_data
    )

# Individual Student Attendance Report Page
@app.route('/reports/student/<int:student_id>')
@login_required
def student_individual_report(student_id):
    student = db.session.get(Student, student_id)
    if not student:
        flash('Student not found.', 'danger')
        return redirect(url_for('reports_dashboard'))

    user = get_current_user()
    teacher = get_current_teacher()
    if user.role == 'tutor':
        tutor_class = get_tutor_assigned_class(teacher.id)
        if not tutor_class or tutor_class.id != student.class_id:
            flash('Access denied. You can only view reports for students in your assigned class.', 'danger')
            return redirect(url_for('tutor_dashboard'))

    subjects = Subject.query.filter_by(class_id=student.class_id).all()
    subject_summaries = []

    for subj in subjects:
        records = AttendanceRecord.query.join(AttendanceSession).filter(
            AttendanceSession.class_id == student.class_id,
            AttendanceSession.subject_id == subj.id,
            AttendanceRecord.student_id == student.id
        ).all()

        total = len(records)
        present = len([r for r in records if r.status == 'Present'])
        absent = total - present
        pct = round((present / total * 100), 2) if total > 0 else 0.0

        subject_summaries.append({
            'subject': subj,
            'total_conducted': total,
            'present_count': present,
            'absent_count': absent,
            'percentage': pct,
            'status_badge': 'RA' if pct < 50.0 else ('Warning' if pct < 75.0 else 'Good')
        })

    theory_marks = TheoryInternalMark.query.filter_by(student_id=student.id).all()
    practical_marks = PracticalInternalMark.query.filter_by(student_id=student.id).all()

    return render_template(
        'student_report.html',
        student=student,
        subject_summaries=subject_summaries,
        theory_marks=theory_marks,
        practical_marks=practical_marks
    )

# Export Report to CSV
@app.route('/reports/export/csv')
@login_required
def export_report_csv():
    user = get_current_user()
    teacher = get_current_teacher()

    report_type = request.args.get('report_type', 'daily_attendance')
    class_id = request.args.get('class_id', type=int)
    subject_id = request.args.get('subject_id', type=int)

    if user.role == 'tutor':
        tutor_class = get_tutor_assigned_class(teacher.id)
        if tutor_class:
            class_id = tutor_class.id

    si = io.StringIO()
    cw = csv.writer(si)

    if report_type in ['daily_attendance', 'weekly_attendance', 'monthly_attendance', 'theory_attendance', 'practical_attendance']:
        cw.writerow(['Session ID', 'Date', 'Period', 'Class', 'Subject', 'Type', 'Teacher', 'Total Students', 'Present', 'Absent', 'Percentage'])

        query = AttendanceSession.query
        if class_id:
            query = query.filter_by(class_id=class_id)
        if subject_id:
            query = query.filter_by(subject_id=subject_id)

        sessions = query.order_by(AttendanceSession.date.desc()).all()
        for s in sessions:
            cw.writerow([
                s.id, s.date.strftime('%Y-%m-%d'), s.period, s.college_class.name,
                s.subject.name, s.type, s.teacher.name, s.total_students,
                s.present_students, s.absent_students, f"{s.attendance_percentage}%"
            ])

    elif report_type in ['theory_marks_report', 'practical_marks_report']:
        cw.writerow(['Register Number', 'Student Name', 'Class', 'Subject', 'Exam', 'Marks Obtained', 'Max Marks', 'Attendance %', 'Attendance Mark (out of 5)', 'Final Mark', 'Status'])

        model_cls = TheoryInternalMark if report_type == 'theory_marks_report' else PracticalInternalMark
        query = model_cls.query.join(Student)

        if class_id:
            query = query.filter(Student.class_id == class_id)
        if subject_id:
            query = query.filter(model_cls.subject_id == subject_id)

        marks = query.all()
        for m in marks:
            cw.writerow([
                m.student.register_number, m.student.name, m.student.college_class.name,
                m.subject.name, m.exam_name, m.marks_obtained, m.max_marks,
                f"{m.attendance_percentage}%", m.attendance_mark, m.final_mark, m.status
            ])

    else:
        cw.writerow(['Register Number', 'Student Name', 'Class', 'Total Classes', 'Present', 'Absent', 'Attendance Percentage', 'Status'])

        if class_id:
            students = Student.query.filter_by(class_id=class_id, status='Active').all()
            for st in students:
                st_records = AttendanceRecord.query.join(AttendanceSession).filter(
                    AttendanceSession.class_id == class_id,
                    AttendanceRecord.student_id == st.id
                ).all()
                total = len(st_records)
                present = len([r for r in st_records if r.status == 'Present'])
                pct = round((present / total * 100), 2) if total > 0 else 0.0
                status_str = 'RA (Below 50%)' if pct < 50.0 else ('Below Threshold (<75%)' if pct < 75.0 else 'Satisfactory')

                if report_type == 'ra_students' and pct >= 50.0:
                    continue
                if report_type == 'below_threshold' and pct >= 75.0:
                    continue

                cw.writerow([st.register_number, st.name, st.college_class.name, total, present, total - present, f"{pct}%", status_str])

    output = Response(si.getvalue(), mimetype='text/csv')
    output.headers["Content-Disposition"] = f"attachment; filename={report_type}_report.csv"
    return output

if __name__ == '__main__':
    with app.app_context():
        init_db(app)
    app.run(debug=True)
