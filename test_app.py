import unittest
from datetime import date
from app import app, db, Student, Admin, Feedback, Complaint

class CanteenFeedbackTestCase(unittest.TestCase):
    def setUp(self):
        app.config['TESTING'] = True
        app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
        app.config['WTF_CSRF_ENABLED'] = False
        self.client = app.test_client()

        with app.app_context():
            db.create_all()
            # Seed default admin
            self.admin = Admin(username='admin', full_name='Canteen Admin')
            self.admin.set_password('admin123')
            db.session.add(self.admin)
            db.session.commit()

    def tearDown(self):
        with app.app_context():
            db.session.remove()
            db.drop_all()

    def test_student_registration_and_login(self):
        # Register student
        response = self.client.post('/register', data={
            'name': 'Rahul Sharma',
            'register_number': 'MCA202401',
            'department': 'MCA',
            'email': 'rahul@college.edu',
            'password': 'password123'
        }, follow_redirects=True)
        self.assertIn(b'Registration successful', response.data)

        # Login student with email
        response = self.client.post('/login', data={
            'email_or_reg': 'rahul@college.edu',
            'password': 'password123'
        }, follow_redirects=True)
        self.assertIn(b'Welcome back, Rahul Sharma!', response.data)

        # Logout
        response = self.client.get('/logout', follow_redirects=True)
        self.assertIn(b'logged out successfully', response.data)

        # Login student with register number
        response = self.client.post('/login', data={
            'email_or_reg': 'MCA202401',
            'password': 'password123'
        }, follow_redirects=True)
        self.assertIn(b'Welcome back, Rahul Sharma!', response.data)

    def test_admin_login(self):
        response = self.client.post('/admin/login', data={
            'username': 'admin',
            'password': 'admin123'
        }, follow_redirects=True)
        self.assertIn(b'Logged in successfully as Administrator', response.data)

    def test_submit_feedback_and_complaint_workflow(self):
        # 1. Register & login student
        self.client.post('/register', data={
            'name': 'Priya Das',
            'register_number': 'MCA202402',
            'department': 'Master of Computer Applications',
            'email': 'priya@college.edu',
            'password': 'priya'
        })
        self.client.post('/login', data={
            'email_or_reg': 'priya@college.edu',
            'password': 'priya'
        })

        # 2. Submit feedback
        response = self.client.post('/student/feedback', data={
            'food_quality_rating': 4,
            'taste_rating': 5,
            'cleanliness_rating': 4,
            'service_rating': 3,
            'overall_rating': 4,
            'message': 'Great lunch options, but queue was long.',
            'feedback_date': date.today().isoformat()
        }, follow_redirects=True)
        self.assertIn(b'feedback has been submitted successfully', response.data)

        # 3. Submit complaint
        response = self.client.post('/student/complaint', data={
            'complaint_type': 'Food Quality',
            'description': 'Food served was cold and stale today.',
            'complaint_date': date.today().isoformat()
        }, follow_redirects=True)
        self.assertIn(b'Complaint submitted successfully!', response.data)

        # Verify complaint created in DB
        with app.app_context():
            c = Complaint.query.filter_by(complaint_type='Food Quality').first()
            self.assertIsNotNone(c)
            self.assertTrue(c.complaint_id.startswith('CMP-'))
            complaint_id_num = c.id

        # 4. Student views my-feedback and my-complaints
        response = self.client.get('/student/my-feedback')
        self.assertIn(b'Great lunch options', response.data)

        response = self.client.get('/student/my-complaints')
        self.assertIn(b'Food served was cold', response.data)

        # 5. Admin logs in to manage complaint
        # Login admin without redirecting immediately or clear previous flash messages
        with self.client.session_transaction() as sess:
            sess.clear()

        self.client.post('/admin/login', data={
            'username': 'admin',
            'password': 'admin123'
        })

        # Update complaint status to In Progress and add remarks
        response = self.client.post(f'/admin/complaints/update/{complaint_id_num}', data={
            'status': 'In Progress',
            'admin_remarks': 'Inspecting kitchen team.'
        }, follow_redirects=True)
        self.assertIn(b'In Progress', response.data)

        # Update complaint status to Resolved
        response = self.client.post(f'/admin/complaints/update/{complaint_id_num}', data={
            'status': 'Resolved',
            'admin_remarks': 'Complaint has been checked and resolved with kitchen head.'
        }, follow_redirects=True)
        self.assertIn(b'Resolved', response.data)

        # Search & status filter check
        response = self.client.get('/admin/complaints?status=Resolved')
        self.assertIn(b'Resolved', response.data)

        response = self.client.get('/admin/complaints?q=Priya')
        self.assertIn(b'Priya Das', response.data)

        # Delete feedback
        with app.app_context():
            fb = Feedback.query.first()
            fb_id = fb.id

        response = self.client.post(f'/admin/feedback/delete/{fb_id}', follow_redirects=True)
        self.assertIn(b'Feedback record deleted successfully', response.data)

if __name__ == '__main__':
    unittest.main()
