
import os
from unittest import TestCase
from models import db, connect_db, Message, User
os.environ['DATABASE_URL'] = "postgresql:///warbler-test"
from sqlalchemy import exc
from app import app



class MessageModelTestCase(TestCase):
    def setUp(self):        

        self.app_context = app.app_context()
        self.app_context.push()
        db.create_all()
        Message.query.delete()
        self.client = app.test_client()



    def set_up_user(self):

        user = User.signup(
                email="test@test.com",
                username="testuser",
                password="HASHED_PASSWORD",
                image_url=None
            )
        user_id = 400001

        db.session.add(user)
        db.session.commit()



    def test_message_model(self):
        """ Test that the message model works."""

        with app.app_context():
            user = User(
                email="test@test.com",
                username="testuser",
                password="HASHED_PASSWORD"
            )
            msg = Message(text = 'Hello!', user_id= user.id
            )

            db.session.add(msg)
            db.session.commit()

            resp = self.client.get('/')

            self.assertEqual(resp.status_code, 200)



    def test_message_is_valid(self):
        """ Testing that a message will not post without a text."""

        self.set_up_user()

        user = User.query.one()
        msg = Message(text = None, user_id= user.id
            )

        db.session.add(msg)

        with self.assertRaises(
            exc.IntegrityError) as context:
            db.session.commit()



    def test_message_shows(self):
        """ Test that message shows on html."""

        self.set_up_user()  

        user = User.query.one() 
        msg = Message(text = "New message!", user_id= user.id
            )

        db.session.add(msg)

        msg_info = Message.query.one()
        
        res = self.client.get(f'/messages/{msg_info.id}')
        html = res.get_data(as_text = True)

        self.assertIn('<p class="single-message">New message!</p>', html)
        self.assertTrue(res.status_code, 200)
        self.assertNotIn('<p class="single-message">New message!!!!</p>', html)
        

    def test_delete_message(self):
        """ Test that a message successfully deletes."""

        self.set_up_user()

        user = User.query.one()
        msg = Message(text = "New message!", user_id= user.id
            )

        db.session.add(msg)
        db.session.commit()

        msg_info = Message.query.one()
        
        res = self.client.post(f'/messages/{msg_info.id}/delete')
        html = res.get_data(as_text = True)
        
        db.session.commit()

        self.assertNotIn('<p class="single-message">New message!</p>', html)
        self.assertEqual(res.status_code, 302)

    
    """ def test_liking_message(self):
       """ """ Test liking a message.""""""
        self.set_up_user()

        testuser = User.query.one()

        testuser2 = User.signup(
                email="test2@test.com",
                username="testuser2",
                password="HASHED_PASSWORD",
                image_url=None
            )

        testuser2_id = 400002

        msg = Message(text = "New message to like.", user_id= testuser.id
            )

        db.session.add(msg)
        db.session.add(testuser, testuser2)
        db.session.commit()

        testuser2.likes.append(msg)

        db.session.commit()

        like = Likes.query.filter(Likes.testuser2.id).all()
        self.assertEqual(len(like), 1) """
        



    def tearDown(self):

        db.session.remove()
        db.drop_all()
        self.app_context.pop()


    