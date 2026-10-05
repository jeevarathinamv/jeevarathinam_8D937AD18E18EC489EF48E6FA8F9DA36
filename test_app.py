import unittest
from datetime import date
from app import app, db, Admin, Student, Room, RoomAllocation, RoomChangeRequest, get_student_active_allocation

class HostelRoomChangeTestCase(unittest.TestCase):
    def setUp(self):
        app.config['TESTING'] = True
        app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
        app.config['WTF_CSRF_ENABLED'] = False
        self.client = app.test_client()

        with app.app_context():
            db.drop_all()
            db.create_all()

            # Seed admin
            admin = Admin(username='admin')
            admin.set_password('admin123')
            db.session.add(admin)

            # Seed rooms
            self.room1 = Room(room_number='101', hostel_name='A Block', room_type='Double', capacity=2, available_beds=1)
            self.room2 = Room(room_number='102', hostel_name='A Block', room_type='Single', capacity=1, available_beds=1)
            self.room3 = Room(room_number='201', hostel_name='B Block', room_type='Double', capacity=2, available_beds=0) # Full room
            db.session.add_all([self.room1, self.room2, self.room3])
            db.session.commit()

            # Store IDs for tests
            self.room1_id = self.room1.id
            self.room2_id = self.room2.id
            self.room3_id = self.room3.id

    def tearDown(self):
        with app.app_context():
            db.session.remove()
            db.drop_all()

    def test_student_registration_and_login(self):
        # Register student
        response = self.client.post('/register', data={
            'name': 'Rahul Sharma',
            'register_number': 'MCA202401',
            'department': 'Master of Computer Applications',
            'email': 'rahul@college.edu',
            'password': 'password123'
        }, follow_redirects=True)
        self.assertIn(b'Registration successful', response.data)

        # Login student
        response = self.client.post('/login', data={
            'email_or_reg': 'rahul@college.edu',
            'password': 'password123'
        }, follow_redirects=True)
        self.assertIn(b'Welcome, Rahul Sharma!', response.data)

    def test_admin_login(self):
        response = self.client.post('/admin/login', data={
            'username': 'admin',
            'password': 'admin123'
        }, follow_redirects=True)
        self.assertIn(b'Logged in successfully as Administrator', response.data)

    def test_room_change_request_workflow_and_bed_updates(self):
        # 1. Register student and initial room assignment
        with app.app_context():
            st = Student(name='Anil Kumar', register_number='MCA202402', department='MCA', email='anil@college.edu')
            st.set_password('pass123')
            db.session.add(st)
            db.session.commit()
            st_id = st.id

            # Assign room1 to student initially
            alloc = RoomAllocation(student_id=st_id, room_id=self.room1_id, allocation_date=date.today(), status='Active')
            db.session.add(alloc)

            # Update room1 available beds
            rm1 = db.session.get(Room, self.room1_id)
            rm1.available_beds -= 1 # 1 - 1 = 0 available beds
            db.session.commit()

        # 2. Login student
        self.client.post('/login', data={'email_or_reg': 'anil@college.edu', 'password': 'pass123'})

        # View current room page
        response = self.client.get('/student/current-room')
        self.assertIn(b'Room 101', response.data)

        # 3. Try submitting request for same room (101) -> Should fail validation
        response = self.client.post('/student/request-change', data={
            'requested_room_id': self.room1_id,
            'reason': 'Personal Reason'
        }, follow_redirects=True)
        self.assertIn(b'Requested room cannot be the same as your current room', response.data)

        # 4. Submit valid change request to Room 102
        response = self.client.post('/student/request-change', data={
            'requested_room_id': self.room2_id,
            'reason': 'Roommate Issue'
        }, follow_redirects=True)
        self.assertIn(b'Room change request submitted successfully', response.data)

        # 5. Try submitting duplicate request while one is pending -> Should fail validation
        response = self.client.post('/student/request-change', data={
            'requested_room_id': self.room3_id,
            'reason': 'Medical Reason'
        }, follow_redirects=True)
        self.assertIn(b'already have an active room change request pending admin approval', response.data)

        # 6. Admin login and view requests
        self.client.get('/logout')
        self.client.post('/admin/login', data={'username': 'admin', 'password': 'admin123'})

        with app.app_context():
            req = RoomChangeRequest.query.filter_by(student_id=st_id, status='Pending').first()
            req_id = req.id

        # 7. Approve the change request
        response = self.client.post(f'/admin/approve-request/{req_id}', data={'admin_remarks': 'Approved by Warden.'}, follow_redirects=True)
        self.assertIn(b'approved successfully', response.data)

        # 8. Verify database state after approval:
        with app.app_context():
            # Room 101 beds should increase from 0 to 1
            rm1 = db.session.get(Room, self.room1_id)
            self.assertEqual(rm1.available_beds, 1)

            # Room 102 beds should decrease from 1 to 0
            rm2 = db.session.get(Room, self.room2_id)
            self.assertEqual(rm2.available_beds, 0)

            # Active allocation for student should now be Room 102
            active_alloc = get_student_active_allocation(st_id)
            self.assertIsNotNone(active_alloc)
            self.assertEqual(active_alloc.room_id, self.room2_id)

    def test_admin_room_management(self):
        # Admin login
        self.client.post('/admin/login', data={'username': 'admin', 'password': 'admin123'})

        # Add room
        response = self.client.post('/admin/add-room', data={
            'room_number': '305',
            'hostel_name': 'C Block',
            'room_type': 'Double',
            'capacity': 2,
            'available_beds': 2
        }, follow_redirects=True)
        self.assertIn(b'Room 305 (C Block) added successfully!', response.data)

        # Edit room
        with app.app_context():
            rm = Room.query.filter_by(room_number='305').first()
            rm_id = rm.id

        response = self.client.post(f'/admin/edit-room/{rm_id}', data={
            'room_number': '305A',
            'hostel_name': 'C Block',
            'room_type': 'Double',
            'capacity': 2,
            'available_beds': 1
        }, follow_redirects=True)
        self.assertIn(b'Room 305A details updated successfully!', response.data)

        # Delete room
        response = self.client.post(f'/admin/delete-room/{rm_id}', follow_redirects=True)
        self.assertIn(b'Room deleted successfully', response.data)

if __name__ == '__main__':
    unittest.main()
