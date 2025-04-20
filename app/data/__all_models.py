import datetime
import sqlalchemy
from flask_login import UserMixin
from sqlalchemy import orm
import sqlalchemy_serializer
from sqlalchemy_serializer import SerializerMixin

from .db_session import SqlAlchemyBase

class Users(SqlAlchemyBase, UserMixin, SerializerMixin):
    __tablename__ = 'users'
    id = sqlalchemy.Column(sqlalchemy.Integer,
                           primary_key=True, autoincrement=True)
    nickname = sqlalchemy.Column(sqlalchemy.String, nullable=False)
    password = sqlalchemy.Column(sqlalchemy.String, nullable=False)

class Categories(SqlAlchemyBase, UserMixin, SerializerMixin):
    __tablename__ = 'categories'
    id = sqlalchemy.Column(sqlalchemy.Integer,
                           primary_key=True, autoincrement=True)
    category_name = sqlalchemy.Column(sqlalchemy.String, nullable=False)

class Posts(SqlAlchemyBase, UserMixin, SerializerMixin):
    __tablename__ = 'posts'
    user_id = sqlalchemy.Column(sqlalchemy.Integer, sqlalchemy.ForeignKey("users.id"))
    id = sqlalchemy.Column(sqlalchemy.Integer,
                           primary_key=True, autoincrement=True)
    category_id = sqlalchemy.Column(sqlalchemy.Integer, sqlalchemy.ForeignKey("categories.id"))
    text = sqlalchemy.Column(sqlalchemy.String)
    photo_url = sqlalchemy.Column(sqlalchemy.String)
    timestamp = sqlalchemy.Column(sqlalchemy.DateTime, default=datetime.datetime.now)
    user = orm.relationship('Users')
    category = orm.relationship('categories')

class Comments(SqlAlchemyBase, UserMixin, SerializerMixin):
    __tablename__ = 'comments'
    user_id = sqlalchemy.Column(sqlalchemy.Integer, sqlalchemy.ForeignKey("users.id"))
    id = sqlalchemy.Column(sqlalchemy.Integer,
                           primary_key=True, autoincrement=True)
    post_id = sqlalchemy.Column(sqlalchemy.Integer, sqlalchemy.ForeignKey("posts.id"))
    text = sqlalchemy.Column(sqlalchemy.String)
    timestamp = sqlalchemy.Column(sqlalchemy.DateTime, default=datetime.datetime.now)
    user = orm.relationship('Users')
    post = orm.relationship('Posts')

class Likes(SqlAlchemyBase, UserMixin, SerializerMixin):
    __tablename__ = 'likes'
    id = sqlalchemy.Column(sqlalchemy.Integer,
                           primary_key=True, autoincrement=True)
    user_id = sqlalchemy.Column(sqlalchemy.Integer, sqlalchemy.ForeignKey("users.id"))
    post_id = sqlalchemy.Column(sqlalchemy.Integer, sqlalchemy.ForeignKey("posts.id"))
    timestamp = sqlalchemy.Column(sqlalchemy.DateTime, default=datetime.datetime.now)
    user = orm.relationship('Users')
    post = orm.relationship('Posts')

class Messages(SqlAlchemyBase, UserMixin, SerializerMixin):
    __tablename__ = 'messages'
    user_id = sqlalchemy.Column(sqlalchemy.Integer, sqlalchemy.ForeignKey("users.id"))
    id = sqlalchemy.Column(sqlalchemy.Integer,
                           primary_key=True, autoincrement=True)
    timestamp = sqlalchemy.Column(sqlalchemy.DateTime, default=datetime.datetime.now)
    user = orm.relationship('Users')