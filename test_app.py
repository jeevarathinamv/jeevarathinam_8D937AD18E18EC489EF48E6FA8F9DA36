import unittest
from datetime import date
from app import app, db, Admin, Customer, Service, Booking, seed_default_data


class ServiceBookingTestCase(unittest.TestCase):
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

    def test_customer_registration_and_login(self):
        # Register customer
        response = self.client.post('/register', data={
            'name': 'John Doe',
            'phone': '9876543210',
            'email': 'john@example.com',
            'password': 'password123'
        }, follow_redirects=True)
        self.assertIn(b'Registration successful', response.data)

        # Login customer
        response = self.client.post('/login', data={
            'email': 'john@example.com',
            'password': 'password123'
        }, follow_redirects=True)
        self.assertIn(b'Welcome back, John Doe!', response.data)

    def test_admin_login(self):
        response = self.client.post('/admin/login', data={
            'username': 'admin',
            'password': 'admin123'
        }, follow_redirects=True)
        self.assertIn(b'Logged in successfully as Administrator', response.data)

    def test_service_crud_operations(self):
        # Admin login
        self.client.post('/admin/login', data={
            'username': 'admin',
            'password': 'admin123'
        })

        # Add new service
        response = self.client.post('/admin/services/add', data={
            'name': 'Window Cleaning',
            'description': 'Glass window exterior and interior cleaning',
            'price': '40.00',
            'duration': '1 Hour',
            'availability': 'Available'
        }, follow_redirects=True)
        self.assertIn(b'Window Cleaning', response.data)

        # Edit service
        with app.app_context():
            srv = Service.query.filter_by(name='Window Cleaning').first()
            srv_id = srv.id

        response = self.client.post(f'/admin/services/edit/{srv_id}', data={
            'name': 'Premium Window Cleaning',
            'description': 'Glass window exterior and interior cleaning with streak-free polish',
            'price': '45.00',
            'duration': '1.5 Hours',
            'availability': 'Available'
        }, follow_redirects=True)
        self.assertIn(b'Premium Window Cleaning', response.data)

        # Delete service
        response = self.client.post(f'/admin/services/delete/{srv_id}', follow_redirects=True)
        self.assertIn(b'deleted successfully', response.data)

    def test_booking_workflow_and_admin_status_update(self):
        # Register and login customer
        self.client.post('/register', data={
            'name': 'Alice Smith',
            'phone': '5551234567',
            'email': 'alice@example.com',
            'password': 'mypassword'
        })
        self.client.post('/login', data={
            'email': 'alice@example.com',
            'password': 'mypassword'
        })

        # Book service #1 (seeded service)
        today_str = date.today().isoformat()
        response = self.client.post('/book-service', data={
            'service_id': 1,
            'preferred_date': today_str,
            'preferred_time': '10:00 AM - 11:00 AM',
            'customer_name': 'Alice Smith',
            'customer_phone': '5551234567',
            'notes': 'Please ring the doorbell upon arrival.'
        }, follow_redirects=True)
        self.assertIn(b'submitted successfully', response.data)

        # Verify booking in customer dashboard / my bookings
        response = self.client.get('/my-bookings')
        self.assertIn(b'Deep House Cleaning', response.data)
        self.assertIn(b'Pending', response.data)

        # Admin login and update booking status to Confirmed then Completed
        self.client.get('/logout')
        self.client.post('/admin/login', data={
            'username': 'admin',
            'password': 'admin123'
        })

        # Confirm booking #1
        response = self.client.post('/admin/bookings/confirm/1', follow_redirects=True)
        self.assertIn(b'confirmed', response.data)

        # Complete booking #1
        response = self.client.post('/admin/bookings/complete/1', follow_redirects=True)
        self.assertIn(b'Completed', response.data)

    def test_admin_customer_search_and_filter(self):
        # Register customer
        self.client.post('/register', data={
            'name': 'Bob Marley',
            'phone': '1112223333',
            'email': 'bob@reggae.com',
            'password': 'password123'
        })

        # Admin login
        self.client.post('/admin/login', data={
            'username': 'admin',
            'password': 'admin123'
        })

        # Search customer by name
        response = self.client.get('/admin/customers?q=Bob')
        self.assertIn(b'Bob Marley', response.data)

        # Search non-existing customer
        response = self.client.get('/admin/customers?q=NonExistent')
        self.assertIn(b'No customer profiles found', response.data)


if __name__ == '__main__':
    unittest.main()
