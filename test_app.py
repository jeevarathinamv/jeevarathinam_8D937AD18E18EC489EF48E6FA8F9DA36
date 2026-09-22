import unittest
from datetime import date
from app import app, db, Student, Equipment, Booking

class SportsBookingTestCase(unittest.TestCase):
    def setUp(self):
        app.config['TESTING'] = True
        app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
        app.config['WTF_CSRF_ENABLED'] = False
        self.client = app.test_client()

        with app.app_context():
            db.create_all()
            # Seed equipment
            self.eq1 = Equipment(name='Cricket Bat', category='Cricket', total_quantity=5, available_quantity=5, description='Test Bat')
            self.eq2 = Equipment(name='Football', category='Football', total_quantity=2, available_quantity=0, description='Out of stock football')
            db.session.add_all([self.eq1, self.eq2])
            db.session.commit()

    def tearDown(self):
        with app.app_context():
            db.session.remove()
            db.drop_all()

    def test_student_registration_and_login(self):
        # Register student
        response = self.client.post('/register', data={
            'name': 'Alex Johnson',
            'register_number': 'REG123',
            'department': 'Computer Applications (MCA)',
            'email': 'alex@college.edu',
            'password': 'password123'
        }, follow_redirects=True)
        self.assertIn(b'Registration successful', response.data)

        # Login student
        response = self.client.post('/login', data={
            'login_type': 'student',
            'email_or_reg': 'alex@college.edu',
            'password': 'password123'
        }, follow_redirects=True)
        self.assertIn(b'Welcome back, Alex Johnson!', response.data)

    def test_admin_login(self):
        response = self.client.post('/login', data={
            'login_type': 'admin',
            'username': 'admin',
            'password': 'admin123'
        }, follow_redirects=True)
        self.assertIn(b'Logged in successfully as Administrator', response.data)

    def test_booking_workflow_and_stock_validation(self):
        # Register and login student
        self.client.post('/register', data={
            'name': 'Sam',
            'register_number': 'REG456',
            'department': 'MCA',
            'email': 'sam@college.edu',
            'password': 'pass'
        })
        self.client.post('/login', data={
            'login_type': 'student',
            'email_or_reg': 'sam@college.edu',
            'password': 'pass'
        })

        # Try booking out of stock equipment
        response = self.client.post('/student/book', data={
            'equipment_id': 2,
            'booking_date': date.today().isoformat(),
            'quantity': 1
        }, follow_redirects=True)
        self.assertIn(b'out of stock', response.data)

        # Try booking excess quantity
        response = self.client.post('/student/book', data={
            'equipment_id': 1,
            'booking_date': date.today().isoformat(),
            'quantity': 10
        }, follow_redirects=True)
        self.assertIn(b'exceeds available stock', response.data)

        # Successful booking request
        response = self.client.post('/student/book', data={
            'equipment_id': 1,
            'booking_date': date.today().isoformat(),
            'quantity': 2
        }, follow_redirects=True)
        self.assertIn(b'Booking request submitted', response.data)

        # Admin login and approval
        self.client.get('/logout')
        self.client.post('/login', data={
            'login_type': 'admin',
            'username': 'admin',
            'password': 'admin123'
        })

        # Approve booking #1
        response = self.client.post('/admin/booking/approve/1', follow_redirects=True)
        self.assertIn(b'approved successfully', response.data)

        with app.app_context():
            eq = Equipment.query.get(1)
            self.assertEqual(eq.available_quantity, 3) # 5 - 2

        # Return booking #1
        response = self.client.post('/admin/booking/return/1', follow_redirects=True)
        self.assertIn(b'marked as Returned', response.data)

        with app.app_context():
            eq = Equipment.query.get(1)
            self.assertEqual(eq.available_quantity, 5) # Stock returned

if __name__ == '__main__':
    unittest.main()
