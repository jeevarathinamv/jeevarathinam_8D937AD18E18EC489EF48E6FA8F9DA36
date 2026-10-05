import unittest
from datetime import date
from app import app, db, Student, Admin, Complaint

class WaterComplaintTestCase(unittest.TestCase):
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
        # Register student
        response = self.client.post('/register', data={
            'name': 'Alice Smith',
            'register_number': 'MCA202501',
            'department': 'Computer Applications (MCA)',
            'email': 'alice@college.edu',
            'password': 'password123'
        }, follow_redirects=True)
        self.assertIn(b'Registration successful', response.data)

        # Try duplicate registration
        response = self.client.post('/register', data={
            'name': 'Alice Smith',
            'register_number': 'MCA202501',
            'department': 'Computer Applications (MCA)',
            'email': 'alice@college.edu',
            'password': 'password123'
        }, follow_redirects=True)
        self.assertIn(b'already exists', response.data)

        # Login student
        response = self.client.post('/login', data={
            'email_or_reg': 'alice@college.edu',
            'password': 'password123'
        }, follow_redirects=True)
        self.assertIn(b'Welcome back, Alice Smith!', response.data)

    def test_admin_login(self):
        response = self.client.post('/admin/login', data={
            'username': 'admin',
            'password': 'admin123'
        }, follow_redirects=True)
        self.assertIn(b'Logged in successfully as Administrator', response.data)

    def test_complaint_submission_and_student_isolation(self):
        # Register and login Student 1 (Alice)
        self.client.post('/register', data={
            'name': 'Alice',
            'register_number': 'REG101',
            'department': 'MCA',
            'email': 'alice1@college.edu',
            'password': 'pass'
        })
        self.client.post('/login', data={
            'email_or_reg': 'alice1@college.edu',
            'password': 'pass'
        })

        # Submit Complaint
        response = self.client.post('/student/report-complaint', data={
            'complaint_type': 'No Water',
            'location': '3rd Floor MCA Block',
            'description': 'No water coming from tap since morning.',
            'complaint_date': date.today().isoformat()
        }, follow_redirects=True)
        self.assertIn(b'Complaint submitted successfully', response.data)

        with app.app_context():
            complaint = Complaint.query.first()
            self.assertIsNotNone(complaint)
            self.assertEqual(complaint.complaint_type, 'No Water')
            self.assertTrue(complaint.complaint_id.startswith('CWP-'))

        # Check My Complaints
        response = self.client.get('/student/my-complaints')
        self.assertIn(b'No Water', response.data)
        self.assertIn(b'3rd Floor MCA Block', response.data)

        # Register and login Student 2 (Bob)
        self.client.get('/logout')
        self.client.post('/register', data={
            'name': 'Bob',
            'register_number': 'REG102',
            'department': 'MCA',
            'email': 'bob@college.edu',
            'password': 'pass'
        })
        self.client.post('/login', data={
            'email_or_reg': 'bob@college.edu',
            'password': 'pass'
        })

        # Bob views My Complaints (should NOT see Alice's complaint)
        response = self.client.get('/student/my-complaints')
        self.assertNotIn(b'3rd Floor MCA Block', response.data)

    def test_admin_complaint_management_and_resolved_date(self):
        # Create student and complaint
        with app.app_context():
            student = Student(name='Charlie', register_number='REG103', department='MCA', email='charlie@college.edu')
            student.set_password('pass')
            db.session.add(student)
            db.session.commit()

            c = Complaint(
                complaint_id='CWP-999001',
                student_id=student.id,
                complaint_type='RO Problem',
                location='Hostel B Mess',
                description='RO filter light blinking red.',
                complaint_date=date.today(),
                status='Pending'
            )
            db.session.add(c)
            db.session.commit()
            complaint_id_db = c.id

        # Admin Login
        self.client.post('/admin/login', data={'username': 'admin', 'password': 'admin123'}, follow_redirects=True)

        # Update status to In Progress
        response = self.client.post(f'/admin/update-complaint/{complaint_id_db}', data={
            'status': 'In Progress',
            'admin_remarks': 'Technician assigned.'
        }, follow_redirects=True)
        self.assertIn(b'In Progress', response.data)

        with app.app_context():
            comp = db.session.get(Complaint, complaint_id_db)
            self.assertEqual(comp.status, 'In Progress')
            self.assertIsNone(comp.resolved_date)

        # Update status to Resolved (automatically sets resolved_date)
        response = self.client.post(f'/admin/update-complaint/{complaint_id_db}', data={
            'status': 'Resolved',
            'admin_remarks': 'RO Filter replaced.'
        }, follow_redirects=True)
        self.assertIn(b'Resolved', response.data)

        with app.app_context():
            comp = db.session.get(Complaint, complaint_id_db)
            self.assertEqual(comp.status, 'Resolved')
            self.assertEqual(comp.resolved_date, date.today())
            self.assertEqual(comp.admin_remarks, 'RO Filter replaced.')

        # Delete complaint
        response = self.client.post(f'/admin/delete-complaint/{complaint_id_db}', follow_redirects=True)
        self.assertIn(b'has been deleted successfully', response.data)

        with app.app_context():
            comp = db.session.get(Complaint, complaint_id_db)
            self.assertIsNone(comp)


if __name__ == '__main__':
    unittest.main()
