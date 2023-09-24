from datetime import datetime
from time import time
import jwt
from hashlib import md5
from app import db, login, app
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from sqlalchemy import UniqueConstraint, Time


class RSVP(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    event_id = db.Column(db.Integer, db.ForeignKey('event.id'), nullable=False)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)
    user = db.relationship('User', back_populates='rsvps')
    status = db.Column(db.String(20), default="Pending")  # Pending, Accepted, Denied
    __table_args__ = (UniqueConstraint('user_id', 'event_id', name='_user_event_uc'),)

    def __repr__(self):
        return f"RSVP('{self.user_id}', '{self.event_id}', '{self.status}')"


class Event(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100))
    description = db.Column(db.String(300))
    location = db.Column(db.String(100))
    date = db.Column(db.Date)
    time = db.Column(db.Time)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"))
    rsvps = db.relationship('RSVP', backref='event', lazy=True)
    image_url = db.Column(db.String(100))
    max_attendees = db.Column(db.Integer)


class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), index=True, unique=True)
    email = db.Column(db.String(120), index=True, unique=True)
    password_hash = db.Column(db.String(128))
    posts = db.relationship("Post", backref="author", lazy="dynamic")
    about_me = db.Column(db.String(140))
    last_seen = db.Column(db.DateTime, default=datetime.utcnow)
    events = db.relationship("Event", backref="user", lazy="dynamic")
    rsvps = db.relationship('RSVP', back_populates='user')

    def __repr__(self):
        return "<User {}>".format(self.username)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    def avatar(self, size):
        digest = md5(self.email.lower().encode("utf-8")).hexdigest()
        return "https://www.gravatar.com/avatar/{}?d=identicon&s={}".format(digest, size)

    def get_reset_password_token(self, expires_in=600):
        return jwt.encode(
            {"reset_password": self.id, "exp": time() + expires_in},
            app.config["SECRET_KEY"],
            algorithm="HS256",
        ).decode("utf-8")

    @staticmethod
    def verify_reset_password_token(token):
        try:
            id = jwt.decode(token, app.config["SECRET_KEY"], algorithms=["HS256"])["reset_password"]
        except:
            return
        return User.query.get(id)


@login.user_loader
def load_user(id):
    return User.query.get(int(id))


class Post(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    body = db.Column(db.String(140))
    timestamp = db.Column(db.DateTime, index=True, default=datetime.utcnow)
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"))

    def __repr__(self):
        return "<Post {}>".format(self.body)
