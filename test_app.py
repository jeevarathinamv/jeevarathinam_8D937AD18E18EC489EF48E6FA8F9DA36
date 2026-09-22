import unittest
from app import app, db, Student, Alumni, MentorshipRequest, CareerGuidance, Admin

class AlumniMentorshipTestCase(unittest.TestCase):
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

    def test_home_page(self):
        response = self.client.get('/')
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Alumni Mentorship', response.data)

    def test_student_registration_and_login(self):
        # Register Student
        response = self.client.post('/student/register', data={
            'name': 'John Doe',
            'register_number': 'REG202501',
            'department': 'Computer Science & Engineering',
            'email': 'john.doe@university.edu',
            'password': 'password123'
        }, follow_redirects=True)
        self.assertIn(b'Student registration successful', response.data)

        # Login Student
        response = self.client.post('/student/login', data={
            'email_or_reg': 'john.doe@university.edu',
            'password': 'password123'
        }, follow_redirects=True)
        self.assertIn(b'Welcome back, John Doe!', response.data)

    def test_alumni_registration_and_login(self):
        # Register Alumni
        response = self.client.post('/alumni/register', data={
            'name': 'Jane Smith',
            'department': 'Computer Science & Engineering',
            'graduation_year': 2020,
            'job_role': 'Senior Software Engineer',
            'company': 'Tech Corp',
            'experience': '3-5 Years',
            'email': 'jane.smith@techcorp.com',
            'password': 'alumnipassword'
        }, follow_redirects=True)
        self.assertIn(b'Alumni registration successful', response.data)

        # Login Alumni
        response = self.client.post('/alumni/login', data={
            'email': 'jane.smith@techcorp.com',
            'password': 'alumnipassword'
        }, follow_redirects=True)
        self.assertIn(b'Welcome back, Jane Smith!', response.data)

    def test_find_mentor_filter(self):
        with app.app_context():
            alumni = Alumni(
                name='David Ray',
                department='Information Technology',
                graduation_year=2019,
                job_role='Data Scientist',
                company='AI Labs',
                experience='5-8 Years',
                email='david@ailabs.com'
            )
            alumni.set_password('pass')
            db.session.add(alumni)
            db.session.commit()

        # Filter by department
        response = self.client.get('/find-mentor?department=Information+Technology')
        self.assertIn(b'David Ray', response.data)

        # Filter by company
        response = self.client.get('/find-mentor?company=AI+Labs')
        self.assertIn(b'Data Scientist', response.data)

    def test_mentorship_request_and_response_flow(self):
        # Setup student & alumni
        with app.app_context():
            student = Student(name='Alice', register_number='REG100', department='IT', email='alice@uni.edu')
            student.set_password('pass')
            alumni = Alumni(name='Bob', department='IT', graduation_year=2018, job_role='DevOps Lead', company='CloudInc', experience='5-8 Years', email='bob@cloud.com')
            alumni.set_password('pass')
            db.session.add_all([student, alumni])
            db.session.commit()
            alumni_id = alumni.id

        # Student logs in
        self.client.post('/student/login', data={'email_or_reg': 'alice@uni.edu', 'password': 'pass'})

        # Send mentorship request
        response = self.client.post('/mentorship-request', data={
            'alumni_id': alumni_id,
            'question': 'How do I get started with DevOps and Kubernetes?'
        }, follow_redirects=True)
        self.assertIn(b'Mentorship request submitted successfully', response.data)

        # Logout student & login alumni
        self.client.get('/logout')
        self.client.post('/alumni/login', data={'email': 'bob@cloud.com', 'password': 'pass'})

        # Respond to request
        response = self.client.post('/mentorship-request/respond/1', data={
            'action': 'accept',
            'response': 'Start with Docker containerization basics and Linux CLI commands.'
        }, follow_redirects=True)
        self.assertIn(b'accepted', response.data)

        with app.app_context():
            m_req = db.session.get(MentorshipRequest, 1)
            self.assertEqual(m_req.status, 'Accepted')
            self.assertIn('Docker containerization', m_req.response)

    def test_career_guidance_post(self):
        with app.app_context():
            alumni = Alumni(name='Carol', department='ECE', graduation_year=2021, job_role='Product Manager', company='Meta', experience='3-5 Years', email='carol@meta.com')
            alumni.set_password('pass')
            db.session.add(alumni)
            db.session.commit()

        # Login alumni
        self.client.post('/alumni/login', data={'email': 'carol@meta.com', 'password': 'pass'})

        # Post career guidance
        response = self.client.post('/career-guidance', data={
            'title': 'Mastering Technical Product Management Interviews',
            'category': 'Interview Tips',
            'content': 'Focus on product design, user metrics, and trade-off analysis.'
        }, follow_redirects=True)
        self.assertIn(b'Career Guidance advice posted successfully', response.data)

        # View career guidance page
        response = self.client.get('/career-guidance?category=Interview+Tips')
        self.assertIn(b'Mastering Technical Product Management Interviews', response.data)

    def test_admin_flow_and_management(self):
        # Admin login
        response = self.client.post('/admin/login', data={
            'username': 'admin',
            'password': 'admin123'
        }, follow_redirects=True)
        self.assertIn(b'Logged in successfully as Administrator', response.data)

        # Admin dashboard
        response = self.client.get('/admin/dashboard')
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Administrator Control Panel', response.data)


if __name__ == '__main__':
    unittest.main()
