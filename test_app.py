import unittest
from app import app, db, Student, Job, Application

class PlacementPortalTestCase(unittest.TestCase):
    def setUp(self):
        app.config['TESTING'] = True
        app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
        app.config['WTF_CSRF_ENABLED'] = False
        self.client = app.test_client()

        with app.app_context():
            db.create_all()
            # Seed job opportunities
            self.job1 = Job(
                company_name='TechSolutions Inc.',
                job_role='Software Engineer Trainee',
                salary_package='6.5 LPA',
                eligibility_criteria='BE/B.Tech/MCA/M.Sc',
                description='Entry level python developer'
            )
            self.job2 = Job(
                company_name='DataDynamics Ltd.',
                job_role='Data Analyst',
                salary_package='5.0 LPA',
                eligibility_criteria='MCA / B.Sc',
                description='Data analysis role'
            )
            db.session.add_all([self.job1, self.job2])
            db.session.commit()

    def tearDown(self):
        with app.app_context():
            db.session.remove()
            db.drop_all()

    def test_student_registration_and_login(self):
        # Register student
        response = self.client.post('/register', data={
            'name': 'Alex Johnson',
            'register_number': 'REG123',
            'department': 'Computer Applications (MCA)',
            'email': 'alex@college.edu',
            'password': 'password123'
        }, follow_redirects=True)
        self.assertIn(b'Registration successful', response.data)

        # Login student
        response = self.client.post('/login', data={
            'login_type': 'student',
            'email_or_reg': 'alex@college.edu',
            'password': 'password123'
        }, follow_redirects=True)
        self.assertIn(b'Welcome back, Alex Johnson!', response.data)

    def test_admin_login(self):
        response = self.client.post('/login', data={
            'login_type': 'admin',
            'username': 'admin',
            'password': 'admin123'
        }, follow_redirects=True)
        self.assertIn(b'Logged in successfully as Administrator', response.data)

    def test_job_application_workflow(self):
        # Register and login student
        self.client.post('/register', data={
            'name': 'Sam',
            'register_number': 'REG456',
            'department': 'MCA',
            'email': 'sam@college.edu',
            'password': 'pass'
        })
        self.client.post('/login', data={
            'login_type': 'student',
            'email_or_reg': 'sam@college.edu',
            'password': 'pass'
        })

        # Submit Job Application
        response = self.client.post('/student/apply/1', follow_redirects=True)
        self.assertIn(b'Successfully applied for Software Engineer Trainee', response.data)

        # Duplicate application attempt
        response = self.client.post('/student/apply/1', follow_redirects=True)
        self.assertIn(b'already applied for this job opportunity', response.data)

        # Admin login & update status to Selected
        self.client.get('/logout')
        self.client.post('/login', data={
            'login_type': 'admin',
            'username': 'admin',
            'password': 'admin123'
        })

        response = self.client.post('/admin/application/update_status/1', data={
            'status': 'Selected'
        }, follow_redirects=True)
        self.assertIn(b'status updated to', response.data)

        with app.app_context():
            application = db.session.get(Application, 1)
            self.assertEqual(application.status, 'Selected')

    def test_admin_job_crud(self):
        # Admin login
        self.client.post('/login', data={
            'login_type': 'admin',
            'username': 'admin',
            'password': 'admin123'
        })

        # Add Job
        response = self.client.post('/admin/job/add', data={
            'company_name': 'Innovate AI',
            'job_role': 'ML Engineer',
            'salary_package': '8.0 LPA',
            'eligibility_criteria': 'MCA/B.Tech CS 70%',
            'description': 'Machine Learning engineer'
        }, follow_redirects=True)
        self.assertIn(b'added successfully', response.data)

        # Edit Job
        response = self.client.post('/admin/job/update/1', data={
            'company_name': 'TechSolutions Updated',
            'job_role': 'Software Development Engineer',
            'salary_package': '7.0 LPA',
            'eligibility_criteria': 'BE/MCA',
            'description': 'Updated details'
        }, follow_redirects=True)
        self.assertIn(b'updated successfully', response.data)

        # Delete Job
        response = self.client.post('/admin/job/delete/2', follow_redirects=True)
        self.assertIn(b'Job opportunity deleted successfully', response.data)

        with app.app_context():
            job = db.session.get(Job, 2)
            self.assertIsNone(job)

if __name__ == '__main__':
    unittest.main()
