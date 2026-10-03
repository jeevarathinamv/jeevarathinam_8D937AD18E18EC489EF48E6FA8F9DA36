import unittest
from datetime import date
from app import app, db, Admin, Customer, Product, Sale, SaleItem

class SmallBusinessSalesTestCase(unittest.TestCase):
    def setUp(self):
        app.config['TESTING'] = True
        app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
        app.config['WTF_CSRF_ENABLED'] = False
        self.client = app.test_client()

        with app.app_context():
            db.create_all()
            # Seed admin
            admin = Admin(username='admin', name='Test Admin')
            admin.set_password('admin123')
            db.session.add(admin)

            # Seed Customer
            self.c1 = Customer(
                name='John Doe',
                phone='9876543210',
                email='john@example.com',
                address='123 Street',
                customer_type='Regular',
                registration_date=date.today()
            )
            db.session.add(self.c1)

            # Seed Product
            self.p1 = Product(
                name='Test Mouse',
                product_code='PRD-001',
                category='Electronics',
                selling_price=500.0,
                available_stock=10,
                min_stock_level=3
            )
            self.p2 = Product(
                name='Out of Stock Item',
                product_code='PRD-002',
                category='Gadgets',
                selling_price=1000.0,
                available_stock=0,
                min_stock_level=2
            )
            db.session.add_all([self.p1, self.p2])
            db.session.commit()

    def tearDown(self):
        with app.app_context():
            db.session.remove()
            db.drop_all()

    def test_admin_login(self):
        response = self.client.post('/login', data={
            'username': 'admin',
            'password': 'admin123'
        }, follow_redirects=True)
        self.assertIn(b'Logged in successfully as Administrator', response.data)

    def test_customer_management(self):
        # Login first
        self.client.post('/login', data={'username': 'admin', 'password': 'admin123'})

        # Add customer
        response = self.client.post('/customers/add', data={
            'name': 'Alice Smith',
            'phone': '9123456789',
            'email': 'alice@example.com',
            'address': '456 Avenue',
            'customer_type': 'VIP'
        }, follow_redirects=True)
        self.assertIn(b'added successfully', response.data)

        # Search customer
        response = self.client.get('/customers?search=Alice', follow_redirects=True)
        self.assertIn(b'Alice Smith', response.data)

        # Edit customer
        response = self.client.post('/customers/edit/1', data={
            'name': 'John Doe Updated',
            'phone': '9876543210',
            'email': 'john@example.com',
            'address': '123 Street Updated',
            'customer_type': 'VIP'
        }, follow_redirects=True)
        self.assertIn(b'updated successfully', response.data)

    def test_product_management_and_stock_status(self):
        self.client.post('/login', data={'username': 'admin', 'password': 'admin123'})

        # Add product
        response = self.client.post('/products/add', data={
            'name': 'Keyboard',
            'product_code': 'PRD-003',
            'category': 'Electronics',
            'selling_price': 1500.0,
            'available_stock': 2,
            'min_stock_level': 5
        }, follow_redirects=True)
        self.assertIn(b'added successfully', response.data)

        with app.app_context():
            p = db.session.get(Product, 3)
            self.assertEqual(p.stock_status, 'Low Stock')

            p_out = db.session.get(Product, 2)
            self.assertEqual(p_out.stock_status, 'Out of Stock')

    def test_sale_creation_and_automatic_stock_deduction(self):
        self.client.post('/login', data={'username': 'admin', 'password': 'admin123'})

        # Create Sale
        response = self.client.post('/sales/create', data={
            'customer_id': 1,
            'product_id': 1,
            'quantity': 3,
            'selling_price': 500.0,
            'discount': 100.0,
            'payment_status': 'Paid',
            'sale_date': date.today().isoformat()
        }, follow_redirects=True)
        self.assertIn(b'created successfully', response.data)

        # Verify stock reduced from 10 to 7
        with app.app_context():
            p = db.session.get(Product, 1)
            self.assertEqual(p.available_stock, 7)

            sale = db.session.get(Sale, 1)
            self.assertEqual(sale.total_amount, 1500.0)
            self.assertEqual(sale.grand_total, 1400.0)

    def test_insufficient_stock_prevent_sale(self):
        self.client.post('/login', data={'username': 'admin', 'password': 'admin123'})

        # Try selling out of stock product
        response = self.client.post('/sales/create', data={
            'customer_id': 1,
            'product_id': 2,
            'quantity': 1,
            'selling_price': 1000.0,
            'discount': 0.0,
            'payment_status': 'Paid',
            'sale_date': date.today().isoformat()
        }, follow_redirects=True)
        self.assertIn(b'Insufficient stock', response.data)

if __name__ == '__main__':
    unittest.main()
