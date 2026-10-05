import unittest
from datetime import date
from app import app, db, Student, Room, Allocation, Admin

class HostelAllocationTestCase(unittest.TestCase):
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

            # Seed Room
            room1 = Room(room_number='A-101', hostel_name='Boys Hostel Block A', room_type='Single', capacity=1, available_beds=1)
            room2 = Room(room_number='A-102', hostel_name='Boys Hostel Block A', room_type='Double', capacity=2, available_beds=2)

            db.session.add_all([admin, room1, room2])
            db.session.commit()

    def tearDown(self):
        with app.app_context():
            db.session.remove()
            db.drop_all()

    def test_student_registration_and_login(self):
        # Register student
        response = self.client.post('/register', data={
            'name': 'John Doe',
            'register_number': 'REG101',
            'department': 'Computer Applications',
            'email': 'john@college.edu',
            'password': 'password123'
        }, follow_redirects=True)
        self.assertIn(b'Registration successful', response.data)

        # Login student
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
        self.assertIn(b'Logged in successfully as Administrator', response.data)

    def test_room_management(self):
        # Admin login
        self.client.post('/admin/login', data={'username': 'admin', 'password': 'admin123'})

        # Add room
        response = self.client.post('/admin/rooms/add', data={
            'hostel_name': 'Girls Hostel Block B',
            'room_number': 'B-201',
            'room_type': 'Single',
            'capacity': 1
        }, follow_redirects=True)
        self.assertIn(b'Room B-201 added successfully', response.data)

        # Edit room
        response = self.client.post('/admin/rooms/edit/1', data={
            'hostel_name': 'Boys Hostel Block A',
            'room_number': 'A-101-Updated',
            'room_type': 'Single',
            'capacity': 1,
            'available_beds': 1
        }, follow_redirects=True)
        self.assertIn(b'updated successfully', response.data)

    def test_room_allocation_and_bed_auto_update(self):
        # Register student
        self.client.post('/register', data={
            'name': 'Jane Smith',
            'register_number': 'REG102',
            'department': 'MCA',
            'email': 'jane@college.edu',
            'password': 'password123'
        })

        # Admin login
        self.client.post('/admin/login', data={'username': 'admin', 'password': 'admin123'})

        # Allocate room A-101 (Single, 1 bed)
        response = self.client.post('/admin/allocate', data={
            'student_id': 1,
            'room_id': 1,
            'allocation_date': date.today().isoformat()
        }, follow_redirects=True)
        self.assertIn(b'successfully allocated', response.data)

        # Verify bed capacity decreased
        with app.app_context():
            room = db.session.get(Room, 1)
            self.assertEqual(room.available_beds, 0)

        # Try allocating same student again (should fail)
        response = self.client.post('/admin/allocate', data={
            'student_id': 1,
            'room_id': 2,
            'allocation_date': date.today().isoformat()
        }, follow_redirects=True)
        self.assertIn(b'already has an active room allocation', response.data)

        # Register second student
        self.client.post('/register', data={
            'name': 'Bob Mark',
            'register_number': 'REG103',
            'department': 'MCA',
            'email': 'bob@college.edu',
            'password': 'password123'
        })

        # Try allocating room A-101 with 0 available beds (should fail)
        response = self.client.post('/admin/allocate', data={
            'student_id': 2,
            'room_id': 1,
            'allocation_date': date.today().isoformat()
        }, follow_redirects=True)
        self.assertIn(b'has no available beds', response.data)

        # Cancel allocation #1 and verify bed count increases back
        response = self.client.post('/admin/allocations/cancel/1', follow_redirects=True)
        self.assertIn(b'cancelled', response.data)

        with app.app_context():
            room = db.session.get(Room, 1)
            self.assertEqual(room.available_beds, 1)

if __name__ == '__main__':
    unittest.main()
