import unittest
from datetime import date
from app import app, db, Student, Admin, Idea, Evaluation

class CollegeEntrepreneurshipTestCase(unittest.TestCase):
    def setUp(self):
        app.config['TESTING'] = True
        app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
        app.config['WTF_CSRF_ENABLED'] = False
        self.client = app.test_client()

        with app.app_context():
            db.create_all()
            if not db.session.query(Admin).filter_by(username='admin').first():
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
            'name': 'Anita Roy',
            'register_number': '23MCA101',
            'department': 'Computer Applications (MCA)',
            'year': '2nd Year',
            'email': 'anita@college.edu',
            'phone': '9876543210',
            'password': 'password123'
        }, follow_redirects=True)
        self.assertIn(b'Registration successful', response.data)

        # Login with Email
        response = self.client.post('/login', data={
            'login_id': 'anita@college.edu',
            'password': 'password123'
        }, follow_redirects=True)
        self.assertIn(b'Welcome back, Anita Roy!', response.data)

        # Logout
        self.client.get('/logout')

        # Login with Register Number
        response = self.client.post('/login', data={
            'login_id': '23MCA101',
            'password': 'password123'
        }, follow_redirects=True)
        self.assertIn(b'Welcome back, Anita Roy!', response.data)

    def test_admin_login(self):
        response = self.client.post('/admin/login', data={
            'username': 'admin',
            'password': 'admin123'
        }, follow_redirects=True)
        self.assertIn(b'Logged in successfully as Administrator', response.data)

    def test_idea_submission_workflow_and_evaluation(self):
        # Register and login student
        self.client.post('/register', data={
            'name': 'Vikram Singh',
            'register_number': '23MCA102',
            'department': 'Master of Computer Applications (MCA)',
            'year': '1st Year',
            'email': 'vikram@college.edu',
            'phone': '9123456789',
            'password': 'pass'
        })
        self.client.post('/login', data={
            'login_id': 'vikram@college.edu',
            'password': 'pass'
        })

        # Submit Entrepreneurship Idea
        response = self.client.post('/submit_idea', data={
            'title': 'Eco-Friendly Smart Solar Irrigation',
            'category': 'Agriculture',
            'problem_statement': 'Traditional irrigation wastes water and power.',
            'proposed_solution': 'IoT and solar powered precision drip system.',
            'target_customers': 'Small and medium scale farmers.',
            'required_resources': 'Solar panels, microcontrollers, moisture sensors.',
            'estimated_budget': 'Rs 45,000',
            'expected_benefits': 'Saves 50% water and power costs.'
        }, follow_redirects=True)
        self.assertIn(b'submitted successfully', response.data)

        # Check Idea in DB
        with app.app_context():
            idea = db.session.query(Idea).filter_by(title='Eco-Friendly Smart Solar Irrigation').first()
            self.assertIsNotNone(idea)
            self.assertTrue(idea.idea_id.startswith('IDEA-'))
            self.assertEqual(idea.status, 'Pending')
            idea_db_id = idea.id

        # Student checks My Ideas & Details
        response = self.client.get('/my_ideas')
        self.assertIn(b'Eco-Friendly Smart Solar Irrigation', response.data)

        response = self.client.get(f'/idea/{idea_db_id}')
        self.assertIn(b'Idea Status Tracking', response.data)

        # Switch to Admin
        self.client.get('/logout')
        self.client.post('/admin/login', data={
            'username': 'admin',
            'password': 'admin123'
        })

        # Admin Manage Students search
        response = self.client.get('/admin/students?search=Vikram')
        self.assertIn(b'Vikram Singh', response.data)

        # Admin update idea status to Selected
        response = self.client.post(f'/admin/idea/update_status/{idea_db_id}', data={
            'status': 'Selected',
            'admin_remarks': 'Outstanding proposal, approved for incubator grant.'
        }, follow_redirects=True)
        self.assertIn(b'Selected', response.data)

        # Admin evaluate idea (Scores: 9, 8, 8, 9 = 34/40)
        response = self.client.post(f'/admin/idea/evaluate/{idea_db_id}', data={
            'innovation_score': '9',
            'feasibility_score': '8',
            'market_potential_score': '8',
            'social_impact_score': '9',
            'overall_remarks': 'High feasibility and strong environmental impact.'
        }, follow_redirects=True)
        self.assertIn(b'Evaluation saved successfully', response.data)

        # Check Selected Ideas Page
        response = self.client.get('/selected_ideas')
        self.assertIn(b'Eco-Friendly Smart Solar Irrigation', response.data)
        self.assertIn(b'34 / 40', response.data)

if __name__ == '__main__':
    unittest.main()
