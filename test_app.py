import unittest
from app import app, db, Student, Resume

class ResumeBuilderTestCase(unittest.TestCase):
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
        # Student Registration
        response = self.client.post('/register', data={
            'name': 'Jane Doe',
            'register_number': 'REG202501',
            'email': 'jane@university.edu',
            'password': 'password123'
        }, follow_redirects=True)
        self.assertIn(b'Registration successful', response.data)

        # Student Login using Email
        response = self.client.post('/login', data={
            'login_type': 'student',
            'email_or_reg': 'jane@university.edu',
            'password': 'password123'
        }, follow_redirects=True)
        self.assertIn(b'Welcome back, Jane Doe!', response.data)

        # Logout
        response = self.client.get('/logout', follow_redirects=True)
        self.assertIn(b'You have been logged out', response.data)

        # Student Login using Register Number
        response = self.client.post('/login', data={
            'login_type': 'student',
            'email_or_reg': 'REG202501',
            'password': 'password123'
        }, follow_redirects=True)
        self.assertIn(b'Welcome back, Jane Doe!', response.data)

    def test_admin_login(self):
        response = self.client.post('/login', data={
            'login_type': 'admin',
            'username': 'admin',
            'password': 'admin123'
        }, follow_redirects=True)
        self.assertIn(b'Logged in successfully as Administrator', response.data)

    def test_resume_crud_and_pdf_generation(self):
        # Register and login student
        self.client.post('/register', data={
            'name': 'Alex Smith',
            'register_number': 'REG202502',
            'email': 'alex@university.edu',
            'password': 'pass'
        })
        self.client.post('/login', data={
            'login_type': 'student',
            'email_or_reg': 'alex@university.edu',
            'password': 'pass'
        })

        # Create Resume
        response = self.client.post('/resume/create', data={
            'title': 'Full Stack Developer Resume',
            'full_name': 'Alex Smith',
            'phone': '+1 555-0199',
            'email': 'alex@university.edu',
            'address': 'California, USA',
            'career_objective': 'To build scalable web systems.',
            'education': 'B.S. Computer Science, Stanford University',
            'skills': 'Python, Flask, JavaScript, SQL',
            'projects': 'E-Commerce App - Built with Flask',
            'certifications': 'AWS Developer Associate',
            'hobbies': 'Chess, Coding'
        }, follow_redirects=True)
        self.assertIn(b'Resume created successfully!', response.data)

        # Edit Resume
        response = self.client.post('/resume/edit/1', data={
            'title': 'Senior Developer Resume',
            'full_name': 'Alex Smith',
            'phone': '+1 555-0199',
            'email': 'alex@university.edu',
            'address': 'California, USA',
            'career_objective': 'To lead engineering teams.',
            'education': 'B.S. Computer Science, Stanford University',
            'skills': 'Python, Flask, React, MySQL',
            'projects': 'E-Commerce App - Built with Flask',
            'certifications': 'AWS Developer Associate',
            'hobbies': 'Chess, Swimming'
        }, follow_redirects=True)
        self.assertIn(b'Resume updated successfully!', response.data)

        # HTML Resume View
        response = self.client.get('/resume/view/1')
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Alex Smith', response.data)
        self.assertIn(b'To lead engineering teams.', response.data)

        # PDF Resume Download Route
        response = self.client.get('/resume/download/1')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.headers['Content-Type'], 'application/pdf')
        self.assertTrue(response.data.startswith(b'%PDF'))

        # Delete Resume by Student
        response = self.client.post('/resume/delete/1', follow_redirects=True)
        self.assertIn(b'Resume deleted successfully', response.data)

    def test_admin_dashboard_and_resume_deletion(self):
        # Register student & create resume
        self.client.post('/register', data={
            'name': 'Bob Ross',
            'register_number': 'REG202503',
            'email': 'bob@university.edu',
            'password': 'pass'
        })
        self.client.post('/login', data={
            'login_type': 'student',
            'email_or_reg': 'bob@university.edu',
            'password': 'pass'
        })
        self.client.post('/resume/create', data={
            'title': 'Graphic Designer',
            'full_name': 'Bob Ross',
            'phone': '+1 555-0188',
            'email': 'bob@university.edu',
            'address': 'Florida, USA',
            'career_objective': 'Passionate about painting digital art.',
            'education': 'B.A. Fine Arts',
            'skills': 'Photoshop, Illustrator, Design',
            'projects': '',
            'certifications': '',
            'hobbies': 'Painting'
        })

        # Admin login
        self.client.get('/logout')
        self.client.post('/login', data={
            'login_type': 'admin',
            'username': 'admin',
            'password': 'admin123'
        })

        # View Admin Dashboard
        response = self.client.get('/admin/dashboard')
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Bob Ross', response.data)

        # Admin Delete Resume
        response = self.client.post('/admin/resume/delete/1', follow_redirects=True)
        self.assertIn(b'has been deleted', response.data)

if __name__ == '__main__':
    unittest.main()
