import unittest
from app import app, db, Student, Subject, Registration, Admin

class StudentSubjectRegistrationTestCase(unittest.TestCase):
    def setUp(self):
        app.config['TESTING'] = True
        app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
        app.config['WTF_CSRF_ENABLED'] = False
        self.client = app.test_client()

        with app.app_context():
            db.create_all()

            # Seed Admin if not present
            if not Admin.query.filter_by(username='admin').first():
                admin = Admin(username='admin')
                admin.set_password('admin123')
                db.session.add(admin)

            # Seed Subjects
            if not Subject.query.filter_by(subject_code='MCA101').first():
                subj1 = Subject(subject_name='Advanced Java', subject_code='MCA101', department='Computer Applications', semester=1, subject_type='Core', credits=4)
                subj2 = Subject(subject_name='DBMS', subject_code='MCA102', department='Computer Applications', semester=1, subject_type='Core', credits=4)
                subj3 = Subject(subject_name='Data Structures', subject_code='CS101', department='Computer Science', semester=1, subject_type='Core', credits=4)
                db.session.add_all([subj1, subj2, subj3])

            db.session.commit()

    def tearDown(self):
        with app.app_context():
            db.session.remove()
            db.drop_all()

    def test_student_registration_and_login(self):
        # Register Student
        response = self.client.post('/register', data={
            'student_name': 'John Doe',
            'register_number': 'REG202501',
            'department': 'Computer Applications',
            'year': 1,
            'semester': 1,
            'email': 'john@college.edu',
            'password': 'password123'
        }, follow_redirects=True)
        self.assertIn(b'Registration successful', response.data)

        # Login Student
        response = self.client.post('/login', data={
            'email_or_reg': 'john@college.edu',
            'password': 'password123'
        }, follow_redirects=True)
        self.assertIn(b'Welcome back, John Doe!', response.data)

    def test_admin_login(self):
        response = self.client.post('/admin/login', data={
            'username': 'admin',
            'password': 'admin123'
        }, follow_redirects=True)
        self.assertIn(b'Logged in successfully as Admin', response.data)

    def test_subject_registration_workflow(self):
        # Register & Login Student
        self.client.post('/register', data={
            'student_name': 'Alice Smith',
            'register_number': 'REG202502',
            'department': 'Computer Applications',
            'year': 1,
            'semester': 1,
            'email': 'alice@college.edu',
            'password': 'password123'
        })
        self.client.post('/login', data={
            'email_or_reg': 'alice@college.edu',
            'password': 'password123'
        })

        # Register for Subject 1 (MCA101 - 4 credits)
        response = self.client.post('/student/register_subject/1', follow_redirects=True)
        self.assertIn(b'Successfully registered for Advanced Java', response.data)

        # Prevent duplicate registration
        response = self.client.post('/student/register_subject/1', follow_redirects=True)
        self.assertIn(b'already registered for Advanced Java', response.data)

        # Try registering for subject in different department (CS101)
        response = self.client.post('/student/register_subject/3', follow_redirects=True)
        self.assertIn(b'You can only register for subjects in your department and semester', response.data)

        # View My Registered Subjects & check total credits
        response = self.client.get('/student/my_subjects')
        self.assertIn(b'Total Registered Credits:', response.data)

        # Cancel registration
        response = self.client.post('/student/cancel_registration/1', follow_redirects=True)
        self.assertIn(b'Registration for Advanced Java has been cancelled', response.data)

    def test_admin_subject_and_student_management(self):
        # Admin Login
        self.client.post('/admin/login', data={
            'username': 'admin',
            'password': 'admin123'
        })

        # Add new subject
        response = self.client.post('/admin/subjects/add', data={
            'subject_name': 'Web Tech Lab',
            'subject_code': 'MCA103',
            'department': 'Computer Applications',
            'semester': 1,
            'subject_type': 'Practical',
            'credits': 2
        }, follow_redirects=True)
        self.assertIn(b'added successfully', response.data)

        # Edit subject
        response = self.client.post('/admin/subjects/edit/1', data={
            'subject_name': 'Advanced Java Programming',
            'subject_code': 'MCA101',
            'department': 'Computer Applications',
            'semester': 1,
            'subject_type': 'Core',
            'credits': 4
        }, follow_redirects=True)
        self.assertIn(b'updated successfully', response.data)

        # Delete subject
        response = self.client.post('/admin/subjects/delete/2', follow_redirects=True)
        self.assertIn(b'Subject deleted successfully', response.data)

if __name__ == '__main__':
    unittest.main()
