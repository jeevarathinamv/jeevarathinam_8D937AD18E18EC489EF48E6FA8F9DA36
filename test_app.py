"""
Unit Test Suite for Raja Raja Cholan Historical Information Website.
"""

import unittest
import os
import json
from app import app
from database import query_db, execute_db, init_db

class CholaHeritageTestCase(unittest.TestCase):
    def setUp(self):
        os.environ['USE_SQLITE'] = '1'
        app.config['TESTING'] = True
        app.config['WTF_CSRF_ENABLED'] = False
        self.client = app.test_client()

        with app.app_context():
            init_db()

    def test_public_pages_render(self):
        """Test that all public views load successfully with HTTP 200."""
        routes = [
            '/',
            '/history',
            '/military',
            '/temple',
            '/kingdom',
            '/achievements',
            '/gallery',
            '/quiz',
            '/admin/login'
        ]
        for route in routes:
            response = self.client.get(route)
            self.assertEqual(response.status_code, 200, f"Route {route} failed to load.")
            self.assertIn(b'Raja Raja Cholan', response.data)

    def test_quiz_api_endpoint(self):
        """Test that the /api/quiz endpoint returns questions in JSON."""
        response = self.client.get('/api/quiz')
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertEqual(data.get('status'), 'success')
        self.assertGreaterEqual(data.get('total'), 8)
        self.assertIn('Arulmozhivarman', json.dumps(data))

    def test_admin_authentication_workflow(self):
        """Test admin login with valid/invalid credentials and logout."""
        # 1. Access dashboard without login -> should redirect to login
        res = self.client.get('/admin/dashboard')
        self.assertEqual(res.status_code, 302)
        self.assertIn('/admin/login', res.headers['Location'])

        # 2. Login with incorrect password
        res = self.client.post('/admin/login', data={
            'username': 'admin',
            'password': 'wrongpassword'
        }, follow_redirects=True)
        self.assertIn(b'Invalid admin credentials', response.data if 'response' in locals() else res.data)

        # 3. Login with valid credentials
        res = self.client.post('/admin/login', data={
            'username': 'admin',
            'password': 'admin123'
        }, follow_redirects=True)
        self.assertIn(b"Emperor's Heritage Dashboard", res.data)

        # 4. Access dashboard now authenticated
        res = self.client.get('/admin/dashboard')
        self.assertEqual(res.status_code, 200)
        self.assertIn(b'Historical Articles', res.data)

        # 5. Logout
        res = self.client.get('/admin/logout', follow_redirects=True)
        self.assertIn(b'You have been securely logged out', res.data)

    def test_admin_article_crud(self):
        """Test adding, editing, and deleting an article."""
        # Authenticate first
        self.client.post('/admin/login', data={'username': 'admin', 'password': 'admin123'})

        # Add article
        res = self.client.post('/admin/article/add', data={
            'title': 'The Grand Kadaram Expedition',
            'category': 'military',
            'era_year': '1014 CE',
            'summary': 'Naval victory across the Malacca strait.',
            'content': 'Imperial navy expedition under the great sovereign.',
            'image_url': '/static/images/chola_navy.svg',
            'is_featured': '1'
        }, follow_redirects=True)
        self.assertIn(b'The Grand Kadaram Expedition', res.data)

        # Verify in DB
        article = query_db("SELECT * FROM articles WHERE title = %s", ('The Grand Kadaram Expedition',), one=True)
        self.assertIsNotNone(article)
        art_id = article['id']

        # Edit article
        res = self.client.post(f'/admin/article/edit/{art_id}', data={
            'title': 'The Grand Kadaram Naval Expedition (Updated)',
            'category': 'military',
            'era_year': '1014 CE',
            'summary': 'Updated naval victory summary.',
            'content': 'Updated content text.',
            'image_url': '/static/images/chola_navy.svg',
            'is_featured': '1'
        }, follow_redirects=True)
        self.assertIn(b'updated successfully', res.data)

        updated_art = query_db("SELECT * FROM articles WHERE id = %s", (art_id,), one=True)
        self.assertEqual(updated_art['title'], 'The Grand Kadaram Naval Expedition (Updated)')

        # Delete article
        res = self.client.post(f'/admin/article/delete/{art_id}', follow_redirects=True)
        self.assertIn(b'deleted', res.data)

        deleted_art = query_db("SELECT * FROM articles WHERE id = %s", (art_id,), one=True)
        self.assertIsNone(deleted_art)

    def test_admin_gallery_crud(self):
        """Test adding and deleting a gallery entry."""
        self.client.post('/admin/login', data={'username': 'admin', 'password': 'admin123'})

        res = self.client.post('/admin/gallery/add', data={
            'title': 'Sacred Thanjavur Inscription Wall',
            'category': 'architecture',
            'description': 'Epigraph detailing donations from royal sister Kundavai.',
            'image_url': '/static/images/thanjavur_temple.svg',
            'attribution': 'Archaeological Survey of India'
        }, follow_redirects=True)
        self.assertIn(b'Sacred Thanjavur Inscription Wall', res.data)

        item = query_db("SELECT * FROM gallery WHERE title = %s", ('Sacred Thanjavur Inscription Wall',), one=True)
        self.assertIsNotNone(item)
        item_id = item['id']

        # Delete
        res = self.client.post(f'/admin/gallery/delete/{item_id}', follow_redirects=True)
        self.assertIn(b'deleted', res.data)
        self.assertIsNone(query_db("SELECT * FROM gallery WHERE id = %s", (item_id,), one=True))

    def test_admin_quiz_crud(self):
        """Test adding and deleting a quiz question."""
        self.client.post('/admin/login', data={'username': 'admin', 'password': 'admin123'})

        res = self.client.post('/admin/quiz/add', data={
            'question': 'What was the regnal title assumed by Arulmozhivarman upon coronation?',
            'option_a': 'Maravarman',
            'option_b': 'Rajakesari',
            'option_c': 'Parakesari',
            'option_d': 'Tribhuvana',
            'correct_option': 'B',
            'explanation': 'He assumed the regnal title Rajakesari Arulmozhivarman.'
        }, follow_redirects=True)
        self.assertIn(b'New quiz question added successfully', res.data)

        q = query_db("SELECT * FROM quiz_questions WHERE question LIKE %s", ('%regnal title%',), one=True)
        self.assertIsNotNone(q)
        q_id = q['id']

        # Delete
        res = self.client.post(f'/admin/quiz/delete/{q_id}', follow_redirects=True)
        self.assertIn(b'deleted', res.data)
        self.assertIsNone(query_db("SELECT * FROM quiz_questions WHERE id = %s", (q_id,), one=True))

if __name__ == '__main__':
    unittest.main()
