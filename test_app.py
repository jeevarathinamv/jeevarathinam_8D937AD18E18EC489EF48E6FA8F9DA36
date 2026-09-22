import unittest
from app import app, db, Student, Category, Question, InterviewAttempt, InterviewAnswer, evaluate_answer

class MockInterviewTestCase(unittest.TestCase):
    def setUp(self):
        app.config['TESTING'] = True
        app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
        app.config['WTF_CSRF_ENABLED'] = False
        self.client = app.test_client()

        with app.app_context():
            db.create_all()
            # Seed Category & Question
            cat = Category(name='Python', description='Python Programming')
            db.session.add(cat)
            db.session.commit()

            q1 = Question(
                category_id=cat.id,
                question_text='What is a list in Python?',
                sample_answer='A list is a mutable ordered collection of elements.',
                keywords='mutable, ordered, collection, elements, list',
                max_marks=10
            )
            q2 = Question(
                category_id=cat.id,
                question_text='What is a tuple in Python?',
                sample_answer='A tuple is an immutable ordered collection of elements.',
                keywords='immutable, ordered, collection, elements, tuple',
                max_marks=10
            )
            db.session.add_all([q1, q2])
            db.session.commit()

            self.cat_id = cat.id
            self.q1_id = q1.id
            self.q2_id = q2.id

    def tearDown(self):
        with app.app_context():
            db.session.remove()
            db.drop_all()

    def test_student_registration_and_login(self):
        # Test Registration
        response = self.client.post('/register', data={
            'name': 'Jane Doe',
            'register_number': 'REG202301',
            'department': 'Computer Science',
            'email': 'jane@college.edu',
            'password': 'password123'
        }, follow_redirects=True)
        self.assertIn(b'Registration successful', response.data)

        # Test Student Login
        response = self.client.post('/login', data={
            'login_type': 'student',
            'email_or_reg': 'jane@college.edu',
            'password': 'password123'
        }, follow_redirects=True)
        self.assertIn(b'Welcome back, Jane Doe!', response.data)

    def test_admin_login_and_question_crud(self):
        # Admin Login
        response = self.client.post('/login', data={
            'login_type': 'admin',
            'username': 'admin',
            'password': 'admin123'
        }, follow_redirects=True)
        self.assertIn(b'Logged in successfully as Administrator', response.data)

        # Add Category
        response = self.client.post('/admin/category/add', data={
            'name': 'Data Structures',
            'description': 'DS & Algo'
        }, follow_redirects=True)
        self.assertIn(b'created successfully', response.data)

        # Add Question
        response = self.client.post('/admin/question/add', data={
            'category_id': self.cat_id,
            'question_text': 'What is recursion?',
            'sample_answer': 'Function calling itself.',
            'keywords': 'function, calling, itself, recursion',
            'max_marks': 10
        }, follow_redirects=True)
        self.assertIn(b'Question added successfully', response.data)

        # Edit Question
        response = self.client.post(f'/admin/question/edit/{self.q1_id}', data={
            'question_text': 'Explain Python list data structure.',
            'sample_answer': 'Mutable sequence type.',
            'keywords': 'mutable, sequence, list',
            'max_marks': 10
        }, follow_redirects=True)
        self.assertIn(b'Question updated successfully', response.data)

        # Delete Question
        response = self.client.post(f'/admin/question/delete/{self.q2_id}', follow_redirects=True)
        self.assertIn(b'Question deleted successfully', response.data)

    def test_answer_evaluation_algorithm(self):
        score, feedback = evaluate_answer(
            user_answer='A list in python is a mutable ordered collection of elements.',
            sample_answer='A list is a mutable ordered collection of elements.',
            keywords_str='mutable, ordered, collection, elements, list',
            max_marks=10
        )
        self.assertEqual(score, 10.0)
        self.assertIn('Excellent', feedback)

        score_partial, feedback_partial = evaluate_answer(
            user_answer='It is a mutable list.',
            sample_answer='A list is a mutable ordered collection of elements.',
            keywords_str='mutable, ordered, collection, elements, list',
            max_marks=10
        )
        self.assertGreater(score_partial, 0)
        self.assertLess(score_partial, 10)

    def test_mock_interview_flow_and_result_saving(self):
        # Register and login student
        self.client.post('/register', data={
            'name': 'John Smith',
            'register_number': 'REG202302',
            'department': 'MCA',
            'email': 'john@college.edu',
            'password': 'pass'
        })
        self.client.post('/login', data={
            'login_type': 'student',
            'email_or_reg': 'john@college.edu',
            'password': 'pass'
        })

        # Start practice interview
        start_res = self.client.get(f'/student/interview/start/{self.cat_id}', follow_redirects=True)
        self.assertIn(b'Question 1 of 2', start_res.data)

        # Answer question 1 and click Next
        q1_post = self.client.post('/student/interview/question', data={
            'user_answer': 'A list is a mutable ordered collection.',
            'action': 'next'
        }, follow_redirects=True)
        self.assertIn(b'Question 2 of 2', q1_post.data)

        # Answer question 2 and submit
        q2_post = self.client.post('/student/interview/question', data={
            'user_answer': 'A tuple is an immutable ordered collection.',
            'action': 'submit'
        }, follow_redirects=True)
        self.assertIn(b'Mock interview completed', q2_post.data)
        self.assertIn(b'Category: Python', q2_post.data)

        with app.app_context():
            attempt = InterviewAttempt.query.first()
            self.assertIsNotNone(attempt)
            self.assertGreater(attempt.total_score, 0)
            answers = InterviewAnswer.query.filter_by(attempt_id=attempt.id).all()
            self.assertEqual(len(answers), 2)

if __name__ == '__main__':
    unittest.main()
