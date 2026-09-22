import unittest
from app import app, db, Student, Admin, HelpRequest

class SmartCollegeHelpDeskTestCase(unittest.TestCase):
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
            db.session.commit()

    def tearDown(self):
        with app.app_context():
            db.session.remove()
            db.drop_all()

    def test_student_registration_and_login(self):
        # Register
        response = self.client.post('/register', data={
            'name': 'Jane Student',
            'register_number': 'REG999',
            'department': 'Computer Science',
            'email': 'jane@college.edu',
            'password': 'password123'
        }, follow_redirects=True)
        self.assertIn(b'Registration successful', response.data)

        # Login
        response = self.client.post('/login', data={
            'login_type': 'student',
            'email_or_reg': 'jane@college.edu',
            'password': 'password123'
        }, follow_redirects=True)
        self.assertIn(b'Welcome back, Jane Student!', response.data)

    def test_admin_login(self):
        response = self.client.post('/login', data={
            'login_type': 'admin',
            'username': 'admin',
            'password': 'admin123'
        }, follow_redirects=True)
        self.assertIn(b'Logged in successfully as Help Desk Administrator', response.data)

    def test_smart_help_faq_access(self):
        response = self.client.get('/smart-help?category=Academic')
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Academic', response.data)

    def test_help_request_submission_and_admin_workflow(self):
        # Register student
        self.client.post('/register', data={
            'name': 'Bob Smith',
            'register_number': 'REG555',
            'department': 'Electronics',
            'email': 'bob@college.edu',
            'password': 'pass'
        })

        # Login student
        self.client.post('/login', data={
            'login_type': 'student',
            'email_or_reg': 'bob@college.edu',
            'password': 'pass'
        })

        # Submit Help Request
        response = self.client.post('/student/request/new', data={
            'category': 'Exam',
            'subject': 'Exam timetable clash',
            'description': 'Two of my elective papers are scheduled on the same date.'
        }, follow_redirects=True)
        self.assertIn(b'submitted successfully', response.data)

        with app.app_context():
            req = HelpRequest.query.filter_by(subject='Exam timetable clash').first()
            self.assertIsNotNone(req)
            self.assertEqual(req.status, 'Pending')
            req_id = req.id

        # Student Dashboard check
        response = self.client.get('/student/dashboard')
        self.assertIn(b'Exam timetable clash', response.data)

        # Logout student and Login Admin
        self.client.get('/logout')
        self.client.post('/login', data={
            'login_type': 'admin',
            'username': 'admin',
            'password': 'admin123'
        })

        # Admin replies and updates status to In Progress
        response = self.client.post(f'/admin/request/reply/{req_id}', data={
            'admin_reply': 'We have forwarded your request to Controller of Exams.',
            'status': 'In Progress'
        }, follow_redirects=True)
        self.assertIn(b'updated successfully to status', response.data)

        with app.app_context():
            req = db.session.get(HelpRequest, req_id)
            self.assertEqual(req.status, 'In Progress')
            self.assertIn('Controller of Exams', req.admin_reply)

        # Admin resolves request
        response = self.client.post(f'/admin/request/reply/{req_id}', data={
            'admin_reply': 'Timetable revised and updated on exam portal.',
            'status': 'Resolved'
        }, follow_redirects=True)
        self.assertIn(b'updated successfully to status', response.data)

        with app.app_context():
            req = db.session.get(HelpRequest, req_id)
            self.assertEqual(req.status, 'Resolved')

if __name__ == '__main__':
    unittest.main()
