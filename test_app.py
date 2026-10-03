import unittest
from datetime import date
from app import app, db, Admin, Consumable, StockHistory

class LabConsumablesTestCase(unittest.TestCase):
    def setUp(self):
        app.config['TESTING'] = True
        app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
        app.config['WTF_CSRF_ENABLED'] = False
        self.client = app.test_client()

        with app.app_context():
            db.create_all()
            if not Admin.query.filter_by(username='admin').first():
                admin = Admin(username='admin')
                admin.set_password('admin123')
                db.session.add(admin)

            c1 = Consumable(
                consumable_name='Ethanol 99%',
                item_code='CHEM-01',
                category='Chemicals',
                quantity=20,
                minimum_stock=5,
                unit='Bottles',
                lab_name='Chemistry Lab',
                added_date=date.today()
            )
            c2 = Consumable(
                consumable_name='Glass Beaker 100ml',
                item_code='GLAS-01',
                category='Glassware',
                quantity=3,
                minimum_stock=5,
                unit='Pieces',
                lab_name='Chemistry Lab',
                added_date=date.today()
            )
            c3 = Consumable(
                consumable_name='A4 Paper',
                item_code='STAT-01',
                category='Stationery',
                quantity=0,
                minimum_stock=2,
                unit='Reams',
                lab_name='Computer Lab 1',
                added_date=date.today()
            )
            db.session.add_all([c1, c2, c3])
            db.session.commit()

    def tearDown(self):
        with app.app_context():
            db.session.remove()
            db.drop_all()

    def login_admin(self):
        return self.client.post('/admin/login', data={
            'username': 'admin',
            'password': 'admin123'
        }, follow_redirects=True)

    def test_stock_status_property(self):
        with app.app_context():
            c1 = Consumable.query.filter_by(item_code='CHEM-01').first()
            c2 = Consumable.query.filter_by(item_code='GLAS-01').first()
            c3 = Consumable.query.filter_by(item_code='STAT-01').first()

            self.assertEqual(c1.stock_status, 'In Stock')
            self.assertEqual(c2.stock_status, 'Low Stock')
            self.assertEqual(c3.stock_status, 'Out of Stock')

    def test_admin_login_and_logout(self):
        res = self.client.post('/admin/login', data={
            'username': 'admin',
            'password': 'wrongpassword'
        }, follow_redirects=True)
        self.assertIn(b'Invalid username or password', res.data)

        res = self.login_admin()
        self.assertIn(b'Logged in successfully', res.data)

        res = self.client.get('/logout', follow_redirects=True)
        self.assertIn(b'logged out successfully', res.data)

    def test_protected_routes(self):
        res = self.client.get('/dashboard', follow_redirects=True)
        self.assertIn(b'Please log in as Admin', res.data)

    def test_add_consumable(self):
        self.login_admin()
        res = self.client.post('/consumables/add', data={
            'consumable_name': 'Test Resistors',
            'item_code': 'ELEC-99',
            'category': 'Electronic Components',
            'quantity': '50',
            'minimum_stock': '10',
            'unit': 'Packs',
            'lab_name': 'Electronics Lab',
            'added_date': date.today().isoformat()
        }, follow_redirects=True)
        self.assertIn(b'added successfully', res.data)

        with app.app_context():
            item = Consumable.query.filter_by(item_code='ELEC-99').first()
            self.assertIsNotNone(item)
            self.assertEqual(item.quantity, 50)
            self.assertEqual(item.stock_status, 'In Stock')

    def test_edit_consumable(self):
        self.login_admin()
        res = self.client.post('/consumables/edit/1', data={
            'consumable_name': 'Ethanol Pure 99.9%',
            'item_code': 'CHEM-01',
            'category': 'Chemicals',
            'minimum_stock': '10',
            'unit': 'Bottles',
            'lab_name': 'Organic Chemistry Lab'
        }, follow_redirects=True)
        self.assertIn(b'updated successfully', res.data)

        with app.app_context():
            c = db.session.get(Consumable, 1)
            self.assertEqual(c.consumable_name, 'Ethanol Pure 99.9%')
            self.assertEqual(c.lab_name, 'Organic Chemistry Lab')

    def test_stock_update_add_and_use(self):
        self.login_admin()

        res = self.client.post('/stock/update', data={
            'consumable_id': '2',
            'action_type': 'add',
            'quantity': '10',
            'transaction_date': date.today().isoformat(),
            'remarks': 'New shipment received'
        }, follow_redirects=True)
        self.assertIn(b'Successfully added 10', res.data)

        with app.app_context():
            c2 = db.session.get(Consumable, 2)
            self.assertEqual(c2.quantity, 13)
            self.assertEqual(c2.stock_status, 'In Stock')

        res = self.client.post('/stock/update', data={
            'consumable_id': '2',
            'action_type': 'use',
            'quantity': '5',
            'transaction_date': date.today().isoformat(),
            'remarks': 'Used in lab experiment'
        }, follow_redirects=True)
        self.assertIn(b'Successfully deducted 5', res.data)

        with app.app_context():
            c2 = db.session.get(Consumable, 2)
            self.assertEqual(c2.quantity, 8)

    def test_negative_stock_prevention(self):
        self.login_admin()

        res = self.client.post('/stock/update', data={
            'consumable_id': '2',
            'action_type': 'use',
            'quantity': '100',
            'transaction_date': date.today().isoformat(),
            'remarks': 'Excessive deduction test'
        }, follow_redirects=True)
        self.assertIn(b'Negative stock is not allowed', res.data)

        with app.app_context():
            c2 = db.session.get(Consumable, 2)
            self.assertEqual(c2.quantity, 3)

    def test_consumable_deletion(self):
        self.login_admin()
        res = self.client.post('/consumables/delete/3', follow_redirects=True)
        self.assertIn(b'deleted successfully', res.data)

        with app.app_context():
            c3 = db.session.get(Consumable, 3)
            self.assertIsNone(c3)

if __name__ == '__main__':
    unittest.main()
