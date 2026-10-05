import os
import io
import unittest
from app import app, db, Student, Admin, Document

class DocumentVerificationTestCase(unittest.TestCase):
    def setUp(self):
        app.config['TESTING'] = True
        app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
        app.config['WTF_CSRF_ENABLED'] = False
        app.config['UPLOAD_FOLDER'] = os.path.join(app.root_path, 'static', 'test_uploads')
        os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
        self.client = app.test_client()

        with app.app_context():
            db.create_all()
            # Seed default admin
            admin = Admin(username='admin')
            admin.set_password('admin123')
            db.session.add(admin)
            db.session.commit()

    def tearDown(self):
        with app.app_context():
            db.session.remove()
            db.drop_all()
        # Clean up test upload folder
        test_upload_dir = app.config['UPLOAD_FOLDER']
        if os.path.exists(test_upload_dir):
            for filename in os.listdir(test_upload_dir):
                file_path = os.path.join(test_upload_dir, filename)
                if os.path.isfile(file_path):
                    os.remove(file_path)

    def test_student_registration_and_login(self):
        # Register new student
        response = self.client.post('/register', data={
            'name': 'John Doe',
            'register_number': 'REG202401',
            'department': 'Master of Computer Applications (MCA)',
            'email': 'john@college.edu',
            'password': 'password123'
        }, follow_redirects=True)
        self.assertIn(b'Registration successful', response.data)

        # Login with registered student
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
        self.assertIn(b'Administrator logged in successfully', response.data)

    def test_document_upload_allowed_and_disallowed_extensions(self):
        # Register and login student
        self.client.post('/register', data={
            'name': 'Alice Smith',
            'register_number': 'REG202402',
            'department': 'MCA',
            'email': 'alice@college.edu',
            'password': 'password123'
        })
        self.client.post('/login', data={
            'email_or_reg': 'alice@college.edu',
            'password': 'password123'
        })

        # Try uploading disallowed extension (.exe)
        bad_file = (io.BytesIO(b'dummy content'), 'malicious.exe')
        response = self.client.post('/student/upload', data={
            'document_name': 'Hacked File',
            'document_type': 'ID Proof',
            'document_file': bad_file
        }, content_type='multipart/form-data', follow_redirects=True)
        self.assertIn(b'Invalid file format', response.data)

        # Upload valid PDF document
        valid_pdf = (io.BytesIO(b'%PDF-1.4 dummy pdf content'), 'marksheet.pdf')
        response = self.client.post('/student/upload', data={
            'document_name': '10th Marksheet',
            'document_type': 'Mark Sheet',
            'document_file': valid_pdf
        }, content_type='multipart/form-data', follow_redirects=True)
        self.assertIn(b'Document uploaded successfully', response.data)

        with app.app_context():
            doc = Document.query.filter_by(document_name='10th Marksheet').first()
            self.assertIsNotNone(doc)
            self.assertEqual(doc.status, 'Pending')
            self.assertEqual(doc.document_type, 'Mark Sheet')

    def test_admin_verification_rejection_and_deletion(self):
        # Setup student and document
        with app.app_context():
            student = Student(name='Bob', register_number='REG202403', department='MCA', email='bob@college.edu')
            student.set_password('pass')
            db.session.add(student)
            db.session.commit()

            doc = Document(
                student_id=student.id,
                document_name='Aadhar Card',
                document_type='ID Proof',
                filename='test_id.jpg',
                file_path='uploads/test_id.jpg',
                status='Pending'
            )
            db.session.add(doc)
            db.session.commit()
            doc_id = doc.id

        # Admin login
        self.client.post('/admin/login', data={
            'username': 'admin',
            'password': 'admin123'
        })

        # Admin rejects document with remark
        response = self.client.post(f'/admin/document/{doc_id}', data={
            'action': 'reject',
            'admin_remark': 'Document is not clear.'
        }, follow_redirects=True)
        self.assertIn(b'marked as Rejected', response.data)

        with app.app_context():
            doc = db.session.get(Document, doc_id)
            self.assertEqual(doc.status, 'Rejected')
            self.assertEqual(doc.admin_remark, 'Document is not clear.')

        # Admin verifies document with remark
        response = self.client.post(f'/admin/document/{doc_id}', data={
            'action': 'verify',
            'admin_remark': 'Clear copy received and verified.'
        }, follow_redirects=True)
        self.assertIn(b'marked as Verified', response.data)

        with app.app_context():
            doc = db.session.get(Document, doc_id)
            self.assertEqual(doc.status, 'Verified')
            self.assertEqual(doc.admin_remark, 'Clear copy received and verified.')

        # Admin deletes document
        response = self.client.post(f'/admin/document/delete/{doc_id}', follow_redirects=True)
        self.assertIn(b'deleted successfully', response.data)

        with app.app_context():
            doc = db.session.get(Document, doc_id)
            self.assertIsNone(doc)

if __name__ == '__main__':
    unittest.main()
