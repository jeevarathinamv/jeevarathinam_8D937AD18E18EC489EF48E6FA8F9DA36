import unittest
from datetime import date
from app import app, db, Student, Admin, Project, Task, Client, Payment, StudentProfile

class FreelancePortalTestCase(unittest.TestCase):
    def setUp(self):
        app.config['TESTING'] = True
        app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
        app.config['WTF_CSRF_ENABLED'] = False
        self.client = app.test_client()

        with app.app_context():
            db.create_all()

    def tearDown(self):
        with app.app_context():
            db.session.remove()
            db.drop_all()

    def test_student_registration_and_login(self):
        # Register student
        response = self.client.post('/register', data={
            'name': 'Rahul Sharma',
            'register_number': 'MCA2025001',
            'department': 'Master of Computer Applications',
            'email': 'rahul@college.edu',
            'password': 'password123'
        }, follow_redirects=True)
        self.assertIn('Registration successful', response.data.decode('utf-8'))

        # Login student
        response = self.client.post('/login', data={
            'email_or_reg': 'rahul@college.edu',
            'password': 'password123'
        }, follow_redirects=True)
        self.assertIn('Welcome back, Rahul Sharma!', response.data.decode('utf-8'))

    def test_admin_login(self):
        response = self.client.post('/admin/login', data={
            'username': 'admin',
            'password': 'admin123'
        }, follow_redirects=True)
        self.assertIn('Logged in successfully as Admin', response.data.decode('utf-8'))

    def test_student_profile_update(self):
        # Register and login student
        self.client.post('/register', data={
            'name': 'Anita Roy',
            'register_number': 'MCA2025002',
            'department': 'MCA',
            'email': 'anita@college.edu',
            'password': 'pass'
        })
        self.client.post('/login', data={
            'email_or_reg': 'anita@college.edu',
            'password': 'pass'
        })

        # Update profile
        response = self.client.post('/student/profile', data={
            'name': 'Anita Roy Updated',
            'department': 'MCA',
            'contact_email': 'anita.contact@gmail.com',
            'skills': 'Python, Flask, Bootstrap',
            'experience': '1 year freelance experience',
            'bio': 'Full-stack student freelancer',
            'portfolio_link': 'https://github.com/anita'
        }, follow_redirects=True)
        self.assertIn('Profile updated successfully', response.data.decode('utf-8'))

    def test_project_task_client_payment_workflow(self):
        # Register and login
        self.client.post('/register', data={
            'name': 'John Doe',
            'register_number': 'MCA2025003',
            'department': 'MCA',
            'email': 'john@college.edu',
            'password': 'pass'
        })
        self.client.post('/login', data={
            'email_or_reg': 'john@college.edu',
            'password': 'pass'
        })

        # Add Client
        response = self.client.post('/student/clients/add', data={
            'name': 'Acme Corp',
            'phone': '9876543210',
            'email': 'client@acme.com',
            'company_name': 'Acme Inc',
            'address': 'Tech Park',
            'notes': 'Important client'
        }, follow_redirects=True)
        html = response.data.decode('utf-8')
        self.assertTrue('Client "Acme Corp" added successfully' in html or 'Acme Corp' in html)

        # Add Project
        response = self.client.post('/student/projects/add', data={
            'title': 'Corporate Web Portal',
            'client_id': 1,
            'category': 'Web Development',
            'budget': '15000',
            'start_date': date.today().isoformat(),
            'deadline': date.today().isoformat(),
            'status': 'In Progress',
            'progress_percentage': 25,
            'description': 'Building Flask web portal'
        }, follow_redirects=True)
        html = response.data.decode('utf-8')
        self.assertTrue('Project "Corporate Web Portal" added successfully' in html or 'Corporate Web Portal' in html)

        # Add Task
        response = self.client.post('/student/tasks', data={
            'project_id': 1,
            'title': 'Design Landing Page',
            'priority': 'High',
            'due_date': date.today().isoformat(),
            'status': 'Pending',
            'description': 'Create Bootstrap 5 HTML landing page'
        }, follow_redirects=True)
        html = response.data.decode('utf-8')
        self.assertTrue('Task added successfully' in html or 'Design Landing Page' in html)

        # Add Payment
        response = self.client.post('/student/payments', data={
            'project_id': 1,
            'client_name': 'Acme Corp',
            'amount': '5000',
            'payment_date': date.today().isoformat(),
            'status': 'Paid',
            'notes': 'Advance payment'
        }, follow_redirects=True)
        html = response.data.decode('utf-8')
        self.assertTrue('Payment record added successfully' in html or 'Advance payment' in html)

        # Update Project Progress
        response = self.client.post('/student/projects/update_progress/1', data={
            'progress_percentage': 100,
            'status': 'Completed',
            'progress_notes': 'All deliverables completed!'
        }, follow_redirects=True)
        html = response.data.decode('utf-8')
        self.assertTrue('Project progress updated successfully' in html or '100%' in html)

        with app.app_context():
            p = db.session.get(Project, 1)
            self.assertEqual(p.progress_percentage, 100)
            self.assertEqual(p.status, 'Completed')

if __name__ == '__main__':
    unittest.main()
