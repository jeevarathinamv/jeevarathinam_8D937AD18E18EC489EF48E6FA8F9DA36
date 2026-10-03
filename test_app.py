import unittest
from datetime import date, timedelta
from app import (
    app, db, Student, Admin, CareerProfile, CareerGoal, Skill, Certification, Milestone,
    calculate_student_overall_progress
)

class CareerTrackerTestCase(unittest.TestCase):
    def setUp(self):
        app.config['TESTING'] = True
        app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
        app.config['WTF_CSRF_ENABLED'] = False
        self.client = app.test_client()

        with app.app_context():
            db.create_all()
            # Seed admin
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
            'name': 'John Doe',
            'register_number': '23MCA101',
            'department': 'Master of Computer Applications',
            'email': 'john@mca.edu',
            'password': 'password123'
        }, follow_redirects=True)
        self.assertIn(b'Registration successful', response.data)

        # Try duplicate registration
        response = self.client.post('/register', data={
            'name': 'John Duplicate',
            'register_number': '23MCA101',
            'department': 'MCA',
            'email': 'john@mca.edu',
            'password': 'password123'
        }, follow_redirects=True)
        self.assertIn(b'already exists', response.data)

        # Login student
        response = self.client.post('/login', data={
            'email_or_reg': '23MCA101',
            'password': 'password123'
        }, follow_redirects=True)
        self.assertIn(b'Welcome back, John Doe!', response.data)

    def test_admin_login(self):
        response = self.client.post('/admin/login', data={
            'username': 'admin',
            'password': 'admin123'
        }, follow_redirects=True)
        self.assertIn(b'Logged in successfully as Administrator', response.data)

    def test_career_profile_management(self):
        # Register and login student
        self.client.post('/register', data={
            'name': 'Alice Smith',
            'register_number': '23MCA102',
            'department': 'MCA',
            'email': 'alice@mca.edu',
            'password': 'pass'
        })
        self.client.post('/login', data={
            'email_or_reg': 'alice@mca.edu',
            'password': 'pass'
        })

        # Update Career Profile
        response = self.client.post('/student/profile', data={
            'target_job_role': 'Full Stack Developer',
            'target_industry': 'IT Services',
            'preferred_career_field': 'Web Applications',
            'skills': 'Python, Flask, JavaScript, SQL',
            'career_objective': 'To become an expert backend engineer.',
            'short_term_goal': 'Master Flask and React.',
            'long_term_goal': 'Lead a software engineering team.'
        }, follow_redirects=True)

        self.assertIn(b'Career profile updated successfully!', response.data)
        self.assertIn(b'Full Stack Developer', response.data)

    def test_career_goals_crud_and_status_logic(self):
        # Register and login student
        self.client.post('/register', data={
            'name': 'Bob Ross',
            'register_number': '23MCA103',
            'department': 'MCA',
            'email': 'bob@mca.edu',
            'password': 'pass'
        })
        self.client.post('/login', data={
            'email_or_reg': 'bob@mca.edu',
            'password': 'pass'
        })

        # Add Goal 1: Active In Progress Goal
        today = date.today()
        future_date = today + timedelta(days=30)
        past_date = today - timedelta(days=10)

        response = self.client.post('/student/goals/add', data={
            'title': 'Learn Flask ORM',
            'category': 'Programming',
            'start_date': today.isoformat(),
            'target_date': future_date.isoformat(),
            'priority': 'High',
            'progress_percentage': 50,
            'status': 'In Progress',
            'description': 'Master SQLAlchemy database models.'
        }, follow_redirects=True)
        self.assertIn(b'New career goal added successfully!', response.data)

        # Add Goal 2: Overdue Goal (target date in the past)
        self.client.post('/student/goals/add', data={
            'title': 'Prepare Resume',
            'category': 'Placement',
            'start_date': (today - timedelta(days=20)).isoformat(),
            'target_date': past_date.isoformat(),
            'priority': 'High',
            'progress_percentage': 30,
            'status': 'In Progress',
            'description': 'Draft resume for campus placements.'
        }, follow_redirects=True)

        # Check goals list and automatic overdue status evaluation
        response = self.client.get('/student/goals')
        self.assertIn(b'Overdue', response.data)
        self.assertIn(b'Learn Flask ORM', response.data)

        # Update Goal progress via quick modal route
        response = self.client.post('/student/goals/update_progress/1', data={
            'progress_percentage': 100,
            'status': 'Completed',
            'notes': 'Completed all tutorials and built project.'
        }, follow_redirects=True)
        self.assertIn(b'updated to 100%', response.data)

        # Verify overall progress calculation
        with app.app_context():
            student = Student.query.filter_by(register_number='23MCA103').first()
            progress = calculate_student_overall_progress(student.id)
            # Goal 1: 100%, Goal 2: 30% -> Average = (100+30)/2 = 65%
            self.assertEqual(progress, 65)

        # Delete Goal
        response = self.client.post('/student/goals/delete/2', follow_redirects=True)
        self.assertIn(b'Goal deleted successfully.', response.data)

    def test_skills_certifications_and_milestones(self):
        # Register and login
        self.client.post('/register', data={
            'name': 'Charlie',
            'register_number': '23MCA104',
            'department': 'MCA',
            'email': 'charlie@mca.edu',
            'password': 'pass'
        })
        self.client.post('/login', data={
            'email_or_reg': 'charlie@mca.edu',
            'password': 'pass'
        })

        # Add Skill
        response = self.client.post('/student/skills', data={
            'skill_name': 'Python',
            'skill_category': 'Programming Languages',
            'skill_level': 'Beginner',
            'target_level': 'Advanced'
        }, follow_redirects=True)
        self.assertIn(b'Skill added successfully!', response.data)

        # Add Certification
        response = self.client.post('/student/certifications', data={
            'name': 'Python for Data Science',
            'issuing_organization': 'NPTEL',
            'issue_date': '2024-01-15',
            'status': 'Active'
        }, follow_redirects=True)
        self.assertIn(b'Certification added successfully!', response.data)

        # Add Milestone
        response = self.client.post('/student/milestones', data={
            'title': 'Completed Web Development Project',
            'milestone_type': 'Finished Project',
            'date_achieved': '2024-05-01',
            'description': 'Built Student Career Tracker web app.'
        }, follow_redirects=True)
        self.assertIn(b'Career milestone added successfully!', response.data)

        # Delete Skill, Certification, Milestone
        self.client.post('/student/skills/delete/1', follow_redirects=True)
        self.client.post('/student/certifications/delete/1', follow_redirects=True)
        self.client.post('/student/milestones/delete/1', follow_redirects=True)

        with app.app_context():
            self.assertEqual(Skill.query.count(), 0)
            self.assertEqual(Certification.query.count(), 0)
            self.assertEqual(Milestone.query.count(), 0)

    def test_admin_student_management_and_progress_monitoring(self):
        # Register student first
        self.client.post('/register', data={
            'name': 'David Miller',
            'register_number': '23MCA105',
            'department': 'MCA',
            'email': 'david@mca.edu',
            'password': 'pass'
        })

        # Login Admin
        self.client.post('/admin/login', data={
            'username': 'admin',
            'password': 'admin123'
        })

        # Admin Dashboard
        response = self.client.get('/admin/dashboard')
        self.assertIn(b'Total Students', response.data)

        # Manage Students & Search
        response = self.client.get('/admin/students?search=David')
        self.assertIn(b'David Miller', response.data)

        # Progress Monitoring Report
        response = self.client.get('/admin/students/progress')
        self.assertIn(b'David Miller', response.data)

        # Delete Student as Admin
        response = self.client.post('/admin/students/delete/1', follow_redirects=True)
        self.assertIn(b'deleted successfully', response.data)

        with app.app_context():
            self.assertEqual(Student.query.count(), 0)

if __name__ == '__main__':
    unittest.main()
