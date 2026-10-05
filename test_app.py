import unittest
from datetime import date, timedelta
from app import app, db, Admin, Student, ExamTimetable

class ExamTimetableTestCase(unittest.TestCase):
    def setUp(self):
        app.config['TESTING'] = True
        app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
        app.config['WTF_CSRF_ENABLED'] = False
        self.client = app.test_client()

        with app.app_context():
            db.create_all()
            # Seed default admin
            admin = Admin(username='admin')
            admin.set_password('admin123')
            db.session.add(admin)

            # Seed sample timetable entries
            exam1 = ExamTimetable(
                exam_name='End Semester Examinations - May 2025',
                department='Master of Computer Applications (MCA)',
                semester='Semester 1',
                subject_name='Data Structures and Algorithms',
                subject_code='MCA101',
                exam_date=date.today() + timedelta(days=5),
                exam_time='10:00 AM - 01:00 PM',
                exam_venue='Lab Hall A'
            )
            exam2 = ExamTimetable(
                exam_name='Mid Term Examinations - March 2025',
                department='Department of Information Technology',
                semester='Semester 2',
                subject_name='Cloud Computing',
                subject_code='IT201',
                exam_date=date.today() + timedelta(days=10),
                exam_time='02:00 PM - 05:00 PM',
                exam_venue='IT Hall 2'
            )
            db.session.add_all([exam1, exam2])
            db.session.commit()

    def tearDown(self):
        with app.app_context():
            db.session.remove()
            db.drop_all()

    def test_public_pages(self):
        # Home page
        response = self.client.get('/')
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Student Exam Timetable Management System', response.data)

        # Timetable page
        response = self.client.get('/timetable')
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'MCA101', response.data)

    def test_student_registration_and_login(self):
        # Register new student
        response = self.client.post('/register', data={
            'student_name': 'Ananya Roy',
            'register_number': '2024MCA001',
            'department': 'Master of Computer Applications (MCA)',
            'email': 'ananya@college.edu',
            'password': 'password123'
        }, follow_redirects=True)
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Registration successful', response.data)

        # Login student
        response = self.client.post('/login', data={
            'email_or_reg': 'ananya@college.edu',
            'password': 'password123'
        }, follow_redirects=True)
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Welcome back, Ananya Roy!', response.data)

        # Access student dashboard
        response = self.client.get('/student/dashboard')
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Upcoming Exams', response.data)
        self.assertIn(b'MCA101', response.data)

    def test_admin_login_and_dashboard(self):
        # Login admin
        response = self.client.post('/admin/login', data={
            'username': 'admin',
            'password': 'admin123'
        }, follow_redirects=True)
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Successfully logged in as Administrator', response.data)

        # Access admin dashboard
        response = self.client.get('/admin/dashboard')
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Total Students', response.data)

    def test_admin_timetable_crud(self):
        # Login as admin
        self.client.post('/admin/login', data={
            'username': 'admin',
            'password': 'admin123'
        })

        # Add exam
        future_date = (date.today() + timedelta(days=15)).strftime('%Y-%m-%d')
        response = self.client.post('/admin/timetable/add', data={
            'exam_name': 'End Semester Examinations - May 2025',
            'department': 'Master of Computer Applications (MCA)',
            'semester': 'Semester 1',
            'subject_name': 'Python Flask Web Dev',
            'subject_code': 'MCA103',
            'exam_date': future_date,
            'exam_time': '10:00 AM - 01:00 PM',
            'exam_venue': 'Computer Lab 1'
        }, follow_redirects=True)
        self.assertIn(b'added successfully', response.data)

        # Edit exam
        response = self.client.post('/admin/timetable/edit/1', data={
            'exam_name': 'End Semester Examinations - May 2025',
            'department': 'Master of Computer Applications (MCA)',
            'semester': 'Semester 1',
            'subject_name': 'Data Structures and Algorithms - Advanced',
            'subject_code': 'MCA101',
            'exam_date': future_date,
            'exam_time': '10:00 AM - 01:00 PM',
            'exam_venue': 'Lab Hall A'
        }, follow_redirects=True)
        self.assertIn(b'updated successfully', response.data)

        # Delete exam
        response = self.client.post('/admin/timetable/delete/1', follow_redirects=True)
        self.assertIn(b'deleted successfully', response.data)

    def test_timetable_filtering(self):
        response = self.client.get('/timetable?department=Master+of+Computer+Applications+(MCA)')
        self.assertIn(b'MCA101', response.data)
        self.assertNotIn(b'IT201', response.data)

if __name__ == '__main__':
    unittest.main()
