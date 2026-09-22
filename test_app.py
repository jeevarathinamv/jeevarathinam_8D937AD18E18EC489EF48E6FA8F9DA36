import unittest
from datetime import date
from app import app, db, Student, Admin, InternshipApplication, Followup

class InternshipTrackerTestCase(unittest.TestCase):
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
        # Register new student
        response = self.client.post('/register', data={
            'name': 'Alice Smith',
            'register_number': 'REG101',
            'department': 'Master of Computer Applications (MCA)',
            'email': 'alice@college.edu',
            'password': 'password123'
        }, follow_redirects=True)
        self.assertIn(b'Registration successful', response.data)

        # Login student with email
        response = self.client.post('/login', data={
            'email_or_reg': 'alice@college.edu',
            'password': 'password123'
        }, follow_redirects=True)
        self.assertIn(b'Welcome back, Alice Smith!', response.data)

        # Logout
        response = self.client.get('/logout', follow_redirects=True)
        self.assertIn(b'logged out', response.data)

    def test_admin_login(self):
        response = self.client.post('/admin/login', data={
            'username': 'admin',
            'password': 'admin123'
        }, follow_redirects=True)
        self.assertIn(b'Logged in successfully as Admin', response.data)

    def test_application_lifecycle_and_followup(self):
        # Register & Login Student
        self.client.post('/register', data={
            'name': 'Bob Williams',
            'register_number': 'REG102',
            'department': 'Computer Science & Engineering',
            'email': 'bob@college.edu',
            'password': 'password123'
        })
        self.client.post('/login', data={
            'email_or_reg': 'REG102',
            'password': 'password123'
        })

        # Add internship application
        response = self.client.post('/student/application/add', data={
            'company_name': 'Google',
            'role': 'SWE Intern',
            'location': 'Bangalore',
            'application_date': date.today().isoformat(),
            'application_link': 'https://careers.google.com/jobs/123',
            'notes': 'Submitted via portal'
        }, follow_redirects=True)
        self.assertIn(b'Application for SWE Intern at Google added successfully', response.data)

        # Check student dashboard
        response = self.client.get('/student/dashboard')
        self.assertIn(b'Google', response.data)
        self.assertIn(b'SWE Intern', response.data)

        # Add Follow-up
        response = self.client.post('/application/1/followup', data={
            'followup_date': date.today().isoformat(),
            'notes': 'HR responded and scheduled screening call',
            'updated_status': 'Interview Scheduled'
        }, follow_redirects=True)
        self.assertIn(b'Follow-up record added successfully', response.data)

        # Verify application status was updated to Interview Scheduled
        with app.app_context():
            app_item = db.session.get(InternshipApplication, 1)
            self.assertEqual(app_item.status, 'Interview Scheduled')
            self.assertEqual(len(app_item.followups), 1)

        # View Application Details
        response = self.client.get('/application/1')
        self.assertIn(b'Google', response.data)
        self.assertIn(b'HR responded and scheduled screening call', response.data)

    def test_admin_updates_and_remarks(self):
        # Create student and application
        with app.app_context():
            student = Student(
                name='Charlie Brown',
                register_number='REG103',
                department='Information Technology',
                email='charlie@college.edu'
            )
            student.set_password('password123')
            db.session.add(student)
            db.session.commit()

            app_item = InternshipApplication(
                student_id=student.id,
                company_name='Microsoft',
                role='Cloud Intern',
                location='Hyderabad',
                application_date=date.today(),
                status='Applied'
            )
            db.session.add(app_item)
            db.session.commit()

        # Admin login
        self.client.post('/admin/login', data={
            'username': 'admin',
            'password': 'admin123'
        })

        # Admin views dashboard
        response = self.client.get('/admin/dashboard')
        self.assertIn(b'Microsoft', response.data)
        self.assertIn(b'Charlie Brown', response.data)

        # Admin updates application with interview date & remarks
        interview_dt = date.today().isoformat()
        response = self.client.post('/admin/application/update/1', data={
            'status': 'Selected',
            'interview_date': interview_dt,
            'admin_remarks': 'Offered stipend package. Congratulations!'
        }, follow_redirects=True)
        self.assertIn(b'updated successfully', response.data)

        with app.app_context():
            updated_app = db.session.get(InternshipApplication, 1)
            self.assertEqual(updated_app.status, 'Selected')
            self.assertEqual(updated_app.admin_remarks, 'Offered stipend package. Congratulations!')

if __name__ == '__main__':
    unittest.main()
