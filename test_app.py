import unittest
from datetime import date
from app import app, db, Student, RecruitmentDrive, Registration, Admin

class CampusRecruitmentTestCase(unittest.TestCase):
    def setUp(self):
        app.config['TESTING'] = True
        app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
        app.config['WTF_CSRF_ENABLED'] = False
        self.client = app.test_client()

        with app.app_context():
            db.create_all()

            # Seed admin
            admin = Admin(username='admin')
            admin.set_password('admin123')
            db.session.add(admin)

            # Seed sample drive
            self.drive1 = RecruitmentDrive(
                company_name='TechCorp',
                job_role='Software Engineer',
                eligibility='B.Tech CS/IT',
                package='$12,000',
                drive_date=date(2025, 12, 1),
                location='Main Auditorium',
                description='Python and Flask developer'
            )
            db.session.add(self.drive1)
            db.session.commit()

    def tearDown(self):
        with app.app_context():
            db.session.remove()
            db.drop_all()

    def test_student_registration_and_login(self):
        # Register student
        response = self.client.post('/register', data={
            'name': 'John Doe',
            'register_number': 'REG101',
            'department': 'Computer Science & Engineering',
            'email': 'john@student.edu',
            'phone_number': '9876543210',
            'password': 'password123'
        }, follow_redirects=True)
        self.assertIn(b'Registration successful', response.data)

        # Login student
        response = self.client.post('/login', data={
            'email_or_reg': 'john@student.edu',
            'password': 'password123'
        }, follow_redirects=True)
        self.assertIn(b'Welcome back, John Doe!', response.data)

    def test_admin_login(self):
        response = self.client.post('/admin/login', data={
            'username': 'admin',
            'password': 'admin123'
        }, follow_redirects=True)
        self.assertIn(b'Logged in successfully as Admin', response.data)

    def test_drive_registration_workflow(self):
        # Register student
        self.client.post('/register', data={
            'name': 'Alice',
            'register_number': 'REG102',
            'department': 'Information Technology',
            'email': 'alice@student.edu',
            'phone_number': '9876543211',
            'password': 'pass'
        })
        # Login student
        self.client.post('/login', data={
            'email_or_reg': 'REG102',
            'password': 'pass'
        })

        # Register for drive
        response = self.client.post('/drives/1/register', follow_redirects=True)
        self.assertIn(b'Successfully registered', response.data)

        # Attempt double registration
        response = self.client.post('/drives/1/register', follow_redirects=True)
        self.assertIn(b'already registered', response.data)

        # Admin login and update status to Selected
        self.client.get('/logout')
        self.client.post('/admin/login', data={
            'username': 'admin',
            'password': 'admin123'
        })

        response = self.client.post('/admin/registrations/update-status/1', data={
            'status': 'Selected'
        }, follow_redirects=True)

        with app.app_context():
            reg = Registration.query.get(1)
            self.assertEqual(reg.status, 'Selected')

    def test_admin_add_edit_delete_drive(self):
        # Admin login
        self.client.post('/admin/login', data={
            'username': 'admin',
            'password': 'admin123'
        })

        # Add drive
        response = self.client.post('/admin/drives/add', data={
            'company_name': 'DataWorks',
            'job_role': 'Data Scientist',
            'eligibility': 'MCA / M.Tech',
            'package': '$15,000',
            'drive_date': '2025-11-20',
            'location': 'Virtual',
            'description': 'Data analytics and ML'
        }, follow_redirects=True)
        self.assertIn(b'created successfully', response.data)

        # Edit drive
        response = self.client.post('/admin/drives/edit/2', data={
            'company_name': 'DataWorks Inc',
            'job_role': 'Senior Data Scientist',
            'eligibility': 'MCA / M.Tech',
            'package': '$18,000',
            'drive_date': '2025-11-25',
            'location': 'Virtual',
            'description': 'Updated description'
        }, follow_redirects=True)
        self.assertIn(b'updated successfully', response.data)

        # Delete drive
        response = self.client.post('/admin/drives/delete/2', follow_redirects=True)
        self.assertIn(b'deleted', response.data)

if __name__ == '__main__':
    unittest.main()
