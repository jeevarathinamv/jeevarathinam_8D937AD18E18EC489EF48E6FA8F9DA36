import unittest
from datetime import date
from app import app, db, Student, Admin, Attendance

class StudentAttendanceTestCase(unittest.TestCase):
    def setUp(self):
        app.config['TESTING'] = True
        app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
        app.config['WTF_CSRF_ENABLED'] = False
        self.client = app.test_client()

        with app.app_context():
            db.create_all()

    def tearDown(self):
        with app.app_context():
            db.session.remove()
            db.drop_all()

    def test_student_registration_and_login(self):
        # Register student
        response = self.client.post('/register', data={
            'name': 'John Doe',
            'register_number': 'REG202501',
            'department': 'Computer Science & Engineering',
            'email': 'john@college.edu',
            'password': 'password123'
        }, follow_redirects=True)
        self.assertIn(b'Registration successful', response.data)

        # Login student
        response = self.client.post('/login', data={
            'email_or_reg': 'john@college.edu',
            'password': 'password123'
        }, follow_redirects=True)
        self.assertIn(b'Welcome back, John Doe!', response.data)

    def test_admin_login(self):
        response = self.client.post('/admin/login', data={
            'username': 'admin',
            'password': 'admin123'
        }, follow_redirects=True)
        self.assertIn(b'Logged in successfully as Administrator', response.data)

    def test_attendance_marking_and_shortage_alert(self):
        # 1. Register student
        self.client.post('/register', data={
            'name': 'Jane Smith',
            'register_number': 'REG202502',
            'department': 'Information Technology',
            'email': 'jane@college.edu',
            'password': 'password123'
        })

        # 2. Login as Admin
        self.client.post('/admin/login', data={
            'username': 'admin',
            'password': 'admin123'
        })

        # 3. Mark 3 Absent records and 1 Present record (25% attendance -> Shortage)
        for d in range(1, 4):
            self.client.post('/admin/attendance', data={
                'student_id': 1,
                'subject': 'Data Structures',
                'date': f'2025-02-0{d}',
                'status': 'Absent'
            }, follow_redirects=True)

        self.client.post('/admin/attendance', data={
            'student_id': 1,
            'subject': 'Data Structures',
            'date': '2025-02-04',
            'status': 'Present'
        }, follow_redirects=True)

        # Logout Admin
        self.client.get('/logout')

        # 4. Login as Student Jane Smith
        self.client.post('/login', data={
            'email_or_reg': 'jane@college.edu',
            'password': 'password123'
        })

        # 5. Verify Student Dashboard displays Shortage Alert (< 75%)
        response = self.client.get('/student/dashboard')
        self.assertIn(b'Attendance Shortage Alert!', response.data)
        self.assertIn(b'25.0%', response.data)

        # 6. Login back as Admin and mark 3 more Present records (4 Present / 7 Total = 57.14%) and 4 more Present (8/11 = 72.7%) then 1 more (9/12 = 75% -> Satisfactory)
        self.client.get('/logout')
        self.client.post('/admin/login', data={
            'username': 'admin',
            'password': 'admin123'
        })

        for d in range(5, 13):
            self.client.post('/admin/attendance', data={
                'student_id': 1,
                'subject': 'Data Structures',
                'date': f'2025-02-{d:02d}',
                'status': 'Present'
            }, follow_redirects=True)

        # 7. Check student dashboard again for Satisfactory alert
        self.client.get('/logout')
        self.client.post('/login', data={
            'email_or_reg': 'jane@college.edu',
            'password': 'password123'
        })

        response = self.client.get('/student/dashboard')
        self.assertIn(b'Attendance is Satisfactory', response.data)
        self.assertIn(b'75.0%', response.data)

if __name__ == '__main__':
    unittest.main()
