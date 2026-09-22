import unittest
from datetime import date
from app import app, db, Student, Course, Certification

class StudentTrackerTestCase(unittest.TestCase):
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
            'name': 'Alex Student',
            'register_number': 'REG2025001',
            'department': 'Computer Science',
            'email': 'alex@example.com',
            'password': 'password123'
        }, follow_redirects=True)
        self.assertIn(b'Registration successful', response.data)

        # Duplicate registration test
        response_dup = self.client.post('/register', data={
            'name': 'Alex Student 2',
            'register_number': 'REG2025001',
            'department': 'CS',
            'email': 'alex@example.com',
            'password': 'pass'
        }, follow_redirects=True)
        self.assertIn(b'already exists', response_dup.data)

        # Login student
        response = self.client.post('/login', data={
            'email_or_reg': 'alex@example.com',
            'password': 'password123'
        }, follow_redirects=True)
        self.assertIn(b'Welcome back, Alex Student!', response.data)

    def test_admin_login(self):
        response = self.client.post('/admin/login', data={
            'username': 'admin',
            'password': 'admin123'
        }, follow_redirects=True)
        self.assertIn(b'Logged in successfully as Administrator', response.data)

    def test_course_and_certification_workflow(self):
        # 1. Register and Login
        self.client.post('/register', data={
            'name': 'Jane Doe',
            'register_number': 'REG2025002',
            'department': 'Data Science',
            'email': 'jane@example.com',
            'password': 'securepassword'
        })
        self.client.post('/login', data={
            'email_or_reg': 'jane@example.com',
            'password': 'securepassword'
        })

        # 2. Add Course
        response = self.client.post('/courses/add', data={
            'course_name': 'Python & Flask Mastery',
            'course_provider': 'Coursera',
            'course_category': 'Web Development',
            'start_date': date.today().isoformat(),
            'end_date': '',
            'course_status': 'Ongoing',
            'course_link': 'https://coursera.org/example'
        }, follow_redirects=True)
        self.assertIn(b'Course added successfully!', response.data)

        # Verify course in database
        with app.app_context():
            course = db.session.query(Course).filter_by(course_name='Python & Flask Mastery').first()
            self.assertIsNotNone(course)
            self.assertEqual(course.course_status, 'Ongoing')

        # 3. Add Certificate
        response = self.client.post('/certifications/add', data={
            'certificate_name': 'Certified Web Developer',
            'course_name': 'Python & Flask Mastery',
            'issuing_organization': 'Meta',
            'issue_date': date.today().isoformat(),
            'certificate_id': 'CERT-123456',
            'certificate_link': 'https://meta.com/verify/CERT-123456'
        }, follow_redirects=True)
        self.assertIn(b'Certificate added successfully!', response.data)

        # Verify certificate in database
        with app.app_context():
            cert = db.session.query(Certification).filter_by(certificate_name='Certified Web Developer').first()
            self.assertIsNotNone(cert)
            self.assertEqual(cert.issuing_organization, 'Meta')

        # 4. View Dashboard
        dash_resp = self.client.get('/student/dashboard')
        self.assertIn(b'Jane Doe', dash_resp.data)
        self.assertIn(b'Python &amp; Flask Mastery', dash_resp.data)

        # 5. Delete Course
        del_course_resp = self.client.post('/courses/delete/1', follow_redirects=True)
        self.assertIn(b'Course record deleted successfully.', del_course_resp.data)

        # 6. Delete Certificate
        del_cert_resp = self.client.post('/certifications/delete/1', follow_redirects=True)
        self.assertIn(b'Certification record deleted successfully.', del_cert_resp.data)

    def test_admin_dashboard_and_record_management(self):
        # Register student and add items
        self.client.post('/register', data={
            'name': 'Bob Smith',
            'register_number': 'REG2025003',
            'department': 'IT',
            'email': 'bob@example.com',
            'password': 'password123'
        })
        self.client.post('/login', data={
            'email_or_reg': 'bob@example.com',
            'password': 'password123'
        })
        self.client.post('/courses/add', data={
            'course_name': 'Cloud Computing',
            'course_provider': 'AWS',
            'course_category': 'Cloud',
            'start_date': date.today().isoformat(),
            'course_status': 'Completed',
            'course_link': ''
        })

        # Admin login
        self.client.get('/logout')
        self.client.post('/admin/login', data={
            'username': 'admin',
            'password': 'admin123'
        })

        # Access admin dashboard
        response = self.client.get('/admin/dashboard')
        self.assertIn(b'Administrator Control Panel', response.data)
        self.assertIn(b'Bob Smith', response.data)
        self.assertIn(b'Cloud Computing', response.data)

        # Delete student record as admin
        del_resp = self.client.post('/admin/student/delete/1', follow_redirects=True)
        self.assertIn(b'deleted', del_resp.data)

if __name__ == '__main__':
    unittest.main()
