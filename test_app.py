import unittest
from datetime import date
from app import app, db, Admin, Enquiry, Lead, FollowUp, seed_default_data

class EnquiryLeadTestCase(unittest.TestCase):
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
                db.session.commit()

    def tearDown(self):
        with app.app_context():
            db.session.remove()
            db.drop_all()

    def test_home_page(self):
        response = self.client.get('/')
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Small Business Online Enquiry', response.data)

    def test_customer_enquiry_submission(self):
        response = self.client.post('/enquiry', data={
            'customer_name': 'Alice Johnson',
            'phone_number': '9876543210',
            'email': 'alice@example.com',
            'subject': 'Website Design Quote',
            'message': 'Need an e-commerce website for my boutique.',
            'enquiry_date': date.today().isoformat()
        }, follow_redirects=True)

        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Your enquiry has been submitted successfully.', response.data)
        self.assertIn(b'ENQ-1001', response.data)

        with app.app_context():
            enquiry = Enquiry.query.filter_by(ref_num='ENQ-1001').first()
            self.assertIsNotNone(enquiry)
            self.assertEqual(enquiry.customer_name, 'Alice Johnson')
            self.assertEqual(enquiry.status, 'New')

    def test_admin_login(self):
        # Invalid credentials
        response = self.client.post('/admin/login', data={
            'username': 'admin',
            'password': 'wrongpassword'
        }, follow_redirects=True)
        self.assertIn(b'Invalid admin username or password', response.data)

        # Valid credentials
        response = self.client.post('/admin/login', data={
            'username': 'admin',
            'password': 'admin123'
        }, follow_redirects=True)
        self.assertIn(b'Logged in successfully as Administrator', response.data)

    def test_admin_dashboard_and_enquiry_workflow(self):
        # Submit an enquiry first
        self.client.post('/enquiry', data={
            'customer_name': 'Bob Smith',
            'phone_number': '9123456789',
            'email': 'bob@example.com',
            'subject': 'SEO Consultation',
            'message': 'Interested in monthly SEO packages.',
            'enquiry_date': date.today().isoformat()
        })

        # Login as admin
        self.client.post('/admin/login', data={
            'username': 'admin',
            'password': 'admin123'
        })

        # Check admin dashboard
        response = self.client.get('/admin/dashboard')
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Total Enquiries', response.data)
        self.assertIn(b'Bob Smith', response.data)

        # View enquiry details
        with app.app_context():
            eq = Enquiry.query.filter_by(customer_name='Bob Smith').first()
            eq_id = eq.id

        response = self.client.get(f'/admin/enquiry/{eq_id}')
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'SEO Consultation', response.data)

        # Update enquiry status & response
        response = self.client.post(f'/admin/enquiry/{eq_id}/update', data={
            'status': 'Responded',
            'admin_response': 'Sent quotation via email.'
        }, follow_redirects=True)
        self.assertIn(b'updated successfully', response.data)

        with app.app_context():
            eq = Enquiry.query.get(eq_id)
            self.assertEqual(eq.status, 'Responded')
            self.assertEqual(eq.admin_response, 'Sent quotation via email.')

    def test_convert_enquiry_to_lead_and_lead_management(self):
        # Submit enquiry
        self.client.post('/enquiry', data={
            'customer_name': 'Charlie Brown',
            'phone_number': '9988776655',
            'email': 'charlie@example.com',
            'subject': 'Mobile App Development',
            'message': 'Need an iOS & Android app.',
            'enquiry_date': date.today().isoformat()
        })

        # Login admin
        self.client.post('/admin/login', data={
            'username': 'admin',
            'password': 'admin123'
        })

        with app.app_context():
            eq = Enquiry.query.filter_by(customer_name='Charlie Brown').first()
            eq_id = eq.id

        # Convert to lead
        response = self.client.post(f'/admin/enquiry/{eq_id}/convert', data={
            'requirement': 'Cross-platform React Native app.',
            'follow_up_date': date.today().isoformat(),
            'notes': 'Follow up next week with estimated cost.'
        }, follow_redirects=True)
        self.assertIn(b'converted to Lead successfully', response.data)

        with app.app_context():
            lead = Lead.query.filter_by(customer_name='Charlie Brown').first()
            self.assertIsNotNone(lead)
            self.assertEqual(lead.status, 'New Lead')
            self.assertEqual(lead.requirement, 'Cross-platform React Native app.')
            lead_id = lead.id

        # Update lead
        response = self.client.post(f'/admin/lead/{lead_id}/update', data={
            'status': 'Contacted',
            'requirement': 'Cross-platform React Native app with payment gateway.',
            'follow_up_date': date.today().isoformat(),
            'notes': 'Had introductory call.'
        }, follow_redirects=True)
        self.assertIn(b'updated', response.data)

        with app.app_context():
            lead = Lead.query.get(lead_id)
            self.assertEqual(lead.status, 'Contacted')

    def test_add_followup_and_delete(self):
        # Login admin
        self.client.post('/admin/login', data={
            'username': 'admin',
            'password': 'admin123'
        })

        # Create lead directly
        with app.app_context():
            lead = Lead(
                customer_name='Diana Prince',
                phone_number='9876543219',
                email='diana@example.com',
                requirement='Cloud CRM hosting.',
                status='New Lead'
            )
            db.session.add(lead)
            db.session.commit()
            lead_id = lead.id

        # Add follow-up
        response = self.client.post('/admin/followup/add', data={
            'lead_id': lead_id,
            'follow_up_date': date.today().isoformat(),
            'status': 'Follow-up',
            'notes': 'Sent formal proposal.'
        }, follow_redirects=True)
        self.assertIn(b'Follow-up added', response.data)

        with app.app_context():
            lead = Lead.query.get(lead_id)
            self.assertEqual(lead.status, 'Follow-up')
            self.assertEqual(len(lead.followups), 1)

        # Delete lead
        response = self.client.post(f'/admin/lead/{lead_id}/delete', follow_redirects=True)
        self.assertIn(b'deleted successfully', response.data)

        with app.app_context():
            lead = Lead.query.get(lead_id)
            self.assertIsNone(lead)

if __name__ == '__main__':
    unittest.main()
