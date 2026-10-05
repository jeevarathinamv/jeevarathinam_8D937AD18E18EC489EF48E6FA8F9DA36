import os
import io
import unittest
from app import app, db, Student, Admin, Book, Download

class CollegeDigitalLibraryTestCase(unittest.TestCase):
    def setUp(self):
        app.config['TESTING'] = True
        app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
        app.config['WTF_CSRF_ENABLED'] = False
        app.config['UPLOAD_FOLDER'] = os.path.join(os.path.dirname(__file__), 'static', 'uploads')
        self.client = app.test_client()

        with app.app_context():
            db.create_all()
            # Seed Admin
            admin = Admin(username='admin', name='System Administrator')
            admin.set_password('admin123')
            db.session.add(admin)

            # Seed Sample Book
            book = Book(
                title='Python Fundamentals',
                author='Guido van Rossum',
                category='Programming',
                description='Learn Python 3 syntax and programming concepts.',
                filename='sample_python_guide.pdf'
            )
            db.session.add(book)
            db.session.commit()

    def tearDown(self):
        with app.app_context():
            db.session.remove()
            db.drop_all()

    def test_student_registration_and_login(self):
        # Register student
        response = self.client.post('/register', data={
            'name': 'Alice Smith',
            'register_number': 'REG2025001',
            'department': 'Computer Applications',
            'email': 'alice@college.edu',
            'password': 'password123'
        }, follow_redirects=True)
        self.assertIn(b'Registration successful', response.data)

        # Login student
        response = self.client.post('/login', data={
            'email_or_reg': 'alice@college.edu',
            'password': 'password123'
        }, follow_redirects=True)
        self.assertIn(b'Welcome back, Alice Smith!', response.data)

        # Logout
        response = self.client.get('/logout', follow_redirects=True)
        self.assertIn(b'You have been logged out', response.data)

    def test_admin_login_and_dashboard(self):
        response = self.client.post('/admin/login', data={
            'username': 'admin',
            'password': 'admin123'
        }, follow_redirects=True)
        self.assertIn(b'Successfully logged in as Administrator', response.data)
        self.assertIn(b'Administrator Dashboard', response.data)

    def test_book_search_and_details(self):
        # Test catalog search
        response = self.client.get('/books?q=Python&category=Programming')
        self.assertIn(b'Python Fundamentals', response.data)

        # Test book details
        response = self.client.get('/books/1')
        self.assertIn(b'Guido van Rossum', response.data)

    def test_pdf_upload_validation_and_book_crud(self):
        # Admin login
        self.client.post('/admin/login', data={
            'username': 'admin',
            'password': 'admin123'
        })

        # Try uploading invalid non-PDF file
        txt_file = (io.BytesIO(b'invalid file content'), 'document.txt')
        response = self.client.post('/admin/books/add', data={
            'title': 'Invalid Book',
            'author': 'Tester',
            'category': 'Other',
            'description': 'Text file test',
            'file': txt_file
        }, follow_redirects=True)
        self.assertIn(b'Only PDF files (.pdf) are allowed', response.data)

        # Upload valid PDF file
        pdf_file = (io.BytesIO(b'%PDF-1.4 sample content'), 'valid_book.pdf')
        response = self.client.post('/admin/books/add', data={
            'title': 'Advanced Database Systems',
            'author': 'C.J. Date',
            'category': 'Database',
            'description': 'Comprehensive SQL reference.',
            'file': pdf_file
        }, follow_redirects=True)
        self.assertIn(b'added successfully', response.data)

        # Edit book
        response = self.client.post('/admin/books/edit/2', data={
            'title': 'Advanced Relational Database Systems',
            'author': 'C.J. Date',
            'category': 'Database',
            'description': 'Updated description.'
        }, follow_redirects=True)
        self.assertIn(b'updated successfully', response.data)

        # Delete book
        response = self.client.post('/admin/books/delete/2', follow_redirects=True)
        self.assertIn(b'deleted successfully', response.data)

    def test_download_and_history_tracking(self):
        # Register and login student
        self.client.post('/register', data={
            'name': 'Bob Student',
            'register_number': 'REG2025002',
            'department': 'Computer Applications',
            'email': 'bob@college.edu',
            'password': 'password123'
        })
        self.client.post('/login', data={
            'email_or_reg': 'bob@college.edu',
            'password': 'password123'
        })

        # Download book #1
        response = self.client.get('/books/download/1')
        self.assertEqual(response.status_code, 200)
        response.close()

        # Check student download history
        response = self.client.get('/student/downloads')
        self.assertIn(b'Python Fundamentals', response.data)

if __name__ == '__main__':
    unittest.main()
