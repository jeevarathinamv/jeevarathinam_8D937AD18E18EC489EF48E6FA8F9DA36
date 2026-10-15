import unittest
from datetime import date
from app import app, db, seed_default_data, Admin, Teacher, ClassModel, Student, Subject, Timetable, AttendanceSession, AttendanceRecord

class CollegeAttendanceTestCase(unittest.TestCase):
    def setUp(self):
        app.config['TESTING'] = True
        app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
        app.config['WTF_CSRF_ENABLED'] = False
        self.client = app.test_client()

        with app.app_context():
            db.create_all()
            seed_default_data()

    def tearDown(self):
        with app.app_context():
            db.session.remove()
            db.drop_all()

    def test_logins(self):
        # Admin Login
        res_admin = self.client.post('/login', data={
            'role': 'admin',
            'identifier': 'admin',
            'password': 'admin123'
        }, follow_redirects=True)
        self.assertIn(b'Welcome to Admin Portal', res_admin.data)

        # Teacher Login
        res_teacher = self.client.post('/login', data={
            'role': 'teacher',
            'identifier': 'TCH101',
            'password': 'teacher123'
        }, follow_redirects=True)
        self.assertIn(b'Teacher Portal', res_teacher.data)

        # Class Tutor Login
        res_tutor = self.client.post('/login', data={
            'role': 'tutor',
            'identifier': 'TCH104', # Tutor for MCA I
            'password': 'teacher123'
        }, follow_redirects=True)
        self.assertIn(b'Class Tutor Dashboard', res_tutor.data)

        # Student Login
        res_student = self.client.post('/login', data={
            'role': 'student',
            'identifier': '2024MCA001',
            'password': 'student123'
        }, follow_redirects=True)
        self.assertIn(b'Student Portal', res_student.data)

    def test_attendance_marking_and_marks_calculation(self):
        # Login as Teacher TCH104 (Prof. Elena Rostova)
        self.client.post('/login', data={
            'role': 'teacher',
            'identifier': 'TCH104',
            'password': 'teacher123'
        })

        # Get timetable slot ID for Monday Hour 1 (MCA I, Python Web Dev)
        with app.app_context():
            slot = Timetable.query.filter_by(day='Monday', hour_number=1).first()
            slot_id = slot.id
            mca_students = Student.query.filter_by(class_id=slot.class_id).all()
            student1_id = mca_students[0].id
            student2_id = mca_students[1].id

        today_str = date.today().strftime('%Y-%m-%d')

        # Submit attendance: Student 1 Present, Student 2 Absent
        post_data = {
            f'status_{student1_id}': 'Present',
            f'status_{student2_id}': 'Absent'
        }
        res = self.client.post(f'/teacher/mark_attendance/{slot_id}?date={today_str}', data=post_data, follow_redirects=True)
        self.assertIn(b'submitted successfully', res.data)

        # Verify Student 1 dashboard (100% attendance -> 5 Marks)
        self.client.get('/logout')
        with app.app_context():
            s1 = Student.query.get(student1_id)
            reg1 = s1.register_number

        self.client.post('/login', data={
            'role': 'student',
            'identifier': reg1,
            'password': 'student123'
        })
        res_s1 = self.client.get('/student/dashboard')
        self.assertIn(b'100', res_s1.data)
        self.assertIn(b'5 / 5', res_s1.data)

        # Verify Student 2 dashboard (0% attendance -> RA)
        self.client.get('/logout')
        with app.app_context():
            s2 = Student.query.get(student2_id)
            reg2 = s2.register_number

        self.client.post('/login', data={
            'role': 'student',
            'identifier': reg2,
            'password': 'student123'
        })
        res_s2 = self.client.get('/student/dashboard')
        self.assertIn(b'RA - Attendance Below 50%', res_s2.data)

    def test_timetable_conflict_validation(self):
        # Admin Login
        self.client.post('/login', data={
            'role': 'admin',
            'identifier': 'admin',
            'password': 'admin123'
        })

        with app.app_context():
            mca1 = ClassModel.query.filter_by(name='MCA I').first()
            teacher = Teacher.query.filter_by(teacher_id_code='TCH104').first()
            subject = Subject.query.filter_by(class_id=mca1.id).first()

        # Try adding duplicate timetable slot for MCA I on Monday Hour 1
        res = self.client.post('/admin/timetable/add', data={
            'class_id': mca1.id,
            'day': 'Monday',
            'hour_number': 1,
            'subject_id': subject.id,
            'teacher_id': teacher.id,
            'start_time': '09:00 AM',
            'end_time': '10:00 AM'
        }, follow_redirects=True)

        self.assertIn(b'Timetable conflict', res.data)

    def test_csv_exports(self):
        self.client.post('/login', data={
            'role': 'admin',
            'identifier': 'admin',
            'password': 'admin123'
        })

        res_ra_csv = self.client.get('/export/csv?type=ra_students')
        self.assertEqual(res_ra_csv.status_code, 200)
        self.assertIn(b'Register Number', res_ra_csv.data)

if __name__ == '__main__':
    unittest.main()
