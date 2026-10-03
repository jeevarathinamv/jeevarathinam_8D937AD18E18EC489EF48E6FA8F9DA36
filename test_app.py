import unittest
from datetime import date, time, datetime, timedelta
from app import app, db, Student, Admin, Workshop, Registration, Attendance, generate_registration_id

class StudentWorkshopTestCase(unittest.TestCase):
    def setUp(self):
        app.config['TESTING'] = True
        app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
        app.config['WTF_CSRF_ENABLED'] = False
        self.client = app.test_client()

        with app.app_context():
            db.create_all()

            # Seed default admin
            admin = Admin(username='admin', name='Admin User')
            admin.set_password('admin123')
            db.session.add(admin)

            # Seed sample workshop
            ws1 = Workshop(
                title='Python Flask Workshop',
                description='Learn Python Flask web development.',
                category='Web Development',
                trainer_name='Dr. Smith',
                date=date.today() + timedelta(days=1), # Tomorrow
                start_time=time(10, 0),
                end_time=time(12, 0),
                venue='Hall A',
                total_seats=2, # Small capacity for testing
                registration_deadline=date.today() + timedelta(days=1),
                status='Upcoming'
            )
            db.session.add(ws1)
            db.session.commit()

    def tearDown(self):
        with app.app_context():
            db.session.remove()
            db.drop_all()

    def test_student_registration_and_login(self):
        # Register Student
        response = self.client.post('/register', data={
            'name': 'John Doe',
            'register_number': '21MCA001',
            'department': 'Master of Computer Applications (MCA)',
            'year': '1st Year',
            'email': 'john@college.edu',
            'phone_number': '9876543210',
            'password': 'password123'
        }, follow_redirects=True)
        self.assertIn(b'Student account registered successfully', response.data)

        # Login Student
        response = self.client.post('/login', data={
            'email_or_reg': '21MCA001',
            'password': 'password123'
        }, follow_redirects=True)
        self.assertIn(b'Welcome back, John Doe!', response.data)

    def test_admin_login(self):
        response = self.client.post('/admin/login', data={
            'username': 'admin',
            'password': 'admin123'
        }, follow_redirects=True)
        self.assertIn(b'Successfully authenticated as Administrator', response.data)

    def test_workshop_registration_seats_and_duplicate_prevention(self):
        # Register 2 students
        with app.app_context():
            s1 = Student(name='Alice', register_number='REG01', department='MCA', year='1st Year', email='alice@test.com', phone_number='1234567890')
            s1.set_password('pass')
            s2 = Student(name='Bob', register_number='REG02', department='MCA', year='2nd Year', email='bob@test.com', phone_number='0987654321')
            s2.set_password('pass')
            db.session.add_all([s1, s2])
            db.session.commit()

        # Login Alice
        self.client.post('/login', data={'email_or_reg': 'alice@test.com', 'password': 'pass'})

        # Register Alice for Workshop #1
        response = self.client.post('/workshop/1/register', follow_redirects=True)
        self.assertIn(b'Workshop registration completed successfully', response.data)

        # Check available seats = 1
        with app.app_context():
            ws = Workshop.query.get(1)
            self.assertEqual(ws.available_seats, 1)

        # Attempt duplicate registration by Alice
        response = self.client.post('/workshop/1/register', follow_redirects=True)
        self.assertIn(b'You are already registered for this workshop', response.data)

        # Logout Alice, Login Bob
        self.client.get('/logout')
        self.client.post('/login', data={'email_or_reg': 'bob@test.com', 'password': 'pass'})

        # Register Bob (takes 2nd seat)
        self.client.post('/workshop/1/register', follow_redirects=True)

        with app.app_context():
            ws = Workshop.query.get(1)
            self.assertEqual(ws.available_seats, 0)

    def test_admin_workshop_management_and_attendance(self):
        # Admin Login
        self.client.post('/admin/login', data={'username': 'admin', 'password': 'admin123'})

        # Create new workshop
        response = self.client.post('/admin/workshop/add', data={
            'title': 'AI & Machine Learning',
            'category': 'Data Science',
            'description': 'AI fundamentals workshop.',
            'trainer_name': 'Prof. Alan',
            'venue': 'Lab 1',
            'date': (date.today() + timedelta(days=5)).isoformat(),
            'start_time': '10:00',
            'end_time': '13:00',
            'total_seats': '25',
            'registration_deadline': (date.today() + timedelta(days=4)).isoformat(),
            'status': 'Upcoming'
        }, follow_redirects=True)
        self.assertIn(b'AI &amp; Machine Learning', response.data)

        # Register a student for workshop #1
        with app.app_context():
            st = Student(name='Charlie', register_number='REG03', department='MCA', year='1st Year', email='charlie@test.com', phone_number='1122334455')
            st.set_password('pass')
            db.session.add(st)
            db.session.commit()
            reg = Registration(registration_id='REGWS999', student_id=st.id, workshop_id=1, status='Registered')
            db.session.add(reg)
            db.session.commit()

        # Mark attendance as Present
        response = self.client.post('/admin/attendance/mark/1', data={'status': 'Present'}, follow_redirects=True)
        self.assertIn(b'Attendance for Charlie marked as Present', response.data)

        with app.app_context():
            att = Attendance.query.filter_by(registration_id=1).first()
            self.assertIsNotNone(att)
            self.assertEqual(att.status, 'Present')

    def test_search_and_filter_workshops(self):
        response = self.client.get('/workshops?search=Flask&category=Web+Development')
        self.assertIn(b'Python Flask Workshop', response.data)

        response = self.client.get('/workshops?search=NonExistentTitle')
        self.assertIn(b'No workshops found', response.data)

if __name__ == '__main__':
    unittest.main()
