import datetime
import sqlalchemy
from flask_login import UserMixin
from sqlalchemy import orm
import sqlalchemy_serializer
from sqlalchemy_serializer import SerializerMixin

from db_session import SqlAlchemyBase

class AuthInfo(SqlAlchemyBase, UserMixin, SerializerMixin):
    __tablename__ = 'auth_info'

    uid = sqlalchemy.Column(sqlalchemy.Integer, nullable=False, autoincrement=True, primary_key=True)
    session_id = sqlalchemy.Column(sqlalchemy.String, nullable=False)
    hashed_password = sqlalchemy.Column(sqlalchemy.String, nullable=False)