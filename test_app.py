import unittest
from datetime import date
from app import app, db, Student, Admin, BookRequest

class LibraryBookRequestTestCase(unittest.TestCase):
    def setUp(self):
        app.config['TESTING'] = True
        app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
        app.config['WTF_CSRF_ENABLED'] = False
        self.client = app.test_client()

        with app.app_context():
            db.create_all()
            # Create test admin
            admin = Admin(username='admin')
            admin.set_password('admin123')
            db.session.add(admin)
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
            'department': 'Computer Applications',
            'email': 'alex@college.edu',
            'password': 'password123'
        }, follow_redirects=True)
        self.assertIn(b'Registration successful', response.data)

        # Login student
        response = self.client.post('/login', data={
            'email_or_reg': 'alex@college.edu',
            'password': 'password123'
        }, follow_redirects=True)
        self.assertIn(b'Welcome back, Alex Johnson!', response.data)

    def test_admin_login(self):
        response = self.client.post('/admin/login', data={
            'username': 'admin',
            'password': 'admin123'
        }, follow_redirects=True)
        self.assertIn(b'Logged in successfully as Administrator', response.data)

    def test_book_request_workflow_and_admin_management(self):
        # 1. Register and login student
        self.client.post('/register', data={
            'name': 'Sam',
            'register_number': 'REG456',
            'department': 'MCA',
            'email': 'sam@college.edu',
            'password': 'pass'
        })
        self.client.post('/login', data={
            'email_or_reg': 'sam@college.edu',
            'password': 'pass'
        })

        # 2. Submit book request
        response = self.client.post('/request_book', data={
            'book_name': 'Designing Data-Intensive Applications',
            'author_name': 'Martin Kleppmann',
            'category': 'Database',
            'reason': 'Required for database architecture course.'
        }, follow_redirects=True)
        self.assertIn(b'Book request submitted successfully', response.data)

        with app.app_context():
            req = BookRequest.query.first()
            self.assertIsNotNone(req)
            self.assertTrue(req.request_id.startswith('REQ-'))
            self.assertEqual(req.status, 'Pending')
            req_id_num = req.id

        # 3. View student request details
        response = self.client.get(f'/request_details/{req_id_num}')
        self.assertIn(b'Designing Data-Intensive Applications', response.data)

        # 4. Admin login and manage request (Approve)
        self.client.get('/logout')
        self.client.post('/admin/login', data={
            'username': 'admin',
            'password': 'admin123'
        })

        response = self.client.post(f'/admin/request/update/{req_id_num}', data={
            'action': 'Approved',
            'admin_remarks': 'Book will be purchased soon.'
        }, follow_redirects=True)
        self.assertIn(b'has been marked as Approved', response.data)

        with app.app_context():
            updated_req = db.session.get(BookRequest, req_id_num)
            self.assertEqual(updated_req.status, 'Approved')
            self.assertEqual(updated_req.admin_remarks, 'Book will be purchased soon.')

        # 5. Test search and filter
        response = self.client.get('/admin/manage_requests?status=Approved&search=Martin')
        self.assertIn(b'Martin Kleppmann', response.data)

        # 6. Delete request
        response = self.client.post(f'/admin/request/delete/{req_id_num}', follow_redirects=True)
        self.assertIn(b'deleted successfully', response.data)

        with app.app_context():
            self.assertEqual(BookRequest.query.count(), 0)

if __name__ == '__main__':
    unittest.main()
