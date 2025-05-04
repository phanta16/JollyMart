import datetime
import sqlalchemy
from flask_login import UserMixin
from sqlalchemy import orm
import sqlalchemy_serializer
from sqlalchemy_serializer import SerializerMixin

from db_session import SqlAlchemyBase

class MediaPostInfo(SqlAlchemyBase, UserMixin, SerializerMixin):
    __tablename__ = 'media_post_info'
    image_id = sqlalchemy.Column(sqlalchemy.Integer, primary_key=True, autoincrement=True)
    filename = sqlalchemy.Column(sqlalchemy.String, nullable=False)
    image = sqlalchemy.Column(sqlalchemy.BLOB, nullable=False)
    post_id = sqlalchemy.Column(sqlalchemy.Integer)
    date = sqlalchemy.Column(sqlalchemy.DateTime, default=datetime.datetime.now())
    extension = sqlalchemy.Column(sqlalchemy.String)

class MediaUserInfo(SqlAlchemyBase, UserMixin, SerializerMixin):
    __tablename__ = 'media_user_info'
    image_id = sqlalchemy.Column(sqlalchemy.Integer, primary_key=True, autoincrement=True)
    filename = sqlalchemy.Column(sqlalchemy.String, nullable=False)
    image = sqlalchemy.Column(sqlalchemy.BLOB, nullable=False)
    user_id = sqlalchemy.Column(sqlalchemy.Integer)
    date = sqlalchemy.Column(sqlalchemy.DateTime, default=datetime.datetime.now())
    extension = sqlalchemy.Column(sqlalchemy.String)