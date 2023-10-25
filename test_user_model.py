"""User model tests."""

# run these tests like:
#
#    python -m unittest test_user_model.py


import os
from unittest import TestCase
from sqlalchemy import exc

from models import db, User, Message, Follows

# BEFORE we import our app, let's set an environmental variable
# to use a different database for tests (we need to do this
# before we import our app, since that will have already
# connected to the database

os.environ['DATABASE_URL'] = "postgresql:///warbler-test"


# Now we can import app

from app import app

# Create our tables (we do this here, so we only create the tables
# once for all tests --- in each test, we'll delete the data
# and create fresh new clean test data
with app.app_context():
    db.create_all()


class UserModelTestCase(TestCase):
    """Test views for messages."""

    def create_app(self):
        app.config['TESTING']= True
        return app 

        
    def setUp(self):
        """Create test client, add sample data."""

        self.app_context = app.app_context()
        self.app_context.push()

        self.client = app.test_client()
        db.create_all()
        User.query.delete()
        Message.query.delete()
        Follows.query.delete()


    def test_user_model(self):
        """Does basic model work?"""

        with app.app_context():
            u = User(
                email="test@test.com",
                username="testuser",
                password="HASHED_PASSWORD"
            )

            db.session.add(u)
            db.session.commit()

            # User should have no messages & no followers
            self.assertEqual(len(u.messages), 0)
            self.assertEqual(len(u.followers), 0)


    def test_valid_signup(self):
        """Test sign up is successful."""

        test = User.signup("test","test@test.com","testing",None)
        test.id = 5000

        db.session.add(test)
        db.session.commit()

        self.assertEqual(test.username, "test")
        self.assertNotEqual(test.username, "jaz")

    

    def test_invalid_signup(self):
        """ Test that you cannot signup with a username that is already taken."""

        test = User.signup("test","test@test.com","testing",None)
        test.id = 5000
        testing_copy = User.signup("test","test@test.com","testing",None)
        testing_copy.id=5001

        with self.assertRaises(exc.IntegrityError) as context:
            db.session.commit()


    def test_authentication(self):
        """ Test authentication."""

        user = User.signup(
                email="test@test.com",
                username="testuser",
                password="password",
                image_url= None)
        user.id = 78787

        db.session.add(user)
        db.session.commit()

        user_authenticate = User.authenticate(user.username, "password")

        self.assertEqual(user_authenticate.id, user.id)


    def test_following(self):
        """ Test that a user is or is not following another user."""
        
        user = User.signup(
                email="test@test.com",
                username="testuser",
                password="password",
                image_url= None)
        user.id = 78787

        user2 = User.signup(
                email="test2@test.com",
                username="testuser2",
                password="password",
                image_url= None)
        user2.id = 78788

        user.following.append(user2)

        db.session.add(user,user2)
        db.session.commit()

        self.assertTrue(user.is_following(user2))
        self.assertFalse(user2.is_following(user))
        self.assertTrue(user2.is_followed_by(user))
        self.assertFalse(user.is_followed_by(user2))



    """ def test_stop_following(self):
        user = Follows()


        with self.client as c:
            
        testuser = self.testuser
        testuser2 = self.testuser2

        res = c.post(f"/users/follow/{testuser.id}", data = {"followed_user": testuser2})
        testuser.following.append(testuser2)
        db.session.commit()
        resp = c.post(f"/users/stop-following/{testuser.id}", data = {"followed_user": testuser2})
        self.testuser.following.remove(self.testuser2)
        db.session.commit()
        following = c.get(f"/users/{testuser.id}/following")
        self.assertNotIn(f'{testuser2.id}', following) """



    def tearDown(self):

        db.session.remove()
        db.drop_all()
        self.app_context.pop()