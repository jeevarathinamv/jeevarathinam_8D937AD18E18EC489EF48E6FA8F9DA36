import unittest
from datetime import date
from app import app, db, Student, Computer, FaultReport, Admin

class LabFaultReporterTestCase(unittest.TestCase):
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

            # Seed Computers
            comp1 = Computer(computer_number='COMP-101', lab_name='Computer Lab 1', computer_name='Dell OptiPlex 3080', ip_address='192.168.1.101', status='Working')
            comp2 = Computer(computer_number='COMP-102', lab_name='Computer Lab 1', computer_name='HP ProDesk', ip_address='192.168.1.102', status='Working')
            db.session.add_all([comp1, comp2])
            db.session.commit()

    def tearDown(self):
        with app.app_context():
            db.session.remove()
            db.drop_all()

    def test_student_registration_and_login(self):
        # Register student
        response = self.client.post('/register', data={
            'student_name': 'John Doe',
            'register_number': 'REG101',
            'department': 'Computer Applications (MCA)',
            'email': 'john@college.edu',
            'password': 'password123'
        }, follow_redirects=True)
        self.assertIn(b'Registration successful', response.data)

        # Login student
        response = self.client.post('/login', data={
            'email_or_reg': 'john@college.edu',
            'password': 'password123'
        }, follow_redirects=True)
        self.assertIn(b'Welcome back, John Doe!', response.data)

    def test_admin_login(self):
        response = self.client.post('/admin/login', data={
            'username': 'admin',
            'password': 'admin123'
        }, follow_redirects=True)
        self.assertIn(b'Logged in successfully as Administrator', response.data)

    def test_report_fault_and_complaint_id_generation(self):
        # Register and login student
        self.client.post('/register', data={
            'student_name': 'Alice Smith',
            'register_number': 'REG102',
            'department': 'MCA',
            'email': 'alice@college.edu',
            'password': 'password123'
        })
        self.client.post('/login', data={
            'email_or_reg': 'REG102',
            'password': 'password123'
        })

        # Submit fault report
        response = self.client.post('/student/report_fault', data={
            'lab_name': 'Computer Lab 1',
            'computer_number': 'COMP-101',
            'fault_type': 'Keyboard Problem',
            'problem_description': 'Spacebar key is broken and sticking.',
            'report_date': date.today().isoformat()
        }, follow_redirects=True)

        self.assertIn(b'Fault report submitted successfully!', response.data)
        self.assertIn(b'CMP-', response.data)

        with app.app_context():
            report = FaultReport.query.filter_by(computer_number='COMP-101').first()
            self.assertIsNotNone(report)
            self.assertTrue(report.complaint_id.startswith('CMP-'))
            self.assertEqual(report.status, 'Pending')

    def test_admin_update_status_and_resolved_date(self):
        # Register and report fault
        self.client.post('/register', data={
            'student_name': 'Bob',
            'register_number': 'REG103',
            'department': 'MCA',
            'email': 'bob@college.edu',
            'password': 'password123'
        })
        self.client.post('/login', data={
            'email_or_reg': 'bob@college.edu',
            'password': 'password123'
        })
        self.client.post('/student/report_fault', data={
            'lab_name': 'Computer Lab 1',
            'computer_number': 'COMP-102',
            'fault_type': 'Monitor Problem',
            'problem_description': 'Screen flicker issues.',
            'report_date': date.today().isoformat()
        })

        # Logout student and login admin
        self.client.get('/logout')
        self.client.post('/admin/login', data={
            'username': 'admin',
            'password': 'admin123'
        })

        # Admin updates complaint status to In Progress
        response = self.client.post('/admin/update_report/1', data={
            'status': 'In Progress',
            'admin_remarks': 'Technician assigned to inspect display cable.'
        }, follow_redirects=True)
        self.assertIn(b'In Progress', response.data)

        # Admin resolves complaint
        response = self.client.post('/admin/update_report/1', data={
            'status': 'Resolved',
            'admin_remarks': 'Monitor cable replaced. Working properly.'
        }, follow_redirects=True)
        self.assertIn(b'Resolved', response.data)

        with app.app_context():
            report = db.session.get(FaultReport, 1)
            self.assertEqual(report.status, 'Resolved')
            self.assertEqual(report.resolved_date, date.today())
            self.assertEqual(report.admin_remarks, 'Monitor cable replaced. Working properly.')

    def test_search_and_filter_reports(self):
        # Setup student & report
        self.client.post('/register', data={
            'student_name': 'Charlie',
            'register_number': 'REG104',
            'department': 'MCA',
            'email': 'charlie@college.edu',
            'password': 'pass'
        })
        self.client.post('/login', data={
            'email_or_reg': 'REG104',
            'password': 'pass'
        })
        self.client.post('/student/report_fault', data={
            'lab_name': 'Computer Lab 1',
            'computer_number': 'COMP-101',
            'fault_type': 'Internet Problem',
            'problem_description': 'No network connectivity.',
            'report_date': date.today().isoformat()
        })

        # Admin search
        self.client.get('/logout')
        self.client.post('/admin/login', data={'username': 'admin', 'password': 'admin123'})

        # Search by Fault Type
        response = self.client.get('/admin/manage_reports?search=Internet')
        self.assertIn(b'COMP-101', response.data)

        # Search by Status
        response = self.client.get('/admin/manage_reports?status=Pending')
        self.assertIn(b'COMP-101', response.data)

        # Non-matching search
        response = self.client.get('/admin/manage_reports?search=NonExistent')
        self.assertIn(b'No Fault Reports Match Your Filter Criteria', response.data)

    def test_computer_crud_operations(self):
        self.client.post('/admin/login', data={'username': 'admin', 'password': 'admin123'})

        # Add Computer
        response = self.client.post('/admin/add_computer', data={
            'computer_number': 'COMP-201',
            'lab_name': 'MCA Lab 2',
            'computer_name': 'Lenovo ThinkStation',
            'ip_address': '192.168.2.201',
            'status': 'Working'
        }, follow_redirects=True)
        self.assertIn(b'COMP-201 added successfully', response.data)

        # Edit Computer
        response = self.client.post('/admin/edit_computer/3', data={
            'computer_number': 'COMP-201-UPDATED',
            'lab_name': 'MCA Lab 2',
            'computer_name': 'Lenovo ThinkStation i7',
            'ip_address': '192.168.2.201',
            'status': 'Under Maintenance'
        }, follow_redirects=True)
        self.assertIn(b'updated successfully', response.data)

        # Delete Computer
        response = self.client.post('/admin/delete_computer/3', follow_redirects=True)
        self.assertIn(b'deleted successfully', response.data)

    def test_student_management_and_deletion(self):
        # Register student
        self.client.post('/register', data={
            'student_name': 'David',
            'register_number': 'REG105',
            'department': 'MCA',
            'email': 'david@college.edu',
            'password': 'pass'
        })

        # Admin login & view students
        self.client.post('/admin/login', data={'username': 'admin', 'password': 'admin123'})
        response = self.client.get('/admin/manage_students')
        self.assertIn(b'David', response.data)

        # Delete student
        response = self.client.post('/admin/delete_student/1', follow_redirects=True)
        self.assertIn(b'Student account deleted successfully', response.data)

if __name__ == '__main__':
    unittest.main()
