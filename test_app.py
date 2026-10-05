import unittest
from datetime import date
from app import app, db, Student, Admin, Complaint

class ClassroomMaintenanceTestCase(unittest.TestCase):
    def setUp(self):
        app.config['TESTING'] = True
        app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
        app.config['WTF_CSRF_ENABLED'] = False
        app.config['SECRET_KEY'] = 'test_secret_key'
        self.client = app.test_client()

        with app.app_context():
            db.create_all()
            # Seed admin
            admin = Admin(username='admin')
            admin.set_password('admin123')
            db.session.add(admin)

            # Seed student
            student = Student(
                name='Alice Smith',
                register_number='23MCA001',
                department='MCA',
                email='alice@college.edu'
            )
            student.set_password('password123')
            db.session.add(student)
            db.session.commit()

    def tearDown(self):
        with app.app_context():
            db.session.remove()
            db.drop_all()

    def test_student_registration(self):
        response = self.client.post('/register', data={
            'name': 'Bob Johnson',
            'register_number': '23MCA002',
            'department': 'MCA',
            'email': 'bob@college.edu',
            'password': 'password123'
        }, follow_redirects=True)
        self.assertIn(b'Registration successful', response.data)

        # Duplicate check
        response_dup = self.client.post('/register', data={
            'name': 'Bob Johnson Duplicate',
            'register_number': '23MCA002',
            'department': 'MCA',
            'email': 'bob@college.edu',
            'password': 'password123'
        }, follow_redirects=True)
        self.assertIn(b'already exists', response_dup.data)

    def test_student_login_and_logout(self):
        # Successful login
        response = self.client.post('/login', data={
            'email_or_reg': '23MCA001',
            'password': 'password123'
        }, follow_redirects=True)
        self.assertIn(b'Welcome back, Alice Smith!', response.data)

        # Logout
        response_logout = self.client.get('/logout', follow_redirects=True)
        self.assertIn(b'logged out successfully', response_logout.data)

    def test_admin_login(self):
        response = self.client.post('/admin/login', data={
            'username': 'admin',
            'password': 'admin123'
        }, follow_redirects=True)
        self.assertIn(b'Logged in successfully as Administrator', response.data)

    def test_complaint_submission_and_student_isolation(self):
        # Login student Alice
        self.client.post('/login', data={
            'email_or_reg': 'alice@college.edu',
            'password': 'password123'
        })

        # Submit complaint
        response = self.client.post('/report-complaint', data={
            'classroom_number': 'Room 101',
            'complaint_type': 'Fan Problem',
            'description': 'Ceiling fan is making heavy noise and vibrating.',
            'complaint_date': date.today().isoformat()
        }, follow_redirects=True)
        self.assertIn(b'Complaint submitted successfully', response.data)

        # Register and login second student Bob
        self.client.get('/logout')
        self.client.post('/register', data={
            'name': 'Bob',
            'register_number': '23MCA002',
            'department': 'MCA',
            'email': 'bob@college.edu',
            'password': 'pass'
        })
        self.client.post('/login', data={
            'email_or_reg': 'bob@college.edu',
            'password': 'pass'
        })

        # Check Bob's dashboard & complaints list
        response_bob_complaints = self.client.get('/my-complaints')
        self.assertNotIn(b'Room 101', response_bob_complaints.data)
        self.assertIn(b'No Complaints Found', response_bob_complaints.data)

        # Bob attempts to view Alice's complaint details directly
        response_unauthorized = self.client.get('/complaint/1', follow_redirects=True)
        self.assertIn(b'Access denied', response_unauthorized.data)

    def test_admin_complaint_management_and_status_update(self):
        # Login Alice and report complaint
        self.client.post('/login', data={
            'email_or_reg': 'alice@college.edu',
            'password': 'password123'
        })
        self.client.post('/report-complaint', data={
            'classroom_number': 'Lab 3',
            'complaint_type': 'Projector Problem',
            'description': 'Projector bulb not turning on.',
            'complaint_date': date.today().isoformat()
        })
        self.client.get('/logout')

        # Login Admin
        self.client.post('/admin/login', data={
            'username': 'admin',
            'password': 'admin123'
        })

        # Check admin dashboard & manage complaints
        response_manage = self.client.get('/manage-complaints')
        self.assertIn(b'Lab 3', response_manage.data)
        self.assertIn(b'Projector Problem', response_manage.data)

        # Update status to In Progress
        response_update1 = self.client.post('/admin/complaint/update/1', data={
            'status': 'In Progress',
            'admin_remarks': 'Technician assigned.'
        }, follow_redirects=True)
        self.assertIn(b'updated successfully', response_update1.data)

        # Update status to Resolved and verify resolved_date auto-population
        response_update2 = self.client.post('/admin/complaint/update/1', data={
            'status': 'Resolved',
            'admin_remarks': 'Projector bulb replaced.'
        }, follow_redirects=True)
        self.assertIn(b'Resolved', response_update2.data)

        with app.app_context():
            c = Complaint.query.get(1)
            self.assertEqual(c.status, 'Resolved')
            self.assertEqual(c.resolved_date, date.today())
            self.assertEqual(c.admin_remarks, 'Projector bulb replaced.')

        # Test search filter
        response_search = self.client.get('/manage-complaints?search=Lab+3')
        self.assertIn(b'Lab 3', response_search.data)

        # Delete complaint
        response_delete = self.client.post('/admin/complaint/delete/1', follow_redirects=True)
        self.assertIn(b'deleted successfully', response_delete.data)

        with app.app_context():
            c = Complaint.query.get(1)
            self.assertIsNone(c)

if __name__ == '__main__':
    unittest.main()
