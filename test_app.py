import os
import unittest
from app import app, db, Student, Profile, PartnerRequest, Admin

class StudyPartnerTestCase(unittest.TestCase):
    def setUp(self):
        app.config['TESTING'] = True
        app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
        app.config['WTF_CSRF_ENABLED'] = False
        self.client = app.test_client()

        with app.app_context():
            db.drop_all()
            db.create_all()

            # Seed Admin if not exists
            admin = Admin.query.filter_by(username='admin').first()
            if not admin:
                admin = Admin(username='admin', email='admin@studypartner.com')
                admin.set_password('admin123')
                db.session.add(admin)

            # Seed Student 1
            s1 = Student(name='Alice', register_number='REG001', department='Computer Science', email='alice@test.com')
            s1.set_password('pass123')

            # Seed Student 2
            s2 = Student(name='Bob', register_number='REG002', department='Information Technology', email='bob@test.com')
            s2.set_password('pass123')

            db.session.add_all([s1, s2])
            db.session.commit()

            # Seed Profiles
            p1 = Profile(student_id=s1.id, subjects='Python, Flask', skills='Python, SQL', preferred_study_time='Evening (5 PM - 8 PM)', study_mode='Online', short_bio='CS Student')
            p2 = Profile(student_id=s2.id, subjects='Database Management, Web', skills='HTML, CSS, JS', preferred_study_time='Morning (8 AM - 12 PM)', study_mode='Hybrid', short_bio='IT Student')

            db.session.add_all([p1, p2])
            db.session.commit()

    def tearDown(self):
        with app.app_context():
            db.session.remove()
            db.drop_all()

    def test_student_registration_and_login(self):
        # Test Registration
        response = self.client.post('/register', data={
            'name': 'Charlie',
            'register_number': 'REG003',
            'department': 'Computer Applications (MCA)',
            'email': 'charlie@test.com',
            'password': 'password123'
        }, follow_redirects=True)
        self.assertIn(b'Registration successful', response.data)

        # Test Login
        response = self.client.post('/login', data={
            'email_or_reg': 'charlie@test.com',
            'password': 'password123'
        }, follow_redirects=True)
        self.assertIn(b'Welcome back, Charlie!', response.data)

    def test_profile_update(self):
        # Login as Alice
        self.client.post('/login', data={'email_or_reg': 'alice@test.com', 'password': 'pass123'})

        # Update profile
        response = self.client.post('/profile', data={
            'subjects': 'Python, Machine Learning, Data Mining',
            'skills': 'Python, Pandas, Scikit-learn',
            'preferred_study_time': 'Night (8 PM - 11 PM)',
            'study_mode': 'Offline',
            'short_bio': 'ML enthusiast'
        }, follow_redirects=True)

        self.assertIn(b'Your profile has been updated successfully', response.data)

        with app.app_context():
            alice = Student.query.filter_by(email='alice@test.com').first()
            self.assertEqual(alice.profile.study_mode, 'Offline')
            self.assertIn('Machine Learning', alice.profile.subjects)

    def test_find_partner_search(self):
        # Login as Alice
        self.client.post('/login', data={'email_or_reg': 'alice@test.com', 'password': 'pass123'})

        # Search by subject "Database"
        response = self.client.get('/find_partner?subject=Database')
        self.assertIn(b'Bob', response.data)

        # Search by non-matching subject
        response = self.client.get('/find_partner?subject=NonExistentSubject')
        self.assertIn(b'No Matching Study Partners Found', response.data)

    def test_partner_request_workflow(self):
        # Alice logs in and sends request to Bob
        self.client.post('/login', data={'email_or_reg': 'alice@test.com', 'password': 'pass123'})

        response = self.client.post('/send_request/2', data={
            'message': 'Let us study Web and Databases together'
        }, follow_redirects=True)
        self.assertIn(b'Study partner request sent to Bob', response.data)

        # Logout Alice, Login Bob
        self.client.get('/logout')
        self.client.post('/login', data={'email_or_reg': 'bob@test.com', 'password': 'pass123'})

        # Check My Partners received requests
        response = self.client.get('/my_partners')
        self.assertIn(b'Alice', response.data)

        # Accept Request
        response = self.client.post('/request/accept/1', follow_redirects=True)
        self.assertIn(b'You accepted study partner request from Alice', response.data)

        with app.app_context():
            req = db.session.get(PartnerRequest, 1)
            self.assertEqual(req.status, 'Accepted')

    def test_admin_functionality(self):
        # Admin Login
        response = self.client.post('/admin/login', data={
            'username': 'admin',
            'password': 'admin123'
        }, follow_redirects=True)
        self.assertIn(b'Logged in successfully as Administrator', response.data)

        # Check Admin Dashboard
        response = self.client.get('/admin/dashboard')
        self.assertIn(b'Alice', response.data)
        self.assertIn(b'Bob', response.data)

        # Delete Student #2 (Bob)
        response = self.client.post('/admin/student/delete/2', follow_redirects=True)
        self.assertIn(b'deleted successfully', response.data)

        with app.app_context():
            bob = db.session.get(Student, 2)
            self.assertIsNone(bob)

if __name__ == '__main__':
    unittest.main()
