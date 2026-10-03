import unittest
from datetime import date
from app import app, db, Admin, Supplier, Product, Purchase, PurchaseItem

class SupplierPurchaseTestCase(unittest.TestCase):
    def setUp(self):
        app.config['TESTING'] = True
        app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
        app.config['WTF_CSRF_ENABLED'] = False
        self.client = app.test_client()

        with app.app_context():
            db.create_all()
            # Seed default admin
            admin = Admin(username='admin')
            admin.set_password('admin123')
            db.session.add(admin)

            # Seed sample supplier
            self.s1 = Supplier(supplier_name='John Doe', company_name='Alpha Tech Supplies', phone='1234567890', email='john@alphatech.com', address='123 Main St', status='Active')
            db.session.add(self.s1)

            # Seed sample products
            self.p1 = Product(product_name='Desk Lamp', product_code='PROD-100', category='Lighting', purchase_price=500.0, current_stock=10, min_stock_level=5)
            self.p2 = Product(product_name='USB Cable', product_code='PROD-101', category='Electronics', purchase_price=100.0, current_stock=2, min_stock_level=5) # Low stock
            self.p3 = Product(product_name='Monitor Stand', product_code='PROD-102', category='Furniture', purchase_price=1500.0, current_stock=0, min_stock_level=3) # Out of stock
            db.session.add_all([self.p1, self.p2, self.p3])

            db.session.commit()

    def tearDown(self):
        with app.app_context():
            db.session.remove()
            db.drop_all()

    def login_admin(self):
        return self.client.post('/login', data={
            'username': 'admin',
            'password': 'admin123'
        }, follow_redirects=True)

    def test_admin_login_and_logout(self):
        # Invalid login
        res = self.client.post('/login', data={'username': 'admin', 'password': 'wrongpassword'}, follow_redirects=True)
        self.assertIn(b'Invalid admin credentials', res.data)

        # Valid login
        res = self.login_admin()
        self.assertIn(b'Logged in successfully as Administrator', res.data)
        self.assertIn(b'Admin Dashboard', res.data)

        # Logout
        res = self.client.get('/logout', follow_redirects=True)
        self.assertIn(b'You have been logged out', res.data)

    def test_supplier_crud_and_search(self):
        self.login_admin()

        # Add supplier
        res = self.client.post('/suppliers/add', data={
            'supplier_name': 'Jane Smith',
            'company_name': 'Beta Logistics',
            'phone': '9876543210',
            'email': 'jane@betalogistics.com',
            'address': '456 Market St',
            'status': 'Active'
        }, follow_redirects=True)
        self.assertIn(b'Beta Logistics', res.data)

        # Search supplier
        res = self.client.get('/suppliers?search=Beta', follow_redirects=True)
        self.assertIn(b'Beta Logistics', res.data)

        # Edit supplier
        res = self.client.post('/suppliers/edit/1', data={
            'supplier_name': 'John Doe Updated',
            'company_name': 'Alpha Tech Supplies Updated',
            'phone': '1234567890',
            'email': 'john@alphatech.com',
            'address': '123 Main St',
            'status': 'Active'
        }, follow_redirects=True)
        self.assertIn(b'Updated', res.data)

        # View Supplier Details
        res = self.client.get('/suppliers/1', follow_redirects=True)
        self.assertIn(b'Alpha Tech Supplies Updated', res.data)

        # Delete Supplier
        res = self.client.post('/suppliers/delete/2', follow_redirects=True)
        self.assertIn(b'deleted successfully', res.data)

    def test_product_crud_and_stock_status(self):
        self.login_admin()

        # Add product
        res = self.client.post('/products/add', data={
            'product_name': 'Wireless Mouse',
            'product_code': 'PROD-200',
            'category': 'Electronics',
            'purchase_price': 450.0,
            'current_stock': 15,
            'min_stock_level': 5
        }, follow_redirects=True)
        self.assertIn(b'Wireless Mouse', res.data)

        # Check stock status properties
        with app.app_context():
            p1 = db.session.get(Product, 1)
            p2 = db.session.get(Product, 2)
            p3 = db.session.get(Product, 3)
            self.assertEqual(p1.stock_status, 'In Stock')
            self.assertEqual(p2.stock_status, 'Low Stock')
            self.assertEqual(p3.stock_status, 'Out of Stock')

        # Edit product
        res = self.client.post('/products/edit/1', data={
            'product_name': 'Desk Lamp Deluxe',
            'product_code': 'PROD-100',
            'category': 'Lighting',
            'purchase_price': 550.0,
            'current_stock': 8,
            'min_stock_level': 5
        }, follow_redirects=True)
        self.assertIn(b'Desk Lamp Deluxe', res.data)

        # Delete product
        res = self.client.post('/products/delete/3', follow_redirects=True)
        self.assertIn(b'deleted successfully', res.data)

    def test_purchase_workflow_and_automatic_stock_update(self):
        self.login_admin()

        # Create purchase with Pending status
        res = self.client.post('/purchases/add', data={
            'purchase_number': 'PUR-2001',
            'supplier_id': 1,
            'product_id': 1,
            'purchase_date': date.today().isoformat(),
            'quantity': 5,
            'purchase_price': 500.0,
            'status': 'Pending',
            'notes': 'Test order'
        }, follow_redirects=True)
        self.assertIn(b'PUR-2001', res.data)

        # Stock should remain 10 for product 1
        with app.app_context():
            p1 = db.session.get(Product, 1)
            self.assertEqual(p1.current_stock, 10)

        # Update purchase status to Received
        res = self.client.post('/purchases/status-update/1', data={'status': 'Received'}, follow_redirects=True)
        self.assertIn(b'updated to', res.data)

        # Stock should automatically increase by 5 (10 -> 15)
        with app.app_context():
            p1 = db.session.get(Product, 1)
            self.assertEqual(p1.current_stock, 15)

        # View Purchase Details
        res = self.client.get('/purchases/1', follow_redirects=True)
        self.assertIn(b'PUR-2001', res.data)

        # Check Purchase History view
        res = self.client.get('/purchase-history', follow_redirects=True)
        self.assertIn(b'PUR-2001', res.data)

        # View Supplier Details showing purchase history
        res = self.client.get('/suppliers/1', follow_redirects=True)
        self.assertIn(b'PUR-2001', res.data)
        self.assertIn(b'2500.00', res.data) # total amount for 5 * 500

if __name__ == '__main__':
    unittest.main()
