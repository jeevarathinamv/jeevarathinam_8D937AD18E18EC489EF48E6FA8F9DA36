import unittest
from datetime import date
from app import app, db, Student, Settings, recalculate_allocations

class CollegeAdmissionTestCase(unittest.TestCase):
    def setUp(self):
        app.config['TESTING'] = True
        app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
        app.config['WTF_CSRF_ENABLED'] = False
        self.client = app.test_client()

        with app.app_context():
            db.create_all()
            # Initialize default seat settings: OC=9, BC=8, BCM=1, MBC=6, SC=5, SCA=1
            Settings.get_settings()

    def tearDown(self):
        with app.app_context():
            db.session.remove()
            db.drop_all()

    def test_settings_initialization(self):
        with app.app_context():
            settings = Settings.get_settings()
            self.assertEqual(settings.oc_seats, 9)
            self.assertEqual(settings.bc_seats, 8)
            self.assertEqual(settings.bcm_seats, 1)
            self.assertEqual(settings.mbc_seats, 6)
            self.assertEqual(settings.sc_seats, 5)
            self.assertEqual(settings.sca_seats, 1)

    def test_add_and_view_student(self):
        response = self.client.post('/students/add', data={
            'application_no': 'APP001',
            'name': 'Rahul Sharma',
            'gender': 'Male',
            'community': 'BC',
            'marks': '92.5',
            'rank_no': '1',
            'remark': 'First candidate'
        }, follow_redirects=True)
        self.assertIn(b'Rahul Sharma', response.data)

        with app.app_context():
            student = Student.query.filter_by(application_no='APP001').first()
            self.assertIsNotNone(student)
            self.assertEqual(student.status, 'Allocated')
            self.assertEqual(student.allocated_category, 'BC')

    def test_automatic_seat_allocation_logic(self):
        with app.app_context():
            # Add 2 BC students when BC has 1 seat only
            settings = Settings.get_settings()
            settings.bc_seats = 1
            settings.oc_seats = 1
            db.session.commit()

            s1 = Student(application_no='A1', name='Student 1', gender='Male', community='BC', marks=95.0, rank_no=1)
            s2 = Student(application_no='A2', name='Student 2', gender='Female', community='BC', marks=90.0, rank_no=2)
            s3 = Student(application_no='A3', name='Student 3', gender='Male', community='BC', marks=85.0, rank_no=3)
            db.session.add_all([s1, s2, s3])
            db.session.commit()

            recalculate_allocations()

            # s1 gets BC
            self.assertEqual(s1.allocated_category, 'BC')
            self.assertEqual(s1.status, 'Allocated')

            # s2 gets OC (since BC is full)
            self.assertEqual(s2.allocated_category, 'OC')
            self.assertEqual(s2.status, 'Allocated')

            # s3 gets Waiting (since BC and OC are full)
            self.assertIsNone(s3.allocated_category)
            self.assertEqual(s3.status, 'Waiting')

    def test_admission_process(self):
        self.client.post('/students/add', data={
            'application_no': 'APP100',
            'name': 'Anita Roy',
            'gender': 'Female',
            'community': 'OC',
            'marks': '98.0',
            'rank_no': '1'
        })

        with app.app_context():
            student = Student.query.filter_by(application_no='APP100').first()
            student_id = student.id

        response = self.client.post(f'/admission/admit/{student_id}', follow_redirects=True)
        self.assertIn(b'admitted successfully', response.data)

        with app.app_context():
            student = db.session.get(Student, student_id)
            self.assertEqual(student.status, 'Admitted')
            self.assertEqual(student.admission_date, date.today())

    def test_dashboard_routes_and_gender_stats(self):
        # Add male and female students
        self.client.post('/students/add', data={
            'application_no': 'BOY1',
            'name': 'John Doe',
            'gender': 'Male',
            'community': 'BC',
            'marks': '85.0',
            'rank_no': '1'
        })
        self.client.post('/students/add', data={
            'application_no': 'GIRL1',
            'name': 'Jane Doe',
            'gender': 'Female',
            'community': 'SC',
            'marks': '88.0',
            'rank_no': '2'
        })

        response = self.client.get('/')
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Boys Statistics', response.data)
        self.assertIn(b'Girls Statistics', response.data)

    def test_edit_and_delete_student_recalculates(self):
        self.client.post('/students/add', data={
            'application_no': 'APP200',
            'name': 'Temp Student',
            'gender': 'Male',
            'community': 'MBC',
            'marks': '75.0',
            'rank_no': '10'
        })

        with app.app_context():
            student = Student.query.filter_by(application_no='APP200').first()
            s_id = student.id

        # Edit student
        response = self.client.post(f'/students/edit/{s_id}', data={
            'application_no': 'APP200',
            'name': 'Updated Student',
            'gender': 'Male',
            'community': 'MBC',
            'marks': '99.0',
            'rank_no': '1',
            'remark': 'Rank upgraded'
        }, follow_redirects=True)
        self.assertIn(b'Updated Student', response.data)

        # Delete student
        response = self.client.post(f'/students/delete/{s_id}', follow_redirects=True)
        self.assertIn(b'deleted successfully', response.data)

        with app.app_context():
            student = db.session.get(Student, s_id)
            self.assertIsNone(student)

    def test_settings_update(self):
        response = self.client.post('/settings', data={
            'oc_seats': '10',
            'bc_seats': '10',
            'bcm_seats': '2',
            'mbc_seats': '5',
            'sc_seats': '5',
            'sca_seats': '1'
        }, follow_redirects=True)
        self.assertIn(b'updated successfully', response.data)

        with app.app_context():
            settings = Settings.get_settings()
            self.assertEqual(settings.oc_seats, 10)
            self.assertEqual(settings.bc_seats, 10)

if __name__ == '__main__':
    unittest.main()
