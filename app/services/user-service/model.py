import datetime
import sqlalchemy
from flask_login import UserMixin
from sqlalchemy import orm
import sqlalchemy_serializer
from sqlalchemy_serializer import SerializerMixin

from db_session import SqlAlchemyBase

class UserInfo(SqlAlchemyBase, UserMixin, SerializerMixin):
    __tablename__ = 'user_info'
    uid = sqlalchemy.Column(sqlalchemy.Integer, primary_key=True)
    username = sqlalchemy.Column(sqlalchemy.String, nullable=False, unique=True)
    email = sqlalchemy.Column(sqlalchemy.String, nullable=False, unique=True)
    date_joined = sqlalchemy.Column(sqlalchemy.DateTime, nullable=False, default=datetime.datetime.now)