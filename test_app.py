import unittest
import io
import os
from app import app, db, Student, Admin, Project, seed_default_data

class StudentProjectShowcaseTestCase(unittest.TestCase):
    def setUp(self):
        app.config['TESTING'] = True
        app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
        app.config['WTF_CSRF_ENABLED'] = False
        self.client = app.test_client()

        with app.app_context():
            db.create_all()
            seed_default_data()

    def tearDown(self):
        with app.app_context():
            db.session.remove()
            db.drop_all()

    def test_student_registration_and_login(self):
        # Register student
        response = self.client.post('/register', data={
            'name': 'Anita Roy',
            'register_number': 'MCA202402',
            'department': 'Computer Applications (MCA)',
            'email': 'anita@college.edu',
            'password': 'password123'
        }, follow_redirects=True)
        self.assertIn(b'Registration successful', response.data)

        # Try duplicate registration
        response = self.client.post('/register', data={
            'name': 'Anita Roy Duplicate',
            'register_number': 'MCA202402',
            'department': 'MCA',
            'email': 'anita@college.edu',
            'password': 'password123'
        }, follow_redirects=True)
        self.assertIn(b'already exists', response.data)

        # Login student with Register Number
        response = self.client.post('/login', data={
            'login_input': 'MCA202402',
            'password': 'password123'
        }, follow_redirects=True)
        self.assertIn(b'Welcome back, Anita Roy!', response.data)

        # Logout
        response = self.client.get('/logout', follow_redirects=True)
        self.assertIn(b'logged out', response.data)

        # Login student with Email
        response = self.client.post('/login', data={
            'login_input': 'anita@college.edu',
            'password': 'password123'
        }, follow_redirects=True)
        self.assertIn(b'Welcome back, Anita Roy!', response.data)

    def test_admin_login(self):
        # Invalid credentials
        response = self.client.post('/admin/login', data={
            'username': 'admin',
            'password': 'wrongpassword'
        }, follow_redirects=True)
        self.assertIn(b'Invalid Admin Username or Password', response.data)

        # Valid credentials
        response = self.client.post('/admin/login', data={
            'username': 'admin',
            'password': 'admin123'
        }, follow_redirects=True)
        self.assertIn(b'Logged in successfully as Administrator', response.data)

    def test_project_submission_and_showcase_filtering(self):
        # Register Student 1
        self.client.post('/register', data={
            'name': 'Vijay Kumar',
            'register_number': 'MCA202403',
            'department': 'Computer Applications (MCA)',
            'email': 'vijay@college.edu',
            'password': 'pass'
        })
        self.client.post('/login', data={
            'login_input': 'vijay@college.edu',
            'password': 'pass'
        })

        # Submit a project
        response = self.client.post('/student/add_project', data={
            'title': 'Smart Attendance System',
            'category': 'Python',
            'technologies': 'Python, OpenCV, Flask, MySQL',
            'description': 'Facial recognition attendance system for college classrooms.',
            'project_link': 'https://github.com/example/smart-attendance',
            'project_image': (io.BytesIO(b"fake image data"), "test.png")
        }, follow_redirects=True)
        self.assertIn(b'submitted successfully', response.data)

        # Check My Projects
        response = self.client.get('/student/my_projects')
        self.assertIn(b'Smart Attendance System', response.data)
        self.assertIn(b'Pending', response.data)

        # Verify project is NOT in Public Showcase yet (since it is Pending)
        response = self.client.get('/showcase')
        self.assertNotIn(b'Smart Attendance System', response.data)

        # Admin Login and Approve
        self.client.get('/logout')
        self.client.post('/admin/login', data={'username': 'admin', 'password': 'admin123'})

        response = self.client.post('/admin/project/approve/1', data={
            'admin_remark': 'Excellent project concept!'
        }, follow_redirects=True)
        self.assertIn(b'has been Approved', response.data)

        # Verify project IS NOW in Public Showcase
        response = self.client.get('/showcase')
        self.assertIn(b'Smart Attendance System', response.data)

    def test_ownership_security_prevention(self):
        # Register Student A
        self.client.post('/register', data={
            'name': 'Student A',
            'register_number': 'REG_A',
            'department': 'MCA',
            'email': 'studenta@college.edu',
            'password': 'pass'
        })
        self.client.post('/login', data={'login_input': 'REG_A', 'password': 'pass'})
        self.client.post('/student/add_project', data={
            'title': 'Project A',
            'category': 'Java',
            'technologies': 'Java, Spring Boot',
            'description': 'Student A Project Description'
        })
        self.client.get('/logout')

        # Register Student B
        self.client.post('/register', data={
            'name': 'Student B',
            'register_number': 'REG_B',
            'department': 'MCA',
            'email': 'studentb@college.edu',
            'password': 'pass'
        })
        self.client.post('/login', data={'login_input': 'REG_B', 'password': 'pass'})

        # Student B attempts to edit Student A's project (#1)
        response = self.client.post('/student/edit_project/1', data={
            'title': 'Hacked Title',
            'category': 'Java',
            'technologies': 'Java',
            'description': 'Malicious Edit'
        }, follow_redirects=True)
        self.assertIn(b'Access denied', response.data)

        # Student B attempts to delete Student A's project (#1)
        response = self.client.post('/student/delete_project/1', follow_redirects=True)
        self.assertIn(b'Access denied', response.data)

    def test_admin_rejection_and_student_management(self):
        # Register Student
        self.client.post('/register', data={
            'name': 'Priya Ramesh',
            'register_number': 'MCA202404',
            'department': 'Computer Applications',
            'email': 'priya@college.edu',
            'password': 'pass'
        })
        self.client.post('/login', data={'login_input': 'priya@college.edu', 'password': 'pass'})
        self.client.post('/student/add_project', data={
            'title': 'Data Mining Framework',
            'category': 'Data Science',
            'technologies': 'Python, Pandas, Scikit-learn',
            'description': 'Data mining algorithms visualizer.'
        })
        self.client.get('/logout')

        # Admin login & reject project
        self.client.post('/admin/login', data={'username': 'admin', 'password': 'admin123'})
        response = self.client.post('/admin/project/reject/1', data={
            'admin_remark': 'Please add dataset details to description.'
        }, follow_redirects=True)
        self.assertIn(b'has been Rejected', response.data)

        # Student views remark in My Projects
        self.client.get('/logout')
        self.client.post('/login', data={'login_input': 'priya@college.edu', 'password': 'pass'})
        response = self.client.get('/student/my_projects')
        self.assertIn(b'Please add dataset details to description', response.data)

        # Admin views manage students & deletes student
        self.client.get('/logout')
        self.client.post('/admin/login', data={'username': 'admin', 'password': 'admin123'})
        response = self.client.get('/admin/manage_students')
        self.assertIn(b'Priya Ramesh', response.data)

        response = self.client.post('/admin/student/delete/1', follow_redirects=True)
        self.assertIn(b'deleted', response.data)

if __name__ == '__main__':
    unittest.main()
