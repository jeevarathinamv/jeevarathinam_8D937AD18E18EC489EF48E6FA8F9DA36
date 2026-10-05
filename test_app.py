import unittest
from app import app, db, Admin, Student, Course, Registration

class StudentCourseRegistrationTestCase(unittest.TestCase):
    def setUp(self):
        app.config['TESTING'] = True
        app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
        app.config['WTF_CSRF_ENABLED'] = False
        self.client = app.test_client()

        with app.app_context():
            db.create_all()

            # Seed Admin
            self.admin = Admin(username='admin')
            self.admin.set_password('admin123')

            # Seed Courses
            self.c1 = Course(course_name='Advanced Java Programming', course_code='MCA101', department='Computer Applications (MCA)', semester=1, course_type='Core', credits=4)
            self.c2 = Course(course_name='Database Management Systems', course_code='MCA102', department='Computer Applications (MCA)', semester=1, course_type='Core', credits=4)
            self.c3 = Course(course_name='Software Engineering', course_code='MCA104', department='Computer Applications (MCA)', semester=1, course_type='Elective', credits=3)
            self.c4 = Course(course_name='Python Web Development', course_code='MCA201', department='Computer Applications (MCA)', semester=2, course_type='Core', credits=4)
            self.c5 = Course(course_name='Data Structures', course_code='CSE101', department='Computer Science & Engineering', semester=1, course_type='Core', credits=4)

            db.session.add_all([self.admin, self.c1, self.c2, self.c3, self.c4, self.c5])
            db.session.commit()

    def tearDown(self):
        with app.app_context():
            db.session.remove()
            db.drop_all()

    def test_student_registration_and_login(self):
        # Register student
        response = self.client.post('/register', data={
            'name': 'Rahul Sharma',
            'register_number': '2023MCA101',
            'department': 'Computer Applications (MCA)',
            'year': 1,
            'semester': 1,
            'email': 'rahul@college.edu',
            'password': 'password123'
        }, follow_redirects=True)
        self.assertIn(b'Registration successful', response.data)

        # Login student
        response = self.client.post('/login', data={
            'email_or_reg': '2023MCA101',
            'password': 'password123'
        }, follow_redirects=True)
        self.assertIn(b'Welcome back, Rahul Sharma!', response.data)

    def test_admin_login(self):
        response = self.client.post('/admin/login', data={
            'username': 'admin',
            'password': 'admin123'
        }, follow_redirects=True)
        self.assertIn(b'Logged in successfully as Administrator', response.data)

    def test_course_registration_rules_and_credits(self):
        # Register and login student
        self.client.post('/register', data={
            'name': 'Priya Nair',
            'register_number': '2023MCA102',
            'department': 'Computer Applications (MCA)',
            'year': 1,
            'semester': 1,
            'email': 'priya@college.edu',
            'password': 'pass'
        })
        self.client.post('/login', data={
            'email_or_reg': 'priya@college.edu',
            'password': 'pass'
        })

        # Register Course 1 (MCA101) - Valid
        response = self.client.post('/register_course/1', follow_redirects=True)
        self.assertIn(b'Successfully registered for course', response.data)

        # Try registering same Course 1 again - Prevent duplicate
        response = self.client.post('/register_course/1', follow_redirects=True)
        self.assertIn(b'already registered for', response.data)

        # Try registering Course 4 (MCA201 - Semester 2 course) - Rule check mismatch
        response = self.client.post('/register_course/4', follow_redirects=True)
        self.assertIn(b'belonging to your department and semester', response.data)

        # Try registering Course 5 (CSE101 - CSE Department course) - Rule check mismatch
        response = self.client.post('/register_course/5', follow_redirects=True)
        self.assertIn(b'belonging to your department and semester', response.data)

        # Register Course 2 (MCA102) - Valid
        response = self.client.post('/register_course/2', follow_redirects=True)
        self.assertIn(b'Successfully registered for course', response.data)

        # Verify Total Credits (4 + 4 = 8)
        response = self.client.get('/my_courses')
        self.assertIn(b'Total Credits: 8', response.data)

        # Cancel Course 1
        response = self.client.post('/cancel_course/1', follow_redirects=True)
        self.assertIn(b'cancelled successfully', response.data)

        # Verify Updated Credits after cancellation (8 - 4 = 4)
        response = self.client.get('/my_courses')
        self.assertIn(b'Total Credits: 4', response.data)

    def test_admin_course_management(self):
        # Admin login
        self.client.post('/admin/login', data={
            'username': 'admin',
            'password': 'admin123'
        })

        # Add course
        response = self.client.post('/admin/courses/add', data={
            'course_name': 'Cloud Computing',
            'course_code': 'MCA105',
            'department': 'Computer Applications (MCA)',
            'semester': 1,
            'course_type': 'Elective',
            'credits': 3
        }, follow_redirects=True)
        self.assertIn(b'added successfully', response.data)

        # Edit course
        response = self.client.post('/admin/courses/edit/1', data={
            'course_name': 'Advanced Java Programming (Updated)',
            'course_code': 'MCA101',
            'department': 'Computer Applications (MCA)',
            'semester': 1,
            'course_type': 'Core',
            'credits': 4
        }, follow_redirects=True)
        self.assertIn(b'updated successfully', response.data)

        # Delete course
        response = self.client.post('/admin/courses/delete/3', follow_redirects=True)
        self.assertIn(b'Course deleted successfully', response.data)

if __name__ == '__main__':
    unittest.main()
