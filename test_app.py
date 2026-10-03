import unittest
from datetime import date
from app import app, db, Admin, Item, StockHistory

class LaboratoryStockTestCase(unittest.TestCase):
    def setUp(self):
        app.config['TESTING'] = True
        app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
        app.config['WTF_CSRF_ENABLED'] = False
        self.client = app.test_client()

        with app.app_context():
            db.create_all()
            # Create test admin
            admin = Admin(username='admin')
            admin.set_password('admin123')
            db.session.add(admin)

            # Create test items
            item1 = Item(item_name='Arduino Uno', item_code='ELEC-001', category='Electronic Components', quantity=10, minimum_stock=5, unit='Pcs', location='Cabinet A')
            item2 = Item(item_name='Desktop PC', item_code='COMP-001', category='Computer Equipment', quantity=2, minimum_stock=5, unit='Units', location='Lab 1')
            item3 = Item(item_name='Oscilloscope', item_code='LAB-001', category='Laboratory Equipment', quantity=0, minimum_stock=2, unit='Units', location='Bay 1')
            db.session.add_all([item1, item2, item3])
            db.session.commit()

    def tearDown(self):
        with app.app_context():
            db.session.remove()
            db.drop_all()

    def test_admin_login_logout(self):
        # Invalid login
        response = self.client.post('/admin/login', data={'username': 'admin', 'password': 'wrongpassword'}, follow_redirects=True)
        self.assertIn(b'Invalid username or password', response.data)

        # Valid login
        response = self.client.post('/admin/login', data={'username': 'admin', 'password': 'admin123'}, follow_redirects=True)
        self.assertIn(b'Welcome back, admin!', response.data)

        # Logout
        response = self.client.get('/admin/logout', follow_redirects=True)
        self.assertIn(b'logged out successfully', response.data)

    def test_stock_status_calculation(self):
        with app.app_context():
            item1 = db.session.query(Item).filter_by(item_code='ELEC-001').first()
            item2 = db.session.query(Item).filter_by(item_code='COMP-001').first()
            item3 = db.session.query(Item).filter_by(item_code='LAB-001').first()

            self.assertEqual(item1.stock_status, 'In Stock')
            self.assertEqual(item2.stock_status, 'Low Stock')
            self.assertEqual(item3.stock_status, 'Out of Stock')

    def test_add_and_edit_item(self):
        # Admin login
        self.client.post('/admin/login', data={'username': 'admin', 'password': 'admin123'})

        # Add item
        response = self.client.post('/admin/items/add', data={
            'item_name': 'Multimeter',
            'item_code': 'LAB-002',
            'category': 'Laboratory Equipment',
            'quantity': 15,
            'minimum_stock': 3,
            'unit': 'Units',
            'location': 'Testing Bench',
            'added_date': date.today().isoformat()
        }, follow_redirects=True)
        self.assertIn(b'added successfully', response.data)

        # Verify added item
        with app.app_context():
            item = db.session.query(Item).filter_by(item_code='LAB-002').first()
            self.assertIsNotNone(item)
            self.assertEqual(item.item_name, 'Multimeter')
            self.assertEqual(item.quantity, 15)

        # Edit item
        response = self.client.post(f'/admin/items/edit/{item.id}', data={
            'item_name': 'Digital Multimeter Pro',
            'item_code': 'LAB-002',
            'category': 'Laboratory Equipment',
            'minimum_stock': 4,
            'unit': 'Units',
            'location': 'Testing Bench 2'
        }, follow_redirects=True)
        self.assertIn(b'updated successfully', response.data)

    def test_stock_update_addition_and_reduction(self):
        # Admin login
        self.client.post('/admin/login', data={'username': 'admin', 'password': 'admin123'})

        # Add stock (+5)
        response = self.client.post('/admin/stock/update', data={
            'item_id': 1,
            'transaction_type': 'Stock Added',
            'quantity': 5,
            'remarks': 'New batch received'
        }, follow_redirects=True)
        self.assertIn(b'Stock updated successfully', response.data)

        with app.app_context():
            item = db.session.get(Item, 1)
            self.assertEqual(item.quantity, 15)  # 10 + 5

        # Reduce stock (-3)
        response = self.client.post('/admin/stock/update', data={
            'item_id': 1,
            'transaction_type': 'Stock Used',
            'quantity': 3,
            'remarks': 'Issued to students'
        }, follow_redirects=True)
        self.assertIn(b'Stock updated successfully', response.data)

        with app.app_context():
            item = db.session.get(Item, 1)
            self.assertEqual(item.quantity, 12)  # 15 - 3

    def test_prevent_negative_stock(self):
        # Admin login
        self.client.post('/admin/login', data={'username': 'admin', 'password': 'admin123'})

        # Attempt to reduce stock by 50 when only 10 available
        response = self.client.post('/admin/stock/update', data={
            'item_id': 1,
            'transaction_type': 'Stock Used',
            'quantity': 50,
            'remarks': 'Excess reduction attempt'
        }, follow_redirects=True)
        self.assertIn(b'Cannot reduce stock by 50', response.data)

        with app.app_context():
            item = db.session.get(Item, 1)
            self.assertEqual(item.quantity, 10)  # Unchanged

if __name__ == '__main__':
    unittest.main()
