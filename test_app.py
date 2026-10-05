import unittest
from datetime import date, timedelta
from app import app, db, Student, Admin, AcademicEvent, seed_default_data

class AcademicCalendarTestCase(unittest.TestCase):
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

    def test_student_registration_and_login(self):
        # Student Registration
        response = self.client.post('/register', data={
            'student_name': 'Rahul Sharma',
            'register_number': '21MCA001',
            'department': 'Computer Applications (MCA)',
            'email': 'rahul@college.edu',
            'password': 'password123'
        }, follow_redirects=True)
        self.assertIn(b'Registration successful', response.data)

        # Duplicate Student Registration
        response = self.client.post('/register', data={
            'student_name': 'Rahul Duplicate',
            'register_number': '21MCA001',
            'department': 'Computer Applications (MCA)',
            'email': 'rahul@college.edu',
            'password': 'password123'
        }, follow_redirects=True)
        self.assertIn(b'already exists', response.data)

        # Student Login with Register Number
        response = self.client.post('/login', data={
            'email_or_reg': '21MCA001',
            'password': 'password123'
        }, follow_redirects=True)
        self.assertIn(b'Welcome back, Rahul Sharma!', response.data)

        # Logout
        response = self.client.get('/logout', follow_redirects=True)
        self.assertIn(b'You have been logged out', response.data)

    def test_admin_login(self):
        # Admin Login
        response = self.client.post('/admin_login', data={
            'username': 'admin',
            'password': 'admin123'
        }, follow_redirects=True)
        self.assertIn(b'Logged in successfully as Administrator', response.data)

        # Verify Admin Dashboard Content
        response = self.client.get('/admin/dashboard')
        self.assertIn(b'Admin Dashboard', response.data)

    def test_event_crud_workflow(self):
        # Log in as Admin
        self.client.post('/admin_login', data={
            'username': 'admin',
            'password': 'admin123'
        })

        today = date.today()
        # Add New Academic Event
        response = self.client.post('/admin/event/add', data={
            'event_title': 'MCA Tech Fest 2025',
            'event_type': 'College Event',
            'department': 'Computer Applications (MCA)',
            'semester': 'All Semesters',
            'start_date': today.strftime('%Y-%m-%d'),
            'end_date': (today + timedelta(days=2)).strftime('%Y-%m-%d'),
            'venue': 'College Grounds',
            'description': 'Annual technical festival for computer applications students.'
        }, follow_redirects=True)
        self.assertIn(b'created successfully', response.data)

        # Verify Event in Event Management
        response = self.client.get('/admin/events')
        self.assertIn(b'MCA Tech Fest 2025', response.data)

        # Edit Academic Event
        with app.app_context():
            event = db.session.query(AcademicEvent).filter_by(event_title='MCA Tech Fest 2025').first()
            event_id = event.id

        response = self.client.post(f'/admin/event/edit/{event_id}', data={
            'event_title': 'Grand MCA Tech Fest 2025',
            'event_type': 'College Event',
            'department': 'Computer Applications (MCA)',
            'semester': 'All Semesters',
            'start_date': today.strftime('%Y-%m-%d'),
            'end_date': (today + timedelta(days=2)).strftime('%Y-%m-%d'),
            'venue': 'Main Auditorium',
            'description': 'Updated technical festival venue and details.'
        }, follow_redirects=True)
        self.assertIn(b'updated successfully', response.data)

        # Delete Academic Event
        response = self.client.post(f'/admin/event/delete/{event_id}', follow_redirects=True)
        self.assertIn(b'deleted successfully', response.data)

    def test_calendar_filtering(self):
        # Register and login student
        self.client.post('/register', data={
            'student_name': 'Anita Roy',
            'register_number': '21MCA002',
            'department': 'Computer Applications (MCA)',
            'email': 'anita@college.edu',
            'password': 'pass'
        })
        self.client.post('/login', data={
            'email_or_reg': 'anita@college.edu',
            'password': 'pass'
        })

        # View Calendar
        response = self.client.get('/calendar')
        self.assertEqual(response.status_code, 200)

        # Filter by Event Type
        response = self.client.get('/calendar?event_type=Holiday')
        self.assertIn(b'National Youth Day Holiday', response.data)

    def test_student_management(self):
        # Register student
        self.client.post('/register', data={
            'student_name': 'Priya Singh',
            'register_number': '21MCA003',
            'department': 'Computer Applications (MCA)',
            'email': 'priya@college.edu',
            'password': 'pass'
        })

        # Admin login
        self.client.post('/admin_login', data={
            'username': 'admin',
            'password': 'admin123'
        })

        # View students list
        response = self.client.get('/admin/students')
        self.assertIn(b'Priya Singh', response.data)

        with app.app_context():
            student = db.session.query(Student).filter_by(email='priya@college.edu').first()
            student_id = student.id

        # Delete student
        response = self.client.post(f'/admin/student/delete/{student_id}', follow_redirects=True)
        self.assertIn(b'deleted successfully', response.data)

if __name__ == '__main__':
    unittest.main()
