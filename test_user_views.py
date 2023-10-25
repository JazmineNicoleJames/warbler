"""User View tests."""

# run these tests like:
#
#    FLASK_ENV=production python -m unittest test_message_views.py


import os
from unittest import TestCase

from models import db, connect_db, Message, User, Follows, Likes

# BEFORE we import our app, let's set an environmental variable
# to use a different database for tests (we need to do this
# before we import our app, since that will have already
# connected to the database

os.environ['DATABASE_URL'] = "postgresql:///warbler-test"


# Now we can import app

from app import app, CURR_USER_KEY

# Create our tables (we do this here, so we only create the tables
# once for all tests --- in each test, we'll delete the data
# and create fresh new clean test data


# Don't have WTForms use CSRF at all, since it's a pain to test

app.config['WTF_CSRF_ENABLED'] = False

class FollowsViewsTestCase(TestCase):

    def setUp(self):
        """Create test client, add sample data."""

        self.app_context = app.app_context()
        self.app_context.push()

        self.client = app.test_client()
        db.create_all()
        User.query.delete()
        Message.query.delete()
        Follows.query.delete()
        
        self.client = app.test_client()
        self.follows = Follows()


        self.testuser = User.signup(username="testuser",
                                    email="test@test.com",
                                    password="testuser",
                                    image_url=None)

        self.testuser2 = User.signup(username="testuser2",
                                    email="test2@test.com",
                                    password="testuser2",
                                    image_url=None)
        
        self.testuser_id = 10
        self.testuser.id = self.testuser_id
        self.testuser2_id = 20
        self.testuser2.id = self.testuser2_id       
        
        db.session.commit()


    def test_users_following(self):
        """ Test that a user is following another."""

        with self.client as c:
            with c.session_transaction() as sess:
                sess[CURR_USER_KEY] = self.testuser.id

            user = self.testuser
            user2 = self.testuser2
            user.following.append(user2)
            db.session.commit()

            res = c.get(f"/users/{user.id}/following")
            html = res.get_data(as_text = True)

            self.assertIn('<a href="/users/10/following">1</a>', html)



    def test_user_show(self):
        """ Test that a user profile shows."""

        with self.client as c:
            res = c.get(f"/users/{self.testuser.id}")

            self.assertEqual(res.status_code, 200)
 



    def test_add_like(self):
        """ Test that liking a message works."""

        msg = Message(id=100, text="Testing Testing", user_id = self.testuser.id)

        db.session.add(msg)
        db.session.commit()

        with self.client as c:
            with c.session_transaction() as sess:
                sess[CURR_USER_KEY] = self.testuser.id
            
            res = c.post("/users/add_like/100", follow_redirects=True)
            like = Likes.query.filter(Likes.message_id==100).all()
     
            self.assertEqual(res.status_code, 200)
            self.assertEqual(len(like), 1)

    
    """ def test_show_like(self):
        """ """Test that a like shows on profile.""" """"

        with self.client as c:
            msg = Message(id=1000, text="Testing Testing", user_id = 10)
            likes = Likes.query.filter_by(testuser_id==user_id).all()

            db.session.commit()
            res = c.get(f"/users/{self.testuser_id}/likes")

            self.assertEqual(res.status_code,200)

            html = res.get_data(as_text = True)
            self.assertIn(f'<a href="/users/{self.testuser_id}/likes">1</a>', html) """


    def setup_followers(self):
        f1 = Follows(user_being_followed_id=self.testuser_id, user_following_id=self.testuser_id)
        f2 = Follows(user_being_followed_id=self.testuser2.id, user_following_id=self.testuser_id)
        
        db.session.add_all([f1,f2])
        db.session.commit()

    def test_followers(self):
        self.setup_followers()

        with self.client as c:
            res = c.get(f"/users/{self.testuser_id}")
            self.assertEqual(res.status_code, 200)



    def tearDown(self):

        db.session.remove()
        db.drop_all()
        self.app_context.pop()