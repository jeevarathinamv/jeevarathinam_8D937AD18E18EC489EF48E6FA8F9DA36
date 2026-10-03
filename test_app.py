import unittest
from datetime import date, timedelta
from app import app, db, Student, Admin, Book, BookIssue, check_and_update_overdue

class LibrarySystemTestCase(unittest.TestCase):
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
            db.session.add(admin)

            # Seed Books
            b1 = Book(book_name='Python Essentials', author_name='Guido', isbn='111-222-333', category='Programming', total_copies=3, available_copies=3)
            b2 = Book(book_name='SQL Mastery', author_name='Edgar', isbn='444-555-666', category='Database', total_copies=1, available_copies=0)
            db.session.add_all([b1, b2])
            db.session.commit()

    def tearDown(self):
        with app.app_context():
            db.session.remove()
            db.drop_all()

    def test_student_registration_and_login(self):
        # Student Registration
        res = self.client.post('/register', data={
            'student_name': 'Alice Smith',
            'register_number': 'REG001',
            'department': 'Computer Applications (MCA)',
            'email': 'alice@college.edu',
            'password': 'password123'
        }, follow_redirects=True)
        self.assertIn(b'Registration successful', res.data)

        # Student Login
        res = self.client.post('/login', data={
            'email_or_reg': 'REG001',
            'password': 'password123'
        }, follow_redirects=True)
        self.assertIn(b'Welcome back, Alice Smith!', res.data)

    def test_admin_login(self):
        res = self.client.post('/admin/login', data={
            'username': 'admin',
            'password': 'admin123'
        }, follow_redirects=True)
        self.assertIn(b'Logged in successfully as Administrator', res.data)

    def test_book_issue_and_stock_validation(self):
        # Register and Login Student
        self.client.post('/register', data={
            'student_name': 'Bob MCA',
            'register_number': 'MCA201',
            'department': 'Computer Applications (MCA)',
            'email': 'bob@college.edu',
            'password': 'pass'
        })
        self.client.post('/login', data={
            'email_or_reg': 'bob@college.edu',
            'password': 'pass'
        })

        # Try issuing out of stock book (b2, available = 0)
        res = self.client.post('/student/issue/2', follow_redirects=True)
        self.assertIn(b'currently has no available copies', res.data)

        # Issue available book (b1, available = 3)
        res = self.client.post('/student/issue/1', follow_redirects=True)
        self.assertIn(b'Successfully issued', res.data)

        with app.app_context():
            b1 = db.session.get(Book, 1)
            self.assertEqual(b1.available_copies, 2)

        # Try issuing the same book again while active
        res = self.client.post('/student/issue/1', follow_redirects=True)
        self.assertIn(b'already issued', res.data)

    def test_admin_return_book(self):
        # Register student and issue book
        self.client.post('/register', data={
            'student_name': 'Charlie',
            'register_number': 'REG301',
            'department': 'MCA',
            'email': 'charlie@college.edu',
            'password': 'pass'
        })
        self.client.post('/login', data={
            'email_or_reg': 'REG301',
            'password': 'pass'
        })
        self.client.post('/student/issue/1')

        # Admin login and mark returned
        self.client.get('/logout')
        self.client.post('/admin/login', data={'username': 'admin', 'password': 'admin123'})

        res = self.client.post('/admin/issues/return/1', follow_redirects=True)
        self.assertIn(b'marked as Returned', res.data)

        with app.app_context():
            b1 = db.session.get(Book, 1)
            self.assertEqual(b1.available_copies, 3)
            issue = db.session.get(BookIssue, 1)
            self.assertEqual(issue.status, 'Returned')
            self.assertIsNotNone(issue.return_date)

    def test_admin_book_crud_and_validation(self):
        self.client.post('/admin/login', data={'username': 'admin', 'password': 'admin123'})

        # Add book
        res = self.client.post('/admin/books/add', data={
            'book_name': 'Web Tech Essentials',
            'author_name': 'John Doe',
            'isbn': '999-888-777',
            'category': 'Web Development',
            'total_copies': 4
        }, follow_redirects=True)
        self.assertIn(b'added successfully', res.data)

        # Edit book with invalid available copies (> total)
        res = self.client.post('/admin/books/edit/3', data={
            'book_name': 'Web Tech Essentials',
            'author_name': 'John Doe',
            'isbn': '999-888-777',
            'category': 'Web Development',
            'total_copies': 4,
            'available_copies': 10
        }, follow_redirects=True)
        self.assertIn(b'Available copies cannot be greater than Total copies', res.data)

        # Delete book
        res = self.client.post('/admin/books/delete/3', follow_redirects=True)
        self.assertIn(b'Book deleted successfully', res.data)

    def test_overdue_detection(self):
        with app.app_context():
            student = Student(student_name='David', register_number='REG401', department='MCA', email='david@college.edu', password='hash')
            db.session.add(student)
            db.session.commit()

            # Create an issue past due date
            past_date = date.today() - timedelta(days=20)
            due_date = date.today() - timedelta(days=6)
            past_issue = BookIssue(student_id=student.id, book_id=1, issue_date=past_date, due_date=due_date, status='Issued')
            db.session.add(past_issue)
            db.session.commit()

            check_and_update_overdue()
            issue = db.session.get(BookIssue, 1)
            self.assertEqual(issue.status, 'Overdue')

if __name__ == '__main__':
    unittest.main()
