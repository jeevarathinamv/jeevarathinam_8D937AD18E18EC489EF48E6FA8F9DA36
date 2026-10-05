import unittest
from datetime import date, timedelta
from app import app, db, Student, Admin, Book, BookIssue

class LibraryFineManagementTestCase(unittest.TestCase):
    def setUp(self):
        app.config['TESTING'] = True
        app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
        app.config['WTF_CSRF_ENABLED'] = False
        self.client = app.test_client()

        with app.app_context():
            db.create_all()
            # Seed admin user
            self.admin = Admin(username='admin', name='Library Admin')
            self.admin.set_password('admin123')
            db.session.add(self.admin)

            # Seed initial book
            self.book1 = Book(
                book_name='Python Crash Course',
                author_name='Eric Matthes',
                book_code='BK-CS-001',
                category='Computer Science',
                available_copies=3
            )
            db.session.add(self.book1)
            db.session.commit()

    def tearDown(self):
        with app.app_context():
            db.session.remove()
            db.drop_all()

    def test_student_registration_and_login(self):
        # Register student
        response = self.client.post('/register', data={
            'name': 'Rohan Sharma',
            'register_number': 'MCA2024001',
            'department': 'Computer Applications (MCA)',
            'email': 'rohan@college.edu',
            'password': 'password123'
        }, follow_redirects=True)
        self.assertIn(b'Registration successful', response.data)

        # Login student
        response = self.client.post('/login', data={
            'login_type': 'student',
            'email_or_reg': 'rohan@college.edu',
            'password': 'password123'
        }, follow_redirects=True)
        self.assertIn(b'Welcome back, Rohan Sharma!', response.data)

    def test_admin_login(self):
        response = self.client.post('/admin/login', data={
            'username': 'admin',
            'password': 'admin123'
        }, follow_redirects=True)
        self.assertIn(b'Logged in successfully as Administrator', response.data)

    def test_book_management(self):
        # Admin login
        self.client.post('/admin/login', data={'username': 'admin', 'password': 'admin123'})

        # Add book
        response = self.client.post('/admin/books/add', data={
            'book_name': 'Clean Code',
            'author_name': 'Robert C. Martin',
            'book_code': 'BK-CS-002',
            'category': 'Computer Science',
            'available_copies': 5
        }, follow_redirects=True)
        self.assertIn(b'added successfully', response.data)

        # Edit book
        with app.app_context():
            book = Book.query.filter_by(book_code='BK-CS-002').first()
            book_id = book.id

        response = self.client.post(f'/admin/books/edit/{book_id}', data={
            'book_name': 'Clean Code - Updated Edition',
            'author_name': 'Robert C. Martin',
            'book_code': 'BK-CS-002',
            'category': 'Computer Science',
            'available_copies': 6
        }, follow_redirects=True)
        self.assertIn(b'updated successfully', response.data)

        # Delete book
        response = self.client.post(f'/admin/books/delete/{book_id}', follow_redirects=True)
        self.assertIn(b'Book deleted successfully', response.data)

    def test_issue_return_book_and_fine_calculation(self):
        # Register student
        self.client.post('/register', data={
            'name': 'Anita Roy',
            'register_number': 'MCA2024002',
            'department': 'Computer Applications (MCA)',
            'email': 'anita@college.edu',
            'password': 'password123'
        })

        # Admin login
        self.client.post('/admin/login', data={'username': 'admin', 'password': 'admin123'})

        today = date.today()
        issue_date = today - timedelta(days=10)
        due_date = today - timedelta(days=3)  # 3 days overdue!

        # Issue book
        response = self.client.post('/admin/issue-book', data={
            'student_id': 1,
            'book_id': 1,
            'issue_date': issue_date.isoformat(),
            'due_date': due_date.isoformat()
        }, follow_redirects=True)
        self.assertIn(b'issued successfully', response.data)

        # Verify automatic overdue status and late fine calculation (3 days late * ₹5 = ₹15)
        with app.app_context():
            issue = db.session.get(BookIssue, 1)
            self.assertEqual(issue.status, 'Overdue')
            self.assertEqual(issue.late_days, 3)
            self.assertEqual(issue.fine_amount, 15.0)
            self.assertEqual(issue.fine_status, 'Pending')

            book = db.session.get(Book, 1)
            self.assertEqual(book.available_copies, 2)  # Decremented stock

        # Process return
        return_date = today
        response = self.client.post('/admin/return-book/1', data={
            'return_date': return_date.isoformat()
        }, follow_redirects=True)
        self.assertIn(b'marked as Returned', response.data)

        with app.app_context():
            issue = db.session.get(BookIssue, 1)
            self.assertEqual(issue.status, 'Returned')
            self.assertEqual(issue.late_days, 3)
            self.assertEqual(issue.fine_amount, 15.0)

            book = db.session.get(Book, 1)
            self.assertEqual(book.available_copies, 3)  # Incremented stock back

    def test_update_fine_status(self):
        # Setup student & overdue issue
        self.client.post('/register', data={
            'name': 'Rahul Verma',
            'register_number': 'MCA2024003',
            'department': 'MCA',
            'email': 'rahul@college.edu',
            'password': 'password123'
        })
        self.client.post('/admin/login', data={'username': 'admin', 'password': 'admin123'})

        today = date.today()
        self.client.post('/admin/issue-book', data={
            'student_id': 1,
            'book_id': 1,
            'issue_date': (today - timedelta(days=10)).isoformat(),
            'due_date': (today - timedelta(days=2)).isoformat()
        })

        # Update fine status to Paid
        response = self.client.post('/admin/fine/update-status/1', data={
            'fine_status': 'Paid'
        }, follow_redirects=True)
        self.assertIn(b'Fine status for issue #1 updated', response.data)

        with app.app_context():
            issue = db.session.get(BookIssue, 1)
            self.assertEqual(issue.fine_status, 'Paid')

if __name__ == '__main__':
    unittest.main()
