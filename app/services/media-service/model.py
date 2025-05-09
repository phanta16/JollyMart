import datetime
import sqlalchemy
from flask_login import UserMixin
from sqlalchemy import orm
import sqlalchemy_serializer
from sqlalchemy_serializer import SerializerMixin

from db_session import SqlAlchemyBase

class MediaInfo(SqlAlchemyBase, UserMixin, SerializerMixin):
    __tablename__ = 'media_info'
    image_id = sqlalchemy.Column(sqlalchemy.Integer, primary_key=True, autoincrement=True)
    filename = sqlalchemy.Column(sqlalchemy.String, nullable=False)
    path = sqlalchemy.Column(sqlalchemy.String, nullable=False)
    date = sqlalchemy.Column(sqlalchemy.DateTime, default=datetime.datetime.now())
    extension = sqlalchemy.Column(sqlalchemy.String)