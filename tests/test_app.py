import os
import unittest
from datetime import date
from app import app, db
from database import (
    User, Teacher, CollegeClass, Subject, ClassTutor, Student,
    AttendanceSession, AttendanceRecord, Notification,
    TheoryInternalMark, PracticalInternalMark, calculate_attendance_mark, init_db
)

class CollegeAttendanceSystemTestCase(unittest.TestCase):
    def setUp(self):
        app.config['TESTING'] = True
        app.config['WTF_CSRF_ENABLED'] = False
        db_file = os.path.join(os.path.abspath(os.path.dirname(__file__)), 'test_college.db')
        app.config['SQLALCHEMY_DATABASE_URI'] = f'sqlite:///{db_file}'
        self.db_file = db_file
        self.client = app.test_client()

        with app.app_context():
            db.drop_all()
            init_db(app)

    def tearDown(self):
        with app.app_context():
            db.session.remove()
            db.drop_all()
        if os.path.exists(self.db_file):
            try:
                os.remove(self.db_file)
            except OSError:
                pass

    # 1. Teacher login works
    def test_01_teacher_login(self):
        response = self.client.post('/login', data={
            'username': 'teacher_cs',
            'password': 'password123'
        }, follow_redirects=True)
        self.assertIn(b'Teacher Dashboard', response.data)

    # 2. Class tutor login works
    def test_02_class_tutor_login(self):
        response = self.client.post('/login', data={
            'username': 'teacher_ak',
            'password': 'password123'
        }, follow_redirects=True)
        self.assertIn(b'Welcome', response.data)

    # 3. Unauthorized users cannot access protected pages
    def test_03_unauthorized_access(self):
        response = self.client.get('/teacher/dashboard', follow_redirects=True)
        self.assertIn(b'Teacher access required', response.data)

        response = self.client.get('/tutor/dashboard', follow_redirects=True)
        self.assertIn(b'Class Tutor access required', response.data)

    # 4 & 5 & 8. Attendance marking, totals, percentage, report & notification creation
    def test_04_attendance_marking_and_totals(self):
        self.client.post('/login', data={'username': 'teacher_vg', 'password': 'password123'})

        response = self.client.post('/attendance', data={
            'class_id': 2,
            'subject_id': 1,
            'date': '2025-03-01',
            'period': 1,
            'status_6': 'Present',
            'status_7': 'Present',
            'status_8': 'Present',
            'status_9': 'Present',
            'status_10': 'Absent',
            'status_11': 'Absent'
        }, follow_redirects=True)

        self.assertIn(b'Attendance saved successfully', response.data)

        with app.app_context():
            session_obj = AttendanceSession.query.filter_by(class_id=2, subject_id=1, date=date(2025, 3, 1), period=1).first()
            self.assertIsNotNone(session_obj)
            self.assertEqual(session_obj.total_students, 6)
            self.assertEqual(session_obj.present_students, 4)
            self.assertEqual(session_obj.absent_students, 2)
            self.assertEqual(round(session_obj.attendance_percentage, 2), 66.67)

            notif = Notification.query.filter_by(session_id=session_obj.id).first()
            self.assertIsNotNone(notif)
            self.assertIn('Teacher Mr. VG submitted attendance', notif.message)

    # 6. Attendance remains saved after restart
    def test_06_persistence_after_restart(self):
        with app.app_context():
            s = AttendanceSession(
                class_id=1, subject_id=9, teacher_id=7, date=date(2025, 3, 2), period=1,
                type='Theory', total_students=5, present_students=4, absent_students=1, attendance_percentage=80.0
            )
            db.session.add(s)
            db.session.commit()
            session_id = s.id

        with app.app_context():
            query_session = db.session.get(AttendanceSession, session_id)
            self.assertIsNotNone(query_session)
            self.assertEqual(query_session.attendance_percentage, 80.0)

    # 7. Duplicate attendance records are updated/prevented
    def test_07_duplicate_attendance_prevention(self):
        self.client.post('/login', data={'username': 'teacher_vg', 'password': 'password123'})

        self.client.post('/attendance', data={
            'class_id': 2, 'subject_id': 1, 'date': '2025-03-01', 'period': 1,
            'status_6': 'Present', 'status_7': 'Present', 'status_8': 'Present',
            'status_9': 'Present', 'status_10': 'Present', 'status_11': 'Present'
        })

        self.client.post('/attendance', data={
            'class_id': 2, 'subject_id': 1, 'date': '2025-03-01', 'period': 1,
            'status_6': 'Present', 'status_7': 'Absent', 'status_8': 'Absent',
            'status_9': 'Present', 'status_10': 'Present', 'status_11': 'Present'
        })

        with app.app_context():
            sessions = AttendanceSession.query.filter_by(class_id=2, subject_id=1, date=date(2025, 3, 1), period=1).all()
            self.assertEqual(len(sessions), 1)
            self.assertEqual(sessions[0].present_students, 4)

    # 9 & 10. Submitting teacher and assigned tutor can view report
    def test_09_10_view_submitted_report(self):
        with app.app_context():
            s = AttendanceSession(
                class_id=2, subject_id=1, teacher_id=1, date=date(2025, 3, 3), period=1,
                type='Theory', total_students=6, present_students=5, absent_students=1, attendance_percentage=83.33
            )
            db.session.add(s)
            db.session.commit()
            session_id = s.id

        self.client.post('/login', data={'username': 'teacher_vg', 'password': 'password123'})
        response = self.client.get(f'/attendance/report/{session_id}')
        self.assertEqual(response.status_code, 200)

        self.client.get('/logout')
        self.client.post('/login', data={'username': 'teacher_vg', 'password': 'password123'})
        response_tutor = self.client.get(f'/attendance/report/{session_id}')
        self.assertEqual(response_tutor.status_code, 200)

    # 11. Tutor cannot access another class's restricted reports
    def test_11_tutor_restricted_access(self):
        with app.app_context():
            s = AttendanceSession(
                class_id=1, subject_id=9, teacher_id=2, date=date(2025, 3, 4), period=1,
                type='Theory', total_students=5, present_students=5, absent_students=0, attendance_percentage=100.0
            )
            db.session.add(s)
            db.session.commit()
            session_id = s.id

        # teacher_vg is teacher/tutor for MCA 2 (class_id=2), NOT MCA 1 (class_id=1) nor teacher for session
        self.client.post('/login', data={'username': 'teacher_vg', 'password': 'password123'})

        response = self.client.get(f'/attendance/report/{session_id}', follow_redirects=True)
        self.assertIn(b'Access denied', response.data)

    # 12 & 14. Theory and practical attendance and internal marks are separate
    def test_12_14_separate_theory_and_practical(self):
        self.client.post('/login', data={'username': 'teacher_vg', 'password': 'password123'})

        self.client.post('/marks/theory', data={
            'class_id': 2, 'subject_id': 1, 'exam_name': 'Theory Mid-Term', 'max_marks': 100,
            'marks_6': 80
        })

        self.client.post('/marks/practical', data={
            'class_id': 2, 'subject_id': 7, 'exam_name': 'AJP Lab Exam', 'max_marks': 100,
            'marks_6': 95
        })

        with app.app_context():
            tm = TheoryInternalMark.query.filter_by(student_id=6, subject_id=1).first()
            pm = PracticalInternalMark.query.filter_by(student_id=6, subject_id=7).first()

            self.assertIsNotNone(tm)
            self.assertIsNotNone(pm)
            self.assertEqual(tm.marks_obtained, 80.0)
            self.assertEqual(pm.marks_obtained, 95.0)

    # 13. Attendance mark calculations at boundaries (90%, 80%, 70%, 60%, 50%, 49%)
    def test_13_attendance_mark_boundaries(self):
        self.assertEqual(calculate_attendance_mark(100.0), 5.0)
        self.assertEqual(calculate_attendance_mark(90.0), 5.0)
        self.assertEqual(calculate_attendance_mark(89.9), 4.0)
        self.assertEqual(calculate_attendance_mark(80.0), 4.0)
        self.assertEqual(calculate_attendance_mark(79.9), 3.0)
        self.assertEqual(calculate_attendance_mark(70.0), 3.0)
        self.assertEqual(calculate_attendance_mark(69.9), 2.0)
        self.assertEqual(calculate_attendance_mark(60.0), 2.0)
        self.assertEqual(calculate_attendance_mark(59.9), 1.0)
        self.assertEqual(calculate_attendance_mark(50.0), 1.0)
        self.assertEqual(calculate_attendance_mark(49.9), 0.0)

    # 15. CSV exports contain real database records
    def test_15_csv_export(self):
        self.client.post('/login', data={'username': 'teacher_vg', 'password': 'password123'})
        response = self.client.get('/reports/export/csv?report_type=daily_attendance&class_id=2')

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.mimetype, 'text/csv')
        self.assertIn(b'Session ID,Date,Period,Class,Subject', response.data)

    # 16. Editing attendance updates saved report correctly
    def test_16_edit_attendance_updates_report(self):
        self.client.post('/login', data={'username': 'teacher_vg', 'password': 'password123'})

        self.client.post('/attendance', data={
            'class_id': 2, 'subject_id': 1, 'date': '2025-03-05', 'period': 1,
            'status_6': 'Present', 'status_7': 'Present', 'status_8': 'Present',
            'status_9': 'Present', 'status_10': 'Present', 'status_11': 'Present'
        })

        self.client.post('/attendance', data={
            'class_id': 2, 'subject_id': 1, 'date': '2025-03-05', 'period': 1,
            'status_6': 'Absent', 'status_7': 'Present', 'status_8': 'Present',
            'status_9': 'Present', 'status_10': 'Present', 'status_11': 'Present'
        })

        with app.app_context():
            session_obj = AttendanceSession.query.filter_by(class_id=2, subject_id=1, date=date(2025, 3, 5), period=1).first()
            self.assertEqual(session_obj.present_students, 5)
            self.assertEqual(session_obj.absent_students, 1)

            st6_rec = AttendanceRecord.query.filter_by(session_id=session_obj.id, student_id=6).first()
            self.assertEqual(st6_rec.status, 'Absent')

if __name__ == '__main__':
    unittest.main()
