import unittest
from app import app, db, Student, Mark, Admin

class StudentMarksTestCase(unittest.TestCase):
    def setUp(self):
        app.config['TESTING'] = True
        app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
        app.config['WTF_CSRF_ENABLED'] = False
        self.client = app.test_client()

        with app.app_context():
            db.create_all()
            # Create default admin
            admin = Admin(username='admin')
            admin.set_password('admin123')
            db.session.add(admin)
            db.session.commit()

    def tearDown(self):
        with app.app_context():
            db.session.remove()
            db.drop_all()

    def test_index_page(self):
        response = self.client.get('/')
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Student Internal Marks', response.data)

    def test_student_registration_and_login(self):
        # Register student
        response = self.client.post('/register', data={
            'name': 'John Doe',
            'register_number': 'REG101',
            'department': 'Computer Science',
            'email': 'john@college.edu',
            'password': 'password123'
        }, follow_redirects=True)
        self.assertIn(b'Registration successful', response.data)

        # Login student with Register Number
        response = self.client.post('/login', data={
            'email_or_reg': 'REG101',
            'password': 'password123'
        }, follow_redirects=True)
        self.assertIn(b'Welcome back, John Doe!', response.data)

    def test_admin_login(self):
        response = self.client.post('/admin/login', data={
            'username': 'admin',
            'password': 'admin123'
        }, follow_redirects=True)
        self.assertIn(b'Logged in successfully as Administrator', response.data)

    def test_admin_add_edit_delete_marks_and_grade_calculation(self):
        # Register a student
        with app.app_context():
            student = Student(
                name='Alice Smith',
                register_number='REG202',
                department='MCA',
                email='alice@college.edu'
            )
            student.set_password('pass123')
            db.session.add(student)
            db.session.commit()

        # Admin Login
        self.client.post('/admin/login', data={
            'username': 'admin',
            'password': 'admin123'
        })

        # Add Marks (25 + 25 + 10 + 5 = 65 -> Grade C, PASS)
        response = self.client.post('/admin/marks/add', data={
            'register_number': 'REG202',
            'subject': 'Python Programming',
            'internal_test_1': 25,
            'internal_test_2': 25,
            'assignment': 10,
            'attendance': 5
        }, follow_redirects=True)
        self.assertIn(b'Marks added successfully', response.data)

        with app.app_context():
            mark = Mark.query.filter_by(register_number='REG202').first()
            self.assertIsNotNone(mark)
            self.assertEqual(mark.total_mark, 65.0)
            self.assertEqual(mark.grade, 'C')
            self.assertEqual(mark.result, '\u2713 Result: PASS')

        # Edit Marks (10 + 10 + 5 + 5 = 30 -> Grade F, FAIL)
        response = self.client.post(f'/admin/marks/edit/{mark.id}', data={
            'subject': 'Python Programming',
            'internal_test_1': 10,
            'internal_test_2': 10,
            'assignment': 5,
            'attendance': 5
        }, follow_redirects=True)
        self.assertIn(b'Marks updated successfully', response.data)

        with app.app_context():
            mark = db.session.get(Mark, mark.id)
            self.assertEqual(mark.total_mark, 30.0)
            self.assertEqual(mark.grade, 'F')
            self.assertEqual(mark.result, '\u26a0 Result: FAIL')

        # Delete Marks
        response = self.client.post(f'/admin/marks/delete/{mark.id}', follow_redirects=True)
        self.assertIn(b'Mark record deleted successfully', response.data)

        with app.app_context():
            mark = db.session.get(Mark, mark.id)
            self.assertIsNone(mark)

    def test_student_dashboard_and_result_view(self):
        # Register and add mark directly
        with app.app_context():
            student = Student(
                name='Bob Brown',
                register_number='REG303',
                department='IT',
                email='bob@college.edu'
            )
            student.set_password('bobpass')
            db.session.add(student)
            db.session.commit()

            mark = Mark(
                student_id=student.id,
                register_number=student.register_number,
                subject='Data Structures',
                internal_test_1=35,
                internal_test_2=35,
                assignment=15,
                attendance=10
            )
            mark.update_totals()
            db.session.add(mark)
            db.session.commit()

        # Login student
        self.client.post('/login', data={
            'email_or_reg': 'bob@college.edu',
            'password': 'bobpass'
        })

        # Check Student Dashboard
        response = self.client.get('/student/dashboard')
        self.assertIn(b'Welcome, Bob Brown!', response.data)
        self.assertIn(b'Data Structures', response.data)
        self.assertIn(b'95.0', response.data) # Total 35+35+15+10=95

        # Check Result Tracker
        response = self.client.get('/result')
        self.assertIn(b'Result Tracker', response.data)
        self.assertIn(b'Grade A+', response.data)

if __name__ == '__main__':
    unittest.main()
