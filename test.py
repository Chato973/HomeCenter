__author__ = 'Peter'

from project import app,db
from flask.ext.testing import TestCase
from project.models import *
from flask.ext.login import current_user
import datetime

import unittest

class BaseTestCase(TestCase):

    def create_app(self):
        app.config.from_object('config.TestConfig')
        return app

    def setUp(self):
        db.create_all()
        db.session.add(User("admin","admin"))
        db.session.add(Show("Firefly",True,False))
        db.session.add(Download("test.avi",123456,"C:\\test.avi",datetime.datetime.now(),1))
        db.session.commit()

    def tearDown(self):
        db.session.remove()
        db.drop_all()

class FlaskTestCase(BaseTestCase):

    #ensure flask is setup correctly

    def test_index(self):
        response =  self.client.get('/login', content_type='html/text')
        self.assertEqual(response.status_code, 200)

    # Ensure main page requires a login
    def test_main_route_requires_login(self):
         
        response =  self.client.get('/', follow_redirects=True)
        self.assertTrue(b'Please log in to access this page.' in response.data)

    # Ensure downloads show up on the mainpage
    def test_posts_show_up(self):
         
        response =  self.client.post(
            '/login',
            data=dict(username="admin", password="admin"),
            follow_redirects=True
        )
        self.assertIn(b'Firefly', response.data)

class UsersViewsTests(BaseTestCase):

    # Ensure the login page loads
    def test_login_page_loads(self):

        response =  self.client.get('/login', content_type='html/text')
        self.assertTrue(b'Please login' in response.data)

    # Ensure the login works correctly with the right credentials
    def test_correct_login(self):

        response =  self.client.post(
            '/login',
            data=dict(username="admin", password="admin"),
            follow_redirects=True
        )
        self.assertIn(b'You were just logged in.', response.data)

    # Ensure the login works with incorrect credentials
    def test_incorrect_login(self):

        response =  self.client.post(
            '/login',
            data=dict(username="admin", password="wrongpassword"),
            follow_redirects=True
        )
        self.assertIn(b'Invalid Credentials. Please try again.', response.data)

    # Ensure logout behaves correctly
    def test_logout(self):
        with self.client:
            self.client.post(
                '/login',
                data=dict(username="admin", password="admin"),
                follow_redirects=True)
            response =  self.client.get(
                '/logout',
                follow_redirects=True
            )
            self.assertIn(b'You were just logged out.', response.data)
            self.assertFalse(current_user.is_active)

    # Ensure logout page requires a login
    def test_logout_route_requires_login(self):

        response =  self.client.get('/logout', follow_redirects=True)
        self.assertTrue(b'Please log in to access this page.' in response.data)

    # Ensure logged in user is the user that logged in

    def test_correct_login_user(self):
        with self.client:
            response =  self.client.post(
                '/login',
                data=dict(username="admin", password="admin"),
                follow_redirects=True
            )
            self.assertTrue(current_user.name == "admin")

    def test_correct_login_user_isactive(self):
        with self.client:
            response =  self.client.post(
                '/login',
                data=dict(username="admin", password="admin"),
                follow_redirects=True
            )
            self.assertTrue(current_user.is_active)

    # Ensure use can register

    def test_correct_register_user(self):
        with self.client:
            response =  self.client.post(
                '/register',
                data=dict(username="test", email="test@test.com", password="test", confirm="test"),
                follow_redirects=True
            )
            self.assertTrue(current_user.name == "test")
            self.assertIn(b'Welcome to Flask!', response.data)
            self.assertTrue(current_user.is_active)

if __name__ == '__main__':
    unittest.main()
