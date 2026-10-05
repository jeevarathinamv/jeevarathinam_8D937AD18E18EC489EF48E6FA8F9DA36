import unittest
from app import app, db, Admin, Student, Book, Reservation

class LibraryReservationTestCase(unittest.TestCase):
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

            # Seed test books
            b1 = Book(
                book_name='Python Programming',
                author_name='John Zelle',
                isbn='978-1590282410',
                category='Computer Science',
                description='Intro to Python',
                total_copies=5,
                available_copies=5
            )
            b2 = Book(
                book_name='Operating System Concepts',
                author_name='Silberschatz',
                isbn='978-1118063330',
                category='Computer Science',
                description='OS principles',
                total_copies=1,
                available_copies=0
            )
            b3 = Book(
                book_name='Database System Concepts',
                author_name='Silberschatz',
                isbn='978-0078022159',
                category='Information Technology',
                description='DBMS concepts',
                total_copies=3,
                available_copies=1
            )
            db.session.add_all([b1, b2, b3])
            db.session.commit()

    def tearDown(self):
        with app.app_context():
            db.session.remove()
            db.drop_all()

    def test_student_registration_and_login(self):
        # Register student
        response = self.client.post('/register', data={
            'student_name': 'Alex Johnson',
            'register_number': '2023MCA101',
            'department': 'Computer Applications (MCA)',
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
        response = self.client.post('/admin_login', data={
            'username': 'admin',
            'password': 'admin123'
        }, follow_redirects=True)
        self.assertIn(b'Logged in successfully as Administrator', response.data)

    def test_book_search_and_filter(self):
        # Search for Python
        response = self.client.get('/books?search=Python')
        self.assertIn(b'Python Programming', response.data)
        self.assertNotIn(b'Operating System Concepts', response.data)

        # Filter by Not Available
        response = self.client.get('/books?status=Not+Available')
        self.assertIn(b'Operating System Concepts', response.data)
        self.assertNotIn(b'Python Programming', response.data)

    def test_book_reservation_workflow_and_rules(self):
        # Register and login student
        self.client.post('/register', data={
            'student_name': 'Sam',
            'register_number': '2023MCA102',
            'department': 'MCA',
            'email': 'sam@college.edu',
            'password': 'pass'
        })
        self.client.post('/login', data={
            'email_or_reg': 'sam@college.edu',
            'password': 'pass'
        })

        # Try reserving out of stock book (#2)
        response = self.client.post('/reserve/2', follow_redirects=True)
        self.assertIn(b'not available for reservation', response.data)

        # Successful reservation of book #1
        response = self.client.post('/reserve/1', follow_redirects=True)
        self.assertIn(b'reserved successfully', response.data)

        with app.app_context():
            book = Book.query.get(1)
            self.assertEqual(book.available_copies, 4) # 5 - 1

        # Prevent duplicate active reservation of same book
        response = self.client.post('/reserve/1', follow_redirects=True)
        self.assertIn(b'already have an active reservation', response.data)

        # Cancel reservation #1
        response = self.client.post('/cancel_reservation/1', follow_redirects=True)
        self.assertIn(b'cancelled successfully', response.data)

        with app.app_context():
            book = Book.query.get(1)
            self.assertEqual(book.available_copies, 5) # Stock restored

    def test_admin_book_management_and_reservation_completion(self):
        # Admin login
        self.client.post('/admin_login', data={
            'username': 'admin',
            'password': 'admin123'
        })

        # Add book
        response = self.client.post('/admin/books/add', data={
            'book_name': 'Cloud Computing',
            'author_name': 'Rajkumar Buyya',
            'isbn': '978-0124114548',
            'category': 'Cloud',
            'description': 'Principles and Paradigms',
            'total_copies': 4
        }, follow_redirects=True)
        self.assertIn(b'Cloud Computing', response.data)

        # Register and login student to reserve book #3
        self.client.get('/logout')
        self.client.post('/register', data={
            'student_name': 'John',
            'register_number': '2023MCA103',
            'department': 'MCA',
            'email': 'john@college.edu',
            'password': 'pass'
        })
        self.client.post('/login', data={
            'email_or_reg': 'john@college.edu',
            'password': 'pass'
        })
        self.client.post('/reserve/3')

        # Admin login and mark reservation complete
        self.client.get('/logout')
        self.client.post('/admin_login', data={
            'username': 'admin',
            'password': 'admin123'
        })

        response = self.client.post('/admin/reservations/complete/1', follow_redirects=True)
        self.assertIn(b'marked as Completed', response.data)

        with app.app_context():
            res = Reservation.query.get(1)
            self.assertEqual(res.status, 'Completed')

if __name__ == '__main__':
    unittest.main()
