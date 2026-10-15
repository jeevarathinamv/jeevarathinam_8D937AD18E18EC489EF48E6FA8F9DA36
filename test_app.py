import unittest
from datetime import date
from app import app, db, Admin, Teacher, Student, Class, Subject, Timetable, AttendanceSession, AttendanceRecord, InternalMarkRule, calculate_internal_mark

class AttendanceSystemTestCase(unittest.TestCase):
    def setUp(self):
        app.config['TESTING'] = True
        app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
        app.config['WTF_CSRF_ENABLED'] = False
        self.client = app.test_client()

        with app.app_context():
            db.drop_all()
            db.create_all()

            # Seed Admin
            admin = Admin(username='admin', email='admin@college.edu')
            admin.set_password('admin123')
            db.session.add(admin)

            # Seed Rules
            rules = [
                InternalMarkRule(min_percentage=90.0, max_percentage=100.0, mark=5, status_label='Eligible'),
                InternalMarkRule(min_percentage=80.0, max_percentage=89.99, mark=4, status_label='Eligible'),
                InternalMarkRule(min_percentage=70.0, max_percentage=79.99, mark=3, status_label='Eligible'),
                InternalMarkRule(min_percentage=60.0, max_percentage=69.99, mark=2, status_label='Eligible'),
                InternalMarkRule(min_percentage=50.0, max_percentage=59.99, mark=1, status_label='Eligible'),
                InternalMarkRule(min_percentage=0.0,  max_percentage=49.99, mark=0, status_label='RA – Attendance Below 50%')
            ]
            db.session.add_all(rules)

            # Seed Classes (BCA I, BCA II, BCA III, MCA I, MCA II)
            c1 = Class(name='BCA I')
            c2 = Class(name='BCA II')
            c3 = Class(name='BCA III')
            c4 = Class(name='MCA I')
            c5 = Class(name='MCA II')
            db.session.add_all([c1, c2, c3, c4, c5])
            db.session.commit()

            # Seed Teachers / Tutors
            t1 = Teacher(teacher_id='TCH101', name='Dr. Rajesh Kumar', email='rajesh@college.edu', role='Class Tutor', assigned_class_id=c4.id)
            t1.set_password('teacher123')
            t2 = Teacher(teacher_id='TCH102', name='Prof. Sunita Sharma', email='sunita@college.edu', role='Teacher')
            t2.set_password('teacher123')
            db.session.add_all([t1, t2])
            db.session.commit()

            c4.tutor_id = t1.id

            # Seed Subjects
            sub1 = Subject(code='MCA101', name='Advanced Data Structures', class_id=c4.id)
            sub2 = Subject(code='MCA102', name='Python Programming', class_id=c4.id)
            db.session.add_all([sub1, sub2])
            db.session.commit()

            t1.assigned_subject_id = sub1.id

            # Seed Students in MCA I
            s1 = Student(name='Kavitha Ramesh', register_number='23MCA01', department='Computer Applications', class_id=c4.id, email='kavitha@college.edu')
            s1.set_password('student123')
            s2 = Student(name='Manoj Kumar', register_number='23MCA04', department='Computer Applications', class_id=c4.id, email='manoj@college.edu')
            s2.set_password('student123')
            db.session.add_all([s1, s2])
            db.session.commit()

    def tearDown(self):
        with app.app_context():
            db.session.remove()
            db.drop_all()

    def test_login_and_auth(self):
        # Admin login
        res = self.client.post('/login', data={'login_type': 'admin', 'identifier': 'admin', 'password': 'admin123'}, follow_redirects=True)
        self.assertIn(b'Administrator Dashboard', res.data)

        # Logout
        res = self.client.get('/logout', follow_redirects=True)
        self.assertIn(b'logged out', res.data)

        # Teacher / Tutor login
        res = self.client.post('/login', data={'login_type': 'teacher', 'identifier': 'rajesh@college.edu', 'password': 'teacher123'}, follow_redirects=True)
        self.assertIn(b'Class Tutor Dashboard', res.data)

        self.client.get('/logout')

        # Student login
        res = self.client.post('/login', data={'login_type': 'student', 'identifier': '23MCA01', 'password': 'student123'}, follow_redirects=True)
        self.assertIn(b'Student Attendance Portal', res.data)

    def test_student_management(self):
        # Admin login
        self.client.post('/login', data={'login_type': 'admin', 'identifier': 'admin', 'password': 'admin123'})

        # Add Student
        res = self.client.post('/admin/students', data={
            'name': 'New Student',
            'register_number': '23MCA99',
            'department': 'Computer Applications',
            'class_id': 4,
            'email': 'newstudent@college.edu',
            'phone': '9999999999',
            'password': 'password123'
        }, follow_redirects=True)
        self.assertIn(b'added successfully', res.data)

        # Verify in DB
        with app.app_context():
            st = Student.query.filter_by(register_number='23MCA99').first()
            self.assertIsNotNone(st)
            self.assertEqual(st.name, 'New Student')

    def test_timetable_and_conflict_prevention(self):
        # Admin login
        self.client.post('/login', data={'login_type': 'admin', 'identifier': 'admin', 'password': 'admin123'})

        # Add timetable slot
        res = self.client.post('/admin/timetable', data={
            'class_id': 4,
            'day': 'Monday',
            'hour_number': 1,
            'subject_id': 1,
            'teacher_id': 1,
            'start_time': '09:30 AM',
            'end_time': '10:30 AM'
        }, follow_redirects=True)
        self.assertIn(b'created successfully', res.data)

        # Attempt duplicate class-hour entry
        res_dup_class = self.client.post('/admin/timetable', data={
            'class_id': 4,
            'day': 'Monday',
            'hour_number': 1,
            'subject_id': 2,
            'teacher_id': 2,
            'start_time': '09:30 AM',
            'end_time': '10:30 AM'
        }, follow_redirects=True)
        self.assertIn(b'Class already has a subject scheduled', res_dup_class.data)

        # Attempt duplicate teacher-hour entry
        res_dup_teacher = self.client.post('/admin/timetable', data={
            'class_id': 1,
            'day': 'Monday',
            'hour_number': 1,
            'subject_id': 1,
            'teacher_id': 1,
            'start_time': '09:30 AM',
            'end_time': '10:30 AM'
        }, follow_redirects=True)
        self.assertIn(b'Teacher is already assigned to another class', res_dup_teacher.data)

    def test_attendance_marking_and_calculations(self):
        # Teacher login (TCH101 - Rajesh)
        self.client.post('/login', data={'login_type': 'teacher', 'identifier': 'rajesh@college.edu', 'password': 'teacher123'})

        # Submit session #1: Kavitha (1) Present, Manoj (2) Absent
        res = self.client.post('/teacher/attendance/save', data={
            'class_id': 4,
            'subject_id': 1,
            'hour_number': 1,
            'session_date': '2025-02-10',
            'attendance_1': 'Present', # Kavitha
            'attendance_2': 'Absent'   # Manoj
        }, follow_redirects=True)
        self.assertIn(b'Attendance recorded successfully', res.data)

        # Attempt duplicate attendance for same session
        res_dup = self.client.post('/teacher/attendance/save', data={
            'class_id': 4,
            'subject_id': 1,
            'hour_number': 1,
            'session_date': '2025-02-10',
            'attendance_1': 'Present',
            'attendance_2': 'Present'
        }, follow_redirects=True)
        self.assertIn(b'has already been submitted', res_dup.data)

        # Check internal mark calculations in student dashboard
        self.client.get('/logout')
        self.client.post('/login', data={'login_type': 'student', 'identifier': '23MCA01', 'password': 'student123'})
        res_kavitha = self.client.get('/student/dashboard')
        self.assertIn(b'100.0%', res_kavitha.data)
        self.assertIn(b'5 / 5', res_kavitha.data)
        self.assertIn(b'Eligible', res_kavitha.data)

        # Check Manoj (0% -> RA)
        self.client.get('/logout')
        self.client.post('/login', data={'login_type': 'student', 'identifier': '23MCA04', 'password': 'student123'})
        res_manoj = self.client.get('/student/dashboard')
        self.assertIn(b'0.0%', res_manoj.data)
        self.assertIn(b'0 / 5', res_manoj.data)
        self.assertIn(b'RA \xe2\x80\x93 Attendance Below 50%', res_manoj.data)

    def test_internal_mark_rule_evaluation(self):
        with app.app_context():
            self.assertEqual(calculate_internal_mark(95.0), (5, 'Eligible'))
            self.assertEqual(calculate_internal_mark(85.0), (4, 'Eligible'))
            self.assertEqual(calculate_internal_mark(75.0), (3, 'Eligible'))
            self.assertEqual(calculate_internal_mark(65.0), (2, 'Eligible'))
            self.assertEqual(calculate_internal_mark(55.0), (1, 'Eligible'))
            self.assertEqual(calculate_internal_mark(45.0), (0, 'RA – Attendance Below 50%'))

    def test_reports_and_csv_export(self):
        # Admin login
        self.client.post('/login', data={'login_type': 'admin', 'identifier': 'admin', 'password': 'admin123'})

        # Get reports
        for r_type in ['daily', 'class_wise', 'student_wise', 'subject_wise', 'monthly', 'internal_mark', 'ra_students']:
            res = self.client.get(f'/reports?type={r_type}')
            self.assertEqual(res.status_code, 200)

        # Export CSV
        res_csv = self.client.get('/reports/export/csv?type=student_wise')
        self.assertEqual(res_csv.status_code, 200)
        self.assertIn('text/csv', res_csv.headers['Content-Type'])
        self.assertIn(b'Student Name,Register Number,Class,Subject', res_csv.data)

if __name__ == '__main__':
    unittest.main()
