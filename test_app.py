import unittest
from app import app, db, Student, Profile, Education, Skill, Project, Certification, Admin

class StudentPortfolioTestCase(unittest.TestCase):
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
            'name': 'Jane Student',
            'register_number': 'REG202401',
            'department': 'Computer Science & Engineering',
            'email': 'jane@student.edu',
            'password': 'password123'
        }, follow_redirects=True)
        self.assertIn(b'Registration successful', response.data)

        # Login student
        response = self.client.post('/login', data={
            'email_or_reg': 'jane@student.edu',
            'password': 'password123'
        }, follow_redirects=True)
        self.assertIn(b'Welcome back, Jane Student!', response.data)

    def test_profile_management(self):
        # Register and login
        self.client.post('/register', data={
            'name': 'Jane Student',
            'register_number': 'REG202401',
            'department': 'Computer Science & Engineering',
            'email': 'jane@student.edu',
            'password': 'password123'
        })
        self.client.post('/login', data={
            'email_or_reg': 'jane@student.edu',
            'password': 'password123'
        })

        # Update profile
        response = self.client.post('/profile', data={
            'name': 'Jane Student Updated',
            'department': 'Computer Science & Engineering',
            'about_me': 'Passionate Python and Web Developer.',
            'career_objective': 'To obtain a Software Engineer role.',
            'hobbies': 'Coding, Reading',
            'phone': '9876543210',
            'address': 'Chennai, India',
            'linkedin_url': 'https://linkedin.com/in/janestudent',
            'github_url': 'https://github.com/janestudent'
        }, follow_redirects=True)
        self.assertIn(b'Profile updated successfully!', response.data)

    def test_crud_education_skills_projects_certifications(self):
        # Register and login
        self.client.post('/register', data={
            'name': 'Alex Coder',
            'register_number': 'REG202402',
            'department': 'Information Technology',
            'email': 'alex@coder.edu',
            'password': 'password123'
        })
        self.client.post('/login', data={
            'email_or_reg': 'alex@coder.edu',
            'password': 'password123'
        })

        # Add Education
        res_edu = self.client.post('/education/add', data={
            'degree': 'B.Tech IT',
            'institution': 'ABC Institute',
            'year_of_passing': '2025',
            'score': '9.0 CGPA'
        }, follow_redirects=True)
        self.assertIn(b'Education details added successfully!', res_edu.data)

        # Add Skill
        res_skill = self.client.post('/skills/add', data={
            'skill_name': 'Python',
            'proficiency': 'Advanced'
        }, follow_redirects=True)
        self.assertIn(b'Skill added successfully!', res_skill.data)

        # Add Project
        res_proj = self.client.post('/projects/add', data={
            'title': 'Portfolio Generator',
            'description': 'A Flask based portfolio generator',
            'technologies_used': 'Python, Flask, Bootstrap, MySQL',
            'project_link': 'https://github.com/alex/portfolio'
        }, follow_redirects=True)
        self.assertIn(b'Project added successfully!', res_proj.data)

        # Add Certification
        res_cert = self.client.post('/certifications/add', data={
            'certificate_title': 'Python Developer Certificate',
            'issuing_organization': 'Coursera',
            'issue_date': 'May 2024',
            'certificate_link': 'https://coursera.org/verify/1234'
        }, follow_redirects=True)
        self.assertIn(b'Certification added successfully!', res_cert.data)

        # View Generated Portfolio Page
        res_port = self.client.get('/portfolio')
        self.assertIn(b'Alex Coder', res_port.data)
        self.assertIn(b'B.Tech IT', res_port.data)
        self.assertIn(b'Python', res_port.data)
        self.assertIn(b'Portfolio Generator', res_port.data)
        self.assertIn(b'Python Developer Certificate', res_port.data)

    def test_admin_workflow(self):
        # Register student
        self.client.post('/register', data={
            'name': 'Student One',
            'register_number': 'REG001',
            'department': 'Mechanical',
            'email': 'student1@test.com',
            'password': 'pass'
        })

        # Admin login
        response = self.client.post('/admin/login', data={
            'username': 'admin',
            'password': 'admin123'
        }, follow_redirects=True)
        self.assertIn(b'Admin login successful!', response.data)

        # Check Admin Dashboard
        res_dash = self.client.get('/admin/dashboard')
        self.assertIn(b'Student One', res_dash.data)
        self.assertIn(b'REG001', res_dash.data)

if __name__ == '__main__':
    unittest.main()
