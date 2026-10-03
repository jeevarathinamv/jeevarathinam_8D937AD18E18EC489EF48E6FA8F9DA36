import unittest
from datetime import date, timedelta
from app import app, db, Student, Admin, Workshop, Registration

class WorkshopPortalTestCase(unittest.TestCase):
    def setUp(self):
        app.config['TESTING'] = True
        app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
        app.config['WTF_CSRF_ENABLED'] = False
        self.client = app.test_client()

        with app.app_context():
            db.create_all()

            # Seed Admin
            admin = Admin(username='admin')
            admin.set_password('admin123')
            db.session.add(admin)

            # Seed Workshops
            ws1 = Workshop(
                title='Python Fundamentals',
                description='Learn Python programming',
                category='Python',
                trainer_name='Dr. Smith',
                date=date.today() + timedelta(days=5),
                time='10:00 AM - 12:00 PM',
                venue='Lab 1',
                total_seats=2,
                available_seats=2,
                status='Upcoming'
            )
            ws2 = Workshop(
                title='Web Design with Bootstrap',
                description='Learn Bootstrap 5',
                category='Web Development',
                trainer_name='Prof. Jane',
                date=date.today() - timedelta(days=5),
                time='02:00 PM - 04:00 PM',
                venue='Hall A',
                total_seats=10,
                available_seats=10,
                status='Completed'
            )
            db.session.add_all([ws1, ws2])
            db.session.commit()

    def tearDown(self):
        with app.app_context():
            db.session.remove()
            db.drop_all()

    def test_student_registration_and_login(self):
        # Register Student
        response = self.client.post('/register', data={
            'name': 'Rahul Sharma',
            'register_number': '2024MCA01',
            'department': 'Master of Computer Applications (MCA)',
            'email': 'rahul@college.edu',
            'password': 'password123'
        }, follow_redirects=True)
        self.assertIn(b'Registration successful', response.data)

        # Login with Email
        response = self.client.post('/login', data={
            'login_input': 'rahul@college.edu',
            'password': 'password123'
        }, follow_redirects=True)
        self.assertIn(b'Welcome back, Rahul Sharma!', response.data)

        # Logout
        self.client.get('/logout')

        # Login with Register Number
        response = self.client.post('/login', data={
            'login_input': '2024MCA01',
            'password': 'password123'
        }, follow_redirects=True)
        self.assertIn(b'Welcome back, Rahul Sharma!', response.data)

    def test_admin_login(self):
        response = self.client.post('/admin/login', data={
            'username': 'admin',
            'password': 'admin123'
        }, follow_redirects=True)
        self.assertIn(b'Successfully logged in as Administrator', response.data)

    def test_workshop_registration_workflow_and_seat_deduction(self):
        # Register & Login Student
        self.client.post('/register', data={
            'name': 'Priya Roy',
            'register_number': '2024MCA02',
            'department': 'MCA',
            'email': 'priya@college.edu',
            'password': 'pass'
        })
        self.client.post('/login', data={
            'login_input': 'priya@college.edu',
            'password': 'pass'
        })

        # Register for Workshop 1 (Python)
        response = self.client.post('/workshop/1/register', follow_redirects=True)
        self.assertIn(b'successfully registered', response.data)

        # Verify seat count reduced to 1
        with app.app_context():
            ws = Workshop.query.get(1)
            self.assertEqual(ws.available_seats, 1)

        # Duplicate registration attempt
        response = self.client.post('/workshop/1/register', follow_redirects=True)
        self.assertIn(b'already registered', response.data)

        # Cancel Registration
        response = self.client.post('/workshop/1/cancel', follow_redirects=True)
        self.assertIn(b'has been cancelled', response.data)

        # Verify seat count restored to 2
        with app.app_context():
            ws = Workshop.query.get(1)
            self.assertEqual(ws.available_seats, 2)

    def test_admin_workshop_crud(self):
        # Admin login
        self.client.post('/admin/login', data={
            'username': 'admin',
            'password': 'admin123'
        })

        # Add Workshop
        response = self.client.post('/admin/workshops/add', data={
            'title': 'Data Science with Pandas',
            'description': 'Introduction to pandas',
            'category': 'Data Science',
            'trainer_name': 'Dr. K. Kumar',
            'date': (date.today() + timedelta(days=10)).strftime('%Y-%m-%d'),
            'time': '10:00 AM - 01:00 PM',
            'venue': 'Lab 2',
            'total_seats': 25,
            'status': 'Upcoming'
        }, follow_redirects=True)
        self.assertIn(b'created successfully', response.data)

        # Edit Workshop
        response = self.client.post('/admin/workshops/edit/3', data={
            'title': 'Advanced Data Science with Pandas',
            'description': 'Advanced pandas features',
            'category': 'Data Science',
            'trainer_name': 'Dr. K. Kumar',
            'date': (date.today() + timedelta(days=10)).strftime('%Y-%m-%d'),
            'time': '10:00 AM - 01:00 PM',
            'venue': 'Lab 2',
            'total_seats': 30,
            'status': 'Upcoming'
        }, follow_redirects=True)
        self.assertIn(b'updated successfully', response.data)

        # Delete Workshop
        response = self.client.post('/admin/workshops/delete/3', follow_redirects=True)
        self.assertIn(b'deleted successfully', response.data)

if __name__ == '__main__':
    unittest.main()
