import os
from datetime import datetime, date, time
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash

db = SQLAlchemy()

class User(db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    role = db.Column(db.String(20), nullable=False, default='teacher') # 'teacher', 'tutor', 'both'

    teacher = db.relationship('Teacher', backref='user', uselist=False, lazy=True)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        from werkzeug.security import check_password_hash
        return check_password_hash(self.password_hash, password)

class Teacher(db.Model):
    __tablename__ = 'teachers'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    teacher_code = db.Column(db.String(20), unique=True, nullable=False)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(120), nullable=False)
    department = db.Column(db.String(100), nullable=False)

    class_tutor_assignments = db.relationship('ClassTutor', backref='teacher', lazy=True)
    teacher_subjects = db.relationship('TeacherSubject', backref='teacher', lazy=True)

class CollegeClass(db.Model):
    __tablename__ = 'classes'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), unique=True, nullable=False) # MCA 1, MCA 2, BCA 1, BCA 2, BCA 3
    department = db.Column(db.String(100), nullable=False)
    academic_year = db.Column(db.String(20), nullable=False)
    semester = db.Column(db.String(20), nullable=False)

    students = db.relationship('Student', backref='college_class', lazy=True)
    subjects = db.relationship('Subject', backref='college_class', lazy=True)
    tutor_assignment = db.relationship('ClassTutor', backref='college_class', uselist=False, lazy=True)

class ClassTutor(db.Model):
    __tablename__ = 'class_tutors'
    id = db.Column(db.Integer, primary_key=True)
    class_id = db.Column(db.Integer, db.ForeignKey('classes.id'), unique=True, nullable=False)
    teacher_id = db.Column(db.Integer, db.ForeignKey('teachers.id'), nullable=False)

    notifications = db.relationship('Notification', backref='tutor', lazy=True)

class Subject(db.Model):
    __tablename__ = 'subjects'
    id = db.Column(db.Integer, primary_key=True)
    class_id = db.Column(db.Integer, db.ForeignKey('classes.id'), nullable=False)
    code = db.Column(db.String(20), nullable=False)
    name = db.Column(db.String(100), nullable=False)
    type = db.Column(db.String(20), nullable=False, default='Theory') # 'Theory' or 'Practical'
    credits = db.Column(db.Integer, default=3)

    __table_args__ = (db.UniqueConstraint('class_id', 'code', name='_class_subject_code_uc'),)

class TeacherSubject(db.Model):
    __tablename__ = 'teacher_subjects'
    id = db.Column(db.Integer, primary_key=True)
    teacher_id = db.Column(db.Integer, db.ForeignKey('teachers.id'), nullable=False)
    subject_id = db.Column(db.Integer, db.ForeignKey('subjects.id'), nullable=False)
    class_id = db.Column(db.Integer, db.ForeignKey('classes.id'), nullable=False)

    subject = db.relationship('Subject', backref='teacher_assignments', lazy=True)
    college_class = db.relationship('CollegeClass', backref='teacher_subjects', lazy=True)

class Student(db.Model):
    __tablename__ = 'students'
    id = db.Column(db.Integer, primary_key=True)
    register_number = db.Column(db.String(50), nullable=False)
    name = db.Column(db.String(100), nullable=False)
    class_id = db.Column(db.Integer, db.ForeignKey('classes.id'), nullable=False)
    department = db.Column(db.String(100), nullable=False)
    academic_year = db.Column(db.String(20), nullable=False)
    semester = db.Column(db.String(20), nullable=False)
    status = db.Column(db.String(20), default='Active') # 'Active', 'Inactive'

    attendance_records = db.relationship('AttendanceRecord', backref='student', lazy=True)
    theory_marks = db.relationship('TheoryInternalMark', backref='student', lazy=True)
    practical_marks = db.relationship('PracticalInternalMark', backref='student', lazy=True)

    __table_args__ = (db.UniqueConstraint('class_id', 'register_number', name='_class_reg_uc'),)

class Timetable(db.Model):
    __tablename__ = 'timetable'
    id = db.Column(db.Integer, primary_key=True)
    class_id = db.Column(db.Integer, db.ForeignKey('classes.id'), nullable=False)
    day = db.Column(db.String(20), nullable=False) # Monday to Friday
    period = db.Column(db.Integer, nullable=False) # 1 to 5
    subject_id = db.Column(db.Integer, db.ForeignKey('subjects.id'), nullable=False)
    teacher_id = db.Column(db.Integer, db.ForeignKey('teachers.id'), nullable=False)
    start_time = db.Column(db.String(20), nullable=False)
    end_time = db.Column(db.String(20), nullable=False)
    type = db.Column(db.String(20), nullable=False, default='Theory') # 'Theory' or 'Practical'

    subject = db.relationship('Subject', backref='timetable_entries', lazy=True)
    teacher = db.relationship('Teacher', backref='timetable_entries', lazy=True)
    college_class = db.relationship('CollegeClass', backref='timetable_entries', lazy=True)

    __table_args__ = (
        db.UniqueConstraint('class_id', 'day', 'period', name='_class_day_period_uc'),
    )

class AttendanceSession(db.Model):
    __tablename__ = 'attendance_sessions'
    id = db.Column(db.Integer, primary_key=True)
    class_id = db.Column(db.Integer, db.ForeignKey('classes.id'), nullable=False)
    subject_id = db.Column(db.Integer, db.ForeignKey('subjects.id'), nullable=False)
    teacher_id = db.Column(db.Integer, db.ForeignKey('teachers.id'), nullable=False)
    date = db.Column(db.Date, nullable=False)
    period = db.Column(db.Integer, nullable=False)
    type = db.Column(db.String(20), nullable=False, default='Theory') # 'Theory' or 'Practical'
    total_students = db.Column(db.Integer, nullable=False, default=0)
    present_students = db.Column(db.Integer, nullable=False, default=0)
    absent_students = db.Column(db.Integer, nullable=False, default=0)
    attendance_percentage = db.Column(db.Float, nullable=False, default=0.0)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    college_class = db.relationship('CollegeClass', backref='attendance_sessions', lazy=True)
    subject = db.relationship('Subject', backref='attendance_sessions', lazy=True)
    teacher = db.relationship('Teacher', backref='attendance_sessions', lazy=True)
    records = db.relationship('AttendanceRecord', backref='session', cascade='all, delete-orphan', lazy=True)
    notifications = db.relationship('Notification', backref='session', cascade='all, delete-orphan', lazy=True)

    __table_args__ = (
        db.UniqueConstraint('class_id', 'subject_id', 'date', 'period', name='_session_unique_uc'),
    )

class AttendanceRecord(db.Model):
    __tablename__ = 'attendance_records'
    id = db.Column(db.Integer, primary_key=True)
    session_id = db.Column(db.Integer, db.ForeignKey('attendance_sessions.id'), nullable=False)
    student_id = db.Column(db.Integer, db.ForeignKey('students.id'), nullable=False)
    status = db.Column(db.String(20), nullable=False) # 'Present', 'Absent'
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)

    __table_args__ = (
        db.UniqueConstraint('session_id', 'student_id', name='_session_student_uc'),
    )

class Notification(db.Model):
    __tablename__ = 'notifications'
    id = db.Column(db.Integer, primary_key=True)
    tutor_id = db.Column(db.Integer, db.ForeignKey('class_tutors.id'), nullable=False)
    session_id = db.Column(db.Integer, db.ForeignKey('attendance_sessions.id'), nullable=False)
    title = db.Column(db.String(200), nullable=False)
    message = db.Column(db.Text, nullable=False)
    is_read = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class TheoryInternalMark(db.Model):
    __tablename__ = 'theory_internal_marks'
    id = db.Column(db.Integer, primary_key=True)
    student_id = db.Column(db.Integer, db.ForeignKey('students.id'), nullable=False)
    subject_id = db.Column(db.Integer, db.ForeignKey('subjects.id'), nullable=False)
    teacher_id = db.Column(db.Integer, db.ForeignKey('teachers.id'), nullable=False)
    exam_name = db.Column(db.String(100), nullable=False)
    max_marks = db.Column(db.Float, nullable=False, default=100.0)
    marks_obtained = db.Column(db.Float, nullable=False, default=0.0)
    attendance_percentage = db.Column(db.Float, nullable=False, default=0.0)
    attendance_mark = db.Column(db.Float, nullable=False, default=0.0) # Out of 5
    final_mark = db.Column(db.Float, nullable=False, default=0.0)
    status = db.Column(db.String(20), nullable=False, default='Pass') # 'Pass', 'RA'
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    subject = db.relationship('Subject', backref='theory_marks', lazy=True)
    teacher = db.relationship('Teacher', backref='theory_marks', lazy=True)

class PracticalInternalMark(db.Model):
    __tablename__ = 'practical_internal_marks'
    id = db.Column(db.Integer, primary_key=True)
    student_id = db.Column(db.Integer, db.ForeignKey('students.id'), nullable=False)
    subject_id = db.Column(db.Integer, db.ForeignKey('subjects.id'), nullable=False)
    teacher_id = db.Column(db.Integer, db.ForeignKey('teachers.id'), nullable=False)
    exam_name = db.Column(db.String(100), nullable=False)
    max_marks = db.Column(db.Float, nullable=False, default=100.0)
    marks_obtained = db.Column(db.Float, nullable=False, default=0.0)
    attendance_percentage = db.Column(db.Float, nullable=False, default=0.0)
    attendance_mark = db.Column(db.Float, nullable=False, default=0.0) # Out of 5
    final_mark = db.Column(db.Float, nullable=False, default=0.0)
    status = db.Column(db.String(20), nullable=False, default='Pass') # 'Pass', 'RA'
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    subject = db.relationship('Subject', backref='practical_marks', lazy=True)
    teacher = db.relationship('Teacher', backref='practical_marks', lazy=True)

class ExamConfig(db.Model):
    __tablename__ = 'exam_configs'
    id = db.Column(db.Integer, primary_key=True)
    type = db.Column(db.String(20), unique=True, nullable=False) # 'Theory' or 'Practical'
    exam_max_weight = db.Column(db.Float, default=20.0)
    attendance_max_weight = db.Column(db.Float, default=5.0)

def calculate_attendance_mark(percentage):
    if percentage >= 90.0:
        return 5.0
    elif percentage >= 80.0:
        return 4.0
    elif percentage >= 70.0:
        return 3.0
    elif percentage >= 60.0:
        return 2.0
    elif percentage >= 50.0:
        return 1.0
    else:
        return 0.0

def seed_database():
    if User.query.count() > 0:
        return

    # 1. Teachers
    teacher_data = [
        {'code': 'T001', 'name': 'Mr. VG', 'email': 'vg@college.edu', 'dept': 'Computer Applications', 'username': 'teacher_vg'},
        {'code': 'T002', 'name': 'Dr. AK', 'email': 'ak@college.edu', 'dept': 'Computer Applications', 'username': 'teacher_ak'},
        {'code': 'T003', 'name': 'Mr. SR', 'email': 'sr@college.edu', 'dept': 'Computer Science', 'username': 'teacher_sr'},
        {'code': 'T004', 'name': 'Mrs. DD', 'email': 'dd@college.edu', 'dept': 'Computer Applications', 'username': 'teacher_dd'},
        {'code': 'T005', 'name': 'Mrs. CE', 'email': 'ce@college.edu', 'dept': 'Computer Science', 'username': 'teacher_ce'},
        {'code': 'T006', 'name': 'Dr. CS', 'email': 'cs@college.edu', 'dept': 'Computer Applications', 'username': 'teacher_cs'},
        {'code': 'T007', 'name': 'Ms. AR', 'email': 'ar@college.edu', 'dept': 'Computer Applications', 'username': 'teacher_ar'},
    ]

    teachers_dict = {}
    for t_info in teacher_data:
        user = User(
            username=t_info['username'],
            name=t_info['name'],
            email=t_info['email'],
            role='both' if t_info['code'] in ['T001', 'T002', 'T003', 'T004', 'T005'] else 'teacher'
        )
        user.set_password('password123')
        db.session.add(user)
        db.session.flush()

        teacher = Teacher(
            user_id=user.id,
            teacher_code=t_info['code'],
            name=t_info['name'],
            email=t_info['email'],
            department=t_info['dept']
        )
        db.session.add(teacher)
        db.session.flush()
        teachers_dict[t_info['code']] = teacher

    # 2. Classes (Exactly 5)
    classes_data = [
        {'name': 'MCA 1', 'dept': 'Computer Applications', 'year': '1st Year', 'sem': 'Semester 1'},
        {'name': 'MCA 2', 'dept': 'Computer Applications', 'year': '2nd Year', 'sem': 'Semester 3'},
        {'name': 'BCA 1', 'dept': 'Computer Applications', 'year': '1st Year', 'sem': 'Semester 1'},
        {'name': 'BCA 2', 'dept': 'Computer Applications', 'year': '2nd Year', 'sem': 'Semester 3'},
        {'name': 'BCA 3', 'dept': 'Computer Applications', 'year': '3rd Year', 'sem': 'Semester 5'},
    ]

    classes_dict = {}
    for c_info in classes_data:
        c = CollegeClass(
            name=c_info['name'],
            department=c_info['dept'],
            academic_year=c_info['year'],
            semester=c_info['sem']
        )
        db.session.add(c)
        db.session.flush()
        classes_dict[c_info['name']] = c

    # 3. Class Tutors
    tutor_mapping = [
        ('MCA 1', 'T002'),
        ('MCA 2', 'T001'),
        ('BCA 1', 'T004'),
        ('BCA 2', 'T003'),
        ('BCA 3', 'T005'),
    ]

    for class_name, teacher_code in tutor_mapping:
        ct = ClassTutor(
            class_id=classes_dict[class_name].id,
            teacher_id=teachers_dict[teacher_code].id
        )
        db.session.add(ct)

    # 4. Subjects
    subjects_seed = [
        ('MCA 2', 'AJP', 'Advanced Java Programming', 'Theory', 4),
        ('MCA 2', 'DSR', 'Data Science using R', 'Theory', 4),
        ('MCA 2', 'CNS', 'Cryptography and Network Security', 'Theory', 3),
        ('MCA 2', 'WT', 'Web Technology', 'Theory', 3),
        ('MCA 2', 'MP', 'Mini Project', 'Practical', 2),
        ('MCA 2', 'WTL', 'WT Lab', 'Practical', 2),
        ('MCA 2', 'AJPL', 'AJP Lab', 'Practical', 2),
        ('MCA 2', 'LIB', 'Library', 'Theory', 1),

        ('MCA 1', 'JAVA', 'Java Programming', 'Theory', 4),
        ('MCA 1', 'DS', 'Data Structures', 'Theory', 4),
        ('MCA 1', 'DBMS', 'Database Management Systems', 'Theory', 4),
        ('MCA 1', 'JAVAL', 'Java Lab', 'Practical', 2),
        ('MCA 1', 'DBMSL', 'DBMS Lab', 'Practical', 2),

        ('BCA 1', 'CF', 'Computer Fundamentals', 'Theory', 3),
        ('BCA 1', 'CP', 'C Programming', 'Theory', 4),
        ('BCA 1', 'CPL', 'C Programming Lab', 'Practical', 2),

        ('BCA 2', 'CPP', 'C++ and OOPS', 'Theory', 4),
        ('BCA 2', 'OS', 'Operating Systems', 'Theory', 4),
        ('BCA 2', 'CPPL', 'C++ Lab', 'Practical', 2),

        ('BCA 3', 'SE', 'Software Engineering', 'Theory', 4),
        ('BCA 3', 'CN', 'Computer Networks', 'Theory', 4),
        ('BCA 3', 'SEL', 'Software Engineering Lab', 'Practical', 2),
    ]

    subjects_dict = {}
    for c_name, code, name, sub_type, credits in subjects_seed:
        c_obj = classes_dict[c_name]
        subj = Subject(
            class_id=c_obj.id,
            code=code,
            name=name,
            type=sub_type,
            credits=credits
        )
        db.session.add(subj)
        db.session.flush()
        subjects_dict[f"{c_name}_{code}"] = subj

    # 5. Teacher-Subject Assignments
    teacher_sub_mappings = [
        ('T001', 'MCA 2_AJP'),
        ('T001', 'MCA 2_AJPL'),
        ('T002', 'MCA 2_DSR'),
        ('T003', 'MCA 2_CNS'),
        ('T004', 'MCA 2_WT'),
        ('T004', 'MCA 2_WTL'),
        ('T005', 'MCA 2_MP'),
        ('T006', 'MCA 2_LIB'),
        ('T007', 'MCA 1_JAVA'),
        ('T002', 'MCA 1_JAVAL'),
        ('T004', 'BCA 1_CP'),
        ('T003', 'BCA 2_CPP'),
        ('T005', 'BCA 3_SE'),
    ]

    for t_code, sub_key in teacher_sub_mappings:
        if sub_key in subjects_dict:
            subj = subjects_dict[sub_key]
            ts = TeacherSubject(
                teacher_id=teachers_dict[t_code].id,
                subject_id=subj.id,
                class_id=subj.class_id
            )
            db.session.add(ts)

    # 6. Sample Students
    sample_students = {
        'MCA 1': [
            ('24MCA001', 'Aarav Sharma'),
            ('24MCA002', 'Bhavya Patel'),
            ('24MCA003', 'Chirag Reddy'),
            ('24MCA004', 'Divya Nair'),
            ('24MCA005', 'Eshwar Kumar'),
        ],
        'MCA 2': [
            ('23MCA101', 'Anand Raj'),
            ('23MCA102', 'Balaji Krishnan'),
            ('23MCA103', 'Catherine Varghese'),
            ('23MCA104', 'Dinesh Karthik'),
            ('23MCA105', 'Elena Gilbert'),
            ('23MCA106', 'Faisal Khan'),
        ],
        'BCA 1': [
            ('24BCA001', 'Gokul Krishna'),
            ('24BCA002', 'Hari Prasad'),
            ('24BCA003', 'Indumathi S'),
            ('24BCA004', 'Jaya Prakash'),
            ('24BCA005', 'Kavitha M'),
        ],
        'BCA 2': [
            ('23BCA001', 'Lokesh Nathan'),
            ('23BCA002', 'Manoj Kumar'),
            ('23BCA003', 'Nandhini R'),
            ('23BCA004', 'Om Prakash'),
            ('23BCA005', 'Pooja Hegde'),
        ],
        'BCA 3': [
            ('22BCA001', 'Qadir Ahmed'),
            ('22BCA002', 'Ramesh V'),
            ('22BCA003', 'Sangeetha B'),
            ('22BCA004', 'Thamarai Selvan'),
            ('22BCA005', 'Uma Maheshwari'),
        ]
    }

    for c_name, stud_list in sample_students.items():
        c_obj = classes_dict[c_name]
        for reg_no, name in stud_list:
            s = Student(
                register_number=reg_no,
                name=name,
                class_id=c_obj.id,
                department=c_obj.department,
                academic_year=c_obj.academic_year,
                semester=c_obj.semester,
                status='Active'
            )
            db.session.add(s)

    # 7. Timetable
    days = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday']
    times = [
        (1, '09:00 AM', '10:00 AM'),
        (2, '10:00 AM', '11:00 AM'),
        (3, '11:15 AM', '12:15 PM'),
        (4, '01:15 PM', '02:15 PM'),
        (5, '02:15 PM', '03:15 PM'),
    ]

    mca2_schedule = [
        (1, 'AJP', 'T001'), (2, 'DSR', 'T002'), (3, 'CNS', 'T003'), (4, 'WT', 'T004'), (5, 'LIB', 'T006'),
        (1, 'WT', 'T004'), (2, 'AJP', 'T001'), (3, 'DSR', 'T002'), (4, 'WTL', 'T004'), (5, 'WTL', 'T004'),
        (1, 'CNS', 'T003'), (2, 'AJP', 'T001'), (3, 'MP', 'T005'), (4, 'DSR', 'T002'), (5, 'WT', 'T004'),
        (1, 'AJPL', 'T001'), (2, 'AJPL', 'T001'), (3, 'CNS', 'T003'), (4, 'WT', 'T004'), (5, 'LIB', 'T006'),
        (1, 'DSR', 'T002'), (2, 'AJP', 'T001'), (3, 'CNS', 'T003'), (4, 'MP', 'T005'), (5, 'WT', 'T004'),
    ]

    mca2_obj = classes_dict['MCA 2']
    for idx, day in enumerate(days):
        day_schedule = mca2_schedule[idx*5 : (idx+1)*5]
        for period_num, sub_code, t_code in day_schedule:
            p_time = times[period_num-1]
            subj = subjects_dict[f"MCA 2_{sub_code}"]
            tt = Timetable(
                class_id=mca2_obj.id,
                day=day,
                period=period_num,
                subject_id=subj.id,
                teacher_id=teachers_dict[t_code].id,
                start_time=p_time[1],
                end_time=p_time[2],
                type=subj.type
            )
            db.session.add(tt)

    for c_name in ['MCA 1', 'BCA 1', 'BCA 2', 'BCA 3']:
        c_obj = classes_dict[c_name]
        c_subjects = [s for s in subjects_dict.values() if s.class_id == c_obj.id]
        if c_subjects:
            first_subj = c_subjects[0]
            t_obj = teachers_dict['T001']
            for day in days:
                for period_num in range(1, 6):
                    p_time = times[period_num-1]
                    tt = Timetable(
                        class_id=c_obj.id,
                        day=day,
                        period=period_num,
                        subject_id=first_subj.id,
                        teacher_id=t_obj.id,
                        start_time=p_time[1],
                        end_time=p_time[2],
                        type=first_subj.type
                    )
                    db.session.add(tt)

    # 8. Exam Configs
    cfg_theory = ExamConfig(type='Theory', exam_max_weight=20.0, attendance_max_weight=5.0)
    cfg_pract = ExamConfig(type='Practical', exam_max_weight=20.0, attendance_max_weight=5.0)
    db.session.add_all([cfg_theory, cfg_pract])

    db.session.commit()
    print("Database seeded successfully!")

def init_db(app):
    with app.app_context():
        if 'sqlalchemy' not in app.extensions:
            db.init_app(app)
        db.create_all()
        seed_database()

if __name__ == '__main__':
    from flask import Flask
    app = Flask(__name__)
    db_path = os.path.join(os.path.abspath(os.path.dirname(__file__)), 'college_attendance.db')
    app.config['SQLALCHEMY_DATABASE_URI'] = f'sqlite:///{db_path}'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    init_db(app)
    print("college_attendance.db initialized.")
