import datetime
import sqlalchemy
from flask_login import UserMixin
from sqlalchemy import orm
import sqlalchemy_serializer
from sqlalchemy_serializer import SerializerMixin

from .db_session import SqlAlchemyBase

class MediaInfo(SqlAlchemyBase, UserMixin, SerializerMixin):
    __tablename__ = 'media_info'
    image_id = sqlalchemy.Column(sqlalchemy.Integer, primary_key=True)
    path = sqlalchemy.Column(sqlalchemy.String)
    post_id = sqlalchemy.Column(sqlalchemy.Integer)
    date = sqlalchemy.Column(sqlalchemy.DateTime)
    extension = sqlalchemy.Column(sqlalchemy.String)