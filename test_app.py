import unittest
from app import app, db, Student, Admin, Grievance

class GrievancePortalTestCase(unittest.TestCase):
    def setUp(self):
        app.config['TESTING'] = True
        app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
        app.config['WTF_CSRF_ENABLED'] = False
        self.client = app.test_client()

        with app.app_context():
            db.create_all()
            # Seed admin user
            admin = Admin(
                username='admin',
                email='admin@college.edu',
                name='System Administrator'
            )
            admin.set_password('admin123')
            db.session.add(admin)
            db.session.commit()

    def tearDown(self):
        with app.app_context():
            db.session.remove()
            db.drop_all()

    def test_student_registration_and_login(self):
        # Register student
        response = self.client.post('/register', data={
            'name': 'Rahul Sharma',
            'register_number': '21MCA042',
            'department': 'Computer Applications (MCA)',
            'email': 'rahul@college.edu',
            'password': 'password123'
        }, follow_redirects=True)
        self.assertIn(b'Registration successful', response.data)

        # Login student with Email
        response = self.client.post('/login', data={
            'email_or_reg': 'rahul@college.edu',
            'password': 'password123'
        }, follow_redirects=True)
        self.assertIn(b'Welcome back, Rahul Sharma!', response.data)

        # Logout
        self.client.get('/logout')

        # Login student with Register Number
        response = self.client.post('/login', data={
            'email_or_reg': '21MCA042',
            'password': 'password123'
        }, follow_redirects=True)
        self.assertIn(b'Welcome back, Rahul Sharma!', response.data)

    def test_admin_login(self):
        response = self.client.post('/admin/login', data={
            'username': 'admin',
            'password': 'admin123'
        }, follow_redirects=True)
        self.assertIn(b'Logged in successfully as Administrator', response.data)

    def test_grievance_workflow(self):
        # 1. Register and Login Student
        self.client.post('/register', data={
            'name': 'Ananya Roy',
            'register_number': '21CSE015',
            'department': 'Computer Science & Engineering',
            'email': 'ananya@college.edu',
            'password': 'password123'
        })
        self.client.post('/login', data={
            'email_or_reg': 'ananya@college.edu',
            'password': 'password123'
        })

        # 2. Submit Grievance
        response = self.client.post('/student/submit-grievance', data={
            'category': 'Academic',
            'subject': 'Exam Schedule Conflict',
            'description': 'Two major subject exams are scheduled on the same date.'
        }, follow_redirects=True)
        self.assertIn(b'submitted successfully', response.data)

        # 3. View Student Dashboard
        response = self.client.get('/student/dashboard')
        self.assertIn(b'Total Grievances', response.data)
        self.assertIn(b'Exam Schedule Conflict', response.data)

        # 4. View Grievance History and Details
        response = self.client.get('/student/grievance-history')
        self.assertIn(b'#GR-1', response.data)

        response = self.client.get('/student/grievance/1')
        self.assertIn(b'Exam Schedule Conflict', response.data)
        self.assertIn(b'Two major subject exams are scheduled on the same date.', response.data)

        # 5. Admin Login and Review
        self.client.get('/logout')
        self.client.post('/admin/login', data={
            'username': 'admin',
            'password': 'admin123'
        })

        # Admin Dashboard View
        response = self.client.get('/admin/dashboard')
        self.assertIn(b'Ananya Roy', response.data)
        self.assertIn(b'21CSE015', response.data)

        # Admin Reply & Update Status to In Progress
        response = self.client.post('/admin/grievance/reply/1', data={
            'status': 'In Progress',
            'admin_reply': 'We are looking into rescheduling the exam date with HOD.'
        }, follow_redirects=True)
        self.assertIn(b'updated successfully', response.data)

        # Admin Update Status to Resolved
        response = self.client.post('/admin/grievance/reply/1', data={
            'status': 'Resolved',
            'admin_reply': 'Exam schedule conflict resolved. Revised timetable published on notice board.'
        }, follow_redirects=True)
        self.assertIn(b'updated successfully', response.data)

        # 6. Verify Student sees updated reply and Resolved status
        self.client.get('/logout')
        self.client.post('/login', data={
            'email_or_reg': 'ananya@college.edu',
            'password': 'password123'
        })

        response = self.client.get('/student/grievance/1')
        self.assertIn(b'Resolved', response.data)
        self.assertIn(b'Exam schedule conflict resolved', response.data)

    def test_admin_delete_grievance(self):
        # Register and submit grievance
        self.client.post('/register', data={
            'name': 'Karan Singh',
            'register_number': '21ME008',
            'department': 'Mechanical Engineering',
            'email': 'karan@college.edu',
            'password': 'pass'
        })
        self.client.post('/login', data={
            'email_or_reg': 'karan@college.edu',
            'password': 'pass'
        })
        self.client.post('/student/submit-grievance', data={
            'category': 'Hostel',
            'subject': 'Hot Water Facility',
            'description': 'Geyser in Block A second floor is not working.'
        })

        # Admin login and delete grievance
        self.client.get('/logout')
        self.client.post('/admin/login', data={
            'username': 'admin',
            'password': 'admin123'
        })

        response = self.client.post('/admin/grievance/delete/1', follow_redirects=True)
        self.assertIn(b'deleted successfully', response.data)

        with app.app_context():
            self.assertEqual(Grievance.query.count(), 0)

if __name__ == '__main__':
    unittest.main()
