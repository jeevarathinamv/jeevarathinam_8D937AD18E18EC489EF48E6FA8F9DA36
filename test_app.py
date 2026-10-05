import unittest
from datetime import date
from app import app, db, Student, Department, Faculty, Notice, Admin

class DepartmentInformationSystemTestCase(unittest.TestCase):
    def setUp(self):
        app.config['TESTING'] = True
        app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
        app.config['WTF_CSRF_ENABLED'] = False
        self.client = app.test_client()

        with app.app_context():
            db.create_all()
            # Seed basic department data
            dept = Department(
                id=1,
                name='Department of Computer Applications',
                code='MCA-DEPT',
                head='Dr. S. Ramanathan',
                email='mca.dept@college.edu',
                phone='+91 98765 43210',
                description='Department overview.'
            )
            admin = Admin(username='admin')
            admin.set_password('admin123')
            db.session.add_all([dept, admin])
            db.session.commit()

    def tearDown(self):
        with app.app_context():
            db.session.remove()
            db.drop_all()

    def test_student_registration_and_login(self):
        # Student Registration
        response = self.client.post('/register', data={
            'name': 'John Doe',
            'register_number': 'REG2025001',
            'department': 'Computer Applications',
            'year': 'Second Year',
            'email': 'john.doe@college.edu',
            'password': 'password123'
        }, follow_redirects=True)
        self.assertIn(b'Registration successful', response.data)

        # Student Login
        response = self.client.post('/login', data={
            'email_or_reg': 'john.doe@college.edu',
            'password': 'password123'
        }, follow_redirects=True)
        self.assertIn(b'Welcome back, John Doe!', response.data)

        # View Student Dashboard
        response = self.client.get('/student/dashboard')
        self.assertIn(b'Student Dashboard', response.data)
        self.assertIn(b'REG2025001', response.data)

    def test_admin_login_and_dashboard(self):
        # Admin Login
        response = self.client.post('/admin/login', data={
            'username': 'admin',
            'password': 'admin123'
        }, follow_redirects=True)
        self.assertIn(b'Logged in successfully as Administrator', response.data)

        # Admin Dashboard
        response = self.client.get('/admin/dashboard')
        self.assertIn(b'Admin Dashboard', response.data)

    def test_department_management(self):
        # Admin Login
        self.client.post('/admin/login', data={'username': 'admin', 'password': 'admin123'})

        # Update Department
        response = self.client.post('/admin/department', data={
            'name': 'Department of Advanced Computing',
            'code': 'DAC-2025',
            'head': 'Dr. S. Ramanathan',
            'email': 'dac@college.edu',
            'phone': '+91 98765 00000',
            'description': 'Updated description for department.'
        }, follow_redirects=True)
        self.assertIn(b'Department information updated successfully', response.data)

        # View Department Public Page
        response = self.client.get('/department')
        self.assertIn(b'Department of Advanced Computing', response.data)

    def test_faculty_crud_operations(self):
        # Admin Login
        self.client.post('/admin/login', data={'username': 'admin', 'password': 'admin123'})

        # Add Faculty
        response = self.client.post('/admin/faculty/add', data={
            'name': 'Dr. Alan Turing',
            'faculty_id': 'FAC201',
            'department': 'Computer Applications',
            'designation': 'Professor',
            'email': 'alan.turing@college.edu',
            'phone': '+91 91234 56789'
        }, follow_redirects=True)
        self.assertIn(b'Dr. Alan Turing', response.data)
        self.assertIn(b'added successfully', response.data)

        # View Faculty List
        response = self.client.get('/faculty')
        self.assertIn(b'Dr. Alan Turing', response.data)

        # Edit Faculty
        response = self.client.post('/admin/faculty/edit/1', data={
            'name': 'Dr. Alan M. Turing',
            'faculty_id': 'FAC201',
            'department': 'Computer Applications',
            'designation': 'Professor & HOD',
            'email': 'alan.turing@college.edu',
            'phone': '+91 91234 56789'
        }, follow_redirects=True)
        self.assertIn(b'Faculty details updated successfully', response.data)

        # Delete Faculty
        response = self.client.post('/admin/faculty/delete/1', follow_redirects=True)
        self.assertIn(b'Faculty deleted successfully', response.data)

    def test_notices_crud_operations(self):
        # Admin Login
        self.client.post('/admin/login', data={'username': 'admin', 'password': 'admin123'})

        # Add Notice
        response = self.client.post('/admin/notices/add', data={
            'title': 'Mid-Semester Examination Schedule',
            'notice_date': date.today().isoformat(),
            'description': 'The mid-semester examinations will begin next week. Please check timetable.'
        }, follow_redirects=True)
        self.assertIn(b'Notice published successfully', response.data)

        # View Public Notices Page
        response = self.client.get('/notices')
        self.assertIn(b'Mid-Semester Examination Schedule', response.data)

        # Edit Notice
        response = self.client.post('/admin/notices/edit/1', data={
            'title': 'Updated Mid-Semester Examination Schedule',
            'notice_date': date.today().isoformat(),
            'description': 'Revised timetable released. Check department board.'
        }, follow_redirects=True)
        self.assertIn(b'Notice updated successfully', response.data)

        # Delete Notice
        response = self.client.post('/admin/notices/delete/1', follow_redirects=True)
        self.assertIn(b'Notice deleted successfully', response.data)

if __name__ == '__main__':
    unittest.main()
