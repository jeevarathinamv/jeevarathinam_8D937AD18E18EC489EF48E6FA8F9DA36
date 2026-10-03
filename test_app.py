import unittest
from datetime import date, timedelta
from app import app, db, Student, Admin, Assignment, Submission, get_deadline_status

class AssignmentTrackerTestCase(unittest.TestCase):
    def setUp(self):
        app.config['TESTING'] = True
        app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
        app.config['WTF_CSRF_ENABLED'] = False
        self.client = app.test_client()

        with app.app_context():
            db.create_all()
            # Seed test assignments
            today = date.today()
            self.asgn1 = Assignment(
                title='Flask Basics',
                subject='Web Tech',
                description='Intro to Flask routing and Jinja',
                given_date=today - timedelta(days=3),
                deadline_date=today + timedelta(days=5)
            )
            self.asgn2 = Assignment(
                title='SQL Normalization',
                subject='DBMS',
                description='1NF to 3NF',
                given_date=today - timedelta(days=10),
                deadline_date=today - timedelta(days=1)
            )
            db.session.add_all([self.asgn1, self.asgn2])

            # Seed test admin
            self.admin = Admin(username='admin', email='admin@college.edu')
            self.admin.set_password('admin123')
            db.session.add(self.admin)

            db.session.commit()

    def tearDown(self):
        with app.app_context():
            db.session.remove()
            db.drop_all()

    def test_student_registration_and_login(self):
        # Register student
        response = self.client.post('/register', data={
            'name': 'Jane Student',
            'register_number': 'REG001',
            'department': 'MCA',
            'email': 'jane@college.edu',
            'password': 'password123'
        }, follow_redirects=True)
        self.assertIn(b'Registration successful', response.data)

        # Login student
        response = self.client.post('/login', data={
            'email_or_reg': 'jane@college.edu',
            'password': 'password123'
        }, follow_redirects=True)
        self.assertIn(b'Welcome back, Jane Student!', response.data)

    def test_admin_login(self):
        response = self.client.post('/admin/login', data={
            'username': 'admin',
            'password': 'admin123'
        }, follow_redirects=True)
        self.assertIn(b'Logged in successfully as Administrator', response.data)

    def test_admin_assignment_crud(self):
        # Admin login
        self.client.post('/admin/login', data={'username': 'admin', 'password': 'admin123'})

        # Add Assignment
        today = date.today().strftime('%Y-%m-%d')
        deadline = (date.today() + timedelta(days=7)).strftime('%Y-%m-%d')
        response = self.client.post('/admin/assignment/add', data={
            'title': 'Algorithm Complexity',
            'subject': 'DSA',
            'description': 'Big-O notation examples',
            'given_date': today,
            'deadline_date': deadline
        }, follow_redirects=True)
        self.assertIn(b'created successfully', response.data)

        # Edit Assignment #1
        response = self.client.post('/admin/assignment/edit/1', data={
            'title': 'Flask Basics & Advanced Routing',
            'subject': 'Web Tech',
            'description': 'Updated description for Flask assignment',
            'given_date': today,
            'deadline_date': deadline
        }, follow_redirects=True)
        self.assertIn(b'updated successfully', response.data)

        # Delete Assignment #2
        response = self.client.post('/admin/assignment/delete/2', follow_redirects=True)
        self.assertIn(b'deleted successfully', response.data)

    def test_student_submission_workflow_and_status(self):
        # Register & Login Student
        self.client.post('/register', data={
            'name': 'Bob Smith',
            'register_number': 'REG002',
            'department': 'MCA',
            'email': 'bob@college.edu',
            'password': 'password123'
        })
        self.client.post('/login', data={'email_or_reg': 'REG002', 'password': 'password123'})

        # Submit Assignment #1 (On-time -> deadline in future)
        response = self.client.post('/student/submit/1', data={
            'submission_text': 'https://github.com/bob/flask-assignment'
        }, follow_redirects=True)
        self.assertIn(b'Assignment submitted successfully! Status: Submitted', response.data)

        # Submit Assignment #2 (Late -> deadline in past)
        response = self.client.post('/student/submit/2', data={
            'submission_text': 'Completed SQL Normalization writeup.'
        }, follow_redirects=True)
        self.assertIn(b'Assignment submitted successfully! Status: Late', response.data)

        # Check Submission History
        response = self.client.get('/student/history')
        self.assertIn(b'Submitted Late', response.data)

    def test_deadline_status_calculator(self):
        today = date.today()
        upcoming = get_deadline_status(today + timedelta(days=5))
        self.assertEqual(upcoming['label'], 'Upcoming')

        due_soon = get_deadline_status(today + timedelta(days=1))
        self.assertEqual(due_soon['label'], 'Due Soon')

        passed = get_deadline_status(today - timedelta(days=2))
        self.assertEqual(passed['label'], 'Deadline Passed')

if __name__ == '__main__':
    unittest.main()
