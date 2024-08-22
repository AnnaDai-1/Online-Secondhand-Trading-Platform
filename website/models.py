from website import db
from flask_login import UserMixin
from sqlalchemy.sql import func

class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(150), unique=True)
    username = db.Column(db.String(150), unique=True)
    password = db.Column(db.String(150))
    date_created = db.Column(db.DateTime(timezone=True), default=func.now())
    items = db.relationship('Item', backref='user', passive_deletes=True)
    comments =  db.relationship('Comment', backref='user', passive_deletes=True)
    contact = db.Column(db.String, nullable=False)


class Image(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    filename = db.Column(db.Text)
    item_id = db.Column(db.Integer, db.ForeignKey('item.id', ondelete="CASCADE"), nullable=False)

class Item(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.Text, nullable=False)
    description = db.Column(db.Text, nullable=False)
    price = db.Column(db.Float, nullable=False)
    thumbnail=db.Column(db.String, nullable=False)
    images = db.relationship('Image', backref='item', passive_deletes=True)
    state = db.Column(db.Boolean, default=True, nullable = False) #true: the item is available/ false: it is not available
    user_id = db.Column(db.Integer, db.ForeignKey('user.id', ondelete="CASCADE"), nullable = False)
    date_created = db.Column(db.DateTime(timezone=True), default=func.now())
    comments =  db.relationship('Comment', backref='item', passive_deletes=True)

class Comment(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    text = db.Column(db.String(200), nullable=False)
    date_created = db.Column(db.DateTime(timezone=True), default=func.now())
    author = db.Column(db.Integer, db.ForeignKey('user.id', ondelete="CASCADE"), nullable=False)
    item_id = db.Column(db.Integer, db.ForeignKey('item.id', ondelete="CASCADE"), nullable=False)