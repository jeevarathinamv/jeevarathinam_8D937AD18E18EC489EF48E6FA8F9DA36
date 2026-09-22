import unittest
from datetime import date, timedelta
from app import app, db, Student, Admin, LeaveRequest

class StudentLeaveTestCase(unittest.TestCase):
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
            'name': 'Alex Johnson',
            'register_number': 'REG2025001',
            'department': 'Computer Applications (MCA/BCA)',
            'email': 'alex@college.edu',
            'password': 'password123'
        }, follow_redirects=True)
        self.assertIn(b'Registration successful', response.data)

        # Login student
        response = self.client.post('/login', data={
            'email_or_reg': 'alex@college.edu',
            'password': 'password123'
        }, follow_redirects=True)
        self.assertIn(b'Welcome back, Alex Johnson!', response.data)

    def test_admin_login(self):
        response = self.client.post('/admin/login', data={
            'username': 'admin',
            'password': 'admin123'
        }, follow_redirects=True)
        self.assertIn(b'Logged in successfully as Administrator', response.data)

    def test_leave_application_and_approval_workflow(self):
        # Register and login student
        self.client.post('/register', data={
            'name': 'Sam Green',
            'register_number': 'REG2025002',
            'department': 'Information Technology',
            'email': 'sam@college.edu',
            'password': 'pass'
        })
        self.client.post('/login', data={
            'email_or_reg': 'sam@college.edu',
            'password': 'pass'
        })

        # Apply for leave
        today = date.today()
        from_date = today.isoformat()
        to_date = (today + timedelta(days=2)).isoformat()

        response = self.client.post('/student/apply-leave', data={
            'leave_type': 'Medical Leave',
            'from_date': from_date,
            'to_date': to_date,
            'reason': 'Fever and viral infection doctor advised 3 days rest.'
        }, follow_redirects=True)
        self.assertIn(b'Leave request submitted successfully', response.data)

        # Check Leave History
        response = self.client.get('/student/leave-history')
        self.assertIn(b'Medical Leave', response.data)
        self.assertIn(b'Pending', response.data)

        # Admin login and approve leave with reply
        self.client.get('/logout')
        self.client.post('/admin/login', data={
            'username': 'admin',
            'password': 'admin123'
        })

        response = self.client.get('/admin/dashboard')
        self.assertIn(b'Sam Green', response.data)

        # Approve Leave Request #1
        response = self.client.post('/admin/leave/action/1', data={
            'status': 'Approved',
            'admin_reply': 'Approved. Take rest and submit medical certificate upon return.'
        }, follow_redirects=True)
        self.assertIn(b'updated to Approved', response.data)

        with app.app_context():
            req = db.session.get(LeaveRequest, 1)
            self.assertEqual(req.status, 'Approved')
            self.assertEqual(req.admin_reply, 'Approved. Take rest and submit medical certificate upon return.')

if __name__ == '__main__':
    unittest.main()
